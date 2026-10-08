# tipler.py — ZİNCİR ÜSTÜ YATIRIMCI TİPLERİ: balinalar mı topluyor, küçük yatırımcı mı akın ediyor, eski (uzun vadeli) coin'ler mi uyanıyor, yatırımcılar ne kadar kârda?
# Veri: Coin Metrics topluluk API'si (ücretsiz, günlük). Önce katalogdan hangi ölçülerin ücretsiz olduğu bulunur.
# Zamanlama (zincir2/zincir3 ile aynı): gün d verisi → gün d+1 kapanışında gir, 3 / 7 gün tut, limit komisyon %0,02 × 2. z: son 90 güne göre (MVRV: 365 gün).
# A) ÖNCEDEN SABİT HİPOTEZLER (yön de önceden sabit, 7 gün):
#   H1 Balinalar topluyor: büyük cüzdanların (BTC ≥1000, ETH ≥10 000) arz payı 30 günde artıyor z ≥ 1 → AL · H1b azalıyor z ≤ −1 (dağıtıyor) → SAT
#   H2 Küçük yatırımcı akını (ters gösterge): küçük cüzdan sayısı 30 günde z ≥ 1,5 artıyor → SAT
#   H3 Balina topluyor, küçük yatırımcı satıyor: H1 balina z ≥ 1 VE küçük cüzdan z ≤ 0 → AL
#   H4 Eski coin'ler uyanıyor: 1 yıldan uzun hareketsiz arzın payı 30 günde z ≤ −1,5 düşüyor (uzun vadeliler satıyor) → SAT · H4b z ≥ 1,5 artıyor (kimse satmıyor) → AL
#   H5 Yatırımcılar çok kârda (MVRV z ≥ 1,5) → SAT · H5b çok zararda (z ≤ −1,5) → AL
#   Karar: ≤2023 net > 0 · 2024+ net > 0 ve %90 alt sınır > 0 → ✅
# B) GENİŞ TARAMA: tüm ücretsiz tip ölçüleri × (z ≥ 1,5 / z ≤ −1,5) × 3/7 gün, yön ≤2023'ten; plasebo (sinyal rastgele kaydırılmış) ile "tesadüfen kaç geçerdi".
import re, time, requests, numpy as np, pandas as pd
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
CMB = "https://community-api.coinmetrics.io/v4"
def jget(url, params=None):
    for k in range(6):
        try:
            r = requests.get(url, params=params, timeout=90)
            if r.status_code == 429: time.sleep(3 * (k + 1)); continue
            return r
        except Exception: time.sleep(3)
    return None
def katalog(asset):
    out = set()
    for ep in ("catalog-v2/asset-metrics", "catalog/assets"):
        url, p = f"{CMB}/{ep}", dict(assets=asset, page_size=10000)
        for _ in range(20):
            r = jget(url, p)
            if r is None or r.status_code != 200: break
            j = r.json()
            def walk(o):
                if isinstance(o, dict):
                    if "metric" in o and any(f.get("frequency") == "1d" for f in o.get("frequencies", [{"frequency": "1d"}])): out.add(o["metric"])
                    for v in o.values(): walk(v)
                elif isinstance(o, list):
                    for v in o: walk(v)
            walk(j.get("data", [])); url, p = j.get("next_page_url"), None
            if not url: break
        if out: break
    return out
def cm(asset, metrics):
    rows, url, p = [], f"{CMB}/timeseries/asset-metrics", dict(assets=asset, metrics=",".join(metrics), frequency="1d", start_time="2016-01-01", page_size=10000)
    for _ in range(60):
        r = jget(url, p)
        if r is None or r.status_code != 200: return None
        j = r.json(); rows += j.get("data", []); url, p = j.get("next_page_url"), None
        if not url: break
        time.sleep(0.5)
    if not rows: return None
    d = pd.DataFrame(rows); d.index = pd.to_datetime(d.time, utc=True).dt.floor("D")
    return d[[c for c in metrics if c in d.columns]].apply(pd.to_numeric, errors="coerce").sort_index()
