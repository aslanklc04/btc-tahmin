# ustuste.py — PROTOKOL_ustuste.md: aynı coin'de önceki sinyal açıkken gelen sinyal daha mı iyi? → ustuste_sonuc.md
import numpy as np, pandas as pd
out = []; yaz = lambda s="": (out.append(s), print(s, flush=True))
K = ["t", "nm", "sinif", "H"]
v = pd.read_csv("veri_seti.csv.gz", usecols=K + ["tur"]).drop_duplicates(K); k = pd.read_csv("karal2_veri.csv.gz", usecols=K + ["D_T0", "B_T0"]).drop_duplicates(K)
X = v.merge(k, on=K, how="inner"); X["t"] = pd.to_datetime(X.t, utc=True); X = X.sort_values(["t", "nm"]).reset_index(drop=True)
X["son"] = X.t + pd.to_timedelta(X.H, unit="h"); X["ok"] = X.D_T0 > 0
DON = [("A 2022-06→2024", "2022-06-01", "2025-01-01"), ("B 2025", "2025-01-01", "2026-01-01"), ("C 2026", "2026-01-01", "2027-01-01")]
X["don"] = None
for ad, a, b in DON: X.loc[(X.t >= pd.Timestamp(a, tz="UTC")) & (X.t < pd.Timestamp(b, tz="UTC")), "don"] = ad
# aynı coin'de açık önceki sinyaller
for c in ("u_any", "u_uzun", "u_ayni", "u_kisa", "u_coklu", "s1_ok"): X[c] = False
X["acik_n"] = 0
for nm, g in X.groupby("nm"):
    t, s, H, ok = g.t.values, g.son.values, g.H.values, g.ok.values; ix = g.index.values
    for a in range(len(g)):
        m = (t[:a] < t[a]) & (s[:a] > t[a])                                                  # S1 öncesi, süresi dolmamış
        if not m.any(): continue
        Hs = H[:a][m]; i = ix[a]
        X.at[i, "u_any"] = True; X.at[i, "acik_n"] = int(m.sum()); X.at[i, "u_uzun"] = bool((Hs > H[a]).any()); X.at[i, "u_ayni"] = bool((Hs == H[a]).any())
        X.at[i, "u_kisa"] = bool((Hs < H[a]).any()); X.at[i, "u_coklu"] = m.sum() >= 2; X.at[i, "s1_ok"] = bool(ok[:a][m][-1])
