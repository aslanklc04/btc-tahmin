# ld_yedek.py — 23.10.2026 (kullanıcı: "diğer testleri de yap, uygunsa canlıya alalım"): 💧 likidite dipte, 🔸 yedek ve 📋 panelden türlerinde (yalnız test).
# 💧 = coin'in Binance vadeli emir defteri ±%1 derinliği (bookDepth arşivi, saatlik) son 720 saate göre z ≤ −2 (ld_genis / ld_kontrol ile aynı; canlıda Neon ölçümü, uyumu neon_uyum.py'de doğrulandı).
# Aileler: 🔸 yedek (🌐🤝 eşik altı) · 📋 panelden 💵 · 🧪 ana coin · 🔇/🪙 · hepsi. Çıkış: ailenin canlı hedefi (yedek 0,50σ · panelden 0,45σ), ayrıca ana hedefi 0,75σ ve süre sonu.
# ÖNCEDEN YAZILI ŞART (sonuç görülmeden):
#   (A) İŞARET: aile + 💧, ailenin kendi hedefiyle 2024–25 VE 2026'da isabette ailenin tamamından ≥ 3 puan yüksek ve işlem başı net ≥ ailenin neti (n ≥ 20 / 8) → o ailenin mesajında 💧 gösterilir.
#   (B) ANAYA YÜKSELTME: aile + 💧, ANA hedefiyle (0,75σ) üç dönemin her birinde isabet ≥ %70, saat ve gün bazında ≥ %65, net > 0 (n ≥ 20 / 20 / 8; 2022–23'te derinlik verisi azsa 15)
#       VE plasebo: 💧 dizisi her coin'de rastgele 72–2000 saat kaydırılır (20 kez), gerçek 2024+ isabet farkı plasebo %95'lik değerinden büyük → 💧 olan bu aile sinyalleri ✅ ana olur.
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
Y3m = YED & ~MOM; Y3 = pd.DataFrame({"tur": "🔇/🪙", "nm": nmv[Y3m], "t": pd.DatetimeIndex(Ez.t.values[Y3m]), "H": Ez.H.values[Y3m], "net": Ez.net.values[Y3m], "z": z[Y3m], "rz": RZ[Y3m], "kay": "çekirdek"})
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
E = pd.concat([d.assign(t=utc(d.t)) for d in [C, Y3] + GV if len(d)], ignore_index=True); E["t"] = pd.to_datetime(E.t, utc=True).dt.as_unit("ns"); E = E[np.isfinite(E.net)].sort_values("t").reset_index(drop=True); E["ok"] = (E.net > 0).astype(float)
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

