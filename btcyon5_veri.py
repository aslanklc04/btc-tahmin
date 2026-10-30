# btcyon5_veri.py — PROTOKOL_btcyon5.md veri: Binance vadeli emir defteri arşivi (bookDepth) → saatlik · Deribit opsiyon işlemleri örneklemi (günde 2×1000)
import io, time, zipfile, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
T0 = time.time(); S = requests.Session(); V = "https://data.binance.vision/data/futures/um/daily/bookDepth/BTCUSDT"
def log(*a): print(f"[{time.time() - T0:5.0f} sn]", *a, flush=True)
def get(u, **kw):
    for k in range(5):
        try:
            r = S.get(u, timeout=60, **kw)
            if r.status_code == 200: return r
            if r.status_code in (400, 404): return None
            if r.status_code == 429: time.sleep(5 + 5 * k); continue
        except Exception: pass
        time.sleep(2 + 3 * k)
    return None
def kitap(g):
    r = get(f"{V}/BTCUSDT-bookDepth-{g}.zip")
    if r is None: return None
    try:
        z = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z.open(z.namelist()[0])); d.columns = [c.strip().lower() for c in d.columns]
        d["t"] = pd.to_datetime(d.timestamp, utc=True).dt.floor("h"); d["percentage"] = pd.to_numeric(d.percentage, errors="coerce"); d["notional"] = pd.to_numeric(d.notional, errors="coerce")
        w = d.pivot_table(index="t", columns="percentage", values="notional", aggfunc="mean"); w.columns = [f"p{int(c):+d}" for c in w.columns]; return w
    except Exception as e: log("kitap", g, e); return None
G = pd.date_range("2022-01-01", "2026-10-29").strftime("%Y-%m-%d")
with ThreadPoolExecutor(12) as ex: P = [x for x in ex.map(kitap, G) if x is not None]
if P:
    KD = pd.concat(P).sort_index(); KD = KD[~KD.index.duplicated()]; KD.astype("float32").rename_axis("t").reset_index().to_parquet("btcyon5_kitap.parquet", index=False)
    log("emir defteri", len(KD), KD.index.min(), KD.index.max(), list(KD.columns))
else: log("emir defteri YOK")
def islemler(arg):
    a = arg; b = a + 12 * 3600_000
    for base in ("https://history.deribit.com", "https://www.deribit.com"):
        r = get(f"{base}/api/v2/public/get_last_trades_by_currency_and_time", params=dict(currency="BTC", kind="option", start_timestamp=a, end_timestamp=b, count=1000, sorting="asc"))
        if r is not None:
            tr = r.json().get("result", {}).get("trades", [])
            if tr: return [(x["timestamp"], x["instrument_name"], 1 if x["direction"] == "buy" else -1, x["price"], x["amount"], x.get("iv", np.nan), x.get("index_price", np.nan)) for x in tr]
    return []
BAS = [int(t.timestamp() * 1000) for d in pd.date_range("2022-01-01", "2026-10-28", tz="UTC") for t in (d, d + pd.Timedelta(hours=12))]
R = []
with ThreadPoolExecutor(4) as ex:
    for i, x in enumerate(ex.map(islemler, BAS)):
        R += x
        if i % 500 == 0: log("deribit", i, "/", len(BAS), "işlem", len(R))
O = pd.DataFrame(R, columns=["ts", "ins", "yon", "fiyat", "miktar", "iv", "endeks"])
if len(O):
    p = O.ins.str.split("-", expand=True); O["vade"] = pd.to_datetime(p[1], format="%d%b%y", utc=True) + pd.Timedelta(hours=8); O["kul"] = pd.to_numeric(p[2], errors="coerce"); O["tur"] = p[3]
    O["t"] = pd.to_datetime(O.ts, unit="ms", utc=True)
    O = O.drop(columns=["ts", "ins"]).astype({"yon": "int8", "fiyat": "float32", "miktar": "float32", "iv": "float32", "endeks": "float32", "kul": "float32"}); O["tur"] = O.tur.astype("category")
    O.to_parquet("btcyon5_opsiyon.parquet", index=False); log("opsiyon işlem", len(O), O.t.min(), O.t.max(), "gün başı ort.", len(O) / O.t.dt.floor("D").nunique())
else: log("opsiyon YOK")
