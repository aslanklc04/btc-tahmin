# fon_coin.py — COİN'İN KENDİ FONLAMASI (yalnız test). teknik_tara.py'de C4b (coin'in Binance fonlaması z ≥ 2 iken ✅ ana sinyaller %59 · %65 · %64, net +0,88 · +1,67 · +1,78) geçti.
# Sorular: (1) Canlıdaki 🔥 (KuCoin BTC fonlaması z ≥ 2) ile ne kadar örtüşüyor? (2) 🔥 yokken de işe yarıyor mu? (3) Canlıda alınabilen KuCoin coin fonlaması Binance'in yerini tutuyor mu?
# ÖNCEDEN YAZILI KARAR (12.10.2026): canlıya yalnız KuCoin coin fonlamasıyla eklenir. Şart: ✅ ana sinyallerde "KuCoin coin fonlaması z ≥ 2 VE 🔥 BTC fonlaması yok"
#   dilimi üç dönemde de ana ortalamasından isabette ≥ +2 puan VE nette ≥ +0,10 (≥ 30 / 30 / 10 sinyal) → mesajda öne alınır.
#   Ayrıca 🔸 yedek / gönderilmeyenlerde aynı dilim üç dönemde ana set ölçütünü geçerse → ✅ ana olur. Geçmezse eklenmez (🔥 zaten fonlamayı kullanıyor).
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
yaz(f"# 💸 Coin'in kendi fonlaması (Binance ↔ KuCoin) ve 🔥 BTC fonlamasıyla örtüşme — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nOlay: ✅ ana {ANA.sum():,} · 🔸 yedek {YED.sum():,} · gönderilmeyen {GON.sum():,}\n")
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

# ---------------- KuCoin: BTC ve coin fonlaması ----------------
def ku_gecmis(sym):
    out, a = [], pd.Timestamp("2022-03-01", tz="UTC")
    while a < pd.Timestamp.now(tz="UTC"):
        b = a + pd.Timedelta(days=30)
        for k in range(4):
            try:
                j = requests.get("https://api-futures.kucoin.com/api/v1/contract/funding-rates", params={"symbol": sym, "from": int(a.timestamp() * 1000), "to": int(b.timestamp() * 1000)}, timeout=30).json()
                if isinstance(j, dict) and isinstance(j.get("data"), list): out += j["data"]
                break
            except Exception: time.sleep(1 + k)
        a = b; time.sleep(0.12)
    if not out: return None
    K_ = pd.DataFrame(out).drop_duplicates("timepoint"); s = pd.Series(K_.fundingRate.astype(float).values, index=pd.DatetimeIndex(pd.to_datetime(K_.timepoint, unit="ms", utc=True)).round("min").as_unit("ns")).sort_index()
    s = s[~s.index.duplicated()]; return (s - s.rolling(90, min_periods=30).mean()) / (s.rolling(90, min_periods=30).std() + 1e-12)
try:
    kc = requests.get("https://api-futures.kucoin.com/api/v1/contracts/active", timeout=30).json().get("data", [])
    KSYM = {}
    for c in kc:
        if c.get("quoteCurrency") == "USDT" and str(c.get("symbol", "")).endswith("USDTM"):
            bc = "BTC" if c.get("baseCurrency") == "XBT" else c.get("baseCurrency"); KSYM.setdefault(bc, c["symbol"])
except Exception as e: KSYM = {}; print("kucoin liste", e)
KU = {}
for nm in sorted(set(nmv)):
    sym = KSYM.get(nm) or KSYM.get("1000" + nm)
    if sym: v = ku_gecmis(sym); KU[nm] = v if v is not None else None
KU = {k: v for k, v in KU.items() if v is not None}
yaz(f"Binance coin fonlaması: {len(FON)} coin · KuCoin coin fonlaması: {len(KU)} coin ({', '.join(f'{k}:{v.index[0]:%Y-%m}' for k, v in sorted(KU.items()))}) · {time.time()-T0:.0f} sn\n")
def asof(seri, tt):
    s = seri.dropna(); i = s.index.searchsorted(tt, side="right") - 1; return np.where(i >= 0, s.values[np.clip(i, 0, None)], np.nan)
fb, fk = np.full(len(Ez), np.nan), np.full(len(Ez), np.nan)
for nm in set(nmv):
    m = nmv == nm
    if nm in FON: fb[m] = asof(FON[nm], tz_[m])
    if nm in KU: fk[m] = asof(KU[nm], tz_[m])
