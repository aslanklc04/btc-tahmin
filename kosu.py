# kosu.py — PROTOKOL_kosu.md: ELİT/🌪️ alt kümesinde çıkış varyantları (karal2) → kosu_sonuc.md
import os, numpy as np, pandas as pd
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
K_ = ["t", "nm", "sinif", "H"]; VAR = ["T0", "T1_0.25", "T1_0.5", "T1_1.0", "T3", "T13"]
V = pd.read_csv("veri_seti.csv.gz", usecols=K_ + ["tur", "rz", "fon", "b_vr"]).drop_duplicates(K_)
KR = pd.read_csv("karal2_veri.csv.gz", usecols=K_ + [f"{m}_{v}" for m in "DB" for v in VAR]).drop_duplicates(K_)
X = V.merge(KR, on=K_); X["t"] = pd.to_datetime(X.t, utc=True); X = X[X.D_T0.notna() & (X.t >= pd.Timestamp("2022-06-01", tz="UTC"))]
X = X[X.sinif.str.startswith("✅") & ~X.tur.isin(["🤝", "💵"])]
GF = next(p for p in ("canli/durum/genis_liste.txt", "../main-wt/durum/genis_liste.txt") if os.path.exists(p)); GEN = {l.strip()[:-4] for l in open(GF) if l.strip()}
elit = ((X.rz <= -2) & ~X.nm.isin(GEN)) | (X.fon >= 2) | (X.tur == "🔀"); oyn = (X.tur == "🌐🧪") & (X.b_vr >= 1.25)
X = X[elit | oyn].copy(); X["don"] = np.where(X.t.dt.year <= 2024, "A", np.where(X.t.dt.year == 2025, "B", "C")); AD = {"A": "2022-06→24", "B": "2025", "C": "2026"}
st = lambda y: (len(y), (y > 0).mean(), y.mean(), y.min())
yaz("# 🏃 ELİT / 🌪️ çıkış varyantları — PROTOKOL_kosu.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · ELİT ∪ 🌪️ {len(X)} sinyal (ELİT {int(elit[elit | oyn].sum())}, 🌪️ {int(oyn[elit | oyn].sum())}) · 1 dk yol (karal2) · hücre: n · isabet · net % · en kötü %_\n")
for m_ in "DB":
    yaz(f"## {'D (t+7 dk piyasa)' if m_ == 'D' else 'B (mesaj fiyatına limit)'}"); yaz("| varyant | " + " | ".join(AD.values()) + " |"); yaz("|---|---|---|---|")
    for v in VAR:
        c = f"{m_}_{v}"; yaz(f"| {v} | " + " | ".join("{} · %{:.0f} · {:+.2f} · {:.1f}".format(*(lambda s: (s[0], 100 * s[1], 100 * s[2], 100 * s[3]))(st(X[X.don == d][c].dropna()))) for d in "ABC") + " |")
a = X[X.don == "A"]; t0 = st(a.D_T0.dropna()); sec = None
for v in VAR[1:]:
    s = st(a[f"D_{v}"].dropna())
    if s[1] >= t0[1] - 0.01 and s[2] >= t0[2] + 0.001 and (sec is None or s[2] > sec[1]): sec = (v, s[2])
yaz(f"\n**Keşif seçimi:** {sec[0] if sec else 'yok (hiçbir varyant şartı geçmedi)'}")
if sec:
    v = sec[0]; ok = True
    for d in "BC":
        for m_ in "DB":
            y = X[X.don == d]; b0, b1 = st(y[f"{m_}_T0"].dropna()), st(y[f"{m_}_{v}"].dropna()); g = b1[1] >= b0[1] - 0.01 and b1[2] >= b0[2] + 0.001 and b1[3] >= b0[3] - 0.02; ok &= g
            yaz(f"- {AD[d]} {m_}: T0 %{100 * b0[1]:.0f} · {100 * b0[2]:+.2f} → {v} %{100 * b1[1]:.0f} · {100 * b1[2]:+.2f} (en kötü {100 * b0[3]:.1f} → {100 * b1[3]:.1f}) {'✔' if g else '✘'}")
    yaz(f"\n**Sonuç → {'✅ GEÇTİ' if ok else '❌ geçmedi'}**")
open("kosu_sonuc.md", "w").write("\n".join(out) + "\n")
