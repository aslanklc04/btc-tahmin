# ustuste2.py — PROTOKOL_ustuste.md Ek 1: önceki sinyal (S1) S2 gelmeden hedefe değdi mi → S2 → ustuste2_sonuc.md
import numpy as np, pandas as pd
out = []; yaz = lambda s="": (out.append(s), print(s, flush=True))
K = ["t", "nm", "sinif", "H"]
v = pd.read_csv("veri_seti.csv.gz", usecols=K + ["c_r24"]).drop_duplicates(K); k = pd.read_csv("karal2_veri.csv.gz", usecols=K + ["D_T0", "B_T0"]).drop_duplicates(K)
X = v.merge(k, on=K); X["t"] = pd.to_datetime(X.t, utc=True); X["ok"] = X.D_T0 > 0
U = pd.read_csv("ustuste2_veri.csv.gz"); U["t"] = pd.to_datetime(U.t, utc=True)
X = X.merge(U[K + ["s1_zaten", "s1_getiri_t2", "s1_H", "olcek"]], on=K, how="left"); X["ust"] = X.s1_H.notna()
X.loc[X.olcek.notna() & ((X.olcek < 0.8) | (X.olcek > 1.25)), "s1_zaten"] = np.nan                      # fiyat ölçeği tutmayan (yeniden adlandırma vb.) çiftler dışarı
DON = [("A 2022-06→2024", "2022-06-01", "2025-01-01"), ("B 2025", "2025-01-01", "2026-01-01"), ("C 2026", "2026-01-01", "2027-01-01")]
X["don"] = None
for ad, a, b in DON: X.loc[(X.t >= pd.Timestamp(a, tz="UTC")) & (X.t < pd.Timestamp(b, tz="UTC")), "don"] = ad
X = X[X.don.notna()]
X["Z"] = np.where(~X.ust, "yok", np.where(X.s1_zaten == 1, "Z1", np.where(X.s1_zaten == 0, np.where(X.s1_getiri_t2 > 0, "Z2", "Z3"), "bilinmiyor")))
def h(x): return f"{len(x)} · %{100 * x.ok.mean():.0f} · {100 * x.D_T0.mean():+.2f}" if len(x) else "—"
yaz("# 🧱 Üst üste sinyal — Ek 1: önceki sinyal zaten tuttu mu? (PROTOKOL_ustuste.md)")
yaz(f"_üst üste S2: {int(X.ust.sum())} · grup: " + ", ".join(f"{k} {v}" for k, v in X.Z.value_counts().items()) + " · hücre: sayı · isabet · işlem başı net % (D_T0)_\n")
KAR = []
for sad, sp in (("hepsi", None), ("✅ ana", "✅"), ("🔸 yedek", "🔸"), ("📋 panelden", "📋")):
    Y = X if sp is None else X[X.sinif.str.startswith(sp)]
    yaz(f"## S2 sınıfı: {sad}"); yaz("| grup | " + " | ".join(a for a, _, _ in DON) + " | karar |"); yaz("|---|---|---|---|---|")
    yaz("| üst üste DEĞİL | " + " | ".join(h(Y[(Y.don == a) & (Y.Z == "yok")]) for a, _, _ in DON) + " | |")
    for z, ad in (("Z1", "Z1 önceki sinyal ZATEN 🎯 vurdu"), ("Z2", "Z2 önceki tutmadı ama kârda"), ("Z3", "Z3 önceki tutmadı ve zararda")):
        hs, ok1, ok2 = [], True, True
        for a, _, _ in DON:
            u = Y[(Y.don == a) & (Y.Z == z)]; n_ = Y[(Y.don == a) & (Y.Z == "yok")]
            med = Y[(Y.don == a) & (Y.Z == "Z1")].c_r24.median(); mk = n_[n_.c_r24 > med] if np.isfinite(med) else n_.iloc[:0]
            if len(u) < 30 or not len(mk): hs.append(h(u) + (" (az)" if len(u) < 30 else "")); ok1 = ok2 = False; continue
            yon = 1 if z != "Z3" else -1
            di, dn = 100 * (u.ok.mean() - n_.ok.mean()), 100 * (u.D_T0.mean() - n_.D_T0.mean()); mi, mn = 100 * (u.ok.mean() - mk.ok.mean()), 100 * (u.D_T0.mean() - mk.D_T0.mean())
            hs.append(f"{h(u)} ‖ fark {di:+.0f} / {dn:+.2f} · momentum kontrolüne {mi:+.0f} / {mn:+.2f} (kontrol {h(mk)})")
            if not (yon * di >= 5 and yon * dn >= 0.10 and yon * mi >= 5 and yon * mn >= 0.10): ok1 = False
            if not ((u.ok.mean() >= 0.70 and u.D_T0.mean() > 0) if z != "Z3" else False): ok2 = False
        yaz(f"| {ad} | " + " | ".join(hs) + f" | {'✅ işe yarıyor' if ok1 else ''}{' 🎯 aday' if ok2 else ''} |"); KAR.append((sad, z, ok1, ok2))
    yaz("")
yaz("## Bilgi — Z1 içinde önceki ve yeni sinyalin ufku")
Z1 = X[X.Z == "Z1"]
for (h1, h2), g in Z1.groupby(["s1_H", "H"]):
    if len(g) >= 40: yaz(f"- {int(h1)} s vurdu → {h2} s: " + " · ".join(f"{a}: {h(g[g.don == a])}" for a, _, _ in DON))
yaz("\n## Karar")
G = [(s, z, a, b) for s, z, a, b in KAR if a or b]
for s, z, a, b in G: yaz(f"- {s} · {z}: {'✅ işe yarıyor' if a else ''} {'🎯 sinyal adayı' if b else ''}")
if not G: yaz("- Şartı geçen grup yok.")
open("ustuste2_sonuc.md", "w").write("\n".join(out) + "\n")
