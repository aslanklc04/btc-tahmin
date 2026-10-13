# meta_model.py — SİNYAL SAYISI DÜŞMEDEN İSABETİ ARTIRMA: "hangi sinyal tutar?" meta-modeli (yalnız test, kullanıcı isteği 13.10.2026).
# Her aday sinyal (✅ ana + 🔸 yedek + gönderilmeyen) için sinyal anında bilinen özellikler: tür, tutma süresi, coin'in kendi Coinbase primi z, BTC primi z,
# son 24 s getiri z (coin + BTC), coin'in Binance fonlaması z, Kore primi z, oynaklık oranı, 7 g göreli getiri, aynı saatte sinyal veren coin sayısı, saat, gün,
# BTC 4/8 s model gücü, coin'in 24 s model gücü. Model: LightGBM, YÜRÜYEN test (her yarıyıl yalnız ondan ÖNCE sonuçlanmış sinyallerle eğitilir).
# ÖNCEDEN YAZILI KARAR (sonuçlar görülmeden; değerlendirme yalnız eğitimde görülmemiş dönemlerde: 2024+ ve 2026):
#   M1 YER DEĞİŞTİRME: eşik, eğitim döneminde seçilen sinyal sayısı ana sayısına eşit olacak şekilde ayarlanır; skoru eşiği geçen adaylar gönderilir.
#      Kabul: 2024+ VE 2026'da isabet ≥ ana +2 puan VE net ≥ ana +0,10 VE haftalık sayı ≥ ana sayısının %90'ı → canlıya aday (sayı düşmeden isabet artar).
#   M2 SIRALAMA: ana sinyaller içinde skoru üst yarıda olanlar alt yarıdakilerden 2024+ VE 2026'da isabette ≥ +4 puan VE nette ≥ +0,20 iyi ise → mesaj içi sıralama skora göre.
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
yaz(f"# 🧪 İsabet ve kâr için yeni teknikler — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nOlay: ✅ ana {ANA.sum():,} · 🔸 yedek {YED.sum():,} · gönderilmeyen {GON.sum():,}\n")
SS = requests.Session(); AYLAR = [d.strftime("%Y-%m") for d in pd.date_range("2022-03-01", "2026-09-01", freq="MS")]
def zcsv(url):
    for k in range(4):
        try:
            r = SS.get(url, timeout=30)
            if r.status_code == 404: return None
            if r.status_code == 200: z_ = zipfile.ZipFile(io.BytesIO(r.content)); return pd.read_csv(z_.open(z_.namelist()[0]), header=None, dtype=str)
        except Exception: time.sleep(1 + k)
    return None
VADS = {"SHIB": "1000SHIBUSDT", "PEPE": "1000PEPEUSDT", "FLOKI": "1000FLOKIUSDT", "BONK": "1000BONKUSDT"}
def fon(nm):
    sym = VADS.get(nm, nm + "USDT"); fr = [x for x in (zcsv(f"https://data.binance.vision/data/futures/um/monthly/fundingRate/{sym}/{sym}-fundingRate-{ym}.zip") for ym in AYLAR) if x is not None]
    if not fr: return nm, None
    f_ = pd.concat(fr); f_ = f_[pd.to_numeric(f_[0], errors="coerce").notna()]; ft = f_[0].astype(float).values; ft = np.where(ft > 1e14, ft / 1000, ft)
    s = pd.Series(f_.iloc[:, -1].astype(float).values, index=pd.DatetimeIndex(pd.to_datetime(ft, unit="ms", utc=True)).round("min").as_unit("ns")); s = s[~s.index.duplicated()].sort_index()
    return nm, (s - s.rolling(90, min_periods=30).mean()) / (s.rolling(90, min_periods=30).std() + 1e-12)
with ThreadPoolExecutor(8) as ex: FON = {k: v for k, v in ex.map(fon, sorted(set(nmv))) if v is not None}
KORE = {}
try:
    UP, _, _, _ = pickle.load(open(f("**/desen_veri.pkl")[0], "rb"))
    UP = {k: v for k, v in UP.items() if v is not None and len(v) > 2000}
    for c, s in UP.items():
        if c == "USDT": continue
        bn = RAW[c].c if c in RAW else (OH[c].close if c in OH else None)
        if bn is None or "USDT" not in UP: continue
        ix = s.index; p = np.log(s / (UP["USDT"].reindex(ix) * bn.reindex(ix))); p = p.where(p.abs() < 0.3)
        KORE[c] = (p - p.rolling(720, min_periods=168).mean()) / (p.rolling(720, min_periods=168).std() + 1e-12)
