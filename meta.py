# meta.py — PROTOKOL_meta.md: meta-labeling (hangi sinyal tutar?) aylık yürüyen test 2024-01 → 2026-10 → meta_sonuc.md
import sys, time, numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
T0 = time.time(); out = []
def yaz(s=""): out.append(s); print(s, flush=True)
K_ = ["t", "nm", "sinif", "H"]
V = pd.read_csv("veri_seti.csv.gz").drop_duplicates(K_); KR = pd.read_csv("karal2_veri.csv.gz", usecols=K_ + ["D_T0", "B_T0"]).drop_duplicates(K_)
X = V.merge(KR, on=K_); X["t"] = pd.to_datetime(X.t, utc=True); X = X[X.D_T0.notna() & (X.t >= pd.Timestamp("2022-06-01", tz="UTC"))].sort_values("t").reset_index(drop=True)
X["y"] = (X.D_T0 > 0).astype(int); X["sn"] = X.sinif.str.split(" \\(").str[0]; X["bit"] = X.t + pd.to_timedelta(X.H, unit="h")
X["n_saat"] = X.groupby("t").nm.transform("size")
# coin'in o ana kadar SONUÇLANMIŞ son 20 sinyali (bitiş < t)
ci_isa = np.full(len(X), np.nan); ci_net = np.full(len(X), np.nan)
for nm, g in X.groupby("nm"):
    ix = g.index.values; tt = g.t.values; bb = g.bit.values; yy = g.y.values; nn = g.D_T0.values; o = np.argsort(bb); bs = bb[o]
    for k, i in enumerate(ix):
        m = np.searchsorted(bs, tt[k], side="left")                                              # bitişi t'den önce olanlar
        if m: s = o[:m][-20:]; ci_isa[i] = yy[s].mean(); ci_net[i] = nn[s].mean()
X["coin_isa20"], X["coin_net20"] = ci_isa, ci_net
NUM = ["H", "s", "z", "rz", "fon", "zB", "b_r4", "b_r24", "b_vr", "gen24", "c_r4", "c_r24", "hod", "dow", "n_saat", "coin_isa20", "coin_net20"]
F = pd.concat([X[NUM].astype(float), pd.get_dummies(X[["sn", "tur", "aile"]].fillna("?"), dtype=float)], axis=1).values
AYLAR = pd.date_range("2024-01-01", "2026-10-01", freq="MS", tz="UTC")
def yuru(y):
    P, Q50, Q70, Q33, Q67 = (np.full(len(X), np.nan) for _ in range(5))
    for m in AYLAR:
        tr = (X.t < m - pd.Timedelta(days=8)).values; te = ((X.t >= m) & (X.t < m + pd.offsets.MonthBegin(1))).values
        if not te.any(): continue
        md = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=31, min_samples_leaf=100, random_state=0).fit(F[tr], y[tr])
        ptr = md.predict_proba(F[tr])[:, 1]; P[te] = md.predict_proba(F[te])[:, 1]
        Q50[te], Q70[te], Q33[te], Q67[te] = np.quantile(ptr, [0.5, 0.7, 1 / 3, 2 / 3])
    return P, Q50, Q70, Q33, Q67, md
P, Q50, Q70, Q33, Q67, SON = yuru(X.y.values); X["p"] = P
print(f"[{time.time() - T0:.0f} sn] yürüyen test bitti", flush=True)
YIL = {"2024": (2024,), "2025": (2025,), "2026": (2026,)}; X["yil"] = X.t.dt.year
def ist(y, k="D_T0"):
    v = y[k].dropna(); return (len(v), (v > 0).mean() if len(v) else np.nan, v.mean() if len(v) else np.nan)
fs = lambda s: f"{s[0]} · %{100 * s[1]:.0f} · {100 * s[2]:+.2f}" if s[0] else "—"
yaz("# 🧠 Meta-model — hangi sinyal tutar? (PROTOKOL_meta.md)")
yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {len(X)} sinyal · aylık yürüyen test (eğitim yalnız geçmiş, 8 gün boşluk) · hücre: sinyal · isabet · işlem başı net % (D: piyasadan; B: limit)_\n")
SON_K = {}
def degerlendir(X, P, Q50, Q70, etiket=""):
    R = {}
    for kural, Q in (("Q50 (üst %50)", Q50), ("Q70 (üst %30)", Q70)):
        sec = (P >= Q) & np.isfinite(P); R[kural] = {}
        for yl in (2024, 2025, 2026):
            m = (X.yil.values == yl) & np.isfinite(P); b, f = X[m], X[m & sec]
            R[kural][yl] = dict(b=ist(b), f=ist(f), bB=ist(b, "B_T0"), fB=ist(f, "B_T0"), oran=len(f) / max(len(b), 1))
    return R
