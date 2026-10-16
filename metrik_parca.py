# metrik_parca.py — Binance USDT-M vadeli "metrics" arşivi (5 dk: açık pozisyon, büyük oyuncu long/short, tüm hesaplar long/short, agresif alıcı/satıcı hacim oranı) → saatlik
# Kullanım: python metrik_parca.py <parca> <parca_sayisi> → metrik_parca{parca}.pkl {coin: DataFrame(oi, top_ls, ls, taker)}  (16.10.2026, vadeli.py için)
import sys, io, zipfile, time, requests, pandas as pd
from concurrent.futures import ThreadPoolExecutor
i, k = int(sys.argv[1]), int(sys.argv[2]); T0 = time.time()
GEN = [l.strip()[:-4] for l in open("canli/durum/genis_liste.txt") if l.strip()]
CEK = [l.strip()[:-4] for l in open("canli/durum/coin_listesi.txt") if l.strip()]
PA = pd.read_csv("canli/durum/prim_acik.csv").coin.tolist()
HEPSI = sorted(set(GEN) | set(CEK) | set(PA) | {"BTC", "ETH"}); BENIM = HEPSI[i::k]
S = requests.Session()
def gun(arg):
    sym, g = arg
    for kk in range(3):
        try:
            r = S.get(f"https://data.binance.vision/data/futures/um/daily/metrics/{sym}/{sym}-metrics-{g}.zip", timeout=40)
            if r.status_code == 404: return None
            if r.status_code != 200: time.sleep(1 + kk); continue
            z_ = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z_.open(z_.namelist()[0]))
            d.columns = [c.strip().lower() for c in d.columns]
            d["t"] = pd.to_datetime(d.create_time, utc=True).dt.ceil("h")
            for c in ("sum_open_interest_value", "sum_toptrader_long_short_ratio", "count_long_short_ratio", "sum_taker_long_short_vol_ratio"): d[c] = pd.to_numeric(d[c], errors="coerce")
            g_ = d.groupby("t")
            return pd.DataFrame({"oi": g_.sum_open_interest_value.last(), "top_ls": g_.sum_toptrader_long_short_ratio.mean(), "ls": g_.count_long_short_ratio.mean(), "taker": g_.sum_taker_long_short_vol_ratio.mean()})
        except Exception: time.sleep(1 + kk)
    return None
GUNLER = [d.strftime("%Y-%m-%d") for d in pd.date_range("2022-01-01", "2026-10-14", freq="D")]
OUT = {}
for nm in BENIM:
    for sym in (nm + "USDT", "1000" + nm + "USDT"):
        if gun((sym, "2026-09-15")) is None and gun((sym, "2025-06-15")) is None and gun((sym, "2024-06-15")) is None: continue
        with ThreadPoolExecutor(16) as ex: parts = [p for p in ex.map(gun, [(sym, g) for g in GUNLER]) if p is not None and len(p)]
        if parts:
            D = pd.concat(parts).sort_index(); D = D[~D.index.duplicated()]; D.index = pd.DatetimeIndex(D.index).as_unit("ns"); OUT[nm] = D
        print(nm, sym, "gün:", len(parts), f"{time.time()-T0:.0f} sn", flush=True); break
    else: print(nm, "vadeli arşivde yok", flush=True)
pd.to_pickle(OUT, f"metrik_parca{i}.pkl"); print(f"parça {i}: {len(OUT)}/{len(BENIM)} coin · {time.time()-T0:.0f} sn")
