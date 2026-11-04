# ld_tani.py — canlı 💧 z'si neden çok coin'de ≤ −2? (tanı; canlıya dokunmaz). Girdi: ana dalın önbelleğindeki durum/derinlik_saat.pkl
import numpy as np, pandas as pd
D = pd.read_pickle("durum/derinlik_saat.pkl").sort_index(); C = [l.strip() for l in open("m/durum/likidite_coinler.txt") if l.strip() and not l.startswith("#")]
print("satır", len(D), "·", D.index.min(), "→", D.index.max(), "· sütun", D.shape[1])
dolu = D[C].notna().mean(axis=1); g = D.index.to_series().diff().dt.total_seconds().div(3600)
print("saat boşlukları (> 1 s):", [(str(t), int(v)) for t, v in g[g > 1].items()][:20])
print("gün gün dolu oranı:"); print(dolu.groupby(D.index.floor("D")).mean().round(2).to_string())
L = np.log(D[C].where(D[C] > 0)); Z = (L - L.rolling(720, min_periods=168).mean()) / (L.rolling(720, min_periods=168).std() + 1e-12)
print("z ≤ −2 oranı gün gün:"); print((Z <= -2).sum(axis=1).div(Z.notna().sum(axis=1)).groupby(D.index.floor("D")).mean().round(3).to_string())
# seviye: her dönemin medyan log derinliği (coin'lerin medyanı), ilk döneme göre
don = pd.cut(D.index, [pd.Timestamp("2000-01-01", tz="UTC"), pd.Timestamp("2026-10-12 16:00", tz="UTC"), pd.Timestamp("2026-10-25 12:00", tz="UTC"), pd.Timestamp("2026-11-01", tz="UTC"), pd.Timestamp("2030-01-01", tz="UTC")], labels=["arşiv", "Neon 1dk", "boşluk", "Neon 3dk"])
med = L.groupby(don, observed=True).median(); print("dönem medyanı − arşiv (coin medyanı, log):"); print((med - med.loc["arşiv"]).median(axis=1).round(3).to_string())
print("dönem satır sayısı:", pd.Series(don).value_counts().to_dict())
# rolling 720 SATIR = kaç saat?
print("son 720 satırın kapsadığı saat:", (D.index[-1] - D.index[-720]).total_seconds() / 3600 if len(D) >= 720 else None)