R = degerlendir(X, P, Q50, Q70)
rng = np.random.default_rng(2); PL = []
for it in range(10):
    yp = X.y.values.copy(); ay = X.t.dt.strftime("%Y-%m").values
    for a in np.unique(ay): ix = np.where(ay == a)[0]; yp[ix] = yp[rng.permutation(ix)]
    Pp, A, B_, _, _, _ = yuru(yp); PL.append(degerlendir(X, Pp, A, B_)); print(f"plasebo {it} · {time.time() - T0:.0f} sn", flush=True)
for kural in R:
    yaz(f"## {kural}"); yaz("| yıl | taban (D) | meta filtreli (D) | fark isabet / net | kalan | taban (B) | filtreli (B) | plasebo en iyi fark (isabet / net) |"); yaz("|---|---|---|---|---|---|---|---|")
    ok_ = hedef = True
    for yl in (2024, 2025, 2026):
        r = R[kural][yl]; di, dn = 100 * (r["f"][1] - r["b"][1]), 100 * (r["f"][2] - r["b"][2])
        pi = max(100 * (p[kural][yl]["f"][1] - p[kural][yl]["b"][1]) for p in PL); pn = max(100 * (p[kural][yl]["f"][2] - p[kural][yl]["b"][2]) for p in PL)
        dB = r["fB"][2] - r["bB"][2]
        ok_ &= di >= 5 and dn >= 0.10 and r["oran"] >= 0.20 and dB > 0 and di > pi and dn > pn; hedef &= r["f"][1] >= 0.80 and r["f"][2] >= 0.005
        yaz(f"| {yl} | {fs(r['b'])} | {fs(r['f'])} | {di:+.1f} / {dn:+.2f} | %{100 * r['oran']:.0f} | {fs(r['bB'])} | {fs(r['fB'])} | {pi:+.1f} / {pn:+.2f} |")
    SON_K[kural] = (ok_, hedef); yaz(f"**{kural}: {'✅ İŞE YARIYOR' if ok_ else '❌ şartı geçmedi'} · hedef (%80 ve +%0,50): {'✅' if hedef else '✘'}**\n")
# sınıf başına (bilgi, Q70)
yaz("## Sınıf başına (Q70, D)"); yaz("| sınıf | " + " | ".join(f"{y} taban → meta" for y in (2024, 2025, 2026)) + " |"); yaz("|---|---|---|---|")
sec = (P >= Q70) & np.isfinite(P)
for sn in ["✅ ana", "🔸 yedek", "📋 panelden"]:
    c = []
    for yl in (2024, 2025, 2026):
        m = (X.yil.values == yl) & np.isfinite(P) & (X.sn.values == sn); c.append(f"{fs(ist(X[m]))} → {fs(ist(X[m & sec]))}")
    yaz(f"| {sn} | " + " | ".join(c) + " |")
# güvene göre pay (bilgi)
yaz("\n## Güvene göre pay (bilgi): olasılık alt üçte bir 0,5× · orta 1× · üst 1,5×")
w = np.where(P < Q33, 0.5, np.where(P < Q67, 1.0, 1.5))
for yl in (2024, 2025, 2026):
    m = (X.yil.values == yl) & np.isfinite(P); d = X.D_T0.values[m]; ww = w[m]
    yaz(f"- {yl}: eşit pay işlem başı {100 * d.mean():+.2f} (std {100 * d.std():.2f}) → güven paylı {100 * (d * ww).sum() / ww.sum():+.2f} (std {100 * (d * ww / ww.mean()).std():.2f})")
# saat sepeti (bilgi, Q70)
yaz("\n## Saat sepeti isabeti (aynı saatteki sinyaller tek sepet, Q70)")
for yl in (2024, 2025, 2026):
    m = (X.yil.values == yl) & np.isfinite(P); a = X[m].groupby("t").D_T0.mean(); b = X[m & sec].groupby("t").D_T0.mean()
    yaz(f"- {yl}: taban {len(a)} saat · %{100 * (a > 0).mean():.0f} → meta {len(b)} saat · %{100 * (b > 0).mean():.0f}")
yaz(f"\n_süre {time.time() - T0:.0f} sn_"); open("meta_sonuc.md", "w").write("\n".join(out) + "\n")
X[["t", "nm", "sinif", "H", "p"]].assign(q50=Q50, q70=Q70).to_csv("meta_tahmin.csv.gz", index=False, compression="gzip")
