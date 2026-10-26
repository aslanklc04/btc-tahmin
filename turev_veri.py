# turev_veri.py — PROTOKOL_turev.md: coin başı vadeli piyasa özellikleri, sinyal anlarında (parça I / N, coin'e göre)
import io, sys, time, zipfile, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
I, N = int(sys.argv[1]), int(sys.argv[2]); T0 = time.time(); S = requests.Session(); B = "https://data.binance.vision/data/futures/um"
V = pd.read_csv("veri_seti.csv.gz", usecols=["t", "nm", "sinif", "H"]); V["t"] = pd.to_datetime(V.t, utc=True)
COINS = sorted(V.nm.unique())[I::N]
def zipcsv(url):
    for k in range(4):
        try:
            r = S.get(url, timeout=40)
            if r.status_code == 404: return None
            if r.status_code == 200:
                z = zipfile.ZipFile(io.BytesIO(r.content)); return pd.read_csv(z.open(z.namelist()[0]))
        except Exception: time.sleep(1 + k)
    return None
def sembol(nm):
    for s in (f"{nm}USDT", f"1000{nm}USDT"):
        if zipcsv(f"{B}/monthly/fundingRate/{s}/{s}-fundingRate-2024-06.zip") is not None or zipcsv(f"{B}/daily/metrics/{s}/{s}-metrics-2025-06-01.zip") is not None: return s
    return None
def z(x, n, mp): return (x - x.rolling(n, min_periods=mp).mean()) / (x.rolling(n, min_periods=mp).std() + 1e-12)
R = []
for nm in COINS:
    try:
        s = sembol(nm)
        if s is None: print(nm, "vadeli sembol yok", flush=True); continue
        d0 = V[V.nm == nm].t.min() - pd.Timedelta(days=35); d1 = V[V.nm == nm].t.max() + pd.Timedelta(days=1); gunler = pd.date_range(d0.normalize(), d1.normalize(), freq="D")
        with ThreadPoolExecutor(16) as ex: P = [p for p in ex.map(lambda g: zipcsv(f"{B}/daily/metrics/{s}/{s}-metrics-{g:%Y-%m-%d}.zip"), gunler) if p is not None]
        F = pd.DataFrame()
        if P:
            m = pd.concat(P); m["ct"] = pd.to_datetime(m.create_time, utc=True); m = m.drop_duplicates("ct").set_index("ct").sort_index()
            h = m[["sum_open_interest_value", "sum_toptrader_long_short_ratio", "count_long_short_ratio"]].astype(float).resample("1h", label="right", closed="right").last()
            tk = m["sum_taker_long_short_vol_ratio"].astype(float).resample("1h", label="right", closed="right").mean()
            oi = np.log(h.sum_open_interest_value.where(h.sum_open_interest_value > 0))
            F = pd.DataFrame({"oi24": oi - oi.shift(24), "oi4": oi - oi.shift(4), "ls_top": z(h.sum_toptrader_long_short_ratio, 720, 168), "ls_all": z(h.count_long_short_ratio, 720, 168),
                              "taker": z(tk.rolling(24, min_periods=12).mean(), 720, 168)})
        aylar = pd.date_range(d0.normalize().replace(day=1), d1, freq="MS")
        with ThreadPoolExecutor(8) as ex: FR = [p for p in ex.map(lambda a: zipcsv(f"{B}/monthly/fundingRate/{s}/{s}-fundingRate-{a:%Y-%m}.zip"), aylar) if p is not None]
        with ThreadPoolExecutor(8) as ex: PI = [p for p in ex.map(lambda a: zipcsv(f"{B}/monthly/premiumIndexKlines/{s}/1h/{s}-1h-{a:%Y-%m}.zip"), aylar) if p is not None]
        fz = pd.Series(dtype=float)
        if FR:
            f = pd.concat(FR); f.columns = [c.strip() for c in f.columns]; f = f[pd.to_numeric(f.calc_time, errors="coerce").notna()]
            f.index = pd.to_datetime(f.calc_time.astype("int64"), unit="ms", utc=True); f = f.sort_index()[~f.index.duplicated()]
            fr = f.last_funding_rate.astype(float); fz = z(fr, 90, 30)
        bz = pd.Series(dtype=float)
        if PI:
            p = pd.concat(PI); p = p[pd.to_numeric(p.iloc[:, 0], errors="coerce").notna()]
            p.index = pd.to_datetime(p.iloc[:, 0].astype("int64"), unit="ms", utc=True) + pd.Timedelta(hours=1); p = p.sort_index()[~p.index.duplicated()]
            c = p.iloc[:, 4].astype(float); bz = z(c.rolling(24, min_periods=12).mean(), 720, 168)
        sv = V[V.nm == nm]
        for r in sv.itertuples():
            row = dict(t=r.t, nm=nm, sinif=r.sinif, H=r.H, sym=s)
            if len(F):
                i = F.index.searchsorted(r.t, side="right") - 1
                if i >= 0 and r.t - F.index[i] <= pd.Timedelta(hours=2): row.update(F.iloc[i].to_dict())
            if len(fz):
                i = fz.index.searchsorted(r.t, side="right") - 1
                if i >= 0: row["fon"] = fz.iloc[i]
            if len(bz):
                i = bz.index.searchsorted(r.t, side="right") - 1
                if i >= 0 and r.t - bz.index[i] <= pd.Timedelta(hours=2): row["baz"] = bz.iloc[i]
            R.append(row)
        print(f"{nm} ({s}): metrics {len(P)} gün · fonlama {len(FR)} ay · prim {len(PI)} ay · {len(sv)} sinyal · {time.time() - T0:.0f} sn", flush=True)
    except Exception as e: print(nm, "HATA", repr(e)[:200], flush=True)
pd.DataFrame(R).to_csv(f"turev_p{I}.csv.gz", index=False, compression="gzip"); print("bitti", len(R))
