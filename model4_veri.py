# model4_veri.py — PROTOKOL_dortyol YOL 4: kesitsel model için coin başına saatlik özellik + sonraki 4 saatin mumları (Binance vadeli 1 s + fonlama). Parça I / N.
import sys, io, time, zipfile, numpy as np, pandas as pd, requests
I, N = int(sys.argv[1]), int(sys.argv[2]); T0 = time.time()
A0 = pd.Timestamp("2022-01-01", tz="UTC"); SON = pd.Timestamp("2026-10-26", tz="UTC"); NH = int((SON - A0) / pd.Timedelta(hours=1))
URL = "https://data.binance.vision/data/futures/um"; S = requests.Session()
ESKI = ["BTC", "ADA", "APT", "ARB", "BNB", "DOGE", "DOT", "ETH", "FLOKI", "LINK", "NEAR", "OP", "PEPE", "SHIB", "SUI"]
YENI = [x.strip()[:-4] for x in open("igne2_evren.txt") if x.strip()]
COINS = list(dict.fromkeys(ESKI + YENI)); benim = COINS[I::N]
def indir(u):
    for k in range(5):
        try:
            r = S.get(u, timeout=60)
            if r.status_code == 404: return None
            if r.status_code == 200: return r.content
        except Exception: pass
        time.sleep(2 + 3 * k)
    return None
def zcsv(b, cols):
    z = zipfile.ZipFile(io.BytesIO(b)); d = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=cols)
    return d[pd.to_numeric(d[cols[0]], errors="coerce").notna()].astype(float)
AY = pd.period_range("2021-11", "2026-09", freq="M").strftime("%Y-%m")
def yukle(nm):
    for sym in (f"{nm}USDT", f"1000{nm}USDT"):
        P = []
        for ay in AY:
            b = indir(f"{URL}/monthly/klines/{sym}/1h/{sym}-1h-{ay}.zip")
            if b: P.append(zcsv(b, [0, 1, 2, 3, 4, 7]))
        for g in pd.date_range("2026-10-01", "2026-10-25").strftime("%Y-%m-%d"):
            b = indir(f"{URL}/daily/klines/{sym}/1h/{sym}-1h-{g}.zip")
            if b: P.append(zcsv(b, [0, 1, 2, 3, 4, 7]))
        if not P: continue
        d = pd.concat(P); d.columns = ["ot", "o", "h", "l", "c", "qv"]; d.loc[d.ot > 1e14, "ot"] = d.ot / 1000
        d["i"] = ((d.ot / 1000 - (A0.timestamp() - 61 * 86400)) // 3600).astype(np.int64)
        n2 = NH + 61 * 24; d = d[(d.i >= 0) & (d.i < n2)].drop_duplicates("i").set_index("i").reindex(np.arange(n2))
        F = []
        for ay in AY:
            b = indir(f"{URL}/monthly/fundingRate/{sym}/{sym}-fundingRate-{ay}.zip")
            if b:
                z = zipfile.ZipFile(io.BytesIO(b)); x = pd.read_csv(z.open(z.namelist()[0])); x.columns = [c.strip().lower() for c in x.columns]
                F.append(pd.DataFrame({"t": pd.to_numeric(x[[c for c in x.columns if "time" in c][0]], errors="coerce"), "r": pd.to_numeric(x[[c for c in x.columns if "rate" in c][-1]], errors="coerce")}).dropna())
        f = pd.concat(F).drop_duplicates("t").sort_values("t") if F else None
        if f is not None: f.loc[f.t > 1e14, "t"] = f.t / 1000
        return sym, d, f
    return None, None, None
T_IDX = pd.date_range(A0 - pd.Timedelta(days=61) + pd.Timedelta(hours=1), periods=NH + 61 * 24, freq="h")       # saat KAPANIŞ zamanı
def ozellik(d, f):
    o, h, l, c, qv = d.o.values, d.h.values, d.l.values, pd.Series(d.c.values).ffill().values, d.qv.fillna(0).values
    lc = np.log(pd.Series(c)); lr = lc.diff(); sd = lr.rolling(720, min_periods=480).std().shift(1)
    X = pd.DataFrame(index=T_IDX)
    for k in (1, 4, 24, 72, 168): X[f"r{k}"] = ((lc - lc.shift(k)) / (sd * np.sqrt(k))).values
    X["vo"] = (lr.rolling(24).std() / sd).values
    q = pd.Series(qv); X["hc"] = np.log((q.rolling(24).sum() + 1) / (q.rolling(720).sum().shift(24) / 30 + 1)).values
    hh = pd.Series(np.where(np.isnan(h), -np.inf, h)).rolling(720).max().shift(1).values; ll = pd.Series(np.where(np.isnan(l), np.inf, l)).rolling(720).min().shift(1).values
    X["tepe"] = np.log(c / hh); X["dip"] = np.log(c / ll); X["liq"] = (q.rolling(168).sum() / 7).values
    fr = np.full(len(T_IDX), np.nan); fz = np.full(len(T_IDX), np.nan)
    if f is not None and len(f) > 30:
        kap = T_IDX.as_unit("ms").asi8; ix = np.searchsorted(f.t.values, kap, side="right") - 1; ok = ix >= 0
        rv = f.r.values; z = (pd.Series(rv) - pd.Series(rv).rolling(90, min_periods=30).mean()) / (pd.Series(rv).rolling(90, min_periods=30).std() + 1e-12)
        fr[ok] = rv[ix[ok]]; fz[ok] = z.values[ix[ok]]
    X["fr"], X["fz"] = fr, fz; X["sd"] = sd.values
    for j in range(1, 5): X[f"o{j}"], X[f"h{j}"], X[f"l{j}"], X[f"c{j}"] = np.roll(o, -j), np.roll(h, -j), np.roll(l, -j), np.roll(c, -j)
    X["c0"] = c
    return X
_, B, BF = yukle("BTC"); XB = ozellik(B, BF)
R = []
for nm in benim:
    sym, d, f = (None, B, BF) if nm == "BTC" else yukle(nm)
    if d is None: print(nm, "veri yok", flush=True); continue
    X = XB.copy() if nm == "BTC" else ozellik(d, f)
    for k in (1, 4, 24): X[f"b{k}"] = XB[f"r{k}"].values
    X["rel24"] = X.r24 - X.b24; X["coin"] = nm
    X = X[(X.index > A0) & (X.index <= SON - pd.Timedelta(hours=5))].dropna(subset=["r168", "o1", "c4", "sd"])
    R.append(X.astype({c: "float32" for c in X.columns if c != "coin"}).reset_index(names="t"))
    print(f"{nm}: {len(X)} saat · {time.time() - T0:.0f} sn", flush=True)
pd.concat(R, ignore_index=True).to_parquet(f"model4_p{I}.parquet", index=False)
print("bitti", sum(len(x) for x in R), f"{time.time() - T0:.0f} sn")
