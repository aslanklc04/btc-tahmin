# desen.py — COINBASE PRİMİ GİBİ "KİM DAHA PAHALIYA ALIYOR" İŞARETLERİ (yalnız test; canlıya dokunmaz)
#  A KORE primi (Upbit KRW): A1 BTC seviyesi = log(Upbit BTC-KRW / (Upbit USDT-KRW × Binance BTCUSDT)) · A2 coin'in BTC'ye göre Kore primi (kur düşer) → o coin
#  B TÜRKİYE primi (BtcTurk TRY): B1 BTC = log(BTCTRY / (USDTTRY × Binance BTCUSDT)) · B2 coin'in BTC'ye göre Türkiye primi → o coin
#  C USDT primi (Coinbase USDT-USD): stabil coin'e talep (kripto almak için USDT aranıyor mu) → BTC ve tüm coin'ler
#  D VADELİ primi (Binance sürekli vadeli premium index, data.binance.vision): vadeli spotun üstünde/altında → o coin
# Her işaret: saatlik, z = son 720 saate göre · olay: z ≥ 2 (yüksek) / z ≤ −2 (düşük), ilk saat, tutma süresince tekrar yok · giriş sinyal saati kapanışı · 4 / 8 / 24 s · limit komisyon %0,02 × 2.
# ÖNCEDEN KARAR: yön (AL/SAT) seçim döneminden (≤2023; veri daha geç başlıyorsa ilk yarısı) · seçim ≥ 30 olay ve net > 0 · 2024+ ≥ 30 olay, net > 0, haftalık blok %5 alt sınır > 0 ·
#   2026 net ≥ 0 (≥ 10 olay varsa) → ✅. Plasebo (zamanda kaydırılmış işaret) ile tesadüfen geçme oranı.
import io, re, time, zipfile, threading, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
BAS = pd.Timestamp("2020-01-01", tz="UTC"); SON = pd.Timestamp.now(tz="UTC").floor("h"); UA = {"User-Agent": "btc-tahmin-arastirma"}
COINS = ["BTC", "ETH", "XRP", "DOGE", "ADA", "SOL", "AVAX", "LINK", "DOT", "NEAR", "SHIB", "SUI", "APT", "ARB", "PEPE"]
class Hiz:
    def __init__(s, aralik): s.a, s.k, s.t = aralik, threading.Lock(), 0.0
    def bekle(s):
        with s.k:
            w = s.a - (time.time() - s.t)
            if w > 0: time.sleep(w)
            s.t = time.time()
def al(url, hiz, **p):
    for k in range(6):
        hiz.bekle()
        try:
            r = requests.get(url, params=p, headers=UA, timeout=30)
            if r.status_code == 429: time.sleep(2 + 2 * k); continue
            return r
        except Exception: time.sleep(2)
    return None
# ---------------- Binance spot (getiri) ----------------
def spot(nm):
    try: o = fetch_1h(BAS.timestamp() * 1000, time.time() * 1000, sym=f"{nm}USDT"); return nm, o.close.astype(float)
    except Exception: return nm, None
with ThreadPoolExecutor(6) as ex: SP = {k: v for k, v in ex.map(spot, COINS) if v is not None and len(v) > 3000}
for v in SP.values(): v.index = pd.DatetimeIndex(v.index).as_unit("ns")
# ---------------- A) Upbit ----------------
HU = Hiz(0.11)
T_UP = time.time()
def upbit(market):
    global T_UP
    T_UP = time.time(); out, to = [], SON
    while to > BAS:
        r = al("https://api.upbit.com/v1/candles/minutes/60", HU, market=market, to=to.strftime("%Y-%m-%dT%H:%M:%SZ"), count=200)
        if r is None or r.status_code != 200: print("upbit", market, r.status_code if r is not None else "yok", (r.text[:100] if r is not None else "")); break
        j = r.json()
        if not j: break
        yeni = pd.Timestamp(j[-1]["candle_date_time_utc"], tz="UTC")
        if yeni >= to or time.time() - T_UP > 900: print("upbit", market, "durdu (sayfa ilerlemedi ya da süre doldu)", yeni, to); out += j; break   # koruma: sonsuz döngü / süre
        out += j; to = yeni
        if len(j) < 200: break
    print("upbit", market, len(out), "mum", f"{time.time()-T0:.0f} sn", flush=True)
    if not out: return None
    d = pd.DataFrame(out).drop_duplicates("candle_date_time_utc")
    s = pd.Series(d.trade_price.astype(float).values, index=pd.to_datetime(d.candle_date_time_utc, utc=True) + pd.Timedelta(hours=1)).sort_index(); s.index = s.index.as_unit("ns"); return s
