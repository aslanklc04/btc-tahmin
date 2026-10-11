# genis_prim.py — tek coin için saatlik Coinbase primi (canlıdaki ortak.cb_prim ile aynı tanım): p = log(Coinbase COIN-USD / Binance COINUSDT), son 720 saate göre z. Çıktı prim_{SYM}.pkl
import sys, time, requests, numpy as np, pandas as pd
from ortak import fetch_1h
SYM = sys.argv[1]; NM = SYM.replace("USDT", ""); BAS = pd.Timestamp("2022-05-01", tz="UTC"); UA = {"User-Agent": "btc-tahmin-arastirma"}
def cb_get(url, **p):
    for k in range(8):
        try:
            r = requests.get(url, params=p, headers=UA, timeout=20)
            if r.status_code == 429: time.sleep(1 + k); continue
            return r
        except Exception: time.sleep(2)
    return None
out, cur, end = [], BAS, pd.Timestamp.now(tz="UTC").floor("h")
while cur < end:
    nx = min(cur + pd.Timedelta(hours=300), end); r = cb_get(f"https://api.exchange.coinbase.com/products/{NM}-USD/candles", granularity=3600, start=cur.isoformat(), end=nx.isoformat())
    if r is not None and r.status_code == 404: break
    if r is not None and r.status_code == 200: out += r.json()
    cur = nx; time.sleep(0.15)
if not out: print(NM, "Coinbase verisi yok"); sys.exit(0)
d = pd.DataFrame(out, columns=["t", "low", "high", "open", "close", "volume"]).drop_duplicates("t")
c_ = pd.Series(d.close.values.astype(float), index=pd.to_datetime(d.t, unit="s", utc=True) + pd.Timedelta(hours=1)).sort_index()
o = fetch_1h(BAS.timestamp() * 1000, time.time() * 1000, sym=SYM)
c_.index = c_.index.astype("datetime64[ns, UTC]"); o.index = o.index.astype("datetime64[ns, UTC]")
ix = o.index[o.index >= c_.index[0]]; p = np.log(c_.reindex(ix) / o.close.reindex(ix)); p = p.where(p.abs() < 0.3)
z = (p - p.rolling(720, min_periods=168).mean()) / (p.rolling(720, min_periods=168).std() + 1e-12)
pd.DataFrame({"c": o.close.reindex(ix), "z": z, "bp": 1e4 * p}).astype("float32").to_pickle(f"prim_{SYM}.pkl")
print(NM, len(ix), "saat · z dolu", int(z.notna().sum()))
