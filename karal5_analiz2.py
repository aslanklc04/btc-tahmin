# karal5_analiz2.py — PROTOKOL_karal5.md doğrulama: sinyal verisi 2025+ · 2026 (ana) + yeni veri 3 küme → karal5_sonuc.md
import glob, json, pandas as pd
SEC = json.load(open(glob.glob("parca/**/karal5_secim.json", recursive=True)[0])); ADL = [SEC["taban"]] + SEC["secim"]
OA = json.load(open(glob.glob("parca/**/karal5_ana_olcu.json", recursive=True)[0])); AD = json.load(open(glob.glob("parca/**/karal5_adlar.json", recursive=True)[0]))
L = []; yaz = lambda s="": (print(s), L.append(s))
yaz(open(glob.glob("parca/**/karal5_tarama.md", recursive=True)[0]).read())
yaz("# DOĞRULAMA (bir kez) — beş kümenin hepsinde 'iyi'")
if not SEC["secim"]: yaz("**Keşifte iki yarıda da iyi olan kural yok → 🎯 değişmez.**"); open("karal5_sonuc.md", "w").write("\n".join(L) + "\n"); raise SystemExit
Y = pd.concat([pd.read_csv(p) for p in glob.glob("parca/**/karal5y_p*.csv.gz", recursive=True)], ignore_index=True); Y["t"] = pd.to_datetime(Y.t, utc=True); Y = Y[Y.grp != "BTC"]
A25, P0 = pd.Timestamp("2025-01-01", tz="UTC"), pd.Timestamp("2022-06-01", tz="UTC")
KUM = {"yeni A 2025+": Y[(Y.grp == "A") & (Y.t >= A25)], "yeni B 2022–24": Y[(Y.grp == "B") & (Y.t >= P0) & (Y.t < A25)], "yeni B 2025+": Y[(Y.grp == "B") & (Y.t >= A25)]}
def yo(d, j):
    x = d[f"r{j}"].dropna(); return 100 * (x > 0).mean(), 100 * x.mean(), len(x)
bj = AD.index(SEC["taban"]); sonuc = []
yaz("| Kural | sinyal 2025+ (ist · saat ist · sinyal net) | sinyal 2026 | yeni A 2025+ (ist · net) | yeni B 2022–24 | yeni B 2025+ | GEÇTİ |"); yaz("|---|---|---|---|---|---|---|")
for j, ad in enumerate(ADL):
    a = AD.index(ad); h = []; hep = True
    for dn in ("2025+", "2026"):
        o = OA[dn]; ok = ((o["snet"][a] >= o["snet"][bj] + 0.03 and o["ii"][a] >= o["ii"][bj] - 1 and o["si"][a] >= o["si"][bj] - 1) or (o["ii"][a] >= o["ii"][bj] + 3 and o["si"][a] >= o["si"][bj] + 1 and o["snet"][a] >= o["snet"][bj]))
        hep &= ok or j == 0; h.append(f"%{o['ii'][a]:.1f} · %{o['si'][a]:.1f} · {o['snet'][a]:+.3f}" + ("" if j == 0 else (" ✅" if ok else " ❌")))
    for k, d in KUM.items():
        i1, n1, _ = yo(d, j); i0, n0, _ = yo(d, 0); ok = (n1 >= n0 + 0.03 and i1 >= i0 - 1) or (i1 >= i0 + 3 and n1 >= n0)
        hep &= ok or j == 0; h.append(f"%{i1:.1f} · {n1:+.3f}" + ("" if j == 0 else (" ✅" if ok else " ❌")))
    if j: sonuc.append((hep, OA["2025+"]["snet"][a], ad))
    yaz(f"| {ad}{' (taban)' if j == 0 else ''} | " + " | ".join(h) + f" | {'' if j == 0 else ('✅' if hep else '❌')} |")
g = [x for x in sonuc if x[0]]
yaz(f"\n**SONUÇ: {('✅ ' + max(g)[2] + ' — beş kümede de geçti') if g else '❌ hiçbir kural beş kümede de geçmedi → 🎯 değişmez'}**")
open("karal5_sonuc.md", "w").write("\n".join(L) + "\n")
