# hizli.py — PROTOKOL_hizli.md: aynı saatteki sinyallerden en hızlı ve en kârlıyı seçmek → hizli_sonuc.md
import glob, numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
K_ = ["t", "nm", "sinif", "H"]
V = pd.read_csv("veri_seti.csv.gz", usecols=K_ + ["s", "G", "mfeD", "z", "rz", "fon", "zB", "b_r4", "b_r24", "b_vr", "gen24", "c_r4", "c_r24", "hod", "dow"]).drop_duplicates(K_)
KR = pd.read_csv("karal2_veri.csv.gz", usecols=K_ + ["D_T0", "D_T1_1.0"]).drop_duplicates(K_); R = pd.read_csv("garch_rho.csv.gz", usecols=K_ + ["rho"]).drop_duplicates(K_)
X = V.merge(KR, on=K_).merge(R, on=K_, how="left"); X["t"] = pd.to_datetime(X.t, utc=True); X = X[X.D_T0.notna() & (X.t >= pd.Timestamp("2022-06-01", tz="UTC"))].reset_index(drop=True)
X["sn"] = X.sinif.str.split(" \\(").str[0]; X["k0"] = X.sn.map({"✅ ana": 0.75, "🔸 yedek": 0.5, "📋 panelden": 0.45}); X["sni"] = X.sn.map({"✅ ana": 0, "🔸 yedek": 1, "📋 panelden": 2})
A = pd.concat([pd.read_parquet(f, columns=["t", "coin", "h"]) for f in sorted(glob.glob("teknik3_mum_*.parquet"))]); A["t"] = pd.to_datetime(A.t, utc=True)
HH = A.drop_duplicates(["coin", "t"]).pivot(index="t", columns="coin", values="h").sort_index(); del A
hi, ci = HH.index, {c: j for j, c in enumerate(HH.columns)}; Hv = HH.values
F = np.full(len(X), np.nan); pos = hi.searchsorted(X.t)
for r, p in zip(X.itertuples(), pos):
    j = ci.get(r.nm)
    if j is None or p >= len(hi) or hi[p] != r.t: continue
    q = int(np.ceil(r.H / 4)); w = Hv[p + 1:p + 1 + q, j]
    if len(w) == q and np.isfinite(w).all(): F[r.Index] = float(w.max() >= r.G * (1 + r.k0 * r.s))
X["F"] = F; X = X[X.F.notna()].reset_index(drop=True)
X["nh"] = X.groupby("t").t.transform("size"); X = X[X.nh >= 4].reset_index(drop=True)
X["yil"] = X.t.dt.year; X["don"] = np.where(X.yil <= 2024, "2022-06→24", X.yil.astype(str))
FE = ["s", "H", "z", "rz", "fon", "zB", "b_r4", "b_r24", "b_vr", "gen24", "c_r4", "c_r24", "hod", "dow", "rho", "sni", "nh"]
X["m1"], X["m2"] = np.nan, np.nan
for yl in (2024, 2025, 2026):
    tr, te = X[X.yil < yl], X.yil == yl
    X.loc[te, "m1"] = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=31, min_samples_leaf=100, random_state=0).fit(tr[FE], tr.F).predict_proba(X.loc[te, FE])[:, 1]
    X.loc[te, "m2"] = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, max_leaf_nodes=31, min_samples_leaf=100, random_state=0).fit(tr[FE], tr["D_T1_1.0"]).predict(X.loc[te, FE])
SIR = {"S1 en oynak coin": ("s", False), "S2 en sakin coin": ("s", True), "S3 primi en yüksek": ("z", False), "S4 son 4 s en çok düşen": ("c_r4", True), "S5 son 4 s en çok yükselen": ("c_r4", False),
       "S6 24 s en çok düşen (z)": ("rz", True), "S7 GARCH en çok hareket bekleyen": ("rho", False), "S8 son 24 s en çok yükselen": ("c_r24", False),
       "M1 model: hızlı olasılığı": ("m1", False), "M2 model: beklenen kâr": ("m2", False)}
