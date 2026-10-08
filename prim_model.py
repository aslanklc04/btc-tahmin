# prim_model.py — COINBASE PRİMİ MODELİN İÇİNDE: primi filtre yerine modelin girdisi yaparsak 4 / 8 saatlik tahmin iyileşir mi? (canlı sisteme dokunmaz)
# Kullanım: python prim_model.py ETHUSDT 4   ·   Model: canlıyla aynı yöntem (LightGBM + lojistik, aylık yürüyen eğitim, yalnız geçmiş veri), temel özellikler = features().
# Varyantlar: TEMEL (fiyat özellikleri) · PRİM (+ 6 prim özelliği) · K × KARIŞTIRMA (prim özellikleri haftalık bloklar halinde zamanda karıştırılır: bilgi yok, dağılım aynı).
# Prim özellikleri (yalnız geçmiş): z (720 s) · z (168 s) · 1 / 4 / 24 saatlik değişim (720 s oynaklığa bölünmüş) · 24 s ortalamanın z'si. Coinbase'de olmadığı dönemler boş (NaN).
# Test 2022-01'den: seçim 2022–23, karar 2024+ (prim_model_rapor.py).
import os, sys, io, re, time, zipfile, requests, numpy as np, pandas as pd, lightgbm as lgb
from sklearn.linear_model import LogisticRegression
from ortak import *
SYM = sys.argv[1]; H = int(sys.argv[2]); YL = CFG[H]["years"]; NM = SYM[:-4]
K = int(os.environ.get("PM_K", 4)); TEST = pd.Timestamp("2022-01-01", tz="UTC"); T0 = time.time()
def log(*a): print(f"[{time.time()-T0:5.0f} sn] {SYM} {H}s:", *a, flush=True)
o = fetch_1h(pd.Timestamp("2017-08-17", tz="UTC").timestamp() * 1000, time.time() * 1000, sym=SYM); c = o.close; idx = o.index
def coinbase(nm):
    s = requests.Session(); s.headers.update({"User-Agent": "btc-tahmin-arastirma"}); out = []; cur = pd.Timestamp("2016-01-01", tz="UTC"); end = pd.Timestamp.now(tz="UTC").floor("h"); bos = 0
    r = s.get(f"https://api.exchange.coinbase.com/products/{nm}-USD", timeout=20)
    if r.status_code != 200: return None
    while cur < end:
        nx = min(cur + pd.Timedelta(hours=300), end)
        for k in range(5):
            try:
                r = s.get(f"https://api.exchange.coinbase.com/products/{nm}-USD/candles", params=dict(granularity=3600, start=cur.isoformat(), end=nx.isoformat()), timeout=20)
                if r.status_code == 429: time.sleep(1 + k); continue
                break
            except Exception: time.sleep(2)
        if r.status_code == 200: out += r.json()
        cur = nx; time.sleep(0.12)
    if not out: return None
    d = pd.DataFrame(out, columns=["t", "low", "high", "open", "close", "volume"]).drop_duplicates("t")
    return pd.Series(d.close.values.astype(float), index=pd.to_datetime(d.t, unit="s", utc=True) + pd.Timedelta(hours=1)).sort_index()
