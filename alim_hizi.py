# alim_hizi.py — "ALIM EMİRLERİ HIZLI GELİYOR, SATIŞ EMİRLERİ ÇABUK ERİYOR" (yalnız test, kullanıcı fikri 12.10.2026).
#   AH  alım hızı: son 1 saatteki agresif alış hacmi (taker buy, Binance spot) son 30 güne göre z ≥ 2 VE alıcı payı ≥ %55
#   SE  satış eriyor: Binance vadeli emir defterinde fiyatın %1 üstündeki satış emirleri (notional) son 4 saatte olağandışı azaldı (z ≤ −2), %1 altındaki alış emirleri azalmadı (z > −1)
#   LD  likidite dipte: fiyatın ±%1'indeki toplam emir derinliği son 30 güne göre olağandışı düşük (z ≤ −2)  [kullanıcı fikri]
#   SB  satış tarafı boş: %1 üstündeki satış derinliği olağandışı düşük (z ≤ −2), alış derinliği normal (z > −1)  [kullanıcı fikri]
#   AH+SE ikisi birden. Emir defteri arşivi 2023'ten → dönemler 2023 · 2024+ · 2026 (Eylül sonuna).
# ÖNCEDEN YAZILI KARAR (12.10.2026, sonuçlar görülmeden):
#   TEK BAŞINA AL: tutma süresi (4 / 8 / 24 s) yalnız 2023'ten seçilir; seçilen süre üç dönemde de ana set ölçütünü geçerse
#     (isabet ≥ %55,9 · %58,6 · %59,1 VE net ≥ +0,30 · +0,647 · +0,589; ≥ 30 / 30 / 10 sinyal) → yeni ✅ sinyal.
#   FİLTRE: canlı sinyallerde koşul varken ANA+ (üç dönemde ana ortalamasından isabet ≥ +2 puan ve net ≥ +0,10 → öne al) ·
#     YED+ / GÖN+ (yedek / gönderilmeyen üç dönemde ana set ölçütünü geçer → ✅ ana).
#   PLASEBO: aynı koşullar 30 ve 60 gün kaydırılarak denenir; gerçekte geçen sayı plasebodan açıkça fazla değilse hiçbir şey eklenmez.
import os, glob, gzip, json, pickle, time, numpy as np, pandas as pd
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
f = lambda p: glob.glob(p, recursive=True)
RAW = {k: v.astype("float64") for k, v in pd.read_pickle(f("art3/**/prim_veri.pkl")[0]).items()}; RAW = {k: v for k, v in RAW.items() if len(v) >= 3000}
for k, v in RAW.items(): v.index = pd.DatetimeIndex(v.index).tz_convert("UTC").as_unit("ns")
# ---------------- olaylar (prim_pencere.py ile aynı) ----------------
EX = {os.path.basename(p)[5:-4]: pd.read_pickle(p) for p in f("art1/**/disa_*USDT.pkl")}
E24 = {os.path.basename(p)[7:-4]: pd.read_pickle(p) for p in f("art2/**/disa24_*USDT.pkl")}
SFB = pd.read_pickle("sf_BTCUSDT.pkl").astype("float64")
CD = "canli/durum"; CANLI = [l.strip() for l in open(f"{CD}/coin_listesi.txt") if l.strip()]
JOINT, TEKL = pd.read_csv(f"{CD}/ortak_acik.csv"), pd.read_csv(f"{CD}/tek_acik.csv")
SIGON = {}
for s in CANLI:
    with gzip.open(f"{CD}/model_{s}.pkl.gz", "rb") as g: SIGON[s] = {k: bool(v["on"]) for k, v in pickle.load(g)["SIG"].items()}
with gzip.open(f"{CD}/model.pkl.gz", "rb") as g: MB = pickle.load(g)
LMT = 0.0002; P0, A24, A26 = pd.Timestamp("2022-06-01", tz="UTC"), pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")
DON = (("22-06→23", lambda i: (i >= P0) & (i < A24)), ("2024+", lambda i: i >= A24), ("2026", lambda i: i >= A26))
EV = []
def kaydet(aile, ad, t, r, H, nm, canli):
    for ti, ri in zip(pd.DatetimeIndex(t), np.asarray(r, float)):
        if np.isfinite(ri): EV.append((aile, ad, canli, H, ti, ri, nm))
