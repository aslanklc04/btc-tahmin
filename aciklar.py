# aciklar.py — FİYAT BOŞLUKLARI ("açıklar") gerçekten önceden iz bırakıyor mu? (canlı sisteme dokunmaz)
# A) CME HAFTA SONU BOŞLUĞU: CME bitcoin vadelisi cuma 16:00 (Chicago) kapanır, pazar 17:00 açılır; arada spot hareket ederse grafikte boşluk kalır.
#    İddia: "boşluklar dolar" → fiyat cuma kapanışına geri döner. Ölçüm (spot BTC ile, aynı saatlerde): boşluğun dolma oranı vs AYNA seviye
#    (aynı uzaklıkta ters yöndeki seviye) — mıknatıs etkisi varsa boşluk aynadan sık dolmalı. İşlem: pazar açılışından 1 saat sonra boşluk yönüne gir,
#    seviyeye limit çıkış, 72 saatte dolmazsa piyasa emriyle çık. Gerçek CME günlük verisi (Yahoo, BTC=F) de varsa ayrıca bakılır.
# B) ADİL DEĞER BOŞLUĞU (FVG): 3 mumda 1. mumun tepesi ile 3. mumun dibi arasında boşluk (1 saatlik ≥ %0,3 · 4 saatlik ≥ %0,6).
#    İddia: fiyat boşluğa geri döner ve oradan tepki verir. Ölçüm: boşluğun üst sınırına limit alış (48 mum içinde dolarsa), 24 saat sonraki getiri;
#    KONTROL: ±7 gün içinde rastgele bir anda aynı derinlikte limit alış. Düşüş boşluğu (satış) de aynı şekilde.
# Önceden sabit karar: iki dönemde de (≤2023 / 2024+) etki kontroldan iyi VE 2024+ limit-komisyonlu net > 0 ve %90 alt sınırı > 0.
import os, time, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
SYMS = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT", "DOGEUSDT", "DOTUSDT", "LINKUSDT", "NEARUSDT", "OPUSDT", "SHIBUSDT"]
def kl(sym):
    end = int(time.time() * 1000); rows = []
    for url in EP:
        try:
            rows, cur = [], int(pd.Timestamp("2017-08-17", tz="UTC").timestamp() * 1000)
            while cur < end:
                r = requests.get(url, params=dict(symbol=sym, interval="1h", startTime=cur, endTime=end, limit=1000), timeout=20); r.raise_for_status(); dt = r.json()
                if not dt: break
                rows += dt; cur = dt[-1][0] + 3_600_000
                if len(dt) < 1000: break
            if rows: break
        except Exception: rows = []
    d = pd.DataFrame([x[:5] for x in rows], columns=["t", "open", "high", "low", "close"]).astype(float)
    d.index = pd.to_datetime(d.t, unit="ms", utc=True) + pd.Timedelta(hours=1); d = d[d.index <= pd.Timestamp.now(tz="UTC")]
    d = d[~d.index.duplicated()].sort_index()[["open", "high", "low", "close"]]
    return sym, d.reindex(pd.date_range(d.index[0], d.index[-1], freq="1h", tz="UTC")).ffill(limit=3)
if os.environ.get("YEREL"):
    _O = pd.read_pickle("/home/claude/lab2/data/o_1h.pkl")[["open", "high", "low", "close"]]; SYMS = SYMS[:2]
    def kl(sym): return sym, _O.copy() if sym == "BTCUSDT" else _O.iloc[30000:].copy()
with ThreadPoolExecutor(10) as ex: K = dict(ex.map(kl, SYMS))
A24, A26 = pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC"); LMT, TKR = 0.0002, 0.0005
yaz(f"# 🕳️ Fiyat boşlukları ('açıklar') — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nVeri: {len(K)} varlık, saatlik Binance · {time.time()-T0:.0f} sn\n")
def donemler(df, col="t"):
    return {"≤2023": df[df[col] < A24], "2024+": df[df[col] >= A24], "2026": df[df[col] >= A26]}
