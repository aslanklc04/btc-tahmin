# wif_simdi.py — 22.10.2026 WIF 🌐🧪 sinyali (giriş $0,2049 · 🎯 $0,2132 · çıkış 23.10 07:06 TR) şu an nerede? (yalnız bilgi)
import requests, pandas as pd
o = []
for s in ("WIFUSDT", "BTCUSDT"):
    x = requests.get("https://data-api.binance.vision/api/v3/klines", params=dict(symbol=s, interval="1h", startTime=int(pd.Timestamp("2026-10-22 03:00", tz="UTC").timestamp() * 1000), limit=40), timeout=20).json()
    d = pd.DataFrame([r[:5] for r in x], columns=["t", "a", "y", "d", "k"]).astype(float); d.index = pd.to_datetime(d.t, unit="ms", utc=True).tz_convert("Europe/Istanbul") + pd.Timedelta(hours=1)
    o.append(f"## {s} (saat = mum kapanışı, TR)")
    o += [f"{t:%d.%m %H:%M} açılış {r.a:.6g} · en yüksek {r.y:.6g} · en düşük {r.d:.6g} · kapanış {r.k:.6g}" for t, r in d.iterrows()]
    if s == "WIFUSDT":
        g = 0.2049; o.append(f"giriş $0,2049'a göre: şu an {100 * (d.k.iloc[-1] / g - 1):+.2f}% · en düşük {100 * (d.d.iloc[1:].min() / g - 1):+.2f}% · en yüksek {100 * (d.y.iloc[1:].max() / g - 1):+.2f}% · 🎯 $0,2132'ye değdi mi: {'EVET' if d.y.iloc[1:].max() >= 0.2132 else 'hayır'}")
print("\n".join(o)); open("wif_simdi_sonuc.md", "w").write("\n".join(o) + "\n")
