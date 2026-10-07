# egit_coin.py — AYLIK: altcoin modellerini eğitir (BTC'ye dokunmaz). Kullanım: python egit_coin.py ETHUSDT   (v2: fiyat aralığı + kararlılık kuralı)
# v35 ile AYNI yöntem: 1s/4s/8s yürüyen test (aylık eğitim, yalnız geçmiş veri) + 1s yığınlama.
# Her coin için üç sinyal adayı: ⭐ (4s+8s Çok güçlü ↑) · 4s Çok güçlü ↑ · 🟢 A sınıfı. Bildirim yalnız öz-denetimi geçen sinyalde açılır:
#   değerlendirme döneminde (2024+ ya da coin'in test başlangıcından beri) isabet ≥ %58, ≥ 50 sinyal, dönemin iki yarısında da ≥ %55. Her ay yeniden denetlenir.
# Her ufuk için fiyat aralığı modelleri (beklenen fiyat + %80 aralık, egit.py ile aynı yöntem) de eğitilir.
import os, sys, gzip, pickle, lightgbm as lgb
from concurrent.futures import ThreadPoolExecutor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from ortak import *
from ortak import _mzip
COINS = {"ETHUSDT": dict(micro="2017-09-01", test="2020-01-01"), "BNBUSDT": dict(micro="2017-12-01", test="2020-01-01"),
         "DOGEUSDT": dict(micro="2019-08-01", test="2021-01-01"), "BTCUSDT": dict(micro="2017-09-01", test="2020-01-01")}
# Listede olmayan coin: ayarlar listeleme tarihinden otomatik (dakika arşivi: listelemeden sonraki ay · test: en az 1 yıl eğitim verisinden sonra)
SINYALLER = ["star", "u4", "acls"]
ESIK, YARI_ESIK, MIN_N = 58.0, 55.0, 50   # öz-denetim: 2024+ (ya da test başlangıcından beri) isabet ≥ %58, ≥ 50 sinyal, dönemin iki yarısında da ≥ %55
SYM = sys.argv[1]; NM = SYM.replace("USDT", ""); T0 = time.time(); HOLD = pd.Timestamp(HOLD_START, tz="UTC")
def log(*a): print(f"[{time.time()-T0:5.0f} sn] {NM}:", *a, flush=True)
# ---------------- 1) veri ----------------
o = fetch_1h(pd.Timestamp("2017-08-17", tz="UTC").timestamp() * 1000, time.time() * 1000, sym=SYM)
log(f"{len(o):,} saat · {o.index[0]:%Y-%m-%d} → {o.index[-1]:%Y-%m-%d %H:%M} UTC")
if SYM in COINS: CF = COINS[SYM]
else:
    l0 = o.index[0]; mic = (l0 + pd.offsets.MonthBegin(1)).normalize(); tst = max(pd.Timestamp("2020-01-01", tz="UTC"), (l0 + pd.Timedelta(days=365) + pd.offsets.MonthBegin(1)).normalize())
    CF = dict(micro=mic.strftime("%Y-%m-%d"), test=tst.strftime("%Y-%m-%d"))