def ozet_islem(x):
    if not len(x): return dict(n=0)
    lo, hi = wboot(x.net.values, x.t.values) if len(x) >= 10 else (np.nan, np.nan)
    return dict(n=len(x), isabet=100 * (x.g > 0).mean(), brut=100 * x.g.mean(), net=100 * x.net.mean(), alt=100 * lo)
# ======================= A) CME hafta sonu boşluğu (spot BTC ile) =======================
B = K["BTCUSDT"]; rows = []
for fri in pd.date_range("2018-01-05", pd.Timestamp.now(tz="UTC").tz_localize(None), freq="W-FRI"):
    F = pd.Timestamp(f"{fri.date()} 16:00", tz="America/Chicago").tz_convert("UTC"); S = pd.Timestamp(f"{(fri + pd.Timedelta(days=2)).date()} 17:00", tz="America/Chicago").tz_convert("UTC")
    if F not in B.index or S not in B.index or S + pd.Timedelta(days=8) > B.index[-1]: continue
    pF, pS = B.close[F], B.close[S]; g = np.log(pS / pF)
    if not np.isfinite(g) or g == 0: continue
    W = B.loc[S + pd.Timedelta(hours=1): S + pd.Timedelta(days=30)]; mirror = pS * np.exp(g)
    hit = (W.low <= pF) if g > 0 else (W.high >= pF); mh = (W.high >= mirror) if g > 0 else (W.low <= mirror)
    tf = (hit.idxmax() - S) / pd.Timedelta(hours=1) if hit.any() else np.inf; tm = (mh.idxmax() - S) / pd.Timedelta(hours=1) if mh.any() else np.inf
    # işlem: S+1 saatte gir (boşluk yönüne), seviyeye limit çıkış, 72 saatte dolmazsa piyasa
    E = S + pd.Timedelta(hours=1); pe = B.close[E]; d = -np.sign(g); W2 = B.loc[E + pd.Timedelta(hours=1): E + pd.Timedelta(hours=72)]
    hit2 = (W2.low <= pF) if g > 0 else (W2.high >= pF); ulasti = (d * (pF / pe - 1) > 0) and hit2.any()
    if (d * (pF / pe - 1)) <= 0: px, fee = pe, 0.0                                              # ilk saatte zaten doldu → işlem yok
    elif ulasti: px, fee = pF, 2 * LMT
    else: px, fee = W2.close.iloc[-1], LMT + TKR
    rows.append(dict(t=S, gap=100 * g, fill_h=tf, ayna_h=tm, islem=(d * (pF / pe - 1)) > 0, g=d * (px / pe - 1), net=d * (px / pe - 1) - fee, ulasti=ulasti))
G = pd.DataFrame(rows)
yaz(f"## A) CME hafta sonu boşluğu (spot BTC, {len(G)} hafta sonu)")
for esik in (0.5, 1.0, 2.0):
    x = G[G.gap.abs() >= esik]; out = []
    for pn, y in donemler(x).items():
        if not len(y): continue
        r = dict(donem=pn, bosluk=len(y), yukari=int((y.gap > 0).sum()))
        for gun in (1, 3, 7, 30): r[f"{gun}g dolma %"] = 100 * (y.fill_h <= 24 * gun).mean(); r[f"{gun}g ayna %"] = 100 * (y.ayna_h <= 24 * gun).mean()
        out.append(r)
    yaz(f"### Boşluk ≥ %{esik} — dolma oranı vs ayna seviye (aynı uzaklık, ters yön)\n```\n" + pd.DataFrame(out).set_index("donem").round(1).to_string() + "\n```")
yaz("### İşlem: pazar açılışından 1 saat sonra boşluk yönüne gir · seviyede limit çıkış · 72 saatte dolmazsa piyasa (işlem başı %)")
tr = []
for esik in (0.5, 1.0, 2.0):
    for yon, m in (("ikisi", None), ("yalnız AŞAĞI boşluk → al", -1), ("yalnız YUKARI boşluk → sat", 1)):
        x = G[(G.gap.abs() >= esik) & G.islem]; x = x if m is None else x[np.sign(x.gap) == m]
        for pn, y in donemler(x).items(): tr.append(dict(esik=f"≥%{esik}", yon=yon, donem=pn, **ozet_islem(y)))