DESEN = re.compile(r"^(AdrBal|SplyAdr|SplyAct|SplyMiner|FlowMiner|CapMVRV|CapReal|RevAll|SER$|VelCur|SplyCur$|AdrActCnt$|NVTAdj$|SplyFF$|SplyExpFut)")
D, KAT = {}, {}
for a in ("btc", "eth"):
    k = katalog(a); KAT[a] = sorted(m for m in k if DESEN.match(m))
    ms, parts = KAT[a] + (["SplyCur"] if "SplyCur" not in KAT[a] else []), []
    for i in range(0, len(ms), 12):
        ch = ms[i:i + 12]; d = cm(a, ch)
        if d is None:                                                                                   # parça başarısızsa tek tek dene
            for m in ch:
                dm = cm(a, [m])
                if dm is not None: parts.append(dm)
        else: parts.append(d)
    D[a] = pd.concat(parts, axis=1) if parts else None
    if D[a] is not None: D[a] = D[a].loc[:, ~D[a].columns.duplicated()]
yaz(f"# 🐋🧑 Zincir üstü yatırımcı tipleri — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}")
for a in D:
    cols = [] if D[a] is None else list(D[a].columns)
    yaz(f"**{a.upper()}** — katalogda tip ölçüsü {len(KAT[a])}, veri gelen {len(cols)}: " + (", ".join(f"`{c}`" for c in cols) if cols else "(yok)"))
def gunluk(sym):
    rows, cur = [], int(pd.Timestamp("2017-08-17", tz="UTC").timestamp() * 1000)
    while True:
        r = requests.get(EP[0], params=dict(symbol=sym, interval="1d", startTime=cur, limit=1000), timeout=20).json()
        if not r: break
        rows += r; cur = r[-1][0] + 86_400_000
        if len(r) < 1000: break
    d = pd.DataFrame([x[:5] for x in rows], columns=["t", "o", "h", "l", "c"]).astype(float); return pd.Series(d.c.values, index=pd.to_datetime(d.t, unit="ms", utc=True))
PX = {"btc": gunluk("BTCUSDT"), "eth": gunluk("ETHUSDT")}
yaz(f"_{time.time()-T0:.0f} sn_\n")
def zs(s, n=90): return (s - s.rolling(n, min_periods=30).mean()) / (s.rolling(n, min_periods=30).std() + 1e-12)
A24, A26, LMT = pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC"), 0.0002
DON = (("≤2023", lambda i: i < A24), ("2024+", lambda i: i >= A24), ("2026", lambda i: i >= A26))
def ilk(d, adaylar): return next((c for c in adaylar if c in d.columns and d[c].notna().sum() > 500), None)
def oz_olcu(d, c):
    """Tip ölçüsünden 30 günlük değişim özelliği: arz → arz payı değişimi, sayı → log değişim, oran → seviye."""
    s = d[c]
    if c.startswith("SplyAdr") or c.startswith("SplyMiner") or c.startswith("SplyAct") or c.startswith("SplyExpFut") or c == "SplyFF":
        sh = s / d["SplyCur"]; return (1 - sh if c.startswith("SplyAct") else sh).diff(30)               # SplyAct → HAREKETSİZ pay
    if c.startswith("CapMVRV") or c in ("SER", "NVTAdj") or c.startswith("VelCur"): return np.log(s.where(s > 0))
    return np.log(s.where(s > 0)).diff(30)
def sonuc(m, px, yon, HD, reps=800):
    y = np.log(px.shift(-(1 + HD)) / px.shift(-1)); ix = m.index
    ev = ix[events(m.reindex(ix).fillna(False).values, HD)]; y = y.reindex(ev).dropna()
    if not len(y): return None
    net = yon * (np.exp(y) - 1) - 2 * LMT; out = {}
    for pn, f in DON:
        e = net[f(net.index)]; out[pn] = (len(e), 100 * (e > 0).mean() if len(e) else np.nan, 100 * e.mean() if len(e) else np.nan, 100 * wboot(e.values, e.index.values, reps)[0] if len(e) >= 8 else np.nan)
    return out
