# senaryo.py — KULLANICI SENARYOSU (13.10.2026): "satıcılar küçük ve bireysel, piyasadan satış az ve küçük; alıcılar kurumsal + bireysel, alış emirleri yüklü" → ne olur?
# Yalnız test; canlıya dokunmaz. Senaryonun ölçülebilir parçaları (her coin kendi geçmişine göre, son 30 gün = 720 saat z):
#   S1 DEFTER DENGESİZ   : Binance vadeli defterinde fiyatın %1 altındaki alış derinliği / %1 üstündeki satış derinliği → log oran z ≥ 2 (alış kalın, satış ince)
#   S2 PİYASA SATIŞI AZ  : Binance spot son 4 saatte piyasa emriyle satışın (taker sell) hacme payı z ≤ −2
#   S3 BÜYÜK ALIR KÜÇÜK SATAR: vadeli büyük hesapların pozisyon long/short oranı ile tüm hesapların long/short oranı farkı (log) z ≥ 2
#   S4 BÜYÜK İŞLEMLİ ALIM: spot son 4 saat ortalama işlem büyüklüğü z ≥ 2 VE piyasa satışı payı z ≤ −1
#   S5 SENARYONUN TAMAMI : defter dengesiz z ≥ 1 VE piyasa satışı payı z ≤ −1 VE büyük−küçük farkı z ≥ 1
# Kullanım: ✅ ana sinyallere ÖNCELİK işareti (sinyal sayısı düşmez). Taban: emir defteri arşivi olan 15 coin'in ✅ ana sinyalleri (🚀 dahil), dönemler 2023 · 2024+ · 2026.
# ÖNCEDEN YAZILI KARAR (sonuçlar görülmeden; 💧 LD ile aynı ölçütler) — her S için:
#   K0 ANA+: üç dönemde isabet ≥ taban +2 puan VE net ≥ taban +0,10 (en az 30 / 30 / 10 sinyal)
#   K1 40 kaydırmalı plasebo (30–400 gün): 2024+ isabet ve net farkı plasebo %95'lik değerinin üstünde
#   K2 dipten bağımsızlık (|24 s z| < 2): üç dönemde +2 puan ve +0,10 (20 / 20 / 10; 2026 < 10 ise yalnız 2023 ve 2024+)
#   K3 haftalık blok bootstrap 2024+ net farkı %90 alt sınırı > 0 · K4 ≥ 10 sinyalli coin'lerin ≥ %60'ında daha isabetli (en az 3 coin)
#   K5 💧'den bağımsızlık: 💧 LD olmayan ana sinyallerde de K2 ile aynı ölçüt (aynı şeyi ölçüyorsa ayrı işaret gereksiz)
#   → K0–K5 hepsi geçerse canlıya öncelik işareti olarak önerilir. 5 varyant denendiği için bir tanesinin tesadüfen geçmesi K1–K4 ile ayrıca elenir.
import os, glob, gzip, json, pickle, time, numpy as np, pandas as pd
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
f = lambda p: glob.glob(p, recursive=True)
RAW = {k: v.astype("float64") for k, v in pd.read_pickle(f("art3/**/prim_veri.pkl")[0]).items()}; RAW = {k: v for k, v in RAW.items() if len(v) >= 3000}
for k, v in RAW.items(): v.index = pd.DatetimeIndex(v.index).tz_convert("UTC").as_unit("ns")
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

PA = pd.read_csv(f"{CD}/prim_acik.csv"); EK = []
for _, r_ in PA.iterrows():
    if r_.coin not in RAW: continue
    D = RAW[r_.coin]; ev = D.index[events((D.z >= r_.esik).fillna(False).values, int(r_.saat))]
    EK.append(pd.DataFrame({"aile": "💵 ABD alıyor (tek başına)", "sinyal": f"💵 {r_.coin}", "canli": "📨", "H": int(r_.saat), "t": ev, "r": np.nan, "nm": r_.coin, "z": D.z.reindex(ev).values, "yon": 1}))
D = RAW["BTC"]; ev = D.index[events((D.z <= -2).fillna(False).values, 24)]
EK.append(pd.DataFrame({"aile": "🔻 BTC kısa", "sinyal": "🔻 BTC kısa", "canli": "📨", "H": 24, "t": ev, "r": np.nan, "nm": "BTC", "z": D.z.reindex(ev).values, "yon": -1}))
E = pd.concat([E] + EK, ignore_index=True); E["t"] = pd.DatetimeIndex(E.t).tz_convert("UTC").as_unit("ns"); E["H"] = E.H.astype(int)
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
BEN = {"2022-06→2023": (55.9, 0.30), "2024+": (58.6, 0.647), "2026": (59.1, 0.589)}
DN = (("2022-06→2023", (tz_ >= P0) & (tz_ < A24_), (A24_ - P0).days / 7), ("2024+", tz_ >= A24_, HAF["2024+"]), ("2026", tz_ >= A26_, HAF["2026"]))
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
RZ = np.full(len(Ez), np.nan)
for nm, o in OH.items():
    m = nmv == nm
    if m.any(): lr = np.log(o.close); sg = lr.diff().rolling(720, min_periods=168).std(); RZ[m] = ((lr - lr.shift(24)) / (sg * np.sqrt(24))).reindex(tz_[m]).values
