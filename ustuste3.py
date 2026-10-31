# ustuste3.py — PROTOKOL_ustuste.md Ek 2: 📋 panelden + önceki 🎯 vurmuş (Z1) sağlamlık testleri → ustuste3_sonuc.md
import hashlib, numpy as np, pandas as pd
out = []; yaz = lambda s="": (out.append(s), print(s, flush=True))
K = ["t", "nm", "sinif", "H"]
v = pd.read_csv("veri_seti.csv.gz", usecols=K).drop_duplicates(K); k = pd.read_csv("karal2_veri.csv.gz", usecols=K + ["D_T0", "B_T0"]).drop_duplicates(K)
X = v.merge(k, on=K); X["t"] = pd.to_datetime(X.t, utc=True); X["ok"] = X.D_T0 > 0
U = pd.read_csv("ustuste3_veri.csv.gz"); U["t"] = pd.to_datetime(U.t, utc=True); UA, UC = U[U.veri == "arastirma"], U[U.veri == "canli"]
X = X.merge(UA[K + ["s1_zaten", "s1_zaten_kati", "vurus_once_saat", "s1_sinif", "s1_H", "olcek"]], on=K, how="left")
bad = X.olcek.notna() & ((X.olcek < 0.8) | (X.olcek > 1.25)); X.loc[bad, ["s1_zaten", "s1_zaten_kati"]] = np.nan
DON = [("A 2022-06→2024", "2022-06-01", "2025-01-01"), ("B 2025", "2025-01-01", "2026-01-01"), ("C 2026", "2026-01-01", "2027-01-01")]
X["don"] = None
for ad, a, b in DON: X.loc[(X.t >= pd.Timestamp(a, tz="UTC")) & (X.t < pd.Timestamp(b, tz="UTC")), "don"] = ad
X = X[X.don.notna()]; X["ust"] = X.s1_H.notna(); P = X[X.sinif.str.startswith("📋")]
Z1 = P[P.s1_zaten == 1]; NO = P[~P.ust]
def h(x, c="D_T0"): x = x.dropna(subset=[c]); return f"{len(x)} · %{100 * (x[c] > 0).mean():.0f} · {100 * x[c].mean():+.2f}" if len(x) else "—"
def ok3(x, alt=0.70, per=0.65):
    tum = len(x) and (x.ok.mean() >= alt) and (x.D_T0.mean() > 0); dn = all(len(x[x.don == a]) and x[x.don == a].ok.mean() >= per for a, _, _ in DON); return bool(tum and dn)
yaz("# 🧱 Üst üste — Ek 2 sağlamlık testleri: 📋 panelden + önceki sinyal 🎯 vurmuş (Z1)")
yaz(f"_Z1 (📋): " + " · ".join(f"{a} {h(Z1[Z1.don == a])}" for a, _, _ in DON) + " ‖ üst üste olmayan 📋: " + " · ".join(f"{a} {h(NO[NO.don == a])}" for a, _, _ in DON) + " · hücre: sayı · isabet · net %_\n")
SON = {}
yaz("## T1 — coin yarıları (md5 tek/çift)")
P = P.assign(yari=P.nm.map(lambda s: int(hashlib.md5(s.encode()).hexdigest(), 16) % 2)); Z1 = P[P.s1_zaten == 1]
t1 = True
for y in (0, 1):
    z = Z1[Z1.yari == y]; o = ok3(z); t1 &= o
    yaz(f"- yarı {y} ({P[P.yari == y].nm.nunique()} coin): tümü {h(z)} · " + " · ".join(f"{a} {h(z[z.don == a])}" for a, _, _ in DON) + f" → {'✅' if o else '❌'}")
SON["T1"] = t1
yaz("\n## T2 — limit giriş (B_T0, dolmayan = işlem yok)")
t2 = True
for a, _, _ in DON:
    z, n_ = Z1[Z1.don == a].dropna(subset=["B_T0"]), NO[NO.don == a].dropna(subset=["B_T0"]); d = 100 * ((z.B_T0 > 0).mean() - (n_.B_T0 > 0).mean()); t2 &= d >= 3
    yaz(f"- {a}: Z1 {h(z, 'B_T0')} · normal {h(n_, 'B_T0')} · fark {d:+.0f} puan")
