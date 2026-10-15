# upbit_veri.py — Upbit (Kore) saatlik mumları + Binance spot kapanışları (15.10.2026; "ABD satıyor ama Asya alıyor" araştırması için veri)
# Çıktı: upbit_veri.pkl = {coin: DataFrame(index=saat kapanışı UTC, krw=Upbit kapanış, krw_hacim=Upbit KRW işlem tutarı, usdt=Binance kapanış)}
import requests, time, threading, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import fetch_1h
BAS = pd.Timestamp("2022-01-01", tz="UTC"); SON = pd.Timestamp.now(tz="UTC").floor("h")
M = [x["market"] for x in requests.get("https://api.upbit.com/v1/market/all", timeout=20).json() if x["market"].startswith("KRW-")]
BIZ = set(l.strip()[:-4] for l in open("canli_liste.txt") if l.strip())
COINS = sorted(set(x[4:] for x in M) & BIZ) + ["BTC"]
KILIT = threading.Lock(); SON_IST = [0.0]
def bekle():
    with KILIT:
        d = 0.13 - (time.time() - SON_IST[0])
        if d > 0: time.sleep(d)
        SON_IST[0] = time.time()
def upbit(nm):
    rows, to = [], SON
    while to > BAS:
        for k in range(5):
            bekle()
            try:
                r = requests.get("https://api.upbit.com/v1/candles/minutes/60", params=dict(market=f"KRW-{nm}", to=to.strftime("%Y-%m-%dT%H:%M:%S"), count=200), timeout=20)
                if r.status_code == 429: time.sleep(1 + k); continue
                j = r.json(); break
            except Exception: time.sleep(1 + k); j = None
        if not j: break
        rows += j; to = pd.Timestamp(j[-1]["candle_date_time_utc"], tz="UTC")
        if len(j) < 200: break
    if not rows: return nm, None
    d = pd.DataFrame(rows); d.index = pd.to_datetime(d.candle_date_time_utc, utc=True) + pd.Timedelta(hours=1)   # kapanış saati (fetch_1h ile aynı)
    d = d[~d.index.duplicated()].sort_index()
    return nm, pd.DataFrame({"krw": d.trade_price.astype(float), "krw_hacim": d.candle_acc_trade_price.astype(float)})
T0 = time.time(); OUT = {}
with ThreadPoolExecutor(6) as ex:
    for nm, d in ex.map(upbit, COINS):
        if d is None: print(nm, "Upbit yok"); continue
        try: b = fetch_1h(BAS.value // 10**6, SON.value // 10**6, sym=nm + "USDT").close
        except Exception as e: print(nm, "Binance yok", e); b = None
        if b is not None: d["usdt"] = b.reindex(d.index)
        OUT[nm] = d; print(f"{nm}: {len(d)} saat {d.index[0]:%Y-%m-%d} → {d.index[-1]:%Y-%m-%d} · {time.time()-T0:.0f} sn", flush=True)
pd.to_pickle(OUT, "upbit_veri.pkl"); print("bitti", len(OUT), f"{time.time()-T0:.0f} sn")
