# kor_test_hazirla.py — 02.11.2026: Claude'un kendi yargısıyla "hangi sinyal tutar" kör testi. Bilgi kesimim Haziran 2026 sonu → yalnız 2026-07-01 sonrası sinyaller (sonucu bilemem).
# Sonuç sütunları (D_T0, B_T0, hD…, mfeD, maeD, son, fB…) DOSYAYA YAZILMAZ; değerlendirme ayrı betikte.
import numpy as np, pandas as pd
K_ = ["t", "nm", "sinif", "H"]
V = pd.read_csv("veri_seti.csv.gz").drop_duplicates(K_); V["t"] = pd.to_datetime(V.t, utc=True)
KR = pd.read_csv("karal2_veri.csv.gz", usecols=K_ + ["D_T0"]).drop_duplicates(K_); KR["t"] = pd.to_datetime(KR.t, utc=True)
X = V.merge(KR[K_ + ["D_T0"]].assign(var=1)[K_ + ["var"]], on=K_); X = X[X.t >= pd.Timestamp("2026-07-01", tz="UTC")]
S = X.sample(150, random_state=20261102).reset_index(drop=True); S["id"] = np.arange(1, 151)
k = S.sinif.str.extract(r"\+0,(\d+)σ")[0].astype(float) / 100
out = pd.DataFrame({"id": S.id, "tarih": S.t.dt.strftime("%m-%d %H"), "coin": S.nm, "sinif": S.sinif.str.split(" \\(").str[0], "tur": S.tur, "H": S.H,
                    "hedef%": (100 * k * S.s).round(2), "prim_z": S.z.round(1), "coin24_z": S.rz.round(1), "fon_z": S.fon.round(1), "btc_prim_z": S.zB.round(1),
                    "btc4%": (100 * S.b_r4).round(1), "btc24%": (100 * S.b_r24).round(1), "btc_oyn": S.b_vr.round(2), "coin4%": (100 * S.c_r4).round(1), "coin24%": (100 * S.c_r24).round(1), "gun": S.dow})
out.to_csv("kor_test_soru.csv", index=False); S[K_ + ["id"]].assign(t=S.t.astype(str)).to_csv("kor_test_anahtar.csv", index=False)
print(len(out), "sinyal ·", out.tarih.min(), "→", out.tarih.max())
