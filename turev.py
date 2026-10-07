# turev.py — VADELİ PİYASA POZİSYONLANMASI 24 saatlik tahmine bilgi katıyor mu? (canlı sisteme dokunmaz). Kullanım: python turev.py ETHUSDT
# Yeni bilgi ailesi (Binance USDⓈ-M arşivi): fonlama oranı · prim endeksi (vadeli−spot) · vadeli alıcı/satıcı baskısı ve hacmi ·
# açık pozisyon (OI) değişimi · hesapların ve büyük trader'ların uzun/kısa oranı · vadeli taker uzun/kısa oranı.
# Deney (24 saat, canlı denemeyle aynı model): TEMEL (yalnız fiyat özellikleri) · TÜREV (fiyat + vadeli özellikler) ·
# 6 × KARIŞTIRMA (vadeli özellikler haftalık bloklar halinde zamanda karıştırılır: bilgi yok, sayı ve dağılım aynı) → gerçek kazanç karıştırmalardan büyük olmalı.
# Test 2022-01'den (vadeli metrikler 2021-12'de başlıyor): seçim 2022–23, karar 2024+. Sonuçlar turev_{SYM}.pkl → turev_rapor.py
import os, sys, io, re, time, zipfile, requests, numpy as np, pandas as pd, lightgbm as lgb
from concurrent.futures import ThreadPoolExecutor
from sklearn.linear_model import LogisticRegression
from ortak import *
SYM = sys.argv[1]; FS = "1000SHIBUSDT" if SYM == "SHIBUSDT" else SYM; H, YL = 24, [3, 5]
K = int(os.environ.get("TUREV_K", 6)); TEST = pd.Timestamp(os.environ.get("TUREV_TEST", "2022-01-01"), tz="UTC"); T0 = time.time()
def log(*a): print(f"[{time.time()-T0:5.0f} sn] {SYM}:", *a, flush=True)
S3, BV = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision", "https://data.binance.vision/"
def s3_list(prefix):
    out, marker = [], ""
    while True:
        for _ in range(4):
            try: r = requests.get(S3, params=dict(delimiter="/", prefix=prefix, marker=marker), timeout=60); r.raise_for_status(); break
            except Exception: time.sleep(3)
        x = r.text; pre = re.findall(r"<Prefix>([^<]+)</Prefix>", x)[1:]; keys = re.findall(r"<Key>([^<]+)</Key>", x); out += pre + keys
        if "<IsTruncated>true</IsTruncated>" not in x or not (pre or keys): return out
        marker = (pre + keys)[-1]
def zcsv(key):
    for _ in range(3):
        try:
            r = requests.get(BV + key, timeout=60)
            if r.status_code == 404: return None
            r.raise_for_status(); z = zipfile.ZipFile(io.BytesIO(r.content)); raw = z.open(z.namelist()[0]).read().decode()
            first = raw.split("\n", 1)[0].split(",")[0].strip()
            return pd.read_csv(io.StringIO(raw), header=None if first.replace(".", "").isdigit() else 0)
        except Exception: time.sleep(2)
    return None
def load(prefix, names=None):
    keys = [k for k in s3_list(prefix) if k.endswith(".zip")]
    with ThreadPoolExecutor(16) as ex: parts = [p for p in ex.map(zcsv, keys) if p is not None and len(p)]
    if not parts: return None
    if names: parts = [p.rename(columns={i: n for i, n in enumerate(names)}) if isinstance(p.columns[0], (int, np.integer)) else p for p in parts]
    return pd.concat(parts, ignore_index=True)
def ms2ts(x):
    v = pd.to_numeric(x, errors="coerce").astype("float64").values; v = np.where(v > 1e14, v / 1000, v); return pd.to_datetime(v, unit="ms", utc=True)
KL = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "count", "taker_buy_volume", "taker_buy_quote_volume", "ignore"]
# ---------------- veri ----------------
if os.environ.get("TUREV_SAHTE"): from turev_sahte import o, FR, PR, FK, MT                     # yerel duman testi
else:
    o = fetch_1h(pd.Timestamp("2017-08-17", tz="UTC").timestamp() * 1000, time.time() * 1000, sym=SYM)
    FR = load(f"data/futures/um/monthly/fundingRate/{FS}/", ["calc_time", "funding_interval_hours", "last_funding_rate"])
    PR = load(f"data/futures/um/monthly/premiumIndexKlines/{FS}/1h/", KL)
    FK = load(f"data/futures/um/monthly/klines/{FS}/1h/", KL)
    MT = load(f"data/futures/um/daily/metrics/{FS}/")
log(f"spot {len(o):,} saat · fonlama {0 if FR is None else len(FR):,} · prim {0 if PR is None else len(PR):,} · vadeli mum {0 if FK is None else len(FK):,} · metrik {0 if MT is None else len(MT):,} satır")
idx = o.index; base = pd.DataFrame(index=idx); c = o.close
def asof(ts, val, tol="3h"):
    s = pd.DataFrame({"t": pd.DatetimeIndex(ts).astype("datetime64[ns, UTC]"), "v": pd.to_numeric(pd.Series(np.asarray(val)), errors="coerce").values}).dropna().sort_values("t").drop_duplicates("t", keep="last")
    L_ = pd.DataFrame({"t": idx.astype("datetime64[ns, UTC]")})
    return pd.Series(pd.merge_asof(L_, s, on="t", direction="backward", tolerance=pd.Timedelta(tol)).v.values, index=idx)
