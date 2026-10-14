# gozden.py — GÖZDEN KAÇAN İYİ ADAYLAR (kullanıcı isteği 14.10.2026: tüm geçmiş testleri tara, kanıtlı olanları test et, geçerse ekle). Yalnız test.
# Kaynak: kosul_tara.py (11.10) "İYİLEŞTİR ✅ ana" ve "YÜKSELT 🔸 yedek" bulguları — o zamanki eski sinyal setinde, plasebo 17 vs 4,7. Bugünkü sette hiç sınanmadılar.
# A) ✅ ANA SİNYALLERE ÖNCELİK İŞARETİ (sayı değişmez) — bugünkü ana set (💵 / ana coin 🧪 yalnız 📉 dip iken; 🌐🤝 / 🌐🧪 dahil):
#    M1 BTC Coinbase primi z ≥ 2 · M2 Coinbase BTC hacmi (24 s) z ≥ 2 · M3 Binance BTC ort. işlem büyüklüğü (24 s) z ≥ 2 · M4 coin'ler arası ayrışma (24 s getiri yayılımı) z ≥ 1
#    M5 DVOL BTC z ≥ 1 · M6 coin primi − BTC primi ≤ −2 · M7 S&P 500 5 gün z ≤ −2 (1 gün gecikmeli)
#    Ölçüt (fon_ana.py / 💧 ile aynı): K0 üç dönemde isabet ≥ ana +2 puan VE net ≥ ana +0,10 (30/30/10) · K1 40 kaydırmalı plasebo %95 üstü (isabet ve net) ·
#    K2 dip/momentum dışında da (20/20/10) · K3 2024+ haftalık blok alt sınır > 0 · K4 ≥ 10 sinyalli coin'lerin ≥ %60'ında daha isabetli (en az 3 coin) → hepsi geçerse işaret adayı.
# B) PANEL → ANA YÜKSELTME: coin primi −1…0 (gönderilmeyen) 🤝/🔇/🧪 sinyalleri + 🔥 KuCoin BTC fonlaması z ≥ 2 (kosul_tara: %62 · %67 · %62).
#    Ölçüt: üç dönemde ana çizgisi (isabet ≥ %55,9 · %58,6 · %59,1 VE net ≥ +0,30 · +0,647 · +0,589; 30/30/10) VE 2024+ alt sınır > 0 VE 30 ve 60 gün kaydırılmış koşul geçmez.
# CANLIYA KENDİLİĞİNDEN EKLENMEZ: geçenler rapor edilir.
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
# ---------------- Binance coin fonlaması ----------------
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

# ---------------- koşul verileri ----------------
SIG1 = {nm: np.log(o.close).diff().rolling(720, min_periods=168).std() for nm, o in OH.items()}
RZS = {nm: (np.log(o.close) - np.log(o.close).shift(24)) / (SIG1[nm] * np.sqrt(24)) for nm, o in OH.items()}
def ku_btc():
    out, a = [], pd.Timestamp("2022-03-01", tz="UTC")
    while a < pd.Timestamp.now(tz="UTC"):
        b = a + pd.Timedelta(days=30)
        for k in range(4):
            try: j = requests.get("https://api-futures.kucoin.com/api/v1/contract/funding-rates", params={"symbol": "XBTUSDTM", "from": int(a.timestamp() * 1000), "to": int(b.timestamp() * 1000)}, timeout=30).json(); break
            except Exception: j = None; time.sleep(1 + k)
        if isinstance(j, dict) and isinstance(j.get("data"), list): out += j["data"]
        a = b
    K_ = pd.DataFrame(out).drop_duplicates("timepoint"); s = pd.Series(K_.fundingRate.astype(float).values, index=pd.DatetimeIndex(pd.to_datetime(K_.timepoint.astype("int64"), unit="ms", utc=True)).as_unit("ns")).sort_index()
    return ((s - s.rolling(90, min_periods=30).mean()) / (s.rolling(90, min_periods=30).std() + 1e-12)).dropna()
KUB = ku_btc()
def asof(seri, tt):
    s = seri.dropna(); i = s.index.searchsorted(tt, side="right") - 1; return np.where(i >= 0, s.values[np.clip(i, 0, None)], np.nan)
