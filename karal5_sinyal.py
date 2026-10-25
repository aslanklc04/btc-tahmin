# karal5_sinyal.py — PROTOKOL_karal5.md sinyal verisi (parça I / N, saate göre bölünür → saat sepetleri parçada tam)
import sys, time, json, numpy as np, pandas as pd, requests
from concurrent.futures import ThreadPoolExecutor
import karal5_motor as M
I, N = int(sys.argv[1]), int(sys.argv[2]); T0 = time.time(); U = "https://data-api.binance.vision/api/v3/klines"
V = pd.read_csv("veri_seti.csv.gz"); V["t"] = pd.to_datetime(V.t, utc=True)
ts = np.sort(V.t.unique()); V = V[V.t.isin(set(ts[I::N]))].reset_index(drop=True)
KS = {"✅ ana (+0,75σ)": 0.75, "🔸 yedek (+0,50σ)": 0.5, "📋 panelden (+0,45σ)": 0.45}; RK = {k: M.kurallar(v) for k, v in KS.items()}
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
def isle(i):
    r = V.loc[i]; H = int(r.H); Hb = H * 60; t0 = r.t; t0m = int(t0.timestamp() // 60)
    x = kl(f"{r.nm}USDT", int(t0.timestamp() * 1000), int((t0 + pd.Timedelta(minutes=2 * Hb + 70)).timestamp() * 1000))
    if len(x) < Hb or int(x[0][0]) != int(t0.timestamp() * 1000): return i, None
    A = np.array([[float(v) for v in z[1:5]] for z in x]); O, Hh, Lo, C = A[:, 0], A[:, 1], A[:, 2], A[:, 3]; G = r.G
    if O[7] <= G: e, chk, Pe, fin = 7, 7, O[7], M.FP
    else:
        w = np.where(Lo[8:67] <= G)[0]
        if not len(w): return i, np.full(len(RK[r.sinif]), np.nan)
        e = 8 + int(w[0]); chk, Pe, fin = e + 1, G, M.FL
    return i, M.motor(Hh, Lo, C, e, chk, Pe, fin, G, r.s, Hb, t0m, 1, RK[r.sinif]).astype("float32")
OUT = {}
with ThreadPoolExecutor(6) as ex:
    for n_, (i, v) in enumerate(ex.map(isle, list(V.index))):
        if v is not None: OUT[i] = v
        if n_ % 1000 == 0: print(f"{n_}/{len(V)} · {time.time() - T0:.0f} sn", flush=True)
ix = sorted(OUT); X = np.stack([OUT[i] for i in ix]) if ix else np.zeros((0, len(RK["✅ ana (+0,75σ)"])), "float32")
V.loc[ix, ["t", "nm", "sinif", "H"]].to_csv(f"karal5s_meta_p{I}.csv.gz", index=False, compression="gzip"); np.save(f"karal5s_X_p{I}.npy", X)
json.dump([a for a, _ in RK["✅ ana (+0,75σ)"]], open("karal5_adlar.json", "w"), ensure_ascii=False); print("bitti", X.shape, f"{time.time() - T0:.0f} sn")
