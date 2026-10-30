# gunluk5.py — PROTOKOL_gunluk5.md: günde ≤ 5, güne dağılmış, en iyi sinyal seçimi (karal5 sinyal verisi, B girişi)
import glob, json, numpy as np, pandas as pd
out = []; yaz = lambda s="": (out.append(s), print(s, flush=True))
M, X = [], []
for f in sorted(glob.glob("parca/**/karal5s_meta_p*.csv.gz", recursive=True)):
    p = f.split("_p")[-1].split(".")[0]; M.append(pd.read_csv(f)); X.append(np.load(glob.glob(f"parca/**/karal5s_X_p{p}.npy", recursive=True)[0]))
AD = json.load(open(glob.glob("parca/**/karal5_adlar.json", recursive=True)[0]))
M = pd.concat(M, ignore_index=True); X = np.concatenate(X); M["t"] = pd.to_datetime(M.t, utc=True)
k = ["t", "nm", "sinif", "H"]; ok = ~M.duplicated(k).values; M, X = M[ok].reset_index(drop=True), X[ok]
V = pd.read_csv("veri_seti.csv.gz", usecols=k + ["tur", "rz", "fon", "z"]).drop_duplicates(k); V["t"] = pd.to_datetime(V.t, utc=True)
M = M.merge(V, on=k, how="left"); assert len(M) == len(X)
ana = M.sinif.str.startswith("✅"); elit = ana & ((M.rz <= -2) | (M.fon >= 2) | (M.tur == "🔀"))
M["kad"] = np.where(elit, 0, np.where(ana, 1, np.where(M.sinif.str.startswith("📋"), 2, 3)))
zz = M.z.fillna(-1.0); M["zp"] = np.where(zz >= 3, -0.5, zz)
M["gun"] = (M.t + pd.Timedelta(hours=3)).dt.date
CIK = {f"🎯 {k_}σ": AD.index(f"S {k_}") for k_ in (0.75, 1.0, 1.25, 1.5, 2.0)} | {"hedefsiz": AD.index("S None")}
HAV = {"H1 tümü": np.ones(len(M), bool), "H2 ✅ ana": ana.values, "H3 💎 ELİT": elit.values}
P = [("2022–24", "2022-06-01", "2025-01-01"), ("2025+", "2025-01-01", "2030"), ("2026", "2026-01-01", "2030")]
yaz("# 📅 Günde ≤ 5, güne dağılmış en iyi sinyal — PROTOKOL_gunluk5.md")
yaz(f"aday sinyal: {len(M):,} · son {M.t.max()} · kural: {len(HAV)} havuz × 3 aralık × {len(CIK)} çıkış")
yaz("_hücre: seçilen/gün · dolum % · işlem isabeti · işlem başı net %_\n")
def sec(mask, G):
    x = M[mask].sort_values(["t", "kad", "zp"], ascending=[True, True, False])
    best = x.groupby("t", sort=True).head(1); keep, son, say = [], None, {}
    for i, t, g in zip(best.index, best.t, best.gun):
        if son is not None and t - son < pd.Timedelta(hours=G): continue
        if say.get(g, 0) >= 5: continue
        keep.append(i); son = t; say[g] = say.get(g, 0) + 1
    return np.array(keep, dtype=int)
gec = []
for hv, mask in HAV.items():
    for G in (2, 3, 4):
        idx = sec(mask, G)
        yaz(f"### {hv} · en az {G} saat aralık")
        yaz("| çıkış | " + " | ".join(p for p, _, _ in P) + " |"); yaz("|---|" + "---|" * len(P))
        for ad, j in CIK.items():
            hs = []; ok = True
            for p, a, b in P:
                ii = idx[(M.t.values[idx] >= np.datetime64(a)) & (M.t.values[idx] < np.datetime64(b))]
                gun = max((min(pd.Timestamp(b, tz="UTC"), M.t.max()) - pd.Timestamp(a, tz="UTC")).days, 1)
                v = X[ii, j]; f = v[np.isfinite(v)]
                if not len(f): hs.append("0"); ok = False; continue
                i_, n_ = 100 * (f > 0).mean(), 100 * f.mean(); gd = len(ii) / gun
                ok = ok and i_ >= 75 and n_ >= 1.5 and gd >= 1
                hs.append(f"{gd:.1f}/gün · %{100 * len(f) / len(ii):.0f} · %{i_:.0f} · {n_:+.2f}")
            if ok: gec.append((hv, G, ad))
            yaz(f"| {ad} | " + " | ".join(hs) + " |")
        yaz()
yaz(f"## Karar: {'✅ geçen: ' + '; '.join(f'{a} · {g} s · {c}' for a, g, c in gec) if gec else '❌ hiçbir kural üç dönemde de %75+ isabet ve +%1,5 kâr (günde ≥ 1 sinyal) sağlamadı'}")
open("gunluk5_sonuc.md", "w").write("\n".join(out) + "\n")
