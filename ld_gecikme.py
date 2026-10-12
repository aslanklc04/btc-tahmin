# ld_gecikme.py — 💧 LİKİDİTE DİPTE'yi CANLIDA KULLANMANIN BEDAVA YOLU: Binance'in GÜNLÜK ARŞİVİ (data.binance.vision, GitHub'dan açık) gecikmeli de olsa yeter mi?
# ld_kontrol.py'de LD sağlamlık testini geçti (K1–K4), ancak anlık emir defteri Binance vadeli API'sinden gelir ve ABD sunucularından (GitHub) kapalı.
# Arşivde gün X'in dosyası X+1 günü bir süre sonra yayınlanır (gecikme S3 kayıtlarından ölçülür; %90'lık değer kullanılır = temkinli).
# Canlıda bir saatte bilinen = yayınlanmış en son günün sonuna kadarki derinlik → koşul 0–24 saat + yayın gecikmesi kadar eski.
# Varyantlar: G0 anlık (karşılaştırma için, canlıda yok) · G1 arşivdeki en son saat LD · G2 arşivdeki son 24 saatte en az bir kez LD.
# ÖNCEDEN YAZILI KARAR (12.10.2026, sonuçlar görülmeden): G1 ya da G2 (ikisi de geçerse daha çok sinyal veren) canlıya alınır ancak:
#   (a) ✅ ana sinyallerde üç dönemde (2023 · 2024+ · 2026) isabet ≥ ana +2 puan VE net ≥ ana +0,10 (en az 30 / 30 / 10),
#   (b) 40 kaydırmalı plasebo dağılımında 2024+ isabet ve net farkı %95'lik değerin üstünde,
#   (c) dip/momentum dışı ana sinyallerde (|z| < 2) de isabet ≥ +2 puan VE net ≥ +0,10 (en az 20 / 20 / 10; 2026'da 10'dan azsa yalnız 2023 ve 2024+).
#   Canlıda kullanım: ✅ ana sinyale 💧 işareti ve öncelik (sinyal sayısı değişmez).
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
# ---------------- arşiv yayın gecikmesi (S3 kayıtları) ----------------
import requests, re
def s3(prefix):
    out, mk = [], ""
    for _ in range(10):
        try: r = requests.get("https://s3-ap-northeast-1.amazonaws.com/data.binance.vision", params={"delimiter": "/", "prefix": prefix, "marker": mk}, timeout=60); x = r.text
        except Exception: break
        ks = re.findall(r"<Key>([^<]+)</Key>\s*<LastModified>([^<]+)</LastModified>", x); out += ks
        if "<IsTruncated>true</IsTruncated>" not in x or not ks: break
        mk = ks[-1][0]
    return out
GEC = []
for sym in ("BTCUSDT", "ETHUSDT", "DOGEUSDT"):
    for k, lm in s3(f"data/futures/um/daily/bookDepth/{sym}/"):
        m_ = re.search(r"(\d{4}-\d{2}-\d{2})\.zip$", k)
        if m_:
            g = pd.Timestamp(m_.group(1), tz="UTC")
            if g >= pd.Timestamp("2026-07-01", tz="UTC"): GEC.append((pd.Timestamp(lm) - (g + pd.Timedelta(days=1))).total_seconds() / 3600)
GEC = np.array(GEC); D90 = int(np.ceil(np.percentile(GEC, 90))) if len(GEC) >= 20 else 24; D90 = max(D90, 1)
yaz(f"# 💧 Likidite dipte — Binance arşivi ile gecikmeli kullanım — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n"
    f"Arşiv yayın gecikmesi (gün bitiminden sonra, son 3 ay, {len(GEC)} dosya): medyan {np.median(GEC) if len(GEC) else np.nan:.1f} s · %90 {np.percentile(GEC, 90) if len(GEC) else np.nan:.1f} s · en çok {GEC.max() if len(GEC) else np.nan:.1f} s → testte {D90} s kullanıldı\n")
# ---------------- LD serileri ----------------
DER = pd.read_pickle(f("**/derinlik.pkl")[0])
def z720(s): return (s - s.rolling(720, min_periods=168).mean()) / (s.rolling(720, min_periods=168).std() + 1e-12)
LDS = {}
for nm, D in DER.items():
    if not {"ask1", "bid1"} <= set(D.columns): continue
    ix = pd.date_range(D.index.min(), D.index.max(), freq="1h"); D = D.reindex(ix)
    LDS[nm] = (z720(np.log(D.ask1 + D.bid1)) <= -2).fillna(False)
