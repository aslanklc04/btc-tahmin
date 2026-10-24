# aralik_analiz.py — PROTOKOL_aralik.md: yürüyen aralıkla R1–R5 kuralları, gerçekçi giriş (B) ve 1 dk yol; keşifte seçim, kontrolde sınama.
import glob, time, numpy as np, pandas as pd, requests
from concurrent.futures import ThreadPoolExecutor
T0 = time.time(); S = requests.Session(); U = "https://data-api.binance.vision/api/v3/klines"
V = pd.read_csv("veri_seti.csv.gz"); V["t"] = pd.to_datetime(V.t, utc=True)
V = V[(V.H == 4) & (V.tur.isin(["🤝", "🌐🤝", "G"]))].copy()
Q = pd.concat([pd.read_csv(f) for f in glob.glob("parca/**/aralik_q_*.csv", recursive=True)]); Q["t"] = pd.to_datetime(Q.t, utc=True)
X = V.merge(Q.drop_duplicates(["t", "nm"]), on=["t", "nm"], how="inner"); X = X[X.fB == 1].reset_index(drop=True)
print(f"aralığı olan, limiti dolan sinyal: {len(X):,} / {len(V):,}", flush=True)
FL, FP, FON = 0.0002, 0.0005, 0.0001
def m1(r):
    a = int(r.t.timestamp() * 1000)
    for k in range(5):
        try:
            x = S.get(U, params=dict(symbol=f"{r.nm}USDT", interval="1m", startTime=a, limit=242), timeout=20)
            if x.status_code in (418, 429): time.sleep(15 + 10 * k); continue
            x = x.json()
            if isinstance(x, list) and len(x) >= 240 and int(x[0][0]) == a: return np.array([[float(v) for v in z[2:5]] for z in x[:240]])
            return None
        except Exception: time.sleep(2 + k)
    return None
with ThreadPoolExecutor(6) as ex: M = list(ex.map(m1, X.itertuples()))
ok = np.array([m is not None for m in M]); X = X[ok].reset_index(drop=True); M = [m for m in M if m is not None]
print(f"1 dk yol: {len(X):,} · {time.time() - T0:.0f} sn", flush=True)
KS = {"✅ ana (+0,75σ)": 0.75, "🔸 yedek (+0,50σ)": 0.5}
def net(i, tp):
    r = X.loc[i]; Hh, C = M[i][:, 0], M[i][:, 2]; e = int(r.mB); Pe = r.PB; fin = FP if e == 7 else FL; chk = e if e == 7 else e + 1
    nf = (int(r.t.timestamp() // 60) + 240) // 480 - (int(r.t.timestamp() // 60) + e) // 480
    if tp is None: return np.nan
    if tp <= Pe: return -fin - FP - FON * nf
    w = np.where(Hh[chk:240] >= tp)[0]
    return (tp / Pe - 1 - fin - FL if len(w) else C[239] / Pe - 1 - fin - FP) - FON * nf
R = {k: [] for k in ("T0", "R1", "R2", "R3", "R4", "R5")}
for i, r in X.iterrows():
    G = r.G; t0 = G * (1 + KS[r.sinif] * r.s); lo, mid, hi = G * np.exp(r.q10 - r.QC), G * np.exp(r.q50), G * np.exp(r.q90 + r.QC)
    R["T0"].append(net(i, t0)); R["R1"].append(net(i, min(t0, hi))); R["R2"].append(net(i, mid) if mid > r.PB * 1.002 else np.nan)
    R["R3"].append(net(i, t0) if mid > G else np.nan); R["R4"].append(net(i, t0) if (hi - G) >= (G - lo) else np.nan); R["R5"].append(net(i, G + 0.5 * (hi - G)))
for k, v in R.items(): X[k] = v
A25, A26, Y2, P0 = (pd.Timestamp(x, tz="UTC") for x in ("2025-01-01", "2026-01-01", "2023-07-01", "2022-06-01")); SON = X.t.max() + pd.Timedelta(hours=1)
def olc(d, c):
    x = d[["t", c]].dropna()
    if len(x) == 0: return dict(n=0, ii=np.nan, si=np.nan, net=np.nan)
    sp = x.groupby("t")[c].mean(); return dict(n=len(x), ii=100 * (x[c] > 0).mean(), si=100 * (sp > 0).mean(), net=100 * x[c].mean())
def sart(o, b): return o["n"] >= 0.4 * b["n"] and o["ii"] >= b["ii"] - 0.5 and o["si"] >= b["si"] - 0.5 and o["net"] >= b["net"] + 0.03
L = [f"# 📐 🎯 + model fiyat aralığı — PROTOKOL_aralik.md · {pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M}",
     f"_{len(X):,} sinyal (aralığı yürüyen testle hesaplanan, limiti dolan) · giriş B · vadeli ücret + fonlama · n · işlem isabeti · saat isabeti · işlem başı net %_\n"]
DON = [("keşif ½-1", P0, Y2), ("keşif ½-2", Y2, A25), ("KONTROL 2025+", A25, SON), ("KONTROL 2026", A26, SON)]
for sn in KS:
    d = X[X.sinif == sn]; L.append(f"## {sn}"); L.append("| Kural | " + " | ".join(a for a, _, _ in DON) + " | keşif |"); L.append("|---|" + "---|" * 5)
    gec = []
    for k in R:
        os_ = [olc(d[(d.t >= a) & (d.t < b)], k) for _, a, b in DON]; bs = [olc(d[(d.t >= a) & (d.t < b)], "T0") for _, a, b in DON]
        kk = k != "T0" and sart(os_[0], bs[0]) and sart(os_[1], bs[1])
        if kk: gec.append((os_[0]["net"] + os_[1]["net"], k))
        L.append(f"| {k} | " + " | ".join(f"{o['n']} · %{o['ii']:.1f} · %{o['si']:.1f} · {o['net']:+.3f}" for o in os_) + f" | {'—' if k == 'T0' else ('✅' if kk else '❌')} |")
    if gec:
        en = max(gec)[1]; os_ = [olc(d[(d.t >= a) & (d.t < b)], en) for _, a, b in DON[2:]]; bs = [olc(d[(d.t >= a) & (d.t < b)], "T0") for _, a, b in DON[2:]]
        L.append(f"\n**Kontrole giden: {en}** → 2025+ {'✅' if sart(os_[0], bs[0]) else '❌'} · 2026 {'✅' if sart(os_[1], bs[1]) else '❌'}\n")
    else: L.append("\n**Kontrole giden yok (keşif şartını geçen kural yok).**\n")
L.append(f"_Süre {time.time() - T0:.0f} sn · 10 deneme (5 kural × 2 sınıf)._")
open("aralik_sonuc.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
