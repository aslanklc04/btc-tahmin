# son_fiyat.py — Telegram sinyallerini değerlendirmek için 04.10.2026'dan bugüne 1 dakikalık spot fiyatlar (Binance, data-api.binance.vision). Yalnız veri çeker.
import time, requests, pandas as pd
SY = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "DOGEUSDT", "DOTUSDT", "SHIBUSDT", "OPUSDT", "LINKUSDT", "NEARUSDT"]
BAS = int(pd.Timestamp("2026-10-03 18:00", tz="UTC").timestamp() * 1000)
SON = int(time.time() * 1000)
out = []
for s in SY:
    t, n = BAS, 0
    while t < SON:
        for i in range(5):
            try:
                r = requests.get("https://data-api.binance.vision/api/v3/klines", params=dict(symbol=s, interval="1m", startTime=t, limit=1000), timeout=20); r.raise_for_status(); k = r.json(); break
            except Exception as e:
                print(s, "hata", e, flush=True); time.sleep(3); k = None
        if not k: break
        out += [(s, x[0], float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[7])) for x in k]; n += len(k)
        t = k[-1][0] + 60000
        if len(k) < 1000: break
    print(s, n, "dakika", flush=True)
D = pd.DataFrame(out, columns=["sym", "t", "o", "h", "l", "c", "qv"])
D.to_csv("son_fiyat.csv.gz", index=False)
print("toplam", len(D), pd.to_datetime(D.t.min(), unit="ms"), "→", pd.to_datetime(D.t.max(), unit="ms"))
