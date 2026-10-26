# turev2_test.py — PROTOKOL_turev2.md: kalabalık satıcı (KS) filtresi, 🔸 yedek ve 📋 panelden (bir kez)
import numpy as np, pandas as pd
M = pd.read_csv("turev_veri.csv.gz"); M["t"] = pd.to_datetime(M.t, utc=True)
K = (M.taker <= -1.01).astype(int) + (M.fon <= 0.0211).astype(int) + (M.ls_all <= -0.709).astype(int) + (M.oi24 <= -0.0771).astype(int); M["KS"] = K >= 2
DON = (("2022–24", "2022-06-01", "2025-01-01"), ("2025+", "2025-01-01", "2030-01-01"), ("2026", "2026-01-01", "2030-01-01"))
def o(d, c="B_T0"):
    x = d[["t", c]].dropna(); sp = x.groupby("t")[c].mean() if len(x) else pd.Series(dtype=float)
    return dict(n=len(x), ii=100 * (x[c] > 0).mean() if len(x) else np.nan, net=100 * x[c].mean() if len(x) else np.nan, si=100 * (sp > 0).mean() if len(sp) else np.nan, h=len(sp))
L = ["# Kalabalık satıcı (KS) filtresi — PROTOKOL_turev2.md (bir kez)", "_KS = taker ≤ −1,01 · fon ≤ 0,0211 · ls_all ≤ −0,709 · oi24 ≤ −0,0771 koşullarından ≥ 2'si · ölçü: gerçekçi (limit giriş, 🎯, vadeli ücret)_", ""]
hep = True
for sn, ad in (("🔸", "🔸 yedek"), ("📋", "📋 panelden")):
    d0 = M[M.sinif.str.startswith(sn)]; L.append(f"## {ad} (karar)"); L.append("| Dönem | Taban: n · isabet · net | KS: n · isabet · net · saat ist | şart |"); L.append("|---|---|---|---|")
    for dn, a, b in DON:
        d = d0[(d0.t >= a) & (d0.t < b)]; tb, ks = o(d), o(d[d.KS]); ok = ks["n"] >= 50 and ks["ii"] >= tb["ii"] + 4 and ks["net"] >= tb["net"] + 0.10; hep &= ok
        L.append(f"| {dn} | {tb['n']} · %{tb['ii']:.1f} · {tb['net']:+.3f} | {ks['n']} · %{ks['ii']:.1f} · {ks['net']:+.3f} · %{ks['si']:.1f} | {'✅' if ok else '❌'} |")
L.append(f"\n**SONUÇ: {'✅ BAŞARILI — iki sınıfta, üç dönemde' if hep else '❌ başarısız'}**\n")
L.append("## Bilgi (karar değil)")
a0 = M[M.sinif.str.startswith("✅")]; E = (a0.rz <= -2) | (a0.kfon >= 2) | (a0.tur == "🔀")
for dn, a, b in DON:
    d = a0[(a0.t >= a) & (a0.t < b)]; e = E[d.index]; wk = max((min(pd.Timestamp(b, tz="UTC"), M.t.max()) - pd.Timestamp(a, tz="UTC")).days / 7, 1)
    tb, ks, ksd, kse = o(d), o(d[d.KS]), o(d[d.KS], "D_T0"), o(d[d.KS & e])
    L.append(f"- ✅ ana {dn} (GÖRÜLMÜŞ veri): taban {tb['n']} · %{tb['ii']:.1f} · {tb['net']:+.3f} → KS {ks['n']} · %{ks['ii']:.1f} · {ks['net']:+.3f} · saat %{ks['si']:.1f} · haftada {ks['h'] / wk:.1f} saat · piyasadan %{ksd['ii']:.1f} {ksd['net']:+.3f} · KS∧💎 {kse['n']} · %{kse['ii']:.1f} · {kse['net']:+.3f}")
open("turev2_sonuc.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