TR = pd.DataFrame(tr); yaz("```\n" + TR.set_index(["esik", "yon", "donem"]).round(2).to_string() + "\n```")
# gerçek CME (Yahoo BTC=F günlük) — varsa
try:
    import yfinance as yf
    C = yf.download("BTC=F", start="2018-01-01", interval="1d", progress=False, auto_adjust=False)
    if isinstance(C.columns, pd.MultiIndex): C.columns = C.columns.get_level_values(0)
    C = C.dropna(); C.index = pd.to_datetime(C.index); cr = []
    for i in range(1, len(C)):
        a, b = C.index[i - 1], C.index[i]
        if a.weekday() != 4 or b.weekday() != 0: continue
        pF, pS = C.Close.iloc[i - 1], C.Open.iloc[i]; g = np.log(pS / pF); mirror = pS * np.exp(g); W = C.iloc[i:i + 22]
        hit = (W.Low <= pF) if g > 0 else (W.High >= pF); mh = (W.High >= mirror) if g > 0 else (W.Low <= mirror)
        cr.append(dict(t=pd.Timestamp(b, tz="UTC"), gap=100 * g, f7=bool(hit.iloc[:5].any()), a7=bool(mh.iloc[:5].any()), f30=bool(hit.any()), a30=bool(mh.any())))
    CR = pd.DataFrame(cr); out = []
    for esik in (0.5, 1.0, 2.0):
        for pn, y in donemler(CR[CR.gap.abs() >= esik]).items():
            if len(y): out.append(dict(esik=f"≥%{esik}", donem=pn, bosluk=len(y), **{"1 hafta dolma %": 100 * y.f7.mean(), "1 hafta ayna %": 100 * y.a7.mean(), "1 ay dolma %": 100 * y.f30.mean(), "1 ay ayna %": 100 * y.a30.mean()}))
    yaz("### Gerçek CME grafiği (Yahoo BTC=F günlük: cuma kapanış → pazartesi açılış)\n```\n" + pd.DataFrame(out).set_index(["esik", "donem"]).round(1).to_string() + "\n```")
except Exception as e: yaz(f"_Gerçek CME verisi alınamadı: {type(e).__name__}: {str(e)[:120]}_")
# ======================= B) Adil değer boşluğu (FVG) =======================
yaz("\n## B) Adil değer boşluğu (FVG) — boşluğa geri dönüşte limit işlem, 24 saat sonra çık · kontrol: ±7 gün içinde rastgele anda aynı derinlikte limit")
rg = np.random.default_rng(0); ev = []
for sym, df in K.items():
    for tf, thr in ((1, 0.003), (4, 0.006)):
        b = df if tf == 1 else df.resample("4h", label="right", closed="right").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
        hi, lo, cl, ix = b.high.values, b.low.values, b.close.values, b.index; n = len(b); Wb, hb, sh = 48, 24 // tf, 168 // tf
        def giris(start, seviye, yon):
            for j in range(start, min(n - hb - 1, start + Wb)):
                if (yon == 1 and lo[j] <= seviye) or (yon == -1 and hi[j] >= seviye): return j
            return None
        for i in range(2, n - Wb - hb - 2):
            for yon in (1, -1):
                if yon == 1 and lo[i] > hi[i - 2] and lo[i] / hi[i - 2] - 1 >= thr: sev = lo[i]
                elif yon == -1 and hi[i] < lo[i - 2] and lo[i - 2] / hi[i] - 1 >= thr: sev = hi[i]
                else: continue
                j = giris(i + 1, sev, yon); derin = sev / cl[i] - 1
                k = int(np.clip(i + rg.integers(-sh, sh + 1), 2, n - Wb - hb - 3)); sev_k = cl[k] * (1 + derin); jk = giris(k + 1, sev_k, yon)
                ev.append(dict(sym=sym[:-4], tf=f"{tf} saat", yon="yukarı FVG → al" if yon == 1 else "aşağı FVG → sat", t=ix[i],
                               dolu=j is not None, g=(yon * (cl[j + hb] / sev - 1)) if j is not None else np.nan,
                               k_dolu=jk is not None, k_g=(yon * (cl[jk + hb] / sev_k - 1)) if jk is not None else np.nan))
