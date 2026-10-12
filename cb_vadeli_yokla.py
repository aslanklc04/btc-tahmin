# cb_vadeli_yokla.py — Coinbase VADELİ verisi GitHub'dan (ABD) alınabiliyor mu? INTX (uluslararası sürekli vadeli) fonlama + mum, ABD vadeli (CDE) ürünleri. Yalnız yoklama.
import requests, json, time
S = requests.Session(); S.headers["User-Agent"] = "btc-tahmin-arastirma"
def g(url, **p):
    try:
        r = S.get(url, params=p, timeout=30); t = r.text
        return r.status_code, (r.json() if r.status_code == 200 and t[:1] in "[{" else t[:200])
    except Exception as e: return -1, str(e)[:150]
out = []
def yaz(s): print(s, flush=True); out.append(str(s))
st, d = g("https://api.international.coinbase.com/api/v1/instruments")
yaz(f"INTX enstrümanlar: {st}")
if st == 200:
    perps = [x for x in d if x.get("type") == "PERP"]; yaz(f"  sürekli vadeli sayısı: {len(perps)} · örnek: {[x.get('symbol') for x in perps[:40]]}")
for path, p in (("instruments/BTC-PERP/funding", {"result_limit": 5}), ("instruments/BTC-PERP/funding", {"result_limit": 5, "result_offset": 20000})):
    st, d = g(f"https://api.international.coinbase.com/api/v1/{path}", **p); yaz(f"INTX {path} {p}: {st} · {json.dumps(d)[:600] if st == 200 else d}")
for prod in ("BTC-PERP-INTX", "ETH-PERP-INTX", "DOGE-PERP-INTX"):
    st, d = g(f"https://api.coinbase.com/api/v3/brokerage/market/products/{prod}/candles", granularity="ONE_HOUR", start=str(int(time.time()) - 3600 * 300), end=str(int(time.time())))
    yaz(f"Advanced Trade mum {prod} (son 300 s): {st} · {(str(len(d.get('candles', []))) + ' mum · ' + json.dumps(d.get('candles', [])[:1])) if st == 200 else d}")
    st, d = g(f"https://api.coinbase.com/api/v3/brokerage/market/products/{prod}/candles", granularity="ONE_HOUR", start=str(1693526400), end=str(1693526400 + 3600 * 300))
    yaz(f"  2023-09 penceresi: {st} · {(str(len(d.get('candles', []))) + ' mum') if st == 200 else d}")
st, d = g("https://api.coinbase.com/api/v3/brokerage/market/products", product_type="FUTURE", limit=300)
if st == 200:
    ps = d.get("products", []); yaz(f"Advanced Trade FUTURE ürünleri: {len(ps)} · örnek: {[x.get('product_id') for x in ps[:60]]}")
else: yaz(f"Advanced Trade FUTURE ürünleri: {st} · {d}")
open("cb_vadeli_yokla_sonuc.md", "w").write("```\n" + "\n".join(out) + "\n```\n")
