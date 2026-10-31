# teknik_golge_tani.py — canlı gölgede 28.10 sonrası 0 sinyal: hangi şart engelliyor? (yalnız tanı)
import pandas as pd, numpy as np, teknik_golge as T
a, b = pd.Timestamp("2026-10-20", tz="UTC"), pd.Timestamp.now(tz="UTC").floor("D")
with T.ThreadPoolExecutor(16) as ex: D = dict(ex.map(lambda nm: T.mum(nm, a - pd.Timedelta(days=40), b), T.COINS))
_, Bt = T.mum("BTC", a - pd.Timedelta(days=90), b); e = Bt.c.ewm(span=200, adjust=False).mean(); btr = Bt.c > e
print("coin yüklenen", sum(v is not None and len(v) >= 800 for v in D.values()), "/", len(T.COINS), "· BTC son mum", Bt.index[-1])
print("BTC > EMA200 payı (gün):"); print((btr[a:]).resample("D").mean().round(2).to_string())
print("BTC kapanış / EMA200 (gün sonu):"); print(pd.DataFrame(dict(c=Bt.c, ema=e))[a:].resample("D").last().round(0).to_string())
C = []
for nm, d in D.items():
    if d is None or len(d) < 800: continue
    c, q = d.c, d.qv; m20, s20 = c.rolling(20).mean(), c.rolling(20).std(); lb = m20 - 2 * s20
    m8 = (c > lb) & (c.shift() <= lb.shift()); q24 = q.rolling(24).sum(); vz = (q24 - q24.rolling(720).mean().shift(24)) / q24.rolling(720).std().shift(24)
    bt = btr.reindex(d.index).fillna(False).astype(bool)
    C.append(pd.DataFrame(dict(m8=m8, m8vz=m8 & (vz >= 2), m8bt=m8 & bt, hepsi=m8 & (vz >= 2) & bt))[a:])
S = pd.concat(C).groupby(level=0).sum().resample("D").sum(); print("günlük olay sayısı (tüm coin'ler):"); print(S.to_string())
