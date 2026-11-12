# h80.py — PROTOKOL_h80.md: %80+ isabet + kâr için alt küme × hedef uzaklığı → h80_sonuc.md
import hashlib, os, numpy as np, pandas as pd
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
K_ = ["t", "nm", "sinif", "H"]; KS = [0.2, 0.3, 0.45, 0.5, 0.6, 0.75, 1.0]; FL, FP, FON = 0.0002, 0.0005, 0.0001
V = pd.read_csv("veri_seti.csv.gz").drop_duplicates(K_); KR = pd.read_csv("karal2_veri.csv.gz", usecols=K_ + ["D_T0", "B_T0"]).drop_duplicates(K_)
X = V.merge(KR, on=K_, how="left"); X["t"] = pd.to_datetime(X.t, utc=True); X = X[X.t >= pd.Timestamp("2022-06-01", tz="UTC")].reset_index(drop=True)
X["sn"] = X.sinif.str.split(" \\(").str[0]; nf = X.H / 8
for k in KS:
    tp = X.G * (1 + k * X.s)
    X[f"D{k}"] = np.where(tp <= X.P, -2 * FP, np.where(X[f"hD{k}"].astype(bool), tp / X.P - 1 - FP - FL, X.son / X.P - 1 - 2 * FP) - FON * nf)
    fin = np.where(X.mB == 7, FP, FL)
    b = np.where(tp <= X.PB, -fin - FP, np.where(X[f"hB{k}"].astype(bool), tp / X.PB - 1 - fin - FL, X.son / X.PB - 1 - fin - FP) - FON * nf)
    X[f"B{k}"] = np.where(X.fB == 1, b, np.nan)
KK = {"✅ ana": 0.75, "🔸 yedek": 0.5, "📋 panelden": 0.45}
chk = []
for sn, k in KK.items():
    m = (X.sn == sn) & X.D_T0.notna(); chk.append((sn, np.corrcoef(X[m][f"D{k}"], X[m].D_T0)[0, 1], (X[m][f"D{k}"] > 0).mean(), (X[m].D_T0 > 0).mean(), X[m][f"D{k}"].mean(), X[m].D_T0.mean()))
GEN = {l.strip()[:-4] for l in open(next(p for p in ("canli/durum/genis_liste.txt", "../main-wt/durum/genis_liste.txt") if os.path.exists(p))) if l.strip()}
X["don"] = np.where(X.t.dt.year <= 2024, "A", np.where(X.t.dt.year == 2025, "B", "C")); X["yari"] = X.nm.map(lambda s: int(hashlib.md5(s.encode()).hexdigest(), 16) % 2)
ana = (X.sn == "✅ ana") & ~X.tur.isin(["🤝", "💵"]); yed = X.sn == "🔸 yedek"
elit = ana & (((X.rz <= -2) & ~X.nm.isin(GEN)) | (X.fon >= 2) | (X.tur == "🔀")); oyn = ana & (X.tur == "🌐🧪") & (X.b_vr >= 1.25)
ALT = {"A1 ✅ ana (🤝/💵 hariç)": ana, "A2 💎 ELİT": elit, "A3 🌪️": oyn, "A4 ELİT ∪ 🌪️": elit | oyn, "A5 ✅ ana 🌐🤝": ana & (X.tur == "🌐🤝"), "A6 ✅ ana 🌐🧪": ana & (X.tur == "🌐🧪"),
       "A7 ✅ ana 🌐": ana & (X.tur == "🌐"), "A8 ✅ ana ∧ BTC oynak": ana & (X.b_vr >= 1.25), "Y1 🔸 yedek": yed, "Y2 yedek ∧ BTC oynak": yed & (X.b_vr >= 1.25), "Y3 yedek ∧ 🔥 fon": yed & (X.fon >= 2),
       "P1 📋 panelden": X.sn == "📋 panelden", "T1 tümü ∧ BTC oynak": X.b_vr >= 1.25}
KT = [0.2, 0.3, 0.45, 0.5, 0.6, 0.75]; AD = {"A": "2022-06→24", "B": "2025", "C": "2026"}
st = lambda v: (len(v), (v > 0).mean() if len(v) else np.nan, v.mean() if len(v) else np.nan)
def degerlendir(mask, M=X):
    """→ (seçilen k | None, geçti mi, ayrıntı)"""
    kes = M[mask & (M.yari == 0) & (M.don == "A")]; best = None
    for k in KT:
        n, i, r = st(kes[f"D{k}"])
        if n >= 40 and i >= 0.80 and r >= 0.0015 and (best is None or r > best[1]): best = (k, r)
    if best is None: return None, False, None
    k = best[0]; ok = True
    for h, d in [(0, "B"), (0, "C"), (1, "A"), (1, "B"), (1, "C")]:
        n, i, r = st(M[mask & (M.yari == h) & (M.don == d)][f"D{k}"]); ok &= n >= 20 and i >= 0.75 and r > 0
    for d in "BC":
        n, i, r = st(M[mask & (M.don == d)][f"D{k}"]); ok &= i >= 0.80 and r >= 0.0015
        n, i, r = st(M[mask & (M.don == d)][f"B{k}"].dropna()); ok &= i >= 0.78 and r > 0
    return k, bool(ok), None
