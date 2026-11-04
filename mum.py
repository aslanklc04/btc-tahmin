# mum.py — PROTOKOL_mum.md: BTC mum örüntüleri (renk · gövde · gölge · seri · diziler) → mum_sonuc.md
import glob, time, numpy as np, pandas as pd
from scipy.stats import norm
T0 = time.time(); out = []
def yaz(s=""): out.append(s); print(s, flush=True)
A = pd.concat([pd.read_parquet(f, columns=["t", "coin", "o", "h", "l", "c"]) for f in sorted(glob.glob("teknik3_mum_*.parquet"))]); A = A[A.coin == "BTC"]
A["t"] = pd.to_datetime(A.t, utc=True); B = A.drop_duplicates("t").set_index("t").sort_index()[["o", "h", "l", "c"]].astype(float)
def topla(B, kural):
    g = B.resample(kural, label="left", closed="left"); return pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min(), "c": g.c.last()}).dropna()
TF = {"1s": (B, 720, (1, 4), 100, 30), "4s": (topla(B, "4h"), 720, (1, 3), 100, 30), "1g": (topla(B, "1D"), 365, (1, 3), 30, 10)}
K1, V1, V2 = pd.Timestamp("2024-07-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC"), None
COST = 0.0012
def kodla(M, W):
    o, h, l, c = M.o, M.h, M.l, M.c
    renk = (c > o).astype(int)                                                                   # 1 yeşil · 0 kırmızı
    def ter(x):
        q1 = x.rolling(W, min_periods=W // 2).quantile(1 / 3).shift(1); q2 = x.rolling(W, min_periods=W // 2).quantile(2 / 3).shift(1)
        return pd.Series(np.where(x <= q1, 0, np.where(x <= q2, 1, 2)), index=x.index).where(q1.notna())
    gv = ter((c - o).abs() / o); ug = ter((h - np.maximum(o, c)) / o); ag = ter((np.minimum(o, c) - l) / o)
    s1 = renk.astype(float); s3 = (renk * 3 + gv); s4 = ((renk * 3 + gv) * 3 + ug) * 3 + ag
    F = {}
    for L in range(1, 7): F[f"F1 renk×{L}"] = sum(s1.shift(k) * 2 ** k for k in range(L))
    run = renk.groupby((renk != renk.shift()).cumsum()).cumcount() + 1; F["F2 seri"] = renk * 100 + run.clip(upper=8)
    for L in range(1, 4): F[f"F3 renk·gövde×{L}"] = sum(s3.shift(k) * 6 ** k for k in range(L))
    for L in range(1, 3): F[f"F4 renk·gövde·gölge×{L}"] = sum(s4.shift(k) * 54 ** k for k in range(L))
    return pd.DataFrame(F)
def coz(aile, kod):
    kod = int(kod)
    if aile.startswith("F1"):
        L = int(aile[-1]); return " ".join("🟩" if (kod >> k) & 1 else "🟥" for k in reversed(range(L)))
    if aile.startswith("F2"): return f"{kod % 100}{'+' if kod % 100 == 8 else ''} {'🟩' if kod >= 100 else '🟥'} üst üste"
    G = ["kısa", "orta", "uzun"]
    if aile.startswith("F3"):
        L = int(aile[-1]); p = [(kod // 6 ** k) % 6 for k in reversed(range(L))]; return " → ".join(f"{'🟩' if x // 3 else '🟥'}{G[x % 3]}" for x in p)
    L = int(aile[-1]); p = [(kod // 54 ** k) % 54 for k in reversed(range(L))]
    return " → ".join(f"{'🟩' if x // 27 else '🟥'} gövde {G[(x // 9) % 3]} · üst {G[(x // 3) % 3]} · alt {G[x % 3]}" for x in p)
HAZ = {}
for tf, (M, W, HS, nmin, nv) in TF.items():
    F = kodla(M, W); R = {h: (M.c.shift(-h) / M.o.shift(-1) - 1) for h in HS}; HAZ[tf] = (M, F, R, HS, nmin, nv)
print(f"[{time.time() - T0:.0f} sn] kodlandı", flush=True)
def tara(kay=None, rng=None):
    rows = []
    for tf, (M, F, R, HS, nmin, nv) in HAZ.items():
        don = np.where(M.index < K1, 0, np.where(M.index < V1, 1, 2))
        for h in HS:
            r = R[h].values
            if kay is not None:
                ok = np.isfinite(r); rr = r[ok]; sh = rng.integers(int(0.1 * len(rr)), int(0.9 * len(rr))); r = r.copy(); r[ok] = np.roll(rr, sh)
            for aile in F.columns:
                f = F[aile].values; m = np.isfinite(f) & np.isfinite(r)
                df = pd.DataFrame({"k": f[m], "r": r[m], "d": don[m]})
                g = df.groupby(["k", "d"]).r.agg(["size", "mean", "std"]).unstack("d")
                for kod, x in g.iterrows():
                    n0, m0, s0 = x[("size", 0)], x[("mean", 0)], x[("std", 0)]
                    if not (n0 >= nmin and s0 > 0): continue
                    t0 = m0 / (s0 / np.sqrt(n0)) / np.sqrt(h); yon = 1 if m0 > 0 else -1
                    rows.append((tf, h, aile, kod, n0, yon * m0 - COST, 2 * (1 - norm.cdf(abs(t0))), yon,
                                 x.get(("size", 1), 0), x.get(("mean", 1), np.nan), x.get(("std", 1), np.nan), x.get(("size", 2), 0), x.get(("mean", 2), np.nan), x.get(("std", 2), np.nan), nv))
    T = pd.DataFrame(rows, columns=["tf", "h", "aile", "kod", "n0", "net0", "p", "yon", "n1", "m1", "s1", "n2", "m2", "s2", "nv"])
    T = T.sort_values("p").reset_index(drop=True); mm = len(T); T["bh"] = T.p <= 0.05 * (np.arange(1, mm + 1)) / mm
    k = np.where(T.bh)[0]; T["sec"] = False
    if len(k): T.loc[:k.max(), "sec"] = True
    T["sec"] &= T.net0 > 0
    T["v1"] = T.yon * T.m1 - COST; T["v2"] = T.yon * T.m2 - COST
    nV = T.n1 + T.n2; mV = (T.n1 * T.m1.fillna(0) + T.n2 * T.m2.fillna(0)) / nV.replace(0, np.nan)
    sV = np.sqrt(((T.n1 - 1).clip(lower=0) * T.s1.fillna(0) ** 2 + (T.n2 - 1).clip(lower=0) * T.s2.fillna(0) ** 2) / (nV - 2).clip(lower=1))
    T["tV"] = T.yon * mV / (sV / np.sqrt(nV)) / np.sqrt(T.h)
    T["gec"] = T.sec & (T.n1 >= T.nv) & (T.n2 >= T.nv) & (T.v1 > 0) & (T.v2 > 0) & (T.tV >= 2)
    return T
T = tara(); print(f"[{time.time() - T0:.0f} sn] gerçek: test {len(T)} · keşif seçimi {T.sec.sum()} · geçen {T.gec.sum()}", flush=True)
rng = np.random.default_rng(55); PL = []
for i in range(20):
    P = tara(True, rng); PL.append((int(P.sec.sum()), int(P.gec.sum()))); print(f"[{time.time() - T0:.0f} sn] plasebo {i}: {PL[-1]}", flush=True)
yaz("# 🕯️ BTC mum örüntüleri — PROTOKOL_mum.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · 1 s / 4 s / 1 g · keşif < 01.07.2024 · V1 2024-07→2025 · V2 2026 · ücret %0,12 · Benjamini–Hochberg q 0,05_\n")
yaz("| zaman dilimi · aile | test | keşifte seçilen | doğrulamayı geçen |"); yaz("|---|---|---|---|")
for (tf, a), g in T.groupby(["tf", "aile"], sort=False): yaz(f"| {tf} · {a} | {len(g)} | {int(g.sec.sum())} | {int(g.gec.sum())} |")
yaz(f"| **toplam** | **{len(T)}** | **{int(T.sec.sum())}** | **{int(T.gec.sum())}** |")
yaz(f"\n**Plasebo (×20, örüntü–getiri bağı koparılmış):** keşif seçimi ort. {np.mean([p[0] for p in PL]):.1f} (en çok {max(p[0] for p in PL)}) · doğrulamayı geçen ort. {np.mean([p[1] for p in PL]):.2f} (en çok {max(p[1] for p in PL)})")
bul = T.gec.sum() >= 1 and T.gec.sum() > max(p[1] for p in PL)
yaz(f"\n**Sonuç → {'✅ BULUNDU' if bul else '❌ bulunamadı'}** (gerçek {int(T.gec.sum())} · plasebo en çok {max(p[1] for p in PL)})\n")
def satir(x):
    M, F, R, HS, *_ = HAZ[x.tf]; f = F[x.aile]; r = R[x.h]; m = (f == x.kod) & r.notna()
    nt = (x.yon * r[m] - COST); idx = nt.index; isb = lambda s: f"%{100 * (s > 0).mean():.0f}"
    v1, v2 = nt[(idx >= K1) & (idx < V1)], nt[idx >= V1]; w = (idx.max() - K1).days / 7
    return (f"| {x.tf} · h {x.h} | {coz(x.aile, x.kod)} | {'long' if x.yon > 0 else 'short'} | {int(x.n0)} · {isb(nt[idx < K1])} · {100 * x.net0:+.3f} | "
            f"{len(v1)} · {isb(v1)} · {100 * x.v1:+.3f} | {len(v2)} · {isb(v2)} · {100 * x.v2:+.3f} | {x.tV:.1f} | {len(nt[idx >= K1]) / w:.1f} |")
G = T[T.gec]
if len(G):
    yaz("## Doğrulamayı geçenler"); yaz("| dilim | örüntü | yön | keşif n · isabet · net % | V1 | V2 | t (V) | haftada |"); yaz("|---|---|---|---|---|---|---|---|"); [yaz(satir(x)) for x in G.itertuples()]
S = T[T.sec & ~T.gec].head(15)
if len(S):
    yaz("\n## Bilgi — keşifte seçilip doğrulamada kalanlar (en güçlü 15)"); yaz("| dilim | örüntü | yön | keşif | V1 | V2 | t (V) | haftada |"); yaz("|---|---|---|---|---|---|---|---|"); [yaz(satir(x)) for x in S.itertuples()]
yaz(f"\n_süre {time.time() - T0:.0f} sn_"); open("mum_sonuc.md", "w").write("\n".join(out) + "\n"); T.to_csv("mum_testler.csv.gz", index=False, compression="gzip")
