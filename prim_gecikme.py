# prim_gecikme.py — TEŞHİS (18.10.2026): Coinbase'in son saat mumu HH:05'te (canlının okuduğu an) tam mı, sonradan değişiyor mu?
# Saat başından sonra +2, +5, +10, +20, +40 dk'da az işlem gören coin'lerin son mumları ve canlı yöntemle z (ortak.cb_prim ile aynı) okunur, karşılaştırılır.
import time, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import fetch_1h, DISPLAY_TZ
UA = {"User-Agent": "btc-tahmin-tani"}
C = ["REQ", "ARPA", "PUNDIX", "BAND", "KNC", "C98", "GNO", "BNT", "MASK", "BLUR", "T", "CVC", "CELR", "AUDIO", "ALT", "KAVA", "UMA", "RPL", "ARKM", "GMT",
     "GTC", "POWR", "RLC", "AUCTION", "LQTY", "GLM", "ALICE", "RARE", "LPT", "AGLD", "1INCH", "CTSI", "FIDA", "MINA", "OGN", "API3", "G", "SUSHI", "VET", "ROSE"]
def anlik(nm):
    now = pd.Timestamp.now(tz="UTC").floor("h"); out = []; s = requests.Session(); s.headers.update(UA)
    for k in (3, 2, 1):
        a, b = now - pd.Timedelta(hours=300 * k), now - pd.Timedelta(hours=300 * (k - 1))
        for _ in range(3):
            r = s.get(f"https://api.exchange.coinbase.com/products/{nm}-USD/candles", params=dict(granularity=3600, start=a.isoformat(), end=b.isoformat()), timeout=20)
            if r.status_code == 200: out += r.json(); break
            time.sleep(1.5)
    d = pd.DataFrame(out, columns=["t", "low", "high", "open", "close", "volume"]).drop_duplicates("t")
    cb = pd.Series(d.close.values.astype(float), index=pd.to_datetime(d.t, unit="s", utc=True) + pd.Timedelta(hours=1)).sort_index()
    vol = pd.Series(d.volume.values.astype(float), index=cb.index.sort_values())
    bn = fetch_1h((now - pd.Timedelta(hours=920)).timestamp() * 1000, time.time() * 1000, sym=f"{nm}USDT").close
    p = np.log(cb / bn.reindex(cb.index)).dropna(); p = p[p.index <= bn.index[-1]]
    z = (p - p.rolling(720, min_periods=168).mean()) / (p.rolling(720, min_periods=168).std() + 1e-12)
    return nm, dict(son=z.index[-1], z=float(z.iloc[-1]), cb_son=cb.index.max(), close_t=float(cb.get(now, np.nan)), bn_t=float(bn.get(now, np.nan)), z_t=float(z.get(now, np.nan)))
h0 = pd.Timestamp.now(tz="UTC").ceil("h"); print("bekleniyor:", h0, flush=True)
while pd.Timestamp.now(tz="UTC") < h0 + pd.Timedelta(minutes=2): time.sleep(10)
S = {}
for dk in (2, 5, 10, 20, 40):
    while pd.Timestamp.now(tz="UTC") < h0 + pd.Timedelta(minutes=dk): time.sleep(5)
    with ThreadPoolExecutor(5) as ex: S[dk] = dict(ex.map(anlik, C))
    print(f"+{dk} dk okundu", flush=True)
rows = []
for nm in C:
    r = {"coin": nm}
    for dk in S: d = S[dk][nm]; r[f"z_{dk}"] = round(d["z"], 2); r[f"son_{dk}"] = f"{d['son']:%H}"; r[f"cb_{dk}"] = d["close_t"]
    rows.append(r)
X = pd.DataFrame(rows); pd.set_option("display.width", 300)
L = [f"# Coinbase son mum gecikmesi — saat {h0.tz_convert(DISPLAY_TZ):%d.%m %H:00} (TR)", "z_N = canlı yöntemle z, son_N = z'nin ait olduğu saat (UTC), cb_N = t mumunun Coinbase kapanışı, N = saat başından dakika", "```", X.to_string(index=False), "```"]
f = lambda a, b: int((X[f"z_{a}"] - X[f"z_{b}"]).abs().gt(0.2).sum())
L.append(f"- +5 dk ile +40 dk z farkı > 0,2 olan coin: {f(5, 40)} / {len(X)} · +2 ile +40: {f(2, 40)} · son mum +5'te eski saat olan: {int((X.son_5 != f'{h0:%H}').sum())} · +40'ta: {int((X.son_40 != f'{h0:%H}').sum())}")
open("prim_gecikme_sonuc.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