X = SFB
for H in (1, 4, 8):
    S, C, T10, T30, y = X[f"S{H}"], X[f"C{H}"], X[f"T10{H}"], X[f"T30{H}"], X[f"y{H}"]
    for sg in (1, -1):
        for li, lad in ((2, "Çok güçlü"), (1, "Güçlü")):
            lvl = np.where(C >= T10, 2, np.where(C >= T30, 1, 0)); m = ((np.sign(S) == sg) & (lvl == li) & T10.notna() & y.notna()).values
            ev = events(m, H); st = MB["R"][H]["STATS"][(li, sg)]; act, _ = action(H, sg, li, st)
            if sg > 0: kaydet("BTC 1/4/8 s + ⭐ + A", f"BTC {H}s {lad} ↑", X.index[ev], np.exp(y.values[ev]) - 1, H, "BTC", "📨" if act[:1] in ("✅", "🟢") else "")
star = ((X.S4 > 0) & (X.C4 >= X.T104) & (X.S8 > 0) & (X.C8 >= X.T108) & X.y8.notna()).values; ev = events(star, 8)
kaydet("BTC 1/4/8 s + ⭐ + A", "BTC ⭐", X.index[ev], np.exp(X.y8.values[ev]) - 1, 8, "BTC", "📨")
ac = ((X.am >= 0.85) & X.y4.notna()).values; ev = events(ac, 4); kaydet("BTC 1/4/8 s + ⭐ + A", "BTC A", X.index[ev], np.exp(X.y4.values[ev]) - 1, 4, "BTC", "📨")
B = EX["BTCUSDT"]; AD = {"star": ("⭐", 8, "y8"), "u4": ("4s ÇG↑", 4, "y4"), "acls": ("A", 4, "y4")}
for s in CANLI:
    nm = s[:-4]; Xc = EX.get(s)
    if Xc is None: continue
    Bx = B.reindex(Xc.index); bu4 = Bx.u4.fillna(False).values.astype(bool); bany = (Bx.star.fillna(False) | Bx.u4.fillna(False) | Bx.acls.fillna(False)).values.astype(bool)
    jo, te = set(JOINT[JOINT.sym == s].sinyal), set(TEKL[TEKL.sym == s].sinyal)
    for k, (ad, H0, yc0) in AD.items():
        for aile, kos, acik in (("coin tek başına", np.ones(len(Xc), bool), SIGON[s].get(k, False)), ("coin 🤝 ortak", bu4, k in jo), ("coin 🔇 sessiz", ~bany, k in te)):
            H, yc = (H0, yc0) if aile == "coin tek başına" else (4, "y4")
            m = Xc[k].fillna(False).values.astype(bool) & kos & Xc[yc].notna().values; ev = events(m, H)
            kaydet(aile, f"{nm} {aile} {ad}", Xc.index[ev], np.exp(Xc[yc].values[ev]) - 1, H, nm, "📨" if acik else "")
for s, Xd in E24.items():
    nm = s.replace("USDT", ""); Xd = Xd.reindex(pd.date_range(Xd.index[0], Xd.index[-1], freq="1h", tz="UTC")); c = Xd.close.ffill(limit=3).values; n = len(Xd)
    m = np.nan_to_num(((Xd.S24 > 0) & (Xd.C24 >= Xd.T10_24)).values).astype(bool) & Xd.T10_24.notna().values & (np.arange(n) + 25 < n); ev = events(m, 24)
    kaydet("🧪 24 saat", f"{nm} 24s", Xd.index[ev], c[ev + 24] / c[ev] - 1, 24, nm, "📨")
