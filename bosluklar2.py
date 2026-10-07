# bosluklar2.py — BAŞKA BOŞLUKLAR: fiyatın önceden iz bıraktığı başka "açıklar" var mı? (canlı sisteme dokunmaz)
# A) Borsalar arası fiyat boşluğu: Coinbase primi (ABD alıcıları) · Kore primi / "kimchi" (Upbit, Koreli bireysel yatırımcı) · Tether primi (USDC/USDT)
# B) Spot–vadeli boşluğu: sürekli vadeli prim endeksi (BTC, ETH) — kaldıraçlı kalabalığın yönü
# C) Emir defteri boşluğu: vadeli emir defterinde fiyatın %1 ve %5 altındaki alış derinliği vs üstündeki satış derinliği (Binance bookDepth, 2023+)
# D) Fonlama saati boşluğu: 00/08/16 UTC fonlama ödemesinden önceki/sonraki saatlerde fiyat davranışı (fonlama yönüne göre)
# Her boşluk serisi için: son 30 güne göre z-skoru → (1) ondalık dilimlerde BTC'nin sonraki 24 saati, (2) uç olaylar (z ≥ +2 / z ≤ −2, ilk saat, 24 saat tekrar yok).
# Önceden sabit karar: olayın yönü ≤2023'te belirlenir; 2024+'da aynı yönde, limit-komisyonlu net > 0 ve %90 alt sınırı > 0 ise ✅. Giriş olaydan 1 saat sonra.
import os, io, re, time, zipfile, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
def log(*a): print(f"[{time.time()-T0:5.0f} sn]", *a, flush=True)
UA = {"User-Agent": "btc-tahmin-arastirma"}
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
    d.index = pd.to_datetime(d.t, unit="ms", utc=True) + pd.Timedelta(hours=1); return d[~d.index.duplicated()].sort_index().close
def coinbase_1h(prod="BTC-USD"):
    out, cur, end = [], pd.Timestamp("2017-08-01", tz="UTC"), pd.Timestamp.now(tz="UTC"); s = requests.Session(); s.headers.update(UA); fails = 0
    while cur < end and fails < 30:
        nx = min(cur + pd.Timedelta(hours=300), end)
        try:
            r = s.get(f"https://api.exchange.coinbase.com/products/{prod}/candles", params=dict(granularity=3600, start=cur.isoformat(), end=nx.isoformat()), timeout=20)
            if r.status_code == 429: time.sleep(1); continue
            r.raise_for_status(); out += r.json(); cur = nx; time.sleep(0.12)
        except Exception: fails += 1; time.sleep(2)
    if not out: return None
    df = pd.DataFrame(out, columns=["t", "low", "high", "open", "close", "volume"]).drop_duplicates("t"); df.index = pd.to_datetime(df.t, unit="s", utc=True) + pd.Timedelta(hours=1)
    return df.sort_index().close
def upbit_1h(market="KRW-BTC"):
    out, to, s, fails = [], pd.Timestamp.now(tz="UTC").floor("h"), requests.Session(), 0
    while to > pd.Timestamp("2017-10-01", tz="UTC") and fails < 30:
        try:
            r = s.get("https://api.upbit.com/v1/candles/minutes/60", params=dict(market=market, count=200, to=to.strftime("%Y-%m-%dT%H:%M:%SZ")), timeout=20)
            if r.status_code == 429: time.sleep(1); continue
            r.raise_for_status(); dt = r.json()
            if not dt: break
            out += dt; to = pd.Timestamp(dt[-1]["candle_date_time_utc"], tz="UTC"); time.sleep(0.11)
        except Exception: fails += 1; time.sleep(2)
    if not out: return None
    df = pd.DataFrame(out); idx = pd.to_datetime(df.candle_date_time_utc, utc=True) + pd.Timedelta(hours=1)
    return pd.Series(df.trade_price.astype(float).values, index=idx).groupby(level=0).last().sort_index()
S3, BV = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision", "https://data.binance.vision/"
def s3_list(prefix):
    out, marker = [], ""
    while True:
        for _ in range(4):
            try: r = requests.get(S3, params=dict(delimiter="/", prefix=prefix, marker=marker), timeout=60); r.raise_for_status(); break
            except Exception: time.sleep(3)
        x = r.text; pre = re.findall(r"<Prefix>([^<]+)</Prefix>", x)[1:]; keys = re.findall(r"<Key>([^<]+)</Key>", x); out += pre + keys
        if "<IsTruncated>true</IsTruncated>" not in x or not (pre or keys): return out
        marker = (pre + keys)[-1]
