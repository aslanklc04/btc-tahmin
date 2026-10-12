# ld_anlik.py — 💧 LİKİDİTE DİPTE'yi ücretsiz bir aracıyla (saatte TEK istek) canlıya almak mümkün mü? (yalnız test, 12.10.2026)
# ld_kontrol.py'de geçen LD, Binance vadeli arşivindeki SAATLİK ORTALAMA derinlikle ölçüldü. Basit bir aracı (ör. Avrupa/Asya'da ücretsiz sunucusuz fonksiyon)
# her saat başı yalnız TEK anlık görüntü alabilir. Bu test canlıdaki durumu birebir taklit eder:
#   A1 anlık: saat başından 2 dk sonraki anlık ±%1 derinlik (canlı iş ~:02'de çalışır), karşılaştırma tabanı = arşivdeki son 720 saatlik ORTALAMALAR (canlıda arşivden gelir)
#   A0 saatlik ortalama (ld_kontrol ile aynı, karşılaştırma için)
# ÖNCEDEN YAZILI KARAR (sonuçlar görülmeden; gate_ld.py ile aynı ölçütler): A1 için K0 ANA+ (üç dönem isabet ≥ +2, net ≥ +0,10; 30/30/10) · K1 40 kaydırmalı plasebo
#   (2024+ isabet ve net farkı %95'lik değerin üstünde) · K2 dipten bağımsızlık (|z| < 2; 20/20/10, 2026 < 10 ise yalnız 2023 ve 2024+) · K3 bootstrap 2024+ alt sınır > 0 ·
#   K4 ≥ 10 sinyalli coin'lerin ≥ %60'ında daha isabetli. Hepsi geçerse → saatte tek istek yapan ücretsiz aracı yeterli; geçmezse dakikada bir örnek alan sürekli çalışan makine gerekir.
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
# ---------------- 🚀 momentum terfisi (canlıda) ----------------
RZ = np.full(len(Ez), np.nan)
for nm, o in OH.items():
    m = nmv == nm
    if m.any(): lr = np.log(o.close); sg = lr.diff().rolling(720, min_periods=168).std(); RZ[m] = ((lr - lr.shift(24)) / (sg * np.sqrt(24))).reindex(tz_[m]).values
MOM = GON & (RZ >= 2); ANA = ANA | MOM; GON = GON & ~MOM
# ---------------- Binance vadeli arşivi: saatlik ortalama + saat başı +2 dk anlık ----------------
import io, zipfile, requests
from concurrent.futures import ThreadPoolExecutor
COINS15 = ["BTC", "ETH", "ADA", "APT", "ARB", "BNB", "DOGE", "DOT", "FLOKI", "LINK", "NEAR", "OP", "PEPE", "SHIB", "SUI"]
VADS = {"SHIB": "1000SHIBUSDT", "PEPE": "1000PEPEUSDT", "FLOKI": "1000FLOKIUSDT"}
def gun(arg):
    sym, g = arg
    for k in range(3):
        try:
            r = requests.get(f"https://data.binance.vision/data/futures/um/daily/bookDepth/{sym}/{sym}-bookDepth-{g}.zip", timeout=40)
            if r.status_code == 404: return None
            if r.status_code != 200: time.sleep(1 + k); continue
            z_ = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z_.open(z_.namelist()[0]))
            d.columns = [c.strip().lower() for c in d.columns]
            if "percentage" not in d.columns: d = pd.read_csv(z_.open(z_.namelist()[0]), header=None, names=["timestamp", "percentage", "depth", "notional"])
            d = d[pd.to_numeric(d.percentage, errors="coerce").isin([1, -1, 1.0, -1.0])].copy()
            d["ts"] = pd.to_datetime(d.timestamp, utc=True); d["percentage"] = d.percentage.astype(float); d["notional"] = d.notional.astype(float)
            w = d.pivot_table(index="ts", columns="percentage", values="notional", aggfunc="mean").rename(columns={1.0: "ask1", -1.0: "bid1"}).dropna()
            w["tot"] = w.ask1 + w.bid1; w.index = pd.DatetimeIndex(w.index).as_unit("ns")
            ort = w.tot.groupby(w.index.ceil("h")).mean()
            g0 = pd.Timestamp(g, tz="UTC"); hedef = pd.date_range(g0, g0 + pd.Timedelta(hours=23), freq="1h").as_unit("ns") + pd.Timedelta(minutes=2)
            ws = w.tot.sort_index(); i = ws.index.searchsorted(hedef, side="right") - 1; ok = i >= 0
            an = pd.Series(np.where(ok, ws.values[np.clip(i, 0, None)], np.nan), index=hedef - pd.Timedelta(minutes=2))
            yas = np.where(ok, (hedef - ws.index[np.clip(i, 0, None)]).total_seconds(), np.inf); an[yas > 300] = np.nan     # 5 dk'dan eski görüntü sayılmaz
            return ort, an
        except Exception: time.sleep(1 + k)
    return None
