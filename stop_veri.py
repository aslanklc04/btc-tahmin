# stop_veri.py — PROTOKOL_stop.md veri + simülasyon (Actions). Her sinyal için stop türlerinin neti (D piyasa · B limit) ve stop olup olmadığı.
# Girdi: veri_seti.csv.gz (G, s = σ720·√H, giriş PB/fB/mB). 1 dk Binance mumu t → t+H; saatlik mum (ATR14).
import time, numpy as np, pandas as pd, requests
from concurrent.futures import ThreadPoolExecutor
T0 = time.time(); U = "https://data-api.binance.vision/api/v3/klines"
K_ = ["t", "nm", "sinif", "H"]
V = pd.read_csv("veri_seti.csv.gz").drop_duplicates(K_).reset_index(drop=True); V["t"] = pd.to_datetime(V.t, utc=True)
KS = {"✅ ana (+0,75σ)": 0.75, "🔸 yedek (+0,50σ)": 0.5, "📋 panelden (+0,45σ)": 0.45}
FL, FP, FON, SLIP = 0.0002, 0.0005, 0.0001, 0.0005
VAR = ["S0"] + [f"SS{m:g}" for m in (1, 1.5, 2, 3, 4)] + [f"SY{p}" for p in (5, 8, 12, 15, 20)] + [f"SA{m}" for m in (2, 3, 4)] + [f"BE{m}" for m in (2, 3)]
S = requests.Session()
def kl(sym, iv, a_ms, b_ms):
    out, cur = [], a_ms
    while cur < b_ms:
        x = None
        for k in range(6):
            try:
                r = S.get(U, params=dict(symbol=sym, interval=iv, startTime=cur, endTime=b_ms - 1, limit=1000), timeout=20)
                if r.status_code in (418, 429): time.sleep(20 + 10 * k); continue
                x = r.json(); break
            except Exception: time.sleep(2 + k)
        if not isinstance(x, list) or not x: break
        out += x; cur = x[-1][0] + (60_000 if iv == "1m" else 3_600_000)
        if len(x) < 1000: break
    return out
def saatlik(nm):
    x = kl(f"{nm}USDT", "1h", int(pd.Timestamp("2022-04-01", tz="UTC").timestamp() * 1000), int(time.time() * 1000))
    if not x: return nm, None
    d = pd.DataFrame([r[:5] for r in x], columns=["o", "a", "h", "l", "c"]).astype(float); d.index = pd.to_datetime(d.o, unit="ms", utc=True) + pd.Timedelta(hours=1)
    d = d[~d.index.duplicated()]; return nm, ((d.h - d.l) / d.c).rolling(14).mean()
with ThreadPoolExecutor(6) as ex: AT = {k: v for k, v in ex.map(saatlik, sorted(set(V.nm))) if v is not None}
print(f"saatlik: {len(AT)} coin · {time.time() - T0:.0f} sn", flush=True)
def sim(O, Hh, Lo, C, e, chk, Pe, fin, tp, Hm, t0m, sl=None, be=False):
    """Dönüş (net, stop oldu mu). sl: sabit stop seviyesi (None = stop yok) · be: 🎯 yolunun yarısına değince stop Pe·1,001'e çekilir."""
    if tp <= Pe: return -fin - FP, False
    n = min(len(C), Hm); w = np.where(Hh[chk:n] >= tp)[0]; jt = chk + w[0] if len(w) else None
    js = None
    if sl is not None:
        slv = np.full(n, sl)
        if be:
            wb = np.where(Hh[chk:n] >= Pe + 0.5 * (tp - Pe))[0]
            if len(wb): slv[chk + wb[0] + 1:] = max(sl, Pe * 1.001)
        ws = np.where(Lo[chk:n] <= slv[chk:n])[0]; js = chk + ws[0] if len(ws) else None
    if js is not None and (jt is None or js <= jt):                                              # aynı dakikada ikisi → stop (kötümser)
        lv = slv[js]; cik = (O[js] if O[js] < lv else lv) * (1 - SLIP); j, fo, st = js, FP, True
    elif jt is not None: cik, j, fo, st = tp, jt, FL, False
    else: j = n - 1; cik, fo, st = C[n - 1], FP, False
    nf = (t0m + j + 1) // 480 - (t0m + e) // 480
    return cik / Pe - 1 - fin - fo - FON * nf, st
def isle(i):
    r = V.loc[i]; H = int(r.H); Hm = H * 60; t0 = r.t; t0m = int(t0.timestamp() // 60)
    x = kl(f"{r.nm}USDT", "1m", int(t0.timestamp() * 1000), int((t0 + pd.Timedelta(minutes=Hm)).timestamp() * 1000))
    if len(x) < min(Hm, 70) or int(x[0][0]) != int(t0.timestamp() * 1000): return None
    M = np.array([[float(v) for v in z[1:5]] for z in x]); O, Hh, Lo, C = M[:, 0], M[:, 1], M[:, 2], M[:, 3]
    if len(C) < Hm: return None
    k0 = KS[r.sinif]; s = r.s; at = AT.get(r.nm); atr = float(at.get(t0, np.nan)) if at is not None else np.nan
    o = {"i": i}
    for gir in ("D", "B"):
        if gir == "D": e, Pe, fin, chk = 7, O[7], FP, 7
        else:
            if r.fB != 1: continue
            e = int(r.mB); Pe = r.PB; fin = FP if e == 7 else FL; chk = e if e == 7 else e + 1
        tp = r.G * (1 + k0 * s); a = dict(O=O, Hh=Hh, Lo=Lo, C=C, e=e, chk=chk, Pe=Pe, fin=fin, tp=tp, Hm=Hm, t0m=t0m)
        L = {"S0": None}
        for m in (1, 1.5, 2, 3, 4): L[f"SS{m:g}"] = Pe * (1 - m * s)
        for p in (5, 8, 12, 15, 20): L[f"SY{p}"] = Pe * (1 - p / 100)
        for m in (2, 3, 4): L[f"SA{m}"] = Pe * (1 - m * atr * np.sqrt(H / 4)) if np.isfinite(atr) else np.nan
        for ad, sl in L.items():
            if sl is not None and not np.isfinite(sl): continue
            nt, st = sim(sl=sl, **a); o[f"{gir}_{ad}"] = nt
            if gir == "D": o[f"st_{ad}"] = st
        for m in (2, 3):
            nt, st = sim(sl=Pe * (1 - m * s), be=True, **a); o[f"{gir}_BE{m}"] = nt
            if gir == "D": o[f"st_BE{m}"] = st
    return o
T1 = time.time(); R = []
with ThreadPoolExecutor(6) as ex:
    for n_, o in enumerate(ex.map(isle, list(V.index))):
        if o: R.append(o)
        if n_ % 2000 == 0: print(f"{n_}/{len(V)} · {time.time() - T1:.0f} sn", flush=True)
D = pd.DataFrame(R).set_index("i"); D = V[K_].join(D, how="inner")
D.to_csv("stop_veri.csv.gz", index=False, compression="gzip")
open("stop_veri_ozet.md", "w").write(f"# stop_veri.csv.gz — {pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M}\n{len(D):,} / {len(V):,} sinyal · {len(D.columns)} sütun · {time.time() - T0:.0f} sn\n_Yalnız veri (PROTOKOL_stop.md)._\n")
print(f"bitti: {len(D):,} sinyal · {time.time() - T0:.0f} sn")