# ======================= ADAY HAVUZU =======================
YED_CUR = ((E.tur.isin(["💵", "🧪"]) & ~E.dip) | (E.tur == "🔇/🪙")).values
A_ = E[~YED_CUR].assign(aile="ANA"); Y_ = E[YED_CUR].copy()
Y_["aile"] = np.select([Y_.tur == "💵", Y_.tur == "🧪"], ["Y1 💵", "Y2 🧪 ana coin"], default="Y3 🔇/🪙")
Pm = GON & ~MOM
P_ = pd.DataFrame({"aile": np.where(ail[Pm] == BTC_A, "P2 BTC saatlik/⭐/A", "P1 coin primi < 0"), "tur": "P", "nm": nmv[Pm], "t": utc(pd.DatetimeIndex(Ez.t.values[Pm])), "H": Ez.H.values[Pm], "net": Ez.net.values[Pm], "z": z[Pm], "rz": RZ[Pm]})
GL = []
for nm in sorted(GEN):
    PR = prim(nm)
    if PR is None: continue
    zs = PR.z; lr = np.log(PR.c); sg = lr.diff().rolling(720, min_periods=168).std(); rzs = (lr - lr.shift(24)) / (sg * np.sqrt(24))
    p = bul(f"ga/**/disa_{nm}USDT.pkl")
    if p:
        X = pd.read_pickle(p); X.index = utc(X.index); st_, u4_, ac_ = (X[k].fillna(False).astype(bool).values for k in ("star", "u4", "acls"))
        ev = events((st_ | u4_ | ac_) & X.y4.notna().values, 4); t = X.index[ev]; bu4 = Bg.u4.reindex(t).fillna(False).astype(bool).values; zz = zs.reindex(t).values
        m = bu4 & (zz >= 0) & (zz < 2); GL.append(pd.DataFrame({"aile": "G1 🌐🤝 z 0…2", "tur": "G", "nm": nm, "t": t[m], "H": 4, "net": np.exp(X.y4.values[ev][m]) - 1 - 0.0004, "z": zz[m], "rz": rzs.reindex(t[m]).values}))
    p = bul(f"ga/**/disa24_{nm}USDT.pkl")
    if p:
        D = pd.read_pickle(p).astype("float64"); D.index = utc(D.index); D = D.reindex(pd.date_range(D.index[0], D.index[-1], freq="1h")); c = D.close.ffill(limit=3).values; n = len(D)
        mk = np.nan_to_num(((D.S24 > 0) & (D.C24 >= D.T10_24)).values).astype(bool) & D.T10_24.notna().values & (np.arange(n) + 25 < n)
        ev = events(mk, 24); t = D.index[ev]; zz = zs.reindex(t).values; m = (zz >= 0) & (zz < 1.5)
        GL.append(pd.DataFrame({"aile": "G2 🌐🧪 z 0…1,5", "tur": "G", "nm": nm, "t": t[m], "H": 24, "net": (c[ev + 24] / c[ev] - 1)[m] - 0.0004, "z": zz[m], "rz": rzs.reindex(t[m]).values}))
Q = pd.concat([A_, Y_, P_] + [g.assign(t=utc(g.t)) for g in GL if len(g)], ignore_index=True)
Q["t"] = pd.to_datetime(Q.t, utc=True).dt.as_unit("ns"); Q = Q[np.isfinite(Q.net.astype(float))].reset_index(drop=True); Q["net"] = Q.net.astype(float)
tq = pd.DatetimeIndex(Q.t); OK = (Q.net.values > 0); NET = 100 * Q.net.values; AIL = Q.aile.values; nmq = Q.nm.values
ANA = AIL == "ANA"
P0x, A24x, A26x = pd.Timestamp("2022-06-01", tz="UTC"), pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")
D3 = (("2022-06→2023", (tq >= P0x) & (tq < A24x)), ("2024+", tq >= A24x), ("2026", tq >= A26x)); m24 = tq >= A24x
MIN = {"2022-06→2023": 30, "2024+": 30, "2026": 10}; HAFTA = {"2022-06→2023": (A24x - P0x).days / 7, "2024+": (tq.max() - A24x).days / 7, "2026": (tq.max() - A26x).days / 7}
def st(m): return {dn: (int((m & md).sum()), 100 * OK[m & md].mean() if (m & md).any() else np.nan, NET[m & md].mean() if (m & md).any() else np.nan) for dn, md in D3}
def sat(ad, o, hf=False): return f"{ad[:46]:46s}" + " | ".join(f"{o[dn][0]:5d}{(' (' + format(o[dn][0] / HAFTA[dn], '4.1f') + '/hf)') if hf else ''} · %{o[dn][1]:4.1f} · {o[dn][2]:+.2f}" for dn in o)
OA = st(ANA)
# ---- koşullar (kay = plasebo kaydırma, gün) ----
RZq = Q.rz.values.astype(float); Zq = Q.z.values.astype(float)
BU4 = Bg.u4.fillna(False).astype(bool); ZB = RAW["BTC"].z
key = pd.Series(nmq).astype(str) + "|" + pd.Series(tq.floor("h").astype(str)); fam = pd.Series(AIL).where(AIL != "ANA", pd.Series(Q.tur.values).astype(str))
cift = (pd.DataFrame({"k": key, "f": fam}).groupby("k").f.transform("nunique") >= 2).values
def kosullar(kay=0):
    sh = pd.Timedelta(days=kay); tt = tq - sh
    def kayd(v):                                                                            # olay-özelliği koşulunu kaydır: aynı coin'in kay gün önceki değeri yerine dizinin kendisi kaydırılır
        if kay == 0: return v
        s = pd.Series(v, index=tq); out = np.zeros(len(v), bool)
        for nm in np.unique(nmq):
            m = nmq == nm; si = s[m]; si = si[~si.index.duplicated()].sort_index(); out[m] = si.reindex(tq[m] - sh, method="nearest", tolerance=pd.Timedelta(days=3)).fillna(False).values.astype(bool)
        return out
    return {"K1 📉 dip": kayd(RZq <= -2), "K2 🚀 momentum": kayd(RZq >= 2), "K3 🔥 BTC fonlama": np.nan_to_num(asof(tt), nan=-9) >= 2,
            "K4 BTC 4s ÇG ↑": BU4.reindex(tt).fillna(False).values.astype(bool), "K5 coin primi ≥ 1": kayd(np.nan_to_num(Zq, nan=-9) >= 1),
            "K6 BTC ⛔": np.nan_to_num(ZB.reindex(tt).values, nan=9) <= -1, "K7 BTC −1…0": (lambda zb: (zb > -1) & (zb <= 0))(np.nan_to_num(ZB.reindex(tt).values, nan=9)),
            "K8 çifte onay": kayd(cift)}
