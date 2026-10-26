# turev_piyasa.py — PROTOKOL_turev.md: piyasa geneli (Deribit DVOL saatlik · korku-açgözlülük günlük) → turev_piyasa.csv.gz (saatlik, t = saat kapanışı)
import time, requests, pandas as pd
S = requests.Session(); U = "https://www.deribit.com/api/v2/public/get_volatility_index_data"
a = int(pd.Timestamp("2021-04-01", tz="UTC").timestamp() * 1000); son = int(time.time() * 1000); D = []
while a < son:
    b = min(son, a + 900 * 3600 * 1000)
    for k in range(5):
        try: j = S.get(U, params=dict(currency="BTC", start_timestamp=a, end_timestamp=b, resolution=3600), timeout=30).json(); break
        except Exception: time.sleep(2 + k)
    D += j.get("result", {}).get("data", []); a = b
d = pd.DataFrame(D, columns=["ts", "o", "h", "l", "c"]).drop_duplicates("ts"); d.index = pd.to_datetime(d.ts, unit="ms", utc=True) + pd.Timedelta(hours=1); d = d.sort_index()
dv = d.c.astype(float); P = pd.DataFrame({"dvol": (dv - dv.rolling(720, min_periods=168).mean()) / (dv.rolling(720, min_periods=168).std() + 1e-12), "dvol24": dv - dv.shift(24), "dvol_ham": dv})
fg = requests.get("https://api.alternative.me/fng/?limit=0&format=json", timeout=30).json()["data"]
g = pd.Series({pd.Timestamp(int(x["timestamp"]), unit="s", tz="UTC"): float(x["value"]) for x in fg}).sort_index()
g.index = g.index + pd.Timedelta(days=1)                                                       # günün değeri ertesi gün 00:00'dan itibaren bilinir sayılır (önceki gün)
P["fg"] = g.reindex(P.index, method="ffill")
P.to_csv("turev_piyasa.csv.gz", compression="gzip"); print(len(P), "saat ·", P.index.min(), "→", P.index.max(), "· fg", g.index.min())