MOM = GON & (RZ >= 2); ANA = ANA | MOM; GON = GON & ~MOM
# ---------------- veri: emir defteri (arşiv), spot mum (taker), vadeli metrikler ----------------
import io, zipfile, requests
from concurrent.futures import ThreadPoolExecutor
def z720(s): return (s - s.rolling(720, min_periods=168).mean()) / (s.rolling(720, min_periods=168).std() + 1e-12)
DER = pd.read_pickle(f("**/derinlik.pkl")[0]); DCO = sorted(k for k, v in DER.items() if {"ask1", "bid1"} <= set(v.columns))
def kline(sym):
    rows, cur, end = [], int(pd.Timestamp("2022-04-01", tz="UTC").timestamp() * 1000), time.time() * 1000
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
with ThreadPoolExecutor(8) as ex: SP = {k: v for k, v in zip(DCO, ex.map(lambda c: kline(c + "USDT"), DCO)) if len(v) > 2000}
VADS = {"SHIB": "1000SHIBUSDT", "PEPE": "1000PEPEUSDT", "FLOKI": "1000FLOKIUSDT"}; SS = requests.Session()
def gunm(arg):
    sym, g = arg
    for k in range(3):
        try:
            r = SS.get(f"https://data.binance.vision/data/futures/um/daily/metrics/{sym}/{sym}-metrics-{g}.zip", timeout=40)
            if r.status_code == 404: return None
            if r.status_code != 200: time.sleep(1 + k); continue
            z_ = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z_.open(z_.namelist()[0]))
            d["t"] = pd.to_datetime(d.create_time, utc=True).dt.ceil("h")
            return d.groupby("t")[["count_long_short_ratio", "sum_toptrader_long_short_ratio"]].last()
        except Exception: time.sleep(1 + k)
    return None
GUNLER = [d.strftime("%Y-%m-%d") for d in pd.date_range("2022-10-01", "2026-10-10", freq="D")]; MET = {}
for nm in DCO:
    sym = VADS.get(nm, nm + "USDT")
    with ThreadPoolExecutor(24) as ex: parts = [p for p in ex.map(gunm, [(sym, g) for g in GUNLER]) if p is not None and len(p)]
    if parts:
        D = pd.concat(parts).sort_index(); D = D[~D.index.duplicated()]; D.index = pd.DatetimeIndex(D.index).as_unit("ns"); MET[nm] = D.reindex(pd.date_range(D.index.min(), D.index.max(), freq="1h"))
    print(nm, "metrik gün:", len(parts), f"{time.time()-T0:.0f} sn", flush=True)
KS, LDS = {}, {}
for nm in DCO:
    if nm not in SP: continue
    d = SP[nm]; ix = d.index; Dd = DER[nm].reindex(ix)
    qv4 = d.qv.rolling(4).sum(); sat4 = (d.qv - d.tbq).rolling(4).sum() / (qv4 + 1e-9); zs = z720(sat4)
    zi = z720(np.log(Dd.bid1 / Dd.ask1)); za = z720(np.log(qv4 / (d.n.rolling(4).sum() + 1e-9)))
    if nm in MET: M = MET[nm].reindex(ix); zd = z720(np.log(M.sum_toptrader_long_short_ratio) - np.log(M.count_long_short_ratio))
    else: zd = pd.Series(np.nan, index=ix)
    KS[nm] = pd.DataFrame({"S1 defter dengesiz (alış kalın, satış ince)": zi >= 2, "S2 piyasa satışı az": zs <= -2, "S3 büyük alır, küçük satar (vadeli hesaplar)": zd >= 2,
                           "S4 büyük işlemli alım": (za >= 2) & (zs <= -1), "S5 senaryonun tamamı": (zi >= 1) & (zs <= -1) & (zd >= 1)}).fillna(False)
    LDS[nm] = (z720(np.log(Dd.ask1 + Dd.bid1)) <= -2).fillna(False)
tz_, nmv = pd.DatetimeIndex(Ez.t), Ez.nm.values; OK, NET = Ez.ok.values, Ez.net.values
def ara(kol, kay=0, S=None):
    v = np.zeros(len(Ez), bool)
    for nm in KS:
        m = nmv == nm
        if m.any():
            s = (S or LDS)[nm] if kol is None else KS[nm][kol]
            v[m] = s.reindex(tz_[m] - pd.Timedelta(hours=kay)).fillna(False).values.astype(bool)
    return v
