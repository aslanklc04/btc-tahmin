# fon_ana.py — 🔥 BTC FONLAMASI YÜKSEKKEN ✅ ANA SİNYALLER (kullanıcı onayı 14.10.2026: "test et geçerse ekle"; yalnız test).
# Gözlem (fon_coin.py, plasebosuz yan sonuç): KuCoin BTC fonlaması z ≥ 2 iken ✅ ana %65 · %69 · %87 (+2,76 · +1,77 · +1,68) vs hepsi %56 · %59 · %60.
# Koşul canlıdakiyle AYNI (gonder.fon_z): KuCoin XBTUSDTM fonlaması, son 90 ödemeye göre z (min 30), sinyal anındaki son ödeme; z ≥ 2.
# Olaylar: coin_gecmis.py ile aynı ✅ ana sinyaller (çekirdek + 🌐 + 💵, 🚀 dahil).
# ÖNCEDEN YAZILI KARAR (sonuçlar görülmeden; 💧 ile aynı ölçütler):
#   K0 ANA+: üç dönemde (2022-06→2023 · 2024+ · 2026) isabet ≥ hepsi +2 puan VE net ≥ hepsi +0,10 (en az 30 / 30 / 10)
#   K1 40 kaydırmalı plasebo (30–400 gün): 2024+ isabet ve net farkı plasebo %95'lik değerinin üstünde
#   K2 dipten/momentumdan bağımsız (|24 s z| < 2): üç dönemde +2 puan ve +0,10 (20 / 20 / 10; 2026 < 10 ise yalnız ilk ikisi)
#   K3 haftalık blok bootstrap 2024+ net farkı %90 alt sınırı > 0 · K4 ≥ 10 sinyalli coin'lerin ≥ %60'ında daha isabetli (en az 3 coin)
#   → hepsi geçerse canlıda: fonlama yüksek saatte ✅ ana mesajlara 🔥 işareti ve test sonucu notu (sinyal sayısı değişmez).
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
MOM = GON & (RZ >= 2); ANA = ANA | MOM
TURL = np.full(len(Ez), "", object)
for k_, v_ in TUR.items(): TURL[(TURL == "") & v_] = k_
TURL[(TURL == "") & MOM] = "🚀"
C = pd.DataFrame({"tur": TURL[ANA], "nm": nmv[ANA], "t": pd.DatetimeIndex(Ez.t.values[ANA]), "H": Ez.H.values[ANA], "net": Ez.net.values[ANA], "z": z[ANA], "rz": RZ[ANA], "kay": "çekirdek"})
# ---------------- 🌐 geniş liste (ld_genis.py ile aynı) ----------------
bul = lambda p: (glob.glob(p, recursive=True) or [None])[0]
def utc(ix): ix = pd.DatetimeIndex(ix); return (ix.tz_localize("UTC") if ix.tz is None else ix.tz_convert("UTC")).as_unit("ns")
GEN = {l.strip()[:-4] for l in open("canli/durum/genis_liste.txt") if l.strip()}
Bg = pd.read_pickle(bul("ga/**/disa_BTCUSDT.pkl")); Bg.index = utc(Bg.index); GV = []
def prim(nm):
    p = bul(f"ga/**/prim_{nm}USDT.pkl")
    if not p: return None
    d = pd.read_pickle(p).astype("float64"); d.index = utc(d.index); d = d[~d.index.duplicated()].sort_index(); return d
for nm in sorted(GEN):
    PR = prim(nm)
    if PR is None: continue
    zs = PR.z; lr = np.log(PR.c); sg = lr.diff().rolling(720, min_periods=168).std(); rzs = (lr - lr.shift(24)) / (sg * np.sqrt(24))
    p = bul(f"ga/**/disa_{nm}USDT.pkl")
    if p:
        X = pd.read_pickle(p); X.index = utc(X.index); st_, u4_, ac_ = (X[k].fillna(False).astype(bool).values for k in ("star", "u4", "acls"))
        ev = events((st_ | u4_ | ac_) & X.y4.notna().values, 4); t = X.index[ev]; bu4 = Bg.u4.reindex(t).fillna(False).astype(bool).values; zz = zs.reindex(t).values
        m = bu4 & (zz >= 2); GV.append(pd.DataFrame({"tur": "🌐🤝", "nm": nm, "t": t[m], "H": 4, "net": np.exp(X.y4.values[ev][m]) - 1 - 0.0004, "z": zz[m], "rz": rzs.reindex(t[m]).values, "kay": "🌐"}))
    p = bul(f"ga/**/disa24_{nm}USDT.pkl")
    if p:
        D = pd.read_pickle(p).astype("float64"); D.index = utc(D.index); D = D.reindex(pd.date_range(D.index[0], D.index[-1], freq="1h")); c = D.close.ffill(limit=3).values; n = len(D)
        mk = np.nan_to_num(((D.S24 > 0) & (D.C24 >= D.T10_24)).values).astype(bool) & D.T10_24.notna().values & (np.arange(n) + 25 < n)
        ev = events(mk, 24); t = D.index[ev]; zz = zs.reindex(t).values; m = zz >= 1.5
        GV.append(pd.DataFrame({"tur": "🌐🧪", "nm": nm, "t": t[m], "H": 24, "net": (c[ev + 24] / c[ev] - 1)[m] - 0.0004, "z": zz[m], "rz": rzs.reindex(t[m]).values, "kay": "🌐"}))
