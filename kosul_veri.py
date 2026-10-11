# kosul_veri.py — KOŞUL TARAMASI için piyasa verileri (2022-05 → bugün). Yalnız veri toplar → kosul_veri.pkl
# Saatlik seriler indekste KAPANIŞ saatiyle (o saat bitince bilinen değer) tutulur; günlük seriler gün etiketiyle (tarama 1 gün gecikmeli kullanır).
#  A Coinbase BTC-USD / ETH-USD saatlik (fiyat + hacim)        B Binance BTCUSDT / ETHUSDT spot saatlik (hacim, alıcı hacmi, işlem sayısı)
#  C Bitstamp BTC/USD saatlik (fiyat + hacim)                  D Binance vadeli metrikler (5 dk: açık pozisyon, uzun/kısa oranları, alıcı/satıcı oranı)
#  E Binance vadeli fonlama oranı                               F Deribit DVOL (BTC, ETH opsiyon oynaklık endeksi) saatlik
#  G Yahoo günlük: CME BTC vadeli, BTC-USD, dolar endeksi, ABD 10 yıl faiz, VIX, S&P 500, altın, yüksek getirili tahvil (HYG)
import io, time, zipfile, threading, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
T0 = time.time(); BAS = pd.Timestamp("2022-05-01", tz="UTC"); SON = pd.Timestamp.now(tz="UTC").floor("h")
UA = {"User-Agent": "btc-tahmin-arastirma"}; V = {}
def log(*a): print(f"[{time.time()-T0:5.0f} sn]", *a, flush=True)
def get(url, **p):
    for k in range(6):
        try:
            r = requests.get(url, params=p, headers=UA, timeout=30)
            if r.status_code == 429: time.sleep(2 + 2 * k); continue
            return r
        except Exception: time.sleep(2)
    return None
# ---------- A Coinbase ----------
_kl, _son = threading.Lock(), [0.0]
def cb(pr):
    out, cur = [], BAS
    while cur < SON:
        with _kl:
            w = 0.15 - (time.time() - _son[0]); time.sleep(max(0, w)); _son[0] = time.time()
        nx = min(cur + pd.Timedelta(hours=300), SON); r = get(f"https://api.exchange.coinbase.com/products/{pr}/candles", granularity=3600, start=cur.isoformat(), end=nx.isoformat())
        if r is not None and r.status_code == 200: out += r.json()
        cur = nx
    d = pd.DataFrame(out, columns=["t", "low", "high", "open", "close", "volume"]).drop_duplicates("t")
    d.index = pd.to_datetime(d.t, unit="s", utc=True) + pd.Timedelta(hours=1); return d.sort_index()[["close", "volume"]].astype(float)
for pr in ("BTC-USD", "ETH-USD"):
    try: V[f"cb_{pr[:3]}"] = cb(pr); log("Coinbase", pr, len(V[f"cb_{pr[:3]}"]))
    except Exception as e: log("Coinbase hata", pr, e)
# ---------- B Binance spot ----------
def bn(sym):
    rows, cur = [], int(BAS.timestamp() * 1000)
    while cur < SON.timestamp() * 1000:
        r = get("https://data-api.binance.vision/api/v3/klines", symbol=sym, interval="1h", startTime=cur, limit=1000)
        k = r.json() if r is not None and r.status_code == 200 else []
        if not k: break
        rows += k; cur = k[-1][0] + 3_600_000
        if len(k) < 1000: break
    d = pd.DataFrame([x[:11] for x in rows], columns=["t", "o", "h", "l", "close", "vol", "ct", "qv", "trades", "tbv", "tbq"]).astype(float)
    d.index = pd.to_datetime(d.t, unit="ms", utc=True) + pd.Timedelta(hours=1); return d[~d.index.duplicated()][["close", "vol", "qv", "trades", "tbq"]]
for s in ("BTCUSDT", "ETHUSDT"):
    try: V[f"bn_{s[:3]}"] = bn(s); log("Binance", s, len(V[f"bn_{s[:3]}"]))
    except Exception as e: log("Binance hata", s, e)
