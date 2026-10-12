# paralel_veri.py — Binance (spot, 1 dk, alıcı hacmi dahil) + Coinbase (1 dk) → 5 dakikalık birleşik tablo. Kullanım: python paralel_veri.py BTC
import sys, io, zipfile, time, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
nm = sys.argv[1]; T0 = time.time(); S = requests.Session(); S.headers["User-Agent"] = "btc-tahmin-arastirma"
BAS, SON = pd.Timestamp("2022-05-01", tz="UTC"), pd.Timestamp("2026-10-01", tz="UTC")
def ay(ym):
    for k in range(4):
        try:
            r = S.get(f"https://data.binance.vision/data/spot/monthly/klines/{nm}USDT/1m/{nm}USDT-1m-{ym}.zip", timeout=60)
            if r.status_code == 404: return None
            if r.status_code != 200: time.sleep(2 + k); continue
            z_ = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z_.open(z_.namelist()[0]), header=None)
            t = d[0].astype("int64").values; t = np.where(t > 1e14, t // 1000, t)
            return pd.DataFrame({"o": d[1].values, "c": d[4].values, "q": d[7].values, "tbq": d[10].values}, index=pd.to_datetime(t, unit="ms", utc=True))
        except Exception: time.sleep(2 + k)
    return None
with ThreadPoolExecutor(8) as ex: P = [x for x in ex.map(ay, [d.strftime("%Y-%m") for d in pd.date_range(BAS.tz_localize(None), (SON - pd.Timedelta(days=1)).tz_localize(None), freq="MS")]) if x is not None]
BN = pd.concat(P).sort_index(); BN = BN[~BN.index.duplicated()]
print(nm, "Binance 1 dk:", len(BN), f"{time.time()-T0:.0f} sn", flush=True)
def cb(a):
    b = a + pd.Timedelta(minutes=300)
    for k in range(8):
        try:
            r = S.get(f"https://api.exchange.coinbase.com/products/{nm}-USD/candles", params={"granularity": 60, "start": a.isoformat(), "end": b.isoformat()}, timeout=30)
            if r.status_code == 429: time.sleep(1 + k); continue
            if r.status_code != 200: time.sleep(1 + k); continue
            return r.json()
        except Exception: time.sleep(1 + k)
    return []
pencere = pd.date_range(BAS, SON, freq="300min")
with ThreadPoolExecutor(5) as ex: R = [x for x in ex.map(cb, pencere) if x]
rows = [y for x in R for y in x]
CB = pd.DataFrame(rows, columns=["t", "l", "h", "o", "c", "v"]).drop_duplicates("t"); CB.index = pd.to_datetime(CB.t, unit="s", utc=True); CB = CB.sort_index()
print(nm, "Coinbase 1 dk:", len(CB), f"{time.time()-T0:.0f} sn", flush=True)
def bes(df, ad):                                                                           # 5 dk çubuk, indeks = çubuk SONU (o an bilinir)
    g = df.resample("5min", label="right", closed="left")
    if ad == "bn": return pd.DataFrame({"bn_o": g.o.first(), "bn_c": g.c.last(), "bn_q": g.q.sum(), "bn_tbq": g.tbq.sum()})
    return pd.DataFrame({"cb_o": g.o.first(), "cb_c": g.c.last(), "cb_q": (df.v * df.c).resample("5min", label="right", closed="left").sum()})
X = bes(BN.astype(float), "bn").join(bes(CB[["o", "c", "v"]].astype(float), "cb"), how="left")
X.astype("float32").to_pickle(f"paralel_{nm}.pkl"); print(nm, "5 dk çubuk:", len(X), "· Coinbase dolu oranı", round(X.cb_q.notna().mean(), 3), f"{time.time()-T0:.0f} sn")
