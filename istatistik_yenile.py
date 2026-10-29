# istatistik_yenile.py — 29.10.2026: mesajlardaki gerçekçi istatistikler, veri_seti / karal2_veri TEKRARSIZ yeniden (eski yöntem: yalnız veri_seti tekrarsızdı)
import pandas as pd, numpy as np, json
V = pd.read_csv("veri_seti.csv.gz", usecols=["t", "nm", "sinif", "H", "tur", "rz", "fon", "z"]); D = pd.read_csv("karal2_veri.csv.gz", usecols=["t", "nm", "sinif", "H", "B_T0", "D_T0"])
for x in (V, D): x["t"] = pd.to_datetime(x.t, utc=True)
k = ["t", "nm", "sinif", "H"]
ESKI = D.merge(V.drop_duplicates(k), on=k); YENI = D.drop_duplicates(k).merge(V.drop_duplicates(k), on=k)
P = [("2022–24", "2022-06-01", "2025-01-01"), ("2025+", "2025-01-01", "2030"), ("2026", "2026-01-01", "2030")]
def grup(M):
    a = M[M.sinif.str.startswith("✅")]; y = M[M.sinif.str.startswith("🔸")]; p = M[M.sinif.str.startswith("📋")]
    G = {"ana": a, "ana 🌐🧪": a[a.tur == "🌐🧪"], "ana 🌐🤝": a[a.tur == "🌐🤝"], "ana 🤝": a[a.tur == "🤝"], "ana 🔀": a[a.tur == "🔀"],
         "🚀 (ana rz≥2)": a[a.rz >= 2], "₿🚀 (ana BTC rz≥2)": a[(a.nm == "BTC") & (a.rz >= 2)], "₿🚀b (ana BTC tur 🚀)": a[(a.nm == "BTC") & (a.tur == "🚀")],
         "📉🔥 (ana rz≤−2)": a[a.rz <= -2], "🔥 ana (fon≥2)": a[a.fon >= 2],
         "💎 ELİT": a[(a.rz <= -2) | (a.fon >= 2) | (a.tur == "🔀")], "ELİT dışı": a[~((a.rz <= -2) | (a.fon >= 2) | (a.tur == "🔀"))],
         "yedek": y, "panelden": p, "panelden 💵": p[p.tur == "💵"], "panelden 🧪": p[p.tur == "🧪"], "panelden 🔇/🪙": p[p.tur == "🔇/🪙"]}
    return G
def ol(x, c="B_T0"):
    r = []
    for _, s, e in P:
        d = x[(x.t >= s) & (x.t < e)][["t", c]].dropna()
        sp = d.groupby("t")[c].mean()
        r.append((len(d), 100 * (d[c] > 0).mean(), 100 * d[c].mean(), 100 * (sp > 0).mean()))
    return r
GE, GY = grup(ESKI), grup(YENI); OUT = {}
print(f"satır: eski {len(ESKI)} · tekrarsız {len(YENI)}")
for ad in GE:
    e, y = ol(GE[ad]), ol(GY[ad]); OUT[ad] = y
    f = lambda r: " · ".join(f"%{i:.0f}" for _, i, _, _ in r) + " | " + " · ".join(f"{n:+.2f}" for _, _, n, _ in r) + " | saat " + " · ".join(f"%{s:.0f}" for _, _, _, s in r) + " | n " + "/".join(str(n) for n, _, _, _ in r)
    print(f"{ad:22s} ESKİ {f(e)}\n{'':22s} YENİ {f(y)}")
json.dump({k: [[int(n), round(i, 1), round(m, 3), round(s, 1)] for n, i, m, s in v] for k, v in OUT.items()}, open("istatistik_yenile.json", "w"), ensure_ascii=False, indent=0)
