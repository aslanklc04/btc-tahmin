# zincir2.py — ARZ / TALEP birlikte: coin'ler borsadan çıkıyor (arz azalıyor) VE stabil coin arzı artıyor (piyasaya yeni para, talep) → yükseliş?
# Talep: DefiLlama toplam stabil coin arzı (USD, günlük; ücretsiz) — 7 ve 30 günlük % değişim. Arz: Coin Metrics borsa giriş/çıkışı (zincir.py ile aynı).
# Gecikme: gün d verisi → gün d+1 kapanışında işlem (temkinli), 3 ve 7 gün tut, limit komisyon %0,02×2. z: son 90 güne göre.
# Önceden sabit kurallar:
#   AL-1 (kullanıcının fikri): arz çıkıyor (7 g net borsa çıkışı z ≥ +1) VE talep artıyor (stabil coin 7 g büyüme z ≥ +1)
#   AL-2: borsadaki miktar 30 g azalıyor (z ≥ +1) VE stabil coin 30 g büyüme z ≥ +1
#   AL-3: yalnız talep: stabil coin 7 g büyüme z ≥ +1,5
#   SAT-1: coin'ler borsaya akıyor (7 g net GİRİŞ z ≥ +1,5) VE talep zayıf (stabil coin 7 g büyüme z ≤ 0)
#   SAT-2: yalnız coin'ler borsaya akıyor (7 g net giriş z ≥ +1,5)
# Karar: ≤2023'te net > 0, 2024+'da net > 0 ve %90 alt sınır > 0 → ✅ (2026 ayrıca).
import time, requests, numpy as np, pandas as pd
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
z1 = open("zincir.py").read(); exec(z1[z1.index('CM = "https'):z1.index('M = ["FlowInExNtv"')])         # cm(), gunluk()
def stabil():
    for url in ("https://stablecoins.llama.fi/stablecoincharts/all", "https://stablecoins.llama.fi/stablecoincharts/all?stablecoin=1"):
        try:
            j = requests.get(url, timeout=60).json()
            s = pd.Series({pd.Timestamp(int(x["date"]), unit="s", tz="UTC").floor("D"): float((x.get("totalCirculatingUSD") or x.get("totalCirculating") or {}).get("peggedUSD", np.nan)) for x in j})
            if s.notna().sum() > 500: return s.sort_index()
        except Exception as e: yaz(f"_DefiLlama {url}: {type(e).__name__} {str(e)[:100]}_")
    return None