K0 = kosullar(0); FON = K0["K3 🔥 BTC fonlama"]; TUR = Q.tur.values.astype(str); DIP = (RZq <= -2) & ~np.isin(nmq, list(GEN))
L.clear()
# ÖNCEDEN YAZILI ŞART: hedef = giriş × (1 + k·σ), σ = coin'in son 720 saatlik saatlik oynaklığı × √süre (giriş anında bilinir); süre içinde saatlik YÜKSEK hedefe değerse
#   hedeften (limit) çıkılır, değmezse süre sonu kapanışından. Bir k ancak ÜÇ dönemde de (2022-06→2023 · 2024–25 · 2026) isabet ≥ %65 VE saat bazında isabet ≥ %60
#   VE işlem başı net > 0 ise "%65 şartını sağlıyor" sayılır. Kâr kaybı ayrıca raporlanır (karar kullanıcıya).
P1 = AIL == "P1 coin primi < 0"; YED = np.isin(AIL, ["Y1 💵", "Y2 🧪 ana coin", "Y3 🔇/🪙"])
PR_ = [YED & FON & (np.nan_to_num(Zq, nan=0) > -1), P1 & FON & (Zq > -1) & (Zq < 0), P1 & FON & (Zq <= -1), (AIL == "G1 🌐🤝 z 0…2") & FON]
U = np.zeros(len(Q), bool)
for m_ in PR_: U |= m_
ANAF = ANA | U; HQ = Q.H.values.astype(int)
G1Y = (AIL == "G1 🌐🤝 z 0…2") & ~FON; PY = np.isin(AIL, ["Y1 💵", "Y2 🧪 ana coin", "Y3 🔇/🪙"]) & ~FON; HES = ANAF | G1Y | PY
from concurrent.futures import ThreadPoolExecutor
NM = sorted(set(nmq[HES]))
def ohl(nm):
    try: o = fetch_1h(pd.Timestamp("2022-05-01", tz="UTC").timestamp() * 1000, time.time() * 1000, sym=f"{nm}USDT"); o.index = utc(o.index); return nm, o[["high", "close"]].astype(float)
    except Exception as e: return nm, None
with ThreadPoolExecutor(8) as ex: OHL = {k: v for k, v in ex.map(ohl, NM) if v is not None}
KS = [None, 0.45, 0.5, 0.75]; NET_K = {k: np.full(len(Q), np.nan) for k in KS}; F_ = 0.0004
for nm in NM:
    o = OHL.get(nm)
    if o is None: continue
    ii = np.where(HES & (nmq == nm))[0]; c = o.close.values; h = o.high.values; sg = np.log(o.close).diff().rolling(720, min_periods=168).std().values
    pos = o.index.searchsorted(tq[ii])
    for j, p in zip(ii, pos):
        H = HQ[j]
        if p >= len(o) or o.index[p] != tq[j] or p + H >= len(o) or not np.isfinite(sg[p]): continue
        e0 = c[p]; NET_K[None][j] = c[p + H] / e0 - 1 - F_
        for k in KS[1:]:
            hedef = e0 * (1 + k * sg[p] * np.sqrt(H)); w = np.where(h[p + 1:p + H + 1] >= hedef)[0]
            NET_K[k][j] = (hedef / e0 - 1 - F_) if len(w) else (c[p + H] / e0 - 1 - F_)