def gun_isle(aile, ad, gunler, nm, saat, HD, yon):
    D = RAW[nm]; t1 = pd.DatetimeIndex(gunler) + pd.Timedelta(days=1, hours=saat); t2 = t1 + pd.Timedelta(days=HD)
    r = yon * (D.c.reindex(t2).values / D.c.reindex(t1).values - 1); kaydet(aile, ad, t1, r, HD * 24, nm, "📨")
try:
    import zincir_canli as ZC
    Zs = ZC.olcu(ZC.cm("eth", gun=1700), ZC.stabil())
    for ad, acik, yon, gun, kos, _ in ZC.KURAL:
        if yon > 0: ev = Zs.index[events(kos(Zs).fillna(False).values, gun)]; gun_isle("⛓️ ETH", f"⛓️ {ad}", ev, "ETH", 6, gun, yon)
except Exception as e: yaz(f"_⛓️ atlandı: {type(e).__name__} {str(e)[:120]}_")
try:
    j = json.load(open("veri_bgeo/coins-addr-1-BTC.json")); d = pd.DataFrame(j); d.index = pd.to_datetime(d.pop("d"), utc=True).dt.floor("D")
    sm = d.drop(columns=[c for c in d.columns if "ts" in c.lower() or "unix" in c.lower()]).apply(pd.to_numeric, errors="coerce").iloc[:, 0].dropna().sort_index()
    sm = sm[~sm.index.duplicated()].asfreq("D"); zk = np.log(sm).diff(30); zk = (zk - zk.rolling(90, min_periods=30).mean()) / (zk.rolling(90, min_periods=30).std() + 1e-12)
    ev = zk.index[events((zk <= -1.5).fillna(False).values, 7)]
    for nm in ("BTC", "ETH"): gun_isle("🧑 küçük yatırımcı", f"🧑 {nm} AL", ev, nm, 12, 7, 1)
except Exception as e: yaz(f"_🧑 atlandı: {type(e).__name__} {str(e)[:120]}_")
E = pd.DataFrame(EV, columns=["aile", "sinyal", "canli", "H", "t", "r", "nm"]); E = E[(E.canli == "📨")].reset_index(drop=True)
zc = np.full(len(E), np.nan)
for nm, g in E.groupby("nm"):
    if nm in RAW: zc[g.index.values] = RAW[nm].z.reindex(pd.DatetimeIndex(g.t).tz_convert("UTC").as_unit("ns")).values
E["z"] = zc; E["yon"] = 1

# ---------------- 💵 (canlı ayar) ve 🔻 BTC kısa olayları ----------------
PA = pd.read_csv(f"{CD}/prim_acik.csv"); EK = []
for _, r_ in PA.iterrows():
    if r_.coin not in RAW: continue
    D = RAW[r_.coin]; ev = D.index[events((D.z >= r_.esik).fillna(False).values, int(r_.saat))]
    EK.append(pd.DataFrame({"aile": "💵 ABD alıyor (tek başına)", "sinyal": f"💵 {r_.coin}", "canli": "📨", "H": int(r_.saat), "t": ev, "r": np.nan, "nm": r_.coin, "z": D.z.reindex(ev).values, "yon": 1}))
D = RAW["BTC"]; ev = D.index[events((D.z <= -2).fillna(False).values, 24)]
EK.append(pd.DataFrame({"aile": "🔻 BTC kısa", "sinyal": "🔻 BTC kısa", "canli": "📨", "H": 24, "t": ev, "r": np.nan, "nm": "BTC", "z": D.z.reindex(ev).values, "yon": -1}))
E = pd.concat([E] + EK, ignore_index=True); E["t"] = pd.DatetimeIndex(E.t).tz_convert("UTC").as_unit("ns"); E["H"] = E.H.astype(int)
# ---------------- saatlik OHLC ----------------
from concurrent.futures import ThreadPoolExecutor
COINS = sorted(set(E.nm)); BAS = pd.Timestamp("2019-11-01", tz="UTC")
def ohlc(nm):
    try:
        o = fetch_1h(BAS.timestamp() * 1000, time.time() * 1000, sym=f"{nm}USDT"); o.index = pd.DatetimeIndex(o.index).as_unit("ns"); return nm, o[["high", "low", "close"]].astype(float)
    except Exception as e: print(nm, "OHLC alınamadı", e); return nm, None
