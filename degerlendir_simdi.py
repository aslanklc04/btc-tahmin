# degerlendir_simdi.py — kullanıcının paylaştığı 13.10 sinyallerinin anlık durumu (yalnız bilgi). Saatler TR (UTC+3).
import requests, pandas as pd
S = [("BLUR", "2026-10-13 00:00", 0.01569, "2026-10-14 00:06"), ("NEAR", "2026-10-13 00:05", 5.356, "2026-10-14 00:06"),
     ("VET", "2026-10-13 04:00", 0.007166, "2026-10-14 04:06"), ("ZEN", "2026-10-13 04:00", 6.015, "2026-10-14 04:06"),
     ("NMR", "2026-10-13 04:00", 12.340, "2026-10-14 04:06"), ("LPT", "2026-10-13 04:00", 1.635, "2026-10-14 04:06"),
     ("SHIB", "2026-10-13 04:00", 0.0000051, "2026-10-14 04:06"), ("AAVE", "2026-10-13 18:05", 159.120, "2026-10-14 18:06"), ("BTC", "2026-10-13 00:00", None, "")]
out = []
for nm, t, p0, cik in S:
    t0 = pd.Timestamp(t, tz="Europe/Istanbul"); st = int(t0.floor("min").timestamp() * 1000)
    k = requests.get("https://data-api.binance.vision/api/v3/klines", params=dict(symbol=nm + "USDT", interval="5m", startTime=st, limit=1000), timeout=20).json()
    d = pd.DataFrame([x[:5] for x in k], columns=["t", "o", "h", "l", "c"]).astype(float)
    p0 = p0 or d.o.iloc[0]; dol = (d.l.iloc[:12] <= p0).any()
    out.append(f"{nm:5s} giriş {p0:.8g} · limit doldu mu (60 dk) {'evet' if dol else 'HAYIR'} · şimdi {d.c.iloc[-1]:.8g} ({100*(d.c.iloc[-1]/p0-1):+.2f}%) · "
               f"en yüksek {100*(d.h.max()/p0-1):+.2f}% · en düşük {100*(d.l.min()/p0-1):+.2f}% · çıkış {cik}")
open("degerlendir_simdi.txt", "w").write(f"{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m %H:%M} TR\n" + "\n".join(out) + "\n"); print("\n".join(out))
