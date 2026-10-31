# yon_golge_karsilastir.py — canlı gölge kodu (yon_golge.py --gecmis) ile araştırma referansı aynı mı?
import pandas as pd, numpy as np
A = pd.read_csv("yon_golge_referans.csv", parse_dates=["t"]).set_index("t"); B = pd.read_csv("yon_golge_dogrula.csv", parse_dates=["t"]).set_index("t")
ix = A.index.intersection(B.index); print("ortak saat", len(ix), "/", len(A))
for c in ("imb4", "imb24", "kz", "kd24", "uz", "ud24", "lsz", "dxy5", "posdiv", "negdiv", "vr", "skor"):
    a, b = A.loc[ix, c].astype(float), B.loc[ix, c].astype(float); ok = a.notna() & b.notna()
    print(f"{c:7s} dolu ref {a.notna().mean():.2f} canlı {b.notna().mean():.2f} · korelasyon {np.corrcoef(a[ok], b[ok])[0, 1] if ok.sum() > 2 and a[ok].std() > 0 and b[ok].std() > 0 else float('nan'):.4f} · ort. mutlak fark {np.abs(a[ok] - b[ok]).mean():.3g} · eşit (1e-6) %{100 * (np.abs(a[ok] - b[ok]) < 1e-6).mean():.0f}")
for c in ("sinyal_w4", "sinyal_neg"):
    a, b = A.loc[ix, c], B.loc[ix, c]; print(f"{c}: ref {int((a != 0).sum())} · canlı {int((b != 0).sum())} · aynı saat aynı sinyal {int(((a == b) & (a != 0)).sum())} · uyum %{100 * (a == b).mean():.1f}")
try:
    A = pd.read_csv("yon_golge_referans_gun.csv", parse_dates=["gun"]).set_index("gun"); B = pd.read_csv("yon_golge_dogrula_gun.csv", parse_dates=["gun"]).set_index("gun"); ix = A.index.intersection(B.index)
    print("korku ortak gün", len(ix), "/", len(A))
    for c in ("dvol", "dv3", "dvz"): a, b = A.loc[ix, c], B.loc[ix, c]; ok = a.notna() & b.notna(); print(f"{c:5s} ort. mutlak fark {np.abs(a[ok] - b[ok]).mean():.3g} · eşit %{100 * (np.abs(a[ok] - b[ok]) < 1e-6).mean():.0f}")
except Exception as e: print("korku karşılaştırma hata", e)
