# egit.py — AYLIK: v35 modellerini eğitir, yürüyen testi yapar, durum/model.pkl dosyasına kaydeder, özeti Telegram'a yollar
import os, sys, gzip, pickle, lightgbm as lgb
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from ortak import *
from ortak import _mzip
RAPOR = []
def display(df):
    txt = df.to_string(); print(txt); RAPOR.append("```\n" + txt + "\n```")
_print = print
def print(*a, **k):
    _print(*a, **k); RAPOR.append(" ".join(str(x) for x in a))
zfit = ZF
T0 = time.time()
baslik("1) BINANCE BTCUSDT — 1 saatlik mumlar (2017'den bugüne)")
T0 = time.time(); o = fetch_1h(pd.Timestamp("2017-08-17", tz="UTC").timestamp() * 1000, time.time() * 1000, verbose=True)
print(f"✅ {len(o):,} mum: {o.index[0]:%Y-%m-%d} → {o.index[-1]:%Y-%m-%d %H:%M} UTC")
FA = features(o); FEATS = list(FA.columns)

# ================= 1b) 1 DAKİKALIK VERİ → SAAT İÇİ YOL ÖZELLİKLERİ (1 saatlik model için) =================
baslik("1b) BINANCE 1 DAKİKALIK ARŞİV (data.binance.vision) → saat içi yol özellikleri")
import io, zipfile
from concurrent.futures import ThreadPoolExecutor
t0 = time.time(); now_ = pd.Timestamp.now(tz="UTC"); cur_m = now_.normalize().replace(day=1)
yms = [d.strftime("%Y-%m") for d in pd.date_range(pd.Timestamp(MICRO_START, tz="UTC"), cur_m - pd.Timedelta(days=1), freq="MS")]
with ThreadPoolExecutor(8) as ex: parts = list(ex.map(_mzip, yms))
mins = [to_min(p) for p in parts if p is not None]
last_arch = mins[-1].index[-1] if mins else pd.Timestamp(MICRO_START, tz="UTC")
tail_ = fetch_1m(last_arch.timestamp() * 1000, time.time() * 1000)
M1 = pd.concat(mins + ([tail_] if tail_ is not None else [])); M1 = M1[~M1.index.duplicated(keep="last")].sort_index()
MIC = micro_features(M1); MICF = list(MIC.columns)
print(f"✅ {len(M1):,} dakika ({sum(p is not None for p in parts)}/{len(yms)} aylık arşiv + API) → {len(MIC):,} saat · {time.time()-t0:.0f} sn")
FA1 = FA.join(MIC.reindex(FA.index)); FEATS1 = FEATS + MICF
HHM = hourly_cv(M1); P2 = path2_features(o.close, HHM, MIC); P2F = list(P2.columns)
FA4 = FA.join(P2); FEATS4 = FEATS + P2F
print(f"✅ 4 saatlik model için {len(P2F)} çok saatlik yol özelliği")
# ================= 2) HER UFUK İÇİN YÜRÜYEN TEST (yalnız geçmiş veri, her ay yeniden eğitim) =================
LEV = ["Zayıf", "Güçlü (en emin %30)", "Çok güçlü (en emin %10)"]
R = {}
for H, cf in CFG.items():
    baslik(f"2) {cf['ad'].upper()} — yürüyen test {TEST_START} → bugün · aylık eğitim · pencere(ler): {' + '.join(str(y) + ' yıl' for y in cf['years'])}")
    t0 = time.time(); D = (FA1 if H == 1 else FA4 if H == 4 else FA).copy(); D["y"] = np.log(o.close.shift(-H) / o.close); D = D.iloc[720:]; DL = D.dropna(subset=["y"])
    def train_month(ms, DL=DL, H=H, yrs_list=cf["years"], FE=(FEATS1 if H == 1 else FEATS4 if H == 4 else FEATS)):
        parts = []
        for yrs in yrs_list:
            tr = DL[DL.index < ms - pd.Timedelta(hours=H)]; tr = tr[tr.index >= tr.index[-1] - pd.Timedelta(days=365 * yrs)]
            yb = (tr.y > 0).astype(int); k = int(len(tr) * .85)
            g = lgb.LGBMClassifier(n_estimators=600, learning_rate=0.03, num_leaves=15, min_child_samples=300, subsample=0.7, subsample_freq=1,
                                   colsample_bytree=0.5, reg_lambda=10, verbose=-1).fit(tr[FE].iloc[:k - H], yb.iloc[:k - H],
                                   eval_set=[(tr[FE].iloc[k:], yb.iloc[k:])], callbacks=[lgb.early_stopping(50, verbose=False)])
            z = zfit(tr[FE]); lo = LogisticRegression(C=0.01, max_iter=500).fit(z(tr[FE]), yb); parts.append((g, z, lo))
        return HModel(parts, FE)
    months = pd.date_range(pd.Timestamp(TEST_START, tz="UTC"), D.index[-1], freq="MS")
    PG = pd.Series(np.nan, index=D.index); PL = PG.copy(); model = None
    for i, ms in enumerate(months):
        me = months[i + 1] if i + 1 < len(months) else D.index[-1] + pd.Timedelta(hours=1)
        rows = D[(D.index >= ms) & (D.index < me)]
        if not len(rows): continue
        model = train_month(ms); pg, pl = model(rows); PG.loc[rows.index], PL.loc[rows.index] = pg, pl
    PG, PL = PG.dropna(), PL.dropna()
    cut = DL.index[-1] - pd.Timedelta(days=30); trq = DL[(DL.index < cut - pd.Timedelta(hours=H)) & (DL.index >= cut - pd.Timedelta(days=365 * 3))]; cal = DL[DL.index >= cut]
    QM = {q: lgb.LGBMRegressor(objective="quantile", alpha=q, n_estimators=400, learning_rate=0.03, num_leaves=15, min_child_samples=300,
                               subsample=0.7, subsample_freq=1, colsample_bytree=0.5, verbose=-1).fit(trq[FEATS], trq.y) for q in (0.1, 0.5, 0.9)}
    qc = np.sort(np.column_stack([QM[q].predict(cal[FEATS]) for q in (0.1, 0.5, 0.9)]), axis=1)
    QC = float(np.quantile(np.maximum(qc[:, 0] - cal.y.values, cal.y.values - qc[:, 2]), 0.8 * (1 + 1 / len(cal))))
    R[H] = dict(model=model, month=months[-1], PG=PG, PL=PL, D=D, QM=QM, QC=QC, t0=t0)
    print(f"   modeller hazır · {time.time()-t0:.0f} sn")

