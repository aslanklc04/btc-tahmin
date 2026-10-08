# kucuk_coin.py — 🧑 "BTC'de küçük yatırımcı kaçıyor" sinyali (1 BTC'den küçük cüzdanlardaki BTC 30 g z ≤ −1,5) TÜM COİNLERDE işe yarıyor mu?
# (Coin'lerin kendi küçük cüzdan verisi ücretsiz yok → BTC'nin sinyaliyle diğer coin'ler alınır.)
# Veri: veri_bgeo/coins-addr-1-BTC.json (önbellek, API çağrısı yok) + Binance günlük mumlar (tüm USDT coin'leri).
# Giriş: veri günü d → d+1 kapanışı (BTC'de TR 15:00 girişle aynı sonucu vermişti), 3 / 7 gün tut, limit komisyon %0,02 × 2. Ara düşüş: günlük en düşükten.
# Dönemler (tipler2/3 ile aynı): seçim → 2024-09 · doğrulama 2024-10 → · 2026 ayrıca.
# Önceden sabit karar (coin başına): seçimde net > 0 · doğrulamada ≥ 8 işlem, net > 0, %90 alt sınır > 0 → ✅.
# Ayrıca "fazla" = sinyal günlerindeki getiri − aynı dönemde rastgele günlerin ortalaması (yükseliş piyasasında her AL kazandırır; fazla bunu ayıklar).
import json, time, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
j = json.load(open("veri_bgeo/coins-addr-1-BTC.json")); d = pd.DataFrame(j); d.index = pd.to_datetime(d.pop("d"), utc=True).dt.floor("D")
sm = d.drop(columns=[c for c in d.columns if "ts" in c.lower() or "unix" in c.lower()]).apply(pd.to_numeric, errors="coerce").iloc[:, 0].dropna().sort_index()
sm = sm[~sm.index.duplicated()].asfreq("D")
def zs(s, n=90): return (s - s.rolling(n, min_periods=30).mean()) / (s.rolling(n, min_periods=30).std() + 1e-12)
z = zs(np.log(sm).diff(30)); ix = z.index
S = requests.Session()
def get(url, **p):
    for k in range(4):
        try:
            r = S.get(url, params=p, timeout=30)
            if r.status_code == 200: return r.json()
            if r.status_code in (400, 404): return None
        except Exception: pass
        time.sleep(1 + 2 * k)
    return None
INFO = get("https://data-api.binance.vision/api/v3/exchangeInfo") or get("https://api.binance.com/api/v3/exchangeInfo")
SY = [s for s in INFO["symbols"] if s["quoteAsset"] == "USDT"]; BASE = {s["symbol"]: s["baseAsset"] for s in SY}; DUR = {s["symbol"]: s["status"] for s in SY}
ITIBARI = set("EUR GBP AUD TRY BRL RUB UAH NGN ZAR BIDR IDRT BVND USDC BUSD TUSD USDP FDUSD DAI PAX UST USDS USDSB SUSD AEUR EURI XUSD USD1 RLUSD BFUSD U USDE PAXG XAUT".split())
def gunluk(sym):
    rows, cur = [], int(pd.Timestamp("2022-06-01", tz="UTC").timestamp() * 1000)
    while True:
        r = get(EP[0], symbol=sym, interval="1d", startTime=cur, limit=1000)
        if not r: break
        rows += r; cur = r[-1][0] + 86_400_000
        if len(r) < 1000: break
    if len(rows) < 300: return sym, None
    x = pd.DataFrame([[r_[0], r_[3], r_[4], r_[7]] for r_ in rows], columns=["t", "l", "c", "q"]).astype(float); x.index = pd.to_datetime(x.t, unit="ms", utc=True)
    return sym, x[["l", "c", "q"]]
semboller = [s["symbol"] for s in SY if BASE[s["symbol"]] not in ITIBARI and not any(BASE[s["symbol"]].endswith(k) for k in ("UP", "DOWN", "BULL", "BEAR"))]
with ThreadPoolExecutor(10) as ex: PX = {BASE[k]: v for k, v in ex.map(gunluk, semboller) if v is not None}
SEC_END, A26, LMT = pd.Timestamp("2024-10-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC"), 0.0002
DON = (("seçim", lambda i: i < SEC_END), ("doğrulama", lambda i: i >= SEC_END), ("2026", lambda i: i >= A26))
yaz(f"# 🧑 'BTC'de küçük yatırımcı kaçıyor' sinyali tüm coin'lerde — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n"
    f"Sinyal verisi {sm.index[0]:%Y-%m-%d} → {sm.index[-1]:%Y-%m-%d} · coin: {len(PX)} (en az 300 günlük, stabil/itibari/kaldıraçlı hariç) · {time.time()-T0:.0f} sn\n")