FV = pd.DataFrame(ev); FV["net"] = FV.g - (LMT + TKR); yaz(f"FVG sayısı: {len(FV):,} · {time.time()-T0:.0f} sn")
out = []
for (tf, yon), x in FV.groupby(["tf", "yon"]):
    for pn, y in donemler(x).items():
        f = y[y.dolu].copy(); kk = y[y.k_dolu]
        if len(f) < 20: continue
        lo, _ = wboot(f.net.values, f.t.values)
        out.append(dict(tf=tf, yon=yon, donem=pn, fvg=len(y), haftada=len(f) / max(1, (y.t.max() - y.t.min()).days / 7), **{"geri dönüş %": 100 * y.dolu.mean(), "kontrol dönüş %": 100 * y.k_dolu.mean(),
                   "isabet": 100 * (f.g > 0).mean(), "kontrol isabet": 100 * (kk.k_g > 0).mean(), "brüt": 100 * f.g.mean(), "kontrol brüt": 100 * kk.k_g.mean(), "net": 100 * f.net.mean(), "alt": 100 * lo}))
FO = pd.DataFrame(out); yaz("```\n" + FO.set_index(["tf", "yon", "donem"]).round(2).to_string() + "\n```")
# ======================= karar =======================
yaz("\n## Karar (önceden sabit)")
for esik in ("≥%0.5", "≥%1.0"):
    for yon in ("ikisi", "yalnız AŞAĞI boşluk → al"):
        p = TR[(TR.esik == esik) & (TR.yon == yon)].set_index("donem")
        if not {"≤2023", "2024+"} <= set(p.index) or p.loc["2024+", "n"] < 10: continue
        x = G[G.gap.abs() >= float(esik[2:])]; d1 = donemler(x); fm = all((y.fill_h <= 168).mean() > (y.ayna_h <= 168).mean() for k_, y in d1.items() if k_ != "2026" and len(y))
        ok = fm and p.loc["≤2023", "net"] > 0 and p.loc["2024+", "net"] > 0 and p.loc["2024+", "alt"] > 0
        yaz(f"- {'✅' if ok else '❌'} CME boşluğu {esik} · {yon}: 1 haftada dolma > ayna (iki dönem) {'✓' if fm else '✗'} · net ≤2023 {p.loc['≤2023','net']:+.2f} · 2024+ {p.loc['2024+','net']:+.2f} (alt {p.loc['2024+','alt']:+.2f}, n={int(p.loc['2024+','n'])})"
            + (f" · 2026 {p.loc['2026','net']:+.2f} (n={int(p.loc['2026','n'])})" if "2026" in p.index and p.loc["2026", "n"] else ""))
for (tf, yon), p in FO.groupby(["tf", "yon"]):
    p = p.set_index("donem")
    if not {"≤2023", "2024+"} <= set(p.index): continue
    ok = all(p.loc[k, "brüt"] > p.loc[k, "kontrol brüt"] for k in ("≤2023", "2024+")) and p.loc["2024+", "net"] > 0 and p.loc["2024+", "alt"] > 0
    yaz(f"- {'✅' if ok else '❌'} FVG {tf} · {yon}: brüt vs kontrol ≤2023 {p.loc['≤2023','brüt']:+.3f}/{p.loc['≤2023','kontrol brüt']:+.3f} · 2024+ {p.loc['2024+','brüt']:+.3f}/{p.loc['2024+','kontrol brüt']:+.3f} · 2024+ net {p.loc['2024+','net']:+.3f} (alt {p.loc['2024+','alt']:+.3f}) · haftada {p.loc['2024+','haftada']:.0f}")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn · net = işlem başı %, limit giriş %0,02 + çıkış (limit %0,02 / piyasa %0,05) · alt = haftalık blok bootstrap %90 alt sınırı_")
open("aciklar_sonuc.md", "w").write("\n".join(L) + "\n")
