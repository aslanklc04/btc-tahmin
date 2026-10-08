# emir_akisi.py — ALICI SABIRSIZ, SATICI SABIRLI MI? Emir akışı fiyatın yönünü önceden gösteriyor mu? (canlı sisteme dokunmaz)
# Kullanıcının fikri: piyasa emriyle alış (sabırsız alıcı) bekleyen limit alışlardan fazla, bekleyen limit satış (sabırlı satıcı) piyasa satışından fazla → yükseliş?
# 1) SPOT alıcı baskısı: (piyasa alışı − piyasa satışı) / hacim, son 1/4/24 saat — 12 coin, 2017+
# 2) VADELİ alıcı baskısı: aynı ölçü vadeli piyasada (2020+)
# 3) EMİLİM: alıcı baskısı yüksek ama fiyat yükselmemiş (satıcılar limit emirle karşılıyor) vs alıcı baskısı yüksek ve fiyat da yükselmiş
# 4) AKIŞ / DEFTER (BTC, 2023+): log(4 saatlik piyasa alışı / fiyatın %1 altındaki bekleyen alış) + log(%1 üstündeki bekleyen satış / 4 saatlik piyasa satışı)
# Ölçüt (önceden sabit, önceki boşluk testleriyle aynı): son 30 güne göre z; olay z ≥ +2 / z ≤ −2 (ilk saat, 24 saat tekrar yok, giriş 1 saat sonra, 24 saat tut);
# yön ≤2023'te (4'te 2023'te) belirlenir; 2024+'da aynı yönde, limit-komisyonlu net > 0 ve %90 alt sınırı > 0 → ✅. 2026 ayrıca.
import io, re, time, zipfile, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
def log(*a): print(f"[{time.time()-T0:5.0f} sn]", *a, flush=True)
SYMS = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT", "DOGEUSDT", "DOTUSDT", "LINKUSDT", "NEARUSDT", "OPUSDT", "SHIBUSDT", "SOLUSDT", "XRPUSDT"]
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
    d = pd.DataFrame([[x[0], x[4], x[7], x[10]] for x in rows], columns=["t", "close", "qv", "tbq"]).astype(float)
    d.index = pd.to_datetime(d.t, unit="ms", utc=True) + pd.Timedelta(hours=1); d = d[~d.index.duplicated()].sort_index()
    return sym, d.reindex(pd.date_range(d.index[0], d.index[-1], freq="1h", tz="UTC"))
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
    first = raw.split("\n", 1)[0].split(",")[0].strip(); d = pd.read_csv(io.StringIO(raw), header=None if first.replace(".", "").isdigit() else 0); return d.set_axis(range(d.shape[1]), axis=1)
def vadeli(sym):
    fs = "1000SHIBUSDT" if sym == "SHIBUSDT" else sym
    keys = [k for k in s3_list(f"data/futures/um/monthly/klines/{fs}/1h/") if k.endswith(".zip")]
    with ThreadPoolExecutor(12) as ex: parts = [csv_(r) for r in ex.map(zraw, keys) if r]
    if not parts: return sym, None
    P = pd.concat(parts); ot = pd.to_numeric(P[0], errors="coerce").astype(float).values; ot = np.where(ot > 1e14, ot / 1000, ot)
    d = pd.DataFrame({"qv": pd.to_numeric(P[7], errors="coerce").values, "tbq": pd.to_numeric(P[10], errors="coerce").values}, index=pd.to_datetime(ot, unit="ms", utc=True) + pd.Timedelta(hours=1))
    return sym, d[~d.index.duplicated()].sort_index()
def defter_gun(key):
    raw = zraw(key)
    if not raw: return None
    try:
        d = pd.read_csv(io.StringIO(raw)); ts = pd.to_datetime(d.timestamp, utc=True, errors="coerce"); d["h"] = ts.dt.floor("h") + pd.Timedelta(hours=1)
        g = d[d.percentage.isin([-1, 1])].groupby(["h", "percentage"]).notional.mean().unstack(); return g.rename(columns={-1: "bid1", 1: "ask1"})
    except Exception: return None
with ThreadPoolExecutor(6) as ex:
    fs = ex.submit(lambda: dict(ThreadPoolExecutor(6).map(kl, SYMS))); fv = ex.submit(lambda: dict(ThreadPoolExecutor(4).map(vadeli, SYMS)))
    bk = [k for k in s3_list("data/futures/um/daily/bookDepth/BTCUSDT/") if k.endswith(".zip")]
    SP = fs.result(); log("spot tamam"); FU = fv.result(); log("vadeli tamam")
