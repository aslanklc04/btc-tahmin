# vrp.py — PROTOKOL_vrp.md: 1 günlük ATM straddle satışı, oynaklık göstergeleriyle zamanlama → vrp_sonuc.md
import glob, numpy as np, pandas as pd
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
O = pd.read_parquet("btcyon5_opsiyon.parquet", columns=["iv", "endeks", "vade", "kul", "t"]); O["t"] = pd.to_datetime(O.t, utc=True); O["vade"] = pd.to_datetime(O.vade, utc=True)
O = O[(O.t.dt.hour == 7) & (O.iv > 5) & (O.iv < 300) & ((O.kul / O.endeks - 1).abs() <= 0.02)]
O["sv"] = (O.vade - O.t).dt.total_seconds() / 3600; O = O[(O.sv >= 20) & (O.sv <= 52)]
IV = O.groupby(O.t.dt.floor("D")).iv.agg(["median", "size"]); IV = IV[IV["size"] >= 5]["median"]; IV.index = IV.index + pd.Timedelta(hours=8)
A = pd.concat([pd.read_parquet(f, columns=["t", "coin", "c"]) for f in sorted(glob.glob("teknik3_mum_*.parquet"))]); A = A[A.coin == "BTC"]; A["t"] = pd.to_datetime(A.t, utc=True)
C = A.drop_duplicates("t").set_index("t").c.sort_index().astype(float); lr = np.log(C).diff()
s24, s720 = lr.rolling(24).std(), lr.rolling(720, min_periods=480).std()
V = pd.read_csv("veri_seti.csv.gz", usecols=["t", "sinif"]); V["t"] = pd.to_datetime(V.t, utc=True); ANA = V[V.sinif.str.startswith("✅")].t.sort_values().values
D = pd.DataFrame({"iv": IV}); D["S0"] = C.reindex(D.index); D["S1"] = C.reindex(D.index + pd.Timedelta(days=1)).values
D["bvr"] = (s24 / s720).reindex(D.index); D["rv24"] = (s24 * np.sqrt(24 * 365) * 100).reindex(D.index)
D["ana24"] = [((ANA > np.datetime64(t - pd.Timedelta(hours=24))) & (ANA <= np.datetime64(t))).any() for t in D.index.tz_convert(None)]
D = D.dropna(subset=["iv", "S0", "S1", "bvr", "rv24"])
sig = (D.iv - 2).clip(lower=1) / 100; D["pnl"] = 0.7979 * sig * np.sqrt(1 / 365) - (D.S1 / D.S0 - 1).abs() - 0.0008
D["don"] = np.select([D.index.year == 2022, D.index.year <= 2024, D.index.year == 2025], ["2022", "2023–24", "2025"], "2026")
KUR = {"R0 her gün": np.ones(len(D), bool), "R1 BTC sakin (b_vr < 1)": (D.bvr < 1.0).values, "R2 IV ≥ 1,2 × son 24 s": (D.iv / D.rv24 >= 1.2).values,
       "R3 R1 ∧ R2": ((D.bvr < 1.0) & (D.iv / D.rv24 >= 1.2)).values, "R4 son 24 s ✅ ana yok": (~D.ana24).values}
rng = np.random.default_rng(66)
def ozet(y):
    if not len(y): return "—", np.nan, np.nan
    cum = y.cumsum(); dd = (cum - cum.cummax()).min()
    return f"{len(y)} · {100 * y.mean():+.3f}% · kazanma %{100 * (y > 0).mean():.0f} · en kötü {100 * y.min():.1f}% · düşüş {100 * dd:.1f}% · ort/sd {y.mean() / y.std():.2f}", y.mean(), y.min()
yaz("# 🧯 Oynaklık primi satışı + zamanlama — PROTOKOL_vrp.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {len(D)} gün ({D.index.min():%d.%m.%Y} → {D.index.max():%d.%m.%Y}) · 1 günlük ATM straddle satışı (IV − 2 puan, ücret %0,08) · hücre: gün · ort. kâr (S'nin %'si) · kazanma · en kötü gün · birikimli en büyük düşüş · ort/sd_\n")
yaz(f"_IV medyanı %{D.iv.median():.0f} · gerçekleşen (24 s) medyanı %{D.rv24.median():.0f} · IV > gerçekleşen günler %{100 * (D.iv > D.rv24).mean():.0f}_\n")
DON = ["2022", "2023–24", "2025", "2026"]; R0 = {d: ozet(D[D.don == d].pnl) for d in DON}
yaz("| kural | " + " | ".join(DON) + " | sonuç |"); yaz("|---|" + "---|" * len(DON) + "---|")
for ad, m in KUR.items():
    hc, iyi = [], ad != "R0 her gün"
    for d in DON:
        mm = m & (D.don == d).values; y = D.pnl[mm]; s, mu, mn = ozet(y); hc.append(s)
        if ad == "R0 her gün": continue
        pool = D.pnl[(D.don == d).values].values; k = mm.sum()
        rnd = [rng.choice(pool, size=k, replace=False).mean() for _ in range(200)] if 0 < k <= len(pool) else [np.inf]
        iyi &= bool(k) and mu > R0[d][1] and mu > 0 and mn > R0[d][2] and mu > np.quantile(rnd, 0.95)
    yaz(f"| {ad} | " + " | ".join(hc) + f" | {'—' if ad == 'R0 her gün' else ('✅ işe yarar' if iyi else '❌')} |")
open("vrp_sonuc.md", "w").write("\n".join(out) + "\n"); D.to_csv("vrp_gunler.csv")
