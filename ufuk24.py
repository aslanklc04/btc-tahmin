# ufuk24.py — UZUN UFUK ARAŞTIRMASI (canlı sisteme dokunmaz): 8 / 24 / 72 saatlik yön modeli, coin başına. Kullanım: python ufuk24.py ETHUSDT
# Yöntem v35 ile aynı: aylık yeniden eğitim (yalnız geçmiş veri, etiketi belli olmamış son H saat eğitime girmez), LightGBM + lojistik, 3 ve 5 yıllık pencereler.
# Sinyal gücü: iki modelin son 30 güne göre z-skoru → Çok güçlü = son 30 günün en güçlü %10'u, Güçlü = %30'u. Sonuçlar disa24_{SYM}.pkl'e yazılır, ufuk24_rapor.py birleştirir.
# Ana soru (önceden sabit): 24 saatlik 'Çok güçlü ↑' sinyali, komisyon sonrası 8 saatlikten iyi mi ve coin'ler toplamında haftada kaç sinyal verir?
import os, sys, time, numpy as np, pandas as pd, lightgbm as lgb
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from ortak import *
SYM = sys.argv[1]; T0 = time.time()
def log(*a): print(f"[{time.time()-T0:5.0f} sn] {SYM}:", *a, flush=True)
HS = {8: [3, 5], 24: [3, 5], 72: [3, 5]}
PRESET = {"ETHUSDT": "2020-01-01", "BNBUSDT": "2020-01-01", "DOGEUSDT": "2021-01-01", "BTCUSDT": "2020-01-01"}
if os.environ.get("YEREL"):
    o = pd.read_pickle("/home/claude/lab2/data/o_1h.pkl")
    if SYM != "BTCUSDT": _rg = np.random.default_rng(len(SYM)); o = o.iloc[20000:].copy(); f_ = np.exp(np.cumsum(_rg.normal(0, 0.006, len(o)))); o[["open", "high", "low", "close"]] = o[["open", "high", "low", "close"]].mul(f_, axis=0)
    HS = {8: [3], 24: [3]}
else: o = fetch_1h(pd.Timestamp("2017-08-17", tz="UTC").timestamp() * 1000, time.time() * 1000, sym=SYM)
l0 = o.index[0]; TEST = pd.Timestamp(PRESET[SYM], tz="UTC") if SYM in PRESET else max(pd.Timestamp("2020-01-01", tz="UTC"), (l0 + pd.Timedelta(days=365) + pd.offsets.MonthBegin(1)).normalize())
if os.environ.get("YEREL"): TEST = pd.Timestamp("2022-06-01", tz="UTC")
log(f"{len(o):,} saat · {l0:%Y-%m-%d} → {o.index[-1]:%Y-%m-%d %H:%M} · test {TEST:%Y-%m}+")
FA = features(o); FEATS = list(FA.columns); EX = pd.DataFrame({"close": o.close})
for H, yl in HS.items():
    D = FA.copy(); D["y"] = np.log(o.close.shift(-H) / o.close); D = D.iloc[720:]; DL = D.dropna(subset=["y"])
    def train_month(ms):
        parts_ = []
        for yrs in yl:
            tr = DL[DL.index < ms - pd.Timedelta(hours=H)]; tr = tr[tr.index >= tr.index[-1] - pd.Timedelta(days=365 * yrs)]
            yb = (tr.y > 0).astype(int); k = int(len(tr) * .85)
            g = lgb.LGBMClassifier(n_estimators=600, learning_rate=0.03, num_leaves=15, min_child_samples=300, subsample=0.7, subsample_freq=1,
                                   colsample_bytree=0.5, reg_lambda=10, verbose=-1).fit(tr[FEATS].iloc[:k - H], yb.iloc[:k - H],
                                   eval_set=[(tr[FEATS].iloc[k:], yb.iloc[k:])], callbacks=[lgb.early_stopping(50, verbose=False)])
            z = ZF(tr[FEATS]); lo = LogisticRegression(C=0.01, max_iter=500).fit(z(tr[FEATS]), yb); parts_.append((g, z, lo))
        return HModel(parts_, FEATS)
    months = pd.date_range(TEST, D.index[-1], freq="MS"); PG = pd.Series(np.nan, index=D.index); PL = PG.copy()
    for i, ms in enumerate(months):
        me = months[i + 1] if i + 1 < len(months) else D.index[-1] + pd.Timedelta(hours=1); rows = D[(D.index >= ms) & (D.index < me)]
        if not len(rows): continue
        pg, pl = train_month(ms)(rows); PG.loc[rows.index], PL.loc[rows.index] = pg, pl
    SF = signal_frame(PG.dropna(), PL.dropna(), FA[f"r{H}"], False).reindex(EX.index)
    EX[f"S{H}"], EX[f"C{H}"], EX[f"T30_{H}"], EX[f"T10_{H}"] = SF.S, SF.C, SF.T30, SF.T10
    B = SF.join(D.y).dropna(subset=["S", "y"]).iloc[::H]; a24 = B.index >= pd.Timestamp("2024-01-01", tz="UTC")
    au = lambda m: roc_auc_score(B.y[m] > 0, B.S[m]) if m.sum() > 50 and (B.y[m] > 0).nunique() == 2 else float("nan")
    log(f"{H}s bitti · AUC ≤2023 {au(~a24):.4f} · 2024+ {au(a24):.4f}")
EX.astype("float32").to_pickle(f"disa24_{SYM}.pkl"); log("kaydedildi")