BU4 = EX["BTCUSDT"].u4.fillna(False).astype(bool); BU4.index = pd.DatetimeIndex(BU4.index).tz_convert("UTC").as_unit("ns")
BZS = RAW["BTC"].z
def kosullar(kay=0):
    t = tz_ - pd.Timedelta(hours=kay); rz = np.full(len(Ez), np.nan); fb = np.full(len(Ez), np.nan); zc = np.full(len(Ez), np.nan)
    for nm in set(nmv):
        m = nmv == nm
        if nm in RZS: rz[m] = RZS[nm].reindex(t[m]).values
        if nm in FON: fb[m] = asof(FON[nm], t[m])
        if nm in RAW: zc[m] = RAW[nm].z.reindex(t[m]).values
    zb = BZS.reindex(t).values; ku = asof(KUB, t); u4 = BU4.reindex(t).fillna(False).values.astype(bool)
    kt = pd.Series(nmv).astype(str) + "|" + pd.Series(t.floor("h").astype(str)); aile_say = pd.DataFrame({"k": kt, "a": ail}).groupby("k").a.nunique()
    cift = (kt.map(aile_say).values >= 2) if kay == 0 else (pd.Series(nmv).astype(str) + "|" + pd.Series((tz_ - pd.Timedelta(hours=kay)).floor("h").astype(str))).map(
        pd.DataFrame({"k": pd.Series(nmv).astype(str) + "|" + pd.Series(tz_.floor("h").astype(str)), "a": ail}).groupby("k").a.nunique()).fillna(0).values >= 1
    n0 = lambda x: np.nan_to_num(x, nan=0)
    return {"K1 📉 dip": n0(rz) <= -2, "K2 🚀 momentum": n0(rz) >= 2, "K3 💸 coin fonlaması": n0(fb) >= 2, "K4 🔥 BTC fonlaması": n0(ku) >= 2,
            "K5 BTC 4s çok güçlü": u4, "K6 coin primi ≥ 2": n0(zc) >= 2, "K7 BTC ⛔": np.nan_to_num(zb, nan=0) <= -1,
            "K8 BTC hafif eksi": (np.nan_to_num(zb, nan=9) > -1) & (np.nan_to_num(zb, nan=9) <= 0), "K9 çifte onay": np.asarray(cift, bool)}
RZ_ = kosullar()["K1 📉 dip"]

