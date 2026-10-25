# sekil_liste.py — PROTOKOL_sekil.md: araştırma ve dokunulmamış coin listeleri
import json, requests
S = requests.Session(); A = "https://data.binance.vision/data/spot/monthly/klines"
ARS = sorted({l.strip()[:-4] for f in ("canli/durum/genis_liste.txt", "canli/durum/coin_listesi.txt") for l in open(f) if l.strip()} | {"BTC"})
info = S.get("https://data-api.binance.vision/api/v3/exchangeInfo", timeout=30).json()["symbols"]
tk = {x["symbol"]: float(x["quoteVolume"]) for x in S.get("https://data-api.binance.vision/api/v3/ticker/24hr", timeout=30).json()}
HARIC = {"USDC", "FDUSD", "TUSD", "BUSD", "DAI", "USDP", "EUR", "TRY", "BRL", "AEUR", "USDE", "PAXG", "WBTC", "WBETH", "BETH", "XUSD", "EURI", "USD1", "GBP", "AUD", "BFUSD", "RLUSD"}
ad = [x["baseAsset"] for x in info if x["quoteAsset"] == "USDT" and x["status"] == "TRADING" and x["baseAsset"] not in ARS and x["baseAsset"] not in HARIC
      and not x["baseAsset"].endswith(("UP", "DOWN", "BULL", "BEAR"))]
ad = sorted(ad, key=lambda b: -tk.get(b + "USDT", 0)); DOK = []
for b in ad:
    if S.head(f"{A}/{b}USDT/5m/{b}USDT-5m-2022-06.zip", timeout=15).status_code == 200: DOK.append(b)
    if len(DOK) >= 120: break
json.dump(dict(A=ARS, B=DOK), open("sekil_liste.json", "w")); print(len(ARS), "araştırma ·", len(DOK), "dokunulmamış:", " ".join(DOK))