def fmt(o): return " · ".join(("—" if not np.isfinite(v) else (f"{v:.0f}" if i < 2 else f"{v:+.2f}")) for i, v in enumerate(o))
# ---- A) önceden sabit hipotezler ----
yaz("## A) Önceden sabit hipotezler (7 gün tut; yön önceden sabit) — işlem · isabet % · işlem başı net % · alt sınır %")
KAR = []
for a in ("btc", "eth"):
    d = D[a]
    if d is None or "SplyCur" not in d.columns: yaz(f"- {a.upper()}: veri yok"); continue
    px = PX[a]; ix = d.index.intersection(px.index); d, px = d.reindex(ix), px.reindex(ix)
    bal = ilk(d, ["SplyAdrBalNtv1K", "SplyAdrBalNtv10K", "SplyAdrTop100", "SplyAdrTop1Pct", "AdrBalNtv1KCnt"] if a == "btc" else ["SplyAdrBalNtv10K", "SplyAdrBalNtv100K", "SplyAdrTop100", "SplyAdrTop1Pct", "AdrBalNtv10KCnt"])
    kuc = ilk(d, ["AdrBalNtv0.01Cnt", "AdrBalNtv0.1Cnt", "AdrBalUSD100Cnt", "AdrBalUSD1KCnt", "AdrBalNtv0.001Cnt"] if a == "btc" else ["AdrBalNtv0.1Cnt", "AdrBalNtv1Cnt", "AdrBalUSD100Cnt", "AdrBalUSD1KCnt", "AdrBalNtv0.01Cnt"])
    esk = ilk(d, ["SplyAct1yr", "SplyAct2yr", "SplyAct180d"]); mv = ilk(d, ["CapMVRVCur", "CapMVRVFF"])
    yaz(f"### {a.upper()} — balina: `{bal}` · küçük yatırımcı: `{kuc}` · eski coin: `{esk}` (hareketsiz pay) · kârlılık: `{mv}`")
    Z = {}
    if bal: Z["bal"] = zs(oz_olcu(d, bal))
    if kuc: Z["kuc"] = zs(oz_olcu(d, kuc))
    if esk: Z["esk"] = zs(oz_olcu(d, esk))
    if mv: Z["mv"] = zs(oz_olcu(d, mv), 365)
    H = {}
    if "bal" in Z: H["H1 balinalar topluyor → AL"] = (Z["bal"] >= 1, 1); H["H1b balinalar dağıtıyor → SAT"] = (Z["bal"] <= -1, -1)
    if "kuc" in Z: H["H2 küçük yatırımcı akını → SAT"] = (Z["kuc"] >= 1.5, -1)
    if "bal" in Z and "kuc" in Z: H["H3 balina topluyor + küçük satıyor → AL"] = ((Z["bal"] >= 1) & (Z["kuc"] <= 0), 1)
    if "esk" in Z: H["H4 eski coin'ler uyanıyor → SAT"] = (Z["esk"] <= -1.5, -1); H["H4b eski coin'ler kımıldamıyor → AL"] = (Z["esk"] >= 1.5, 1)
    if "mv" in Z: H["H5 yatırımcılar çok kârda → SAT"] = (Z["mv"] >= 1.5, -1); H["H5b yatırımcılar çok zararda → AL"] = (Z["mv"] <= -1.5, 1)
    rows = []
    for k, (m, yon) in H.items():
        for HD in (3, 7):
            o = sonuc(m, px, yon, HD)
            if o is None: continue
            rows.append(dict(hipotez=k, gun=HD, **{pn: fmt(o[pn]) for pn, _ in DON}))
            if HD == 7:
                ok = o["≤2023"][2] > 0 and o["2024+"][0] >= 8 and o["2024+"][2] > 0 and o["2024+"][3] > 0
                KAR.append(f"- {'✅' if ok else '❌'} {a.upper()} · {k} · 7 gün: ≤2023 {fmt(o['≤2023'])} · 2024+ {fmt(o['2024+'])} · 2026 {fmt(o['2026'])}")
    if rows: yaz("```\n" + pd.DataFrame(rows).set_index(["hipotez", "gun"]).to_string() + "\n```")
    son = {k: v.dropna().iloc[-1] for k, v in Z.items() if v.notna().any()}
    yaz("Şu an: " + " · ".join(f"{dict(bal='balina payı', kuc='küçük cüzdan', esk='hareketsiz eski arz', mv='MVRV')[k]} z {v:+.2f}" for k, v in son.items()) + f" (veri günü {Z[next(iter(Z))].dropna().index[-1]:%d.%m})\n")