except Exception as e: yaz(f"_Kore verisi alınamadı: {type(e).__name__} {str(e)[:100]}_")
yaz(f"Coin fonlaması: {len(FON)} coin · Kore primi: {len(KORE)} coin ({', '.join(sorted(KORE))}) · {time.time()-T0:.0f} sn\n")
E24n = {}
for s_, X in E24.items():
    X = X.copy(); X.index = pd.DatetimeIndex(X.index).tz_convert("UTC").as_unit("ns"); E24n[s_[:-4]] = X
# ---------------- özellikler (yalnız geçmiş) ----------------
import lightgbm as lgb
from sklearn.metrics import roc_auc_score
CAND = ANA | YED | GON; ix = np.where(CAND)[0]
F = pd.DataFrame(index=range(len(Ez)))
F["aile"] = pd.Categorical(Ez.aile.values).codes; F["H"] = Ez.H.values; F["z"] = z; F["zB"] = zB; F["saat"] = tz_.hour; F["gun"] = tz_.dayofweek
rz = np.full(len(Ez), np.nan); vr = np.full(len(Ez), np.nan); r7 = np.full(len(Ez), np.nan); fz = np.full(len(Ez), np.nan); kz = np.full(len(Ez), np.nan)
bc = np.log(OH["BTC"].close); r7b = bc.diff(168)
for nm, o in OH.items():
    m = nmv == nm
    if not m.any(): continue
    lr = np.log(o.close); r1 = lr.diff(); sg = r1.rolling(720, min_periods=168).std(); t_ = tz_[m]
    rz[m] = ((lr - lr.shift(24)) / (sg * np.sqrt(24))).reindex(t_).values
    vr[m] = (r1.rolling(24).std() / sg).reindex(t_).values; r7[m] = (lr.diff(168) - r7b.reindex(lr.index)).reindex(t_).values
    if nm in FON:
        fs = FON[nm].dropna(); i = fs.index.searchsorted(t_, side="right") - 1; fz[m] = np.where(i >= 0, fs.values[np.clip(i, 0, None)], np.nan)
    if nm in KORE: kz[m] = KORE[nm].reindex(t_).values
F["rz"], F["vr"], F["r7"], F["fz"], F["kz"] = rz, vr, r7, fz, kz
bl = np.log(OH["BTC"].close); bs = bl.diff().rolling(720, min_periods=168).std(); F["rzB"] = ((bl - bl.shift(24)) / (bs * np.sqrt(24))).reindex(tz_).values
say = pd.Series(nmv[CAND], index=tz_[CAND].floor("h")).groupby(level=0).nunique(); F["say"] = say.reindex(tz_.floor("h")).fillna(0).values
sb = SFB.copy(); sb.index = pd.DatetimeIndex(sb.index).tz_convert("UTC").as_unit("ns"); sbr = sb.reindex(tz_)
F["b4"] = (np.sign(sbr.S4) * sbr.C4).values; F["b8"] = (np.sign(sbr.S8) * sbr.C8).values
s24 = np.full(len(Ez), np.nan)
for nm, X in E24n.items():
    m = nmv == nm
    if m.any(): Xr = X.reindex(tz_[m]); s24[m] = (np.sign(Xr.S24) * Xr.C24).values