DON = (("2022-06→2023", (tq >= P0x) & (tq < A24x)), ("2024–25", (tq >= A24x) & (tq < A26x)), ("2026", tq >= A26x)); SELm = DON[0][1]
GUNTR = np.asarray(tq.tz_convert("Europe/Istanbul").floor("D")); SAAT = np.asarray(tq.floor("h"))
def hucre(m, k):
    m = m & np.isfinite(NET_K[k])
    if m.sum() == 0: return dict(n=0, hit=np.nan, net=np.nan, saat=np.nan, gun=np.nan)
    r = NET_K[k][m]; g = pd.Series(r).groupby(SAAT[m]).mean(); d = pd.Series(r).groupby(GUNTR[m]).mean()
    return dict(n=int(m.sum()), hit=100 * (r > 0).mean(), net=100 * r.mean(), saat=100 * (g > 0).mean(), gun=100 * (d > 0).mean())
# ---- yeni koşul dizileri (satır bazında, t anında bilinen) ----
TRh = tq.tz_convert("Europe/Istanbul").hour.values; TRd = tq.tz_convert("Europe/Istanbul").dayofweek.values
ZBq = np.nan_to_num(RAW["BTC"].z.reindex(tq).values, nan=-9)
bcl = np.log(RAW["BTC"].c); bsg = bcl.diff().rolling(720, min_periods=168).std(); B24 = ((bcl - bcl.shift(24)) / (bsg * np.sqrt(24))).reindex(tq).values
R7 = np.full(len(Q), np.nan)
for nm, o in OHL.items():
    m = nmq == nm
    if m.any(): lr = np.log(o.close); sg = lr.diff().rolling(720, min_periods=168).std(); R7[m] = ((lr - lr.shift(168)) / (sg * np.sqrt(168))).reindex(tq[m]).values
FAM = {"🔸 yedek (🌐🤝 eşik altı)": G1Y, "📋 panelden (hepsi)": PY, "  ↳ 💵 ABD alıyor": PY & (AIL == "Y1 💵"), "  ↳ 🧪 24 s ana coin": PY & (AIL == "Y2 🧪 ana coin"), "  ↳ 🔇/🪙 coin tek": PY & (AIL == "Y3 🔇/🪙")}
anasaat = set(SAAT[ANAF])
def kalab(fm):
    c = pd.Series(1, index=np.where(fm)[0]).groupby(SAAT[fm]).transform("size"); out = np.zeros(len(Q)); out[c.index] = c.values; return out
KOS = {k: v for k, v in K0.items() if not k.startswith("K3") and not k.startswith("K4")}
KOS.update({"K6' BTC ⛔ değil": ~K0["K6 BTC ⛔"], "N1 BTC primi > 0": ZBq > 0, "N2 coin primi ≥ 0,5": np.nan_to_num(Zq, nan=-9) >= 0.5,
            "N3a TR 09–17": (TRh >= 9) & (TRh < 17), "N3b TR 17–01": (TRh >= 17) | (TRh < 1), "N3c TR 01–09": (TRh >= 1) & (TRh < 9),
            "N4a hafta içi": TRd < 5, "N4b hafta sonu": TRd >= 5, "N5a coin 24 s düşmüş": np.nan_to_num(RZq, nan=9) <= 0, "N5b coin 24 s yükselmiş": np.nan_to_num(RZq, nan=-9) > 0,
            "N6a BTC 24 s düşmüş": np.nan_to_num(B24, nan=9) <= 0, "N6b BTC 24 s yükselmiş": np.nan_to_num(B24, nan=-9) > 0,
            "N7a coin 7 g düşmüş": np.nan_to_num(R7, nan=9) <= 0, "N7b coin 7 g yükselmiş": np.nan_to_num(R7, nan=-9) > 0,
            "N9a aynı saatte ✅ ana var": np.isin(SAAT, list(anasaat)), "N9b aynı saatte ✅ ana yok": ~np.isin(SAAT, list(anasaat))})
