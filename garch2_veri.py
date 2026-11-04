# garch2_veri.py — PROTOKOL_garch.md Ek 2: GARCH'a göre 🎯 (TG) ile 1 dk yeniden oynatma (Actions) → garch2_veri.csv.gz
import time, numpy as np, pandas as pd, requests
from concurrent.futures import ThreadPoolExecutor
T0 = time.time(); U = "https://data-api.binance.vision/api/v3/klines"; S = requests.Session()
K_ = ["t", "nm", "sinif", "H"]; FL, FP, FON = 0.0002, 0.0005, 0.0001
V = pd.read_csv("veri_seti.csv.gz").drop_duplicates(K_); V["t"] = pd.to_datetime(V.t, utc=True)
R = pd.read_csv("garch_rho.csv.gz", usecols=K_ + ["rho"]); R["t"] = pd.to_datetime(R.t, utc=True); V = V.merge(R, on=K_, how="inner").reset_index(drop=True)
KS = {"✅ ana (+0,75σ)": 0.75, "🔸 yedek (+0,50σ)": 0.5, "📋 panelden (+0,45σ)": 0.45}
def kl(sym, a, b):
    out, cur = [], a
    while cur < b:
        x = None
        for k in range(6):
            try:
                r = S.get(U, params=dict(symbol=sym, interval="1m", startTime=cur, endTime=b - 1, limit=1000), timeout=20)
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
    return cik / Pe - 1 - fin - fo - FON * ((t0m + j + 1) // 480 - (t0m + e) // 480)
def isle(i):
    r = V.loc[i]; H = int(r.H); Hm = H * 60; t0 = r.t; t0m = int(t0.timestamp() // 60)
    if not np.isfinite(r.rho): return None
    x = kl(f"{r.nm}USDT", int(t0.timestamp() * 1000), int((t0 + pd.Timedelta(minutes=Hm)).timestamp() * 1000))
    if len(x) < min(Hm, 70) or int(x[0][0]) != int(t0.timestamp() * 1000): return None
    M = np.array([[float(v) for v in z[1:5]] for z in x]); O, Hh, C = M[:, 0], M[:, 1], M[:, 3]
    if len(C) < Hm: return None
    k0 = KS[r.sinif]; rr = float(np.clip(r.rho, 0.5, 2.0)); o = {"i": i, "rho_k": rr}
    for gir in ("D", "B"):
        if gir == "D": e, Pe, fin, chk = 7, O[7], FP, 7
        else:
            if r.fB != 1: continue
            e = int(r.mB); Pe = r.PB; fin = FP if e == 7 else FL; chk = e if e == 7 else e + 1
        a = dict(Hh=Hh, C=C, e=e, chk=chk, Pe=Pe, fin=fin, Hm=Hm, t0m=t0m)
        o[f"{gir}_T0"] = sim(tp=r.G * (1 + k0 * r.s), **a); o[f"{gir}_TG"] = sim(tp=r.G * (1 + k0 * r.s * rr), **a)
    return o
T1 = time.time(); out = []
with ThreadPoolExecutor(6) as ex:
    for n_, o in enumerate(ex.map(isle, list(V.index))):
        if o: out.append(o)
        if n_ % 2000 == 0: print(f"{n_}/{len(V)} · {time.time() - T1:.0f} sn", flush=True)
D = pd.DataFrame(out).set_index("i"); D = V[K_ + ["tur"]].join(D, how="inner"); D.to_csv("garch2_veri.csv.gz", index=False, compression="gzip"); print("bitti", len(D))
