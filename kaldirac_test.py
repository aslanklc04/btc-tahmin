# kaldirac_test.py — KALDIRAÇLI İŞLEM İÇİN MODEL DÜZENİ (yalnız test). Olaylar vadeli_test.py ile aynı (canlıdaki ✅ ana sinyaller, Binance vadeli fiyatı, limit emir, fonlama dahil).
# Soru: kaldıraç ve teminat nasıl ayarlanırsa hesap en iyi büyür, en az düşer? Basit hesap (bileşik değil): her sinyale BAŞLANGIÇ sermayesinin f'i teminat,
#   pozisyon = teminat × kaldıraç; işlem içi en derin düşüş likidasyon mesafesini (1/kaldıraç − %0,5) aşarsa teminat −%100. Aynı anda açık teminat sermayeyi aşamaz (aşanlar atlanır).
# DÜZENLER: D0 sabit 3x (bugünkü mesaj önerisi) · sabit 1/2/5/10x · saat tavanı (aynı saatteki sinyaller toplam %10'u bölüşür) ·
#   oynaklığa göre kaldıraç L = 1 / (k × σ × √H) (σ: coin'in son 30 gün saatlik oynaklığı, H: tutma saati), 1–10x · türe göre kaldıraç (2022–23'teki %99 derin düşüşün yarısı) ·
#   likidasyon öncesi stop (likidasyon mesafesinin %70'inde çık).
# ÖNCEDEN YAZILI KARAR (12.10.2026): en yüksek "yıllık getiri / en büyük düşüş" oranı 2022-06→2023'te seçilir (en büyük düşüş ≤ %30 olanlar arasından);
#   seçilen düzen 2024+ ve 2026'da da D0'dan yüksek oran verirse önerilir ve mesajlara sinyal başına kaldıraç önerisi olarak yazılır.
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
import io, zipfile, requests
from concurrent.futures import ThreadPoolExecutor
CAN24 = {os.path.basename(p)[8:-11] for p in glob.glob(f"{CD}/model24_*USDT.pkl.gz")}
GENIS = {l.strip()[:-4] for l in open(f"{CD}/genis_liste.txt") if l.strip()}
Ez["zB"] = RAW["BTC"].z.reindex(tz_).values; zB = Ez.zB.values; nmv = Ez.nm.values; ail = Ez.aile.values
c24 = (ail == "🧪 24 saat") & np.isin(nmv, list(CAN24)); dis24 = (ail == "🧪 24 saat") & ~c24
TUR = {"🤝 BTC ile birlikte (ana coin'ler)": (ail == "coin 🤝 ortak") & (z >= 0),
       "🧪 24 saat (ana 10 coin)": c24 & (z >= 0),
       "🔇🔀 BTC sessiz + coin alınıyor": (ail == "coin 🔇 sessiz") & (z > 0) & np.isfinite(zB) & (zB > -1) & (zB <= 0),
       "💵 ABD güçlü alıyor": ail == "💵 ABD alıyor (tek başına)",
       "⛓️ ETH arz/talep (7 gün)": ail == "⛓️ ETH",
       "🧑 küçük yatırımcı (7 gün)": ail == "🧑 küçük yatırımcı"}
ANA0 = np.zeros(len(Ez), bool)
for v in TUR.values(): ANA0 |= v
key = pd.Series(nmv).astype(str) + "|" + pd.Series(tz_.floor("h").astype(str)); kset = set(key[((ail == "coin 🤝 ortak") | (ail == "coin 🔇 sessiz"))])
tek_dup = (ail == "coin tek başına") & key.isin(kset).values
YED = ~ANA0 & ~dis24 & ~tek_dup & (z > -1) & (ail != "🔻 BTC kısa")
out, a = [], pd.Timestamp("2022-03-01", tz="UTC")                                                  # 🔥 KuCoin fonlaması (canlıdaki gibi)
while a < pd.Timestamp.now(tz="UTC"):
    b = a + pd.Timedelta(days=30)
    try:
        j = requests.get("https://api-futures.kucoin.com/api/v1/contract/funding-rates", params={"symbol": "XBTUSDTM", "from": int(a.timestamp() * 1000), "to": int(b.timestamp() * 1000)}, timeout=30).json()
        if isinstance(j, dict) and isinstance(j.get("data"), list): out += j["data"]
    except Exception as e: print("kucoin", e)
    a = b
