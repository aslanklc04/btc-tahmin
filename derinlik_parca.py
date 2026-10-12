# derinlik_parca.py — Binance USDT-M vadeli emir defteri arşivi (bookDepth ±%1, saatlik ortalama) — geniş liste + 💵 coin'leri, parça parça.
# Kullanım: python derinlik_parca.py <parca> <parca_sayisi>   → derinlik_parca{parca}.pkl  {coin: DataFrame(ask1, bid1)}
import sys, io, zipfile, time, requests, pandas as pd
from concurrent.futures import ThreadPoolExecutor
i, k = int(sys.argv[1]), int(sys.argv[2]); T0 = time.time()
GEN = [l.strip()[:-4] for l in open("canli/durum/genis_liste.txt") if l.strip()]
PA = pd.read_csv("canli/durum/prim_acik.csv").coin.tolist()
ESKI = {"BTC", "ETH", "ADA", "APT", "ARB", "BNB", "DOGE", "DOT", "FLOKI", "LINK", "NEAR", "OP", "PEPE", "SHIB", "SUI"}
HEPSI = sorted((set(GEN) | set(PA)) - ESKI); BENIM = HEPSI[i::k]
S = requests.Session()
def gun(arg):
    sym, g = arg
    for kk in range(3):
        try:
            r = S.get(f"https://data.binance.vision/data/futures/um/daily/bookDepth/{sym}/{sym}-bookDepth-{g}.zip", timeout=40)
            if r.status_code == 404: return None
            if r.status_code != 200: time.sleep(1 + kk); continue
            z_ = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z_.open(z_.namelist()[0]))
            d.columns = [c.strip().lower() for c in d.columns]
            if "percentage" not in d.columns: d = pd.read_csv(z_.open(z_.namelist()[0]), header=None, names=["timestamp", "percentage", "depth", "notional"])
            d = d[pd.to_numeric(d.percentage, errors="coerce").isin([1, -1])].copy()
            d["t"] = pd.to_datetime(d.timestamp, utc=True).dt.ceil("h"); d["percentage"] = d.percentage.astype(float); d["notional"] = d.notional.astype(float)
            return d.pivot_table(index="t", columns="percentage", values="notional", aggfunc="mean").rename(columns={1.0: "ask1", -1.0: "bid1"})
        except Exception: time.sleep(1 + kk)
    return None
GUNLER = [d.strftime("%Y-%m-%d") for d in pd.date_range("2022-12-01", "2026-09-30", freq="D")]
DER = {}
for nm in BENIM:
    for sym in (nm + "USDT", "1000" + nm + "USDT"):
        if gun((sym, "2026-09-15")) is None and gun((sym, "2025-06-15")) is None and gun((sym, "2024-06-15")) is None: continue
        with ThreadPoolExecutor(16) as ex: parts = [p for p in ex.map(gun, [(sym, g) for g in GUNLER]) if p is not None and len(p)]
        if parts:
            D = pd.concat(parts).sort_index(); D = D[~D.index.duplicated()]; D.index = pd.DatetimeIndex(D.index).as_unit("ns"); DER[nm] = D
        print(nm, sym, "gün:", len(parts), f"{time.time()-T0:.0f} sn", flush=True); break
    else: print(nm, "vadeli arşivde yok", flush=True)
pd.to_pickle(DER, f"derinlik_parca{i}.pkl"); print(f"parça {i}: {len(DER)}/{len(BENIM)} coin · {time.time()-T0:.0f} sn")