E = pd.concat([d.assign(t=utc(d.t)) for d in [C] + GV if len(d)], ignore_index=True); E["t"] = pd.to_datetime(E.t, utc=True).dt.as_unit("ns"); E = E[np.isfinite(E.net)].sort_values("t").reset_index(drop=True); E["ok"] = (E.net > 0).astype(float)
E["dip"] = (E.rz <= -2) & ~E.nm.isin(GEN)

# ---------------- KuCoin BTC fonlaması (canlıyla aynı) ----------------
import requests
out, a = [], pd.Timestamp("2022-03-01", tz="UTC")
while a < pd.Timestamp.now(tz="UTC"):
    b = a + pd.Timedelta(days=30)
    for k in range(4):
        try: j = requests.get("https://api-futures.kucoin.com/api/v1/contract/funding-rates", params={"symbol": "XBTUSDTM", "from": int(a.timestamp() * 1000), "to": int(b.timestamp() * 1000)}, timeout=30).json(); break
        except Exception: j = None; time.sleep(2 + 2 * k)
    if isinstance(j, dict) and isinstance(j.get("data"), list): out += j["data"]
    a = b
K_ = pd.DataFrame(out).drop_duplicates("timepoint"); FK = pd.Series(K_.fundingRate.astype(float).values, index=pd.to_datetime(K_.timepoint.astype("int64"), unit="ms", utc=True)).sort_index()
FZ = (FK - FK.rolling(90, min_periods=30).mean()) / (FK.rolling(90, min_periods=30).std() + 1e-12); FZ = FZ.dropna()
def asof(zaman):
    zaman = pd.DatetimeIndex(zaman).as_unit("ns"); fi = FZ.index.as_unit("ns"); i = fi.searchsorted(zaman, side="right") - 1
    return np.where(i >= 0, FZ.values[np.clip(i, 0, None)], np.nan)
tz_, nmv = pd.DatetimeIndex(E.t), E.nm.values; OK, NET = (E.net.values > 0), E.net.values
def kos(kay=0): return np.nan_to_num(asof(tz_ - pd.Timedelta(hours=kay)), nan=-9) >= 2
P0x, A24x, A26x = pd.Timestamp("2022-06-01", tz="UTC"), pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")
D3 = (("2022-06→2023", (tz_ >= P0x) & (tz_ < A24x)), ("2024+", tz_ >= A24x), ("2026", tz_ >= A26x)); m24 = tz_ >= A24x
def st(m): return {dn: (int((m & md).sum()), 100 * OK[m & md].mean() if (m & md).any() else np.nan, 100 * NET[m & md].mean() if (m & md).any() else np.nan) for dn, md in D3}
def sat(ad, o): return f"{ad[:40]:40s}" + " | ".join(f"{o[dn][0]:5d} · %{o[dn][1]:4.1f} · {o[dn][2]:+.2f}" for dn in o)
def ustun(oc, ob, mins, gevsek=False):
    ks = [dn for dn in oc if not (gevsek and dn == "2026" and oc[dn][0] < mins[dn])]
    return len(ks) >= 2 and all(oc[dn][0] >= mins[dn] for dn in ks) and all(oc[dn][1] >= ob[dn][1] + 2 and oc[dn][2] >= ob[dn][2] + 0.10 for dn in ks)