# ================= 2a) 1 SAAT: ÇOK UFUKLU YIĞINLAMA (aylık, yalnız geçmiş veriyle öğrenilir) =================
baslik("2a) 1 SAAT — ÇOK UFUKLU YIĞINLAMA (1s + 4s + 8s sinyallerinden aylık öğrenilen birleştirici)")
def base_S(H, rh=None): return signal_frame(R[H]["PG"], R[H]["PL"], FA[f"r{H}"] if rh is None else rh, CFG[H]["don"]).S
JS = pd.DataFrame({"S1": base_S(1), "S4": base_S(4), "S8": base_S(8)}).dropna(); JS["y1"] = R[1]["D"].y.reindex(JS.index)
ST = pd.Series(np.nan, index=JS.index); STACK = None
sm = pd.date_range(JS.index[0] + pd.Timedelta(days=90), JS.index[-1], freq="MS")
for i, ms in enumerate(sm):
    me = sm[i + 1] if i + 1 < len(sm) else JS.index[-1] + pd.Timedelta(hours=1)
    tr = JS[JS.index < ms - pd.Timedelta(hours=1)].dropna(subset=["y1"]); te = JS[(JS.index >= ms) & (JS.index < me)]
    if len(tr) < 2000 or not len(te): continue
    STACK = LogisticRegression(C=0.1).fit(tr[["S1", "S4", "S8"]].clip(-5, 5), (tr.y1 > 0).astype(int)); ST.loc[te.index] = STACK.decision_function(te[["S1", "S4", "S8"]].clip(-5, 5))
