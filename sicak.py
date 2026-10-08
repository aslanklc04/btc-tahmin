# sicak.py — KULLANICININ FİKİRLERİ (yalnız test; canlıya dokunmaz):
#  H1 SICAK PARA: borsalara giren stabil coin (USDT/USDC) çıkandan olağandışı fazla → BTC / ETH yükselir mi? (Coin Metrics ücretsiz: FlowInExNtv − FlowOutExNtv, günlük; z son 90 gün)
#  H2 ALIM PATLAMASI: son saatte piyasa alışı (taker buy, $) son 30 günün saatlik medyanının ≥ 2× / 3× ve alış payı ≥ %55 → AL
#  H3 BÜYÜK ALIM EMİRLERİ ("normalde 1 TL'lik alım, bugün 2–3 TL"): son 4 saatte ortalama işlem büyüklüğü ($/işlem) normalin ≥ 2× / 3× ve alış payı ≥ %52 → AL
#  H3g aynısı GÜNLÜK (gün sonu, 1 / 3 gün tut) · H4 KATLANARAK ARTAN ALIM: piyasa alışı 3 saat üst üste artıyor, son saat ≥ 2× normal, alış payı ≥ %55 → AL
# Veri: Binance spot saatlik mum (işlem sayısı ve taker-buy hacmi dahil), ~20 coin, 2020+. Giriş: sinyal saatinin (gününün) kapanışı · tutma süresince tekrar yok · limit komisyon %0,02 × 2.
# ÖNCEDEN KARAR (her fikir × süre, coin'ler birlikte): seçim (≤2023) ≥ 30 olay ve net > 0 · 2024+ ≥ 30 olay, net > 0, haftalık blok %5 alt sınır > 0 · 2026 net ≥ 0 (≥ 10 olay varsa).
#   Plasebo (sinyal zamanda kaydırılmış) ile tesadüfen geçme oranı.
import os, time, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
COINS = ["BTC", "ETH", "BNB", "SOL", "XRP", "DOGE", "ADA", "AVAX", "LINK", "DOT", "NEAR", "SHIB", "PEPE", "SUI", "APT", "ARB", "OP", "FLOKI", "UNI", "AAVE"]
def kl(nm):
    end = int(time.time() * 1000); rows, cur = [], int(pd.Timestamp("2019-12-01", tz="UTC").timestamp() * 1000)
    for url in EP:
        try:
            rows, cur = [], int(pd.Timestamp("2019-12-01", tz="UTC").timestamp() * 1000)
            while cur < end:
                r = requests.get(url, params=dict(symbol=f"{nm}USDT", interval="1h", startTime=cur, endTime=end, limit=1000), timeout=20); r.raise_for_status(); dt = r.json()
                if not dt: break
                rows += dt; cur = dt[-1][0] + 3_600_000
                if len(dt) < 1000: break
            if rows: break
        except Exception: rows = []
    if not rows: return nm, None
    d = pd.DataFrame([[x[0], x[4], x[7], x[8], x[10]] for x in rows], columns=["t", "c", "qv", "n", "tbq"]).astype(float)
    d.index = pd.to_datetime(d.t, unit="ms", utc=True) + pd.Timedelta(hours=1); d = d[~d.index.duplicated()].sort_index()
    d = d.reindex(pd.date_range(d.index[0], d.index[-1], freq="1h", tz="UTC")); d = d[d.index <= pd.Timestamp.now(tz="UTC")]
    return nm, d.drop(columns="t")
with ThreadPoolExecutor(6) as ex: K = {k: v for k, v in ex.map(kl, COINS) if v is not None and len(v) > 5000}
yaz(f"# 💸 Sıcak para ve alım büyüklüğü fikirleri — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nSpot veri: {len(K)} coin ({', '.join(K)}) · {time.time()-T0:.0f} sn")
LMT = 0.0002; A24, A26 = pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")
med = lambda s, n=720: s.rolling(n, min_periods=168).median().shift(1)                       # yalnız geçmiş
SIN = {}                                                                                         # ad → {coin: bool Series (saatlik)}
for nm, d in K.items():
    qv, n, tb = d.qv, d.n, d.tbq; pay = tb / qv.replace(0, np.nan)
    tb_k = tb / med(tb)
    ats4 = qv.rolling(4).sum() / n.rolling(4).sum(); ats_k = ats4 / med(qv / n.replace(0, np.nan)); pay4 = tb.rolling(4).sum() / qv.rolling(4).sum()
    for k in (2, 3):
        SIN.setdefault(f"H2 alım patlaması ≥{k}× · alış payı ≥ %55", {})[nm] = (tb_k >= k) & (pay >= 0.55)
        SIN.setdefault(f"H3 büyük alım emirleri (4 s ort. işlem ≥{k}×) · alış payı ≥ %52", {})[nm] = (ats_k >= k) & (pay4 >= 0.52)
    SIN.setdefault("H4 katlanarak artan alım (3 saat üst üste, son ≥2×) · alış payı ≥ %55", {})[nm] = (tb > tb.shift(1)) & (tb.shift(1) > tb.shift(2)) & (tb_k >= 2) & (pay >= 0.55)