K_ = pd.DataFrame(out).drop_duplicates("timepoint"); ku = pd.Series(K_.fundingRate.astype(float).values, index=pd.to_datetime(K_.timepoint, unit="ms", utc=True)).sort_index()
kz = ((ku - ku.rolling(90, min_periods=30).mean()) / (ku.rolling(90, min_periods=30).std() + 1e-12)).dropna()
i_ = kz.index.searchsorted(tz_.floor("h"), side="right") - 1; K2 = np.nan_to_num(np.where(i_ >= 0, kz.values[np.clip(i_, 0, None)], np.nan), nan=0) >= 2
TERFI = YED & K2; YED_G = YED & ~K2
lab = np.full(len(Ez), "", dtype=object)
for ad, m in TUR.items(): lab[m & (lab == "")] = ad
lab[TERFI & (lab == "")] = "🔥 fonlama yüksekken yükselen"; lab[YED_G & (lab == "")] = "🔸 yedek (karşılaştırma)"
EVT = pd.DataFrame({"lab": lab, "nm": nmv, "t": tz_, "H": Ez.H.values.astype(int), "snet": Ez.net.values, "yon": Ez.yon.values})
EVT = EVT[EVT.lab != ""].copy()
# 🌐 geniş liste (genis_esik.py / ozet_tum.py ile aynı)
def bul(p):
    x = glob.glob(p, recursive=True); return x[0] if x else None
Bg = pd.read_pickle(bul("ga/**/disa_BTCUSDT.pkl")); Bg.index = pd.DatetimeIndex(Bg.index).tz_convert("UTC"); GV = []
for nm in sorted(GENIS):
    sym = nm + "USDT"; pz, d1, d24 = bul(f"ga/**/prim_{sym}.pkl"), bul(f"ga/**/disa_{sym}.pkl"), bul(f"ga/**/disa24_{sym}.pkl")
    if pz is None: continue
    Z = pd.read_pickle(pz).astype("float64"); Z.index = pd.DatetimeIndex(Z.index).tz_convert("UTC")
    if d1:
        X = pd.read_pickle(d1); X.index = pd.DatetimeIndex(X.index).tz_convert("UTC"); bu4 = Bg.reindex(X.index).u4.fillna(False).astype(bool).values
        any_ = (X.star.fillna(False).astype(bool) | X.u4.fillna(False).astype(bool) | X.acls.fillna(False).astype(bool)).values & X.y4.notna().values
        ev = events(any_ & bu4, 4); t = X.index[ev]; GV.append(pd.DataFrame({"lab": "🌐🤝 yeni coinler BTC ile birlikte", "nm": nm, "t": t, "H": 4, "snet": np.exp(X.y4.values[ev]) - 1 - 0.0004, "z": Z.z.reindex(t).values}))
    if d24:
        D = pd.read_pickle(d24).astype("float64"); D.index = pd.DatetimeIndex(D.index).tz_convert("UTC")
        D = D.reindex(pd.date_range(D.index[0], D.index[-1], freq="1h", tz="UTC")); c = D.close.ffill(limit=3).values; n = len(D)
        m = np.nan_to_num(((D.S24 > 0) & (D.C24 >= D.T10_24)).values).astype(bool) & D.T10_24.notna().values & (np.arange(n) + 25 < n)
        ev = events(m, 24); t = D.index[ev]; GV.append(pd.DataFrame({"lab": "🌐🧪 yeni coinler 24 saat", "nm": nm, "t": t, "H": 24, "snet": c[ev + 24] / c[ev] - 1 - 0.0004, "z": Z.z.reindex(t).values}))
