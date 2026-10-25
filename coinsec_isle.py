# coinsec_isle.py — PROTOKOL_coinsec.md: her coin için BTC olay saatlerinde özellikler + gerçekçi 4 saatlik işlem sonucu (parça I / N)
# Girdi: sekil_liste.json (A/B evrenleri) · coinsec_olay.csv (BTC olay saatleri, t = sinyal saatinin kapanışı, UTC)
import io, sys, json, time, zipfile, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
I, N = int(sys.argv[1]), int(sys.argv[2]); T0 = time.time(); S = requests.Session(); A = "https://data.binance.vision/data/spot/monthly/klines"
LS = json.load(open("sekil_liste.json")); IS = [("A", c) for c in LS["A"] if c != "BTC"] + [("B", c) for c in LS["B"]]; IS = IS[I::N] + ([("BTC", "BTC")] if I == 0 else [])
AYLAR = pd.date_range("2022-04-01", "2026-09-01", freq="MS")
OL = pd.read_csv("coinsec_olay.csv"); OL["t"] = pd.to_datetime(OL.t, utc=True); OL = OL[OL.t >= pd.Timestamp("2022-06-01", tz="UTC")]
FL, FP, FON, K, H = 0.0002, 0.0005, 0.0001, 0.75, 4
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
    """t: sinyal saatinin kapanışı. Dönüş: (doldu mu, B neti, D neti, 🎯 değdi mi) — PROTOKOL_coinsec 'İşlem ölçümü'."""
    i0 = d.index.get_indexer([t - pd.Timedelta(minutes=5)])[0]
    if i0 < 0: return None
    n = 1 + 1 + H * 12 + 1                                                                   # G mumu · t+0 · … · t+4 s+5 dk mumu
    w = d.iloc[i0:i0 + n]
    if len(w) < n or w[["o", "h", "l", "c"]].isna().any().any(): return None
    O, Hh, L, C = w.o.values, w.h.values, w.l.values, w.c.values; G = C[0]; tp = G * (1 + K * s * np.sqrt(H)); ex = n - 1   # ex = t+4 s+5 dk mumu (kapanışında çık)
    t0m = int(t.timestamp() // 60)
    def kapat(e, Pe, fin, chk):                                                               # e: giriş mumu sırası (1 = t+0)
        if tp <= Pe: j, cik, fo = e, Pe, FP
        else:
            hit = np.where(Hh[chk:ex + 1] >= tp)[0]
            if len(hit): j, cik, fo = chk + hit[0], tp, FL
            else: j, cik, fo = ex, C[ex], FP
        nf = (t0m + (j - 1) * 5 + 5) // 480 - (t0m + (e - 1) * 5) // 480
        return cik / Pe - 1 - fin - fo - FON * nf, cik == tp
    nD, _ = kapat(2, O[2], FP, 2)                                                             # D: t+5 dk mumunun açılışından piyasa
    if O[2] <= G: nB, tB = kapat(2, O[2], FP, 2); return True, nB, nD, tB                   # ilk mum G'nin altında açıldı → hemen dolar
    hit = np.where(L[2:14] <= G)[0]                                                           # t+5 → t+65 dk (12 mum)
    if not len(hit): return False, np.nan, nD, False
    e = 2 + hit[0]; nB, tB = kapat(e, G, FL, e + 1); return True, nB, nD, tB                # limit dolumu: 🎯 kontrolü sonraki mumdan
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
            R.append(dict(t=t, coin=c, grp=g, s=f.s, beta=f.beta, rho=f.rho, rz=f.rz, rel=f.rel, liq=f.liq, fB=x[0], nB=x[1], nD=x[2], tpB=x[3]))
        print(f"{g} {c}: {sum(1 for r in R if r['coin'] == c)} olay · {time.time() - T0:.0f} sn", flush=True)
    except Exception as e: print(c, "HATA", repr(e)[:200], flush=True)
pd.DataFrame(R).to_csv(f"coinsec_p{I}.csv.gz", index=False, compression="gzip"); print("bitti", len(R), f"{time.time() - T0:.0f} sn")
