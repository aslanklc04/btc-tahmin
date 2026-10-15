# coin_sinif.py — COIN'E GÖRE ANA / YEDEK (kullanıcı fikri 15.10.2026: "bu sinyal bu coinde 3 dönemde de çok iyi işlediyse ana yap"; yalnız test, canlıya bir şey eklenmez).
# Olaylar: fon_ana.py ile aynı (✅ ana çekirdek + 🌐 + 💵, 🚀 dahil) + Y3 🔇/🪙 coin tek (coin primi ≥ 0). Şimdiki sınıf = 14.10 kuralları:
#   🔸 yedek = 💵 ve ana coin 🧪 (📉 dip değilse) + 🔇/🪙 · ✅ ana = geri kalan hepsi.
# HİLESİZ ÖLÇÜM: her sinyalde coin×tür geçmişi YALNIZ o anda çıkışı tamamlanmış önceki sinyallerden (ileriye bakmadan). Değerlendirme dönemleri 2022-06→2023 · 2024+ · 2026.
# Varyantlar (önceden sabit):
#   V1 geçmiş ortalaması: coin×tür geçmişinde ≥ 20 sinyal · İYİ = isabet ≥ %60 VE net ≥ +0,60 · KÖTÜ = isabet < %52 VEYA net < 0
#   V2 "her dönemde iyi" (kullanıcının dediği): geçmiş takvim yıllarından ≥ 8 sinyalli en az 2 yıl · İYİ = her yılda isabet ≥ %58 VE net > +0,30 · KÖTÜ = her yılda isabet < %55 VE net < 0
#   Uygulama: P (yükselt) = İYİ hücredeki 🔸 yedek → ✅ ana · D (indir) = KÖTÜ hücredeki ✅ ana → 🔸 yedek
# ÖNCEDEN YAZILI KARAR (sonuçlar görülmeden):
#   P GEÇER: yükselen sinyaller üç dönemde ana çizgisini geçer (isabet ≥ %55,9 · %58,6 · %59,1 VE net ≥ +0,30 · +0,647 · +0,589; en az 30 / 30 / 10)
#            VE yükselmeyen yedeklerden 2024+ ve 2026'da isabet +3 puan üstün VE plasebo (coin geçmişleri tür içinde coin'ler arası karıştırılır, 40 kez):
#            2024+ yükselen isabeti plasebo %95'in üstünde.
#   D GEÇER: inen sinyaller üç dönemde kalan ana'dan isabet ≥ 3 puan VE net ≥ 0,20 düşük (en az 30 / 30 / 10) VE yeni ana seti üç dönemde isabet ve net olarak şimdikinden
#            düşük değil VE plasebo: 2024+ inenlerin isabeti plasebo %5'in altında.
#   Geçen parça(lar) önerilir; hiçbiri geçmezse fikir canlıya girmez. "Hileli" (tüm dönemleri bilerek seçilen) sürüm yalnız karşılaştırma için yazılır.
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

