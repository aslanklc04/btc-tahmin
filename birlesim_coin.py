# birlesim_coin.py — COIN COIN: model sinyallerinin isabeti, tümü vs "ABD alıyor" onaylı (BTC primi / coin'in kendi Coinbase primi), 2024+ ve 2026
# Sinyaller: coin ⭐ (8 s) + 4s Çok güçlü ↑ + A sınıfı (4 s) birlikte ("model sinyali") ve ayrıca 24 saat 'Çok güçlü ↑'. Onay: sinyal saatinde prim z > 0.
import os, glob, time, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
src = open("bosluklar2.py").read(); exec(src[src.index("UA = "):src.index("def coinbase_1h")])          # kl()
BAS = pd.Timestamp("2023-10-01", tz="UTC")                                                   # 2024+ için 30 günlük pencere yeter
def cb(prod):
    out, cur, end = [], BAS, pd.Timestamp.now(tz="UTC"); s = requests.Session(); s.headers.update(UA); fails = 0
    if s.get(f"https://api.exchange.coinbase.com/products/{prod}", timeout=15).status_code != 200: return None
    while cur < end and fails < 30:
        nx = min(cur + pd.Timedelta(hours=300), end)
        try:
            r = s.get(f"https://api.exchange.coinbase.com/products/{prod}/candles", params=dict(granularity=3600, start=cur.isoformat(), end=nx.isoformat()), timeout=20)
            if r.status_code == 429: time.sleep(1); continue
            r.raise_for_status(); out += r.json(); cur = nx; time.sleep(0.12)
        except Exception: fails += 1; time.sleep(2)
    if not out: return None
    d = pd.DataFrame(out, columns=["t", "low", "high", "open", "close", "volume"]).drop_duplicates("t"); return pd.Series(d.close.values.astype(float), index=pd.to_datetime(d.t, unit="s", utc=True) + pd.Timedelta(hours=1)).sort_index()
EX = {os.path.basename(p)[5:-4][:-4]: pd.read_pickle(p) for p in glob.glob("art1/**/disa_*USDT.pkl", recursive=True)}
E24 = {os.path.basename(p)[7:-4][:-4]: pd.read_pickle(p) for p in glob.glob("art2/**/disa24_*USDT.pkl", recursive=True)}
NM = sorted(set(EX) | set(E24))
def prim(nm):
    try:
        c_ = cb(f"{nm}-USD"); b_ = kl(f"{nm}USDT")
        if c_ is None or b_ is None: return nm, None
        ix = pd.date_range(max(c_.index[0], BAS), b_.index[-1], freq="1h", tz="UTC"); p = np.log(c_.reindex(ix) / b_.reindex(ix).ffill(limit=3))
        return nm, (p - p.rolling(720, min_periods=168).mean()) / (p.rolling(720, min_periods=168).std() + 1e-12)
    except Exception: return nm, None
with ThreadPoolExecutor(4) as ex: Z = {k: v for k, v in ex.map(prim, NM) if v is not None}
ZB = Z["BTC"]; A24, A26, LMT = pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC"), 0.0002
CANLI = ["ADA", "APT", "ARB", "BNB", "DOGE", "DOT", "ETH", "FLOKI", "LINK", "NEAR", "OP", "PEPE", "SHIB", "SUI"]; D24 = ["ADA", "BNB", "BTC", "DOGE", "DOT", "ETH", "LINK", "NEAR", "OP", "SHIB"]
rows = []
for nm, X in EX.items():
    for k, H, yc in (("star", 8, "y8"), ("u4", 4, "y4"), ("acls", 4, "y4")):
        m = X[k].fillna(False).astype(bool).values & X[yc].notna().values
        for i in events(m, H):
            t = X.index[i]
            if t >= A24: rows.append(dict(tur="model", coin=nm, t=t, y=X[yc].iloc[i], zb=ZB.get(t, np.nan), zo=Z[nm].get(t, np.nan) if nm in Z else np.nan))
for nm, X in E24.items():
    X = X.reindex(pd.date_range(X.index[0], X.index[-1], freq="1h", tz="UTC")); c = X.close.ffill(limit=3).values; n = len(X)
    m = np.nan_to_num(((X.S24 > 0) & (X.C24 >= X.T10_24)).values).astype(bool) & X.T10_24.notna().values & (np.arange(n) + 26 < n)
    for i in events(m, 24):
        t = X.index[i]
        if t >= A24: rows.append(dict(tur="24s", coin=nm, t=t, y=np.log(c[i + 25] / c[i + 1]), zb=ZB.get(t, np.nan), zo=Z[nm].get(t, np.nan) if nm in Z else np.nan))
R = pd.DataFrame(rows).dropna(subset=["y"]); R["ok"] = R.y > 0; R["net"] = 100 * (np.exp(R.y) - 1 - 2 * LMT)
def h(x): return f"%{100*x.ok.mean():.0f} ({len(x)})" if len(x) >= 5 else (f"({len(x)})" if len(x) else "—")
def nt(x): return f"{x.net.mean():+.2f}" if len(x) >= 5 else "—"
yaz(f"# 🪙💵 Coin coin isabet: tümü vs 'ABD alıyor' onaylı — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nKendi Coinbase primi olan: {' '.join(sorted(Z))} · hücre: isabet (sinyal sayısı) · net = işlem başı %, limit komisyon\n")
for tur, ad, liste in (("model", "Model sinyalleri (⭐ + 4s Çok güçlü ↑ + A sınıfı)", None), ("24s", "24 saat 'Çok güçlü ↑'", D24)):
    for pn, a in (("2024+", A24), ("2026", A26)):
        out = []
        for nm in sorted(R[R.tur == tur].coin.unique()):
            x = R[(R.tur == tur) & (R.coin == nm) & (R.t >= a)]
            if not len(x): continue
            ob, oo = x[x.zb > 0], x[x.zo > 0] if x.zo.notna().any() else x.iloc[:0]
            out.append({"coin": nm + (" ●" if ((nm in D24) if tur == "24s" else (nm in CANLI)) else ""), "tümü": h(x), "net tümü": nt(x), "BTC primi onaylı": h(ob), "net (BTC onaylı)": nt(ob),
                        "kendi primi onaylı": h(oo) if len(oo) else "prim yok", "net (kendi onaylı)": nt(oo) if len(oo) else "—", "kendi primi ⛔ (z ≤ −1)": h(x[x.zo <= -1]) if x.zo.notna().any() else "—"})
        T = pd.DataFrame(out)
        if len(T):
            x = R[(R.tur == tur) & (R.t >= a)]
            T.loc[len(T)] = {"coin": "HEPSİ", "tümü": h(x), "net tümü": nt(x), "BTC primi onaylı": h(x[x.zb > 0]), "net (BTC onaylı)": nt(x[x.zb > 0]), "kendi primi onaylı": h(x[x.zo > 0]), "net (kendi onaylı)": nt(x[x.zo > 0]), "kendi primi ⛔ (z ≤ −1)": h(x[x.zo <= -1])}
            yaz(f"## {ad} · {pn}  (● = canlıda izlenen)\n```\n" + T.set_index("coin").to_string() + "\n```")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_"); open("birlesim_coin_sonuc.md", "w").write("\n".join(L) + "\n")
