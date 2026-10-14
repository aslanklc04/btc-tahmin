# kombin.py — 🔸 YEDEK SİNYALLERİ ✅ ANA'YA YÜKSELTECEK KOMBİNASYONLAR (kullanıcı isteği 14.10.2026: "kombinasyon yap dene, hiçbir şey ekleme, sonucu söyle"; yalnız test).
# Yedek aileler (canlıdaki gibi): Y1 💵 ABD alıyor (hepsi) · Y2 ana coin 🧪 24 saat (coin primi ≥ 0, 📉 dip değil) · Y3 🔇/🪙 coin tek başına (coin primi ≥ 0, 🔀 değil).
# Koşullar (canlıda hesaplanabilen, önceden sabit): K1 📉 dip (24 s z ≤ −2) · K2 🚀 momentum (z ≥ 2) · K3 💸 coin'in Binance fonlaması z ≥ 2 · K4 🔥 KuCoin BTC fonlaması z ≥ 2 (canlıda zaten yükseltiyor; kıyas)
#   K5 BTC 4 saat çok güçlü ↑ aynı saatte · K6 coin primi z ≥ 2 · K7 BTC primi ⛔ (z ≤ −1) · K8 BTC primi hafif eksi (−1 < z ≤ 0) · K9 çifte onay (aynı coin'de aynı saatte başka aileden sinyal)
#   Tekli 9 + ikili 36 koşul × 3 aile = 135 aday.
# ÖNCEDEN YAZILI KARAR (sonuçlar görülmeden): aday GEÇER = üç dönemde (2022-06→2023 · 2024+ · 2026) ana çizgisi (isabet ≥ %55,9 · %58,6 · %59,1 VE net ≥ +0,30 · +0,647 · +0,589;
#   en az 30 / 30 / 10 sinyal) VE 2024+ haftalık blok %5 alt sınırı > 0 VE plasebo: koşul 30 ve 60 gün kaydırılınca ikisinde de geçmez.
#   Genel şans kontrolü: gerçek geçen sayısı ≥ (30 g + 60 g plasebo ortalaması) + 2 olmalı; değilse hiçbiri önerilmez. CANLIYA HİÇBİR ŞEY EKLENMEZ — yalnız rapor.
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
YA = {"Y1 💵 ABD alıyor": ail == "💵 ABD alıyor (tek başına)", "Y2 ana coin 🧪 24 s": c24 & (z >= 0) & ~RZ_, "Y3 🔇/🪙 coin tek": YED}
MIN = {"2022-06→2023": 30, "2024+": 30, "2026": 10}
def olc(m):
    o = {}
    for dn, md, hf in DN:
        x = Ez[m & md]; o[dn] = (len(x), 100 * x.ok.mean() if len(x) else np.nan, 100 * x.net.mean() if len(x) else np.nan)
    x = Ez[m & DN[1][1]]; lo = wboot(x.net.values, x.t.values, 300)[0] if len(x) >= 10 else np.nan
    gec = all(o[dn][0] >= MIN[dn] and o[dn][1] >= BEN[dn][0] and o[dn][2] >= BEN[dn][1] for dn in MIN) and lo > 0
    return gec, o, lo
def yz(o): return " | ".join(f"{o[dn][0]:5d} · %{o[dn][1]:4.1f} · {o[dn][2]:+.2f}" if o[dn][0] >= 5 else f"{o[dn][0]:5d} az" for dn, _, _ in DN)
import itertools
def adaylar(KS):
    ks = list(KS); out = [(k, KS[k]) for k in ks]
    for a, b in itertools.combinations(ks, 2): out.append((f"{a.split()[0]}+{b.split()[0]}", KS[a] & KS[b]))
    return out
K0, K30, K60 = kosullar(0), kosullar(720), kosullar(1440)
A0, A30, A60 = adaylar(K0), adaylar(K30), adaylar(K60)
yaz(f"# 🔸→✅ Yedekleri ana'ya yükseltecek kombinasyonlar — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n"
    + " · ".join(f"{k}: {v.sum():,}" for k, v in YA.items()) + f" · coin fonlaması: {len(FON)} coin · {time.time()-T0:.0f} sn\n")
yaz("_sinyal sayısı · isabet · işlem başı net % — 2022-06→2023 | 2024+ | 2026 · ana çizgisi: %55,9 +0,30 | %58,6 +0,65 | %59,1 +0,59_\n")
GER, PL = [], 0
for ya, ym in YA.items():
    _, o, _ = olc(ym); yaz(f"\n### {ya}\n```\n{'(hepsi)':28s} {yz(o)}")
    for (ad, c), (_, c30), (_, c60) in zip(A0, A30, A60):
        g, o, lo = olc(ym & c); g30 = olc(ym & c30)[0]; g60 = olc(ym & c60)[0]; PL += g30 + g60
        if o["2024+"][0] >= 30 or g: yaz(f"{ad[:28]:28s} {yz(o)}{'  ★ GEÇTİ' if g else ''}{' (plasebo da geçti ✗)' if g and (g30 or g60) else ''}")
        if g and not g30 and not g60: GER.append((ya, ad, o, lo))
    yaz("```")
plo = PL / 2
yaz(f"\n**Gerçek veride geçen (plasebosuz):** {len(GER)} · **plasebo ortalaması:** {plo:.1f} (135 aday × 2 kaydırma)")
OKG = len(GER) >= plo + 2
yaz("\n## Önceden yazılı karar (canlıya EKLENMEZ, yalnız rapor)")
if GER and OKG:
    for ya, ad, o, lo in GER: yaz(f"- ✅ {ya} + {ad}: " + yz(o) + f" · 2024+ alt sınır {100*lo:+.2f}")
elif GER: yaz(f"- ⚠️ {len(GER)} aday geçti ama plasebodan açıkça fazla değil → şanstan ayırt edilemiyor")
else: yaz("- ❌ Hiçbir kombinasyon yedekleri ana çizgisine çıkarmadı")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("kombin_sonuc.md", "w").write("\n".join(L) + "\n")