# ======================= COIN'E GÖRE ANA / YEDEK =======================
E["cikis"] = E.t + pd.to_timedelta(E.H.astype(int), unit="h"); E["yil"] = E.t.dt.year
YED_CUR = (E.tur.isin(["💵", "🧪"]) & ~E.dip) | (E.tur == "🔇/🪙"); ANA_CUR = ~YED_CUR
tz_ = pd.DatetimeIndex(E.t); OK = E.ok.values.astype(bool); NET = 100 * E.net.values
P0x, A24x, A26x = pd.Timestamp("2022-06-01", tz="UTC"), pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")
D3 = (("2022-06→2023", (tz_ >= P0x) & (tz_ < A24x)), ("2024+", tz_ >= A24x), ("2026", tz_ >= A26x))
BENx = {"2022-06→2023": (55.9, 0.30), "2024+": (58.6, 0.647), "2026": (59.1, 0.589)}; MIN = {"2022-06→2023": 30, "2024+": 30, "2026": 10}
HAFTA = {"2022-06→2023": (A24x - P0x).days / 7, "2024+": (tz_.max() - A24x).days / 7, "2026": (tz_.max() - A26x).days / 7}
def st(m): return {dn: (int((m & md).sum()), 100 * OK[m & md].mean() if (m & md).any() else np.nan, NET[m & md].mean() if (m & md).any() else np.nan) for dn, md in D3}
def sat(ad, o, hafta=False): return f"{ad[:44]:44s}" + " | ".join(f"{o[dn][0]:5d}{(' (' + format(o[dn][0] / HAFTA[dn], '4.1f') + '/hf)') if hafta else ''} · %{o[dn][1]:4.1f} · {o[dn][2]:+.2f}" for dn in o)
YILLAR = sorted(E.yil.unique()); YI = {y: i for i, y in enumerate(YILLAR)}
GR = {}                                                                                      # (coin, tür) → çıkışa göre sıralı birikimli toplamlar (yıl yıl)
for (nm, tur), g in E.groupby(["nm", "tur"]):
    g = g.sort_values("cikis"); ny = len(YILLAR); n = len(g)
    Y = np.zeros((n + 1, ny)); W = np.zeros((n + 1, ny)); S = np.zeros((n + 1, ny))
    yi = g.yil.map(YI).values
    Y[np.arange(1, n + 1), yi] = 1; W[np.arange(1, n + 1), yi] = g.ok.values; S[np.arange(1, n + 1), yi] = 100 * g.net.values
    GR[(nm, tur)] = (pd.DatetimeIndex(g.cikis).as_unit("ns").asi8, Y.cumsum(0), W.cumsum(0), S.cumsum(0))
def sinifla(esle=None):
    """her sinyal için (V1, V2) etiketi: 1 = İYİ, -1 = KÖTÜ, 0 = belirsiz. esle: tür içinde coin → başka coin (plasebo)."""
    v1 = np.zeros(len(E), int); v2 = np.zeros(len(E), int)
    for (nm, tur), idx in E.groupby(["nm", "tur"]).groups.items():
        hk = (esle[tur].get(nm, nm) if esle else nm, tur)
        if hk not in GR: continue
        cx, CY, CW, CS = GR[hk]; idx = np.asarray(idx)
        i = np.searchsorted(cx, tz_[idx].as_unit("ns").asi8, side="left")                   # çıkışı sinyal anından önce olanlar
        ny_, nw_, ns_ = CY[i], CW[i], CS[i]; n = ny_.sum(1); h = 100 * nw_.sum(1) / np.maximum(n, 1); a = ns_.sum(1) / np.maximum(n, 1)
        v1[idx] = np.where(n >= 20, np.where((h >= 60) & (a >= 0.60), 1, np.where((h < 52) | (a < 0), -1, 0)), 0)
        q = ny_ >= 8; nq = q.sum(1)
        with np.errstate(invalid="ignore", divide="ignore"):
            hy = 100 * nw_ / ny_; ay = ns_ / ny_
        iyi = np.all(~q | ((hy >= 58) & (ay > 0.30)), 1); kotu = np.all(~q | ((hy < 55) & (ay < 0)), 1)
        v2[idx] = np.where(nq >= 2, np.where(iyi, 1, np.where(kotu, -1, 0)), 0)
    return v1, v2
V1, V2 = sinifla()
yaz(f"# 🪙 Coin'e göre ana / yedek — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n"
    f"Sinyal: {len(E):,} (şimdi ✅ ana {ANA_CUR.sum():,} · 🔸 yedek {YED_CUR.sum():,}) · coin×tür hücresi: {len(GR):,} · {time.time()-T0:.0f} sn\n")