with ThreadPoolExecutor(24) as ex: BK = [b for b in ex.map(defter_gun, bk) if b is not None and len(b)]
BOOK = pd.concat(BK).groupby(level=0).mean().sort_index() if BK else None; log(f"emir defteri {0 if BOOK is None else len(BOOK)} saat")
A24, A26 = pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC"); H, LMT = 24, 0.0002
def zs(s): return (s - s.rolling(720, min_periods=168).mean()) / (s.rolling(720, min_periods=168).std() + 1e-12)
def baski(qv, tbq, k): return (2 * tbq.rolling(k, min_periods=max(1, k // 2)).sum() - qv.rolling(k, min_periods=max(1, k // 2)).sum()) / (qv.rolling(k, min_periods=max(1, k // 2)).sum() + 1e-12)
yaz(f"# 🧾 Emir akışı: alıcı sabırsız, satıcı sabırlı mı? — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nSpot {len(SP)} coin · vadeli {sum(v is not None for v in FU.values())} coin · BTC emir defteri {0 if BOOK is None else len(BOOK)} saat · {time.time()-T0:.0f} sn\n")
Y = {s: np.log(d.close.shift(-(H + 1)) / d.close.shift(-1)) for s, d in SP.items()}
def analiz(ad, SER, secim_son=A24):
    D = []
    for s, x in SER.items():
        if x is None: continue
        z = zs(x.replace([np.inf, -np.inf], np.nan)); y = Y[s].reindex(z.index)
        d = pd.DataFrame({"z": z, "y": y}).dropna(); d["coin"] = s
        for (a, b) in ((d.index[0], secim_son), (secim_son, A24) if secim_son < A24 else (A24, A24), (A24, d.index[-1] + pd.Timedelta(hours=1))):
            m = (d.index >= a) & (d.index < b); d.loc[m, "ex"] = d.y[m] - d.y[m].mean()                # coin ve dönem ortalamasına göre fazla
        D.append(d)
    D = pd.concat(D)
    if len(D) < 5000: yaz(f"## {ad}\nyetersiz veri\n"); return
    q = D[D.index < secim_son].z.quantile(np.linspace(0, 1, 11)).to_numpy(copy=True); q[0], q[-1] = -np.inf, np.inf
    D["dilim"] = pd.cut(D.z, q, labels=range(1, 11))
    tb = pd.DataFrame({pn: D[m].groupby("dilim", observed=False).ex.mean() * 1e4 for pn, m in (("seçim", D.index < secim_son), ("2024+", D.index >= A24), ("2026", D.index >= A26))}).round(1)
    yaz(f"## {ad}\nDilim (1 = en düşük, 10 = en yüksek; yüksek = alıcı daha sabırsız) → sonraki 24 saat, coin ortalamasına göre fazla (baz puan):\n```\n" + tb.T.to_string() + "\n```")
    for yad, cond in (("z ≥ +2", lambda z: z >= 2), ("z ≤ −2", lambda z: z <= -2)):
        E = []
        for s, d in D.groupby("coin"):
            d = d.sort_index(); ev = d.index[events(cond(d.z).values, H)]; E.append(d.loc[ev])
        E = pd.concat(E); r = {}
        for pn, m in (("seçim", E.index < secim_son), ("2024+", E.index >= A24), ("2026", E.index >= A26)): r[pn] = E[m]
        f1 = r["seçim"].ex.mean(); yon = np.sign(f1) if np.isfinite(f1) and f1 != 0 else 1; x2 = r["2024+"]
        net = yon * x2.y.values - 2 * LMT; lo, _ = wboot(net, x2.index.values) if len(x2) >= 10 else (np.nan, np.nan)
        ok = len(r["seçim"]) >= 20 and len(x2) >= 10 and np.sign(x2.ex.mean()) == yon and net.mean() > 0 and lo > 0
        yaz(f"- {'✅' if ok else '❌'} {yad}: seçim {len(r['seçim'])} olay, fazla {100*f1:+.2f}% → yön {'AL' if yon > 0 else 'SAT'} · 2024+ {len(x2)} olay, fazla {100*x2.ex.mean():+.2f}%, işlem net {100*net.mean():+.2f}% (alt {100*lo:+.2f}%)"
            + (f" · 2026 {len(r['2026'])} olay, fazla {100*r['2026'].ex.mean():+.2f}%" if len(r["2026"]) else ""))
    yaz("")
for k in (1, 4, 24): analiz(f"1) Spot alıcı baskısı, son {k} saat (12 coin)", {s: baski(d.qv, d.tbq, k) for s, d in SP.items()})
for k in (4, 24): analiz(f"2) Vadeli alıcı baskısı, son {k} saat", {s: (baski(d.qv, d.tbq, k) if d is not None else None) for s, d in FU.items()})
# 3) emilim: alıcı baskısı × fiyat değişimi (24 saat), dilimler seçim döneminden
yaz("## 3) Emilim — 24 saatlik alıcı baskısı (z) × 24 saatlik fiyat değişimi (z) · sonraki 24 saat, coin ortalamasına göre fazla (baz puan)")
rows = []
for s, d in SP.items():
    b = zs(baski(d.qv, d.tbq, 24)); p = zs(np.log(d.close / d.close.shift(24))); y = Y[s]
    x = pd.DataFrame({"b": b, "p": p, "y": y}).dropna(); x["coin"] = s
    for a, bb in ((x.index[0], A24), (A24, x.index[-1] + pd.Timedelta(hours=1))):
        m = (x.index >= a) & (x.index < bb); x.loc[m, "ex"] = x.y[m] - x.y[m].mean()
    rows.append(x)
X = pd.concat(rows); lab = lambda v: np.where(v >= 1, "yüksek", np.where(v <= -1, "düşük", "orta"))
X["baskı"], X["fiyat"] = lab(X.b), lab(X.p)
for pn, m in (("≤2023", X.index < A24), ("2024+", X.index >= A24), ("2026", X.index >= A26)):
    t_ = X[m].pivot_table(index="baskı", columns="fiyat", values="ex", aggfunc="mean") * 1e4; n_ = X[m].pivot_table(index="baskı", columns="fiyat", values="ex", aggfunc="size")
    yaz(f"### {pn} (satır: alıcı baskısı · sütun: son 24 saat fiyat)\n```\n" + t_.round(1).to_string() + "\n```\n(saat sayısı)\n```\n" + n_.to_string() + "\n```")
yaz("_Emilim = alıcı baskısı 'yüksek' ama fiyat 'düşük/orta' hücresi · Gerçek talep = baskı 'yüksek' ve fiyat 'yüksek'_\n")
# 4) akış / defter (BTC)
if BOOK is not None and {"bid1", "ask1"} <= set(BOOK.columns):
    fu = FU.get("BTCUSDT"); px = SP["BTCUSDT"].close
    if fu is not None:
        BOOK.index = pd.DatetimeIndex(BOOK.index).as_unit("ns"); fu.index = pd.DatetimeIndex(fu.index).as_unit("ns"); fu = fu.reindex(BOOK.index); tb4 = fu.tbq.rolling(4, min_periods=2).sum(); ts4 = (fu.qv - fu.tbq).rolling(4, min_periods=2).sum()
        bid, ask = BOOK.bid1.rolling(4, min_periods=2).mean(), BOOK.ask1.rolling(4, min_periods=2).mean()
        sabir = np.log(tb4 / bid) + np.log(ask / ts4)
        idx = pd.date_range(BOOK.index[0], BOOK.index[-1], freq="1h", tz="UTC")
        analiz("4) Akış / defter (BTC): sabırsız alıcı (piyasa alışı / bekleyen alış) + sabırlı satıcı (bekleyen satış / piyasa satışı)", {"BTCUSDT": sabir.reindex(idx)}, secim_son=A24)
        analiz("4b) Yalnız sabırsız alıcı: log(4 saatlik piyasa alışı / %1 alttaki bekleyen alış)", {"BTCUSDT": np.log(tb4 / bid).reindex(idx)}, secim_son=A24)
        analiz("4c) Yalnız sabırlı satıcı: log(%1 üstteki bekleyen satış / 4 saatlik piyasa satışı)", {"BTCUSDT": np.log(ask / ts4).reindex(idx)}, secim_son=A24)
yaz(f"_Süre: {time.time()-T0:.0f} sn · seçim dönemi: ≤2023 (emir defteri için 2023) · net = yön × getiri − limit komisyon %0,02×2 · alt = haftalık blok bootstrap %90_")
open("emir_akisi_sonuc.md", "w").write("\n".join(L) + "\n")
