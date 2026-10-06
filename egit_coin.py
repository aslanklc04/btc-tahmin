# egit_coin.py — AYLIK: altcoin modellerini eğitir (BTC'ye dokunmaz). Kullanım: python egit_coin.py ETHUSDT
# v35 ile AYNI yöntem: 1s/4s/8s yürüyen test (aylık eğitim, yalnız geçmiş veri) + 1s yığınlama.
# Bildirilen sinyaller (çoklu coin testi, 2024+ canlı ölçüm, önceden sabit ölçüt: isabet ≥ %58 ve BTC'den farklı saatlerde haftada ≥ 1 sinyal / ≥ %56):
#   ETH: ⭐ · 4s Çok güçlü ↑ · 🟢 A sınıfı   |   BNB: ⭐ · 4s Çok güçlü ↑ · 🟢 A sınıfı   |   DOGE: ⭐
# Kendini denetler: her ay bir sinyalin 2024+ isabeti %58'in altına düşerse o sinyalin bildirimi kapanır.
import os, sys, gzip, pickle, lightgbm as lgb
from concurrent.futures import ThreadPoolExecutor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from ortak import *
from ortak import _mzip
COINS = {"ETHUSDT": dict(micro="2017-09-01", test="2020-01-01", sinyaller=["star", "u4", "acls"]),
         "BNBUSDT": dict(micro="2017-12-01", test="2020-01-01", sinyaller=["star", "u4", "acls"]),
         "DOGEUSDT": dict(micro="2019-08-01", test="2021-01-01", sinyaller=["star"])}
ESIK = 58.0                                                                                   # 2024+ isabet alt sınırı (öz-denetim)
SYM = sys.argv[1]; CF = COINS[SYM]; NM = SYM.replace("USDT", ""); T0 = time.time(); HOLD = pd.Timestamp(HOLD_START, tz="UTC")
def log(*a): print(f"[{time.time()-T0:5.0f} sn] {NM}:", *a, flush=True)
# ---------------- 1) veri ----------------
o = fetch_1h(pd.Timestamp("2017-08-17", tz="UTC").timestamp() * 1000, time.time() * 1000, sym=SYM)
log(f"{len(o):,} saat · {o.index[0]:%Y-%m-%d} → {o.index[-1]:%Y-%m-%d %H:%M} UTC")
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
    R[H] = dict(model=model, month=months[-1], PG=PG.dropna(), PL=PL.dropna(), D=D); log(f"{H}s yürüyen test bitti")
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
    ev = events(np.asarray(mask), H); r = np.exp(np.asarray(y)[ev]) - 1; hh = idx[ev] >= HOLD; wk = (idx[-1] - idx[0]).days / 7
    return dict(n=len(ev), n_h=int(hh.sum()), wk=len(ev) / wk, acc=(r > 0).mean() * 100 if len(ev) else float("nan"),
                acc_h=(r[hh] > 0).mean() * 100 if hh.any() else float("nan"), gross_h=r[hh].mean() * 100 if hh.any() else float("nan"))
A4 = SF[4].dropna(subset=["S", "T30", "y"]); u4m = (A4.S > 0) & (A4.C >= A4.T10)
SIG = {"u4": dict(ad="4s Çok güçlü ↑", H=4, **_st(u4m.values, A4.y.values, A4.index, 4))}
J = SF[4].join(SF[8], lsuffix="4", rsuffix="8").dropna(subset=["S4", "T104", "S8", "T108", "y4", "y8"])
sm_ = ((J.S4 > 0) & (J.C4 >= J.T104) & (J.S8 > 0) & (J.C8 >= J.T108)).values
s4, s8 = _st(sm_, J.y4.values, J.index, 8), _st(sm_, J.y8.values, J.index, 8)
SIG["star"] = dict(ad="⭐ en güçlü", H=8, **s8, acc4=s4["acc"], acc_h4=s4["acc_h"])
AC = pd.DataFrame({H: rpct(SF[H].S) for H in CFG}).dropna(); AC["m"] = AC.mean(axis=1); AC["y4"] = R[4]["D"].y.reindex(AC.index); AC = AC.dropna(subset=["y4"])
SIG["acls"] = dict(ad="🟢 A sınıfı", H=4, **_st((AC.m >= 0.85).values, AC.y4.values, AC.index, 4))
for k, v in SIG.items():
    olcu = v["acc_h4"] if k == "star" else v["acc_h"]                                         # ⭐ ölçütü 4 saat sonucu (çoklu coin testindeki gibi)
    v["on"] = bool(k in CF["sinyaller"] and v["n_h"] >= 50 and olcu >= ESIK); v["olcu"] = olcu
    log(f"{v['ad']}: haftada {v['wk']:.1f} · isabet %{v['acc']:.1f} (2024+ %{olcu:.1f}, n={v['n_h']}) → {'AÇIK' if v['on'] else 'kapalı'}")
# ---------------- 4) kayıt ----------------
KEEP = pd.Timedelta(days=70); cutk = lambda s: s[s.index >= s.index[-1] - KEEP]
state = dict(created=pd.Timestamp.now(tz="UTC"), sym=SYM, FEATS=FEATS, FEATS1=FEATS1, FEATS4=FEATS4, SIG=SIG, AUC=AUC,
             R={H: dict(model=R[H]["model"], month=R[H]["month"], PG=cutk(R[H]["PG"]), PL=cutk(R[H]["PL"])) for H in CFG},
             ST=cutk(ST), STACK=STACK, MIC_TAIL=MIC.iloc[-1500:], HHM_TAIL=HHM.iloc[-1500:])
os.makedirs("durum", exist_ok=True)
with gzip.open(f"durum/model_{SYM}.pkl.gz", "wb") as f: pickle.dump(state, f)
rap = (f"# 🪙 {NM} aylık eğitim — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n\n" + "\n".join(f"- {H} saat: AUC 2024+ {AUC[H]:.4f}" for H in CFG) + "\n\n"
       "| Sinyal | Haftada | İsabet | İsabet 2024+ | 2024+ sinyal | Brüt 2024+ % | Bildirim |\n|---|---|---|---|---|---|---|\n"
       + "\n".join(f"| {v['ad']} | {v['wk']:.1f} | %{v['acc']:.1f} | %{v['olcu']:.1f} | {v['n_h']} | {v['gross_h']:+.3f} | {'✅ açık' if v['on'] else '— kapalı'} |" for v in SIG.values()) + "\n")
open(f"durum/rapor_{SYM}.md", "w").write(rap)
acik = [v for v in SIG.values() if v["on"]]
tg_send(f"🪙🧠 {NM} aylık eğitimi tamamlandı ({(time.time()-T0)/60:.0f} dk) · AUC 2024+ 1s {AUC[1]:.3f} · 4s {AUC[4]:.3f} · 8s {AUC[8]:.3f}\n"
        + ("Açık bildirimler: " + " · ".join(f"{v['ad']} %{v['olcu']:.0f} (haftada ~{v['wk']:.1f})" for v in acik) if acik else "Bu ay hiçbir sinyal %58 ölçütünü geçmedi — bildirim kapalı."))
log(f"✅ kaydedildi: durum/model_{SYM}.pkl.gz ({os.path.getsize(f'durum/model_{SYM}.pkl.gz')/1e6:.1f} MB) · {(time.time()-T0)/60:.1f} dk")