P23 = pd.Timestamp("2023-01-01", tz="UTC"); m24 = tz_ >= A24_
D3 = (("2023", (tz_ >= P23) & (tz_ < A24_)), ("2024+", m24), ("2026", tz_ >= A26_))
def st(m): return {dn: (int((m & md).sum()), 100 * OK[m & md].mean() if (m & md).any() else np.nan, 100 * NET[m & md].mean() if (m & md).any() else np.nan) for dn, md in D3}
def sat(ad, o): return f"{ad[:46]:46s}" + " | ".join(f"{o[dn][0]:5d} · %{o[dn][1]:4.1f} · {o[dn][2]:+.2f}" for dn in o)
def ustun(oc, ob, mins, gevsek=False):
    ks = [dn for dn in oc if not (gevsek and dn == "2026" and oc[dn][0] < mins[dn])]
    return len(ks) >= 2 and all(oc[dn][0] >= mins[dn] for dn in ks) and all(oc[dn][1] >= ob[dn][1] + 2 and oc[dn][2] >= ob[dn][2] + 0.10 for dn in ks)
A_ = ANA & np.isin(nmv, list(KS)); NOR = np.isfinite(RZ) & (np.abs(RZ) < 2); LD0 = ara(None); OA = st(A_)
yaz(f"# 🏦 Senaryo: küçük satıcı / büyük alıcı / ince satış defteri — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n"
    f"Coin: {len(KS)} ({', '.join(KS)}) · vadeli metrik: {len(MET)} coin · ✅ ana sinyal (bu coin'ler, 🚀 dahil): {A_.sum():,} · {time.time()-T0:.0f} sn\n")
yaz("_sinyal sayısı · isabet · işlem başı net % — 2023 | 2024+ | 2026_\n```"); yaz(sat("✅ ana (taban)", OA)); yaz(sat("✅ ana + 💧 LD (karşılaştırma)", st(A_ & LD0)))
SONUC = []
for kol in next(iter(KS.values())).columns:
    c = ara(kol); oc = st(A_ & c); yaz(sat(kol, oc))
    K0 = ustun(oc, OA, {"2023": 30, "2024+": 30, "2026": 10})
    def fark(cc): a = A_ & m24; b = a & cc; return (100 * (OK[b].mean() - OK[a].mean()), 100 * (NET[b].mean() - NET[a].mean())) if b.sum() >= 10 else (np.nan, np.nan)
    G1 = fark(c); PLS = np.array([fark(ara(kol, int(g * 24))) for g in np.linspace(30, 400, 40)])
    p95h, p95n = (np.nanpercentile(PLS[:, i], 95) if np.isfinite(PLS[:, i]).any() else np.nan for i in (0, 1))
    K1 = bool(G1[0] > p95h and G1[1] > p95n)
    K2 = ustun(st(A_ & NOR & c), st(A_ & NOR), {"2023": 20, "2024+": 20, "2026": 10}, gevsek=True)
    b = A_ & c & m24; lo_, hi_ = wboot(NET[b] - NET[A_ & m24].mean(), tz_[b]) if b.sum() >= 5 else (np.nan, np.nan); K3 = bool(lo_ > 0)
    sk = []
    for nm in KS:
        mc = (nmv == nm) & A_ & (tz_ >= P23); mb = mc & c
        if mb.sum() >= 10: sk.append((nm, int(mb.sum()), 100 * OK[mb].mean(), 100 * OK[mc].mean()))
    K4 = len(sk) >= 3 and np.mean([a > b2 for _, _, a, b2 in sk]) >= 0.6
    K5 = ustun(st(A_ & ~LD0 & c), st(A_ & ~LD0), {"2023": 20, "2024+": 20, "2026": 10}, gevsek=True)
    ort = (c & LD0)[A_].sum() / max(c[A_].sum(), 1)
    SONUC.append((kol, K0, K1, K2, K3, K4, K5, G1, p95h, p95n, lo_, hi_, sk, ort, st(A_ & ~LD0 & c)))
yaz("```\n_💧 olmayan ana sinyallerde (K5 için):_\n```"); yaz(sat("✅ ana, 💧 yok (taban)", st(A_ & ~LD0)))
for r in SONUC: yaz(sat(r[0] + " (💧 yok)", r[14]))
yaz("```\n## Ölçütler")
for kol, K0, K1, K2, K3, K4, K5, G1, p95h, p95n, lo_, hi_, sk, ort, _ in SONUC:
    i = lambda x: "✅" if x else "❌"
    yaz(f"**{kol}** — K0 {i(K0)} · K1 plasebo {i(K1)} (isabet {G1[0]:+.1f} vs %95 {p95h:+.1f}; net {G1[1]:+.2f} vs {p95n:+.2f}) · K2 dipten bağımsız {i(K2)} · "
        f"K3 bootstrap {i(K3)} ({100*lo_:+.2f} … {100*hi_:+.2f}) · K4 yaygınlık {i(K4)} ({sum(a > b2 for _, _, a, b2 in sk)}/{len(sk)}) · K5 💧'den bağımsız {i(K5)} · sinyallerinin %{100*ort:.0f}'i aynı anda 💧")
GEC = [r[0] for r in SONUC if all(r[1:7])]
yaz("\n## Önceden yazılı karar\n" + (f"- ✅ GEÇTİ: {', '.join(GEC)} → canlıya öncelik işareti önerilir" if GEC else "- ❌ Hiçbiri tüm ölçütleri geçmedi → eklenmez"))
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("senaryo_sonuc.md", "w").write("\n".join(L) + "\n")