GUNLER = [d.strftime("%Y-%m-%d") for d in pd.date_range("2022-12-01", "2026-09-30", freq="D")]
ORT, AN = {}, {}
for nm in COINS15:
    sym = VADS.get(nm, nm + "USDT")
    with ThreadPoolExecutor(16) as ex: parts = [p for p in ex.map(gun, [(sym, g) for g in GUNLER]) if p is not None]
    if parts:
        o = pd.concat([p[0] for p in parts]).sort_index(); o = o[~o.index.duplicated()]; a = pd.concat([p[1] for p in parts]).sort_index(); a = a[~a.index.duplicated()]
        ix = pd.date_range(o.index.min(), o.index.max(), freq="1h"); ORT[nm], AN[nm] = o.reindex(ix), a.reindex(ix)
    print(nm, "gün:", len(parts), f"{time.time()-T0:.0f} sn", flush=True)
def taban(s): ls = np.log(s); return ls.rolling(720, min_periods=168).mean(), ls.rolling(720, min_periods=168).std()
LD0, LD1 = {}, {}
for nm in ORT:
    m_, s_ = taban(ORT[nm]); LD0[nm] = (((np.log(ORT[nm]) - m_) / (s_ + 1e-12)) <= -2).fillna(False)
    mp, sp = m_.shift(1), s_.shift(1)                                              # canlıda: anlık görüntü + bir önceki saate kadarki ortalamalar
    LD1[nm] = (((np.log(AN[nm]) - mp) / (sp + 1e-12)) <= -2).fillna(False)
def ara(S, kay=0):
    v = np.zeros(len(Ez), bool)
    for nm, s in S.items():
        m = nmv == nm
        if m.any(): v[m] = s.reindex(tz_[m] - pd.Timedelta(hours=kay)).fillna(False).values.astype(bool)
    return v
yaz(f"# 💧 Likidite dipte — saatte tek anlık görüntüyle (ücretsiz aracı senaryosu) — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n"
    f"Coin: {len(ORT)} · anlık görüntü bulunan saat oranı: " + " · ".join(f"{k} %{100 * AN[k].notna().mean():.0f}" for k in ORT) + "\n")
yaz("Anlık ↔ saatlik ortalama uyumu: " + " · ".join(f"{k} {np.log(AN[k]).corr(np.log(ORT[k])):.2f}" for k in ORT) + "\n")
P23 = pd.Timestamp("2023-01-01", tz="UTC"); OK, NET = Ez.ok.values, Ez.net.values
D3 = (("2023", (tz_ >= P23) & (tz_ < A24_)), ("2024+", tz_ >= A24_), ("2026", tz_ >= A26_))
def st(m): return {dn: (int((m & md).sum()), 100 * OK[m & md].mean() if (m & md).any() else np.nan, 100 * NET[m & md].mean() if (m & md).any() else np.nan) for dn, md in D3}
def sat(ad, o): return f"{ad:44s}" + " | ".join(f"{o[dn][0]:5d} · %{o[dn][1]:4.1f} · {o[dn][2]:+.2f}" for dn in o)
def ustun(oc, ob, mins, gevsek=False):
    ks = [dn for dn in oc if not (gevsek and dn == "2026" and oc[dn][0] < mins[dn])]
    return len(ks) >= 2 and all(oc[dn][0] >= mins[dn] for dn in ks) and all(oc[dn][1] >= ob[dn][1] + 2 and oc[dn][2] >= ob[dn][2] + 0.10 for dn in ks)
