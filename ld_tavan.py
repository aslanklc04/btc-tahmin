# ld_tavan.py — 💦 LİKİDİTE TAVANDA (kullanıcı sorusu 15.10.2026): coin'in ±%1 emir derinliği kendi son 30 gününe göre olağandışı KALIN (z ≥ +2) iken ✅ ana sinyaller (yalnız test).
# 💧 (z ≤ −2) ile aynı veri ve aynı ölçütler; yön ters. ÖNCEDEN YAZILI KARAR (sonuçlar görülmeden):
#   İYİ yönde: K1–K4 (💧 ile aynı) hepsi geçerse → öncelik işareti adayı.
#   KÖTÜ yönde (KX): üç dönemde (2023 · 2024+ · 2026) isabet ≤ ana −2 puan VE net ≤ ana −0,10 (en az 30 / 30 / 10) VE 40 kaydırmalı plaseboda 2024+ isabet farkı %5'lik değerin altında
#     → ⚠️ "likidite çok kalın: zayıf" uyarı adayı (sinyal silinmez). İkisi de değilse: etkisiz, eklenmez.
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
# ---------------- veri ----------------
import requests
from concurrent.futures import ThreadPoolExecutor
def kline(sym):
    rows, cur, end = [], int(pd.Timestamp("2022-02-01", tz="UTC").timestamp() * 1000), time.time() * 1000
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
KC = sorted(set(nmv[ANA]))
with ThreadPoolExecutor(8) as ex: SP = {k: v for k, v in zip(KC, ex.map(lambda c: kline(c + "USDT"), KC)) if len(v) > 2000}
DER = pd.read_pickle(f("**/derinlik.pkl")[0])
def z720(s): return (s - s.rolling(720, min_periods=168).mean()) / (s.rolling(720, min_periods=168).std() + 1e-12)
LDS, VK = {}, {}
for nm, d in SP.items():
    if nm in DER and {"ask1", "bid1"} <= set(DER[nm].columns):
        D = DER[nm].reindex(d.index); LDS[nm] = (z720(np.log(D.ask1 + D.bid1)) >= 2).fillna(False)
    r1 = np.log(d.c).diff().abs(); qv = d.qv.replace(0, np.nan)
    VK[nm] = pd.DataFrame({"V1 Amihud 24 s": z720(np.log(r1.rolling(24).sum() / qv.rolling(24).sum())) >= 2,
                           "V2 Amihud 4 s": z720(np.log(r1.rolling(4).sum() / qv.rolling(4).sum())) >= 2,
                           "V3 aralık / hacim 24 s": z720(np.log((d.h.rolling(24).max() - d.l.rolling(24).min()) / d.c / qv.rolling(24).sum())) >= 2}).fillna(False)
def ara(S, kay=0, kol=None):
    v = np.zeros(len(Ez), bool)
    for nm, s in S.items():
        m = nmv == nm
        if m.any(): x = s[kol] if kol else s; v[m] = x.reindex(tz_[m] - pd.Timedelta(hours=kay)).fillna(False).values.astype(bool)
    return v
yaz(f"# 💧 Likidite TAVANDA — sağlamlık testi + canlı vekiller — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n"
    f"Olay: ✅ ana {ANA.sum():,} (🚀 dahil) · emir defteri: {len(LDS)} coin · spot mum: {len(SP)} coin\n")
P23 = pd.Timestamp("2023-01-01", tz="UTC"); OK, NET = Ez.ok.values, Ez.net.values
D3 = (("2023", (tz_ >= P23) & (tz_ < A24_)), ("2024+", tz_ >= A24_), ("2026", tz_ >= A26_))
DS = (("2022-06→2023", (tz_ >= P0) & (tz_ < A24_)), ("2024+", tz_ >= A24_), ("2026", tz_ >= A26_))
def st(m, dn_):
    return {dn: (int((m & md).sum()), 100 * OK[m & md].mean() if (m & md).any() else np.nan, 100 * NET[m & md].mean() if (m & md).any() else np.nan) for dn, md in dn_}
def sat(ad, o): return f"{ad:44s}" + " | ".join(f"{o[dn][0]:5d} · %{o[dn][1]:4.1f} · {o[dn][2]:+.2f}" for dn in o)
def ustun(oc, ob, mins, gevsek=False):
    ks = [dn for dn in oc if not (gevsek and dn == "2026" and oc[dn][0] < mins[dn])]
    return all(oc[dn][0] >= mins[dn] for dn in ks) and all(oc[dn][1] >= ob[dn][1] + 2 and oc[dn][2] >= ob[dn][2] + 0.10 for dn in ks) and len(ks) >= 2