EVAL0 = max(HOLD, pd.Timestamp(CF["test"], tz="UTC")); log(f"dakika arşivi {CF['micro']} · test {CF['test']} · değerlendirme {EVAL0:%Y-%m-%d}+")
FA = features(o); FEATS = list(FA.columns)
cur_m = pd.Timestamp.now(tz="UTC").normalize().replace(day=1)
yms = [d.strftime("%Y-%m") for d in pd.date_range(pd.Timestamp(CF["micro"], tz="UTC"), cur_m - pd.Timedelta(days=1), freq="MS")]
with ThreadPoolExecutor(8) as ex: parts = list(ex.map(lambda ym: _mzip(ym, SYM), yms))
mins = [to_min(p) for p in parts if p is not None]
tail_ = fetch_1m(mins[-1].index[-1].timestamp() * 1000, time.time() * 1000, sym=SYM)
M1 = pd.concat(mins + ([tail_] if tail_ is not None else [])); M1 = M1[~M1.index.duplicated(keep="last")].sort_index()
log(f"{len(M1):,} dakika ({sum(p is not None for p in parts)}/{len(yms)} aylık arşiv)")
MIC = micro_features(M1); FA1 = FA.join(MIC.reindex(FA.index)); FEATS1 = FEATS + list(MIC.columns)
HHM = hourly_cv(M1); P2 = path2_features(o.close, HHM, MIC); FA4 = FA.join(P2); FEATS4 = FEATS + list(P2.columns)
# ---------------- 2) yürüyen test (egit.py ile aynı ayarlar) ----------------
R = {}
for H, cf in CFG.items():
    D = (FA1 if H == 1 else FA4 if H == 4 else FA).copy(); D["y"] = np.log(o.close.shift(-H) / o.close); D = D.iloc[720:]; DL = D.dropna(subset=["y"])
    FE = FEATS1 if H == 1 else FEATS4 if H == 4 else FEATS
    def train_month(ms, DL=DL, H=H, FE=FE, yrs_list=cf["years"]):
        parts_ = []
        for yrs in yrs_list:
            tr = DL[DL.index < ms - pd.Timedelta(hours=H)]; tr = tr[tr.index >= tr.index[-1] - pd.Timedelta(days=365 * yrs)]
            yb = (tr.y > 0).astype(int); k = int(len(tr) * .85)
            g = lgb.LGBMClassifier(n_estimators=600, learning_rate=0.03, num_leaves=15, min_child_samples=300, subsample=0.7, subsample_freq=1,
                                   colsample_bytree=0.5, reg_lambda=10, verbose=-1).fit(tr[FE].iloc[:k - H], yb.iloc[:k - H],
                                   eval_set=[(tr[FE].iloc[k:], yb.iloc[k:])], callbacks=[lgb.early_stopping(50, verbose=False)])
            z = ZF(tr[FE]); lo = LogisticRegression(C=0.01, max_iter=500).fit(z(tr[FE]), yb); parts_.append((g, z, lo))
        return HModel(parts_, FE)
    months = pd.date_range(pd.Timestamp(CF["test"], tz="UTC"), D.index[-1], freq="MS"); PG = pd.Series(np.nan, index=D.index); PL = PG.copy(); model = None
    for i, ms in enumerate(months):
        me = months[i + 1] if i + 1 < len(months) else D.index[-1] + pd.Timedelta(hours=1); rows = D[(D.index >= ms) & (D.index < me)]
        if not len(rows): continue
        model = train_month(ms); pg, pl = model(rows); PG.loc[rows.index], PL.loc[rows.index] = pg, pl
    cut = DL.index[-1] - pd.Timedelta(days=30); trq = DL[(DL.index < cut - pd.Timedelta(hours=H)) & (DL.index >= cut - pd.Timedelta(days=365 * 3))]; cal = DL[DL.index >= cut]
    QM = {q: lgb.LGBMRegressor(objective="quantile", alpha=q, n_estimators=400, learning_rate=0.03, num_leaves=15, min_child_samples=300,
                               subsample=0.7, subsample_freq=1, colsample_bytree=0.5, verbose=-1).fit(trq[FEATS], trq.y) for q in (0.1, 0.5, 0.9)}
    qc = np.sort(np.column_stack([QM[q].predict(cal[FEATS]) for q in (0.1, 0.5, 0.9)]), axis=1)
    QC = float(np.quantile(np.maximum(qc[:, 0] - cal.y.values, cal.y.values - qc[:, 2]), 0.8 * (1 + 1 / len(cal))))
    R[H] = dict(model=model, month=months[-1], PG=PG.dropna(), PL=PL.dropna(), D=D, QM=QM, QC=QC); log(f"{H}s yürüyen test bitti")
