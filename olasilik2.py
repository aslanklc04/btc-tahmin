# olasilik2.py — PROTOKOL_olasilik2.md: P1 Markov "sıcak el" · P2 Thompson haydut · P3 HMM rejim → olasilik2_sonuc.md
import glob, warnings, numpy as np, pandas as pd
from scipy.stats import norm
from hmmlearn.hmm import GaussianHMM
warnings.filterwarnings("ignore"); out = []
def yaz(s=""): out.append(s); print(s, flush=True)
K_ = ["t", "nm", "sinif", "H"]
V = pd.read_csv("veri_seti.csv.gz", usecols=K_ + ["tur"]).drop_duplicates(K_); KR = pd.read_csv("karal2_veri.csv.gz", usecols=K_ + ["D_T0"]).drop_duplicates(K_)
X = V.merge(KR, on=K_); X["t"] = pd.to_datetime(X.t, utc=True); X = X[X.D_T0.notna() & (X.t >= pd.Timestamp("2022-06-01", tz="UTC"))].sort_values("t").reset_index(drop=True)
X["bit"] = X.t + pd.to_timedelta(X.H, unit="h"); X["ok"] = X.D_T0 > 0; X["yil"] = X.t.dt.year; X["kol"] = X.sinif.str.split(" \\(").str[0] + " " + X.tur.fillna("?")
YIL = (2024, 2025, 2026); fs = lambda n, i, r: f"{n} · %{100 * i:.0f} · {100 * r:+.3f}%"
yaz("# 🎲 Olasılık bilimi 2 — Markov · Thompson · HMM (PROTOKOL_olasilik2.md)"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {len(X)} sinyal · ölçü D_T0_\n")
# ---------- P1 Markov / sıcak el (saat sepetleri) ----------
S = X.groupby("t").agg(net=("D_T0", "mean"), bit=("bit", "max")).reset_index(); S["ok"] = S.net > 0; S["yil"] = S.t.dt.year
bt, bo = S.bit.values, S.ok.values; o = np.argsort(bt); bs = bt[o]; onc = np.full(len(S), np.nan)
for i, t in enumerate(S.t.values):
    k = np.searchsorted(bs, t, side="left")
    if k: onc[i] = bo[o[k - 1]]                                                                 # sonucu t'den önce bilinen EN SON sepet
S["onc"] = onc; rng = np.random.default_rng(4)
def p1(S):
    R = {}
    for y in YIL:
        s = S[(S.yil == y) & S.onc.notna()]; a, b = s[s.onc == 1].ok.mean(), s[s.onc == 0].ok.mean(); w = np.where(s.onc == 1, 1.5, 0.5)
        R[y] = (100 * (a - b), (s.net * w).sum() / w.sum() - s.net.mean(), len(s))
    return R
R1 = p1(S); PL = []
for _ in range(200): S2 = S.copy(); S2["onc"] = rng.permutation(S2.onc.values); PL.append(p1(S2))
yaz("## P1 — Markov zinciri / sıcak el (saat sepeti)"); yaz("| yıl | sepet | P(kazan│önceki kazandı) − P(kazan│önceki kaybetti) | ×1,5/×0,5 pay: net farkı | plasebo %95 (fark / net) |"); yaz("|---|---|---|---|---|")
g1 = True
for y in YIL:
    d, n_, k = R1[y]; pd_ = np.quantile([p[y][0] for p in PL], .95); pn = np.quantile([p[y][1] for p in PL], .95)
    yaz(f"| {y} | {k} | {d:+.1f} puan | {100 * n_:+.3f}% | {pd_:+.1f} / {100 * pn:+.3f}% |"); g1 &= d >= 3 and n_ >= 0.0005 and d > pd_ and n_ > pn
yaz(f"**P1 → {'✅ GEÇTİ' if g1 else '❌ geçmedi'}**\n")
# ---------- P2 Thompson / haydut ----------
kol, tv, bv, okv, nv = X.kol.values, X.t.values, X.bit.values, X.ok.values, X.D_T0.values; W = np.full(len(X), np.nan)
for k_ in np.unique(kol):
    ix = np.where(kol == k_)[0]; b_ = bv[ix]; oo = np.argsort(b_); bs_ = b_[oo]
    for i in ix:
        if tv[i] < np.datetime64("2024-01-01"): continue
        hi = np.searchsorted(bs_, tv[i], side="left"); lo = np.searchsorted(bs_, tv[i] - np.timedelta64(180, "D"), side="left"); s_ = ix[oo[lo:hi]]
        if len(s_) < 10: W[i] = 0.5; continue
        m, sd = nv[s_].mean(), nv[s_].std() / np.sqrt(len(s_)); W[i] = norm.cdf(m / (sd + 1e-12))
X["w"] = np.where(W <= 0.2, 0.0, W)
yaz("## P2 — Thompson örneklemesi (kol = sınıf × tür, son 180 gün, yalnız sonucu bilinenler)"); yaz("| yıl | eşit pay | haydut ağırlıklı | fark net | atlanan sinyal |"); yaz("|---|---|---|---|---|")
g2 = True
for y in YIL:
    s = X[(X.yil == y) & X.w.notna()]; eq = (len(s), s.ok.mean(), s.D_T0.mean()); ww = s.w.values
    wn = (s.D_T0 * ww).sum() / ww.sum(); wi = (s.ok * ww).sum() / ww.sum()
    yaz(f"| {y} | {fs(*eq)} | %{100 * wi:.0f} · {100 * wn:+.3f}% | {100 * (wn - eq[2]):+.3f}% | %{100 * (ww == 0).mean():.0f} |"); g2 &= wn >= eq[2] + 0.0005 and wi >= eq[1]
yaz(f"**P2 → {'✅ GEÇTİ' if g2 else '❌ geçmedi'}**\n")
# ---------- P3 HMM rejim ----------
A = pd.concat([pd.read_parquet(f, columns=["t", "coin", "c"]) for f in sorted(glob.glob("teknik3_mum_*.parquet"))]); A = A[A.coin == "BTC"]; A["t"] = pd.to_datetime(A.t, utc=True)
B = A.drop_duplicates("t").set_index("t").c.sort_index().astype(float); g = np.log(B[B.index.hour == 0]).diff().dropna()
def ileri(m, x):
    """İleri algoritma (filtrelenmiş durum olasılıkları; geleceğe bakmaz)."""
    mu, sd = m.means_.ravel(), np.sqrt(m.covars_.ravel()); A_ = m.transmat_; a = m.startprob_.copy(); P = []
    for v in x:
        a = (a @ A_) * norm.pdf(v, mu, sd); a /= a.sum(); P.append(a.copy())
    return np.array(P)
FP = pd.DataFrame(index=g.index, columns=["p_f"], dtype=float)
for ay in pd.date_range("2024-01-01", "2026-10-01", freq="MS", tz="UTC"):
    tr = g[g.index < ay]; m = GaussianHMM(2, covariance_type="diag", n_iter=50, random_state=0).fit(tr.values.reshape(-1, 1))
    f = int(np.argmax(m.covars_.ravel()))                                                        # fırtınalı = yüksek oynaklık
    seg = g[g.index < ay + pd.offsets.MonthBegin(1)]; P = ileri(m, seg.values); idx = seg.index >= ay
    FP.loc[seg.index[idx], "p_f"] = P[idx, f]
X["gun"] = X.t.dt.floor("D"); X["p_f"] = X.gun.map(FP.p_f.shift(1))                              # dünkü kapanışa kadar bilinen olasılık
yaz("## P3 — Gizli Markov modeli (BTC günlük, 2 durum, ileri algoritma)"); yaz("| yıl | sakin (p_f < 0,3) | fırtınalı (p_f ≥ 0,7) | tümü | kural: kötü durumda alma | kalan |"); yaz("|---|---|---|---|---|---|")
g3 = True
for y in YIL:
    s = X[(X.yil == y) & X.p_f.notna()]; sk, fr = s[s.p_f < 0.3], s[s.p_f >= 0.7]
    egit = X[(X.yil < y) & X.p_f.notna()]; kotu_f = (egit[egit.p_f >= 0.7].D_T0.mean() < egit[egit.p_f < 0.3].D_T0.mean()) if len(egit) > 100 else None
    if kotu_f is None: kotu_f = True
    k = s[~(s.p_f >= 0.7)] if kotu_f else s[~(s.p_f < 0.3)]
    yaz(f"| {y} | {fs(len(sk), sk.ok.mean(), sk.D_T0.mean())} | {fs(len(fr), fr.ok.mean(), fr.D_T0.mean())} | {fs(len(s), s.ok.mean(), s.D_T0.mean())} | {'fırtınada' if kotu_f else 'sakinde'} alma → {fs(len(k), k.ok.mean(), k.D_T0.mean())} | %{100 * len(k) / len(s):.0f} |")
    g3 &= k.D_T0.mean() >= s.D_T0.mean() + 0.0005 and k.ok.mean() >= s.ok.mean() and len(k) >= 0.5 * len(s)
yaz(f"**P3 → {'✅ GEÇTİ' if g3 else '❌ geçmedi'}**\n")
yaz(f"## Özet: P1 {'✅' if g1 else '❌'} · P2 {'✅' if g2 else '❌'} · P3 {'✅' if g3 else '❌'}"); open("olasilik2_sonuc.md", "w").write("\n".join(out) + "\n")
