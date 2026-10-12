# teknik_tara.py — İSABET VE KÂRI ARTIRACAK YENİ TEKNİKLER (yalnız test). Canlı düzen (12.10.2026): ✅ ana · 🔸 yedek (yalnız coin'in kendi primi ≥ 0 olan 🔇 / 🪙) · gönderilmeyenler.
# Koşullar (sinyal anında, yalnız geçmişten): C1 24 saatlik model de yukarı · C2 aynı saatte çok coin / tek coin · C3 son 24 saatte çok yükselmiş / düşmüş ·
#   C4 coin'in KENDİ vadeli fonlaması düşük / çok yüksek · C6 Kore primi (coin'in kendi / BTC'nin) yüksek · C7 BTC 50 günlük ortalamanın üstünde / altında.
#   T5 giriş tekniği: sinyal fiyatının biraz altına limit emir (k × saatlik oynaklık), 2 saatte dolmazsa işlem yok.
# ÖNCEDEN YAZILI KARAR (12.10.2026, sonuçlar görülmeden). Dönemler 2022-06→2023 · 2024+ · 2026; en az 30 / 30 / 10 sinyal.
#   ANA+ (öncelik): ana sinyallerden koşullu olanlar üç dönemde de ana ortalamasından isabette ≥ +2 puan VE nette ≥ +0,10 → mesajda öne alınır.
#   ANA− (eleme): koşullu ana sinyaller üç dönemde de net < 0 → yedeğe iner.
#   YED+ / GÖN+ (yükseltme): koşullu yedekler ya da gönderilmeyenler üç dönemde de ana set ölçütünü geçerse (isabet ≥ %55,9 · %58,6 · %59,1 VE net ≥ +0,30 · +0,647 · +0,589) → ✅ ana.
#   T5: ana sinyallerde hem işlem başı net hem haftalık toplam net üç dönemde de bugünkü girişten yüksekse → mesajdaki giriş fiyatı değişir.
#   PLASEBO: aynı koşullar 30 gün kaydırılmış veriyle de denenir; gerçek veride geçen sayısı plasebodan fazla değilse hiçbir bulguya güvenilmez.
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
yaz(f"# 🧪 İsabet ve kâr için yeni teknikler — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nOlay: ✅ ana {ANA.sum():,} · 🔸 yedek {YED.sum():,} · gönderilmeyen {GON.sum():,}\n")
# ---------------- ek veriler ----------------
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
def kosullar(kay):
    tt = tz_ - pd.Timedelta(hours=kay); K = {}
    s24, cc, t30 = (np.full(len(Ez), np.nan) for _ in range(3))
    for nm, X in E24n.items():
        m = nmv == nm
        if m.any(): Xr = X.reindex(tt[m]); s24[m], cc[m], t30[m] = Xr.S24.values, Xr.C24.values, Xr.T30_24.values
    K["C1a 24 s modeli de yukarı"] = s24 > 0; K["C1b 24 s modeli güçlü yukarı"] = (s24 > 0) & (cc >= t30)
    cf = np.isin(ail, ["coin 🤝 ortak", "coin 🔇 sessiz", "coin tek başına", "🧪 24 saat"])
    say = pd.Series(nmv[cf], index=tz_[cf].floor("h")).groupby(level=0).nunique(); cnt = say.reindex(tt.floor("h")).fillna(0).values
    K["C2a aynı saatte ≥ 5 coin sinyali"] = cnt >= 5; K["C2b aynı saatte tek coin"] = cnt == 1
    rz = np.full(len(Ez), np.nan)
    for nm, o in OH.items():
        m = nmv == nm
        if not m.any(): continue
        lr = np.log(o.close); sg = lr.diff().rolling(720, min_periods=168).std(); rz[m] = ((lr - lr.shift(24)) / (sg * np.sqrt(24))).reindex(tt[m]).values
    K["C3a son 24 s çok yükselmiş (z ≥ 2)"] = rz >= 2; K["C3b son 24 s çok düşmüş (z ≤ −2)"] = rz <= -2
    fz = np.full(len(Ez), np.nan)
    for nm, fs in FON.items():
        m = nmv == nm
        if not m.any(): continue
        fs = fs.dropna(); i = fs.index.searchsorted(tt[m], side="right") - 1; fz[m] = np.where(i >= 0, fs.values[np.clip(i, 0, None)], np.nan)
    K["C4a coin fonlaması düşük (z ≤ −1)"] = fz <= -1; K["C4b coin fonlaması çok yüksek (z ≥ 2)"] = fz >= 2
    kz = np.full(len(Ez), np.nan)
    for nm, ks in KORE.items():
        m = nmv == nm
        if m.any(): kz[m] = ks.reindex(tt[m]).values
    kb = KORE["BTC"].reindex(tt).values if "BTC" in KORE else np.full(len(Ez), np.nan)
    K["C6a coin'in Kore primi yüksek (z ≥ 1)"] = kz >= 1; K["C6b BTC'nin Kore primi yüksek (z ≥ 1)"] = kb >= 1
    bc = OH["BTC"].close; ust = (bc > bc.rolling(1200, min_periods=600).mean()).astype(float).where(bc.rolling(1200, min_periods=600).mean().notna()).reindex(tt).values
    K["C7a BTC 50 g ortalamanın üstünde"] = ust == 1; K["C7b BTC 50 g ortalamanın altında"] = ust == 0
    return K