def coin_test(x, HD):
    c = x.c.reindex(ix); lo = x.l.reindex(ix)
    y = c.shift(-(1 + HD)) / c.shift(-1) - 1                                                          # d+1 kapanışında gir, HD gün tut
    mae = pd.concat([lo.shift(-(1 + k)) for k in range(1, HD + 1)], axis=1).min(axis=1) / c.shift(-1) - 1
    ev = ix[events((z <= -1.5).fillna(False).values, HD)]; e = pd.DataFrame({"y": y.reindex(ev), "mae": mae.reindex(ev)}).dropna()
    out = {}
    for pn, f in DON:
        ee = e[f(e.index)]; base = y[f(y.index)].dropna()
        net = ee.y - 2 * LMT
        out[pn] = dict(n=len(ee), isabet=100 * (net > 0).mean() if len(ee) else np.nan, net=100 * net.mean() if len(ee) else np.nan,
                       alt=100 * wboot(net.values, net.index.values)[0] if len(ee) >= 8 else np.nan, fazla=100 * (ee.y.mean() - base.mean()) if len(ee) and len(base) else np.nan,
                       mae=100 * ee.mae.min() if len(ee) else np.nan)
    return out
R = []
for nm, x in PX.items():
    for HD in (3, 7):
        o = coin_test(x, HD)
        if o["seçim"]["n"] < 8 or o["doğrulama"]["n"] < 8: continue
        ok = o["seçim"]["net"] > 0 and o["doğrulama"]["net"] > 0 and o["doğrulama"]["alt"] > 0
        R.append(dict(coin=nm, gun=HD, **{f"{pn}_{k}": v for pn in ("seçim", "doğrulama", "2026") for k, v in o[pn].items()}, ok=ok,
                      hacim=x.q[x.index >= A26].mean() if (x.index >= A26).any() else 0))
R = pd.DataFrame(R)
yaz(f"Test edilen coin (her iki dönemde ≥ 8 işlem): 7 gün {int((R.gun==7).sum())} · 3 gün {int((R.gun==3).sum())} · {time.time()-T0:.0f} sn\n")
def satir(r): return (f"| {r.coin} | {int(r['seçim_n'])} · %{r['seçim_isabet']:.0f} · {r['seçim_net']:+.2f} | {int(r['doğrulama_n'])} · %{r['doğrulama_isabet']:.0f} · **{r['doğrulama_net']:+.2f}** (alt {r['doğrulama_alt']:+.2f}) | "
                      f"{r['doğrulama_fazla']:+.2f} | " + (f"{int(r['2026_n'])} · %{r['2026_isabet']:.0f} · {r['2026_net']:+.2f}" if r["2026_n"] else "—") + f" | {r['doğrulama_mae']:.0f} | {'✅' if r.ok else '❌'} |")
BAS = "| Coin | Seçim: işlem · isabet · net % | Doğrulama: işlem · isabet · net % | Doğrulama fazla % | 2026 | En kötü ara düşüş % | Karar |\n|---|---|---|---|---|---|---|"
for HD in (7, 3):
    G = R[R.gun == HD]
    if G.empty: continue
    btc = G[G.coin == "BTC"]
    yaz(f"## {HD} gün tut\n### Genel tablo\n- Coin sayısı {len(G)} · ✅ geçen **{int(G.ok.sum())}** (%{100*G.ok.mean():.0f})\n"
        f"- Doğrulamada: net > 0 olan coin %{100*(G['doğrulama_net']>0).mean():.0f} · medyan net %{G['doğrulama_net'].median():+.2f} · medyan fazla (rastgele güne göre) %{G['doğrulama_fazla'].median():+.2f}\n"
        f"- Seçimde: medyan net %{G['seçim_net'].median():+.2f} · medyan fazla %{G['seçim_fazla'].median():+.2f}\n"
        + (f"- BTC kendisi: doğrulama net %{btc['doğrulama_net'].iloc[0]:+.2f}, fazla %{btc['doğrulama_fazla'].iloc[0]:+.2f} · BTC'den yüksek doğrulama neti olan coin: %{100*(G['doğrulama_net']>btc['doğrulama_net'].iloc[0]).mean():.0f}\n" if len(btc) else ""))
    SIS = [l.strip().replace("USDT", "") for l in open("durum/coin_listesi.txt") if l.strip()]
    one = list(dict.fromkeys(["BTC", "ETH", "SOL", "XRP", "BNB"] + SIS))
    yaz(f"### Büyük coin'ler + sistemdeki coin'ler\n{BAS}\n" + "\n".join(satir(r) for _, r in G.set_index("coin").reindex(one).dropna(subset=["gun"]).reset_index().iterrows()))
    top = G.sort_values("hacim", ascending=False).head(30)
    yaz(f"\n### 2026'da en çok işlem gören 30 coin\n{BAS}\n" + "\n".join(satir(r) for _, r in top.iterrows()))
    yaz(f"\n### ✅ Geçen tüm coin'ler (doğrulama netine göre)\n{BAS}\n" + "\n".join(satir(r) for _, r in G[G.ok].sort_values("doğrulama_net", ascending=False).iterrows()))
yaz(f"\nŞu an: küçük cüzdan z {z.dropna().iloc[-1]:+.2f} (veri günü {z.dropna().index[-1]:%d.%m}) · _Süre: {time.time()-T0:.0f} sn_")
open("kucuk_coin_sonuc.md", "w").write("\n".join(L) + "\n")
