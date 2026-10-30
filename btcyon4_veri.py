# btcyon4_veri.py — PROTOKOL_btcyon4.md veri: 1 dk vadeli mum → saatlik balina akışı · Upbit KRW-BTC saatlik · USD/KRW · Coinbase USDT-USD saatlik
import io, time, zipfile, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
T0 = time.time(); S = requests.Session(); V = "https://data.binance.vision/data/futures/um"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
def log(*a): print(f"[{time.time() - T0:5.0f} sn]", *a, flush=True)
def get(u, **kw):
    for k in range(5):
        try:
            r = S.get(u, timeout=90, **kw)
            if r.status_code == 200: return r
            if r.status_code in (400, 404): return None
        except Exception: pass
        time.sleep(2 + 3 * k)
    return None
def kl(u):
    r = get(u)
    if r is None: return None
    z = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=[0, 7, 8, 10])
    d = d[pd.to_numeric(d[0], errors="coerce").notna()].astype(float); d.columns = ["ot", "qv", "n", "tb"]; d.loc[d.ot > 1e14, "ot"] = d.ot / 1000; return d
AYLAR = pd.period_range("2021-12", "2026-09", freq="M").strftime("%Y-%m").tolist(); GUN = pd.date_range("2026-10-01", "2026-10-29").strftime("%Y-%m-%d").tolist()
U = [f"{V}/monthly/klines/BTCUSDT/1m/BTCUSDT-1m-{a}.zip" for a in AYLAR] + [f"{V}/daily/klines/BTCUSDT/1m/BTCUSDT-1m-{g}.zip" for g in GUN]
with ThreadPoolExecutor(6) as ex: P = list(ex.map(kl, U))
M = pd.concat([p for p in P if p is not None], ignore_index=True).drop_duplicates("ot").sort_values("ot")
M["t"] = pd.to_datetime(M.ot, unit="ms", utc=True); M["ay"] = M.t.dt.strftime("%Y-%m"); M["boy"] = M.qv / M.n.clip(lower=1)
log("1 dk", len(M), M.t.min(), M.t.max())
esik = M.groupby("ay").boy.quantile(0.95); onceki = esik.shift(1); M["esik"] = M.ay.map(onceki)
w = M.boy >= M.esik; M["wq"] = np.where(w, M.qv, 0.0); M["wtb"] = np.where(w, M.tb, 0.0)
M["s"] = M.t.dt.floor("h"); g = M.groupby("s")
B = pd.DataFrame({"qv": g.qv.sum(), "tb": g.tb.sum(), "wq": g.wq.sum(), "wtb": g.wtb.sum(), "n": g.n.sum()}); B.index.name = "t"
B.reset_index().to_parquet("btcyon4_balina.parquet", index=False); log("balina saatlik", len(B), "balina hacim payı ort.", (B.wq / B.qv).mean())
# ---- Upbit KRW-BTC saatlik ----
R = []; to = pd.Timestamp("2026-10-30", tz="UTC"); bas = pd.Timestamp("2021-12-01", tz="UTC")
while to > bas:
    r = get("https://api.upbit.com/v1/candles/minutes/60", params=dict(market="KRW-BTC", to=to.strftime("%Y-%m-%dT%H:%M:%SZ"), count=200), headers=UA)
    if r is None: log("upbit hata", to); break
    j = r.json()
    if not j: break
    R += j; to = pd.Timestamp(j[-1]["candle_date_time_utc"], tz="UTC"); time.sleep(0.12)
up = pd.DataFrame(R)
if len(up):
    up = pd.DataFrame({"t": pd.to_datetime(up.candle_date_time_utc).dt.tz_localize("UTC"), "up_c": up.trade_price.astype(float), "up_qv": up.candle_acc_trade_price.astype(float)}).drop_duplicates("t").sort_values("t")
log("upbit", len(up), up.t.min() if len(up) else None, up.t.max() if len(up) else None)
# ---- Coinbase USDT-USD ----
P2 = []; a = pd.Timestamp("2021-12-01", tz="UTC"); son = pd.Timestamp("2026-10-30", tz="UTC")
while a < son:
    b = min(a + pd.Timedelta(hours=299), son); r = get("https://api.exchange.coinbase.com/products/USDT-USD/candles", params=dict(granularity=3600, start=a.isoformat(), end=b.isoformat()), headers=UA)
    if r is not None: P2 += r.json()
    a = b; time.sleep(0.15)
cb = pd.DataFrame(P2, columns=["ts", "l", "h", "o", "c", "v"]); cb["t"] = pd.to_datetime(cb.ts, unit="s", utc=True); cb = cb.drop_duplicates("t")[["t", "c"]].rename(columns={"c": "usdt_c"})
log("coinbase USDT", len(cb), cb.t.min() if len(cb) else None, cb.t.max() if len(cb) else None)
S_ = up.merge(cb, on="t", how="outer").sort_values("t") if len(up) else cb
try:
    import yfinance as yf
    h = yf.Ticker("KRW=X").history(start="2021-11-01", interval="1d", auto_adjust=True)
    kr = pd.DataFrame({"gun": pd.DatetimeIndex(h.index.tz_localize(None).normalize()).tz_localize("UTC"), "usdkrw": h.Close.values}); log("USD/KRW", len(kr))
    kr.to_parquet("btcyon4_kur.parquet", index=False)
except Exception as e: log("kur hata", e)
S_.to_parquet("btcyon4_akis.parquet", index=False); log("bitti")