F["s24"] = s24
y = Ez.ok.values.astype(int); BIT = tz_ + pd.to_timedelta(Ez.H.values.astype(int), unit="h")
KAT = ["aile"]
yaz(f"# 🧠 Meta-model: sayı düşmeden isabet — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nAday sinyal: {CAND.sum():,} (✅ {ANA.sum():,} · 🔸 {YED.sum():,} · gönderilmeyen {GON.sum():,}) · özellik: {F.shape[1]}\n")
FOLD = [pd.Timestamp(x, tz="UTC") for x in ("2024-01-01", "2024-07-01", "2025-01-01", "2025-07-01", "2026-01-01")] + [tz_.max() + pd.Timedelta(hours=1)]
P = np.full(len(Ez), np.nan); THR = np.full(len(Ez), np.nan); AUCS = []
for a, b in zip(FOLD[:-1], FOLD[1:]):
    tr = CAND & (BIT < a); te = CAND & (tz_ >= a) & (tz_ < b)
    mdl = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.03, num_leaves=15, min_child_samples=100, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, verbose=-1)
    mdl.fit(F[tr], y[tr], categorical_feature=KAT)
    p_tr = mdl.predict_proba(F[tr])[:, 1]; P[te] = mdl.predict_proba(F[te])[:, 1]
    son2 = tr & (tz_ >= a - pd.Timedelta(days=730)); n_ana = (son2 & ANA).sum()             # eşik: son 2 yılda ana sayısı kadar sinyal seçecek skor
    pp = np.sort(mdl.predict_proba(F[son2])[:, 1])[::-1]; THR[te] = pp[min(n_ana, len(pp)) - 1] if n_ana else 1
    AUCS.append((a, roc_auc_score(y[te], P[te]) if te.sum() > 50 else np.nan, roc_auc_score(y[te & ANA], P[te & ANA]) if (te & ANA).sum() > 50 else np.nan))
yaz("Yürüyen test AUC (0,5 = yazı-tura): " + " · ".join(f"{a:%Y-%m}: tüm {u1:.3f} / ana içinde {u2:.3f}" for a, u1, u2 in AUCS) + "\n")
META = CAND & np.isfinite(P) & (P >= THR)
A24, A26 = pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC"); SONT = tz_.max()
DD = (("2024+", tz_ >= A24, (SONT - A24).days / 7), ("2026", tz_ >= A26, (SONT - A26).days / 7))
def st(m): return {dn: (int((m & md).sum()), (m & md).sum() / hf, 100 * Ez.ok.values[m & md].mean() if (m & md).any() else np.nan, 100 * Ez.net.values[m & md].mean() if (m & md).any() else np.nan) for dn, md, hf in DD}
def sat(ad, o): return f"{ad:46s}" + " | ".join(f"{o[dn][1]:5.1f}/hf · %{o[dn][2]:4.1f} · {o[dn][3]:+.2f} ({o[dn][0]})" for dn, _, _ in DD)
OA, OM = st(ANA), st(META)
yaz("_haftada · isabet · işlem başı net % (sinyal) — 2024+ | 2026 (hepsi eğitimde görülmemiş)_\n```"); yaz(sat("✅ ana (bugünkü kural)", OA)); yaz(sat("M1 meta-model seçimi (aynı sayıda)", OM))
yaz(sat("   … meta seçiminde ana olanlar", st(META & ANA))); yaz(sat("   … meta seçiminde yeni gelenler (yedek/gönderilmeyen)", st(META & ~ANA))); yaz(sat("   … meta'nın düşürdüğü ana sinyaller", st(ANA & ~META)))
med = np.full(len(Ez), np.nan)
for a, b in zip(FOLD[:-1], FOLD[1:]):
    te = ANA & (tz_ >= a) & (tz_ < b) & np.isfinite(P)
    if te.any(): med[te] = np.median(P[te])
UST, ALT = ANA & (P >= med), ANA & (P < med)
yaz(sat("M2 ana içinde skor üst yarı", st(UST))); yaz(sat("M2 ana içinde skor alt yarı", st(ALT))); yaz("```")
M1 = all(OM[dn][2] >= OA[dn][2] + 2 and OM[dn][3] >= OA[dn][3] + 0.10 and OM[dn][1] >= 0.9 * OA[dn][1] for dn, _, _ in DD)
ou, oa_ = st(UST), st(ALT); M2 = all(ou[dn][2] >= oa_[dn][2] + 4 and ou[dn][3] >= oa_[dn][3] + 0.20 for dn, _, _ in DD)
imp = pd.Series(mdl.booster_.feature_importance("gain"), index=F.columns).sort_values(ascending=False)
yaz("Son modelde en etkili özellikler: " + " · ".join(f"{k} {100*v/imp.sum():.0f}%" for k, v in imp.head(8).items()))
yaz(f"\n## Önceden yazılı karar\n- M1 yer değiştirme (sayı aynı, isabet ↑): {'✅ GEÇTİ' if M1 else '❌ geçmedi'}\n- M2 ana içinde skora göre sıralama: {'✅ GEÇTİ' if M2 else '❌ geçmedi'}")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("meta_model_sonuc.md", "w").write("\n".join(L) + "\n")
