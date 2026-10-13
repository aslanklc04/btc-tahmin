# coin_gecmis.py — SIRALAMAYA COIN'İN KENDİ GEÇMİŞİ (kullanıcı onayı 13.10.2026; yalnız test). Tetikleyen: BLUR (2024+ isabet %50) 🧪 türü yüzünden 1. sıraya çıktı, −%24.
# Olaylar: ✅ ana sinyaller (çekirdek coin'ler + 🌐 geniş liste 🤝/🧪 + 💵), 🚀 dahil. Coin geçmişi YALNIZ GEÇMİŞTEN: o anda çıkışı tamamlanmış önceki ✅ ana sinyalleri.
# Tahmini isabet (küçültülmüş): (coin'in geçmiş kazananı + 20 × ön değer) / (coin'in geçmiş sinyal sayısı + 20)
#   Y1: ön değer %58 (sabit) · Y2: ön değer = şu anki sıranın tür isabeti (📉🔥 %68, prim z ≥ 3 %55, diğer %60) → tür ve coin birlikte
#   Kâr da aynı şekilde (ön değer +0,6 / 📉🔥 +1,2 / z ≥ 3 +0,3). Sıra: tahmini isabet ↓, sonra tahmini kâr ↓, sonra prim ↓.
#   ŞİMDİKİ: sira_anahtari (tür isabeti → tür kârı → prim). 💸 fonlama geçmişte yok → hesaba katılmadı.
# ÖNCEDEN YAZILI KARAR (sonuçlar görülmeden):
#   R1 1. SIRA: aynı saatte ≥ 2 ✅ sinyal olan saatlerde 1. sıradaki sinyal: üç dönemde (2022-06→2023 · 2024+ · 2026) isabet ≥ şimdiki +2 puan VE net ≥ şimdiki +0,10
#      (en az 30 / 30 / 10 saat) · R1b ilk yarı (ilk ⌈n/2⌉ sinyal) için de isabet ve net ≥ şimdiki (gerileme yok)
#   R2 PLASEBO: coin geçmişleri coin'ler arasında rastgele karıştırılır (40 kez); 2024+ 1. sıra isabet farkı gerçek > plasebo %95
#   R3 AYIRT EDİCİLİK: tüm ✅ sinyallerde tahmini isabetin üst üçte biri alt üçte birinden üç dönemde isabet ve net olarak yüksek
#   → R1 + R1b + R2 + R3 geçen varyant (ikisi geçerse 2024+ 1. sıra isabeti yüksek olan) sıralamaya girer. Sinyal sayısı değişmez (yalnız sıra).
#   EK (⚠️ zayıf coin işareti, sinyal silinmez): tahmini isabeti < %52 olan sinyallerde net üç dönemde < 0 ise (en az 30 / 30 / 10) → ⚠️ işareti önerilir.
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
C = pd.DataFrame({"nm": nmv[ANA], "t": pd.DatetimeIndex(Ez.t.values[ANA]), "H": Ez.H.values[ANA], "net": Ez.net.values[ANA], "z": z[ANA], "rz": RZ[ANA], "kay": "çekirdek"})
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
        m = bu4 & (zz >= 2); GV.append(pd.DataFrame({"nm": nm, "t": t[m], "H": 4, "net": np.exp(X.y4.values[ev][m]) - 1 - 0.0004, "z": zz[m], "rz": rzs.reindex(t[m]).values, "kay": "🌐"}))
    p = bul(f"ga/**/disa24_{nm}USDT.pkl")
    if p:
        D = pd.read_pickle(p).astype("float64"); D.index = utc(D.index); D = D.reindex(pd.date_range(D.index[0], D.index[-1], freq="1h")); c = D.close.ffill(limit=3).values; n = len(D)
        mk = np.nan_to_num(((D.S24 > 0) & (D.C24 >= D.T10_24)).values).astype(bool) & D.T10_24.notna().values & (np.arange(n) + 25 < n)
        ev = events(mk, 24); t = D.index[ev]; zz = zs.reindex(t).values; m = zz >= 1.5
        GV.append(pd.DataFrame({"nm": nm, "t": t[m], "H": 24, "net": (c[ev + 24] / c[ev] - 1)[m] - 0.0004, "z": zz[m], "rz": rzs.reindex(t[m]).values, "kay": "🌐"}))