G = pd.concat(GV, ignore_index=True); G = G[np.isfinite(G.snet) & np.isfinite(G.z)]
G = G[((G.lab.str.startswith("🌐🤝")) & (G.z >= 2)) | ((G.lab.str.startswith("🌐🧪")) & (G.z >= 1.5))].drop(columns="z"); G["yon"] = 1
EVT = pd.concat([EVT, G], ignore_index=True); EVT["t"] = pd.DatetimeIndex(EVT.t).tz_convert("UTC").as_unit("ns")
FSON = pd.Timestamp("2026-10-01", tz="UTC"); EVT = EVT[(EVT.t >= P0) & (EVT.t + pd.to_timedelta(EVT.H, unit="h") < FSON)].reset_index(drop=True)
yaz(f"# 🎚️ Kaldıraçlı işlem için model düzeni — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nOlay: {len(EVT):,} ({EVT.nm.nunique()} coin) · dönem 2022-06 → 2026-09\n")
# ---------------- vadeli veri ----------------
SS = requests.Session(); AYLAR = [d.strftime("%Y-%m") for d in pd.date_range("2022-05-01", "2026-09-01", freq="MS")]
def zcsv(url):
    for k in range(4):
        try:
            r = SS.get(url, timeout=30)
            if r.status_code == 404: return None
            if r.status_code == 200:
                z_ = zipfile.ZipFile(io.BytesIO(r.content)); return pd.read_csv(z_.open(z_.namelist()[0]), header=None, dtype=str)
        except Exception: time.sleep(1 + k)
    return None
def vadeli(nm):
    sym = nm + "USDT"
    kl = [zcsv(f"https://data.binance.vision/data/futures/um/monthly/klines/{sym}/1h/{sym}-1h-{ym}.zip") for ym in AYLAR]
    kl = [x for x in kl if x is not None]
    if not kl: return nm, None, None
    k = pd.concat(kl); k = k[pd.to_numeric(k[0], errors="coerce").notna()].iloc[:, :6].astype(float); k.columns = ["t", "open", "high", "low", "close", "vol"]
    k["t"] = np.where(k.t > 1e14, k.t / 1000, k.t)                                                 # mikro saniyeli arşivler
    k.index = pd.DatetimeIndex(pd.to_datetime(k.t, unit="ms", utc=True) + pd.Timedelta(hours=1)).as_unit("ns"); k = k[~k.index.duplicated()].sort_index()
    fr = [zcsv(f"https://data.binance.vision/data/futures/um/monthly/fundingRate/{sym}/{sym}-fundingRate-{ym}.zip") for ym in AYLAR]
    fr = [x for x in fr if x is not None]; F = None
    if fr:
        f_ = pd.concat(fr); f_ = f_[pd.to_numeric(f_[0], errors="coerce").notna()]
        ft = f_[0].astype(float).values; ft = np.where(ft > 1e14, ft / 1000, ft)
        F = pd.Series(f_.iloc[:, -1].astype(float).values, index=pd.DatetimeIndex(pd.to_datetime(ft, unit="ms", utc=True)).round("min").as_unit("ns"))
        F = F[~F.index.duplicated()].sort_index()
    return nm, k[["high", "low", "close"]], F
with ThreadPoolExecutor(12) as ex: VD = {nm: (k, F) for nm, k, F in ex.map(vadeli, sorted(EVT.nm.unique()))}
yok = sorted(nm for nm, (k, F) in VD.items() if k is None); yaz(f"Vadeli verisi: {sum(k is not None for k, F in VD.values())} coin · vadelisi olmayan: {', '.join(yok) or '—'} · {time.time()-T0:.0f} sn\n")
# ---------------- 2) sinyal bazında ----------------
fr_, fc_, mae_, sg_ = np.full(len(EVT), np.nan), np.zeros(len(EVT)), np.full(len(EVT), np.nan), np.full(len(EVT), np.nan)
for nm, g in EVT.groupby("nm"):
    k, F = VD.get(nm, (None, None))
    if k is None: continue
    cum = F.cumsum() if F is not None and len(F) else None
    t0 = pd.DatetimeIndex(g.t); t1 = t0 + pd.to_timedelta(g.H.values, unit="h"); i0, i1 = k.index.get_indexer(t0), k.index.get_indexer(t1)
    lo_, cl_ = k.low.values, k.close.values; sg_k = np.log(k.close).diff().rolling(720, min_periods=168).std().values   # coin'in saatlik oynaklığı (son 30 gün, yalnız geçmiş)
    for j, (a0, a1) in enumerate(zip(i0, i1)):
        if a0 < 0 or a1 < 0 or a1 <= a0: continue
        ix_ = g.index[j]; yon = g.yon.values[j]; fr_[ix_] = yon * (cl_[a1] / cl_[a0] - 1); sg_[ix_] = sg_k[a0]
        mae_[ix_] = (lo_[a0 + 1:a1 + 1].min() / cl_[a0] - 1) if yon > 0 else -(k.high.values[a0 + 1:a1 + 1].max() / cl_[a0] - 1)
    if cum is not None:
        ci, cv = cum.index.values, cum.values
        def cat(tt): j = np.searchsorted(ci, tt.values, side="right") - 1; return np.where(j >= 0, cv[np.clip(j, 0, None)], 0.0)   # ≤ tt son birikimli fonlama
        c1, c0 = cat(t1), cat(t0)
        fc_[g.index] = g.yon.values * (c1 - c0)                                                      # long için ödenen fonlama (artı = maliyet)