# ---------------- B) BtcTurk ----------------
HB = Hiz(0.25)
def btcturk(sym):
    out, cur = [], BAS
    while cur < SON:
        nx = min(cur + pd.Timedelta(days=30), SON)
        r = al("https://graph-api.btcturk.com/v1/klines/history", HB, symbol=sym, resolution=60, **{"from": int(cur.timestamp()), "to": int(nx.timestamp())})
        if r is not None and r.status_code == 200:
            j = r.json()
            if j.get("s") == "ok" and j.get("t"): out += list(zip(j["t"], j["c"]))
        elif r is not None and cur == BAS: print("btcturk", sym, r.status_code, r.text[:100])
        cur = nx
    print("btcturk", sym, len(out), "mum", f"{time.time()-T0:.0f} sn", flush=True)
    if not out: return None
    d = pd.DataFrame(out, columns=["t", "c"]).drop_duplicates("t")
    s = pd.Series(d.c.astype(float).values, index=pd.to_datetime(d.t.astype("int64"), unit="s", utc=True) + pd.Timedelta(hours=1)).sort_index(); s.index = s.index.as_unit("ns"); return s
# ---------------- C) Coinbase USDT-USD ----------------
HC = Hiz(0.12)
def coinbase(prod):
    out, cur = [], BAS
    while cur < SON:
        nx = min(cur + pd.Timedelta(hours=300), SON); r = al(f"https://api.exchange.coinbase.com/products/{prod}/candles", HC, granularity=3600, start=cur.isoformat(), end=nx.isoformat())
        if r is not None and r.status_code == 200: out += r.json()
        cur = nx
    if not out: return None
    d = pd.DataFrame(out, columns=["t", "low", "high", "open", "close", "volume"]).drop_duplicates("t")
    s = pd.Series(d.close.astype(float).values, index=pd.to_datetime(d.t, unit="s", utc=True) + pd.Timedelta(hours=1)).sort_index(); s.index = s.index.as_unit("ns"); return s
# ---------------- D) Binance vadeli premium index (arşiv) ----------------
S3, BV = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision", "https://data.binance.vision/"
def s3_list(prefix):
    out, marker = [], ""
    while True:
        r = None
        for _ in range(4):
            try: r = requests.get(S3, params=dict(delimiter="/", prefix=prefix, marker=marker), timeout=60); r.raise_for_status(); break
            except Exception: time.sleep(3)
        if r is None: return out
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
def vadeli_prim(nm):
    fs = {"SHIB": "1000SHIBUSDT", "PEPE": "1000PEPEUSDT"}.get(nm, f"{nm}USDT")
    keys = [k for k in s3_list(f"data/futures/um/monthly/premiumIndexKlines/{fs}/1h/") if k.endswith(".zip")]
    with ThreadPoolExecutor(8) as ex: raws = [r for r in ex.map(zraw, keys) if r]
    if not raws: return nm, None
    parts = []
    for raw in raws:
        first = raw.split("\n", 1)[0].split(",")[0].strip(); d = pd.read_csv(io.StringIO(raw), header=None if first.replace(".", "").isdigit() else 0); parts.append(d.set_axis(range(d.shape[1]), axis=1))
    P = pd.concat(parts); ot = pd.to_numeric(P[0], errors="coerce").astype(float).values; ot = np.where(ot > 1e14, ot / 1000, ot)
    s = pd.Series(pd.to_numeric(P[4], errors="coerce").values, index=pd.to_datetime(ot, unit="ms", utc=True) + pd.Timedelta(hours=1)); s = s[~s.index.duplicated()].sort_index(); s.index = s.index.as_unit("ns")
    return nm, s[s.index >= BAS]
