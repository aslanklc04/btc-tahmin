# ou2_veri.py — PROTOKOL_ou2.md verisi (Actions): hiç bakılmamış en hacimli 120 USDT coin'i + BTC, 1 s mum 2022 →
import time, requests, pandas as pd
U = "https://data-api.binance.vision/api/v3"; S = requests.Session()
eski = set(open("ou2_eski_coinler.txt").read().split())
info = S.get(f"{U}/exchangeInfo", timeout=60).json()["symbols"]; tic = {x["symbol"]: float(x["quoteVolume"]) for x in S.get(f"{U}/ticker/24hr", timeout=60).json()}
STAB = {"USDC", "FDUSD", "TUSD", "BUSD", "USDP", "DAI", "EUR", "EURI", "AEUR", "USDE", "USD1", "XUSD", "BFUSD", "RLUSD", "PAXG", "WBTC", "WBETH", "BNSOL", "USDS"}
aday = [s["baseAsset"] for s in info if s["quoteAsset"] == "USDT" and s["status"] == "TRADING" and s["baseAsset"] not in eski and s["baseAsset"] not in STAB
        and not any(s["baseAsset"].endswith(k) for k in ("UP", "DOWN", "BULL", "BEAR"))]
aday = sorted(aday, key=lambda b: -tic.get(f"{b}USDT", 0))[:160]; print("aday", len(aday), aday[:20])
def kl(sym):
    out, cur, son = [], int(pd.Timestamp("2022-01-01", tz="UTC").timestamp() * 1000), int(time.time() * 1000)
    while cur < son:
        for k in range(5):
            try: x = S.get(f"{U}/klines", params=dict(symbol=sym, interval="1h", startTime=cur, limit=1000), timeout=30).json(); break
            except Exception: time.sleep(2 + 2 * k); x = None
        if not isinstance(x, list) or not x: break
        out += x; cur = x[-1][0] + 3_600_000
        if len(x) < 1000: break
    return out
P = []; n = 0
for b in ["BTC"] + aday:
    x = kl(f"{b}USDT")
    if len(x) < 3000 and b != "BTC": continue
    d = pd.DataFrame([z[:5] for z in x], columns=["ot", "o", "h", "l", "c"]).astype(float); d["t"] = pd.to_datetime(d.ot, unit="ms", utc=True) + pd.Timedelta(hours=1); d["coin"] = b
    P.append(d.drop(columns="ot")); n += b != "BTC"; print(b, len(d), flush=True)
    if n >= 120: break
pd.concat(P, ignore_index=True).astype({"o": "float32", "h": "float32", "l": "float32", "c": "float32"}).to_parquet("ou2_mum.parquet"); print("bitti", n)