# ---------- C Bitstamp ----------
try:
    out, cur = [], int(BAS.timestamp())
    while cur < SON.timestamp():
        r = get("https://www.bitstamp.net/api/v2/ohlc/btcusd/", step=3600, limit=1000, start=cur)
        o = r.json().get("data", {}).get("ohlc", []) if r is not None and r.status_code == 200 else []
        if not o: break
        out += o; cur = int(o[-1]["timestamp"]) + 3600; time.sleep(0.3)
    d = pd.DataFrame(out).astype(float).drop_duplicates("timestamp"); d.index = pd.to_datetime(d.timestamp, unit="s", utc=True) + pd.Timedelta(hours=1)
    V["bs_BTC"] = d.sort_index()[["close", "volume"]]; log("Bitstamp", len(d))
except Exception as e: log("Bitstamp hata", e)
# ---------- D vadeli metrikler (günlük zip, 5 dk) ----------
def zipcsv(url):
    r = get(url)
    if r is None or r.status_code != 200: return None
    z = zipfile.ZipFile(io.BytesIO(r.content)); return pd.read_csv(z.open(z.namelist()[0]))
for s in ("BTCUSDT", "ETHUSDT"):
    try:
        gunler = pd.date_range(BAS, SON - pd.Timedelta(days=1), freq="D")
        with ThreadPoolExecutor(16) as ex: parts = list(ex.map(lambda g: zipcsv(f"https://data.binance.vision/data/futures/um/daily/metrics/{s}/{s}-metrics-{g:%Y-%m-%d}.zip"), gunler))
        d = pd.concat([p for p in parts if p is not None]); d["t"] = pd.to_datetime(d.create_time, utc=True)
        d = d.set_index("t").sort_index()[["sum_open_interest_value", "count_toptrader_long_short_ratio", "sum_toptrader_long_short_ratio", "count_long_short_ratio", "sum_taker_long_short_vol_ratio"]].astype(float)
        V[f"met_{s[:3]}"] = d.resample("1h", label="right", closed="right").last(); log("metrik", s, len(d), "satır")
    except Exception as e: log("metrik hata", s, e)
# ---------- E fonlama ----------
for s in ("BTCUSDT", "ETHUSDT"):
    try:
        aylar = pd.date_range(BAS, SON, freq="MS")
        with ThreadPoolExecutor(8) as ex: parts = list(ex.map(lambda a: zipcsv(f"https://data.binance.vision/data/futures/um/monthly/fundingRate/{s}/{s}-fundingRate-{a:%Y-%m}.zip"), aylar))
        d = pd.concat([p for p in parts if p is not None]); d.index = pd.to_datetime(d.calc_time, unit="ms", utc=True)
        V[f"fon_{s[:3]}"] = d.sort_index()["last_funding_rate"].astype(float); log("fonlama", s, len(d))
    except Exception as e: log("fonlama hata", s, e)
# ---------- F Deribit DVOL ----------
for cur_ in ("BTC", "ETH"):
    try:
        out, bit = [], int(SON.timestamp() * 1000)
        for _ in range(200):
            r = get("https://www.deribit.com/api/v2/public/get_volatility_index_data", currency=cur_, start_timestamp=int(BAS.timestamp() * 1000), end_timestamp=bit, resolution="3600")
            res = r.json().get("result", {}) if r is not None and r.status_code == 200 else {}
            dt = res.get("data", [])
            if not dt: break
            out += dt; c = res.get("continuation")
            if not c or c >= bit: break
            bit = c
        d = pd.DataFrame(out, columns=["t", "o", "h", "l", "close"]).drop_duplicates("t"); d.index = pd.to_datetime(d.t, unit="ms", utc=True) + pd.Timedelta(hours=1)
        V[f"dvol_{cur_}"] = d.sort_index().close.astype(float); log("DVOL", cur_, len(d))
    except Exception as e: log("DVOL hata", cur_, e)
# ---------- G Yahoo günlük ----------
try:
    import yfinance as yf
    for ad, tk in {"cme": "BTC=F", "btcusd": "BTC-USD", "dxy": "DX-Y.NYB", "tnx": "^TNX", "vix": "^VIX", "spx": "^GSPC", "altin": "GC=F", "hyg": "HYG"}.items():
        h = yf.Ticker(tk).history(start="2022-01-01", auto_adjust=True)["Close"]; V[f"y_{ad}"] = pd.Series(h.values, index=pd.DatetimeIndex([x.date() for x in h.index]))
    log("Yahoo", len(V["y_spx"]))
except Exception as e: log("Yahoo hata", e)
pd.to_pickle(V, "kosul_veri.pkl"); log("kaydedildi:", ", ".join(f"{k} {len(v)}" for k, v in V.items()))
