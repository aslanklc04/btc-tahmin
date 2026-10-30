# elit2.py — PROTOKOL_elit2.md
import numpy as np, pandas as pd
k = ["t", "nm", "sinif", "H"]
V = pd.read_csv("veri_seti.csv.gz", usecols=k + ["tur", "rz", "fon", "z", "zB", "b_r24", "c_r4", "gen24", "b_vr"]).drop_duplicates(k)
D = pd.read_csv("karal2_veri.csv.gz", usecols=k + ["B_T0", "D_T0"]).drop_duplicates(k)
for x in (V, D): x["t"] = pd.to_datetime(x.t, utc=True)
M = D.merge(V, on=k)
P = [("2022–24", "2022-06-01", "2025-01-01"), ("2025+", "2025-01-01", "2030"), ("2026", "2026-01-01", "2030")]
out = []; yaz = lambda s="": (out.append(s), print(s))
def ol(x, c="B_T0"):
    r = []
    for _, a, b in P:
        v = x[(x.t >= a) & (x.t < b)][c].dropna(); r.append((len(v), 100 * (v > 0).mean() if len(v) else np.nan, 100 * v.mean() if len(v) else np.nan))
    return r
f = lambda r: " | ".join(f"{n} · %{i:.1f} · {m:+.2f}" for n, i, m in r)
F = {"1 yalnız dip (rz ≤ −2)": lambda m: m.rz <= -2, "2 rz ≤ −2,5": lambda m: m.rz <= -2.5, "3 rz ≤ −3": lambda m: m.rz <= -3, "4 dip ∨ 🔥 (🔀 hariç)": lambda m: (m.rz <= -2) | (m.fon >= 2),
     "5 coin primi z ≥ 0,5": lambda m: m.z >= 0.5, "6 z ≥ 1": lambda m: m.z >= 1, "7 BTC primi zB ≥ 0": lambda m: m.zB >= 0, "8 BTC 24 s ≤ 0": lambda m: m.b_r24 <= 0,
     "9 BTC 24 s > 0": lambda m: m.b_r24 > 0, "10 coin 4 s ≥ 0": lambda m: m.c_r4 >= 0, "11 coin 4 s < 0": lambda m: m.c_r4 < 0, "12 süre 4 s": lambda m: m.H == 4,
     "13 süre ≥ 24 s": lambda m: m.H >= 24, "14 gen24 ≥ 0,5": lambda m: m.gen24 >= 0.5, "15 gen24 < 0,5": lambda m: m.gen24 < 0.5, "16 b_vr ≤ 1": lambda m: m.b_vr <= 1}
ana = M[M.sinif.str.startswith("✅")]; E = ana[(ana.rz <= -2) | (ana.fon >= 2) | (ana.tur == "🔀")]
VP = M[~M.sinif.str.startswith("✅") & ((M.rz <= -2) | (M.fon >= 2))]
TE, TV = ol(E), ol(VP)
yaz("# 💎 ELİT+ — PROTOKOL_elit2.md · B_T0 (limit) · hücre: işlem · isabet · işlem başı net %")
yaz(f"\n**Taban ELİT:** {f(TE)}\n**Taban doğrulama (yedek + panelden, ELİT benzeri):** {f(TV)}\n")
yaz("| filtre | keşif (ELİT) | keşif | doğrulama (yedek+panelden) | doğrulama |"); yaz("|---|---|---|---|---|")
gec = []
for ad, fn in F.items():
    re_, rv = ol(E[fn(E).fillna(False)]), ol(VP[fn(VP).fillna(False)])
    k1 = all(n >= (20 if j == 2 else 40) and i >= TE[j][1] + 3 and m >= TE[j][2] for j, (n, i, m) in enumerate(re_))
    k2 = all(n >= 30 and i >= TV[j][1] + 3 and m >= TV[j][2] for j, (n, i, m) in enumerate(rv))
    if k1 and k2: gec.append((np.mean([m for _, _, m in re_]), ad))
    yaz(f"| {ad} | {f(re_)} | {'✅' if k1 else '❌'} | {f(rv)} | {'✅' if k2 else '❌'} |")
yaz(f"\n**Karar:** {'✅ ' + max(gec)[1] + ' (geçenler: ' + ', '.join(a for _, a in gec) + ')' if gec else '❌ keşif + doğrulamayı birlikte geçen filtre yok'}")
if gec:
    fn = F[max(gec)[1]]; x = E[fn(E).fillna(False)]
    yaz(f"- piyasadan giriş (D): {f(ol(x, 'D_T0'))} · ELİT D: {f(ol(E, 'D_T0'))}")
    w = (x.t.max() - x.t.min()).days / 7; yaz(f"- sıklık: haftada {len(x) / w:.1f} sinyal · {x.t.nunique() / w:.1f} farklı saat (ELİT: {len(E) / w:.1f})")
open("elit2_sonuc.md", "w").write("\n".join(out) + "\n")
