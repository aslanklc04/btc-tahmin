# birlesim.py — MODEL SİNYALİ + COINBASE PRİMİ: isabetli sinyal geldiğinde ABD'li yatırımcı da prim ödeyip alıyor mu? Alıyorsa sinyal daha mı çok tutuyor?
# Sinyaller (canlı sistemdekilerle aynı, geçmiş yürüyen testten): BTC ⭐ (8 s) · BTC 4s Çok güçlü ↑ · BTC A sınıfı (4 s) ·
#   coin ⭐ (8 s) / 4s Çok güçlü ↑ / A sınıfı (19 coin) · 24 saat deneme sinyali (10 coin, 'Çok güçlü ↑').
# Prim: log(Coinbase BTC-USD / Binance BTCUSDT), son 30 güne göre z — sinyal saatinde BİLİNEN değer. Coin sinyallerinde ayrıca coin'in KENDİ Coinbase primi.
# Gruplar: ABD alıyor (z ≥ +1) · nötr (−1 < z < +1) · ABD satıyor (z ≤ −1); ayrıca z > 0 / z ≤ 0.
# ÖNCEDEN SABİT karar: "onaylı" (z > 0) grubun isabeti VE net'i, onaysız (z ≤ 0) gruptan ≤2023'te de 2024+'da da yüksek, ve sinyallerin ≥ %30'u kalıyor → ✅
import os, glob, time, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
src = open("bosluklar2.py").read(); exec(src[src.index("UA = "):src.index("def upbit_1h")])          # kl() ve coinbase_1h()
EX = {os.path.basename(p)[5:-4]: pd.read_pickle(p) for p in glob.glob("art1/**/disa_*USDT.pkl", recursive=True)}
E24 = {os.path.basename(p)[7:-4]: pd.read_pickle(p) for p in glob.glob("art2/**/disa24_*USDT.pkl", recursive=True)}
CBP = ["BTC", "ETH", "ADA", "DOGE", "DOT", "LINK", "NEAR", "OP", "SHIB", "SOL", "AVAX", "SUI", "APT", "ARB", "PEPE", "INJ", "FET"]
def cb_var(prod):
    try: return requests.get(f"https://api.exchange.coinbase.com/products/{prod}", headers=UA, timeout=15).status_code == 200
    except Exception: return False
def prim(nm):
    if not cb_var(f"{nm}-USD"): return nm, None
    cb = coinbase_1h(f"{nm}-USD"); bn = kl(f"{nm}USDT")
    if cb is None or bn is None: return nm, None
    ix = pd.date_range(bn.index[0], bn.index[-1], freq="1h", tz="UTC"); p = np.log(cb.reindex(ix) / bn.reindex(ix).ffill(limit=3))
    return nm, (p - p.rolling(720, min_periods=168).mean()) / (p.rolling(720, min_periods=168).std() + 1e-12)
with ThreadPoolExecutor(4) as ex: Z = {k: v for k, v in ex.map(prim, CBP) if v is not None}
yaz(f"# 🤝💵 Model sinyali + Coinbase primi — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nPrimi hesaplanan: {' '.join(Z)} · model dosyaları: {len(EX)} coin (⭐/4s/A) + {len(E24)} coin (24 s) · {time.time()-T0:.0f} sn\n")
ZB = Z["BTC"]; LMT = 0.0002; A24, A26 = pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")
rows = []
for sym, X in EX.items():
    nm = sym[:-4]
    for k, H, ycol, ad in (("star", 8, "y8", "⭐ en güçlü (8 s)"), ("u4", 4, "y4", "4s Çok güçlü ↑"), ("acls", 4, "y4", "A sınıfı (4 s)")):
        m = X[k].fillna(False).astype(bool).values & X[ycol].notna().values
        for i in events(m, H):
            t = X.index[i]; rows.append(dict(grup=("BTC " if nm == "BTC" else "Coin ") + ad, coin=nm, t=t, y=X[ycol].iloc[i], zb=ZB.get(t, np.nan), zo=Z[nm].get(t, np.nan) if nm in Z else np.nan))
