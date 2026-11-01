# bağımsız kontrol + ek sağlamlık (protokol dışı, bilgi): coin yarıları, örtüşme, haftalık sıklık
import hashlib, numpy as np, pandas as pd
k = ["t", "nm", "sinif", "H"]
v = pd.read_csv("veri_seti.csv.gz"); v = v.drop_duplicates(k); r = pd.read_csv("karal2_veri.csv.gz").drop_duplicates(k)
x = pd.merge(v[k + ["tur", "rz", "b_vr", "c_r24"]], r[k + ["D_T0", "B_T0"]], on=k, how="inner"); x = x[x.D_T0.notna()]
x["t"] = pd.to_datetime(x.t, utc=True); x = x[x.t >= "2022-06-01"]; x["y"] = x.t.dt.year.clip(lower=2024).map({2024: "A", 2025: "B", 2026: "C"})
x["yari"] = x.nm.map(lambda s: int(hashlib.md5(s.encode()).hexdigest(), 16) % 2)
H = {"1 ana 🌐🧪 + 📉🔥": (x.sinif.str.startswith("✅")) & (x.tur == "🌐🧪") & (x.rz <= -2), "2 ana 🌐🧪 + BTC oynak": (x.sinif.str.startswith("✅")) & (x.tur == "🌐🧪") & (x.b_vr >= 1.25),
     "3 panelden 💵 + coin 24s ≤ −5%": (x.sinif.str.startswith("📋")) & (x.tur == "💵") & (x.c_r24 <= -0.05)}
f = lambda y: f"{len(y)} · %{100 * (y.D_T0 > 0).mean():.0f} · {100 * y.D_T0.mean():+.2f}" if len(y) else "—"
for ad, m in H.items():
    y = x[m]; print(ad, "|", " | ".join(f"{d}: {f(y[y.y == d])}" for d in "ABC"), "| yarı0:", f(y[y.yari == 0]), "| yarı1:", f(y[y.yari == 1]),
          "| B_T0 limit:", " ".join(f"%{100 * (y[y.y == d].B_T0.dropna() > 0).mean():.0f}" for d in "ABC"),
          f"| haftada ≈ {len(y[y.t >= '2025-01-01']) / ((x.t.max() - pd.Timestamp('2025-01-01', tz='UTC')).days / 7):.1f} (2025+)",
          f"| en kötü işlem {100 * y.D_T0.min():.1f}% · coin sayısı {y.nm.nunique()} · en çok sinyal veren 5 coin payı %{100 * y.nm.value_counts().head(5).sum() / len(y):.0f}")
a = H["1 ana 🌐🧪 + 📉🔥"]; b = H["2 ana 🌐🧪 + BTC oynak"]; print("örtüşme 1∩2:", int((a & b).sum()), "· 2 içinde dip olmayan:", f(x[b & ~a]))