with ThreadPoolExecutor(6) as ex: OH = {k: v for k, v in ex.map(ohlc, COINS) if v is not None}
SIG1 = {nm: np.log(o.close).diff().rolling(720, min_periods=168).std() for nm, o in OH.items()}

LMT_ = 0.0002
def taban(ev):
    o = OH.get(ev.nm)
    if o is None: return np.nan
    i = o.index.searchsorted(ev.t)
    if i >= len(o) or o.index[i] != ev.t or i + int(ev.H) >= len(o): return np.nan
    return ev.yon * (o.close.values[i + int(ev.H)] / o.close.values[i] - 1) - 2 * LMT_
E["net"] = [taban(ev) for ev in E.itertuples()]; E = E[np.isfinite(E.net)].copy(); E["ok"] = E.net > 0
def tip(r):
    if r.aile.startswith("coin "): return r.sinyal.split(" ", 1)[1]
    if r.aile.startswith("🧪"): return "🧪 24 s"
    if r.aile.startswith("💵"): return "💵 ABD alıyor"
    return r.sinyal
E["tip"] = [tip(r) for r in E.itertuples()]
E["zb"] = np.select([E.z <= -1, E.z <= 0, E.z <= 1, E.z > 1], ["⛔", "⚠️", "✅", "💪"], default="?")
tt = pd.DatetimeIndex(E.t); A23, A24_, A26_ = pd.Timestamp("2023-01-01", tz="UTC"), pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")
SONT = tt.max(); HAF = {"2023": 52.0, "2024+": (SONT - A24_).days / 7, "2026": (SONT - A26_).days / 7}
BTC_A, TEK_A = "BTC 1/4/8 s + ⭐ + A", "coin tek başına"
Ez = E[E.zb != "?"].copy(); tz_ = pd.DatetimeIndex(Ez.t); btc = (Ez.aile == BTC_A).values; tek = (Ez.aile == TEK_A).values; z = Ez.z.values
# ÖNCEDEN YAZILI KARAR (12.10.2026): ana set — 2022-06→2023 %55,9 · +0,433 | 2024+ %58,6 · +0,647 | 2026 %59,1 · +0,589. Kullanıcı kararıyla 2022–23 kâr eşiği +0,30.
#   Eşik ancak üç dönemde de isabet ≥ ana set VE net ≥ ana set (2022–23 net ≥ +0,30) ise geçer (≥ 30 / 30 / 10 sinyal). Birden çok geçerse en düşük eşik (en çok sinyal) seçilir.
BEN = {"2022-06→2023": (55.9, 0.30), "2024+": (58.6, 0.647), "2026": (59.1, 0.589)}
DN = (("2022-06→2023", (tz_ >= P0) & (tz_ < A24_), (A24_ - P0).days / 7), ("2024+", tz_ >= A24_, HAF["2024+"]), ("2026", tz_ >= A26_, HAF["2026"]))
# ---------------- canlı düzen ----------------
import io, zipfile, requests, pickle
CAN24 = {os.path.basename(p)[8:-11] for p in glob.glob(f"{CD}/model24_*USDT.pkl.gz")}
Ez["zB"] = RAW["BTC"].z.reindex(tz_).values; zB = Ez.zB.values; nmv = Ez.nm.values; ail = Ez.aile.values
c24 = (ail == "🧪 24 saat") & np.isin(nmv, list(CAN24)); dis24 = (ail == "🧪 24 saat") & ~c24
TUR = {"🤝": (ail == "coin 🤝 ortak") & (z >= 0), "🧪": c24 & (z >= 0), "🔀": (ail == "coin 🔇 sessiz") & (z > 0) & np.isfinite(zB) & (zB > -1) & (zB <= 0),
       "💵": ail == "💵 ABD alıyor (tek başına)", "⛓️": ail == "⛓️ ETH", "🧑": ail == "🧑 küçük yatırımcı"}
