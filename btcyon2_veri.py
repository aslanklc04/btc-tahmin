# btcyon2_veri.py — PROTOKOL_btcyon2.md veri: günlük spot (BTC/ETH/SOL 2017+), vadeli prim endeksi 1 s, CoinMetrics değerleme → btcyon2_gun.parquet · btcyon2_prim.parquet
import io, time, zipfile, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
T0 = time.time(); S = requests.Session(); V = "https://data.binance.vision/data"
def log(*a): print(f"[{time.time() - T0:5.0f} sn]", *a, flush=True)
def get(u, **kw):
    for k in range(5):
        try:
            r = S.get(u, timeout=60, **kw)
            if r.status_code == 200: return r
            if r.status_code in (400, 404): return None
        except Exception: pass
        time.sleep(2 + 3 * k)
    return None
def kl(u, cols):
    r = get(u)
    if r is None: return None
    z = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=cols)
    return d[pd.to_numeric(d[cols[0]], errors="coerce").notna()].astype(float)
def seri(pazar, sym, aralik, aylar, gunler, tip="klines"):
    U = [f"{V}/{pazar}/monthly/{tip}/{sym}/{aralik}/{sym}-{aralik}-{a}.zip" for a in aylar] + [f"{V}/{pazar}/daily/{tip}/{sym}/{aralik}/{sym}-{aralik}-{g}.zip" for g in gunler]
    with ThreadPoolExecutor(8) as ex: P = [x for x in ex.map(lambda u: kl(u, [0, 1, 2, 3, 4, 7]), U) if x is not None]
    k = pd.concat(P, ignore_index=True); k.columns = ["ot", "o", "h", "l", "c", "qv"]; k.loc[k.ot > 1e14, "ot"] = k.ot / 1000
    k.index = pd.to_datetime(k.ot, unit="ms", utc=True); return k[~k.index.duplicated()].sort_index().drop(columns="ot")
GUN = pd.date_range("2026-10-01", "2026-10-29").strftime("%Y-%m-%d")
G = []
for sym in ("BTCUSDT", "ETHUSDT", "SOLUSDT"):
    k = seri("spot", sym, "1d", pd.period_range("2017-08", "2026-09", freq="M").strftime("%Y-%m"), GUN); k["coin"] = sym[:-4]; G.append(k); log(sym, "günlük", len(k), k.index.min(), k.index.max())
G = pd.concat(G).rename_axis("t").reset_index()
u = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"; Dd = []
r = get(u, params=dict(assets="btc", metrics="CapMVRVCur,AdrActCnt,TxTfrValAdjUSD", frequency="1d", start_time="2013-01-01", page_size=10000))
while r is not None:
    j = r.json(); Dd += j.get("data", []); nx = j.get("next_page_url"); r = get(nx) if nx else None
cm = pd.DataFrame(Dd)
if len(cm):
    cm["t"] = pd.to_datetime(cm.time, utc=True).dt.floor("D"); cm = cm.set_index("t")[[c for c in ("CapMVRVCur", "AdrActCnt", "TxTfrValAdjUSD") if c in cm]].apply(pd.to_numeric, errors="coerce")
    log("coinmetrics", len(cm), list(cm.columns), cm.index.min(), cm.index.max())
    G = G.merge(cm.reset_index().assign(coin="BTC"), on=["t", "coin"], how="left")
G.to_parquet("btcyon2_gun.parquet", index=False)
P = seri("futures/um", "BTCUSDT", "1h", pd.period_range("2021-10", "2026-09", freq="M").strftime("%Y-%m"), GUN, tip="premiumIndexKlines")
log("prim endeksi", len(P), P.index.min(), P.index.max(), P.c.describe().to_dict())
P[["o", "h", "l", "c"]].rename_axis("t").reset_index().to_parquet("btcyon2_prim.parquet", index=False)
