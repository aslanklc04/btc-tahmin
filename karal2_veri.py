# karal2_veri.py — PROTOKOL_karal2.md veri aşaması (24.10.2026). Yalnız veri: her sinyal için tüm formüllerin neti (vadeli + fonlama yaklaşığı).
# Girdi: veri_seti.csv.gz (sinyaller, giriş P/PB/fB/mB, s = σ720·√H). 1 dk Binance mumu t → t+2H; saatlik mum (σ168, σ24, ATR14 için).
import time, numpy as np, pandas as pd, requests
from concurrent.futures import ThreadPoolExecutor
T0 = time.time(); U = "https://data-api.binance.vision/api/v3/klines"
V = pd.read_csv("veri_seti.csv.gz"); V["t"] = pd.to_datetime(V.t, utc=True)
KS = {"✅ ana (+0,75σ)": 0.75, "🔸 yedek (+0,50σ)": 0.5, "📋 panelden (+0,45σ)": 0.45}
KG = [0.3, 0.45, 0.6, 0.75, 0.9, 1.1]; TAU = [0.25, 0.5, 1.0]; FL, FP, FON = 0.0002, 0.0005, 0.0001
S = requests.Session()
def kl(sym, iv, a_ms, b_ms):
    out, cur = [], a_ms
    while cur < b_ms:
        for k in range(6):
            try:
                r = S.get(U, params=dict(symbol=sym, interval=iv, startTime=cur, endTime=b_ms - 1, limit=1000), timeout=20)
                if r.status_code in (418, 429): time.sleep(20 + 10 * k); continue
                x = r.json(); break
            except Exception: time.sleep(2 + k); x = None
        if not isinstance(x, list) or not x: break
        out += x; cur = x[-1][0] + (60_000 if iv == "1m" else 3_600_000)
        if len(x) < 1000: break
    return out
# ---- saatlik: σ168, σ24, ATR14 (sinyal anına kadar) ----
def saatlik(nm):
    x = kl(f"{nm}USDT", "1h", int(pd.Timestamp("2022-04-01", tz="UTC").timestamp() * 1000), int(time.time() * 1000))
    if not x: return nm, None
    d = pd.DataFrame([r[:5] for r in x], columns=["o", "a", "h", "l", "c"]).astype(float); d.index = pd.to_datetime(d.o, unit="ms", utc=True) + pd.Timedelta(hours=1)
    d = d[~d.index.duplicated()]; lr = np.log(d.c).diff()
    return nm, pd.DataFrame({"s168": lr.rolling(168).std(), "s24": lr.rolling(24).std(), "atr": ((d.h - d.l) / d.c).rolling(14).mean()})
with ThreadPoolExecutor(6) as ex: HS = {k: v for k, v in ex.map(saatlik, sorted(set(V.nm))) if v is not None}
print(f"saatlik: {len(HS)} coin · {time.time() - T0:.0f} sn", flush=True)
def sim(Hh, Lo, C, e, chk, Pe, fin, tp, Hm, t0m, tau=None, s1=None, uzat=False):
    """e: giriş dakikası · chk: 🎯 kontrolünün başladığı dakika · Pe: giriş fiyatı · Hm: süre sonu dakika sayısı · t0m: t'nin epoch dakikası."""
    if tp <= Pe: return -fin - FP                                                              # 🎯 girişin altında → hemen piyasa çıkış
    n = min(len(C), Hm)
    w = np.where(Hh[chk:n] >= tp)[0]
    if len(w):
        m = chk + w[0]
        if tau is None: cik, fo, j = tp, FL, m
        else:
            hi = Hh[m:n]; lo = Lo[m:n]; rm = np.maximum.accumulate(np.maximum(hi, tp))
            st = np.maximum(Pe * 1.002, np.concatenate([[tp], rm[:-1]]) * (1 - tau * s1))
            ww = np.where(lo[1:] <= st[1:])[0]
            if len(ww): j = m + 1 + ww[0]; cik, fo = st[1 + ww[0]], FP
            else: j = n - 1; cik, fo = C[n - 1], FP
    else:
        j = n - 1; cik, fo = C[n - 1], FP
        if uzat and C[n - 1] < Pe and len(C) > n:
            be = Pe * 1.0007; n2 = min(len(C), 2 * Hm); w2 = np.where(Hh[n:n2] >= be)[0]
            if len(w2): j = n + w2[0]; cik, fo = be, FL
            else: j = n2 - 1; cik, fo = C[n2 - 1], FP
    nf = (t0m + j + 1) // 480 - (t0m + e) // 480                                              # geçilen 00/08/16 UTC sayısı
    return cik / Pe - 1 - fin - fo - FON * nf
