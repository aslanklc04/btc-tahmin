# kaynak_yokla.py — 🧑 küçük yatırımcı verisi: bitcoin-data.com hâlâ durgun mu, yerine geçebilecek kaynak var mı (yalnız yoklama)
import requests, pandas as pd
H = {"User-Agent": "btc-tahmin"}
def dene(ad, u, **k):
    try:
        r = requests.get(u, timeout=60, headers=H, **k); print(f"\n== {ad}: HTTP {r.status_code} · {len(r.content)} bayt"); print(r.text[:600].replace("\n", " "))
        return r
    except Exception as e: print(f"\n== {ad}: HATA {e}")
r = dene("bitcoin-data 1 BTC", "https://bitcoin-data.com/v1/coins-addr-1-BTC")
try:
    j = r.json(); d = pd.DataFrame(j); print("son satırlar:", d.tail(3).to_dict("records"))
except Exception as e: print("json yok", e)
dene("bitcoin-data last", "https://bitcoin-data.com/v1/coins-addr-1-BTC/last")
dene("bitcoin-data 10 BTC", "https://bitcoin-data.com/v1/coins-addr-10-BTC/last")
dene("bitcoin-data mvrv last", "https://bitcoin-data.com/v1/mvrv/last")
CM = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
for m in ["SplyAdrBalNtv1", "SplyAdrBalNtv0.1", "SplyAdrBalNtv0.01", "SplyAdrBalNtv10", "SplyCur", "AdrBalNtv1Cnt", "AdrBal1in100KCnt", "SplyAdrBal1in100K"]:
    dene(f"CoinMetrics {m}", CM, params=dict(assets="btc", metrics=m, frequency="1d", start_time="2026-10-01", page_size=100))