yaz("_sinyal sayısı · isabet · işlem başı net % — 2022-06→2023 | 2024+ | 2026 · ana çizgisi: %55,9 +0,30 | %58,6 +0,65 | %59,1 +0,59_\n```")
OA, OY = st(ANA_CUR), st(YED_CUR); yaz(sat("ŞİMDİ ✅ ana", OA, True)); yaz(sat("ŞİMDİ 🔸 yedek", OY, True)); yaz("```")
def ana_mi(o): return all(o[dn][0] >= MIN[dn] and o[dn][1] >= BENx[dn][0] and o[dn][2] >= BENx[dn][1] for dn in o)
RES = {}
for vad, V in (("V1 geçmiş ortalaması", V1), ("V2 her dönemde iyi", V2)):
    P_ = YED_CUR & (V == 1); D_ = ANA_CUR & (V == -1); kalanY = YED_CUR & ~P_; kalanA = ANA_CUR & ~D_
    oP, oD, oKY, oKA = st(P_), st(D_), st(kalanY), st(kalanA)
    yeniP, yeniPD = st(ANA_CUR | P_), st((ANA_CUR | P_) & ~D_)
    yaz(f"\n### {vad}\n```"); yaz(sat("⬆️ yükselen yedek (İYİ hücre)", oP)); yaz(sat("   yükselmeyen yedek", oKY))
    yaz(sat("⬇️ inen ana (KÖTÜ hücre)", oD)); yaz(sat("   kalan ana", oKA))
    yaz(sat("YENİ ana = şimdi + yükselen", yeniP, True)); yaz(sat("YENİ ana = şimdi + yükselen − inen", yeniPD, True)); yaz("```")
    RES[vad] = (P_, D_, oP, oD, oKY, oKA, yeniPD)
# plasebo: coin geçmişleri tür içinde coin'ler arasında karıştırılır
rng = np.random.default_rng(7); PL = {k: [] for k in RES}
TURC = {tur: sorted(set(E.nm[E.tur == tur])) for tur in E.tur.unique()}
m24 = tz_ >= A24x
for _ in range(40):
    es = {tur: dict(zip(cs, rng.permutation(cs))) for tur, cs in TURC.items()}
    v1p, v2p = sinifla(es)
    for vad, V in (("V1 geçmiş ortalaması", v1p), ("V2 her dönemde iyi", v2p)):
        P_ = YED_CUR & (V == 1) & m24; D_ = ANA_CUR & (V == -1) & m24
        PL[vad].append((100 * OK[P_].mean() if P_.sum() >= 10 else np.nan, 100 * OK[D_].mean() if D_.sum() >= 10 else np.nan))
yaz("\n## Ölçütler")
GEC = {}
for vad, (P_, D_, oP, oD, oKY, oKA, yeniPD) in RES.items():
    pl = np.array(PL[vad]); p95 = np.nanpercentile(pl[:, 0], 95) if np.isfinite(pl[:, 0]).any() else np.nan; p05 = np.nanpercentile(pl[:, 1], 5) if np.isfinite(pl[:, 1]).any() else np.nan
    gP1 = ana_mi(oP); gP2 = all(oP[dn][0] >= MIN[dn] and oP[dn][1] >= oKY[dn][1] + 3 for dn in ("2024+", "2026")); gP3 = bool(np.isfinite(p95) and oP["2024+"][1] > p95)
    gD1 = all(oD[dn][0] >= MIN[dn] and oD[dn][1] <= oKA[dn][1] - 3 and oD[dn][2] <= oKA[dn][2] - 0.20 for dn in oD)
    gD2 = all(yeniPD[dn][1] >= OA[dn][1] and yeniPD[dn][2] >= OA[dn][2] for dn in OA); gD3 = bool(np.isfinite(p05) and oD["2024+"][1] < p05)
    i = lambda x: "✅" if x else "❌"
    yaz(f"**{vad}** — ⬆️ P: ana çizgisi {i(gP1)} · yükselmeyenden +3 puan {i(gP2)} · plasebo {i(gP3)} (2024+ %{oP['2024+'][1]:.1f} vs plasebo %95 %{p95:.1f})  |  "
        f"⬇️ D: kalan ana'dan düşük {i(gD1)} · yeni set gerilemiyor {i(gD2)} · plasebo {i(gD3)} (2024+ %{oD['2024+'][1]:.1f} vs plasebo %5 %{p05:.1f})")
    GEC[vad] = (gP1 and gP2 and gP3, gD1 and gD2 and gD3)
