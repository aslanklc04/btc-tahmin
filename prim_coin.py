# prim_coin.py — COİN'İN KENDİ COINBASE PRİMİ TEK BAŞINA SİNYAL: ABD bir coin'i olağandışı güçlü alıyorsa (prim z ≥ 2) o coin'i AL, güçlü satıyorsa (z ≤ −2) SAT.
# Prim = log(Coinbase COIN-USD / Binance COINUSDT), saatlik, son 720 saate göre z (canlıdaki ortak.cb_prim ile aynı tanım).
# Evren: Coinbase'de USD, Binance'te USDT çifti olan en likit coin'ler (sistemdeki 14 coin + Binance hacmine göre en büyükler, en fazla 50; stabil hariç).
# Olay: koşulun ilk saati, tutma süresince tekrar yok · giriş 1 saat sonra (sinyal saatinin kapanışından 1 saat sonraki kapanış) · 4 / 8 / 24 saat tut · limit komisyon %0,02 × 2.
# Önceden sabit kurallar: AL2 z ≥ 2 · AL3 z ≥ 3 · SAT2 z ≤ −2. Seçim 2022-06 → 2023 · doğrulama 2024+ · 2026 ayrıca.
# ✅ (coin × kural × süre): seçimde ≥ 10 işlem ve net > 0 · doğrulamada ≥ 15 işlem, net > 0, %90 alt sınır > 0. Havuz (tüm coin'ler) ve plasebo (sinyal kaydırılmış) ile şans payı.
import os, time, threading, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
UA = {"User-Agent": "btc-tahmin-arastirma"}; BAS = pd.Timestamp("2022-05-01", tz="UTC")
_kilit, _son = threading.Lock(), [0.0]
def cb_get(url, **p):
    for k in range(8):
        with _kilit:                                                                                   # Coinbase genel sınırı: ~10 istek/sn → en az 0,12 sn arayla
            w = 0.12 - (time.time() - _son[0])
            if w > 0: time.sleep(w)
            _son[0] = time.time()
        try:
            r = requests.get(url, params=p, headers=UA, timeout=20)
            if r.status_code == 429: time.sleep(1 + k); continue
            return r
        except Exception: time.sleep(2)
    return None
PR = cb_get("https://api.exchange.coinbase.com/products").json()
CBU = {p["base_currency"] for p in PR if p.get("quote_currency") == "USD" and p.get("status") == "online" and not p.get("trading_disabled")}
INFO = requests.get("https://data-api.binance.vision/api/v3/exchangeInfo", timeout=60).json()
BU = {s["baseAsset"] for s in INFO["symbols"] if s["quoteAsset"] == "USDT" and s["status"] == "TRADING"}
TK = requests.get("https://data-api.binance.vision/api/v3/ticker/24hr", timeout=60).json()
HAC = pd.Series({t["symbol"][:-4]: float(t["quoteVolume"]) for t in TK if t["symbol"].endswith("USDT")})
STAB = set("USDC USDT DAI TUSD USDP PYUSD FDUSD EUR GBP EURC USDS USDE USD1 RLUSD PAX BUSD WBTC CBETH".split())
ORT = sorted((CBU & BU) - STAB)
SIS = [l.strip().replace("USDT", "") for l in open("durum/coin_listesi.txt") if l.strip()]
EVREN = list(dict.fromkeys(["BTC", "ETH"] + [c for c in SIS if c in ORT] + list(HAC.reindex(ORT).dropna().sort_values(ascending=False).index)))[:50]
yaz(f"# 💵 Coin'in kendi Coinbase primi → tek başına AL / SAT — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nCoinbase USD ∩ Binance USDT: {len(ORT)} coin · test edilen ({len(EVREN)}): {', '.join(EVREN)}\n")
def cb(nm):
    out, cur, end = [], BAS, pd.Timestamp.now(tz="UTC").floor("h")
    while cur < end:
        nx = min(cur + pd.Timedelta(hours=300), end); r = cb_get(f"https://api.exchange.coinbase.com/products/{nm}-USD/candles", granularity=3600, start=cur.isoformat(), end=nx.isoformat())
        if r is None or r.status_code != 200:
            if r is not None and r.status_code == 404: return None
            cur = nx; continue
        out += r.json(); cur = nx
    if not out: return None
    d = pd.DataFrame(out, columns=["t", "low", "high", "open", "close", "volume"]).drop_duplicates("t")
    return pd.Series(d.close.values.astype(float), index=pd.to_datetime(d.t, unit="s", utc=True) + pd.Timedelta(hours=1)).sort_index()
def veri(nm):
    try:
        c_ = cb(nm); o = fetch_1h(BAS.timestamp() * 1000, time.time() * 1000, sym=f"{nm}USDT")
        if c_ is None or o is None or len(c_) < 2000: return nm, None
        c_.index = c_.index.astype("datetime64[ns, UTC]"); o.index = o.index.astype("datetime64[ns, UTC]")
        ix = o.index[o.index >= c_.index[0]]; p = np.log(c_.reindex(ix) / o.close.reindex(ix))
        z = (p - p.rolling(720, min_periods=168).mean()) / (p.rolling(720, min_periods=168).std() + 1e-12)
        return nm, pd.DataFrame({"c": o.close.reindex(ix), "z": z, "bp": 1e4 * p})
    except Exception as e: print(nm, e); return nm, None
