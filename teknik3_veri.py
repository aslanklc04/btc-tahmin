# teknik3_veri.py — PROTOKOL_teknik3.md veri: 141 coin + BTC, Binance vadeli 1 s OHLCV (yoksa spot) → teknik3_mum_{0,1,2}.parquet
import io, sys, time, zipfile, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
T0 = time.time(); S = requests.Session(); V = "https://data.binance.vision/data"
COINS = sorted(set(pd.read_csv("veri_seti.csv.gz", usecols=["nm"]).nm) | {"BTC"})
AY = pd.period_range("2021-11", "2026-09", freq="M").strftime("%Y-%m"); GUN = pd.date_range("2026-10-01", "2026-10-30").strftime("%Y-%m-%d")
def get(u):
    for k in range(4):
        try:
            r = S.get(u, timeout=60)
            if r.status_code == 200: return r.content
            if r.status_code == 404: return None
        except Exception: pass
        time.sleep(2 + 2 * k)
    return None
def mum(nm):
    for pazar, sym in (("futures/um", f"{nm}USDT"), ("futures/um", f"1000{nm}USDT"), ("spot", f"{nm}USDT")):
        P = []
        for u in [f"{V}/{pazar}/monthly/klines/{sym}/1h/{sym}-1h-{a}.zip" for a in AY] + [f"{V}/{pazar}/daily/klines/{sym}/1h/{sym}-1h-{g}.zip" for g in GUN]:
            b = get(u)
            if b:
                z = zipfile.ZipFile(io.BytesIO(b)); d = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=[0, 1, 2, 3, 4, 7]); P.append(d[pd.to_numeric(d[0], errors="coerce").notna()].astype(float))
        if P:
            k = pd.concat(P, ignore_index=True); k.columns = ["ot", "o", "h", "l", "c", "qv"]; k.loc[k.ot > 1e14, "ot"] = k.ot / 1000
            k = k.drop_duplicates("ot").sort_values("ot"); k["t"] = pd.to_datetime(k.ot, unit="ms", utc=True); k["coin"] = nm; k["kaynak"] = pazar[:3]
            return k.drop(columns="ot")
    return None
with ThreadPoolExecutor(8) as ex: R = [x for x in ex.map(mum, COINS) if x is not None]
print(f"[{time.time() - T0:.0f} sn] coin {len(R)} / {len(COINS)}", flush=True)
A = pd.concat(R, ignore_index=True).astype({c: "float32" for c in ("o", "h", "l", "c", "qv")}); A["coin"] = A.coin.astype("category"); A["kaynak"] = A.kaynak.astype("category")
cs = sorted(A.coin.unique())
for i in range(3):
    p = A[A.coin.isin(cs[i::3])]; p.to_parquet(f"teknik3_mum_{i}.parquet", index=False, compression="zstd"); print(i, len(p), flush=True)
print(f"[{time.time() - T0:.0f} sn] bitti satır {len(A)}")
