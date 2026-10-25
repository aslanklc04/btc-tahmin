# karal5_tur.py — kullanıcı onayı (26.10): ✅ ana için "UZ 1.0 +1.0H be" canlıya → mesajdaki 📏 rakamları için tür tür gerçekçi ölçüm (taban ile yan yana)
import glob, json, re, numpy as np, pandas as pd
AD = json.load(open(glob.glob("parca/**/karal5_adlar.json", recursive=True)[0])); MT, XS = [], []
for p in sorted(glob.glob("parca/**/karal5s_meta_p*.csv.gz", recursive=True)):
    k = re.search(r"_p(\d+)\.csv", p).group(1); MT.append(pd.read_csv(p)); XS.append(np.load(glob.glob(f"parca/**/karal5s_X_p{k}.npy", recursive=True)[0]))
D = pd.concat(MT, ignore_index=True); X = np.vstack(XS).astype(float); D["t"] = pd.to_datetime(D.t, utc=True)
V = pd.read_csv("veri_seti.csv.gz", usecols=["t", "nm", "sinif", "H", "tur", "rz"]); V["t"] = pd.to_datetime(V.t, utc=True)
D = D.merge(V.drop_duplicates(["t", "nm", "sinif", "H"]), on=["t", "nm", "sinif", "H"], how="left")
j0, j1 = AD.index("S 0.75"), AD.index("UZ 1.0 +1.0H be"); DON = (("2022–24", "2022-06-01", "2025-01-01"), ("2025+", "2025-01-01", "2027-01-01"), ("2026", "2026-01-01", "2027-01-01"))
L = ["# ✅ ana: taban S 0.75 → UZ 1.0 +1.0H be (tür tür, işlem isabeti · işlem başı net · saat isabeti)", ""]
def o(m, j):
    x = X[m, j]; t = D.t.values[m]; f = ~np.isnan(x)
    if f.sum() == 0: return "—"
    sp = pd.Series(x[f]).groupby(t[f]).mean(); return f"%{100 * (x[f] > 0).mean():.0f} · {100 * x[f].mean():+.2f} · s%{100 * (sp > 0).mean():.0f} (n{f.sum()})"
R = {}
for tur in [None] + sorted(D[D.sinif.str.startswith("✅")].tur.dropna().unique()):
    for ad, a, b in DON:
        m = (D.sinif.str.startswith("✅") & (D.t >= a) & (D.t < b) & ((D.tur == tur) if tur else True)).values
        L.append(f"- {tur or 'TÜMÜ'} {ad}: taban {o(m, j0)} → yeni {o(m, j1)}")
        x = X[m, j1]; f = ~np.isnan(x); R.setdefault(tur or "TÜMÜ", []).append((round(100 * (x[f] > 0).mean()) if f.sum() else None, round(100 * x[f].mean(), 2) if f.sum() else None, int(f.sum())))
for ad_, mm in (("rz ≥ 2 (🚀 işaretli küme)", D.rz >= 2), ("rz ≤ −2 (📉🔥 küme)", D.rz <= -2), ("BTC 🚀", (D.nm == "BTC") & (D.tur == "🚀"))):
    for ad, a, b in DON:
        m = (D.sinif.str.startswith("✅") & (D.t >= a) & (D.t < b) & mm).values; L.append(f"- {ad_} {ad}: taban {o(m, j0)} → yeni {o(m, j1)}")
open("karal5_tur.md", "w").write("\n".join(L) + "\n"); json.dump(R, open("karal5_tur.json", "w"), ensure_ascii=False); print("\n".join(L))