cb = coinbase(NM)
if cb is None: log("Coinbase verisi yok"); raise SystemExit(0)
cb.index = cb.index.astype("datetime64[ns, UTC]"); I = idx.astype("datetime64[ns, UTC]")
p = pd.Series(np.log(cb.reindex(I).ffill(limit=2).values / c.values), index=idx)
def z(x, n=720): return (x - x.rolling(n, min_periods=min(168, n)).mean()) / (x.rolling(n, min_periods=min(168, n)).std() + 1e-12)
sdp = p.diff().rolling(720, min_periods=168).std() + 1e-12
DER = pd.DataFrame({"pr_z720": z(p), "pr_z168": z(p, 168), "pr_d1": p.diff() / sdp, "pr_d4": p.diff(4) / (sdp * 2), "pr_d24": p.diff(24) / (sdp * np.sqrt(24)), "pr_m24z": z(p.rolling(24).mean())}, index=idx)
DER = DER.replace([np.inf, -np.inf], np.nan).astype("float32"); DF = list(DER.columns)
log(f"Coinbase {cb.index[0]:%Y-%m} → · test döneminde prim dolu oran %{100*DER[idx >= TEST].pr_z720.notna().mean():.0f}")
# ---------------- yürüyen test ----------------
FA = features(o); FEATS = list(FA.columns); y = np.log(c.shift(-H) / c)
def wf(X, FE):
    D = X.copy(); D["y"] = y; D = D.iloc[720:]; DL = D.dropna(subset=["y"]); PG = pd.Series(np.nan, index=D.index); PL = PG.copy(); model = None
    months = pd.date_range(max(TEST, (D.index[0] + pd.Timedelta(days=400)).normalize().replace(day=1)), D.index[-1], freq="MS")
    for i, ms in enumerate(months):
        me = months[i + 1] if i + 1 < len(months) else D.index[-1] + pd.Timedelta(hours=1); rows = D[(D.index >= ms) & (D.index < me)]
        if not len(rows): continue
        parts_ = []
        for yrs in YL:
            tr = DL[DL.index < ms - pd.Timedelta(hours=H)]; tr = tr[tr.index >= tr.index[-1] - pd.Timedelta(days=365 * yrs)]
            yb = (tr.y > 0).astype(int); k = int(len(tr) * .85)
            g = lgb.LGBMClassifier(n_estimators=600, learning_rate=0.03, num_leaves=15, min_child_samples=300, subsample=0.7, subsample_freq=1,
                                   colsample_bytree=0.5, reg_lambda=10, verbose=-1).fit(tr[FE].iloc[:k - H], yb.iloc[:k - H],
                                   eval_set=[(tr[FE].iloc[k:], yb.iloc[k:])], callbacks=[lgb.early_stopping(50, verbose=False)])
            zf = ZF(tr[FE]); zf.med, zf.mu, zf.sd = zf.med.fillna(0), zf.mu.fillna(0), zf.sd.fillna(1)
            lo_ = LogisticRegression(C=0.01, max_iter=500).fit(zf(tr[FE]), yb); parts_.append((g, zf, lo_))
        model = HModel(parts_, FE); pg, pl = model(rows); PG.loc[rows.index], PL.loc[rows.index] = pg, pl
    return PG.dropna(), PL.dropna(), model
OUT = pd.DataFrame({"close": c})
def kaydet(ad, PG, PL):
    sf = signal_frame(PG, PL, FA[f"r{H}"], False).reindex(idx); OUT[f"S_{ad}"], OUT[f"C_{ad}"], OUT[f"T10_{ad}"] = sf.S, sf.C, sf.T10
PG, PL, _ = wf(FA, FEATS); kaydet("temel", PG, PL); log("temel bitti")
XT = FA.join(DER); PG, PL, mT = wf(XT, FEATS + DF); kaydet("prim", PG, PL)
imp = pd.Series(np.mean([g.booster_.feature_importance("gain") for g, _, _ in mT.parts], axis=0), index=FEATS + DF).sort_values(ascending=False)
log("prim bitti · en önemli 12: " + " ".join(f"{k}{'*' if k in DF else ''}" for k in imp.index[:12]) + f" · prim özelliklerinin kazanç payı %{100*imp[DF].sum()/imp.sum():.0f}")
ok_ = np.where(DER.notna().any(axis=1).values)[0]; a_, b_ = ok_[0], len(idx); wk = (np.arange(a_, b_) - a_) // 168; blocks = [np.arange(a_, b_)[wk == w] for w in np.unique(wk)]
rg = np.random.default_rng(int.from_bytes(SYM.encode(), "little") % 2**32)
for k in range(1, K + 1):
    perm = np.concatenate([blocks[j] for j in rg.permutation(len(blocks))]); V = DER.values.copy(); V[a_:b_] = DER.values[perm]
    PG, PL, _ = wf(FA.join(pd.DataFrame(V, index=idx, columns=DF)), FEATS + DF); kaydet(f"k{k}", PG, PL); log(f"karıştırma {k} bitti")
OUT.astype("float32").to_pickle(f"pm_{SYM}_{H}.pkl"); log("kaydedildi")
