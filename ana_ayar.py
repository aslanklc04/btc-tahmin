# ana_ayar.py — PROTOKOL_ana_ayar.md
import numpy as np, pandas as pd
V = pd.read_csv("veri_seti.csv.gz", usecols=["t", "nm", "sinif", "H", "tur", "z"]); V["t"] = pd.to_datetime(V.t, utc=True)
K = pd.read_csv("karal2_veri.csv.gz", usecols=["t", "nm", "sinif", "H", "D_T0", "B_T0"]); K["t"] = pd.to_datetime(K.t, utc=True)
V = V.drop_duplicates(["t", "nm", "sinif", "H"]); K = K.drop_duplicates(["t", "nm", "sinif", "H"])                     # tekrarlı satırlar (aynı sinyal iki kez) ayıklanır
D = V.merge(K, on=["t", "nm", "sinif", "H"], how="inner"); print("eşleşen:", len(D), "/", len(V))
U = lambda s: pd.Timestamp(s, tz="UTC")
DON = {"2022–24": (U("2022-06-01"), U("2025-01-01")), "2025": (U("2025-01-01"), U("2026-01-01")), "2026": (U("2026-01-01"), U("2027-01-01"))}
out = []; yaz = lambda s="": (out.append(s), print(s))
def ol(x, c="D_T0"):
    v = x[c].dropna(); s = x.loc[v.index].groupby("t")[c].mean()
    return dict(n=len(v), i=100 * (v > 0).mean() if len(v) else np.nan, net=100 * v.mean() if len(v) else np.nan, si=100 * (s > 0).mean() if len(s) else np.nan)
f = lambda o: f"{o['n']} · %{o['i']:.1f} · {o['net']:+.2f} · saat %{o['si']:.0f}" if o["n"] else "0"
def tablo(gruplar, c="D_T0"):
    yaz("| grup | " + " | ".join(DON) + " |"); yaz("|---|" + "---|" * len(DON))
    R = {}
    for ad, x in gruplar.items():
        R[ad] = {dn: ol(x[(x.t >= a) & (x.t < z)], c) for dn, (a, z) in DON.items()}
        yaz(f"| {ad} | " + " | ".join(f(o) for o in R[ad].values()) + " |")
    return R
def karar(A, B, mn=30):
    return all(A[d]["n"] >= mn and A[d]["i"] <= B[d]["i"] - 3 and A[d]["net"] < B[d]["net"] for d in DON)
ana = D[D.sinif.str.contains("ana")]
yaz("# ✅ ana sınıf ayarı — PROTOKOL_ana_ayar.md · gerçekçi geçmiş (D = piyasadan giriş)")
yaz("_hücre: işlem · işlem isabeti · işlem başı net % · saat isabeti_\n")
yaz("## Test 1 — coin primi z ≥ 3 (✅ ana · 4 s · 🌐🤝 / 🤝)")
k = ana[(ana.H == 4) & ana.tur.isin(["🌐🤝", "🤝"])]
R = tablo({"A: z ≥ 3": k[k.z >= 3], "B: 0 ≤ z < 3": k[(k.z >= 0) & (k.z < 3)], "  z 2–3": k[(k.z >= 2) & (k.z < 3)], "  z 0–2": k[(k.z >= 0) & (k.z < 2)]})
k1 = karar(R["A: z ≥ 3"], R["B: 0 ≤ z < 3"]); yaz(f"\n**Karar 1: {'✅ z ≥ 3 ✅ anadan 🔸 yedeğe iner' if k1 else '❌ şart sağlanmadı — değişiklik yok'}**")
yaz("\n_Bilgi — limit giriş (B):_"); tablo({"A: z ≥ 3": k[k.z >= 3], "B: 0 ≤ z < 3": k[(k.z >= 0) & (k.z < 3)]}, "B_T0")
yaz("\n## Test 2 — uzun süreli ✅ ana türler")
L = ana[ana.tur.isin(["🌐🧪", "💵", "🧪"]) & (ana.H >= 8)]; S = ana[(ana.H == 4) & ana.tur.isin(["🤝", "🌐🤝", "🔀", "🚀"])]
G = {"L: 🌐🧪 / 💵 / 🧪 (8 s+)": L, "S: 4 s ana": S}
for t in ("🌐🧪", "💵", "🧪"): G[f"  L · {t}"] = L[L.tur == t]
R2 = tablo(G)
k2 = karar(R2["L: 🌐🧪 / 💵 / 🧪 (8 s+)"], R2["S: 4 s ana"]); yaz(f"\n**Karar 2 (grup): {'✅ uzun türler 🔸 yedeğe iner' if k2 else '❌ şart sağlanmadı'}**")
for t in ("🌐🧪", "💵", "🧪"):
    kt = karar(R2[f"  L · {t}"], R2["S: 4 s ana"]); yaz(f"- {t}: {'✅ yedeğe iner' if kt else '❌ değişiklik yok'}" + ("" if all(R2[f'  L · {t}'][d]['n'] >= 30 for d in DON) else " (bir dönemde < 30 işlem)"))
open("ana_ayar_sonuc.md", "w").write("\n".join(out) + "\n")