S_, E_ = np.sort(X.t.values), np.sort(X.son.values)
X["acik_tum"] = np.searchsorted(S_, X.t.values, "left") - np.searchsorted(E_, X.t.values, "right"); X["acik_baska"] = X.acik_tum - X.acik_n
X["kontrol"] = (~X.u_any) & (X.acik_baska >= 1)
X = X[X.don.notna()]
yaz("# 🧱 Üst üste sinyal — PROTOKOL_ustuste.md")
yaz(f"_sinyal {len(X):,} (tekrarsız) · üst üste (U1) %{100 * X.u_any.mean():.0f} · ölçü: D_T0 (7. dk piyasa giriş, 🎯, vadeli ücret) · hücre: sayı · isabet · işlem başı net %_\n")
def h(x): return f"{len(x)} · %{100 * x.ok.mean():.0f} · {100 * x.D_T0.mean():+.2f}" if len(x) else "—"
TUR = {"U1 herhangi açık": "u_any", "U2 açık olan daha uzun ufuk (ör. 24 açıkken 8)": "u_uzun", "U3 aynı ufuk": "u_ayni", "U4 açık olan daha kısa ufuk": "u_kisa", "U5 ≥ 2 açık": "u_coklu"}
SIN = {"hepsi": None, "✅ ana": "✅", "🔸 yedek": "🔸", "📋 panelden": "📋"}
KAR = []
for sad, sp in SIN.items():
    Y = X if sp is None else X[X.sinif.str.startswith(sp)]
    yaz(f"## S2 sınıfı: {sad}")
    yaz("| | " + " | ".join(a for a, _, _ in DON) + " | karar |"); yaz("|---|---|---|---|---|")
    yaz("| üst üste DEĞİL | " + " | ".join(h(Y[(Y.don == a) & ~Y.u_any]) for a, _, _ in DON) + " | |")
    yaz("| kontrol (aynı coin boş, başka coin'de açık) | " + " | ".join(h(Y[(Y.don == a) & Y.kontrol]) for a, _, _ in DON) + " | |")
    for tad, col in TUR.items():
        hs, ok1, ok2 = [], True, True
        for a, _, _ in DON:
            u, n_, kt = Y[(Y.don == a) & Y[col]], Y[(Y.don == a) & ~Y.u_any], Y[(Y.don == a) & Y.kontrol]
            if len(u) < 30 or not len(n_) or not len(kt): ok1 = ok2 = False; hs.append(h(u) + (" (az)" if len(u) < 30 else "")); continue
            di, dn = 100 * (u.ok.mean() - n_.ok.mean()), 100 * (u.D_T0.mean() - n_.D_T0.mean()); ki, kn = 100 * (u.ok.mean() - kt.ok.mean()), 100 * (u.D_T0.mean() - kt.D_T0.mean())
            hs.append(f"{h(u)} ‖ fark {di:+.0f} puan / {dn:+.2f} (kontrole {ki:+.0f} / {kn:+.2f})")
            if not (di >= 5 and dn >= 0.10 and ki >= 5 and kn >= 0.10): ok1 = False
            if not (u.ok.mean() >= 0.70 and u.D_T0.mean() > 0): ok2 = False
        yaz(f"| {tad} | " + " | ".join(hs) + f" | {'✅ işe yarıyor' if ok1 else ''}{' 🎯 aday' if ok2 else ''} |"); KAR.append((sad, tad, ok1, ok2))
    yaz("")
yaz("## Bilgi — ufuk çiftleri (S1 açık ufku → S2 ufku), tüm sınıflar")
yaz("| S1 → S2 | " + " | ".join(a for a, _, _ in DON) + " |"); yaz("|---|---|---|---|")
P = []
for nm, g in X.groupby("nm"):
    t, s, H = g.t.values, g.son.values, g.H.values
    for a in range(len(g)):
        m = (t[:a] < t[a]) & (s[:a] > t[a])
        if m.any(): P.append((g.index[a], int(H[:a][m][-1]), int(H[a])))
PP = pd.DataFrame(P, columns=["i", "H1", "H2"]).set_index("i").join(X[["don", "ok", "D_T0"]])
for (h1, h2), g in PP.groupby(["H1", "H2"]):
    if len(g) < 40: continue
    yaz(f"| {h1} s → {h2} s | " + " | ".join(h(g[g.don == a]) for a, _, _ in DON) + " |")
yaz("\n## Bilgi — önceki sinyal (S1) sonunda tuttu mu? (S2 anında bilinmez; yalnız bağlantıyı gösterir)")
for a, _, _ in DON:
    u = X[(X.don == a) & X.u_any]; yaz(f"- {a}: S1 tuttuysa S2 {h(u[u.s1_ok])} · S1 tutmadıysa S2 {h(u[~u.s1_ok])}")
yaz("\n## Bilgi — aynı anda kaç açık sinyal (aynı coin) → S2")
for nmax in (0, 1, 2, 3):
    sel = X.acik_n == nmax if nmax < 3 else X.acik_n >= 3
    yaz(f"- açık {nmax}{'+' if nmax == 3 else ''}: " + " · ".join(f"{a}: {h(X[(X.don == a) & sel])}" for a, _, _ in DON))
yaz("\n## Karar")
for sad, tad, ok1, ok2 in KAR:
    if ok1 or ok2: yaz(f"- {sad} · {tad}: {'✅ işe yarıyor' if ok1 else ''} {'🎯 sinyal adayı' if ok2 else ''}")
if not any(o1 or o2 for _, _, o1, o2 in KAR): yaz("- Şartı geçen tür yok.")
open("ustuste_sonuc.md", "w").write("\n".join(out) + "\n")