def isle(i):
    r = V.loc[i]; H = int(r.H); Hm = H * 60; t0 = r.t; t0m = int(t0.timestamp() // 60)
    x = kl(f"{r.nm}USDT", "1m", int(t0.timestamp() * 1000), int((t0 + pd.Timedelta(minutes=2 * Hm)).timestamp() * 1000))
    if len(x) < min(Hm, 70) or int(x[0][0]) != int(t0.timestamp() * 1000): return None
    M = np.array([[float(v) for v in z[1:5]] for z in x]); O, Hh, Lo, C = M[:, 0], M[:, 1], M[:, 2], M[:, 3]
    if len(C) < Hm: return None
    k0 = KS[r.sinif]; s1 = r.s / np.sqrt(H); hs = HS.get(r.nm); ex_ = hs.loc[t0] if (hs is not None and t0 in hs.index) else None
    o = {"i": i}
    for gir in ("B", "D"):
        if gir == "D": e, Pe, fin, chk = 7, O[7], FP, 7
        else:
            if r.fB != 1: continue
            e = int(r.mB); Pe = r.PB; fin = FP if e == 7 else FL; chk = e if e == 7 else e + 1
        tp0 = r.G * (1 + k0 * r.s); a = dict(Hh=Hh, Lo=Lo, C=C, e=e, chk=chk, Pe=Pe, fin=fin, Hm=Hm, t0m=t0m)
        o[f"{gir}_T0"] = sim(tp=tp0, **a)
        for tau in TAU: o[f"{gir}_T1_{tau}"] = sim(tp=tp0, tau=tau, s1=s1, **a)
        o[f"{gir}_T3"] = sim(tp=tp0, uzat=True, **a)
        o[f"{gir}_T13"] = sim(tp=tp0, tau=0.5, s1=s1, uzat=True, **a)
        if ex_ is not None and np.isfinite(ex_.values).all():
            for nmx, sx in (("s168", ex_.s168 * np.sqrt(H)), ("s24", ex_.s24 * np.sqrt(H)), ("atr", ex_.atr * np.sqrt(H))):
                for k in KG: o[f"{gir}_T2_{nmx}_{k}"] = sim(tp=r.G * (1 + k * sx), **a)
    return o
T1 = time.time(); R = []
with ThreadPoolExecutor(6) as ex:
    for n_, o in enumerate(ex.map(isle, list(V.index))):
        if o: R.append(o)
        if n_ % 2000 == 0: print(f"{n_}/{len(V)} · {time.time() - T1:.0f} sn", flush=True)
D = pd.DataFrame(R).set_index("i"); D = V[["t", "nm", "sinif", "H"]].join(D, how="inner")
D.to_csv("karal2_veri.csv.gz", index=False, compression="gzip")
open("karal2_veri_ozet.md", "w").write(f"# karal2_veri.csv.gz — {pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M}\n{len(D):,} / {len(V):,} sinyal · {len(D.columns)} sütun · {time.time() - T0:.0f} sn\n_Yalnız veri (PROTOKOL_karal2.md)._\n")
print(f"bitti: {len(D):,} sinyal · {time.time() - T0:.0f} sn")