E = pd.concat([d.assign(t=utc(d.t)) for d in [C] + GV if len(d)], ignore_index=True); E["t"] = pd.to_datetime(E.t, utc=True).dt.as_unit("ns"); E = E[np.isfinite(E.net)].sort_values("t").reset_index(drop=True); E["ok"] = (E.net > 0).astype(float)
E["dip"] = (E.rz <= -2) & ~E.nm.isin(GEN)
E["th"] = np.where(E.dip, 68.0, np.where(E.z >= 3, 55.0, 60.0)); E["tn"] = np.where(E.dip, 1.2, np.where(E.z >= 3, 0.3, 0.6))
yaz(f"# 🪙 Sıralamaya coin'in kendi geçmişi — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n✅ ana sinyal: {len(E):,} (çekirdek {int((E.kay == 'çekirdek').sum()):,} · 🌐 {int((E.kay == '🌐').sum()):,}) · coin: {E.nm.nunique()} · {time.time()-T0:.0f} sn\n")
# ---------------- coin'in geçmişi (yalnız çıkışı tamamlanmış önceki sinyaller) ----------------
def gecmis(E, eslem=None):
    pn, pk, ps = np.zeros(len(E)), np.zeros(len(E)), np.zeros(len(E))
    nmx = E.nm.values if eslem is None else E.nm.map(eslem).values
    for nm in pd.unique(E.nm.values):
        kaynak = E[nmx == nm] if eslem is not None else None
        hed = np.where(E.nm.values == nm)[0]
        src = E.iloc[np.where(nmx == nm)[0]] if eslem is not None else E.iloc[hed]
        cik = (src.t + pd.to_timedelta(src.H, unit="h")).values; o = np.argsort(cik); cik = cik[o]
        ck = np.concatenate([[0], np.cumsum(src.ok.values[o])]); cn = np.concatenate([[0], np.cumsum(src.net.values[o])])
        j = np.searchsorted(cik, E.t.values[hed], side="right"); pn[hed], pk[hed], ps[hed] = j, ck[j], cn[j]
    return pn, pk, ps
def tahmin(pn, pk, ps, onh, onn, m=20.0): return 100 * (pk + m * onh / 100) / (pn + m), 100 * (ps + m * onn / 100) / (pn + m)
pn, pk, ps = gecmis(E)
E["y1h"], E["y1n"] = tahmin(pn, pk, ps, 58.0, 0.6); E["y2h"], E["y2n"] = tahmin(pn, pk, ps, E.th.values, E.tn.values)
E["saat"] = E.t.dt.floor("h"); P0x, A24x, A26x = pd.Timestamp("2022-06-01", tz="UTC"), pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")
DD = (("2022-06→2023", P0x, A24x), ("2024+", A24x, None), ("2026", A26x, None)); MIN = {"2022-06→2023": 30, "2024+": 30, "2026": 10}
def donem(t, a, b): return (t >= a) & ((t < b) if b is not None else True)
ANAH = {"ŞİMDİKİ (tür)": lambda g: g.sort_values(["th", "tn", "z"], ascending=False), "Y1 coin geçmişi (ön %58)": lambda g: g.sort_values(["y1h", "y1n", "z"], ascending=False),
        "Y2 tür + coin geçmişi": lambda g: g.sort_values(["y2h", "y2n", "z"], ascending=False)}
CK = E.groupby("saat").filter(lambda g: len(g) >= 2)
def sira_olc(CK, ad):
    bir, yari = [], []
    for s, g in CK.groupby("saat"):
        g2 = ANAH[ad](g); bir.append((s, g2.ok.iloc[0], g2.net.iloc[0])); k = int(np.ceil(len(g2) / 2)); yari.append((s, g2.ok.iloc[:k].mean(), g2.net.iloc[:k].mean()))
    B1, BY = pd.DataFrame(bir, columns=["s", "ok", "net"]), pd.DataFrame(yari, columns=["s", "ok", "net"])
    return {dn: tuple((int(donem(X.s, a, b).sum()), 100 * X.ok[donem(X.s, a, b)].mean(), 100 * X.net[donem(X.s, a, b)].mean()) for X in (B1, BY)) for dn, a, b in DD}
yaz(f"_Aynı saatte ≥ 2 ✅ sinyal olan saat: {CK.saat.nunique():,}_\n\n## 1) 1. sıradaki sinyal ve ilk yarı\n_saat · isabet · işlem başı net % — 2022-06→2023 | 2024+ | 2026_\n```")
SO = {ad: sira_olc(CK, ad) for ad in ANAH}
for ad, o in SO.items():
    yaz(f"{ad:26s} 1. sıra: " + " | ".join(f"{o[dn][0][0]:4d} · %{o[dn][0][1]:4.1f} · {o[dn][0][2]:+.2f}" for dn, _, _ in DD))
    yaz(f"{'':26s} ilk yarı: " + " | ".join(f"{o[dn][1][0]:4d} · %{o[dn][1][1]:4.1f} · {o[dn][1][2]:+.2f}" for dn, _, _ in DD))