rng = np.random.default_rng(12); oz = lambda d: (d.F.mean(), d.D_T0.mean(), (d.D_T0 > 0).mean(), d.mfeD.mean(), d["D_T1_1.0"].mean())
yaz("# ⚡ En hızlı ve en kârlı sinyali seçmek — PROTOKOL_hizli.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · ≥ 4 sinyalli saatlerdeki {len(X)} sinyal / {X.t.nunique()} saat · saat başına en üst 3 · hücre: hızlı (ilk çeyrekte 🎯) · isabet · net % (D_T0) · en büyük lehte hareket %_\n")
yaz("**Taban (tüm sinyaller):** " + " · ".join(f"{d}: hızlı %{100 * g.F.mean():.0f} · isabet %{100 * (g.D_T0 > 0).mean():.0f} · net {100 * g.D_T0.mean():+.2f} · mfe {100 * g.mfeD.mean():.1f}" for d, g in X.groupby("don")) + "\n")
PL = {}
for d, g in X.groupby("don"):
    r_ = []
    for _ in range(50): r_.append(oz(g.assign(_r=rng.random(len(g))).sort_values("_r").groupby("t").head(3)))
    PL[d] = np.array(r_)
yaz("**Rastgele 3 (×50) ort. / en iyi:** " + " · ".join(f"{d}: hızlı %{100 * PL[d][:, 0].mean():.0f} / %{100 * PL[d][:, 0].max():.0f} · net {100 * PL[d][:, 1].mean():+.2f} / {100 * PL[d][:, 1].max():+.2f} · isabet %{100 * PL[d][:, 2].mean():.0f}" for d in PL) + "\n")
yaz("| sıralayıcı | 2022-06→24 | 2025 | 2026 | hız+kâr | yalnız hız/büyüklük | risk (2025+): en kötü · std · kaybeden ort. · izleyen stoplu net |"); yaz("|---|---|---|---|---|---|---|")
for ad, (col, asc) in SIR.items():
    S = X[X[col].notna()].sort_values(col, ascending=asc, kind="mergesort").groupby("t").head(3); DN = ["2024", "2025", "2026"] if col in ("m1", "m2") else ["2022-06→24", "2025", "2026"]
    if col in ("m1", "m2"): S = S.assign(don=S.yil.astype(str));
    hc, bul, hiz = [], True, True
    for d in DN:
        g = S[S.don == d]; p = PL["2022-06→24"] if d == "2024" else PL[d]
        if d == "2024":
            g24 = X[X.yil == 2024]; p = np.array([oz(g24.assign(_r=rng.random(len(g24))).sort_values("_r").groupby("t").head(3)) for _ in range(50)])
        f_, n_, i_, m_, t_ = oz(g)
        bul &= f_ > p[:, 0].max() and n_ > p[:, 1].max() and i_ >= p[:, 2].mean() - 0.01; hiz &= f_ > p[:, 0].max() and m_ > p[:, 3].max()
        hc.append(f"{d + ': ' if d == '2024' else ''}%{100 * f_:.0f} · %{100 * i_:.0f} · {100 * n_:+.2f} · {100 * m_:.1f}")
    if col in ("m1", "m2"): hc = [hc[0] + " (2024)", hc[1], hc[2]] if False else hc
    g2 = S[S.yil >= 2025]; l = g2.D_T0[g2.D_T0 <= 0]
    yaz(f"| {ad} | " + " | ".join(hc) + f" | {'✅' if bul else '❌'} | {'✔' if hiz else '✘'} | {100 * g2.D_T0.min():.0f}% · {100 * g2.D_T0.std():.1f} · {100 * l.mean():.1f}% · {100 * g2['D_T1_1.0'].mean():+.2f} |")
open("hizli_sonuc.md", "w").write("\n".join(out) + "\n")
