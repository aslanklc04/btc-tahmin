# zincir.py — ARZ / TALEP (zincir üstü): coin'ler borsadan soğuk cüzdana çıkıyor (arz azalıyor), stabil coin borsaya giriyor (talep artıyor) → fiyat yükselir mi?
# Veri: Coin Metrics topluluk API'si (ücretsiz, günlük): borsaya giriş/çıkış (FlowInExNtv/FlowOutExNtv), borsalardaki toplam (SplyExNtv) — BTC, ETH, USDT, USDC.
# Gecikme: gün d'nin verisi ertesi gün yayımlanır → işlem gün d+1 KAPANIŞINDA açılır (temkinli: 1 gün gecikme), 1 / 3 / 7 gün tutulur.
# Ölçüler (son 90 güne göre z): arz çıkışı = −(7 günlük net akış / borsadaki miktar) · borsadaki miktarın 30 günlük değişimi · stabil coin talebi = USDT+USDC 7 günlük net borsa girişi (USD)
# Kullanıcının koşulu (önceden sabit): ARZ ÇIKIYOR (BTC 7 g net çıkış z ≥ +1) VE TALEP ARTIYOR (stabil coin 7 g net giriş z ≥ +1) → AL.
# Karar: ≤2023'te ve 2024+'da yön aynı, 2024+ net > 0 ve %90 alt sınır > 0 → ✅ (komisyon: limit %0,02×2).
import time, requests, numpy as np, pandas as pd
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
CM = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
def cm(asset, metrics):
    rows, url, params = [], CM, dict(assets=asset, metrics=",".join(metrics), frequency="1d", start_time="2016-01-01", page_size=10000)
    for _ in range(50):
        for k in range(5):
            r = requests.get(url, params=params, timeout=60)
            if r.status_code == 429: time.sleep(3 * (k + 1)); continue
            break
        if r.status_code != 200: yaz(f"_Coin Metrics {asset} {metrics}: HTTP {r.status_code} {r.text[:150]}_"); return None
        j = r.json(); rows += j.get("data", []); url = j.get("next_page_url"); params = None
        if not url: break
        time.sleep(0.7)
    if not rows: return None
    d = pd.DataFrame(rows); d.index = pd.to_datetime(d.time, utc=True).dt.floor("D"); return d.drop(columns=["asset", "time"]).apply(pd.to_numeric, errors="coerce").sort_index()
def gunluk(sym):
    rows, cur, end = [], int(pd.Timestamp("2017-08-17", tz="UTC").timestamp() * 1000), int(time.time() * 1000)
    while cur < end:
        r = requests.get(EP[0], params=dict(symbol=sym, interval="1d", startTime=cur, limit=1000), timeout=20).json()
        if not r: break
        rows += r; cur = r[-1][0] + 86_400_000
        if len(r) < 1000: break
    d = pd.DataFrame([x[:5] for x in rows], columns=["t", "o", "h", "l", "c"]).astype(float); return pd.Series(d.c.values, index=pd.to_datetime(d.t, unit="ms", utc=True))      # gün d'nin kapanışı
M = ["FlowInExNtv", "FlowOutExNtv", "SplyExNtv"]
D = {a: cm(a, M) for a in ("btc", "eth")}; ST = {a: cm(a, ["FlowInExUSD", "FlowOutExUSD"]) for a in ("usdt", "usdc")}
if ST["usdt"] is None: ST = {a: cm(a, ["FlowInExNtv", "FlowOutExNtv"]) for a in ("usdt", "usdc")}
PX = {"btc": gunluk("BTCUSDT"), "eth": gunluk("ETHUSDT")}
yaz(f"# ⛓️ Arz/talep (zincir üstü) — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nVeri: " + " · ".join(f"{k.upper()} {('yok' if v is None else f'{v.index[0]:%Y-%m}→{v.index[-1]:%Y-%m-%d}')}" for k, v in {**D, **ST}.items()) + f" · {time.time()-T0:.0f} sn\n")
def zs(s, n=90): return (s - s.rolling(n, min_periods=30).mean()) / (s.rolling(n, min_periods=30).std() + 1e-12)
stab = None
for a, d in ST.items():
    if d is None: continue
    cols = [c for c in d.columns if c.startswith("FlowIn")], [c for c in d.columns if c.startswith("FlowOut")]
    net = d[cols[0][0]] - d[cols[1][0]]; stab = net if stab is None else stab.add(net, fill_value=0)