R[1]["ST"] = ST.dropna(); R[1]["stack"] = STACK
print(f"✅ yığınlama ağırlıkları (son ay): 1s {STACK.coef_[0][0]:+.3f} · 4s {STACK.coef_[0][1]:+.3f} · 8s {STACK.coef_[0][2]:+.3f}")
def final_frame(H): return frame_from_S(cz(R[1]["ST"])) if H == 1 else signal_frame(R[H]["PG"], R[H]["PL"], FA[f"r{H}"], CFG[H]["don"])

# ================= 2b) HER UFUK İÇİN SONUÇ TABLOSU =================
for H, cf in CFG.items():
    baslik(f"2b) {cf['ad'].upper()} — test sonuçları" + (" (çok ufuklu yığınlama ile)" if H == 1 else ""))
    t0 = R[H]["t0"]; D = R[H]["D"]; SF = final_frame(H); SF["y"] = D.y.reindex(SF.index)
    B = SF[SF.index.hour % H == 0].dropna(subset=["S", "T30", "y"])                      # bağımsız bloklar (ufuk aralıklı)
    r = np.exp(B.y.values) - 1; up = B.y.values > 0; d = np.where(B.S > 0, 1, -1)
    hold = B.index >= pd.Timestamp(HOLD_START, tz="UTC"); A_all = roc_auc_score(up, B.S); A_h = roc_auc_score(up[hold], B.S[hold]); se = auc_se(A_h, hold.sum())
    AH = SF.dropna(subset=["S", "T30", "y"]); rA = np.exp(AH.y.values) - 1; upA = AH.y.values > 0; dA = np.where(AH.S > 0, 1, -1)
    lvA = np.where(AH.C >= AH.T10, 2, np.where(AH.C >= AH.T30, 1, 0)); hA = AH.index >= pd.Timestamp(HOLD_START, tz="UTC"); wkA = (AH.index[-1] - AH.index[0]).days / 7
    STATS, rows_ = {}, []
    for li, lv in enumerate(LEV):
        for sg, yon in [(1, "YUKARI"), (-1, "AŞAĞI")]:
            ev = events((lvA == li) & (dA == sg), H); g = sg * rA[ev]; evh = ev[hA[ev]]; lo_, hi_ = wboot(g, AH.index[ev])
            st = dict(n=len(ev), wk=len(ev) / wkA, acc=((dA[ev] == 1) == upA[ev]).mean() * 100, gross=g.mean() * 100, lo=lo_ * 100, hi=hi_ * 100,
                      net=g.mean() * 100 - 2 * SPOT_FEE * 100, acc_h=((dA[evh] == 1) == upA[evh]).mean() * 100)
            STATS[(li, sg)] = st
            rows_.append({"Güven": lv, "Yön": yon, "Sinyal": st["n"], "Haftada": st["wk"], "İsabet %": st["acc"], "İsabet 2024+ %": st["acc_h"], "Brüt %": st["gross"],
                          "[%90]": f"[{st['lo']:+.3f}, {st['hi']:+.3f}]", "Spot net %": st["net"]})
    verdict = "✅ yön bilgisi anlamlı" if (A_h - 0.5) / se > 2 else "❔ yön bilgisi 2024+ döneminde kanıtlanamadı"
    print(f"AUC 2020–bugün {A_all:.4f} · AUC 2024+ {A_h:.4f} (z={(A_h-0.5)/se:.1f}) → {verdict} · {time.time()-t0:.0f} sn\n(tablo: CANLI ÖLÇÜM — her saat kontrol, sinyalin ilk ortaya çıktığı an)")
    display(pd.DataFrame(rows_).round(3).set_index(["Güven", "Yön"]))
    R[H].update(STATS=STATS, SF=SF, A_all=A_all, A_h=A_h, z=(A_h - 0.5) / se, verdict=verdict)