def ara(KK, plas=False):
    res = []
    for fad, fm in FAM.items():
        kb = kalab(fm)
        if plas: idx_ = ordr[fad]; kb[idx_] = np.roll(kb[idx_], int(rg.integers(len(idx_) // 10, 9 * len(idx_) // 10)))
        K_ = dict(KK); K_["N8a kalabalık saat (≥ 4)"] = kb >= 4; K_["N8b sakin saat (≤ 2)"] = (kb >= 1) & (kb <= 2)
        for k in (0.75, 0.5):
            taban = hucre(fm & SELm, k)["hit"]; tek = []
            for kad, km in K_.items():
                s_ = hucre(fm & km & SELm, k)
                if s_["n"] >= 30 and s_["hit"] >= 63 and s_["hit"] >= taban + 3: tek.append((s_["hit"], kad, km))
            tek.sort(key=lambda x: -x[0]); C = [(b, c) for a, b, c in tek]
            for a in range(min(5, len(tek))):
                for b in range(a + 1, min(5, len(tek))):
                    m2 = tek[a][2] & tek[b][2]; s_ = hucre(fm & m2 & SELm, k)
                    if s_["n"] >= 30 and s_["hit"] >= 63 and s_["hit"] >= taban + 3: C.append((tek[a][1] + " + " + tek[b][1], m2))
            for kad, km in C:
                a_, b_, c_ = (hucre(fm & km & dm, k) for _, dm in DON)
                gec = b_["n"] >= 30 and c_["n"] >= 10 and all(x["hit"] >= 65 and x["saat"] >= 65 and x["gun"] >= 65 and x["net"] > 0 for x in (b_, c_))
                res.append(dict(aile=fad, k=k, kural=kad, a=a_, b=b_, c=c_, gec=gec, pay=(fm & km).sum() / max(fm.sum(), 1)))
    return res
DER = {}
for p in glob.glob("dart/**/derinlik_parca*.pkl", recursive=True): DER.update(pd.read_pickle(p))
for p in glob.glob("der/**/derinlik.pkl", recursive=True):
    for k_, v_ in pd.read_pickle(p).items():
        if k_ not in DER: DER[k_] = v_
def z720(x): return (x - x.rolling(720, min_periods=168).mean()) / (x.rolling(720, min_periods=168).std() + 1e-12)
LDS = {}
for nm, D in DER.items():
    if not {"ask1", "bid1"} <= set(D.columns): continue
    D = D.copy(); D.index = utc(D.index); D = D[~D.index.duplicated()].sort_index(); D = D.reindex(pd.date_range(D.index.min(), D.index.max(), freq="1h"))
    LDS[nm] = z720(np.log(D.ask1 + D.bid1))
def ldmask(kay=None):
    out = np.zeros(len(Q), bool); var = np.zeros(len(Q), bool)
    for nm, zs in LDS.items():
        m = nmq == nm
        if not m.any(): continue
        z_ = zs if kay is None else zs.shift(int(kay[nm]))
        v = z_.reindex(tq[m]).values; var[m] = np.isfinite(v); out[m] = np.nan_to_num(v, nan=0) <= -2
    return out, var
LD, LDV = ldmask()
FAM = {"🔸 yedek (🌐🤝 eşik altı)": (G1Y, 0.5), "📋 panelden — hepsi": (PY, 0.45), "  ↳ 💵 ABD alıyor": (PY & (AIL == "Y1 💵"), 0.45),
       "  ↳ 🧪 24 s ana coin": (PY & (AIL == "Y2 🧪 ana coin"), 0.45), "  ↳ 🔇/🪙 coin tek": (PY & (AIL == "Y3 🔇/🪙"), 0.45)}
MINB = {"2022-06→2023": 15, "2024–25": 20, "2026": 8}
yaz(f"# 💧 Likidite dipte — yedek ve panelden — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}")
yaz(f"derinlik verisi: {len(LDS)} coin · aile satırlarının derinlik verisi olan payı: " + " · ".join(f"{k.strip()} %{100 * (fm & LDV).sum() / max(fm.sum(), 1):.0f}" for k, (fm, _) in FAM.items()))
yaz("_Hücre: n · isabet · net % · saat % · gün % — yalnız derinlik verisi olan sinyaller. Dönemler: 2022-06→2023 · 2024–25 · 2026 (derinlik arşivi 2026-09 sonuna kadar)._\n")
f_ = lambda x: f"{x['n']:>5} · %{x['hit']:3.0f} · {x['net']:+5.2f} · s%{x['saat']:3.0f} · g%{x['gun']:3.0f}" if x["n"] else f"{'—':^40s}"
SONUC = {}
for fad, (fm, kf) in FAM.items():
    F = fm & LDV
    yaz(f"## {fad.strip()}\n```")
    for ad, m, k in (("hepsi · kendi hedefi", F, kf), ("💧 · kendi hedefi", F & LD, kf), ("hepsi · ana hedefi 0,75σ", F, 0.75), ("💧 · ana hedefi 0,75σ", F & LD, 0.75), ("hepsi · süre sonu", F, None), ("💧 · süre sonu", F & LD, None)):
        yaz(f"{ad:26s} | " + " | ".join(f_(hucre(m & dm, k)) for _, dm in DON))
    yaz("```")
    a_ok = all((lambda h, t: h["n"] >= (20 if dn == "2024–25" else 8) and h["hit"] >= t["hit"] + 3 and h["net"] >= t["net"])(hucre(F & LD & dm, kf), hucre(F & dm, kf)) for dn, dm in DON[1:])
    b_ok = all((lambda h: h["n"] >= MINB[dn] and h["hit"] >= 70 and h["saat"] >= 65 and h["gun"] >= 65 and h["net"] > 0)(hucre(F & LD & dm, 0.75)) for dn, dm in DON)
    SONUC[fad] = dict(A=a_ok, B=b_ok, F=F)
    yaz(f"(A) işaret: {'✅' if a_ok else '❌'} · (B) anaya yükseltme (plasebo öncesi): {'✅' if b_ok else '❌'}\n")
open("ld_yedek_sonuc.md", "w").write("\n".join(L) + "\n")
m24 = np.asarray(tq >= A24x)
def fark(F, ldm, k): a, b = hucre(F & ldm & m24, k), hucre(F & m24, k); return a["hit"] - b["hit"] if a["n"] else np.nan
rg = np.random.default_rng(5); PL = {k: [] for k in SONUC}
for it in range(20):
    kay = {nm: int(rg.integers(72, 2001)) for nm in LDS}; ldp, _ = ldmask(kay)
    for fad, (fm, kf) in FAM.items(): PL[fad].append(fark(SONUC[fad]["F"], ldp, 0.75))
    print(f"plasebo {it + 1}", flush=True)
yaz("## Plasebo (2024+ isabet farkı, ana hedefi 0,75σ; 20 kaydırma)\n```")
for fad, (fm, kf) in FAM.items():
    g = fark(SONUC[fad]["F"], LD, 0.75); p95 = np.nanpercentile(PL[fad], 95) if np.isfinite(PL[fad]).any() else np.nan; ok = np.isfinite(g) and np.isfinite(p95) and g > p95
    SONUC[fad]["P"] = ok; yaz(f"{fad.strip():28s} gerçek fark {g:+5.1f} puan · plasebo %95 {p95:+5.1f} → {'✅' if ok else '❌'}")
yaz("```\n## KARAR (önceden yazılı)")
for fad in FAM:
    r = SONUC[fad]; yaz(f"- {fad.strip()}: (A) 💧 işareti {'✅ gösterilir' if r['A'] else '❌ gösterilmez'} · (B) 💧 olunca ✅ anaya yükselir: {'✅' if r['B'] and r['P'] else '❌'}")
open("ld_yedek_sonuc.md", "w").write("\n".join(L) + "\n")