ANA = np.zeros(len(Ez), bool)
for v in TUR.values(): ANA |= v
key = pd.Series(nmv).astype(str) + "|" + pd.Series(tz_.floor("h").astype(str)); kset = set(key[((ail == "coin 🤝 ortak") | (ail == "coin 🔇 sessiz"))])
tek_dup = (ail == "coin tek başına") & key.isin(kset).values
ADAY = np.isin(ail, ["coin 🤝 ortak", "🧪 24 saat", "coin 🔇 sessiz", "coin tek başına", "BTC 1/4/8 s + ⭐ + A"]) & ~dis24 & ~tek_dup
YED = ADAY & ~ANA & np.isin(ail, ["coin 🔇 sessiz", "coin tek başına"]) & (z >= 0)
GON = ADAY & ~ANA & ~YED
yaz(f"# ⚡ Alım hızı ve satış emirlerinin erimesi — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nOlay: ✅ ana {ANA.sum():,} · 🔸 yedek {YED.sum():,} · gönderilmeyen {GON.sum():,}\n")
# ---------------- veri: spot saatlik (alıcı hacmi) + vadeli emir defteri ----------------
import io, zipfile, requests
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
COINS15 = ["BTC", "ETH", "ADA", "APT", "ARB", "BNB", "DOGE", "DOT", "FLOKI", "LINK", "NEAR", "OP", "PEPE", "SHIB", "SUI"]
VADS = {"SHIB": "1000SHIBUSDT", "PEPE": "1000PEPEUSDT", "FLOKI": "1000FLOKIUSDT"}
def kline(sym):
    rows, cur, end = [], int(pd.Timestamp("2022-05-01", tz="UTC").timestamp() * 1000), time.time() * 1000
    while cur < end:
        dt = None
        for k in range(6):
            try: r = requests.get("https://data-api.binance.vision/api/v3/klines", params=dict(symbol=sym, interval="1h", startTime=cur, limit=1000), timeout=20); r.raise_for_status(); dt = r.json(); break
            except Exception: time.sleep(2 + 2 * k)
        if not dt: break
        rows += dt; cur = dt[-1][0] + 3_600_000
        if len(dt) < 1000: break
    d = pd.DataFrame([x[:11] for x in rows], columns=["t", "o", "h", "l", "c", "v", "ct", "qv", "n", "tbv", "tbq"]).astype(float)
    d.index = pd.DatetimeIndex(pd.to_datetime(d.t, unit="ms", utc=True) + pd.Timedelta(hours=1)).as_unit("ns"); return d[~d.index.duplicated()].sort_index()
with ThreadPoolExecutor(8) as ex: SP = dict(zip(COINS15, ex.map(lambda c: kline(c + "USDT"), COINS15)))
def gun(arg):
    sym, g = arg
    for k in range(3):
        try:
            r = requests.get(f"https://data.binance.vision/data/futures/um/daily/bookDepth/{sym}/{sym}-bookDepth-{g}.zip", timeout=40)
            if r.status_code == 404: return None
            if r.status_code != 200: time.sleep(1 + k); continue
            z_ = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z_.open(z_.namelist()[0]))
            d.columns = [c.strip().lower() for c in d.columns]
            if "percentage" not in d.columns:
                d = pd.read_csv(z_.open(z_.namelist()[0]), header=None, names=["timestamp", "percentage", "depth", "notional"])
            d = d[pd.to_numeric(d.percentage, errors="coerce").isin([1, -1, 1.0, -1.0])]
            d["t"] = pd.to_datetime(d.timestamp, utc=True).dt.ceil("h"); d["percentage"] = d.percentage.astype(float); d["notional"] = d.notional.astype(float)
            return d.pivot_table(index="t", columns="percentage", values="notional", aggfunc="mean").rename(columns={1.0: "ask1", -1.0: "bid1"})
        except Exception: time.sleep(1 + k)
    return None