def zraw(key):
    for _ in range(3):
        try:
            r = requests.get(BV + key, timeout=90)
            if r.status_code == 404: return None
            r.raise_for_status(); z = zipfile.ZipFile(io.BytesIO(r.content)); return z.open(z.namelist()[0]).read().decode()
        except Exception: time.sleep(2)
    return None
def csv_(raw):
    first = raw.split("\n", 1)[0].split(",")[0].strip(); return pd.read_csv(io.StringIO(raw), header=None if first.replace(".", "").isdigit() else 0)
def premium_1h(fs):
    keys = [k for k in s3_list(f"data/futures/um/monthly/premiumIndexKlines/{fs}/1h/") if k.endswith(".zip")]
    with ThreadPoolExecutor(16) as ex: parts = [csv_(r) for r in ex.map(zraw, keys) if r]
    P = pd.concat([p.set_axis(range(p.shape[1]), axis=1) for p in parts]); ot = pd.to_numeric(P[0], errors="coerce").astype(float).values; ot = np.where(ot > 1e14, ot / 1000, ot)
    return pd.Series(pd.to_numeric(P[4], errors="coerce").values, index=pd.to_datetime(ot, unit="ms", utc=True) + pd.Timedelta(hours=1)).groupby(level=0).last().sort_index()
def funding(fs):
    keys = [k for k in s3_list(f"data/futures/um/monthly/fundingRate/{fs}/") if k.endswith(".zip")]
    with ThreadPoolExecutor(16) as ex: parts = [csv_(r) for r in ex.map(zraw, keys) if r]
    P = pd.concat([p.set_axis(range(p.shape[1]), axis=1) for p in parts]); ot = pd.to_numeric(P[0], errors="coerce").astype(float).values; ot = np.where(ot > 1e14, ot / 1000, ot)
    return pd.Series(pd.to_numeric(P[2], errors="coerce").values, index=pd.to_datetime(ot, unit="ms", utc=True).floor("h")).groupby(level=0).last().sort_index()
ORNEK = {}
def book_gun(key):
    raw = zraw(key)
    if not raw: return None
    try:
        d = csv_(raw); d.columns = [str(c) for c in d.columns]
        if "timestamp" not in d.columns: d.columns = ["timestamp", "percentage", "depth", "notional"][:d.shape[1]]
        if not ORNEK: ORNEK["ilk"] = raw[:300]
        ts = pd.to_datetime(d.timestamp, utc=True, errors="coerce"); d["h"] = ts.dt.floor("h") + pd.Timedelta(hours=1); d["p"] = pd.to_numeric(d.percentage, errors="coerce")
        v = pd.to_numeric(d.notional if "notional" in d else d.depth, errors="coerce"); d["v"] = v
        g = d.groupby(["h", "p"]).v.mean().unstack()
        out = pd.DataFrame(index=g.index)
        for k in (1, 5):
            if -k in g.columns and k in g.columns: out[f"imb{k}"] = (g[-k] - g[k]) / (g[-k] + g[k])
        return out
    except Exception as e:
        ORNEK.setdefault("hata", f"{type(e).__name__}: {e} · {raw[:200]}"); return None
# ---------------- veriler (paralel; bir kaynak düşerse yalnız o bölüm atlanır) ----------------
def safe(f, *a):
    try: return f(*a)
    except Exception as e: log("⚠️", f.__name__, a, type(e).__name__, str(e)[:150]); return None
with ThreadPoolExecutor(8) as ex:
    f_btc, f_eth, f_usdc = ex.submit(safe, kl, "BTCUSDT"), ex.submit(safe, kl, "ETHUSDT"), ex.submit(safe, kl, "USDCUSDT")
    f_cb, f_up = ex.submit(safe, coinbase_1h), ex.submit(safe, upbit_1h)
    f_pb, f_pe, f_fr = ex.submit(safe, premium_1h, "BTCUSDT"), ex.submit(safe, premium_1h, "ETHUSDT"), ex.submit(safe, funding, "BTCUSDT")
    BTC, ETH, USDC = f_btc.result(), f_eth.result(), f_usdc.result(); log("binance tamam")
    CB, UP = f_cb.result(), f_up.result(); log(f"coinbase {0 if CB is None else len(CB)} · upbit {0 if UP is None else len(UP)}")
    PB, PE, FR = f_pb.result(), f_pe.result(), f_fr.result(); log("vadeli arşiv tamam")