yaz("# 🎯 %80+ isabet ve kâr — alt küme × hedef uzaklığı (PROTOKOL_h80.md)"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {len(X)} sinyal · hücre: n · isabet · işlem başı net % (D: 7. dk piyasadan)_\n")
yaz("**Hesap doğrulaması (sınıfın bugünkü hedefinde karal2 D_T0 ile):** " + " · ".join(f"{sn}: ilişki {c:.3f}, isabet %{100 * a:.1f} ↔ %{100 * b:.1f}, net {100 * e:+.2f} ↔ {100 * f:+.2f}" for sn, c, a, b, e, f in chk))
if min(c[1] for c in chk) < 0.98: yaz("\n**⛔ doğrulama tutmadı → test durduruldu**"); open("h80_sonuc.md", "w").write("\n".join(out) + "\n"); raise SystemExit
f3 = lambda v: "{} · %{:.0f} · {:+.2f}".format(st(v)[0], 100 * st(v)[1], 100 * st(v)[2]) if len(v) else "—"
GEC = []
for ad, m in ALT.items():
    m = m.values; k, ok, _ = degerlendir(m)
    yaz(f"\n## {ad}"); yaz("| k (🎯 = k·σ·√H) | 2022-06→24 | 2025 | 2026 | 2025 limit (B) | 2026 limit (B) |"); yaz("|---|---|---|---|---|---|")
    for kk in KT + [1.0]:
        yaz(f"| {kk}{' ◀ seçilen' if kk == k else ''} | " + " | ".join(f3(X[m & (X.don == d)][f"D{kk}"]) for d in "ABC") + " | " + " | ".join(f3(X[m & (X.don == d)][f"B{kk}"].dropna()) for d in "BC") + " |")
    if k is None: yaz("**Keşif: %80 isabet + ≥ +%0,15 net sağlayan hedef yok → elendi**"); continue
    hc = " · ".join(f"yarı{h} {AD[d]} {f3(X[m & (X.yari == h) & (X.don == d)][f'D{k}'])}" for h, d in [(0, "A"), (0, "B"), (0, "C"), (1, "A"), (1, "B"), (1, "C")])
    yaz(f"**Seçilen k {k} · hücreler: {hc} → {'✅ GEÇTİ' if ok else '❌ doğrulamada kaldı'}**")
    if ok: GEC.append((ad, m, k))
rng = np.random.default_rng(80); PL = []
for _ in range(50):
    Xp = X.copy(); c = 0
    perm = np.arange(len(X))
    for _, ix in X.groupby(["sn", "don"]).indices.items(): perm[ix] = rng.permutation(ix)
    for ad, m in ALT.items():
        k, ok, _ = degerlendir(pd.Series(m.values[perm], index=X.index).values); c += ok
    PL.append(c)
yaz(f"\n## Sonuç\n**Doğrulamayı geçen: {len(GEC)} / {len(ALT)} · plasebo (etiketler karıştırılmış ×50): ort. {np.mean(PL):.2f}, en çok {max(PL)} → {'✅ BULUNDU' if GEC and len(GEC) > max(PL) else '❌ bulunamadı'}**")
hf = (X.t.max() - pd.Timestamp("2025-01-01", tz="UTC")).days / 7
for ad, m, k in GEC:
    yaz(f"\n### Risk tablosu — {ad} · k {k}"); yaz("| dönem | isabet · net | ort. kazanç | ort. kayıp | bir kaybı kaç kazanç siler | en kötü işlem | en kötü %5 ort. | aynı sinyaller bugünkü hedefle |"); yaz("|---|---|---|---|---|---|---|---|")
    k0 = X[m].sn.map(KK).iloc[0]
    for d in "ABC":
        v = X[m & (X.don == d)][f"D{k}"]; w, l = v[v > 0], v[v <= 0]; v0 = X[m & (X.don == d)][f"D{k0}"]
        yaz(f"| {AD[d]} | {f3(v)} | {100 * w.mean():+.2f}% | {100 * l.mean():+.2f}% | {abs(l.mean() / w.mean()):.1f} | {100 * v.min():.1f}% | {100 * v.nsmallest(max(1, len(v) // 20)).mean():.2f}% | k {k0}: {f3(v0)} |")
    y2 = X[m & (X.don != "A")]; yaz(f"_2025+ haftada {len(y2) / hf:.1f} sinyal · farklı gün/hafta {y2.t.dt.floor('D').nunique() / hf:.1f}_")
open("h80_sonuc.md", "w").write("\n".join(out) + "\n")