A24, A26, LMT = pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC"), 0.0002
KAR = []
for a in ("btc", "eth"):
    d, px = D[a], PX[a]
    if d is None: continue
    ix = d.index.intersection(px.index); d, px = d.reindex(ix), px.reindex(ix)
    net7 = (d.FlowInExNtv - d.FlowOutExNtv).rolling(7).sum()
    F = {"Arz çıkışı: 7 g net borsa ÇIKIŞI / borsadaki miktar": -net7 / d.SplyExNtv, "Borsadaki miktar 30 g değişimi (düşüş = arz azalıyor)": -np.log(d.SplyExNtv / d.SplyExNtv.shift(30)),
         "Arz çıkışı: 1 g net çıkış / borsadaki miktar": -(d.FlowInExNtv - d.FlowOutExNtv) / d.SplyExNtv}
    if stab is not None: F["Talep: stabil coin 7 g net borsa GİRİŞİ"] = stab.reindex(ix).rolling(7).sum()
    Z = {k: zs(v) for k, v in F.items()}
    if stab is not None: Z["KULLANICI: arz çıkıyor (z ≥ +1) VE talep artıyor (z ≥ +1)"] = ((Z[list(F)[0]] >= 1) & (Z["Talep: stabil coin 7 g net borsa GİRİŞİ"] >= 1)).astype(float) * 3 - 1.5
    yaz(f"## {a.upper()} (pozitif = senin fikrin yönünde: arz borsadan çıkıyor / talep borsaya giriyor)")
    for HD in (1, 3, 7):
        y = np.log(px.shift(-(1 + HD)) / px.shift(-1))                                                       # 1 gün gecikme: gün d+1 kapanışında gir
        rows = []
        for k, z in Z.items():
            x = pd.DataFrame({"z": z, "y": y}).dropna()
            for pn, m in (("≤2023", x.index < A24), ("2024+", x.index >= A24), ("2026", x.index >= A26)):
                xx = x[m]; base = xx.y.mean()
                if len(xx) < 30: continue
                hi = xx[xx.z >= 1.5]; lo = xx[xx.z <= -1.5]
                rows.append(dict(olcu=k[:60], donem=pn, gun=len(xx), **{"yüksek (z ≥ 1,5) fazla %": 100 * (hi.y.mean() - base) if len(hi) >= 5 else np.nan, "yüksek gün": len(hi),
                            "düşük (z ≤ −1,5) fazla %": 100 * (lo.y.mean() - base) if len(lo) >= 5 else np.nan, "korelasyon": xx.z.corr(xx.y)}))
        yaz(f"### Sonraki {HD} gün (yükseliş/düşüş = o gün 'yüksek'/'düşük' iken tabana göre fazla getiri)\n```\n" + pd.DataFrame(rows).set_index(["olcu", "donem"]).round(3).to_string() + "\n```")
    # para testi: yüksek → AL, 3 ve 7 gün (önceden sabit), yön ≤2023'ten
    for HD in (3, 7):
        y = np.log(px.shift(-(1 + HD)) / px.shift(-1))
        for k, z in Z.items():
            ev = z.index[events((z >= 1.5).fillna(False).values, HD)]; E = pd.DataFrame({"y": y.reindex(ev)}).dropna()
            if len(E) < 15: continue
            def per(m): x = E[m]; return x
            e1, e2, e3 = E[E.index < A24], E[E.index >= A24], E[E.index >= A26]
            b1, b2 = y[y.index < A24].mean(), y[y.index >= A24].mean(); f1 = e1.y.mean() - b1 if len(e1) else np.nan; yon = 1 if not np.isfinite(f1) or f1 >= 0 else -1
            net = yon * e2.y.values - 2 * LMT; lo, _ = wboot(net, e2.index.values) if len(e2) >= 8 else (np.nan, np.nan)
            ok = len(e1) >= 10 and len(e2) >= 8 and np.sign(e2.y.mean() - b2) == yon and net.mean() > 0 and lo > 0
            KAR.append(f"- {'✅' if ok else '❌'} {a.upper()} · {k[:70]} · {HD} gün: ≤2023 {len(e1)} olay, fazla %{100*f1:+.2f} → {'AL' if yon > 0 else 'SAT'} · 2024+ {len(e2)} olay, fazla %{100*(e2.y.mean()-b2):+.2f}, net %{100*net.mean():+.2f} (alt %{100*lo:+.2f})"
                       + (f" · 2026 {len(e3)} olay, fazla %{100*(e3.y.mean()-y[y.index>=A26].mean()):+.2f}" if len(e3) else ""))
yaz("\n## Karar (olay: ölçü z ≥ 1,5 · ilk gün, tutma süresince tekrar yok · yön ≤2023'ten · 2024+ aynı yön, net > 0, alt > 0)\n" + "\n".join(KAR))
yaz(f"\n_Süre: {time.time()-T0:.0f} sn · fazla = aynı dönemde rastgele güne göre fark · korelasyon = günlük ölçü ile sonraki getiri arasındaki ilişki (0 = yok)_")
open("zincir_sonuc.md", "w").write("\n".join(L) + "\n")