GUNLER = [d.strftime("%Y-%m-%d") for d in pd.date_range("2022-12-01", "2026-09-30", freq="D")]
DER = {}
for nm in COINS15:
    sym = VADS.get(nm, nm + "USDT")
    with ThreadPoolExecutor(16) as ex: parts = [p for p in ex.map(gun, [(sym, g) for g in GUNLER]) if p is not None and len(p)]
    if parts:
        D = pd.concat(parts).sort_index(); D = D[~D.index.duplicated()]; D.index = pd.DatetimeIndex(D.index).as_unit("ns"); DER[nm] = D
    print(nm, "emir defteri gün:", len(parts), f"{time.time()-T0:.0f} sn", flush=True)
pd.to_pickle(DER, "derinlik.pkl")
yaz(f"Spot: {len(SP)} coin · emir defteri: {len(DER)} coin ({', '.join(f'{k}:{v.index[0]:%Y-%m}' for k, v in DER.items())}) · {time.time()-T0:.0f} sn\n")
def z720(s): return (s - s.rolling(720, min_periods=168).mean()) / (s.rolling(720, min_periods=168).std() + 1e-12)
KOS = {}
for nm in COINS15:
    d = SP[nm]; ah = (z720(np.log(d.tbq + 1)) >= 2) & ((d.tbq / (d.qv + 1e-9)) >= 0.55)
    se = ld = sb = pd.Series(False, index=d.index)
    if nm in DER and {"ask1", "bid1"} <= set(DER[nm].columns):
        D = DER[nm].reindex(d.index); a4 = np.log(D.ask1).diff(4); b4 = np.log(D.bid1).diff(4)
        se = ((z720(a4) <= -2) & (z720(b4) > -1)).fillna(False)
        ld = (z720(np.log(D.ask1 + D.bid1)) <= -2).fillna(False)
        sb = ((z720(np.log(D.ask1)) <= -2) & (z720(np.log(D.bid1)) > -1)).fillna(False)
    KOS[nm] = pd.DataFrame({"AH alım hızı": ah.fillna(False), "SE satış emirleri eriyor": se, "AH+SE ikisi birden": (ah & se).fillna(False),
                            "LD likidite dipte": ld, "SB satış tarafı boş": sb})
