# elitbenzeri.py — PROTOKOL_elitbenzeri.md → elitbenzeri_sonuc.md
import hashlib, itertools, numpy as np, pandas as pd
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
K_ = ["t", "nm", "sinif", "H"]
V = pd.read_csv("veri_seti.csv.gz", usecols=K_ + ["tur", "z", "rz", "fon", "zB", "b_r24", "b_vr", "c_r4", "c_r24", "hod", "dow", "s", "gen24"]).drop_duplicates(K_)
KR = pd.read_csv("karal2_veri.csv.gz", usecols=K_ + ["D_T0", "B_T0"]).drop_duplicates(K_); G = pd.read_csv("garch_rho.csv.gz", usecols=K_ + ["rho"])
X = V.merge(KR, on=K_).merge(G, on=K_, how="left"); X["t"] = pd.to_datetime(X.t, utc=True); X = X[X.D_T0.notna() & (X.t >= pd.Timestamp("2022-06-01", tz="UTC"))]
X["sn"] = X.sinif.str.split(" \\(").str[0]; X = X[~((X.sn == "✅ ana") & X.tur.isin(["🤝", "💵"]))].reset_index(drop=True)
X["yil"] = np.where(X.t.dt.year <= 2024, "A", np.where(X.t.dt.year == 2025, "B", "C")); X["yari"] = X.nm.map(lambda s: int(hashlib.md5(s.encode()).hexdigest(), 16) % 2)
X["s_ust"] = X.groupby(["sn", "yil"]).s.transform(lambda v: v >= v.quantile(2 / 3))
C = {"C1 dip": X.rz <= -2, "C2 🚀": X.rz >= 2, "C3 🔥fon": X.fon >= 2, "C4 fon düşük": X.fon <= -1, "C5 prim z≥2": X.z >= 2, "C6 prim z≥1": X.z >= 1, "C7 prim<0": X.z < 0,
     "C8 ABD BTC alıyor": X.zB >= 1, "C9 ABD BTC satıyor": X.zB < 0, "C10 BTC24≤−2%": X.b_r24 <= -0.02, "C11 BTC24≥+2%": X.b_r24 >= 0.02, "C12 BTC oynak": X.b_vr >= 1.25,
     "C13 BTC sakin": X.b_vr <= 0.8, "C14 coin4s≤−1%": X.c_r4 <= -0.01, "C15 coin24≤−5%": X.c_r24 <= -0.05, "C16 coin24≥+5%": X.c_r24 >= 0.05, "C17 ABD seansı": X.hod.between(12, 16),
     "C18 Asya gecesi": X.hod.between(0, 5), "C19 hafta sonu": X.dow >= 5, "C20 GARCH↑": X.rho >= 1.2, "C21 GARCH↓": X.rho <= 0.8, "C22 coin oynak": X.s_ust, "C23 süre≥24s": X.H >= 24, "C24 gen24≥0,5": X.gen24 >= 0.5}
AD = list(C); M = np.column_stack([C[k].fillna(False).values.astype(bool) for k in AD]); NAMES = [(i,) for i in range(len(AD))] + list(itertools.combinations(range(len(AD)), 2))
ok, net, B = (X.D_T0 > 0).values, X.D_T0.values, X.B_T0.values; sn, yil, yari = X.sn.values, X.yil.values, X.yari.values
HUC = [(0, "A"), (0, "B"), (0, "C"), (1, "A"), (1, "B"), (1, "C")]
def tara(M):
    G_ = []
    for s_ in ("✅ ana", "🔸 yedek", "📋 panelden"):
        ms = sn == s_; hm = {h: ms & (yari == h[0]) & (yil == h[1]) for h in HUC}
        for nm in NAMES:
            c = M[:, nm[0]] if len(nm) == 1 else (M[:, nm[0]] & M[:, nm[1]])
            k = hm[(0, "A")] & c; n = k.sum()
            if n < 40 or ok[k].mean() < 0.73 or net[k].mean() < 0.004: continue
            iyi = True
            for h in HUC[1:]:
                k = hm[h] & c; n = k.sum()
                if n < 20 or ok[k].mean() < 0.70 or net[k].mean() < 0.003: iyi = False; break
            if iyi and np.nanmean(B[ms & c]) > 0: G_.append((s_, nm))
    return G_
GEC = tara(M); rng = np.random.default_rng(21); PL = []
for _ in range(20):
    Mp = M.copy()
    for (s_, y_), ix in X.groupby(["sn", "yil"]).indices.items(): Mp[ix] = M[rng.permutation(ix)]
    PL.append(len(tara(Mp)))
yaz("# 💎 ELİT / 🌪️ seviyesinde yeni sinyal türleri — PROTOKOL_elitbenzeri.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {len(X)} sinyal · 900 aday tür · ölçü D_T0 · hücre: işlem · isabet · net %_\n")
yaz(f"**Geçen tür: {len(GEC)} · plasebo (×20) ort. {np.mean(PL):.1f} · en çok {max(PL)} → {'✅ plasebonun üstünde' if len(GEC) > max(PL) else '❌ tesadüften ayırt edilemiyor'}**\n")
el = (sn == "✅ ana") & (M[:, 0] | M[:, 2] | (X.tur.values == "🔀")); oy = (sn == "✅ ana") & (X.tur.values == "🌐🧪") & M[:, 11]; elsaat = set(X.t[el | oy])
if GEC:
    yaz("| sınıf | koşul | yarı0 22–24 | yarı0 2025 | yarı0 2026 | yarı1 22–24 | yarı1 2025 | yarı1 2026 | haftada (2025–26) | haftada farklı gün | ELİT/🌪️ ile aynı saat |"); yaz("|---|---|" + "---|" * 9)
    hf = (X.t.max() - pd.Timestamp("2025-01-01", tz="UTC")).days / 7
    for s_, nm in GEC:
        c = M[:, nm[0]] if len(nm) == 1 else (M[:, nm[0]] & M[:, nm[1]]); ms = (sn == s_) & c; hc = []
        for h in HUC: k = ms & (yari == h[0]) & (yil == h[1]); hc.append(f"{k.sum()} · %{100 * ok[k].mean():.0f} · {100 * net[k].mean():+.2f}")
        y = X[ms & (X.t >= pd.Timestamp("2025-01-01", tz="UTC")).values]
        yaz(f"| {s_} | {' + '.join(AD[i] for i in nm)} | " + " | ".join(hc) + f" | {len(y) / hf:.1f} | {y.t.dt.floor('D').nunique() / hf:.1f} | %{100 * y.t.isin(elsaat).mean():.0f} |")
open("elitbenzeri_sonuc.md", "w").write("\n".join(out) + "\n")
