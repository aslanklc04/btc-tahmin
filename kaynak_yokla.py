# kaynak_yokla.py — 26.10: 🧑 bitcoin-data.com neden 18.10'da kaldı? Uç noktayı ve benzerlerini yokla (yalnız tanı)
import requests, json
S = requests.Session(); H = {"User-Agent": "btc-tahmin"}; L = []
for u in ["https://bitcoin-data.com/v1/coins-addr-1-BTC", "https://bitcoin-data.com/v1/coins-addr-1-BTC/last", "https://bitcoin-data.com/v1/coins-addr-10-BTC",
          "https://bitcoin-data.com/v1/btc-price", "https://bitcoin-data.com/v1/sopr", "https://bitcoin-data.com/v1/mvrv"]:
    try:
        r = S.get(u, headers=H, timeout=60); hd = {k: v for k, v in r.headers.items() if k.lower().startswith(("x-", "retry", "date", "content-type"))}
        try:
            j = r.json(); son = j[-3:] if isinstance(j, list) else j
        except Exception: son = r.text[:300]
        L.append(f"## {u}\nHTTP {r.status_code} · {len(r.content):,} bayt · başlıklar {hd}\nson: {json.dumps(son, ensure_ascii=False)[:600]}\n")
    except Exception as e: L.append(f"## {u}\nHATA {e!r}\n")
open("kaynak_yokla.md", "w").write("\n".join(L)); print("\n".join(L))
