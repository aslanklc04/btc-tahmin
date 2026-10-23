# veri_zaman.py — 23.10.2026 (kullanıcı: "cron'u :00'a alırsam Binance'ten veri anında gelir mi, eksiksiz olur mu?") · yalnız ölçüm, canlıya dokunmaz.
# Bir sonraki saat başında :00:20 · :00:45 · :01:30 · :02:15'te tüm canlı kaynakları çeker, :06:00'daki (kesin) değerle karşılaştırır.
# Kaynaklar: Binance 1 s mum (BTC + 6 coin, data-api ve api) · Coinbase 1 s mum (BTC-USD + 4 coin) · Neon /saat (💧, biten saat) · Neon /fonlama · KuCoin fonlama.
import time, requests, pandas as pd
NE = "https://br-still-union-baibtf1k-derinlik.compute.c-8.eu-central-1.aws.neon.tech"
BN = ["BTC", "ETH", "SOL", "INJ", "CAKE", "RLC", "SHIB"]; CB = ["BTC", "ETH", "INJ", "SHIB", "LDO"]
s = requests.Session(); s.headers.update({"User-Agent": "btc-tahmin"})
def olc():
    now = pd.Timestamp.now(tz="UTC"); H = now.floor("h"); o = {}
    for u in ("https://data-api.binance.vision", "https://api.binance.com"):
        for c in BN:
            try:
                x = s.get(f"{u}/api/v3/klines", params=dict(symbol=c + "USDT", interval="1h", limit=3), timeout=15).json()
                k = [r for r in x if r[6] < now.timestamp() * 1000]                                  # kapanmış mumlar (closeTime < şimdi)
                o[f"BN {u.split('//')[1][:8]} {c}"] = (pd.Timestamp(k[-1][0], unit="ms", tz="UTC") + pd.Timedelta(hours=1), float(k[-1][4]), float(k[-1][5]))
            except Exception as e: o[f"BN {u.split('//')[1][:8]} {c}"] = ("hata", type(e).__name__, 0)
    for c in CB:
        try:
            x = s.get(f"https://api.exchange.coinbase.com/products/{c}-USD/candles", params=dict(granularity=3600, start=(H - pd.Timedelta(hours=5)).isoformat(), end=H.isoformat()), timeout=15).json()
            t = max(r[0] for r in x); r = [r for r in x if r[0] == t][0]
            o[f"CB {c}"] = (pd.Timestamp(t, unit="s", tz="UTC") + pd.Timedelta(hours=1), float(r[4]), float(r[5]))
        except Exception as e: o[f"CB {c}"] = ("hata", type(e).__name__, 0)
    try:
        d = s.get(f"{NE}/saat", params={"h": (H - pd.Timedelta(hours=1)).strftime("%Y%m%d%H")}, timeout=90).json(); cs = d.get("coins", {})
        n = [v.get("n", 0) for v in cs.values()]; o["Neon 💧 biten saat"] = (H, len(cs), (min(n) if n else 0, int(pd.Series(n).median()) if n else 0, sum(x >= 10 for x in n)))
    except Exception as e: o["Neon 💧 biten saat"] = ("hata", type(e).__name__, 0)
    try: d = s.get(f"{NE}/fonlama", timeout=60).json(); o["Neon fonlama"] = ("ok", str(d)[:120], 0)
    except Exception as e: o["Neon fonlama"] = ("hata", type(e).__name__, 0)
    try:
        j = s.get("https://api-futures.kucoin.com/api/v1/contract/funding-rates", params={"symbol": "XBTUSDTM", "from": int((H - pd.Timedelta(hours=24)).timestamp() * 1000), "to": int(now.timestamp() * 1000)}, timeout=20).json()
        t = max(int(r["timepoint"]) for r in j["data"]); o["KuCoin fonlama"] = (pd.Timestamp(t, unit="ms", tz="UTC"), len(j["data"]), 0)
    except Exception as e: o["KuCoin fonlama"] = ("hata", type(e).__name__, 0)
    return now, o
H0 = (pd.Timestamp.now(tz="UTC") + pd.Timedelta(minutes=1)).ceil("h"); R = []
for sn in (20, 45, 90, 135, 360):
    w = (H0 + pd.Timedelta(seconds=sn) - pd.Timestamp.now(tz="UTC")).total_seconds()
    if w > 0: time.sleep(w)
    R.append(olc()); print(R[-1][0], flush=True)
TR = lambda t: (t + pd.Timedelta(hours=3)).strftime("%H:%M:%S")
son = R[-1][1]; L = [f"# ⏱️ Saat başı veri tazeliği — {TR(H0)[:5]} TR saati (son saat = {TR(H0 - pd.Timedelta(hours=1))[:5]}–{TR(H0)[:5]} mumu)\n",
     "Her hücre: o anda dönen SON KAPANMIŞ mumun bitiş saati · kapanış fiyatı :06'daki kesin değerle aynı mı.\n",
     "| Kaynak | " + " | ".join(f"{TR(t)}" for t, _ in R[:-1]) + f" | {TR(R[-1][0])} (kesin) |", "|---|" + "---|" * len(R)]
for k in son:
    h = []
    for t, o in R:
        a, b, c = o.get(k, ("—", "", 0)); f, b0, c0 = son[k]
        if isinstance(a, pd.Timestamp): h.append(f"{TR(a)[:5]} " + ("✅" if a == H0 else "⏳ 1 saat eski") + ("" if not isinstance(f, pd.Timestamp) or a != f or k.startswith(("Neon", "Ku")) else (" · fiyat aynı" if b == b0 else f" · fiyat farklı {b} → {b0}")) + (f" · {b} coin, n min/medyan {c[0]}/{c[1]}, ≥10 olan {c[2]}" if k.startswith("Neon 💧") else ""))
        else: h.append(f"{a} {b}")
    L.append(f"| {k} | " + " | ".join(h) + " |")
open("veri_zaman_sonuc.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