LD0 = ara(LDS)
yaz("_sinyal sayısı · isabet · işlem başı net % — 2023 | 2024+ | 2026_\n```")
OA = st(ANA, D3); yaz(sat("✅ ana (hepsi)", OA)); yaz(sat("✅ ana + 💦 LT", st(ANA & LD0, D3)))
NOR = np.isfinite(RZ) & (np.abs(RZ) < 2); yaz(sat("✅ ana, dip/momentum dışı (|z| < 2)", st(ANA & NOR, D3))); yaz(sat("✅ ana, dip/momentum dışı + 💦 LT", st(ANA & NOR & LD0, D3)))
DIP = RZ <= -2; yaz(sat("✅ ana + 📉 dip (z ≤ −2)", st(ANA & DIP, D3))); yaz(sat("✅ ana + 💦 LT + 📉 dip", st(ANA & LD0 & DIP, D3)))
yaz(f"```\nÖrtüşme: 💦 LT olan ana sinyallerde aynı anda 📉 dip payı %{100 * (DIP[ANA & LD0]).mean():.0f} · 📉 dip olan ana sinyallerde aynı anda 💦 LT payı %{100 * (LD0[ANA & DIP]).mean():.0f}")
# K1
m24 = tz_ >= A24_
def fark(c): a = ANA & m24; b = a & c; return 100 * (OK[b].mean() - OK[a].mean()) if b.sum() >= 10 else np.nan, 100 * (NET[b].mean() - NET[a].mean()) if b.sum() >= 10 else np.nan
G1 = fark(LD0); PLS = np.array([fark(ara(LDS, int(g * 24))) for g in np.linspace(30, 400, 40)])
p95h, p95n = np.nanpercentile(PLS[:, 0], 95), np.nanpercentile(PLS[:, 1], 95); K1 = G1[0] > p95h and G1[1] > p95n
yaz(f"\n**K1 plasebo dağılımı (2024+, 40 kaydırma):** gerçek isabet farkı {G1[0]:+.1f} puan (plasebo %95: {p95h:+.1f}) · net farkı {G1[1]:+.2f} (plasebo %95: {p95n:+.2f}) → {'✅' if K1 else '❌'}")
# K2
K2 = ustun(st(ANA & NOR & LD0, D3), st(ANA & NOR, D3), {"2023": 20, "2024+": 20, "2026": 10}, gevsek=True)
yaz(f"**K2 dipten bağımsızlık:** {'✅' if K2 else '❌'}")
# K3
b = ANA & LD0 & m24; lo_, hi_ = wboot(NET[b] - NET[ANA & m24].mean(), tz_[b]); K3 = lo_ > 0
yaz(f"**K3 haftalık blok bootstrap (2024+ net farkı %90 aralığı):** {100*lo_:+.2f} … {100*hi_:+.2f} → {'✅' if K3 else '❌'}")
# K4
m23 = tz_ >= P23; sk = []
for nm in sorted(set(nmv[ANA & LD0 & m23])):
    mc = (nmv == nm) & ANA & m23; mb = mc & LD0
    if mb.sum() >= 10: sk.append((nm, mb.sum(), 100 * OK[mb].mean(), 100 * OK[mc].mean()))
pay = np.mean([a > b_ for _, _, a, b_ in sk]) if sk else np.nan; K4 = len(sk) >= 3 and pay >= 0.6
yaz(f"**K4 yaygınlık:** {sum(a > b_ for _, _, a, b_ in sk)}/{len(sk)} coin'de daha isabetli → {'✅' if K4 else '❌'}  ·  " + " · ".join(f"{nm} {n} sinyal %{a:.0f} vs %{b_:.0f}" for nm, n, a, b_ in sk))

# ---- KÖTÜ yön (KX) ----
OA3 = st(ANA, D3); OL3 = st(ANA & LD0, D3)
KX0 = all(OL3[dn][0] >= mn and OL3[dn][1] <= OA3[dn][1] - 2 and OL3[dn][2] <= OA3[dn][2] - 0.10 for dn, mn in (("2023", 30), ("2024+", 30), ("2026", 10)))
p5h = np.nanpercentile(PLS[:, 0], 5); KX1 = bool(G1[0] < p5h)
LTIYI = K1 and K2 and K3 and K4
yaz(f"\n**KX kötü yön:** üç dönemde zayıf {'✅' if KX0 else '❌'} · plasebo (2024+ isabet farkı {G1[0]:+.1f}, %5'lik {p5h:+.1f}) {'✅' if KX1 else '❌'}")
yaz("\n## Önceden yazılı karar\n" + ("- ✅ İYİ yönde geçti → öncelik işareti adayı" if LTIYI else ("- ⚠️ KÖTÜ yönde geçti → uyarı adayı" if KX0 and KX1 else "- ➖ Etkisiz ya da kanıtsız → eklenmez")))
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("ld_tavan_sonuc.md", "w").write("\n".join(L) + "\n")