# ---- 4s + 8s UYUMU (bilgi amaçlı): ikisi birden 'Çok güçlü YUKARI' iken sonuçlar ----
baslik("2d) 🎯 BARİYER MODELLERİ — ufuk içinde önce +1σ hedef mi, −1σ stop mu? (1 · 4 · 8 saat, yürüyen test)")
BK, BHS = 1.0, [1, 4, 8]; BAR = {}
cc, hh, ll = o.close.values, o.high.values, o.low.values; nn = len(o)
for BH in BHS:
    t0 = time.time(); sgm = (np.log(o.close).diff().rolling(168).std() * np.sqrt(BH)).values; blab = np.full(nn, np.nan)
    for i in range(nn - BH):
        if np.isnan(sgm[i]): continue
        up_, dn_ = cc[i] * (1 + BK * sgm[i]), cc[i] * (1 - BK * sgm[i])
        for j in range(i + 1, i + BH + 1):
            hu, hd = hh[j] >= up_, ll[j] <= dn_
            if hu and hd: break                                                          # aynı saatte ikisi: belirsiz, etiket yok
            if hu: blab[i] = 1; break
            if hd: blab[i] = 0; break
    DB = FA.copy(); DB["lab"] = blab; DB = DB.iloc[720:]
    def train_bar(ms, DB=DB, BH=BH):
        tr = DB[(DB.index < ms - pd.Timedelta(hours=BH))].dropna(subset=["lab"]); tr = tr[tr.index >= tr.index[-1] - pd.Timedelta(days=365 * 3)]
        yb = tr.lab.astype(int); k = int(len(tr) * .85)
        g = lgb.LGBMClassifier(n_estimators=600, learning_rate=0.03, num_leaves=15, min_child_samples=300, subsample=0.7, subsample_freq=1, colsample_bytree=0.5,
                               reg_lambda=10, verbose=-1).fit(tr[FEATS].iloc[:k - BH], yb.iloc[:k - BH], eval_set=[(tr[FEATS].iloc[k:], yb.iloc[k:])], callbacks=[lgb.early_stopping(50, verbose=False)])
        z = zfit(tr[FEATS]); lo = LogisticRegression(C=0.01, max_iter=500).fit(z(tr[FEATS]), yb)
        return HModel([(g, z, lo)], FEATS)
    bm = pd.date_range(pd.Timestamp(TEST_START, tz="UTC"), DB.index[-1], freq="MS"); PGb = pd.Series(np.nan, index=DB.index); PLb = PGb.copy(); MB = None
    for i, ms in enumerate(bm):
        me = bm[i + 1] if i + 1 < len(bm) else DB.index[-1] + pd.Timedelta(hours=1); rows = DB[(DB.index >= ms) & (DB.index < me)]
        if not len(rows): continue
        MB = train_bar(ms); pg, pl = MB(rows); PGb.loc[rows.index], PLb.loc[rows.index] = pg, pl
    PGb, PLb = PGb.dropna(), PLb.dropna(); SFb = signal_frame(PGb, PLb, FA[f"r{BH}"], False); SFb["lab"] = DB.lab.reindex(SFb.index)
    BBb = SFb[SFb.index.hour % BH == 0].dropna(subset=["S", "T30"]); bh_ = BBb.index >= pd.Timestamp(HOLD_START, tz="UTC")
    BA = SFb.dropna(subset=["S", "T30"]); bdA = np.where(BA.S > 0, 1, -1); blvA = np.where(BA.C >= BA.T10, 2, np.where(BA.C >= BA.T30, 1, 0)); bhA = BA.index >= pd.Timestamp(HOLD_START, tz="UTC")
    ST_, rows_ = {}, []
    for li, lv in enumerate(LEV):
        for sg, yon in [(1, "YUKARI"), (-1, "AŞAĞI")]:
            ev = events((blvA == li) & (bdA == sg), BH); tgt_ = 1 if sg == 1 else 0; lb = BA.lab.values[ev]; ok = ~np.isnan(lb); lbh = BA.lab.values[ev[bhA[ev]]]; okh = ~np.isnan(lbh)
            ST_[(li, sg)] = dict(n=int(ok.sum()), first=(lb[ok] == tgt_).mean() * 100 if ok.any() else np.nan, first_h=(lbh[okh] == tgt_).mean() * 100 if okh.any() else np.nan)
            rows_.append({"Güven": lv, "Yön": yon, "Bariyere ulaşan sinyal": ST_[(li, sg)]["n"], "Sinyal yönünde ÖNCE bariyer %": ST_[(li, sg)]["first"], "2024+ %": ST_[(li, sg)]["first_h"]})
    rs = BBb[bh_].dropna(subset=["lab"]); A_ = roc_auc_score(rs.lab, rs.S)
    BAR[BH] = dict(model=MB, month=bm[-1], PG=PGb, PL=PLb, STATS=ST_, auc=A_)
    print(f"\n■ {BH} saat ±1σ — bariyer AUC 2024+ {A_:.4f} · {time.time()-t0:.0f} sn"); display(pd.DataFrame(rows_).round(2).set_index(["Güven", "Yön"]))