DN = (("2022-06→2023", (tz_ >= P0) & (tz_ < A24_), (A24_ - P0).days / 7), ("2024+", tz_ >= A24_, HAF["2024+"]), ("2026", tz_ >= A26_, HAF["2026"]))
BEN = {"2022-06→2023": (55.9, 0.30), "2024+": (58.6, 0.647), "2026": (59.1, 0.589)}; MIN = {"2022-06→2023": 30, "2024+": 30, "2026": 10}
def ist(m):
    return {dn: (int((m & md).sum()), 100 * Ez.ok.values[m & md].mean() if (m & md).any() else np.nan, 100 * Ez.net.values[m & md].mean() if (m & md).any() else np.nan) for dn, md, _ in DN}
def yazi(o): return " | ".join(f"{o[dn][0]/hf:5.1f}/hf · %{o[dn][1]:4.1f} · {o[dn][2]:+.2f}" if o[dn][0] >= 5 else f"{o[dn][0]:5d} az" for dn, _, hf in DN)
def yeter(o): return all(o[dn][0] >= MIN[dn] for dn in MIN)
OANA = ist(ANA)
def kurallar(K):
    gec = []
    for ad, c in K.items():
        oa, oy, og = ist(ANA & c), ist(YED & c), ist(GON & c)
        if yeter(oa) and all(oa[dn][1] >= OANA[dn][1] + 2 and oa[dn][2] >= OANA[dn][2] + 0.10 for dn in MIN): gec.append(("ANA+", ad))
        if yeter(oa) and all(oa[dn][2] < 0 for dn in MIN): gec.append(("ANA−", ad))
        for gr, o in (("YED+", oy), ("GÖN+", og)):
            if yeter(o) and all(o[dn][1] >= BEN[dn][0] and o[dn][2] >= BEN[dn][1] for dn in MIN): gec.append((gr, ad))
    return gec
K0 = kosullar(0)
yaz("_haftada · isabet · işlem başı net % — 2022-06→2023 | 2024+ | 2026_\n```")
yaz(f"{'✅ ANA (hepsi)':46s}{yazi(OANA)}\n{'🔸 YEDEK (hepsi)':46s}{yazi(ist(YED))}\n{'GÖNDERİLMEYEN (hepsi)':46s}{yazi(ist(GON))}")
for ad, c in K0.items():
    yaz(f"\n{ad}\n  {'✅ ana + koşul':44s}{yazi(ist(ANA & c))}\n  {'🔸 yedek + koşul':44s}{yazi(ist(YED & c))}\n  {'gönderilmeyen + koşul':44s}{yazi(ist(GON & c))}")
yaz("```")
G0 = kurallar(K0); GP = kurallar(kosullar(720)) + kurallar(kosullar(1440))
yaz(f"\n**Gerçek veride geçen:** {len(G0)} · **plasebo (30 ve 60 gün kaydırılmış, iki deneme toplamı):** {len(GP)}")
for gr, ad in G0: yaz(f"- {gr}: {ad}")
# ---------------- T5 geri çekilme girişi ----------------
yaz("\n## T5 — sinyal fiyatının altına limit emir (2 saatte dolmazsa işlem yok), ✅ ana sinyaller\n_dolan sinyal oranı · işlem başı net · haftalık toplam net (haftada sinyal × işlem başı)_\n```")
A = Ez[ANA].copy(); T5 = {}
for k in (0.0, 0.5, 1.0):
    net_ = np.full(len(A), np.nan); dol = np.zeros(len(A), bool)
    for nm, g in A.groupby("nm"):
        o = OH.get(nm)
        if o is None: continue
        lr = np.log(o.close); sg = lr.diff().rolling(720, min_periods=168).std().values; ix0 = o.index.get_indexer(pd.DatetimeIndex(g.t))
        for j, (i0, H) in enumerate(zip(ix0, g.H.values)):
            if i0 < 0 or i0 + H >= len(o): continue
            lim = o.close.values[i0] * (1 - k * (sg[i0] if np.isfinite(sg[i0]) else 0.01))
            if k == 0 or o.low.values[i0 + 1:i0 + 3].min() <= lim:
                pos = A.index.get_loc(g.index[j]); dol[pos] = True; net_[pos] = o.close.values[i0 + H] / lim - 1 - 0.0004
    s = []
    for dn, md, hf in DN:
        mm = md[ANA]; n_ = net_[mm & dol]; T5[(k, dn)] = (100 * np.nanmean(n_) if len(n_) else np.nan, 100 * np.nansum(n_) / hf)
        s.append(f"%{100*dol[mm].mean():3.0f} dolan · {T5[(k, dn)][0]:+.2f} · haftalık {T5[(k, dn)][1]:+5.1f}")
    yaz(f"k = {k:<4} {' | '.join(s)}")
yaz("```")
T5G = [k for k in (0.5, 1.0) if all(T5[(k, dn)][0] > T5[(0.0, dn)][0] and T5[(k, dn)][1] > T5[(0.0, dn)][1] for dn, _, _ in DN)]
yaz("\n## Önceden yazılı karar\n" + ("\n".join(f"- {gr}: **{ad}**" for gr, ad in G0) if G0 else "- Koşullardan hiçbiri kuralı geçmedi")
    + f"\n- Plasebo kontrolü: gerçek {len(G0)} · plasebo ortalaması {len(GP)/2:.1f} → " + ("✅ gerçek bulgu fazlası var" if len(G0) > len(GP) / 2 + 1 else "❌ şanstan ayırt edilemiyor, canlıya alınmaz")
    + f"\n- T5 giriş: " + (f"✅ k = {min(T5G)} geçti" if T5G else "❌ geçmedi — giriş aynen (sinyal fiyatı)"))
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("teknik_tara_sonuc.md", "w").write("\n".join(L) + "\n")