def z(x, n=720): return (x - x.rolling(n, min_periods=168).mean()) / (x.rolling(n, min_periods=168).std() + 1e-12)
F = {}
if FR is not None:
    fr = asof(ms2ts(FR.calc_time).floor("s"), FR.last_funding_rate, "9h"); F.update(fr=fr, fr_z=z(fr), fr_m24=fr.rolling(24).mean(), fr_m168=fr.rolling(168).mean())
if PR is not None:
    pr = pd.Series(pd.to_numeric(PR.close, errors="coerce").values, index=(ms2ts(PR.open_time) + pd.Timedelta(hours=1)).astype("datetime64[ns, UTC]")); pr = pd.Series(pr[~pr.index.duplicated()].reindex(idx.astype("datetime64[ns, UTC]")).values, index=idx)
    F.update(prem=pr, prem_m8=pr.rolling(8).mean(), prem_m24=pr.rolling(24).mean(), prem_z=z(pr.rolling(8).mean()))
if FK is not None:
    fk = pd.DataFrame({k: pd.to_numeric(FK[k], errors="coerce").values for k in ("quote_volume", "taker_buy_quote_volume", "count")}, index=(ms2ts(FK.open_time) + pd.Timedelta(hours=1)).astype("datetime64[ns, UTC]"))
    fk = fk[~fk.index.duplicated()].reindex(idx.astype("datetime64[ns, UTC]")); fk.index = idx; qv, tb = fk.quote_volume, fk.taker_buy_quote_volume
    for k in (1, 4, 24): F[f"ftk{k}"] = (2 * tb.rolling(k).sum() - qv.rolling(k).sum()) / (qv.rolling(k).sum() + 1e-12)
    F["fvol_z"] = np.log(qv.rolling(24).sum() + 1) - np.log(qv.rolling(720).sum() / 30 + 1)
if MT is not None:
    tt = pd.to_datetime(MT.create_time, utc=True) + pd.Timedelta(minutes=5)                     # 5 dakikalık kayıt, ancak bittiğinde bilinir
    oi = asof(tt, MT.sum_open_interest_value); lo = np.log(oi)
    for k in (1, 4, 24): F[f"oi{k}"] = lo - lo.shift(k)
    F["oi_z"] = z(lo); F["oi_r24"] = F["oi24"] - np.log(c / c.shift(24))
    ls = np.log(asof(tt, MT.count_long_short_ratio)); F.update(ls=ls, ls_z=z(ls), ls24=ls - ls.shift(24))
    tp = np.log(asof(tt, MT.sum_toptrader_long_short_ratio)); F.update(top=tp, top_z=z(tp))
    tk = pd.Series(pd.to_numeric(MT.sum_taker_long_short_vol_ratio, errors="coerce").values, index=pd.DatetimeIndex(tt).ceil("h").astype("datetime64[ns, UTC]")); tk = pd.Series(np.log(tk[tk > 0]).groupby(level=0).mean().reindex(idx.astype("datetime64[ns, UTC]")).values, index=idx)
    F.update(mtk1=tk, mtk24=tk.rolling(24, min_periods=6).mean())
DER = pd.DataFrame(F, index=idx).replace([np.inf, -np.inf], np.nan).astype("float32"); DF = list(DER.columns)
cov = DER[idx >= TEST].notna().mean(); log(f"{len(DF)} vadeli özellik · test döneminde dolu oran: " + " ".join(f"{k}:{v:.0%}" for k, v in cov.items()))
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
    sf = signal_frame(PG, PL, FA.r24, False).reindex(idx); OUT[f"S_{ad}"], OUT[f"C_{ad}"], OUT[f"T10_{ad}"] = sf.S, sf.C, sf.T10
PG, PL, _ = wf(FA, FEATS); kaydet("temel", PG, PL); log("temel bitti")
XT = FA.join(DER); PG, PL, mT = wf(XT, FEATS + DF); kaydet("turev", PG, PL)
imp = pd.Series(np.mean([g.booster_.feature_importance("gain") for g, _, _ in mT.parts], axis=0), index=FEATS + DF).sort_values(ascending=False)
log("türev bitti · en önemli 12: " + " ".join(f"{k}{'*' if k in DF else ''}" for k in imp.index[:12]) + f" · vadeli özelliklerin kazanç payı %{100*imp[DF].sum()/imp.sum():.0f}")
ok_ = np.where(DER.notna().any(axis=1).values)[0]; a_, b_ = ok_[0], len(idx); wk = (np.arange(a_, b_) - a_) // 168; blocks = [np.arange(a_, b_)[wk == w] for w in np.unique(wk)]
rg = np.random.default_rng(int.from_bytes(SYM.encode(), "little") % 2**32)
for k in range(1, K + 1):
    perm = np.concatenate([blocks[j] for j in rg.permutation(len(blocks))]); V = DER.values.copy(); V[a_:b_] = DER.values[perm]
    PG, PL, _ = wf(FA.join(pd.DataFrame(V, index=idx, columns=DF)), FEATS + DF); kaydet(f"k{k}", PG, PL); log(f"karıştırma {k} bitti")
OUT.astype("float32").to_pickle(f"turev_{SYM}.pkl"); log("kaydedildi")