EVT["fret"], EVT["fon"], EVT["mae"], EVT["sig"] = fr_, fc_, mae_, sg_
EVT["fnet_l"] = EVT.fret - 0.0004 - EVT.fon; EVT["fnet_p"] = EVT.fret - 0.0010 - EVT.fon
V = EVT[np.isfinite(EVT.fret) & np.isfinite(EVT.snet)].copy(); yaz(f"\nVadeliyle hesaplanabilen olay: {len(V):,} / {len(EVT):,}\n")
# ---------------- kaldıraç düzenleri ----------------
import heapq
SIRA = list(TUR) + ["🌐🤝 yeni coinler BTC ile birlikte", "🌐🧪 yeni coinler 24 saat", "🔥 fonlama yüksekken yükselen"]
A = V[V.lab.isin(SIRA) & np.isfinite(V.mae) & np.isfinite(V.fnet_l)].copy().sort_values("t").reset_index(drop=True)
A["sig"] = A.sig.fillna(A.sig.median())
DON = (("2022-06→2023", (A.t >= P0) & (A.t < A24_)), ("2024+", A.t >= A24_), ("2026 (Eyl.)", A.t >= A26_))
SEC = A[(A.t >= P0) & (A.t < A24_)]
M99 = {lb: -SEC[SEC.lab == lb].mae.quantile(0.01) for lb in SIRA if (SEC.lab == lb).sum() >= 20}
LTUR = {lb: float(np.clip(np.floor(0.5 / max(m, 1e-3)), 1, 10)) for lb, m in M99.items()}
yaz("## Türe göre kaldıraç (yalnız 2022–23'ten: %99 derin düşüşün yarısına dayanacak kadar)\n```")
for lb, m in M99.items(): yaz(f"{lb:42s} %99 derin düşüş %{100*m:5.1f} → {LTUR[lb]:.0f}x")
yaz("```")
def simule(X, Lv, f=0.02, tavan=None, stop=None):
    # basit hesap: başlangıç sermayesi 1; her sinyale f teminat (saat tavanı varsa aynı saatteki n sinyal min(f, tavan/n)); açık teminat ≤ 1 + gerçekleşen kâr
    tn = X.t.values.astype("datetime64[ns]").astype(np.int64); en = tn + X.H.values.astype(np.int64) * 3_600_000_000_000
    fn, ma = X.fnet_l.values, X.mae.values; WK = 7 * 86400 * 10**9
    eq, tepe, mdd, liq, n, atla, ac, kullan, hafta, i, N = 1.0, 1.0, 0.0, 0, 0, 0, [], 0.0, {}, 0, len(tn)
    while i < N:
        j = i
        while j < N and tn[j] == tn[i]: j += 1
        while ac and ac[0][0] <= tn[i]:
            te, _, m, p_ = heapq.heappop(ac); eq += p_; kullan -= m; tepe = max(tepe, eq); mdd = max(mdd, (tepe - eq) / tepe); hafta[te // WK] = hafta.get(te // WK, 0) + p_
        per = f if tavan is None else min(f, tavan / (j - i))
        for q in range(i, j):
            L_ = Lv[q]
            if kullan + per > eq or eq <= 0: atla += 1; continue
            if stop is not None and ma[q] <= -stop * (1 / L_ - 0.005): p_ = -per * stop - per * L_ * 0.0006      # stop likidasyondan ÖNCE çalışır
            elif ma[q] <= -(1 / L_ - 0.005): p_ = -per; liq += 1
            else: p_ = per * L_ * fn[q]
            heapq.heappush(ac, (en[q], q, per, p_)); kullan += per; n += 1
        i = j
    while ac:
        te, _, m, p_ = heapq.heappop(ac); eq += p_; tepe = max(tepe, eq); mdd = max(mdd, (tepe - eq) / tepe); hafta[te // WK] = hafta.get(te // WK, 0) + p_
    return eq - 1, mdd, liq, n, atla, (min(hafta.values()) if hafta else np.nan)
DUZ = {"D0 sabit 3x (bugünkü öneri)": dict(lev=lambda X: np.full(len(X), 3.0))}
for L_ in (1, 2, 5, 10): DUZ[f"sabit {L_}x"] = dict(lev=lambda X, L_=L_: np.full(len(X), float(L_)))
for L_ in (3, 5): DUZ[f"sabit {L_}x + saat tavanı %10"] = dict(lev=lambda X, L_=L_: np.full(len(X), float(L_)), tavan=0.10)
for k in (4, 6, 8): DUZ[f"oynaklığa göre (k={k}) + saat tavanı"] = dict(lev=lambda X, k=k: np.clip(1 / (k * X.sig.values * np.sqrt(X.H.values) + 1e-9), 1, 10), tavan=0.10)
DUZ["türe göre + saat tavanı"] = dict(lev=lambda X: X.lab.map(LTUR).fillna(3.0).values.astype(float), tavan=0.10)
for L_ in (5, 10): DUZ[f"sabit {L_}x + likidasyon öncesi stop + saat tavanı"] = dict(lev=lambda X, L_=L_: np.full(len(X), float(L_)), tavan=0.10, stop=0.7)
yaz("\n## Düzenler — her sinyale başlangıç sermayesinin %2'si teminat\n_yıllık getiri (başlangıç sermayesine göre, bileşiksiz) · en büyük düşüş · oran = getiri / düşüş · likide işlem · en kötü hafta · alınan / atlanan sinyal_\n```")
SON = {}
for ad, kw in DUZ.items():
    yaz(ad)
    for dn, md in DON:
        X = A[md]; yil = max((X.t.max() - X.t.min()).days / 365.25, 0.1)
        kw2 = {k_: v_ for k_, v_ in kw.items() if k_ != 'lev'}; top, mdd, liq, n, atla, kh = simule(X, kw['lev'](X), **kw2); oran = (top / yil) / max(mdd, 1e-4); SON[(ad, dn)] = (top / yil, mdd, oran)
        yaz(f"   {dn:14s} yıllık {100*top/yil:+7.1f}% · en büyük düşüş %{100*mdd:5.1f} · oran {oran:6.1f} · likide {liq:4d} · en kötü hafta {100*kh:+6.1f}% · {n} / {atla}")
yaz("```")
aday = [ad for ad in DUZ if SON[(ad, "2022-06→2023")][1] <= 0.30]
sec = max(aday, key=lambda ad: SON[(ad, "2022-06→2023")][2]) if aday else None
gec = sec is not None and all(SON[(sec, dn)][2] > SON[("D0 sabit 3x (bugünkü öneri)", dn)][2] for dn in ("2024+", "2026 (Eyl.)"))
yaz("\n## Önceden yazılı karar\n" + (f"- 2022–23'te seçilen düzen: **{sec}** (oran {SON[(sec, '2022-06→2023')][2]:.1f}, en büyük düşüş %{100*SON[(sec, '2022-06→2023')][1]:.1f})\n"
    + f"- 2024+ ve 2026'da D0'dan (sabit 3x) iyi mi: {'✅ EVET → önerilir' if gec else '❌ hayır → bugünkü öneri (2–3x) kalır'}" if sec else "- Hiçbir düzen en büyük düşüş ≤ %30 şartını sağlamadı"))
yaz(f"\n_Süre: {time.time()-T0:.0f} sn · olay {len(A):,}_")
open("kaldirac_test_sonuc.md", "w").write("\n".join(L) + "\n")
