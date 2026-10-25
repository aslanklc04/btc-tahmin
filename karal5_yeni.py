# karal5_yeni.py — PROTOKOL_karal5.md YENİ VERİ (parça I / N): BTC olay saatleri × coin, 5 dk, B girişi, taban S 0.75 + seçilen kurallar
# Girdi: sekil_liste.json (A/B evrenleri) · coinsec_olay.csv (BTC olay saatleri, t = sinyal saatinin kapanışı, UTC)
import io, sys, json, time, zipfile, requests, numpy as np, pandas as pd
import karal5_motor as M
from concurrent.futures import ThreadPoolExecutor
I, N = int(sys.argv[1]), int(sys.argv[2]); T0 = time.time(); S = requests.Session(); A = "https://data.binance.vision/data/spot/monthly/klines"
LS = json.load(open("sekil_liste.json")); IS = [("A", c) for c in LS["A"] if c != "BTC"] + [("B", c) for c in LS["B"]]; IS = IS[I::N] + ([("BTC", "BTC")] if I == 0 else [])
AYLAR = pd.date_range("2022-04-01", "2026-09-01", freq="MS")
OL = pd.read_csv("coinsec_olay.csv"); OL["t"] = pd.to_datetime(OL.t, utc=True); OL = OL[OL.t >= pd.Timestamp("2022-06-01", tz="UTC")]
H = 4; SEC = json.load(open("karal5_secim.json")); TUM = dict(M.kurallar(0.75)); ADL = [SEC["taban"]] + SEC["secim"]; RR = [(a, TUM[a]) for a in ADL]
def ay(arg):
    c, m = arg
    for k in range(4):
        try:
            r = S.get(f"{A}/{c}USDT/5m/{c}USDT-5m-{m:%Y-%m}.zip", timeout=40)
            if r.status_code == 404: return None
            if r.status_code == 200:
                z = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=[0, 1, 2, 3, 4, 7])
                if not str(d.iloc[0, 0]).isdigit(): d = d.iloc[1:].astype(float)
                return d
        except Exception: time.sleep(2 + 2 * k)
    return None
def yukle(c):
    with ThreadPoolExecutor(12) as ex: P = [p for p in ex.map(ay, [(c, m) for m in AYLAR]) if p is not None]
    if not P: return None
    d = pd.concat(P); d.columns = ["t", "o", "h", "l", "c", "qv"]; d["t"] = d.t.astype("int64"); d.loc[d.t > 10**14, "t"] //= 1000   # 2025+: mikro saniye
    d.index = pd.to_datetime(d.t, unit="ms", utc=True); d = d[~d.index.duplicated()].sort_index().drop(columns="t").astype(float)
    return d.reindex(pd.date_range(d.index[0], d.index[-1], freq="5min"))                     # indeks = 5 dk mumun AÇILIŞ zamanı
def saatlik(d):
    h = d.resample("1h").agg({"c": "last", "qv": "sum"}); h.index = h.index + pd.Timedelta(hours=1)   # indeks = saatin KAPANIŞI (t'de bilinir)
    h["c"] = h.c.ffill(limit=2); return h
DB = yukle("BTC"); HB = saatlik(DB); LRB = np.log(HB.c).diff(); R24B = np.log(HB.c / HB.c.shift(24))
print(f"BTC 5 dk: {len(DB):,} · {DB.index[0]} → {DB.index[-1]} · {time.time() - T0:.0f} sn", flush=True)
def ozellik(h):
    lr = np.log(h.c).diff(); s = lr.rolling(720, min_periods=600).std()
    vb = LRB.reindex(h.index); beta = lr.rolling(720, min_periods=600).cov(vb) / vb.rolling(720, min_periods=600).var()
    rho = lr.rolling(720, min_periods=600).corr(vb); r24 = np.log(h.c / h.c.shift(24)); sq = s * np.sqrt(24)
    return pd.DataFrame({"s": s, "beta": beta, "rho": rho, "rz": r24 / sq, "rel": (r24 - beta * R24B.reindex(h.index)) / sq, "liq": np.log(h.qv.rolling(720, min_periods=600).mean())})
def islem(d, t, s):
    i0 = d.index.get_indexer([t - pd.Timedelta(minutes=5)])[0]
    if i0 < 0: return None
    n = 1 + 2 * H * 12 + 2; w = d.iloc[i0:i0 + n]
    if len(w) < 1 + H * 12 + 1 or w[["o", "h", "l", "c"]].isna().any().any(): return None
    G = w.c.values[0]; O, Hh, Lo, C = (w[k].values[1:] for k in ("o", "h", "l", "c")); Hb = H * 12; t0m = int(t.timestamp() // 60); su = s * np.sqrt(H)
    if O[1] <= G: e, chk, Pe, fin = 1, 1, O[1], M.FP
    else:
        x = np.where(Lo[1:13] <= G)[0]                                                          # t+5 → t+60 dk mumları
        if not len(x): return np.full(len(RR), np.nan)
        e = 1 + int(x[0]); chk, Pe, fin = e + 1, G, M.FL
    return M.motor(Hh, Lo, C, e, chk, Pe, fin, G, su, Hb, t0m, 5, RR)
R = []
for g, c in IS:
    try:
        d = DB if c == "BTC" else yukle(c)
        if d is None or len(d) < 12 * 24 * 60: print(c, "veri yok", flush=True); continue
        F = ozellik(saatlik(d)).reindex(OL.t)
        for t, f in zip(OL.t, F.itertuples(index=False)):
            if not (np.isfinite(f.s) and f.s > 0 and np.isfinite(f.beta) and np.isfinite(f.liq)): continue
            x = islem(d, t, f.s)
            if x is None: continue
            R.append(dict(t=t, coin=c, grp=g, **{f"r{j}": float(v) for j, v in enumerate(x)}))
        print(f"{g} {c}: {sum(1 for r in R if r['coin'] == c)} olay · {time.time() - T0:.0f} sn", flush=True)
    except Exception as e: print(c, "HATA", repr(e)[:200], flush=True)
pd.DataFrame(R).to_csv(f"karal5y_p{I}.csv.gz", index=False, compression="gzip"); print("bitti", len(R), f"{time.time() - T0:.0f} sn")