SON["T2"] = t2; yaz(f"→ {'✅' if t2 else '❌'}")
yaz("\n## T3 — katı vuruş (S1'in ilk saati sayılmaz)")
ZK = P[P.s1_zaten_kati == 1]; t3 = all(len(ZK[ZK.don == a]) >= 30 and ZK[ZK.don == a].ok.mean() >= 0.70 and ZK[ZK.don == a].D_T0.mean() > 0 for a, _, _ in DON)
yaz("- " + " · ".join(f"{a} {h(ZK[ZK.don == a])}" for a, _, _ in DON) + f" → {'✅' if t3 else '❌'}"); SON["T3"] = t3
yaz("\n## T4 — aylık istikrar (≥ 5 Z1 sinyalli aylar)")
Z1m, NOm = Z1.assign(ay=Z1.t.dt.strftime("%Y-%m")), NO.assign(ay=NO.t.dt.strftime("%Y-%m"))
gz = Z1m.groupby("ay").ok.agg(["mean", "size"]); gn = NOm.groupby("ay").ok.mean(); aylar = gz[gz["size"] >= 5].index
iyi = [(gz.loc[a, "mean"] >= gn.get(a, np.nan)) for a in aylar]; oran = np.mean(iyi) if len(iyi) else np.nan; t4 = bool(oran >= 0.60)
yaz(f"- {len(aylar)} ay · Z1 ≥ normal olan ay oranı %{100 * oran:.0f} → {'✅' if t4 else '❌'}"); SON["T4"] = t4
yaz("\n## T5 — en çok Z1 veren 5 coin çıkarılınca")
top = Z1.nm.value_counts().head(5); z5 = Z1[~Z1.nm.isin(top.index)]; t5 = ok3(z5)
yaz(f"- çıkarılan: {', '.join(f'{c} {n}' for c, n in top.items())} (Z1'in %{100 * top.sum() / len(Z1):.0f}'i) · kalan {h(z5)} · " + " · ".join(f"{a} {h(z5[z5.don == a])}" for a, _, _ in DON) + f" → {'✅' if t5 else '❌'}"); SON["T5"] = t5
yaz("\n## T6 — bilgi")
for c, ad in (("s1_sinif", "önceki sinyalin sınıfı"), ("s1_H", "önceki sinyalin ufku"), ("H", "yeni sinyalin ufku")):
    yaz(f"- {ad}: " + " · ".join(f"{k_} {h(g)}" for k_, g in Z1.groupby(c) if len(g) >= 20))
yaz(f"- vuruş son 4 saatte: {h(Z1[Z1.vurus_once_saat < 4])} · daha önce: {h(Z1[Z1.vurus_once_saat >= 4])}")
XA = X[X.s1_zaten == 1]; yaz("- diğer sınıflarda Z1 (bilgi): " + " · ".join(f"{s} " + " / ".join(h(g[g.don == a]) for a, _, _ in DON) for s, g in XA.groupby(XA.sinif.str[0]) if s != "📋"))
yaz("\n## T7 — canlı (12.10.2026 →, gönderilmiş sinyaller, gerçekçi ölçüm)")
C = pd.read_csv("karne_gercek_main.csv"); C["t"] = pd.to_datetime(C.t0, utc=True); C = C.rename(columns={"coin": "nm"})
C = C.merge(UC[K + ["s1_zaten"]], on=K, how="left"); C["ok"] = C.D_T0 > 0
for s in ("hepsi", "panelden", "yedek", "ana"):
    y_ = C if s == "hepsi" else C[C.sinif == s]
    yaz(f"- {s}: Z1 {h(y_[y_.s1_zaten == 1])} · üst üste ama vurmamış {h(y_[y_.s1_zaten == 0])} · üst üste değil {h(y_[y_.s1_zaten.isna()])}")
gec = SON["T1"] and SON["T3"] and SON["T4"] and SON["T5"]
yaz(f"\n## Karar: {'✅ T1, T3, T4, T5 geçti → mesajlara ♻️ işareti eklenir' if gec else '❌ zorunlu testlerden biri geçmedi → eklenmez'} (" + " · ".join(f"{k_} {'✅' if v_ else '❌'}" for k_, v_ in SON.items()) + ")")
open("ustuste3_sonuc.md", "w").write("\n".join(out) + "\n")