for sym, X in E24.items():
    nm = sym[:-4]; X = X.reindex(pd.date_range(X.index[0], X.index[-1], freq="1h", tz="UTC")); c = X.close.ffill(limit=3).values; n = len(X)
    m = np.nan_to_num(((X.S24 > 0) & (X.C24 >= X.T10_24)).values).astype(bool) & X.T10_24.notna().values & (np.arange(n) + 26 < n)
    for i in events(m, 24):
        t = X.index[i]; rows.append(dict(grup="24 saat deneme (Çok güçlü ↑)" if nm in ("ADA", "BNB", "BTC", "DOGE", "DOT", "ETH", "LINK", "NEAR", "OP", "SHIB") else "24 saat (diğer coin'ler)",
                                         coin=nm, t=t, y=np.log(c[i + 25] / c[i + 1]), zb=ZB.get(t, np.nan), zo=Z[nm].get(t, np.nan) if nm in Z else np.nan))
R = pd.DataFrame(rows).dropna(subset=["y"]); R = R[R.t >= pd.Timestamp("2020-01-01", tz="UTC")]; R["net"] = np.exp(R.y) - 1 - 2 * LMT; R["ok"] = R.y > 0
DON = {"≤2023": R.t < A24, "2024+": R.t >= A24, "2026": R.t >= A26}
def tablo(zcol, baslik):
    out = []
    for g, x in R.groupby("grup"):
        x = x.dropna(subset=[zcol])
        for pn, mk in DON.items():
            y_ = x[mk.reindex(x.index)]; tot = len(y_)
            for gad, sel in (("hepsi", y_[zcol].notna()), ("ABD alıyor (z ≥ +1)", y_[zcol] >= 1), ("z > 0", y_[zcol] > 0), ("nötr", y_[zcol].abs() < 1), ("z ≤ 0", y_[zcol] <= 0), ("ABD satıyor (z ≤ −1)", y_[zcol] <= -1)):
                s = y_[sel]
                if len(s) < 10: continue
                lo, _ = wboot(s.net.values, s.t.values) if len(s) >= 20 else (np.nan, np.nan)
                out.append(dict(sinyal=g, donem=pn, prim=gad, n=len(s), pay=100 * len(s) / tot, isabet=100 * s.ok.mean(), net=100 * s.net.mean(), alt=100 * lo))
    T = pd.DataFrame(out); yaz(f"## {baslik}\n```\n" + T.set_index(["sinyal", "donem", "prim"]).round(2).to_string() + "\n```"); return T
T1 = tablo("zb", "Sinyal anında BTC'nin Coinbase primi (ABD'nin genel alım/satımı)")
yaz("\n## Karar (önceden sabit: 'z > 0' grubu, 'z ≤ 0' grubundan ≤2023 ve 2024+'da hem isabet hem net olarak iyi, sinyallerin ≥ %30'u kalıyor)")
for g in T1.sinyal.unique():
    p = T1[T1.sinyal == g].set_index(["donem", "prim"]); ok = True; parts = []
    for pn in ("≤2023", "2024+"):
        if (pn, "z > 0") not in p.index or (pn, "z ≤ 0") not in p.index: ok = False; continue
        a, b = p.loc[(pn, "z > 0")], p.loc[(pn, "z ≤ 0")]; ok &= a.isabet > b.isabet and a.net > b.net and a.pay >= 30
        parts.append(f"{pn}: isabet %{b.isabet:.1f} → %{a.isabet:.1f}, net {b.net:+.2f} → {a.net:+.2f} (kalan %{a.pay:.0f})")
    z26 = (f" · 2026: %{p.loc[('2026','z ≤ 0')].isabet:.1f} → %{p.loc[('2026','z > 0')].isabet:.1f}, net {p.loc[('2026','z ≤ 0')].net:+.2f} → {p.loc[('2026','z > 0')].net:+.2f}"
           if ("2026", "z > 0") in p.index and ("2026", "z ≤ 0") in p.index else "")
    yaz(f"- {'✅' if ok else '❌'} {g}: " + " · ".join(parts) + z26)
if R.zo.notna().sum() > 200:
    R2 = R[~R.grup.str.startswith("BTC")].copy(); R_ = R; R = R2; tablo("zo", "Coin sinyallerinde coin'in KENDİ Coinbase primi"); R = R_
yaz(f"\n_Süre: {time.time()-T0:.0f} sn · net = işlem başı %, limit komisyon %0,02 × 2 · alt = haftalık blok bootstrap %90 alt sınırı · pay = o dönemdeki sinyallerin yüzde kaçı bu grupta_")
open("birlesim_sonuc.md", "w").write("\n".join(L) + "\n")