K2 = (asof(KU["BTC"], tz_) >= 2) if "BTC" in KU else np.zeros(len(Ez), bool)
ok_ = np.isfinite(fb) & np.isfinite(fk)
yaz(f"Binance ↔ KuCoin coin fonlaması z ilişkisi (aynı olaylarda): {np.corrcoef(fb[ok_], fk[ok_])[0, 1]:+.2f} · ikisi birden z ≥ 2 / biri z ≥ 2: {((fb >= 2) & (fk >= 2)).sum()} / {((fb >= 2) | (fk >= 2)).sum()}\n")
DN = (("2022-06→2023", (tz_ >= P0) & (tz_ < A24_), (A24_ - P0).days / 7), ("2024+", tz_ >= A24_, HAF["2024+"]), ("2026", tz_ >= A26_, HAF["2026"]))
BEN = {"2022-06→2023": (55.9, 0.30), "2024+": (58.6, 0.647), "2026": (59.1, 0.589)}; MIN = {"2022-06→2023": 30, "2024+": 30, "2026": 10}
def ist(m): return {dn: (int((m & md).sum()), 100 * Ez.ok.values[m & md].mean() if (m & md).any() else np.nan, 100 * Ez.net.values[m & md].mean() if (m & md).any() else np.nan) for dn, md, _ in DN}
def yazi(o): return " | ".join(f"{o[dn][0]/hf:5.1f}/hf · %{o[dn][1]:4.1f} · {o[dn][2]:+.2f} ({o[dn][0]})" if o[dn][0] >= 5 else f"{o[dn][0]:5d} az" for dn, _, hf in DN)
OANA = ist(ANA)
def anaplus(o): return all(o[dn][0] >= MIN[dn] for dn in MIN) and all(o[dn][1] >= OANA[dn][1] + 2 and o[dn][2] >= OANA[dn][2] + 0.10 for dn in MIN)
def benplus(o): return all(o[dn][0] >= MIN[dn] for dn in MIN) and all(o[dn][1] >= BEN[dn][0] and o[dn][2] >= BEN[dn][1] for dn in MIN)
yaz("_haftada · isabet · işlem başı net % (sinyal) — 2022-06→2023 | 2024+ | 2026_\n```")
yaz(f"{'✅ ANA (hepsi)':58s}{yazi(OANA)}")
SAT = (("Binance coin fonlaması z ≥ 2 (teknik_tara C4b)", fb >= 2), ("  └ 🔥 BTC fonlaması da yüksek (örtüşen)", (fb >= 2) & K2), ("  └ 🔥 yokken (yalnız coin)", (fb >= 2) & ~K2),
       ("KuCoin coin fonlaması z ≥ 2 (canlıda alınabilir)", fk >= 2), ("  └ 🔥 BTC fonlaması da yüksek (örtüşen)", (fk >= 2) & K2), ("  └ 🔥 yokken (yalnız coin) ← KARAR", (fk >= 2) & ~K2),
       ("🔥 BTC fonlaması yüksek (canlıdaki, bilgi)", K2))
for ad, c in SAT: yaz(f"{ad:58s}{yazi(ist(ANA & c))}")
yaz("— 🔸 yedek / gönderilmeyen —")
for ad, c in (("yedek · KuCoin coin fonlaması z ≥ 2, 🔥 yok", (fk >= 2) & ~K2), ("gönderilmeyen · KuCoin coin fonlaması z ≥ 2, 🔥 yok", (fk >= 2) & ~K2)):
    grp = YED if ad.startswith("yedek") else GON; yaz(f"{ad:58s}{yazi(ist(grp & c))}")
yaz("```")
oK = ist(ANA & (fk >= 2) & ~K2); oY = ist(YED & (fk >= 2) & ~K2); oG = ist(GON & (fk >= 2) & ~K2)
yaz("\n## Önceden yazılı karar\n"
    + f"- ✅ ana öncelik (KuCoin coin fonlaması z ≥ 2, 🔥 yokken): {'✅ GEÇTİ → öne alınır' if anaplus(oK) else '❌ geçmedi'}\n"
    + f"- 🔸 yedek → ana: {'✅ GEÇTİ' if benplus(oY) else '❌ geçmedi'} · gönderilmeyen → ana: {'✅ GEÇTİ' if benplus(oG) else '❌ geçmedi'}")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("fon_coin_sonuc.md", "w").write("\n".join(L) + "\n")