yaz("### Karar (A)\n" + "\n".join(KAR))
# ---- B) geniş tarama ----
yaz("\n## B) Geniş tarama: tüm ücretsiz tip ölçüleri (yön ≤2023'ten; 2024+ net > 0 ve alt > 0 → ✅)")
res, rng, pl_ok, pl_n = [], np.random.default_rng(0), 0, 0
for a in ("btc", "eth"):
    d = D[a]
    if d is None or "SplyCur" not in d.columns: continue
    px = PX[a]; ix = d.index.intersection(px.index); d, px = d.reindex(ix), px.reindex(ix)
    for c in d.columns:
        if c == "SplyCur" or d[c].notna().sum() < 800: continue
        z = zs(oz_olcu(d, c), 365 if c.startswith("CapMVRV") else 90)
        for sk, m in (("z ≥ 1,5", z >= 1.5), ("z ≤ −1,5", z <= -1.5)):
            for HD in (3, 7):
                y = np.log(px.shift(-(1 + HD)) / px.shift(-1)); ev = ix[events(m.fillna(False).values, HD)]; e1 = y.reindex(ev).dropna(); e1 = e1[e1.index < A24]
                if len(e1) < 15: continue
                yon = 1 if e1.mean() > 0 else -1; o = sonuc(m, px, yon, HD)
                ok = o["≤2023"][2] > 0 and o["2024+"][0] >= 8 and o["2024+"][2] > 0 and o["2024+"][3] > 0
                res.append(dict(coin=a.upper(), olcu=c, sinyal=sk, gun=HD, yon="AL" if yon > 0 else "SAT", **{pn: fmt(o[pn]) for pn, _ in DON}, ok=ok))
                for _ in range(10):
                    sh = int(rng.integers(120, len(m) - 120)); pm = pd.Series(np.roll(m.fillna(False).values, sh), index=m.index)
                    ev = ix[events(pm.values, HD)]; p1 = y.reindex(ev).dropna(); p1 = p1[p1.index < A24]
                    if len(p1) < 15: continue
                    po = sonuc(pm, px, 1 if p1.mean() > 0 else -1, HD, reps=200); pl_n += 1
                    pl_ok += po["≤2023"][2] > 0 and po["2024+"][0] >= 8 and po["2024+"][2] > 0 and po["2024+"][3] > 0
R = pd.DataFrame(res)
if len(R):
    yaz(f"Toplam {len(R)} deneme · ✅ geçen **{int(R.ok.sum())}** · plasebo geçme oranı %{100*pl_ok/max(1,pl_n):.1f} → tesadüfen beklenen ≈ **{pl_ok/max(1,pl_n)*len(R):.1f}**")
    yaz("### ✅ Geçenler\n```\n" + (R[R.ok].drop(columns="ok").to_string(index=False) if R.ok.any() else "(yok)") + "\n```")
    yaz("### Tümü\n```\n" + R.drop(columns="ok").to_string(index=False) + "\n```")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("tipler_sonuc.md", "w").write("\n".join(L) + "\n")
