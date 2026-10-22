# kaynak_kontrol.py — 22.10.2026: dış veri kaynakları güncel mi? (🧑 bitcoin-data.com 19.10'dan beri değerlendirme yapmadı) · yalnız bilgi
import requests, pandas as pd, json
o = [f"# Kaynak kontrolü — {pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M}"]
try:
    r = requests.get("https://bitcoin-data.com/v1/coins-addr-1-BTC", timeout=60, headers={"User-Agent": "btc-tahmin"})
    o.append(f"bitcoin-data.com HTTP {r.status_code} · başlıklar: " + ", ".join(f"{k}={v}" for k, v in r.headers.items() if "limit" in k.lower() or "retry" in k.lower()))
    if r.status_code == 200:
        d = pd.DataFrame(r.json()); o.append(f"  satır {len(d)} · sütunlar {list(d.columns)[:5]} · son 5: " + json.dumps(r.json()[-5:])[:600])
    else: o.append("  gövde: " + r.text[:300])
except Exception as e: o.append(f"bitcoin-data.com HATA {type(e).__name__}: {e}")
for ad, url in (("Coin Metrics ETH", "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets=eth&metrics=SplyExNtv&frequency=1d&page_size=3&paging_from=end"),
                ("DefiLlama stabil", "https://stablecoins.llama.fi/stablecoincharts/all")):
    try:
        r = requests.get(url, timeout=60); j = r.json()
        son = j["data"][-1] if isinstance(j, dict) and "data" in j else (j[-1] if isinstance(j, list) else str(j)[:200])
        o.append(f"{ad}: HTTP {r.status_code} · son: {str(son)[:200]}")
    except Exception as e: o.append(f"{ad} HATA {type(e).__name__}: {e}")
print("\n".join(o)); open("kaynak_kontrol_sonuc.md", "w").write("\n".join(o) + "\n")
# 🔥 KuCoin BTC fonlama z — gonder.fon_z ile aynı hesap, son 14 gün her ödeme
import time
now = int(time.time() * 1000); out = []
for k in (2, 1):
    j = requests.get("https://api-futures.kucoin.com/api/v1/contract/funding-rates", params={"symbol": "XBTUSDTM", "from": now - k * 30 * 86400000, "to": now - (k - 1) * 30 * 86400000}, timeout=20).json()
    out += j.get("data", []) if isinstance(j, dict) else []
d = pd.Series({int(x["timepoint"]): float(x["fundingRate"]) for x in out}).sort_index()
z = (d - d.rolling(90, min_periods=30).mean()) / (d.rolling(90, min_periods=30).std() + 1e-12)
z.index = pd.to_datetime(z.index, unit="ms", utc=True).tz_convert("Europe/Istanbul"); z = z[z.index >= pd.Timestamp.now(tz="Europe/Istanbul") - pd.Timedelta(days=14)]
o.append(f"\n🔥 KuCoin BTC fonlama z (≥ 2 → yedekler ana olur), son 14 gün: {len(z)} ödeme · en yüksek {z.max():+.2f} · ≥ 2 olan {int((z >= 2).sum())}")
o.append(" · ".join(f"{t:%d.%m %H}h {v:+.1f}" for t, v in z.items()))
print("\n".join(o[-2:])); open("kaynak_kontrol_sonuc.md", "w").write("\n".join(o) + "\n")