def ld_var(tt, nm, kip):
    s = LDS[nm]
    if kip == "G0": return s.reindex(tt).fillna(False).values
    a = (tt - pd.Timedelta(hours=D90)).floor("D")                 # arşivde bilinen en son saat (gün sonu)
    if kip == "G1": return s.reindex(a).fillna(False).values
    s24 = s.astype(float).rolling(24, min_periods=1).max() > 0; return s24.reindex(a).fillna(False).values
def ara(kip, kay=0):
    v = np.zeros(len(Ez), bool)
    for nm in LDS:
        m = nmv == nm
        if m.any(): v[m] = ld_var(tz_[m] - pd.Timedelta(hours=kay), nm, kip)
    return v.astype(bool)
P23 = pd.Timestamp("2023-01-01", tz="UTC"); OK, NET = Ez.ok.values, Ez.net.values
D3 = (("2023", (tz_ >= P23) & (tz_ < A24_)), ("2024+", tz_ >= A24_), ("2026", tz_ >= A26_))
def st(m): return {dn: (int((m & md).sum()), 100 * OK[m & md].mean() if (m & md).any() else np.nan, 100 * NET[m & md].mean() if (m & md).any() else np.nan) for dn, md in D3}
def sat(ad, o): return f"{ad:46s}" + " | ".join(f"{o[dn][0]:5d} · %{o[dn][1]:4.1f} · {o[dn][2]:+.2f}" for dn in o)
def ustun(oc, ob, mins, gevsek=False):
    ks = [dn for dn in oc if not (gevsek and dn == "2026" and oc[dn][0] < mins[dn])]
    return len(ks) >= 2 and all(oc[dn][0] >= mins[dn] for dn in ks) and all(oc[dn][1] >= ob[dn][1] + 2 and oc[dn][2] >= ob[dn][2] + 0.10 for dn in ks)
NOR = np.isfinite(RZ) & (np.abs(RZ) < 2); m24 = tz_ >= A24_
OA, ON = st(ANA), st(ANA & NOR)
def fark(c): a = ANA & m24; b = a & c; return (100 * (OK[b].mean() - OK[a].mean()), 100 * (NET[b].mean() - NET[a].mean())) if b.sum() >= 10 else (np.nan, np.nan)
yaz("_sinyal sayısı · isabet · işlem başı net % — 2023 | 2024+ | 2026_\n```"); yaz(sat("✅ ana (hepsi)", OA)); yaz(sat("✅ ana, dip/momentum dışı", ON))
SON = {}
for kip, ad in (("G0", "G0 anlık (canlıda yok, karşılaştırma)"), ("G1", "G1 arşivdeki en son saat"), ("G2", "G2 arşivdeki son 24 saatte")):
    c = ara(kip); oc, on = st(ANA & c), st(ANA & NOR & c)
    a_ = ustun(oc, OA, {"2023": 30, "2024+": 30, "2026": 10}); c_ = ustun(on, ON, {"2023": 20, "2024+": 20, "2026": 10}, gevsek=True)
    g = fark(c); P = np.array([fark(ara(kip, int(d * 24))) for d in np.linspace(30, 400, 40)]); b_ = g[0] > np.nanpercentile(P[:, 0], 95) and g[1] > np.nanpercentile(P[:, 1], 95)
    yaz(sat(f"{ad}", oc)); yaz(sat("   … dip/momentum dışı", on))
    yaz(f"   → (a) ANA+ {'✅' if a_ else '❌'} · (b) plasebo: isabet farkı {g[0]:+.1f} (%95 {np.nanpercentile(P[:, 0], 95):+.1f}), net farkı {g[1]:+.2f} (%95 {np.nanpercentile(P[:, 1], 95):+.2f}) {'✅' if b_ else '❌'} · (c) dipten bağımsız {'✅' if c_ else '❌'}")
    SON[kip] = (a_ and b_ and c_, sum(oc[dn][0] for dn in oc))
yaz("```")
ad_ = {"G1": "G1 arşivdeki en son saat", "G2": "G2 arşivdeki son 24 saatte"}; gec = [k for k in ("G1", "G2") if SON[k][0]]
sec = max(gec, key=lambda k: SON[k][1]) if gec else None
yaz("\n## Önceden yazılı karar\n" + (f"- ✅ **{ad_[sec]}** geçti → 💧 canlıya alınabilir (Binance arşivi, GitHub'dan erişilebilir, ek sunucu gerekmez)" if sec else
    "- ❌ Gecikmeli arşiv yetmiyor → canlı için anlık emir defteri gerekir (ABD dışı küçük sunucu ya da bilgisayarından aktarım)"))
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("ld_gecikme_sonuc.md", "w").write("\n".join(L) + "\n")