yaz("```")
# plasebo: coin geçmişleri coin'ler arasında karıştırılır
rng = np.random.default_rng(7); coins = pd.unique(E.nm.values); PL = {"Y1 coin geçmişi (ön %58)": [], "Y2 tür + coin geçmişi": []}
for k in range(40):
    es = dict(zip(coins, rng.permutation(coins))); a, b, c = gecmis(E, es); Ep = E.copy()
    Ep["y1h"], Ep["y1n"] = tahmin(a, b, c, 58.0, 0.6); Ep["y2h"], Ep["y2n"] = tahmin(a, b, c, E.th.values, E.tn.values)
    CKp = Ep.groupby("saat").filter(lambda g: len(g) >= 2)
    for ad in PL: PL[ad].append(sira_olc(CKp, ad)["2024+"][0][1] - SO["ŞİMDİKİ (tür)"]["2024+"][0][1])
yaz("\n## 2) Ölçütler")
SEC = []
for ad in ("Y1 coin geçmişi (ön %58)", "Y2 tür + coin geçmişi"):
    o, s0 = SO[ad], SO["ŞİMDİKİ (tür)"]
    R1 = all(o[dn][0][0] >= MIN[dn] and o[dn][0][1] >= s0[dn][0][1] + 2 and o[dn][0][2] >= s0[dn][0][2] + 0.10 for dn in MIN)
    R1b = all(o[dn][1][1] >= s0[dn][1][1] and o[dn][1][2] >= s0[dn][1][2] for dn in MIN)
    g = o["2024+"][0][1] - s0["2024+"][0][1]; p95 = np.percentile(PL[ad], 95); R2 = g > p95
    hk, nk = ad[:2].lower() + "h", None; q = E[hk]; ust, alt = q >= q.quantile(2 / 3), q <= q.quantile(1 / 3); r3 = []
    for dn, a, b in DD:
        md = donem(E.t, a, b); r3.append((100 * E.ok[md & ust].mean(), 100 * E.ok[md & alt].mean(), 100 * E.net[md & ust].mean(), 100 * E.net[md & alt].mean()))
    R3 = all(x[0] > x[1] and x[2] > x[3] for x in r3)
    i = lambda x: "✅" if x else "❌"
    yaz(f"**{ad}** — R1 1. sıra {i(R1)} · R1b ilk yarı gerilemiyor {i(R1b)} · R2 plasebo {i(R2)} (2024+ fark {g:+.1f} puan, plasebo %95 {p95:+.1f}) · R3 ayırt edicilik {i(R3)} ("
        + " | ".join(f"üst %{x[0]:.1f} {x[2]:+.2f} vs alt %{x[1]:.1f} {x[3]:+.2f}" for x in r3) + ")")
    if R1 and R1b and R2 and R3: SEC.append((o["2024+"][0][1], ad))
# ⚠️ zayıf coin
yaz("\n## 3) ⚠️ zayıf coin (tahmini isabet < %52, Y2)\n```")
zy = E.y2h < 52; oz = {}
for dn, a, b in DD:
    md = donem(E.t, a, b); oz[dn] = (int((md & zy).sum()), 100 * E.ok[md & zy].mean(), 100 * E.net[md & zy].mean(), 100 * E.ok[md & ~zy].mean(), 100 * E.net[md & ~zy].mean())
    yaz(f"{dn:14s} zayıf: {oz[dn][0]:5d} · %{oz[dn][1]:4.1f} · {oz[dn][2]:+.2f}   diğerleri: %{oz[dn][3]:4.1f} · {oz[dn][4]:+.2f}")
UY = all(oz[dn][0] >= MIN[dn] and oz[dn][2] < 0 for dn in MIN)
yaz("```\n## Önceden yazılı karar")
yaz(f"- Sıralama: " + (f"✅ {max(SEC)[1]} → canlı sıralamaya önerilir (sinyal sayısı değişmez)" if SEC else "❌ hiçbir varyant geçmedi → sıralama aynı kalır"))
yaz(f"- ⚠️ zayıf coin işareti: " + ("✅ önerilir (sinyal silinmez)" if UY else "❌ geçmedi"))
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("coin_gecmis_sonuc.md", "w").write("\n".join(L) + "\n")
