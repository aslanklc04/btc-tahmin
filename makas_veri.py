# makas_veri.py — PROTOKOL_makas.md verisi (Actions): Binance USDTTRY / BTCTRY / BTCUSDT 1 s · Yahoo TRY=X saatlik + günlük
import time, requests, pandas as pd, yfinance as yf
U = "https://data-api.binance.vision/api/v3/klines"; S = requests.Session()
def kl(sym, a="2022-01-01"):
    out, cur, son = [], int(pd.Timestamp(a, tz="UTC").timestamp() * 1000), int(time.time() * 1000)
    while cur < son:
        r = S.get(U, params=dict(symbol=sym, interval="1h", startTime=cur, limit=1000), timeout=30); x = r.json()
        if not isinstance(x, list) or not x: print(sym, "durdu", str(x)[:120]); break
        out += x; cur = x[-1][0] + 3_600_000
        if len(x) < 1000: break
    d = pd.DataFrame([z[:6] for z in out], columns=["ot", "o", "h", "l", "c", "v"]).astype(float); d["t"] = pd.to_datetime(d.ot, unit="ms", utc=True) + pd.Timedelta(hours=1); d["sym"] = sym
    print(sym, len(d), d.t.min() if len(d) else None, d.t.max() if len(d) else None, flush=True); return d.drop(columns="ot")
B = pd.concat([kl(s) for s in ("USDTTRY", "BTCTRY", "BTCUSDT")], ignore_index=True); B.to_parquet("makas_binance.parquet")
h = yf.Ticker("TRY=X").history(period="730d", interval="60m"); g = yf.Ticker("TRY=X").history(start="2022-01-01", interval="1d")
for x, f in ((h, "makas_yahoo_saat.parquet"), (g, "makas_yahoo_gun.parquet")):
    x = x[["Open", "High", "Low", "Close"]].rename(columns=str.lower); x.index = x.index.tz_convert("UTC"); x.rename_axis("t").reset_index().to_parquet(f); print(f, len(x), x.index.min(), x.index.max())