P23x = pd.Timestamp("2022-06-01", tz="UTC")
DUZ = (("2022-06→2023", (tz_ >= P23x) & (tz_ < A24_)), ("2024+", tz_ >= A24_), ("2026", tz_ >= A26_)); m24 = tz_ >= A24_
OKv, NETv = Ez.ok.values.astype(bool), Ez.net.values
def st(m): return {dn: (int((m & md).sum()), 100 * OKv[m & md].mean() if (m & md).any() else np.nan, 100 * NETv[m & md].mean() if (m & md).any() else np.nan) for dn, md in DUZ}
def sat(ad, o): return f"{ad[:42]:42s}" + " | ".join(f"{o[dn][0]:5d} · %{o[dn][1]:4.1f} · {o[dn][2]:+.2f}" if o[dn][0] >= 5 else f"{o[dn][0]:5d} az" for dn in o)
KK = kosullar(); DIPm, MOMm = KK["K1 📉 dip"], KK["K2 🚀 momentum"]
usd = ail == "💵 ABD alıyor (tek başına)"; ana24 = c24 & (z >= 0)
ANA_NOW = (ANA & ~usd & ~ana24) | (ANA & (usd | ana24) & DIPm)                                   # bugünkü canlı ana (çekirdek coin'ler)
# ---------------- piyasa göstergeleri ----------------
V = pd.read_pickle(f("**/kosul_veri.pkl")[0])
def hiz(s): s = pd.Series(s).astype(float); s.index = pd.DatetimeIndex(s.index).tz_convert("UTC") if s.index.tz is not None else pd.DatetimeIndex(s.index).tz_localize("UTC"); return s[~s.index.duplicated()].sort_index()
def z720(s): return (s - s.rolling(720, min_periods=168).mean()) / (s.rolling(720, min_periods=168).std() + 1e-12)
G = {}
bn, cb_ = V.get("bn_BTC"), V.get("cb_BTC")
q24 = hiz(bn.qv).rolling(24).sum(); G["M3"] = z720(np.log(q24 / hiz(bn.trades).rolling(24).sum()))
G["M2"] = z720(np.log(hiz(cb_.volume).rolling(24).sum()))
G["M5"] = z720(hiz(V["dvol_BTC"]))
y = hiz(V["y_spx"]).dropna(); zz = np.log(y).diff(5); zz = (zz - zz.rolling(60, min_periods=20).mean()) / (zz.rolling(60, min_periods=20).std() + 1e-12); zz.index = zz.index + pd.Timedelta(days=1)
G["M7"] = zz
C = pd.DataFrame({nm: v.c for nm, v in RAW.items()}); C.index = pd.DatetimeIndex(C.index).tz_convert("UTC"); r24 = np.log(C).diff(24); G["M4"] = z720(r24.std(axis=1))
G["M1"] = RAW["BTC"].z
ESIK = {"M1": (">=", 2), "M2": (">=", 2), "M3": (">=", 2), "M4": (">=", 1), "M5": (">=", 1), "M7": ("<=", -2)}
AD = {"M1": "M1 BTC Coinbase primi z ≥ 2", "M2": "M2 Coinbase BTC hacmi z ≥ 2", "M3": "M3 Binance BTC ort. işlem büyüklüğü z ≥ 2", "M4": "M4 coin'ler arası ayrışma z ≥ 1",
      "M5": "M5 DVOL BTC z ≥ 1", "M6": "M6 coin primi − BTC primi ≤ −2", "M7": "M7 S&P 500 5 gün z ≤ −2"}
def kos(mk, kay=0):
    t = tz_ - pd.Timedelta(hours=kay)
    if mk == "M6":
        zc = np.full(len(Ez), np.nan)
        for nm in set(nmv):
            m = nmv == nm
            if nm in RAW: zc[m] = RAW[nm].z.reindex(t[m]).values
        return np.nan_to_num(zc - RAW["BTC"].z.reindex(t).values, nan=0) <= -2
    s = G[mk]; v = asof(s.dropna(), t) if mk == "M7" else s.reindex(t, method="ffill" if mk in ("M5",) else None).values
    op, th = ESIK[mk]; v = np.nan_to_num(v, nan=(-99 if op == ">=" else 99)); return v >= th if op == ">=" else v <= th
A_ = ANA_NOW & (nmv != "BTC") | (ANA_NOW & (nmv == "BTC")); NOR = ~DIPm & ~MOMm; OA = st(A_)
yaz(f"# 🔎 Gözden kaçan adaylar — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nBugünkü ✅ ana (çekirdek coin'ler): {A_.sum():,} · panel (coin primi −1…0): {(GON & (z > -1) & (z < 0)).sum():,} · {time.time()-T0:.0f} sn\n")
yaz("## A) ✅ ana sinyallere öncelik işareti\n_sinyal · isabet · işlem başı net % — 2022-06→2023 | 2024+ | 2026_\n```"); yaz(sat("✅ ana (bugünkü)", OA))
SON = []
for mk in ("M1", "M2", "M3", "M4", "M5", "M6", "M7"):
    c = kos(mk); oc = st(A_ & c); yaz(sat(AD[mk], oc))
    K0 = all(oc[dn][0] >= mn and oc[dn][1] >= OA[dn][1] + 2 and oc[dn][2] >= OA[dn][2] + 0.10 for dn, mn in (("2022-06→2023", 30), ("2024+", 30), ("2026", 10)))
    def fark(cc): a = A_ & m24; b = a & cc; return (100 * (OKv[b].mean() - OKv[a].mean()), 100 * (NETv[b].mean() - NETv[a].mean())) if b.sum() >= 10 else (np.nan, np.nan)
    g1 = fark(c); PLS = np.array([fark(kos(mk, int(d * 24))) for d in np.linspace(30, 400, 40)])
    p95h, p95n = (np.nanpercentile(PLS[:, i], 95) if np.isfinite(PLS[:, i]).any() else np.nan for i in (0, 1)); K1 = bool(g1[0] > p95h and g1[1] > p95n)
    on, ob = st(A_ & NOR & c), st(A_ & NOR); ks = [dn for dn in on if not (dn == "2026" and on[dn][0] < 10)]
    K2 = len(ks) >= 2 and all(on[dn][0] >= 20 and on[dn][1] >= ob[dn][1] + 2 and on[dn][2] >= ob[dn][2] + 0.10 for dn in ks)
    b = A_ & c & m24; lo_ = wboot(NETv[b] - NETv[A_ & m24].mean(), tz_[b])[0] if b.sum() >= 10 else np.nan; K3 = bool(lo_ > 0)
    sk = []
    for nm in sorted(set(nmv)):
        mc = (nmv == nm) & A_ & (tz_ >= P23x); mb = mc & c
        if mb.sum() >= 10: sk.append((OKv[mb].mean() > OKv[mc].mean()))
    K4 = len(sk) >= 3 and np.mean(sk) >= 0.6
    SON.append((AD[mk], K0, K1, K2, K3, K4, g1, p95h, p95n, lo_, f"{sum(sk)}/{len(sk)}"))
