# kaynak_yokla.py — 🧑 bitcoin-data.com geri geldi mi; 18.10 sonrası boşluk dolduruldu mu; arada z ≤ −1,5 olayı var mı (yalnız yoklama)
import requests, numpy as np, pandas as pd
r = requests.get("https://bitcoin-data.com/v1/coins-addr-1-BTC", timeout=60, headers={"User-Agent": "btc-tahmin"})
d = pd.DataFrame(r.json()); d.index = pd.to_datetime(d.pop("d"), utc=True).dt.floor("D"); s = pd.to_numeric(d.coinsAddr1btc, errors="coerce").dropna(); s = s[~s.index.duplicated()].sort_index()
f = s.asfreq("D"); print("eksik gün (2026):", list(f[f.isna()]["2026"].index.strftime("%d.%m")))
x = np.log(f).diff(30); z = (x - x.rolling(90, min_periods=30).mean()) / (x.rolling(90, min_periods=30).std() + 1e-12)
print(pd.DataFrame(dict(btc=f, gunluk_degisim=f.diff().round(0), z=z.round(2)))["2026-10-05":].to_string())