# hileli karşılaştırma: tüm dönemleri bilerek (üç dönemde de iyi olan hücre)
yaz("\n## Karşılaştırma: geriye bakarak (HİLELİ — sonucu bilerek) seçilseydi\n```")
hk = pd.DataFrame({"nm": E.nm, "tur": E.tur, "ok": OK, "net": NET, "d": np.select([D3[0][1], tz_ >= A24x], ["a", "b"], default="x")})
iyi_h = set()
for (nm, tur), g in hk[hk.d != "x"].groupby(["nm", "tur"]):
    a, b = g[g.d == "a"], g[g.d == "b"]
    if len(a) >= 8 and len(b) >= 8 and 100 * a.ok.mean() >= 58 and a.net.mean() > 0.3 and 100 * b.ok.mean() >= 58 and b.net.mean() > 0.3: iyi_h.add((nm, tur))
HIL = YED_CUR & np.array([(n_, t_) in iyi_h for n_, t_ in zip(E.nm, E.tur)])
yaz(sat("⬆️ yükselen yedek (hileli seçim)", st(HIL))); yaz("```")
yaz("_Hileli seçim aynı veriyi hem seçmek hem ölçmek için kullanır; canlıda bu mümkün değil. Asıl karar yukarıdaki hilesiz (ileriye dönük) sonuçla._")
# bugün olsaydı: hangi hücreler İYİ / KÖTÜ (tüm geçmişle)
yaz("\n## Bilgi: bugünkü tüm geçmişle V1 / V2 etiketi alan hücreler (yedek→İYİ · ana→KÖTÜ)")
son = pd.Timestamp.now(tz="UTC")
for vad, kol in (("V1", 0), ("V2", 1)):
    iy, ko = [], []
    for (nm, tur), (cx, CY, CW, CS) in GR.items():
        ny_, nw_, ns_ = CY[-1], CW[-1], CS[-1]; n = ny_.sum(); h = 100 * nw_.sum() / max(n, 1); a = ns_.sum() / max(n, 1)
        yed = tur in ("💵", "🧪", "🔇/🪙")
        if kol == 0: lab = (1 if (h >= 60 and a >= 0.6) else (-1 if (h < 52 or a < 0) else 0)) if n >= 20 else 0
        else:
            q = ny_ >= 8
            with np.errstate(invalid="ignore", divide="ignore"): hy = 100 * nw_ / ny_; ay = ns_ / ny_
            lab = (1 if np.all(~q | ((hy >= 58) & (ay > 0.3))) else (-1 if np.all(~q | ((hy < 55) & (ay < 0))) else 0)) if q.sum() >= 2 else 0
        if lab == 1 and yed: iy.append(f"{nm} {tur} ({int(n)}, %{h:.0f}, {a:+.2f})")
        if lab == -1 and not yed: ko.append(f"{nm} {tur} ({int(n)}, %{h:.0f}, {a:+.2f})")
    yaz(f"- **{vad} İYİ yedek hücre ({len(iy)}):** " + (", ".join(iy[:40]) or "yok")); yaz(f"- **{vad} KÖTÜ ana hücre ({len(ko)}):** " + (", ".join(ko[:40]) or "yok"))
yaz("\n## Önceden yazılı karar")
for vad, (gp, gd) in GEC.items():
    yaz(f"- {vad}: ⬆️ yükseltme {'✅ GEÇTİ' if gp else '❌ geçmedi'} · ⬇️ indirme {'✅ GEÇTİ' if gd else '❌ geçmedi'}")
if not any(gp or gd for gp, gd in GEC.values()): yaz("- → fikir canlıya girmez (coin'in kendi geçmişi ileriye dönük ayırt etmiyor)")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("coin_sinif_sonuc.md", "w").write("\n".join(L) + "\n")