SC = stabil(); D = {a: cm(a, ["FlowInExNtv", "FlowOutExNtv", "SplyExNtv"]) for a in ("btc", "eth")}; PX = {"btc": gunluk("BTCUSDT"), "eth": gunluk("ETHUSDT")}
yaz(f"# ⛓️💵 Arz + talep birlikte — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nStabil coin arzı: {'yok' if SC is None else f'{SC.index[0]:%Y-%m} → {SC.index[-1]:%Y-%m-%d}, son {SC.iloc[-1]/1e9:,.0f} milyar $'} · Coin Metrics BTC/ETH · {time.time()-T0:.0f} sn\n")
def zs(s, n=90): return (s - s.rolling(n, min_periods=30).mean()) / (s.rolling(n, min_periods=30).std() + 1e-12)
A24, A26, LMT = pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC"), 0.0002
KAR = []
for a in ("btc", "eth"):
    d, px = D[a], PX[a]; ix = d.index.intersection(px.index); d, px = d.reindex(ix), px.reindex(ix); sc = SC.reindex(ix).ffill(limit=3)
    cik7 = zs(-(d.FlowInExNtv - d.FlowOutExNtv).rolling(7).sum() / d.SplyExNtv); ms30 = zs(-np.log(d.SplyExNtv / d.SplyExNtv.shift(30)))
    t7, t30 = zs(np.log(sc / sc.shift(7))), zs(np.log(sc / sc.shift(30)))
    K = {"AL-1 arz çıkıyor + talep artıyor (7 g)": ((cik7 >= 1) & (t7 >= 1), 1), "AL-2 borsadaki miktar azalıyor + stabil coin 30 g büyüyor": ((ms30 >= 1) & (t30 >= 1), 1),
         "AL-3 yalnız talep: stabil coin 7 g büyüme z ≥ 1,5": (t7 >= 1.5, 1), "SAT-1 coin'ler borsaya akıyor + talep zayıf": ((cik7 <= -1.5) & (t7 <= 0), -1), "SAT-2 yalnız coin'ler borsaya akıyor": (cik7 <= -1.5, -1)}
    yaz(f"## {a.upper()} · talep ölçüsünün tek başına etkisi (stabil coin 7 g büyüme z dilimleri → sonraki 7 gün, tabana göre fazla %)")
    y7 = np.log(px.shift(-8) / px.shift(-1)); x = pd.DataFrame({"z": t7, "y": y7}).dropna(); rows = []
    for pn, m in (("≤2023", x.index < A24), ("2024+", x.index >= A24), ("2026", x.index >= A26)):
        xx = x[m]; b = xx.y.mean(); rows.append({"dönem": pn, **{lab: 100 * (xx[c].y.mean() - b) for lab, c in (("z ≤ −1", xx.z <= -1), ("−1…0", (xx.z > -1) & (xx.z <= 0)), ("0…1", (xx.z > 0) & (xx.z < 1)), ("z ≥ 1", xx.z >= 1))}, "korelasyon": xx.z.corr(xx.y)})
    yaz("```\n" + pd.DataFrame(rows).set_index("dönem").round(2).to_string() + "\n```")
    out = []
    for HD in (3, 7):
        y = np.log(px.shift(-(1 + HD)) / px.shift(-1))
        for k, (m, yon) in K.items():
            ev = m.index[events(m.fillna(False).values, HD)]; E = pd.DataFrame({"y": y.reindex(ev)}).dropna(); E["net"] = yon * (np.exp(E.y) - 1) - 2 * LMT
            for pn, mm in (("≤2023", E.index < A24), ("2024+", E.index >= A24), ("2026", E.index >= A26)):
                e = E[mm]
                if len(e) < 3: continue
                lo, _ = wboot(e.net.values, e.index.values) if len(e) >= 8 else (np.nan, np.nan)
                out.append(dict(kural=k, gun=HD, donem=pn, olay=len(e), isabet=100 * ((yon * e.y) > 0).mean(), net=100 * e.net.mean(), alt=100 * lo))
    O = pd.DataFrame(out); yaz(f"### {a.upper()} kurallar (net = işlem başı %, yön kuralın kendisinde: AL ya da SAT)\n```\n" + O.set_index(["kural", "gun", "donem"]).round(2).to_string() + "\n```")
    for (k, HD), g in O.groupby(["kural", "gun"], sort=False):
        p = g.set_index("donem")
        if not {"≤2023", "2024+"} <= set(p.index): continue
        ok = p.loc["≤2023", "net"] > 0 and p.loc["2024+", "net"] > 0 and p.loc["2024+", "alt"] > 0
        KAR.append(f"- {'✅' if ok else '❌'} {a.upper()} · {k} · {HD} gün: ≤2023 {int(p.loc['≤2023','olay'])} olay net %{p.loc['≤2023','net']:+.2f} · 2024+ {int(p.loc['2024+','olay'])} olay, isabet %{p.loc['2024+','isabet']:.0f}, net %{p.loc['2024+','net']:+.2f} (alt %{p.loc['2024+','alt']:+.2f})"
                   + (f" · 2026 {int(p.loc['2026','olay'])} olay net %{p.loc['2026','net']:+.2f}" if "2026" in p.index else ""))
    son = pd.DataFrame({"arz çıkışı z": cik7, "borsadaki miktar azalışı z": ms30, "talep 7g z": t7, "talep 30g z": t30}).dropna().iloc[-1]
    yaz(f"Şu an ({a.upper()}): " + " · ".join(f"{k} {v:+.2f}" for k, v in son.items()) + "\n")
yaz("## Karar (önceden sabit: ≤2023 net > 0 · 2024+ net > 0 ve alt > 0)\n" + "\n".join(KAR) + f"\n\n_Süre: {time.time()-T0:.0f} sn_")
open("zincir2_sonuc.md", "w").write("\n".join(L) + "\n")