yaz("```")
i_ = lambda x: "✅" if x else "❌"
for ad, K0, K1, K2, K3, K4, g1, p95h, p95n, lo_, kk in SON:
    yaz(f"- **{ad}** — K0 {i_(K0)} · K1 plasebo {i_(K1)} (isabet {g1[0]:+.1f} vs %95 {p95h:+.1f}; net {g1[1]:+.2f} vs {p95n:+.2f}) · K2 dipten bağımsız {i_(K2)} · K3 {i_(K3)} ({100*lo_:+.2f}) · K4 {i_(K4)} ({kk})")
GA = [s_[0] for s_ in SON if all(s_[1:6])]
# ---------------- B) panel → ana (🔥) ----------------
BEN = {"2022-06→2023": (55.9, 0.30), "2024+": (58.6, 0.647), "2026": (59.1, 0.589)}
def ben(o): return all(o[dn][0] >= mn and o[dn][1] >= BEN[dn][0] and o[dn][2] >= BEN[dn][1] for dn, mn in (("2022-06→2023", 30), ("2024+", 30), ("2026", 10)))
PAN = GON & (z > -1) & (z < 0) & np.isin(ail, ["coin 🤝 ortak", "coin 🔇 sessiz", "🧪 24 saat", "coin tek başına"])
yaz("\n## B) Panel (coin primi −1…0) → ana, 🔥 BTC fonlaması yüksekken\n```")
yaz(sat("panel (coin primi −1…0) hepsi", st(PAN)))
GB = []
for ad, kay in (("+ 🔥 BTC fonlaması z ≥ 2", 0), ("  (plasebo 30 gün)", 720), ("  (plasebo 60 gün)", 1440)):
    c = kosullar(kay)["K4 🔥 BTC fonlaması"]; o = st(PAN & c); yaz(sat(ad, o)); GB.append(ben(o))
b = PAN & kosullar(0)["K4 🔥 BTC fonlaması"] & m24; loB = wboot(NETv[b], tz_[b])[0] if b.sum() >= 10 else np.nan
yaz(f"```\n2024+ alt sınır {100*loB:+.2f}")
GBok = GB[0] and loB > 0 and not GB[1] and not GB[2]
yaz("\n## Önceden yazılı karar (canlıya kendiliğinden EKLENMEZ)")
yaz("- A) " + (f"✅ geçen işaret(ler): {', '.join(GA)}" if GA else "❌ hiçbir işaret K0–K4'ün hepsini geçmedi"))
yaz("- B) " + ("✅ 🔥 fonlama yüksekken panel (coin primi −1…0) sinyalleri de ana olabilir" if GBok else "❌ geçmedi → 🔥 yükseltmesi yalnız yedeklerde kalır"))
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("gozden_sonuc.md", "w").write("\n".join(L) + "\n")
