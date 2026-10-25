# giris2.py — PROTOKOL_giris2.md veri aşaması (parça I / N): her sinyal için 9 giriş kuralının neti (karal2_veri.py ölçümüyle aynı)
import sys, time, numpy as np, pandas as pd, requests
from concurrent.futures import ThreadPoolExecutor
I, N = int(sys.argv[1]), int(sys.argv[2]); T0 = time.time(); U = "https://data-api.binance.vision/api/v3/klines"
V = pd.read_csv("veri_seti.csv.gz"); V["t"] = pd.to_datetime(V.t, utc=True); V = V.iloc[I::N]
KS = {"✅ ana (+0,75σ)": 0.75, "🔸 yedek (+0,50σ)": 0.5, "📋 panelden (+0,45σ)": 0.45}; FL, FP, FON = 0.0002, 0.0005, 0.0001
S = requests.Session()
def kl(sym, a_ms, b_ms):
    out, cur = [], a_ms
    while cur < b_ms:
        x = None
        for k in range(6):
            try:
                r = S.get(U, params=dict(symbol=sym, interval="1m", startTime=cur, endTime=b_ms - 1, limit=1000), timeout=20)
                if r.status_code in (418, 429): time.sleep(20 + 10 * k); continue
                x = r.json(); break
            except Exception: time.sleep(2 + k)
        if not isinstance(x, list) or not x: break
        out += x; cur = x[-1][0] + 60_000
        if len(x) < 1000: break
    return out
def sim(Hh, C, e, chk, Pe, fin, tp, Hm, t0m):
    if tp <= Pe: return -fin - FP
    n = min(len(C), Hm); w = np.where(Hh[chk:n] >= tp)[0]
    if len(w): j, cik, fo = chk + w[0], tp, FL
    else: j, cik, fo = n - 1, C[n - 1], FP
    nf = (t0m + j + 1) // 480 - (t0m + e) // 480
    return cik / Pe - 1 - fin - fo - FON * nf
def isle(i):
    r = V.loc[i]; H = int(r.H); Hm = H * 60; t0 = r.t; t0m = int(t0.timestamp() // 60)
    x = kl(f"{r.nm}USDT", int(t0.timestamp() * 1000), int((t0 + pd.Timedelta(minutes=Hm + 70)).timestamp() * 1000))
    if len(x) < Hm or int(x[0][0]) != int(t0.timestamp() * 1000): return None
    M = np.array([[float(v) for v in z[1:5]] for z in x]); O, Hh, Lo, C = M[:, 0], M[:, 1], M[:, 2], M[:, 3]
    G = r.G; tp = G * (1 + KS[r.sinif] * r.s); a = dict(Hh=Hh, C=C, tp=tp, Hm=Hm, t0m=t0m); o = {"i": i}
    def limit(L, son, piyasa):                                                                 # L: limit fiyatı · son: pencerenin son dakikası (dahil) · piyasa: dolmazsa son+1 açılışından gir
        if O[7] <= L: return sim(e=7, chk=7, Pe=O[7], fin=FP, **a)
        w = np.where(Lo[8:son + 1] <= L)[0]
        if len(w): m = 8 + w[0]; return sim(e=m, chk=m + 1, Pe=L, fin=FL, **a)
        if piyasa and son + 1 < len(O): m = son + 1; return sim(e=m, chk=m, Pe=O[m], fin=FP, **a)
        return np.nan
    o["B"] = limit(G, 66, False); o["D7"] = sim(e=7, chk=7, Pe=O[7], fin=FP, **a)
    for nn in (15, 30, 60): o[f"E{nn}"] = limit(G, 6 + nn, True)
    for d in (10, 25, 50): o[f"P{d}"] = limit(G * (1 + d / 10000), 66, False)
    o["P25E60"] = limit(G * 1.0025, 66, True)
    return o
R = []
with ThreadPoolExecutor(6) as ex:
    for n_, o in enumerate(ex.map(isle, list(V.index))):
        if o: R.append(o)
        if n_ % 1000 == 0: print(f"{n_}/{len(V)} · {time.time() - T0:.0f} sn", flush=True)
D = pd.DataFrame(R).set_index("i"); D = V[["t", "nm", "sinif", "H"]].join(D, how="inner")
D.to_csv(f"giris2_p{I}.csv.gz", index=False, compression="gzip"); print(f"bitti: {len(D):,} · {time.time() - T0:.0f} sn")
