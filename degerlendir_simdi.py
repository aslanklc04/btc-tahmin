# degerlendir_simdi.py — kullanıcının paylaştığı canlı sinyallerin gerçek sonucu (yalnız bilgi). Saatler TR (UTC+3).
# Giriş: mesajdaki limit fiyat (60 dk içinde fiyat ≤ giriş ise doldu). Çıkış: çıkış saatinin 5 dk mum açılışı (süre dolmadıysa şimdiki fiyat). Maliyet %0,04.
import requests, pandas as pd
S = [("🧪🌐", "BLUR", "2026-10-13 00:00", 0.01569, "2026-10-14 00:06"), ("💵", "NEAR", "2026-10-13 00:05", 5.356, "2026-10-14 00:06"),
     ("🧪🌐", "VET", "2026-10-13 04:00", 0.007166, "2026-10-14 04:06"), ("🧪🌐", "ZEN", "2026-10-13 04:00", 6.015, "2026-10-14 04:06"),
     ("🧪🌐", "NMR", "2026-10-13 04:00", 12.340, "2026-10-14 04:06"), ("🧪🌐", "LPT", "2026-10-13 04:00", 1.635, "2026-10-14 04:06"),
     ("🧪📉🔥", "SHIB", "2026-10-13 04:00", 0.0000051, "2026-10-14 04:06"), ("💵", "AAVE", "2026-10-13 18:05", 159.120, "2026-10-14 18:06"),
     ("💵", "CRV", "2026-10-14 10:04", 0.3349, "2026-10-14 18:06"), ("🧪🌐", "MAGIC", "2026-10-14 11:00", 0.1133, "2026-10-15 11:06"),
     ("🧪", "SHIB", "2026-10-14 17:00", 0.00000504, "2026-10-15 17:06"), ("💵", "FIL", "2026-10-14 17:05", 1.104, "2026-10-15 01:06")]
now = pd.Timestamp.now(tz="Europe/Istanbul"); out = []
for tur, nm, t, p0, cik in S:
    t0 = pd.Timestamp(t, tz="Europe/Istanbul"); tc = pd.Timestamp(cik, tz="Europe/Istanbul")
    k = requests.get("https://data-api.binance.vision/api/v3/klines", params=dict(symbol=nm + "USDT", interval="5m", startTime=int(t0.timestamp() * 1000), limit=1000), timeout=20).json()
    d = pd.DataFrame([x[:5] for x in k], columns=["t", "o", "h", "l", "c"]).astype(float); d.index = pd.to_datetime(d.t, unit="ms", utc=True).dt.tz_convert("Europe/Istanbul")
    dol = bool((d.l.iloc[:12] <= p0).any()); kap = now >= tc
    p1 = float(d.o[d.index >= tc.floor("5min")].iloc[0]) if kap and (d.index >= tc.floor("5min")).any() else float(d.c.iloc[-1])
    w = d[d.index < tc]; r = 100 * (p1 / p0 - 1) - 0.04
    b = requests.get("https://data-api.binance.vision/api/v3/klines", params=dict(symbol="BTCUSDT", interval="5m", startTime=int(t0.timestamp() * 1000), limit=1000), timeout=20).json()
    bb = pd.DataFrame([x[:5] for x in b], columns=["t", "o", "h", "l", "c"]).astype(float); bb.index = pd.to_datetime(bb.t, unit="ms", utc=True).dt.tz_convert("Europe/Istanbul")
    b1 = float(bb.o[bb.index >= tc.floor("5min")].iloc[0]) if kap and (bb.index >= tc.floor("5min")).any() else float(bb.c.iloc[-1])
    out.append(dict(tur=tur, coin=nm, giris=t[5:], cikis=cik[5:], durum="KAPANDI" if kap else "AÇIK", doldu=dol, net=round(r, 2), en_yuksek=round(100 * (w.h.max() / p0 - 1), 2), en_dusuk=round(100 * (w.l.min() / p0 - 1), 2), btc=round(100 * (b1 / bb.o.iloc[0] - 1), 2)))
X = pd.DataFrame(out); pd.set_option("display.width", 250)
open("degerlendir_simdi.txt", "w").write(f"{now:%d.%m %H:%M} TR\n" + X.to_string(index=False) + "\n"); print(X.to_string(index=False))