A_ = np.ones(len(E), bool); NOR = np.isfinite(E.rz.values) & (np.abs(E.rz.values) < 2); C0 = kos(); OA = st(A_)
yaz(f"# 🔥 BTC fonlaması yüksekken ✅ ana sinyaller — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n"
    f"✅ ana sinyal: {len(E):,} · coin {E.nm.nunique()} · KuCoin ödeme: {len(FK):,} ({FK.index[0]:%Y-%m-%d} → {FK.index[-1]:%Y-%m-%d}) · fonlama z ≥ 2 olan ödeme: %{100 * (FZ >= 2).mean():.1f} · {time.time()-T0:.0f} sn\n")
yaz("_sinyal sayısı · isabet · işlem başı net % — 2022-06→2023 | 2024+ | 2026_\n```")
yaz(sat("✅ ana (hepsi)", OA)); yaz(sat("✅ ana + 🔥 fonlama z ≥ 2", st(A_ & C0)))
for k_ in ("çekirdek", "🌐"):
    mk = E.kay.values == k_; yaz(sat(f"  {k_}", st(mk))); yaz(sat(f"  {k_} + 🔥", st(mk & C0)))
yaz(sat("dip/momentum dışı", st(A_ & NOR))); yaz(sat("dip/momentum dışı + 🔥", st(A_ & NOR & C0))); yaz("```")
K0 = ustun(st(A_ & C0), OA, {"2022-06→2023": 30, "2024+": 30, "2026": 10})
def fark(c): a = A_ & m24; b = a & c; return (100 * (OK[b].mean() - OK[a].mean()), 100 * (NET[b].mean() - NET[a].mean())) if b.sum() >= 10 else (np.nan, np.nan)
G1 = fark(C0); PLS = np.array([fark(kos(int(g * 24))) for g in np.linspace(30, 400, 40)])
p95h, p95n = np.nanpercentile(PLS[:, 0], 95), np.nanpercentile(PLS[:, 1], 95); K1 = bool(G1[0] > p95h and G1[1] > p95n)
K2 = ustun(st(A_ & NOR & C0), st(A_ & NOR), {"2022-06→2023": 20, "2024+": 20, "2026": 10}, gevsek=True)
b = A_ & C0 & m24; lo_, hi_ = wboot(NET[b] - NET[A_ & m24].mean(), tz_[b]); K3 = bool(lo_ > 0)
sk = []
for nm in sorted(set(nmv)):
    mc = (nmv == nm) & (tz_ >= P0x); mb = mc & C0
    if mb.sum() >= 10: sk.append((nm, int(mb.sum()), 100 * OK[mb].mean(), 100 * OK[mc].mean()))
K4 = len(sk) >= 3 and np.mean([a > b2 for _, _, a, b2 in sk]) >= 0.6
i = lambda x: "✅" if x else "❌"
yaz(f"\n- **K0 ANA+:** {i(K0)}")
yaz(f"- **K1 plasebo (2024+, 40 kaydırma):** isabet farkı {G1[0]:+.1f} (plasebo %95 {p95h:+.1f}) · net farkı {G1[1]:+.2f} (plasebo %95 {p95n:+.2f}) → {i(K1)}")
yaz(f"- **K2 dipten/momentumdan bağımsız:** {i(K2)}")
yaz(f"- **K3 bootstrap (2024+ net farkı %90):** {100*lo_:+.2f} … {100*hi_:+.2f} → {i(K3)}")
yaz(f"- **K4 yaygınlık:** {sum(a > b2 for _, _, a, b2 in sk)}/{len(sk)} coin → {i(K4)} · " + " · ".join(f"{nm} {n} %{a:.0f} vs %{b2:.0f}" for nm, n, a, b2 in sk))
CUR = ~(np.isin(E.tur.values, ["💵", "🧪"]) & ~(E.rz.values <= -2))
yaz("\n_Bilgi (14.10 sonrası ana seti: 💵 ve ana coin 🧪 yalnız 📉 dip iken):_\n```"); yaz(sat("✅ ana (14.10 seti)", st(A_ & CUR))); yaz(sat("✅ ana (14.10 seti) + 🔥", st(A_ & CUR & C0))); yaz("```")
GEC = K0 and K1 and K2 and K3 and K4
o = st(A_ & C0)
yaz("\n## Önceden yazılı karar\n" + (f"- ✅ **GEÇTİ** → canlıda fonlama yüksek saatte ✅ ana mesajlara 🔥 işareti (isabet " + " · ".join(f"%{o[dn][1]:.0f}" for dn in o) + ", net " + " · ".join(f"+{o[dn][2]:.2f}" for dn in o) + ")" if GEC else "- ❌ geçmedi → eklenmez"))
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("fon_ana_sonuc.md", "w").write("\n".join(L) + "\n")