if os.path.exists("prim_veri.pkl"): V = pd.read_pickle("prim_veri.pkl"); yaz("_(veri önceki çalışmanın kaydından)_")
else:
    with ThreadPoolExecutor(6) as ex: V = {k: v for k, v in ex.map(veri, EVREN) if v is not None}
    pd.to_pickle({k: v.astype("float32") for k, v in V.items()}, "prim_veri.pkl")
V = {k: v.astype("float64") for k, v in V.items() if len(v) >= 3000}
yaz(f"Veri gelen: {len(V)} coin · {time.time()-T0:.0f} sn\n")
A24, A26, LMT = pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC"), 0.0002
DON = (("seçim 2022-06→2023", lambda i: i < A24), ("doğrulama 2024+", lambda i: i >= A24), ("2026", lambda i: i >= A26))
KUR = {"AL2 (z ≥ 2)": (lambda z: z >= 2, 1), "AL3 (z ≥ 3)": (lambda z: z >= 3, 1), "SAT2 (z ≤ −2)": (lambda z: z <= -2, -1)}
def net_ser(D, m, yon, H):
    y = D.c.shift(-(1 + H)) / D.c.shift(-1) - 1; ev = D.index[events(m.values, H)]; return yon * y.reindex(ev).dropna() - 2 * LMT
def ozet(net, reps=800):
    out = {}
    for pn, f in DON:
        x = net[f(net.index)]; out[pn] = (len(x), 100 * (x > 0).mean() if len(x) else np.nan, 100 * x.mean() if len(x) else np.nan, 100 * wboot(x.values, x.index.values, reps)[0] if len(x) >= 8 else np.nan)
    return out
def fmt(o): return " · ".join(("—" if not np.isfinite(v) else (f"{v:.0f}" if i < 2 else f"{v:+.2f}")) for i, v in enumerate(o))
def gecti(o): s, d = o[DON[0][0]], o[DON[1][0]]; return bool(s[0] >= 10 and s[2] > 0 and d[0] >= 15 and d[2] > 0 and d[3] > 0)
yaz("## 1. Havuz (tüm coin'ler birlikte) · işlem · isabet % · işlem başı net % · alt sınır %")
HV = []
for k, (fn, yon) in KUR.items():
    for H in (4, 8, 24):
        net = pd.concat([net_ser(D, fn(D.z).fillna(False), yon, H) for D in V.values()]).sort_index(); o = ozet(net)
        HV.append(dict(kural=k, saat=H, **{pn: fmt(o[pn]) for pn, _ in DON}, karar="✅" if gecti(o) else "❌"))
yaz("```\n" + pd.DataFrame(HV).set_index(["kural", "saat"]).to_string() + "\n```")
yaz("\n## 2. Coin başına")
rows, rng, pl_ok, pl_n = [], np.random.default_rng(0), 0, 0
for nm, D in V.items():
    for k, (fn, yon) in KUR.items():
        m = fn(D.z).fillna(False)
        for H in (4, 8, 24):
            o = ozet(net_ser(D, m, yon, H))
            rows.append(dict(coin=nm, kural=k.split(" ")[0], saat=H, **{pn: fmt(o[pn]) for pn, _ in DON}, ok=gecti(o),
                             n24=o[DON[1][0]][0], is24=o[DON[1][0]][1], net24=o[DON[1][0]][2], alt24=o[DON[1][0]][3], n26=o["2026"][0], is26=o["2026"][1], net26=o["2026"][2]))
            for _ in range(5):
                if len(m) < 3000: break
                sh = int(rng.integers(500, len(m) - 500)); pm = pd.Series(np.roll(m.values, sh), index=m.index)
                po = ozet(net_ser(D, pm, yon, H), reps=200)
                if po[DON[0][0]][0] >= 10: pl_n += 1; pl_ok += gecti(po)
R = pd.DataFrame(rows); R.to_csv("prim_coin_tum.csv", index=False)
yaz(f"Toplam {len(R)} deneme · ✅ geçen **{int(R.ok.sum())}** · plasebo geçme oranı %{100*pl_ok/max(1,pl_n):.1f} → tesadüfen beklenen ≈ **{pl_ok/max(1,pl_n)*len(R):.1f}**")
yaz("### ✅ Geçenler\n```\n" + (R[R.ok][["coin", "kural", "saat"] + [pn for pn, _ in DON]].to_string(index=False) if R.ok.any() else "(yok)") + "\n```")
for kk in ("AL2", "AL3", "SAT2"):
    G = R[(R.kural == kk) & (R.saat == 24)].sort_values("net24", ascending=False)
    yaz(f"### {kk} · 24 saat (doğrulama netine göre)\n```\n" + G[["coin"] + [pn for pn, _ in DON] + ["ok"]].assign(ok=G.ok.map({True: "✅", False: "❌"})).to_string(index=False) + "\n```")
yaz("\n## Şu an\n" + " · ".join(f"{nm} z {D.z.dropna().iloc[-1]:+.1f}" for nm, D in V.items() if D.z.notna().any()))
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("prim_coin_sonuc.md", "w").write("\n".join(L) + "\n")
