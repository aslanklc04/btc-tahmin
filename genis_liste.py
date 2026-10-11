# genis_liste.py — GENİŞ COİN TARAMASI evreni: Coinbase USD ∩ Binance USDT (stabil / altın / sarılı hariç), Binance 24 saat hacmine göre en büyük N.
# Binance'te 2024-10'dan önce listelenmiş olmalı (seçim + doğrulama dönemi için en az ~2 yıl veri). Çıktı: GitHub matris listesi + genis_evren.csv
import sys, json, time, requests, pandas as pd
N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
UA = {"User-Agent": "btc-tahmin-arastirma"}
PR = requests.get("https://api.exchange.coinbase.com/products", headers=UA, timeout=60).json()
CBU = {p["base_currency"] for p in PR if p.get("quote_currency") == "USD" and p.get("status") == "online" and not p.get("trading_disabled")}
INFO = requests.get("https://data-api.binance.vision/api/v3/exchangeInfo", timeout=60).json()
BU = {s["baseAsset"] for s in INFO["symbols"] if s["quoteAsset"] == "USDT" and s["status"] == "TRADING"}
TK = requests.get("https://data-api.binance.vision/api/v3/ticker/24hr", timeout=60).json()
HAC = pd.Series({t["symbol"][:-4]: float(t["quoteVolume"]) for t in TK if t["symbol"].endswith("USDT")})
STAB = set("USDC USDT DAI TUSD USDP PYUSD FDUSD EUR GBP EURC USDS USDE USD1 RLUSD PAX BUSD WBTC CBETH PAXG XAUT WETH STETH BTC".split())
ORT = sorted((CBU & BU) - STAB)
sira = list(HAC.reindex(ORT).dropna().sort_values(ascending=False).index)
rows = []
for nm in sira:
    try:
        k = requests.get("https://data-api.binance.vision/api/v3/klines", params=dict(symbol=f"{nm}USDT", interval="1M", startTime=0, limit=1), timeout=20).json()
        ilk = pd.to_datetime(k[0][0], unit="ms", utc=True) if k else None
    except Exception: ilk = None
    rows.append(dict(nm=nm, sym=f"{nm}USDT", hacim=HAC[nm], ilk=ilk))
    time.sleep(0.05)
E = pd.DataFrame(rows); E["uygun"] = E.ilk.notna() & (E.ilk < pd.Timestamp("2024-10-01", tz="UTC"))
S = E[E.uygun].head(N); E.to_csv("genis_evren.csv", index=False)
print(f"Coinbase ∩ Binance: {len(ORT)} · listeleme uygun: {int(E.uygun.sum())} · seçilen: {len(S)}", file=sys.stderr)
print(json.dumps(["BTCUSDT"] + list(S.sym)))