print("Not: bariyerlere ufuk içinde hiç dokunulmayan durumlar hesaba katılmaz (tablo: dokunulan sinyaller arasında hangisi önce geldi).")

baslik("2c) ⭐ EN GÜÇLÜ SİNYAL — 4 saat ve 8 saat aynı anda 'Çok güçlü YUKARI' (Binance geçmişi)")
J = R[4]["SF"].join(R[8]["SF"], lsuffix="4", rsuffix="8").dropna(subset=["S4", "T104", "S8", "T108", "y4", "y8"])
a4 = (J.S4 > 0) & (J.C4 >= J.T104); a8 = (J.S8 > 0) & (J.C8 >= J.T108); AGR = {}; wkJ = (J.index[-1] - J.index[0]).days / 7; hJ = J.index >= pd.Timestamp(HOLD_START, tz="UTC")
print("(CANLI ÖLÇÜM — her saat kontrol, sinyalin ilk ortaya çıktığı an; aynı sinyal 8 saat boyunca bir kez)")
for nm, m in [("yalnız 4s güçlü", a4 & ~a8), ("yalnız 8s güçlü", a8 & ~a4), ("ikisi birden", a4 & a8)]:
    ev = events(m.values, 8)
    for Hh in (4, 8):
        rr_ = np.exp(J[f"y{Hh}"].values[ev]) - 1; rh_ = np.exp(J[f"y{Hh}"].values[ev[hJ[ev]]]) - 1
        AGR[(nm, Hh)] = dict(n=len(ev), wk=len(ev) / wkJ, acc=(rr_ > 0).mean() * 100, acc_h=(rh_ > 0).mean() * 100, gross=rr_.mean() * 100)
        print(f"{nm:16s} → {Hh}s sonucu: n={len(ev):4d} (haftada {len(ev)/wkJ:.1f}) · isabet %{AGR[(nm, Hh)]['acc']:.1f} (2024+ %{AGR[(nm, Hh)]['acc_h']:.1f}) · brüt %{AGR[(nm, Hh)]['gross']:+.3f}")

baslik("2g) ⭐ SONRASI ALTCOİNLER — BTC ⭐ geldiğinde 8 saat içinde altcoinlerin yükselme oranı (canlı ölçüm, 2023–bugün)")
ALT_LIST = ["ETHUSDT", "BNBUSDT", "SOLUSDT", "ADAUSDT", "DOTUSDT", "XRPUSDT", "DOGEUSDT"]   # test edildi: 2023–24 seçim, 2025–26 doğrulama
def fetch_1h_sym(sym, start_ms, end_ms):
    rows, cur = [], int(start_ms)
    while cur < end_ms:
        dt = None
        for url in EP:
            try:
                r = requests.get(url, params=dict(symbol=sym, interval="1h", startTime=cur, endTime=int(end_ms), limit=1000), timeout=20)
                if r.status_code == 200: dt = r.json(); break
            except Exception: pass
        if not dt: break
        rows += dt; cur = dt[-1][0] + 3_600_000
        if len(dt) < 1000: break
    if not rows: return None
    df = pd.DataFrame([x[:5] for x in rows]).astype(float)
    s = pd.Series(df[4].values, index=pd.to_datetime(df[0], unit="ms", utc=True) + pd.Timedelta(hours=1)); s = s[s.index <= pd.Timestamp.now(tz="UTC")]
    return s[~s.index.duplicated()].sort_index()