def base_S(H): return signal_frame(R[H]["PG"], R[H]["PL"], FA[f"r{H}"], False).S
JS = pd.DataFrame({"S1": base_S(1), "S4": base_S(4), "S8": base_S(8)}).dropna(); JS["y1"] = R[1]["D"].y.reindex(JS.index)
ST = pd.Series(np.nan, index=JS.index); STACK = None; sm = pd.date_range(JS.index[0] + pd.Timedelta(days=90), JS.index[-1], freq="MS")
for i, ms in enumerate(sm):
    me = sm[i + 1] if i + 1 < len(sm) else JS.index[-1] + pd.Timedelta(hours=1)
    tr = JS[JS.index < ms - pd.Timedelta(hours=1)].dropna(subset=["y1"]); te = JS[(JS.index >= ms) & (JS.index < me)]
    if len(tr) < 2000 or not len(te): continue
    STACK = LogisticRegression(C=0.1).fit(tr[["S1", "S4", "S8"]].clip(-5, 5), (tr.y1 > 0).astype(int)); ST.loc[te.index] = STACK.decision_function(te[["S1", "S4", "S8"]].clip(-5, 5))
ST = ST.dropna()
SF = {1: frame_from_S(cz(ST)), 4: signal_frame(R[4]["PG"], R[4]["PL"], FA.r4, False), 8: signal_frame(R[8]["PG"], R[8]["PL"], FA.r8, False)}
for H in CFG: SF[H]["y"] = R[H]["D"].y.reindex(SF[H].index)
# ---------------- 3) sinyal istatistikleri (canlı ölçüm: ilk ortaya çıktığı saat, H saat tekrar sayılmaz) ----------------
AUC = {}
for H in CFG:
    B = SF[H][SF[H].index.hour % H == 0].dropna(subset=["S", "T30", "y"]); h = B.index >= HOLD; AUC[H] = roc_auc_score(B.y[h] > 0, B.S[h])