try:
    import yfinance as yf
    k_ = yf.download("KRW=X", start="2017-09-01", interval="1d", progress=False, auto_adjust=False)
    if isinstance(k_.columns, pd.MultiIndex): k_.columns = k_.columns.get_level_values(0)
    KRW = pd.Series(k_.Close.values, index=pd.to_datetime(k_.index).tz_localize("UTC") + pd.Timedelta(days=1)).dropna()   # günün kapanışı ertesi gün kullanılır
except Exception as e: KRW = None; log("KRW yok", e)
bk = safe(lambda: [k for k in s3_list("data/futures/um/daily/bookDepth/BTCUSDT/") if k.endswith(".zip")]) or []; log(f"emir defteri: {len(bk)} gün")
with ThreadPoolExecutor(24) as ex: BK = [b for b in ex.map(book_gun, bk) if b is not None and len(b)]
BOOK = pd.concat(BK).groupby(level=0).mean().sort_index() if BK else None; log(f"emir defteri saatlik: {0 if BOOK is None else len(BOOK)}")
idx = pd.date_range(BTC.index[0], BTC.index[-1], freq="1h", tz="UTC"); c = BTC.reindex(idx).ffill(limit=3); ce = ETH.reindex(idx).ffill(limit=3) if ETH is not None else c
yaz(f"# 🕳️ Başka boşluklar — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nVeri: Binance BTC/ETH/USDC · Coinbase {'✓' if CB is not None else '✗'} · Upbit {'✓' if UP is not None else '✗'} · USD/KRW {'✓' if KRW is not None else '✗'} · vadeli prim ✓ · fonlama ✓ · emir defteri {len(BK)} gün · {time.time()-T0:.0f} sn")
if ORNEK: yaz("Emir defteri dosya örneği: `" + (ORNEK.get("ilk", "") or ORNEK.get("hata", ""))[:250].replace("\n", " ⏎ ") + "`" + (f" · hata: {ORNEK['hata'][:200]}" if "hata" in ORNEK else ""))
SER = {}
if CB is not None: SER["Coinbase primi (BTC)"] = (np.log(CB.reindex(idx) / c), "BTC")
if UP is not None and KRW is not None:
    krw = KRW.reindex(KRW.index.union(idx)).ffill().reindex(idx); SER["Kore primi / kimchi (BTC)"] = (np.log(UP.reindex(idx) / (c * krw)), "BTC")
if USDC is not None: SER["Tether primi (USDT, USDC/USDT'den)"] = (-np.log(USDC.reindex(idx)), "BTC")
if PB is not None: SER["Spot–vadeli primi (BTC)"] = (PB.reindex(idx).rolling(8, min_periods=4).mean(), "BTC")
if PE is not None and ETH is not None: SER["Spot–vadeli primi (ETH)"] = (PE.reindex(idx).rolling(8, min_periods=4).mean(), "ETH")
if BOOK is not None:
    for k in (1, 5):
        if f"imb{k}" in BOOK: SER[f"Emir defteri dengesizliği ±%{k} (BTC)"] = (BOOK[f"imb{k}"].reindex(idx).rolling(4, min_periods=2).mean(), "BTC")
