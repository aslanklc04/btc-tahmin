# dt/veri.py — BAĞIMSIZ DENETİM veri indirme (yalnız okuma). Kullanım: python dt/veri.py SHARD NSHARD
# Binance spot 1 saatlik OHLCV (data-api.binance.vision) + Coinbase 1 saatlik kapanış (api.exchange.coinbase.com), 2021-06-01 → şimdi.
# İndeks = mumun KAPANIŞ zamanı (açılış + 1 saat) — canlı kodla aynı kural; hizalama denetimi analiz betiğinde ayrıca yapılır.
import sys, time, pickle, os, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
SH, NS = int(sys.argv[1]), int(sys.argv[2])
COINS = [l.strip() for l in open("dt/coinler.txt") if l.strip()][SH::NS]
T0 = pd.Timestamp("2021-06-01", tz="UTC"); NOW = pd.Timestamp.now(tz="UTC").floor("h")
def bn(sym):
    rows, cur, end = [], int(T0.timestamp() * 1000), int(NOW.timestamp() * 1000)
    s = requests.Session()
    while cur < end:
        for k in range(5):
            try:
                r = s.get("https://data-api.binance.vision/api/v3/klines", params=dict(symbol=sym, interval="1h", startTime=cur, endTime=end, limit=1000), timeout=30)
                if r.status_code == 200: d = r.json(); break
                if r.status_code == 400: return None
            except Exception: pass
            time.sleep(2 + 3 * k)
        else: raise RuntimeError(f"binance {sym}")
        if not d: break
        rows += d; cur = d[-1][0] + 3_600_000
        if len(d) < 1000: break
    if not rows: return None
    df = pd.DataFrame([x[:6] for x in rows], columns=["t", "o", "h", "l", "c", "v"]).astype(float)
    df.index = pd.to_datetime(df.t.astype("int64"), unit="ms", utc=True) + pd.Timedelta(hours=1)
    df = df[df.index <= NOW]; return df[~df.index.duplicated()].sort_index()[["o", "h", "l", "c", "v"]]
_last = [0.0]
def cb(nm):
    s = requests.Session(); s.headers.update({"User-Agent": "denetim"}); out = []; cur = T0 - pd.Timedelta(hours=1)
    while cur < NOW:
        nx = min(cur + pd.Timedelta(hours=300), NOW)
        for k in range(6):
            w = 0.13 - (time.time() - _last[0])
            if w > 0: time.sleep(w)
            _last[0] = time.time()
            try:
                r = s.get(f"https://api.exchange.coinbase.com/products/{nm}-USD/candles", params=dict(granularity=3600, start=cur.isoformat(), end=nx.isoformat()), timeout=30)
                if r.status_code == 404: return None
                if r.status_code == 200: out += r.json(); break
            except Exception: pass
            time.sleep(1.5 * (k + 1))
        cur = nx
    if not out: return pd.Series(dtype=float)
    d = pd.DataFrame(out, columns=["t", "low", "high", "open", "close", "volume"]).drop_duplicates("t")
    return pd.Series(d.close.values.astype(float), index=pd.to_datetime(d.t.astype("int64"), unit="s", utc=True) + pd.Timedelta(hours=1)).sort_index()
T = time.time(); OUT = {}
with ThreadPoolExecutor(4) as ex: B = dict(zip(COINS, ex.map(bn, COINS)))
print(f"binance bitti {time.time()-T:.0f} sn", flush=True)
for sym in COINS:
    nm = sym[:-4]; c = cb(nm); OUT[sym] = dict(bn=B[sym], cb=c)
    print(f"{sym}: bn {0 if B[sym] is None else len(B[sym])} · cb {'yok' if c is None else len(c)} · {time.time()-T:.0f} sn", flush=True)
os.makedirs("out", exist_ok=True); pickle.dump(OUT, open(f"out/veri_{SH}.pkl", "wb"))