zf = lambda p: (p - p.rolling(720, min_periods=168).mean()) / (p.rolling(720, min_periods=168).std() + 1e-12)
ISARET = {}                                                                                      # aile → {coin: z serisi}
import os, pickle
VF = "desen_veri.pkl"
if os.path.exists(VF): UP, BT, U, VP = pickle.load(open(VF, "rb")); print("veri önbellekten")
else:
    def _up(): return {c: upbit(f"KRW-{c}") for c in ["USDT"] + COINS}
    def _bt(): return {c: btcturk(f"{c}TRY") for c in ["USDT"] + COINS}
    def _vp():
        with ThreadPoolExecutor(4) as ex: return {k: v for k, v in ex.map(vadeli_prim, list(SP)) if v is not None and len(v) > 2000}
    with ThreadPoolExecutor(4) as ex: f1, f2, f3, f4 = ex.submit(_up), ex.submit(_bt), ex.submit(coinbase, "USDT-USD"), ex.submit(_vp); UP, BT, U, VP = f1.result(), f2.result(), f3.result(), f4.result()
    pickle.dump((UP, BT, U, VP), open(VF, "wb"))
UP = {k: v for k, v in UP.items() if v is not None and len(v) > 2000}; BT = {k: v for k, v in BT.items() if v is not None and len(v) > 2000}
yaz(f"# 🔎 Coinbase primi gibi işaretler — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nBinance spot: {len(SP)} coin · Upbit KRW: {len(UP)} ({', '.join(UP)}) · BtcTurk TRY: {len(BT)} ({', '.join(BT)}) · "
    f"Coinbase USDT-USD: {'yok' if U is None else len(U)} saat · Binance vadeli prim: {len(VP)} coin · {time.time()-T0:.0f} sn\n")
# A
if "BTC" in UP and "BTC" in SP:
    if "USDT" in UP:
        ix = SP["BTC"].index; p = np.log(UP["BTC"].reindex(ix) / (UP["USDT"].reindex(ix) * SP["BTC"])); ISARET["A1 Kore primi (BTC seviyesi) → BTC"] = {"BTC": zf(p.where(p.abs() < 0.3))}
    pb = np.log(UP["BTC"] / SP["BTC"].reindex(UP["BTC"].index))
    ISARET["A2 coin'in BTC'ye göre Kore primi → coin"] = {c: zf((np.log(UP[c] / SP[c].reindex(UP[c].index)) - pb.reindex(UP[c].index)).where(lambda x: x.abs() < 0.3)) for c in UP if c not in ("BTC", "USDT") and c in SP}
# B
if "BTC" in BT and "BTC" in SP:
    if "USDT" in BT:
        ix = SP["BTC"].index; p = np.log(BT["BTC"].reindex(ix) / (BT["USDT"].reindex(ix) * SP["BTC"])); ISARET["B1 Türkiye primi (BTC seviyesi) → BTC"] = {"BTC": zf(p.where(p.abs() < 0.3))}
    pb = np.log(BT["BTC"] / SP["BTC"].reindex(BT["BTC"].index))
    ISARET["B2 coin'in BTC'ye göre Türkiye primi → coin"] = {c: zf((np.log(BT[c] / SP[c].reindex(BT[c].index)) - pb.reindex(BT[c].index)).where(lambda x: x.abs() < 0.3)) for c in BT if c not in ("BTC", "USDT") and c in SP}
# C
if U is not None and len(U) > 2000:
    zu = zf(np.log(U).where(lambda x: x.abs() < 0.05)); ISARET["C USDT primi → BTC"] = {"BTC": zu}; ISARET["C USDT primi → tüm coin'ler"] = {c: zu for c in SP}