_A0 = pd.Timestamp("2023-01-01", tz="UTC"); star_ev = J.index[events((a4 & a8).values, 8)]; star_ev = star_ev[star_ev >= _A0]; ALTSTAR = {}
for sym in ALT_LIST:
    try:
        px_ = fetch_1h_sym(sym, (_A0 - pd.Timedelta(days=2)).timestamp() * 1000, time.time() * 1000)
        R_ = (px_.shift(-8) / px_ - 1).dropna(); R_ = R_[R_.index >= _A0]; r_ = R_.reindex(star_ev).dropna()
        if len(r_) < 50: continue
        nm_ = sym.replace("USDT", ""); ALTSTAR[nm_] = dict(n=len(r_), up=(r_ > 0).mean() * 100, base=(R_ > 0).mean() * 100, adv=(r_.mean() - R_.mean()) * 100)
        print(f"{nm_:5s} ⭐ sonrası 8 saatte yükselme %{ALTSTAR[nm_]['up']:.1f} (rastgele an %{ALTSTAR[nm_]['base']:.1f}) · ortalama zamanlama avantajı %{ALTSTAR[nm_]['adv']:+.3f} · n={len(r_)}")
    except Exception as e: print(f"{sym}: alınamadı ({str(e)[:60]})")
ALT_SHOW = sorted([(v["up"], k) for k, v in ALTSTAR.items() if v["up"] >= 58], reverse=True)
ALT_LINE = ("🪙 Geçmişte bu sinyalden 8 saat sonra yükselme oranı: " + " · ".join(f"{k} %{u:.0f}" for u, k in ALT_SHOW) +
            " (rastgele an ~%50; ortalama kazanç avantajı küçük — alımları dağıtmak için zamanlama bilgisi)") if ALT_SHOW else ""
print(ALT_LINE or "(yükselme oranı %58'i geçen altcoin yok — satır gösterilmeyecek)")

baslik("2f) 🟢 A SINIFI — 1s + 4s + 8s sinyallerinin ortalama yüzdeliği ≥ 0,85 (sonuç: 4 saat sonra, canlı ölçüm)")
def s_final(H): return (cz(R[1]["ST"]) if H == 1 else R[H]["SF"].S)
AC = pd.DataFrame({H: rpct(s_final(H)) for H in CFG}).dropna(); AC["m"] = AC.mean(axis=1); AC["y4"] = R[4]["D"].y.reindex(AC.index); AC = AC.dropna(subset=["y4"])
evA = events((AC.m >= 0.85).values, 4); rA_ = np.exp(AC.y4.values[evA]) - 1; hAC = AC.index >= pd.Timestamp(HOLD_START, tz="UTC"); rAh = np.exp(AC.y4.values[evA[hAC[evA]]]) - 1
loA, hiA = wboot(rA_, AC.index[evA]); wkAC = (AC.index[-1] - AC.index[0]).days / 7
ACLS = dict(n=len(evA), wk=len(evA) / wkAC, acc=(rA_ > 0).mean() * 100, acc_h=(rAh > 0).mean() * 100, gross=rA_.mean() * 100, lo=loA * 100, hi=hiA * 100,
            base=(np.exp(AC.y4.values) - 1 > 0).mean() * 100)
print(f"A sınıfı: {ACLS['n']} sinyal (haftada {ACLS['wk']:.1f}) · 4s isabet %{ACLS['acc']:.1f} (2024+ %{ACLS['acc_h']:.1f}) · brüt %{ACLS['gross']:+.3f} [%90: {ACLS['lo']:+.3f}, {ACLS['hi']:+.3f}]"
      f" · karşılaştırma: rastgele saat %{ACLS['base']:.1f}")