def test(ad, sinyal, HS, fiyat, gunluk=False):
    sonuc = []
    for H in HS:
        parca = []
        for nm, m in sinyal.items():
            c = fiyat[nm]; m = m.reindex(c.index).fillna(False).values.astype(bool); ev = events(m, H)
            y = c.shift(-H) / c - 1; x = (y.iloc[ev] - 2 * LMT).dropna(); parca.append(pd.DataFrame({"coin": nm, "net": x.values}, index=x.index))
        X = pd.concat(parca).sort_index() if parca else pd.DataFrame(columns=["coin", "net"])
        o = {}
        for dn, a, b in (("≤2023", None, A24), ("2024+", A24, None), ("2026", A26, None)):
            x = X[((X.index >= a) if a is not None else True) & ((X.index < b) if b is not None else True)].net
            o[dn] = (len(x), 100 * (x > 0).mean() if len(x) else np.nan, 100 * x.mean() if len(x) else np.nan, 100 * wboot(x.values, x.index.values, 600)[0] if len(x) >= 8 else np.nan)
        ok = o["≤2023"][0] >= 30 and o["≤2023"][2] > 0 and o["2024+"][0] >= 30 and o["2024+"][2] > 0 and o["2024+"][3] > 0 and (o["2026"][0] < 10 or o["2026"][2] >= 0)
        hf = (X.index.max() - A24).days / 7 if len(X) else 1
        sonuc.append(dict(fikir=ad, sure=f"{H // 24} gün" if gunluk else f"{H} s", **{dn: (f"{v[0]} · %{v[1]:.0f} · {v[2]:+.2f} · alt {v[3]:+.2f}" if v[0] else "—") for dn, v in o.items()},
                          haftada=round(len(X[X.index >= A24]) / hf, 1), gecti="✅" if ok else "❌", _ok=ok))
    return sonuc
FY = {nm: d.c for nm, d in K.items()}
R = []
for ad, s in SIN.items(): R += test(ad, s, (4, 8, 24), FY)
# ---- H3g günlük ----
G, SG = {}, {}
for nm, d in K.items():
    g = d.resample("1D", label="right", closed="right").agg({"c": "last", "qv": "sum", "n": "sum", "tbq": "sum"}); G[nm] = g.c
    ats = g.qv / g.n.replace(0, np.nan); r = ats / ats.rolling(30, min_periods=10).median().shift(1); pay = g.tbq / g.qv.replace(0, np.nan)
    for k in (2, 3): SG.setdefault(f"H3g günlük büyük alım emirleri (ort. işlem ≥{k}×) · alış payı ≥ %52", {})[nm] = (r >= k) & (pay >= 0.52)
for ad, s in SG.items(): R += test(ad, s, (1, 3), G, gunluk=True)
# ---- H1 sıcak para (Coin Metrics, stabil coin borsa akışı) ----
CM = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
def cm(asset):
    rows, url, p = [], CM, dict(assets=asset, metrics="FlowInExNtv,FlowOutExNtv", frequency="1d", page_size=10000, start_time="2019-12-01")
    for _ in range(10):
        for k in range(4):
            r = requests.get(url, params=p, timeout=60)
            if r.status_code == 429: time.sleep(3 * (k + 1)); continue
            break
        if r.status_code != 200: print("cm", asset, r.status_code, r.text[:150]); return None
        j = r.json(); rows += j.get("data", []); url = j.get("next_page_url"); p = None
        if not url: break
    if not rows: return None
    d = pd.DataFrame(rows); d.index = pd.to_datetime(d.time, utc=True)
    return (pd.to_numeric(d.FlowInExNtv, errors="coerce") - pd.to_numeric(d.FlowOutExNtv, errors="coerce")).rename(asset)
ST = [s for s in (cm(a) for a in ("usdt_eth", "usdt_trx", "usdc", "usdt", "usdc_eth")) if s is not None]
if ST:
    net = pd.concat(ST, axis=1).sum(axis=1, min_count=1).dropna(); net.index = net.index + pd.Timedelta(days=2)   # D günü verisi D+1 sabahı yayımlanır → temkinli: D+1 gün kapanışında giriş
    z1 = (net - net.rolling(90, min_periods=30).mean()) / (net.rolling(90, min_periods=30).std() + 1e-9); s7 = net.rolling(7).sum(); z7 = (s7 - s7.rolling(90, min_periods=30).mean()) / (s7.rolling(90, min_periods=30).std() + 1e-9)
    yaz(f"Stabil coin borsa akışı: {', '.join(s.name for s in ST)} · {net.index[0]:%Y-%m-%d} → {net.index[-1]:%Y-%m-%d} · son gün net {net.iloc[-1]/1e6:+,.0f} milyon $ (z {z1.iloc[-1]:+.1f})")
    for ad, m in (("H1 sıcak para: günlük stabil coin net girişi z ≥ 1,5", z1 >= 1.5), ("H1 sıcak para: 7 günlük net giriş z ≥ 1,5", z7 >= 1.5)):
        for coin in ("BTC", "ETH"):
            if coin in G: R += test(f"{ad} → {coin}", {coin: m}, (1, 3, 7), {coin: G[coin]}, gunluk=True)
        R += test(f"{ad} → tüm coin'ler", {nm: m for nm in G}, (1, 3, 7), G, gunluk=True)
else: yaz("_Coin Metrics ücretsiz sürümünde stabil coin borsa akışı alınamadı → H1 test edilemedi_")
T = pd.DataFrame(R)
# ---- plasebo ----
rng = np.random.default_rng(0); pl, pn = 0, 0
for ad, s in list(SIN.items()):
    for _ in range(4):
        sh = {nm: pd.Series(np.roll(m.values, int(rng.integers(500, len(m) - 500))), index=m.index) for nm, m in s.items()}
        for r in test(ad, sh, (4, 8, 24), FY): pn += 1; pl += r["_ok"]
yaz(f"\n## Sonuç — {int(T._ok.sum())} / {len(T)} deneme geçti · plasebo geçme oranı %{100*pl/max(1,pn):.1f} → tesadüfen ≈ {pl/max(1,pn)*len(T):.1f}\n_olay · isabet · işlem başı net % · haftalık blok %5 alt sınır_\n```\n"
    + T.drop(columns="_ok").to_string(index=False) + "\n```")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("sicak_sonuc.md", "w").write("\n".join(L) + "\n")