A_ = ANA & np.isin(nmv, list(ORT)); NOR = np.isfinite(RZ) & (np.abs(RZ) < 2); m24 = tz_ >= A24_
L0, L1 = ara(LD0), ara(LD1); OA = st(A_)
yaz("_sinyal sayısı · isabet · işlem başı net % — 2023 | 2024+ | 2026_\n```"); yaz(sat("✅ ana (15 coin)", OA)); yaz(sat("A0 + saatlik ortalama LD (ld_kontrol)", st(A_ & L0)))
yaz(sat("A1 + saat başı +2 dk anlık LD (canlı aracı)", st(A_ & L1))); yaz(sat("   … dip/momentum dışı (taban)", st(A_ & NOR))); yaz(sat("   … dip/momentum dışı + A1", st(A_ & NOR & L1))); yaz("```")
K0 = ustun(st(A_ & L1), OA, {"2023": 30, "2024+": 30, "2026": 10})
def fark(c): a = A_ & m24; b = a & c; return (100 * (OK[b].mean() - OK[a].mean()), 100 * (NET[b].mean() - NET[a].mean())) if b.sum() >= 10 else (np.nan, np.nan)
G1 = fark(L1); PLS = np.array([fark(ara(LD1, int(g * 24))) for g in np.linspace(30, 400, 40)])
p95h, p95n = np.nanpercentile(PLS[:, 0], 95), np.nanpercentile(PLS[:, 1], 95); K1 = G1[0] > p95h and G1[1] > p95n
K2 = ustun(st(A_ & NOR & L1), st(A_ & NOR), {"2023": 20, "2024+": 20, "2026": 10}, gevsek=True)
b = A_ & L1 & m24; lo_, hi_ = wboot(NET[b] - NET[A_ & m24].mean(), tz_[b]); K3 = lo_ > 0
sk = []
for nm in sorted(ORT):
    mc = (nmv == nm) & A_ & (tz_ >= P23); mb = mc & L1
    if mb.sum() >= 10: sk.append((nm, int(mb.sum()), 100 * OK[mb].mean(), 100 * OK[mc].mean()))
K4 = len(sk) >= 3 and np.mean([a > b2 for _, _, a, b2 in sk]) >= 0.6
yaz(f"\n- **K0 ANA+:** {'✅' if K0 else '❌'}")
yaz(f"- **K1 plasebo (2024+, 40 kaydırma):** isabet farkı {G1[0]:+.1f} (plasebo %95 {p95h:+.1f}) · net farkı {G1[1]:+.2f} (plasebo %95 {p95n:+.2f}) → {'✅' if K1 else '❌'}")
yaz(f"- **K2 dipten bağımsızlık:** {'✅' if K2 else '❌'}")
yaz(f"- **K3 bootstrap (2024+ net farkı %90):** {100*lo_:+.2f} … {100*hi_:+.2f} → {'✅' if K3 else '❌'}")
yaz(f"- **K4 yaygınlık:** {sum(a > b2 for _, _, a, b2 in sk)}/{len(sk)} coin → {'✅' if K4 else '❌'} · " + " · ".join(f"{nm} {n} %{a:.0f} vs %{b2:.0f}" for nm, n, a, b2 in sk))
OKA = K0 and K1 and K2 and K3 and K4
yaz("\n## Önceden yazılı karar\n" + ("- ✅ **Saatte tek anlık görüntü yeterli** → ücretsiz basit aracı (saatte 1 istek) ile 💧 canlıya alınabilir" if OKA
    else "- ❌ Tek anlık görüntü yetmiyor → dakikada bir örnek alan sürekli çalışan makine gerekir"))
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("ld_anlik_sonuc.md", "w").write("\n".join(L) + "\n")