baslik("2h) ⏰ 4 SAAT — SAATE GÖRE EŞİK: iyi saat dilimlerinde 'Güçlü' yukarı sinyaller de bildirilir (canlı ölçüm)")
S4F = R[4]["SF"].dropna(subset=["S", "T30", "T10", "y"]); blk4 = np.asarray(S4F.index.hour // 4)
g30 = ((S4F.S > 0) & (S4F.C >= S4F.T30)).values; c10 = ((S4F.S > 0) & (S4F.C >= S4F.T10)).values; BLK = {}
for b in range(6):
    ev = events(g30 & (blk4 == b), 4); r_ = S4F.y.values[ev]; BLK[b] = dict(n=len(ev), acc=(r_ > 0).mean() * 100 if len(ev) else float("nan"))
    tr0 = (b * 4 + 3) % 24
    print(f"   {b*4:02d}–{b*4+3:02d} UTC (TR {tr0:02d}:00–{(tr0+3)%24:02d}:59): 'Güçlü+ YUKARI' 4s isabet %{BLK[b]['acc']:.1f} (n={BLK[b]['n']})")
GOOD_BLK = [b for b, v in BLK.items() if v["n"] >= 100 and v["acc"] >= 58]
evT = events(g30 & ~c10 & np.isin(blk4, GOOD_BLK), 4); rT = np.exp(S4F.y.values[evT]) - 1; hT = S4F.index[evT] >= pd.Timestamp(HOLD_START, tz="UTC")
wkT = (S4F.index[-1] - S4F.index[0]).days / 7
IYI = dict(n=len(evT), wk=len(evT) / wkT, acc=(rT > 0).mean() * 100 if len(evT) else float("nan"), acc_h=(rT[hT] > 0).mean() * 100 if hT.any() else float("nan"),
           gross=rT.mean() * 100 if len(evT) else float("nan"))
IYI_ON = len(GOOD_BLK) > 0 and IYI["n"] >= 100 and IYI["acc"] >= 56                       # kendini denetler: Binance'te tutmazsa bildirim kapalı
print(f"İyi saat dilimleri (UTC blokları): {GOOD_BLK} · bu dilimlerde 'Güçlü' (çok güçlü olmayan) yukarı sinyal: {IYI['n']} (haftada {IYI['wk']:.1f}) · "
      f"4s isabet %{IYI['acc']:.1f} (2024+ %{IYI['acc_h']:.1f}) → {'✅ bildirim AÇIK' if IYI_ON else '❌ bildirim kapalı (yeterince isabetli değil)'}")

baslik("2i) 💥 TESLİMİYET ONAYI ve 🎯 BARİYER UYUMU (Binance verisiyle eşikler ve canlı ölçüm)")
P2_all = path2_features(o.close, HHM, MIC); TF = tes_features(o, MIC, P2_all)
Kp = (TF.index >= pd.Timestamp("2017-09-01", tz="UTC")) & (TF.index < pd.Timestamp("2020-01-01", tz="UTC"))
TES_THR = [[(f, op, float(TF.loc[Kp, f].quantile(int(q) / 100))) for f, op, q in rule] for rule in TES_RULES]
U_tes = tes_eval(TF, TES_THR)
S1F = frame_from_S(cz(R[1]["ST"])).dropna(subset=["S", "T10"]); y1 = R[1]["D"].y.reindex(S1F.index); m10 = ((S1F.S > 0) & (S1F.C >= S1F.T10)) & y1.notna()
hold1 = S1F.index >= pd.Timestamp(HOLD_START, tz="UTC"); u_ = U_tes.reindex(S1F.index).fillna(False).values
def _acc(mask):
    ev = events(mask, 1); r = y1.values[ev]; hh = hold1[ev]; return dict(n=len(ev), acc=(r > 0).mean() * 100 if len(ev) else float("nan"), acc_h=(r[hh] > 0).mean() * 100 if hh.any() else float("nan"))
TES = dict(on=_acc(m10.values & u_), off=_acc(m10.values & ~u_))
print(f"1s çok güçlü ↑ + 💥 teslimiyet onayı: {TES['on']['n']} sinyal · isabet %{TES['on']['acc']:.1f} (2024+ %{TES['on']['acc_h']:.1f}) | onaysız: %{TES['off']['acc']:.1f} (2024+ %{TES['off']['acc_h']:.1f})")
Sb8 = signal_frame(BAR[8]["PG"], BAR[8]["PL"], FA["r8"], False).S; S4F2 = R[4]["SF"].dropna(subset=["S", "T30", "y"]); b8 = Sb8.reindex(S4F2.index)
g4 = ((S4F2.S > 0) & (S4F2.C >= S4F2.T30)).values; hold4 = S4F2.index >= pd.Timestamp(HOLD_START, tz="UTC")
def _acc4(mask):
    ev = events(mask, 4); r = S4F2.y.values[ev]; hh = hold4[ev]; return dict(n=len(ev), acc=(r > 0).mean() * 100 if len(ev) else float("nan"), acc_h=(r[hh] > 0).mean() * 100 if hh.any() else float("nan"))
BUY = dict(uyumlu=_acc4(g4 & (b8 > 0).values), celiskili=_acc4(g4 & (b8 < 0).values))
print(f"4s güçlü+ ↑ · bariyer UYUMLU: %{BUY['uyumlu']['acc']:.1f} (2024+ %{BUY['uyumlu']['acc_h']:.1f}, n={BUY['uyumlu']['n']}) | ÇELİŞKİLİ: %{BUY['celiskili']['acc']:.1f} (2024+ %{BUY['celiskili']['acc_h']:.1f}, n={BUY['celiskili']['n']})")
print(f"\n⏱ hazırlık {(time.time()-T0)/60:.1f} dk")

# ================= 3) CANLI PANEL + TELEGRAM =================
# ================= KAYIT =================
KEEP = pd.Timedelta(days=70); cutk = lambda s: s[s.index >= s.index[-1] - KEEP]
state = dict(created=pd.Timestamp.now(tz="UTC"), FEATS=FEATS, FEATS1=FEATS1, FEATS4=FEATS4, AGR=AGR, ACLS=ACLS, ALT_LINE=ALT_LINE, ALTSTAR=ALTSTAR, GOOD_BLK=GOOD_BLK, IYI=IYI, IYI_ON=IYI_ON, BLK=BLK, TES_THR=TES_THR, TES=TES, BUY=BUY, MIC_TAIL=MIC.iloc[-1500:], HHM_TAIL=HHM.iloc[-1500:], BK=BK, BHS=BHS,
             R={H: dict(model=R[H]["model"], month=R[H]["month"], PG=cutk(R[H]["PG"]), PL=cutk(R[H]["PL"]), QM=R[H]["QM"], QC=R[H]["QC"], STATS=R[H]["STATS"],
                        A_h=R[H]["A_h"], z=R[H]["z"], verdict=R[H]["verdict"]) for H in CFG},
             ST=cutk(R[1]["ST"]), STACK=R[1]["stack"],
             BAR={BH: dict(model=BAR[BH]["model"], month=BAR[BH]["month"], PG=cutk(BAR[BH]["PG"]), PL=cutk(BAR[BH]["PL"]), STATS=BAR[BH]["STATS"], auc=BAR[BH]["auc"]) for BH in BHS})
os.makedirs("durum", exist_ok=True)
with gzip.open("durum/model.pkl.gz", "wb") as f: pickle.dump(state, f)
open("egitim_raporu.md", "w").write(f"# Aylık eğitim raporu — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n\n" + "\n\n".join(RAPOR))
a4_, a8_ = AGR[("ikisi birden", 4)], AGR[("ikisi birden", 8)]
tg_send(f"🧠 Aylık eğitim tamamlandı ({(time.time()-T0)/60:.0f} dk).\n" + "\n".join(f"{CFG[H]['ad']}: AUC 2024+ {R[H]['A_h']:.3f} (z={R[H]['z']:.1f}) {R[H]['verdict']}" for H in CFG)
        + f"\n⭐ en güçlü (canlı ölçüm): 4s %{a4_['acc']:.1f} · 8s %{a8_['acc']:.1f} · haftada ~{a4_['wk']:.1f}" + f"\n🟢 A sınıfı: 4s %{ACLS['acc']:.1f} · haftada ~{ACLS['wk']:.0f}" + f"\n💥 teslimiyet onayı (1s): %{TES['on']['acc']:.1f} · 🎯 bariyer uyumlu (4s): %{BUY['uyumlu']['acc']:.1f} / çelişkili %{BUY['celiskili']['acc']:.1f}" + f"\n⏰ iyi saat dilimi (4s güçlü): %{IYI['acc']:.1f} · haftada ~{IYI['wk']:.0f} · {'açık' if IYI_ON else 'kapalı'}")
_print(f"✅ kaydedildi: durum/model.pkl.gz ({os.path.getsize('durum/model.pkl.gz')/1e6:.1f} MB) · toplam {(time.time()-T0)/60:.1f} dk")