def _st(mask, y, idx, H):
    ev = events(np.asarray(mask), H); r = np.exp(np.asarray(y)[ev]) - 1; hh = idx[ev] >= EVAL0; wk = (idx[-1] - idx[0]).days / 7
    rh = r[hh]; th = idx[ev][hh]; mid = th[len(th) // 2] if len(th) else None; a1 = rh[th < mid] if len(th) else rh; a2 = rh[th >= mid] if len(th) else rh
    return dict(n=len(ev), n_h=int(hh.sum()), wk=len(ev) / wk, acc=(r > 0).mean() * 100 if len(ev) else float("nan"),
                acc_h=(rh > 0).mean() * 100 if len(rh) else float("nan"), gross_h=rh.mean() * 100 if len(rh) else float("nan"),
                h1=(a1 > 0).mean() * 100 if len(a1) else float("nan"), h2=(a2 > 0).mean() * 100 if len(a2) else float("nan"))
A4 = SF[4].dropna(subset=["S", "T30", "y"]); u4m = (A4.S > 0) & (A4.C >= A4.T10)
SIG = {"u4": dict(ad="4s Çok güçlü ↑", H=4, **_st(u4m.values, A4.y.values, A4.index, 4))}
J = SF[4].join(SF[8], lsuffix="4", rsuffix="8").dropna(subset=["S4", "T104", "S8", "T108", "y4", "y8"])
sm_ = ((J.S4 > 0) & (J.C4 >= J.T104) & (J.S8 > 0) & (J.C8 >= J.T108)).values
s4, s8 = _st(sm_, J.y4.values, J.index, 8), _st(sm_, J.y8.values, J.index, 8)
SIG["star"] = dict(ad="⭐ en güçlü", H=8, **s8, acc4=s4["acc"], acc_h4=s4["acc_h"], h1_4=s4["h1"], h2_4=s4["h2"])
AC = pd.DataFrame({H: rpct(SF[H].S) for H in CFG}).dropna(); AC["m"] = AC.mean(axis=1); AC["y4"] = R[4]["D"].y.reindex(AC.index); AC = AC.dropna(subset=["y4"])
SIG["acls"] = dict(ad="🟢 A sınıfı", H=4, **_st((AC.m >= 0.85).values, AC.y4.values, AC.index, 4))
for k, v in SIG.items():
    olcu, y1_, y2_ = (v["acc_h4"], v["h1_4"], v["h2_4"]) if k == "star" else (v["acc_h"], v["h1"], v["h2"])   # ⭐ ölçütü 4 saat sonucu (çoklu coin testindeki gibi)
    v["on"] = bool(k in SINYALLER and v["n_h"] >= MIN_N and olcu >= ESIK and y1_ >= YARI_ESIK and y2_ >= YARI_ESIK); v["olcu"], v["y1"], v["y2"] = olcu, y1_, y2_
    log(f"{v['ad']}: haftada {v['wk']:.1f} · isabet %{v['acc']:.1f} ({EVAL0:%Y}+ %{olcu:.1f}, n={v['n_h']}, yarılar %{y1_:.0f}/%{y2_:.0f}) → {'AÇIK' if v['on'] else 'kapalı'}")
if os.environ.get("DISA_AKTAR"):                                                               # tarama raporu için saatlik sinyal/sonuç tablosu
    EX = pd.DataFrame({"u4": u4m.reindex(SF[4].index).fillna(False)}, index=SF[4].index)
    EX["star"] = pd.Series(sm_, index=J.index).reindex(EX.index).fillna(False); EX["acls"] = (AC.m >= 0.85).reindex(EX.index).fillna(False)
    EX["y4"] = R[4]["D"].y.reindex(EX.index); EX["y8"] = R[8]["D"].y.reindex(EX.index); EX.to_pickle(f"disa_{SYM}.pkl")
# ---------------- 4) kayıt ----------------
KEEP = pd.Timedelta(days=70); cutk = lambda s: s[s.index >= s.index[-1] - KEEP]
state = dict(created=pd.Timestamp.now(tz="UTC"), sym=SYM, FEATS=FEATS, FEATS1=FEATS1, FEATS4=FEATS4, SIG=SIG, AUC=AUC,
             R={H: dict(model=R[H]["model"], month=R[H]["month"], PG=cutk(R[H]["PG"]), PL=cutk(R[H]["PL"]), QM=R[H]["QM"], QC=R[H]["QC"]) for H in CFG}, CF=CF, EVAL0=EVAL0,
             ST=cutk(ST), STACK=STACK, MIC_TAIL=MIC.iloc[-1500:], HHM_TAIL=HHM.iloc[-1500:])
os.makedirs("durum", exist_ok=True)
with gzip.open(f"durum/model_{SYM}.pkl.gz", "wb") as f: pickle.dump(state, f)
rap = (f"# 🪙 {NM} aylık eğitim — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n\n" + "\n".join(f"- {H} saat: AUC 2024+ {AUC[H]:.4f}" for H in CFG) + "\n\n"
       f"Değerlendirme dönemi: {EVAL0:%d.%m.%Y}+ · kural: isabet ≥ %{ESIK:.0f}, ≥ {MIN_N} sinyal, iki yarıda da ≥ %{YARI_ESIK:.0f}\n\n"
       "| Sinyal | Haftada | İsabet (tümü) | İsabet (değ.) | Sinyal (değ.) | 1. yarı | 2. yarı | Brüt (değ.) % | Bildirim |\n|---|---|---|---|---|---|---|---|---|\n"
       + "\n".join(f"| {v['ad']} | {v['wk']:.1f} | %{v['acc']:.1f} | %{v['olcu']:.1f} | {v['n_h']} | %{v['y1']:.1f} | %{v['y2']:.1f} | {v['gross_h']:+.3f} | {'✅ açık' if v['on'] else '— kapalı'} |" for v in SIG.values()) + "\n")
open(f"durum/rapor_{SYM}.md", "w").write(rap)
acik = [v for v in SIG.values() if v["on"]]
tg_send(f"🪙🧠 {NM} aylık eğitimi tamamlandı ({(time.time()-T0)/60:.0f} dk) · AUC 2024+ 1s {AUC[1]:.3f} · 4s {AUC[4]:.3f} · 8s {AUC[8]:.3f}\n"
        + ("Açık bildirimler: " + " · ".join(f"{v['ad']} %{v['olcu']:.0f} (haftada ~{v['wk']:.1f})" for v in acik) if acik else "Bu ay hiçbir sinyal %58 ölçütünü geçmedi — bildirim kapalı."))
log(f"✅ kaydedildi: durum/model_{SYM}.pkl.gz ({os.path.getsize(f'durum/model_{SYM}.pkl.gz')/1e6:.1f} MB) · {(time.time()-T0)/60:.1f} dk")