P23, A24x, A26x, SONx = pd.Timestamp("2023-01-01", tz="UTC"), pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC"), pd.Timestamp("2026-10-01", tz="UTC")
DNx = (("2023", P23, A24x), ("2024+", A24x, SONx), ("2026", A26x, SONx))
BEN = {"2023": (55.9, 0.30), "2024+": (58.6, 0.647), "2026": (59.1, 0.589)}; MIN = {"2023": 30, "2024+": 30, "2026": 10}
def tek(kos_ad, H, kay=0):
    rows = []
    for nm in COINS15:
        d = SP[nm]; m = KOS[nm][kos_ad].shift(kay // 1 if kay else 0).fillna(False).values.astype(bool) if kay else KOS[nm][kos_ad].values.astype(bool)
        n = len(d); m = m & (np.arange(n) + H < n) & (d.index >= P23) & (d.index + pd.Timedelta(hours=H) < SONx); ev = events(m, H)
        rows.append(pd.DataFrame({"t": d.index[ev], "net": d.c.values[ev + H] / d.c.values[ev] - 1 - 0.0004}))
    X = pd.concat(rows); X["ok"] = X.net > 0; return X
def olc(X):
    o = {}
    for dn, a, b in DNx:
        x = X[(X.t >= a) & (X.t < b)]; hf = max((min(b, X.t.max()) - a).days / 7, 1); o[dn] = (len(x), len(x) / hf, 100 * x.ok.mean() if len(x) else np.nan, 100 * x.net.mean() if len(x) else np.nan)
    return o
def gecer(o): return all(o[dn][0] >= MIN[dn] and o[dn][2] >= BEN[dn][0] and o[dn][3] >= BEN[dn][1] for dn in MIN)
def yz(o): return " | ".join(f"{o[dn][1]:5.1f}/hf · %{o[dn][2]:4.1f} · {o[dn][3]:+.2f} ({o[dn][0]})" if o[dn][0] >= 5 else f"{o[dn][0]:5d} az" for dn, _, _ in DNx)
yaz("## 1) Tek başına AL sinyali (15 coin, spot, %0,04 maliyet)\n_haftada · isabet · işlem başı net % (sinyal) — 2023 | 2024+ | 2026_\n```")
TEKG = []
def tek_karar(kay=0):
    gec = []
    for ka in KOS[COINS15[0]].columns:
        R = {H: olc(tek(ka, H, kay)) for H in (4, 8, 24)}
        Hs = max(R, key=lambda H: R[H]["2023"][3] if np.isfinite(R[H]["2023"][3]) else -9)
        if kay == 0:
            for H in (4, 8, 24): yaz(f"{ka:28s} {H:>2} s{' ← 2023 seçimi' if H == Hs else '':14s} {yz(R[H])}")
        if gecer(R[Hs]): gec.append(f"TEK: {ka} ({Hs} s)")
    return gec
TEKG = tek_karar(0); yaz("```")
# ---------------- 2) canlı sinyallere filtre ----------------
def kos_ez(kay):
    K = {}
    for ka in KOS[COINS15[0]].columns:
        arr = np.zeros(len(Ez), bool)
        for nm in COINS15:
            m = nmv == nm
            if m.any(): s = KOS[nm][ka]; arr[m] = s.reindex(tz_[m] - pd.Timedelta(hours=kay)).fillna(False).values.astype(bool)
        K[ka] = arr
    return K
DN = (("2023", (tz_ >= P23) & (tz_ < A24x), (A24x - P23).days / 7), ("2024+", tz_ >= A24x, HAF["2024+"]), ("2026", tz_ >= A26x, HAF["2026"]))
def ist(m): return {dn: (int((m & md).sum()), (m & md).sum() / hf, 100 * Ez.ok.values[m & md].mean() if (m & md).any() else np.nan, 100 * Ez.net.values[m & md].mean() if (m & md).any() else np.nan) for dn, md, hf in DN}
OANA = ist(ANA)
def filt_karar(K, yazdir=False):
    gec = []
    for ka, c in K.items():
        oa, oy, og = ist(ANA & c), ist(YED & c), ist(GON & c)
        if yazdir: yaz(f"\n{ka}\n  {'✅ ana + koşul':30s}{yz(oa)}\n  {'🔸 yedek + koşul':30s}{yz(oy)}\n  {'gönderilmeyen + koşul':30s}{yz(og)}")
        if all(oa[dn][0] >= MIN[dn] for dn in MIN) and all(oa[dn][2] >= OANA[dn][2] + 2 and oa[dn][3] >= OANA[dn][3] + 0.10 for dn in MIN): gec.append(f"ANA+: {ka}")
        for gr, o in (("YED+", oy), ("GÖN+", og)):
            if gecer(o): gec.append(f"{gr}: {ka}")
    return gec
yaz("\n## 2) Canlı sinyallere filtre (ana coin'ler)\n```" + f"\n{'✅ ANA (hepsi, 2023+)':32s}{yz(OANA)}")
FG = filt_karar(kos_ez(0), True); yaz("```")
PL = tek_karar(720) + tek_karar(1440) + filt_karar(kos_ez(720)) + filt_karar(kos_ez(1440))
G0 = TEKG + FG
yaz(f"\n**Gerçek veride geçen:** {len(G0)} · **plasebo (30 ve 60 gün kaydırılmış, iki deneme toplamı):** {len(PL)}")
yaz("\n## Önceden yazılı karar\n" + ("\n".join(f"- {g}" for g in G0) if G0 else "- Hiçbir kural geçmedi → eklenmez")
    + f"\n- Plasebo: gerçek {len(G0)} · plasebo ortalaması {len(PL)/2:.1f} → " + ("✅ şanstan fazlası var" if len(G0) > len(PL) / 2 + 1 else "❌ şanstan ayırt edilemiyor"))
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("alim_hizi_sonuc.md", "w").write("\n".join(L) + "\n")
