# garch.py — PROTOKOL_garch.md → garch_sonuc.md
import glob, time, warnings, numpy as np, pandas as pd
from arch import arch_model
warnings.filterwarnings("ignore"); T0 = time.time(); out = []
def yaz(s=""): out.append(s); print(s, flush=True)
K_ = ["t", "nm", "sinif", "H"]
V = pd.read_csv("veri_seti.csv.gz", usecols=K_).drop_duplicates(K_); KR = pd.read_csv("karal2_veri.csv.gz", usecols=K_ + ["D_T0", "B_T0"]).drop_duplicates(K_)
X = V.merge(KR, on=K_); X["t"] = pd.to_datetime(X.t, utc=True); X = X[X.D_T0.notna() & (X.t >= pd.Timestamp("2022-06-01", tz="UTC"))].reset_index(drop=True)
A = pd.concat([pd.read_parquet(f, columns=["t", "coin", "c"]) for f in sorted(glob.glob("teknik3_mum_*.parquet"))]); A["t"] = pd.to_datetime(A.t, utc=True)
A = A[A.coin.isin(X.nm.unique())].drop_duplicates(["coin", "t"])
X["rho"] = np.nan; AYLAR = pd.date_range("2022-06-01", "2026-11-01", freq="MS", tz="UTC")
for nm, d in A.groupby("coin"):
    c = d.set_index("t").c.sort_index().astype(float); r = 100 * np.log(c).diff().dropna()
    if len(r) < 4000: continue
    s720 = (r / 100).rolling(720, min_periods=480).std(); sig2 = pd.Series(np.nan, index=r.index); PAR = pd.Series(index=r.index, dtype=object)
    for ay in AYLAR:
        tr = r[r.index < ay].iloc[-3000:]
        if len(tr) < 1500: continue
        try: f = arch_model(tr, mean="Constant", vol="GARCH", p=1, q=1, dist="normal", rescale=False).fit(disp="off")
        except Exception: continue
        mu, om, al, be = f.params["mu"], f.params["omega"], f.params["alpha[1]"], f.params["beta[1]"]
        seg = r[(r.index >= ay - pd.Timedelta(hours=1)) & (r.index < ay + pd.offsets.MonthBegin(1))]
        if not len(seg): continue
        s2 = float(f.conditional_volatility.iloc[-1] ** 2); eps_prev = float(tr.iloc[-1] - mu); vals = []
        for v in seg.values:
            s2 = om + al * eps_prev ** 2 + be * s2; vals.append(s2); eps_prev = v - mu                  # vals[i] = σ² for seg[i] (bilgi: seg[i−1]'e kadar)
        sig2.loc[seg.index] = vals; PAR.loc[seg.index] = [(om, al, be)] * len(seg)
    g = X[X.nm == nm]
    for i, rw in g.iterrows():
        t = rw.t
        if t not in r.index: continue
        k = r.index.get_loc(t)
        if k + 1 >= len(r) or not isinstance(PAR.iloc[k], tuple) or not np.isfinite(sig2.iloc[k]) or not np.isfinite(s720.iloc[k]): continue
        om, al, be = PAR.iloc[k]; mu_eps = r.iloc[k] - r.iloc[max(0, k - 3000):k].mean()
        s1 = om + al * mu_eps ** 2 + be * sig2.iloc[k]                                                 # t'deki getiri dahil → t+1 varyansı
        pers = al + be; Vv = om / (1 - pers) if pers < 1 else s1; H = int(rw.H)
        ex = Vv + pers ** np.arange(H) * (s1 - Vv) if pers < 1 else np.full(H, s1)
        X.at[i, "rho"] = np.sqrt(ex.mean()) / 100 / s720.iloc[k]
    print(f"[{time.time() - T0:.0f} sn] {nm}", flush=True)
X["ok"] = X.D_T0 > 0; X["sn"] = X.sinif.str.split(" \\(").str[0]
X["don"] = np.select([X.t < pd.Timestamp("2025-01-01", tz="UTC"), X.t < pd.Timestamp("2026-01-01", tz="UTC")], ["A", "B"], "C"); DAD = {"A": "2022-06→24", "B": "2025", "C": "2026"}
X.to_csv("garch_rho.csv.gz", index=False, compression="gzip")
def tara(rho):
    R = []
    for sn in ["✅ ana", "🔸 yedek", "📋 panelden"]:
        for ad, f in (("G1 oynaklık artacak (ρ ≥ 1,2)", lambda v: v >= 1.2), ("G2 oynaklık azalacak (ρ ≤ 0,8)", lambda v: v <= 0.8)):
            iyi = kotu = True; hc = []
            for d in "ABC":
                m = (X.sn == sn).values & (X.don == d).values & np.isfinite(rho); on = m & f(np.nan_to_num(rho, nan=1.0)); off = m & ~on
                a, b = X[on], X[off]
                if len(a) < 30 or len(b) < 30: iyi = kotu = False; hc.append("—"); continue
                di, dn = 100 * (a.ok.mean() - b.ok.mean()), 100 * (a.D_T0.mean() - b.D_T0.mean()); dB = (a.B_T0.dropna() > 0).mean() - (b.B_T0.dropna() > 0).mean()
                hc.append(f"{len(a)} · %{100 * a.ok.mean():.0f} · {100 * a.D_T0.mean():+.2f} ({di:+.0f} / {dn:+.2f})")
                iyi &= di >= 5 and dn >= 0.10 and dB > 0; kotu &= di <= -5 and dn <= -0.10 and dB < 0
            R.append((sn, ad, hc, iyi, kotu))
    return R
R = tara(X.rho.values); rng = np.random.default_rng(8); PL = []
for _ in range(50):
    rr = X.rho.values.copy()
    for (sn, d), ix in X.groupby(["sn", "don"]).indices.items(): rr[ix] = rr[rng.permutation(ix)]
    PL.append(sum(r[3] or r[4] for r in tara(rr)))
yaz("# 📈 GARCH oynaklık tahmini ile sinyal ayrımı — PROTOKOL_garch.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · ρ hesaplanan sinyal {int(X.rho.notna().sum())} / {len(X)} · ρ medyan {X.rho.median():.2f} · hücre: sinyal · isabet · net (fark isabet / net, aynı sınıfta koşulsuzlara göre)_\n")
yaz("| sınıf | koşul | " + " | ".join(DAD.values()) + " | sonuç |"); yaz("|---|---|---|---|---|---|")
for sn, ad, hc, iyi, kotu in R: yaz(f"| {sn} | {ad} | " + " | ".join(hc) + f" | {'✅ iyi' if iyi else ('❌ kötü' if kotu else '')} |")
yaz(f"\n**Geçen hücre: {sum(r[3] or r[4] for r in R)} · plasebo ort. {np.mean(PL):.2f} (en çok {max(PL)})**")
open("garch_sonuc.md", "w").write("\n".join(out) + "\n")