# D
if VP: ISARET["D vadeli primi (vadeli − spot) → coin"] = {c: zf(v) for c, v in VP.items()}
# ---------------- test ----------------
LMT = 0.0002; A24, A26 = pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")
def olaylar(zs, kos, H):
    parca = []
    for c, z in zs.items():
        if c not in SP: continue
        px = SP[c]; m = kos(z.reindex(px.index)).fillna(False).values.astype(bool); ev = events(m, H); y = px.shift(-H) / px - 1
        x = y.iloc[ev].dropna(); parca.append(pd.Series(x.values, index=x.index))
    return pd.concat(parca).sort_index() if parca else pd.Series(dtype=float)
def degerlendir(r, sec_son):
    o = {}
    sec = r[r.index < sec_son]; yon = 1 if len(sec) and sec.mean() > 0 else -1; n = yon * r - 2 * LMT
    for dn, a, b in (("seçim", None, sec_son), ("2024+", A24, None), ("2026", A26, None)):
        x = n[((n.index >= a) if a is not None else True) & ((n.index < b) if b is not None else True)]
        o[dn] = (len(x), 100 * (x > 0).mean() if len(x) else np.nan, 100 * x.mean() if len(x) else np.nan, 100 * wboot(x.values, x.index.values, 500)[0] if len(x) >= 8 else np.nan)
    ok = o["seçim"][0] >= 30 and o["seçim"][2] > 0 and o["2024+"][0] >= 30 and o["2024+"][2] > 0 and o["2024+"][3] > 0 and (o["2026"][0] < 10 or o["2026"][2] >= 0)
    return yon, o, ok
R = []; rng = np.random.default_rng(0); pl, pn = 0, 0
for ad, zs in ISARET.items():
    bas = min(z.dropna().index[0] for z in zs.values() if z.notna().any()); sec_son = A24 if bas < pd.Timestamp("2022-07-01", tz="UTC") else bas + (A24 - bas) / 2 if bas < A24 else bas + pd.Timedelta(days=180)
    for kad, kos in (("z ≥ 2 (yüksek)", lambda z: z >= 2), ("z ≤ −2 (düşük)", lambda z: z <= -2)):
        for H in (4, 8, 24):
            r = olaylar(zs, kos, H)
            if len(r) < 20: continue
            yon, o, ok = degerlendir(r, sec_son)
            R.append(dict(isaret=ad, kosul=kad, saat=H, yon="AL" if yon > 0 else "SAT", **{dn: (f"{v[0]} · %{v[1]:.0f} · {v[2]:+.2f} · alt {v[3]:+.2f}" if v[0] else "—") for dn, v in o.items()}, gecti="✅" if ok else "❌"))
            for _ in range(3):
                zsh = {c: pd.Series(np.roll(z.values, int(rng.integers(500, max(600, len(z) - 500)))), index=z.index) for c, z in zs.items()}
                rp = olaylar(zsh, kos, H)
                if len(rp) >= 20: pn += 1; pl += degerlendir(rp, sec_son)[2]
T = pd.DataFrame(R)
yaz(f"## Sonuç — {int((T.gecti == '✅').sum()) if len(T) else 0} / {len(T)} deneme geçti · plasebo geçme oranı %{100*pl/max(1,pn):.1f} → tesadüfen ≈ {pl/max(1,pn)*len(T):.1f}\n_olay · isabet · işlem başı net % · haftalık blok %5 alt sınır · yön seçim döneminden_\n```\n" + (T.to_string(index=False) if len(T) else "(veri yok)") + "\n```")
yaz("\n## Şu an\n" + " · ".join(f"{ad.split(' →')[0]}: " + ", ".join(f"{c} z {z.dropna().iloc[-1]:+.1f}" for c, z in list(zs.items())[:6] if z.notna().any()) for ad, zs in ISARET.items() if "tüm coin" not in ad))
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("desen_sonuc.md", "w").write("\n".join(L) + "\n")
