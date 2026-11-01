# denetim_yokla.py — 02.11.2026: işlem botu fizibilitesi — GitHub Actions (ABD) sunucusundan Binance TR / Binance global API'lerine erişim (anahtarsız, yalnız herkese açık uçlar)
import requests
for ad, u in (("Binance TR sembol listesi", "https://www.binance.tr/open/v1/common/symbols"), ("Binance TR saat", "https://www.binance.tr/open/v1/common/time"),
              ("Binance TR piyasa (api.binance.me)", "https://api.binance.me/api/v3/ping"), ("Binance global spot", "https://api.binance.com/api/v3/ping"),
              ("Binance global vadeli", "https://fapi.binance.com/fapi/v1/ping"), ("Binance US", "https://api.binance.us/api/v3/ping")):
    try:
        r = requests.get(u, timeout=20); print(f"{ad}: HTTP {r.status_code} · {r.text[:160]!r}")
        if "symbols" in u and r.status_code == 200:
            j = r.json(); L = j.get("data", {}).get("list", []) if isinstance(j, dict) else []
            print("  sembol sayısı", len(L), "· TRY:", sum(1 for x in L if str(x.get("symbol", "")).endswith("_TRY")), "· USDT:", sum(1 for x in L if str(x.get("symbol", "")).endswith("_USDT")), "· örnek", [x.get("symbol") for x in L[:8]])
    except Exception as e: print(f"{ad}: HATA {repr(e)[:160]}")
