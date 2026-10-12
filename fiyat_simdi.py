# fiyat_simdi.py — şu anki fiyatlar: bizim 141 coin'de gece yarısından (TR 00:00) ve son 24 saatten beri değişim (yalnız bilgi)
import requests, pandas as pd, numpy as np, time
from concurrent.futures import ThreadPoolExecutor
L = [l.strip() for f in ("canli/durum/coin_listesi.txt", "canli/durum/genis_liste.txt") for l in open(f) if l.strip()] + ["BTCUSDT"]
T = {d["symbol"]: d for d in requests.get("https://data-api.binance.vision/api/v3/ticker/24hr", timeout=30).json() if d["symbol"] in L}
gy = int(pd.Timestamp("2026-10-11 21:00", tz="UTC").timestamp() * 1000)
def k(s):
    try:
        x = requests.get("https://data-api.binance.vision/api/v3/klines", params=dict(symbol=s, interval="1h", startTime=gy, limit=1), timeout=20).json(); return s, float(x[0][1])
    except Exception: return s, np.nan
with ThreadPoolExecutor(10) as ex: G = dict(ex.map(k, L))
R = pd.DataFrame([dict(c=s[:-4], son=float(T[s]["lastPrice"]), d24=float(T[s]["priceChangePercent"]), gece=100 * (float(T[s]["lastPrice"]) / G[s] - 1)) for s in L if s in T and np.isfinite(G.get(s, np.nan))])
ana = ["ADA","APT","ARB","BNB","DOGE","DOT","ETH","FLOKI","LINK","NEAR","OP","PEPE","SHIB","SUI","BTC"]
o = [f"# Şu an ({pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m %H:%M} TR) · {len(R)} coin",
     f"- Gece 00:00'dan beri: yükselen {(R.gece > 0).sum()} · %2+ {(R.gece >= 2).sum()} · %5+ {(R.gece >= 5).sum()} · düşen {(R.gece < 0).sum()} · ortanca {R.gece.median():+.2f}%",
     f"- Son 24 saatte: yükselen {(R.d24 > 0).sum()} · %2+ {(R.d24 >= 2).sum()} · %5+ {(R.d24 >= 5).sum()} · düşen {(R.d24 < 0).sum()} · ortanca {R.d24.median():+.2f}%",
     "- Ana coinler (gece / 24 s): " + " · ".join(f"{r.c} {r.gece:+.1f}/{r.d24:+.1f}" for r in R[R.c.isin(ana)].itertuples()),
     "- En çok yükselen (gece): " + " · ".join(f"{r.c} {r.gece:+.1f}" for r in R.sort_values("gece", ascending=False).head(15).itertuples())]
print("\n".join(o)); open("fiyat_simdi_sonuc.md", "w").write("\n".join(o) + "\n")