A24, A26 = pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC"); H, LMT = 24, 0.0002
yaz("\n_Sonraki 24 saat: olaydan 1 saat sonra giriş, 24 saat tut · 'fazla' = aynı dönemde rastgele saatin ortalamasına göre fark (puan) · net = yön × getiri − limit komisyon_\n")
KAR = []
for ad, (s, var) in SER.items():
    pr = c if var == "BTC" else ce; y = np.log(pr.shift(-(H + 1)) / pr.shift(-1)); s = s.replace([np.inf, -np.inf], np.nan)
    z = (s - s.rolling(720, min_periods=168).mean()) / (s.rolling(720, min_periods=168).std() + 1e-12)
    D = pd.DataFrame({"s": s, "z": z, "y": y}).dropna()
    if len(D) < 2000: yaz(f"## {ad}\nyetersiz veri ({len(D)} saat)\n"); continue
    sel = D[D.index < A24]; sel = sel if len(sel) > 24 * 180 else D[D.index < D.index[0] + (D.index[-1] - D.index[0]) / 3]
    q = sel.z.quantile(np.linspace(0, 1, 11)).to_numpy(copy=True); q[0], q[-1] = -np.inf, np.inf
    D["dilim"] = pd.cut(D.z, q, labels=range(1, 11)); per = {"seçim": D[D.index < (A24 if len(D[D.index < A24]) > 24 * 180 else sel.index[-1])], "2024+": D[D.index >= A24]}
    tb = pd.DataFrame({pn: x.groupby("dilim", observed=False).y.mean() * 1e4 - x.y.mean() * 1e4 for pn, x in per.items()}).round(1)
    yaz(f"## {ad} · {D.index[0]:%Y-%m} → · ortalama {D.s.mean():+.5f}, sapma {D.s.std():.5f}\nDilim (1 = boşluk en düşük, 10 = en yüksek) → sonraki 24 saat, tabana göre fazla (baz puan, 100 = %1):\n```\n" + tb.T.to_string() + "\n```")
    for yon_ad, m in (("z ≥ +2 (boşluk çok geniş)", D.z >= 2), ("z ≤ −2 (boşluk ters yönde çok geniş)", D.z <= -2)):
        ev = D.index[events(m.reindex(D.index).fillna(False).values, H)]; E = D.loc[ev]
        r = {}
        for pn, (a, b) in {"seçim": (D.index[0], per["seçim"].index[-1]), "2024+": (A24, D.index[-1]), "2026": (A26, D.index[-1])}.items():
            x = E[(E.index >= a) & (E.index <= b)]; base = D[(D.index >= a) & (D.index <= b)].y.mean()
            r[pn] = (len(x), (x.y.mean() - base) * 100 if len(x) else np.nan, x)
        n1, f1, _ = r["seçim"]; yon = np.sign(f1) if np.isfinite(f1) and f1 != 0 else 1
        n2, f2, x2 = r["2024+"]; net = yon * x2.y.values - 2 * LMT if n2 else np.array([]); lo, _ = wboot(net, x2.index.values) if n2 >= 10 else (np.nan, np.nan)
        ok = n1 >= 20 and n2 >= 10 and np.sign(f2) == yon and net.mean() > 0 and lo > 0
        n3, f3, x3 = r["2026"]
        yaz(f"- {'✅' if ok else '❌'} {yon_ad}: seçim {n1} olay, fazla {f1:+.2f}% → yön {'AL' if yon > 0 else 'SAT'} · 2024+ {n2} olay, fazla {f2:+.2f}%, işlem net {100*net.mean() if n2 else float('nan'):+.2f}% (alt {100*lo:+.2f}%)"
            + (f" · 2026 {n3} olay, fazla {f3:+.2f}%" if n3 else ""))
        KAR.append((ad, yon_ad, ok))
    yaz("")
# ---------------- D) fonlama saati ----------------
yaz("## D) Fonlama saati: ödemeden önceki son saat (… → 00/08/16 UTC) ve sonraki ilk saat, fonlama yönüne göre BTC getirisi (baz puan)")
r1 = np.log(c / c.shift(1)); fr = FR.reindex(idx).ffill(limit=8).shift(1) if FR is not None else pd.Series(np.nan, index=idx)                               # bir önceki ödemede belirlenen oran (bilinen)
rows = []
for pn, m in {"≤2023": idx < A24, "2024+": idx >= A24, "2026": idx >= A26}.items():
    for etk, msk in (("fonlama > %0,01 (uzunlar öder)", fr > 0.0001), ("fonlama < 0 (kısalar öder)", fr < 0), ("hepsi", fr.notna())):
        mm = pd.Series(m, index=idx) & msk
        once = r1[mm & (idx.hour % 8 == 0)]; sonra = r1[mm & (idx.hour % 8 == 1)]; diger = r1[mm & ~np.isin(idx.hour % 8, [0, 1])]
        rows.append(dict(donem=pn, durum=etk, saat=int(once.notna().sum()), **{"ödemeden önceki saat": 1e4 * once.mean(), "sonraki saat": 1e4 * sonra.mean(), "diğer saatler": 1e4 * diger.mean()}))
yaz("```\n" + pd.DataFrame(rows).set_index(["donem", "durum"]).round(2).to_string() + "\n```")
yaz(f"\n## Özet\n" + "\n".join(f"- {'✅' if ok else '❌'} {a} · {b}" for a, b, ok in KAR) + f"\n\n_Süre: {time.time()-T0:.0f} sn_")
open("bosluklar2_sonuc.md", "w").write("\n".join(L) + "\n")
