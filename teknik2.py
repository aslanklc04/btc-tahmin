# teknik2.py — KENDİ TÜRETTİĞİM YENİ TEKNİKLER (yalnız test, 12.10.2026). Daha önce denenmemiş, canlıda Binance spot + Coinbase verisiyle hesaplanabilen 22 koşul.
# Canlı düzen (12.10.2026): ✅ ana (🤝 · 🧪 · 🔀 · 💵 · ⛓️ · 🧑 + 🚀 momentum terfisi) · 🔸 yedek (coin'in kendi primi ≥ 0 olan 🔇 / 🪙) · gönderilmeyenler.
# Koşullar (sinyal anında, yalnız geçmiş veriyle):
#   N1 MODELİN SON KARNESİ: a) son 7 günde sonuçlanan ✅ ana sinyallerin isabeti ≥ %65 (sistem formda) · b) ≤ %45 (sistem kötü gidiyor) [en az 15 sonuç]
#                           c) bu coin'in son 3 ✅ ana sinyali üçü de kazandı · d) üçü de kaybetti
#   N2 MUM ŞEKLİ (son 4 saat tek mum): a) uzun ALT fitil (aralığın ≥ yarısı: alıcı dipten topladı) · b) uzun ÜST fitil (yukarıda satıcı var) — mumun boyu en az 4 saatlik normal oynaklık kadar
#   N3 COİN'İN KENDİ HACMİ (24 s, son 30 güne göre): a) patlama z ≥ 2 · b) ilgisiz z ≤ −1
#   N4 30 GÜNLÜK ARALIK: a) 30 günlük zirvenin %1 yakınında (kırılım) · b) 30 günlük dibin %3 yakınında (destek)
#   N5 GİZLİ TOPLAMA / DAĞITIM: a) fiyat 24 s düşmüş ama piyasa alıcı payı yüksek (z ≥ 1) · b) fiyat 24 s yükselmiş ama alıcı payı düşük (z ≤ −1)
#   N6 ABD ALIMININ SÜREKLİLİĞİ: a) coin primi son 24 saatin ≥ %90'ında pozitif ve şimdi pozitif · b) şimdi pozitif ama son 24 saatin ≤ %25'inde pozitif (yeni döndü)
#   N7 BTC ÖNCÜLÜĞÜ (2 s): a) BTC fırladı (z ≥ 1,5), coin henüz takip etmedi (z ≤ 0,5) · b) coin fırladı, BTC yerinde (coin'in kendi haberi)
#   N8 YUVARLAK SAYI: a) fiyat bir yuvarlak sayının (60.000 · 3 · 0,5 gibi) %1 altında (direnç) · b) %1 üstünde (yeni geçti, destek)
#   N9 BTC'DEN KOPUŞ (72 s korelasyon, BTC hariç): a) ≤ 0,3 coin kendi yolunda · b) ≥ 0,85 BTC'ye kilitli
#   N10 ABD ALIMININ GENİŞLİĞİ (prim verisi olan ~50 coin): a) coin'lerin ≥ %70'inde Coinbase primi pozitif · b) ≤ %30'unda
#   N11 BTC MODELİ: a) BTC 4 saatlik model güçlü AŞAĞI diyor · b) BTC 24 saatlik model yukarı diyor
# ÖNCEDEN YAZILI KARAR (12.10.2026, sonuçlar görülmeden; teknik_tara.py ile aynı kurallar). Dönemler 2022-06→2023 · 2024+ · 2026; en az 30 / 30 / 10 sinyal.
#   ANA+ : koşullu ✅ ana sinyaller üç dönemde de ana ortalamasından isabette ≥ +2 puan VE nette ≥ +0,10 → mesajda öne alınır (öncelik).
#   ANA− : koşullu ✅ ana sinyaller üç dönemde de net < 0 → yedeğe iner.
#   YED+ / GÖN+ : koşullu yedekler / gönderilmeyenler üç dönemde de ana set ölçütünü geçerse (isabet ≥ %55,9 · %58,6 · %59,1 VE net ≥ +0,30 · +0,647 · +0,589) → ✅ ana.
#   PLASEBO: aynı koşullar 30 ve 60 gün kaydırılmış zamanla da denenir; gerçek geçen sayısı plasebo ortalamasından en az 2 fazla değilse hiçbir bulgu canlıya alınmaz.
#   Ayrıca geçen her kural tek tek: aynı kural iki plasebo kaydırmasının hiçbirinde geçmemiş olmalı.
import os, glob, gzip, json, pickle, time, requests, numpy as np, pandas as pd
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
# ---------------- saatlik spot mum (alıcı hacmi dahil; canlıdaki veri kaynağı: data-api.binance.vision) ----------------
from concurrent.futures import ThreadPoolExecutor
COINS = sorted(set(E.nm) | {"BTC"})
def kline(sym):
    rows, cur, end = [], int(pd.Timestamp("2022-02-01", tz="UTC").timestamp() * 1000), time.time() * 1000
    while cur < end:
        dt = None
        for k in range(6):
            try: r = requests.get("https://data-api.binance.vision/api/v3/klines", params=dict(symbol=sym, interval="1h", startTime=cur, limit=1000), timeout=20); r.raise_for_status(); dt = r.json(); break
            except Exception: time.sleep(2 + 2 * k)
        if not dt: break
        rows += dt; cur = dt[-1][0] + 3_600_000
        if len(dt) < 1000: break
    d = pd.DataFrame([x[:11] for x in rows], columns=["t", "o", "h", "l", "c", "v", "ct", "qv", "n", "tbv", "tbq"]).astype(float)
    d.index = pd.DatetimeIndex(pd.to_datetime(d.t, unit="ms", utc=True) + pd.Timedelta(hours=1)).as_unit("ns"); return d[~d.index.duplicated()].sort_index()
def ohlc(nm):
    try:
        d = kline(nm + "USDT"); return nm, (d if len(d) > 2000 else None)
    except Exception as e: print(nm, "mum alınamadı", e); return nm, None
with ThreadPoolExecutor(8) as ex: SP = {k: v for k, v in ex.map(ohlc, COINS) if v is not None}
OH = {nm: pd.DataFrame({"high": d.h, "low": d.l, "close": d.c}) for nm, d in SP.items()}
SIG1 = {nm: np.log(o.close).diff().rolling(720, min_periods=168).std() for nm, o in OH.items()}
print(f"mum: {len(SP)}/{len(COINS)} coin · {time.time()-T0:.0f} sn", flush=True)

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
E24n = {}
for s_, X in E24.items():
    X = X.copy(); X.index = pd.DatetimeIndex(X.index).tz_convert("UTC").as_unit("ns"); E24n[s_[:-4]] = X
# ---------------- 🚀 momentum terfisi (canlıda 12.10.2026'dan beri): gönderilmeyen + son 24 s z ≥ 2 → ✅ ana ----------------
RZ = np.full(len(Ez), np.nan)
for nm, o in OH.items():
    m = nmv == nm
    if m.any(): lr = np.log(o.close); sg = lr.diff().rolling(720, min_periods=168).std(); RZ[m] = ((lr - lr.shift(24)) / (sg * np.sqrt(24))).reindex(tz_[m]).values
MOM = GON & (RZ >= 2); ANA = ANA | MOM; GON = GON & ~MOM
yaz(f"# 🧪 Kendi türettiğim yeni teknikler (22 koşul) — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n"
    f"Olay: ✅ ana {ANA.sum():,} (🚀 terfi {MOM.sum():,} dahil) · 🔸 yedek {YED.sum():,} · gönderilmeyen {GON.sum():,} · mum verisi {len(SP)} coin\n")
# ---------------- koşul serileri (coin başına, yalnız geçmiş) ----------------
def utc(ix):
    ix = pd.DatetimeIndex(ix); return (ix.tz_localize("UTC") if ix.tz is None else ix.tz_convert("UTC")).as_unit("ns")
def z720(s): return (s - s.rolling(720, min_periods=168).mean()) / (s.rolling(720, min_periods=168).std() + 1e-12)
B_ = SP["BTC"]; lrB = np.log(B_.c); r1B = lrB.diff(); sgB = r1B.rolling(720, min_periods=168).std(); rb2 = (lrB - lrB.shift(2)) / (sgB * np.sqrt(2))
PC = {}
for nm, d in SP.items():
    lr = np.log(d.c); r1 = lr.diff(); sg = r1.rolling(720, min_periods=168).std()
    H4, L4, O4 = d.h.rolling(4).max(), d.l.rolling(4).min(), d.o.shift(3); R = H4 - L4; R_ok = (R / d.c) >= 2 * sg
    alt = ((np.minimum(O4, d.c) - L4) / R.replace(0, np.nan)); ust = ((H4 - np.maximum(O4, d.c)) / R.replace(0, np.nan))
    q24 = d.qv.rolling(24).sum(); vz = z720(np.log(q24.replace(0, np.nan))); tb = z720(d.tbq.rolling(24).sum() / q24.replace(0, np.nan)); r24 = lr.diff(24)
    hi, lo = d.h.rolling(720, min_periods=720).max(), d.l.rolling(720, min_periods=720).min()
    rc2 = (lr - lr.shift(2)) / (sg * np.sqrt(2)); rb2_ = rb2.reindex(d.index)
    kor = r1.rolling(72, min_periods=60).corr(r1B.reindex(d.index))
    p = d.c.values; u = 10.0 ** np.floor(np.log10(p)); yuk = np.ceil(p / u - 1e-9) * u; dus = np.floor(p / u + 1e-9) * u
    bt = nm == "BTC"
    PC[nm] = pd.DataFrame({
        "N2a": (alt >= 0.5) & R_ok, "N2b": (ust >= 0.5) & R_ok,
        "N3a": vz >= 2, "N3b": vz <= -1,
        "N4a": d.c >= 0.99 * hi, "N4b": d.c <= 1.03 * lo,
        "N5a": (r24 < 0) & (tb >= 1), "N5b": (r24 > 0) & (tb <= -1),
        "N7a": (rb2_ >= 1.5) & (rc2 <= 0.5) & (not bt), "N7b": (rc2 >= 1.5) & (rb2_ <= 0.5) & (not bt),
        "N8a": pd.Series(((yuk - p) / p > 0) & ((yuk - p) / p <= 0.01), index=d.index), "N8b": pd.Series(((p - dus) / p >= 0) & ((p - dus) / p <= 0.01), index=d.index),
        "N9a": (kor <= 0.3) & (not bt), "N9b": (kor >= 0.85) & (not bt)}, index=d.index).fillna(False).astype(bool)
for nm, v in RAW.items():
    zz = v.z; pos = (zz > 0).astype(float).where(zz.notna()); p24 = pos.rolling(24, min_periods=20).mean()
    PZ = pd.DataFrame({"N6a": (p24 >= 0.9) & (zz > 0), "N6b": (zz > 0) & (p24 <= 0.25)}).fillna(False)
    PC[nm] = PC[nm].join(PZ, how="left") if nm in PC else PZ
ZA = pd.DataFrame({k: v.z for k, v in RAW.items()}); say_ = ZA.notna().sum(axis=1); BR = ((ZA > 0).sum(axis=1) / say_).where(say_ >= 10)
SFB.index = utc(SFB.index); B24 = E24n.get("BTC")
AD = {"N1a": "N1a son 7 günde ✅ ana isabeti ≥ %65 (sistem formda)", "N1b": "N1b son 7 günde ✅ ana isabeti ≤ %45 (sistem kötü)",
      "N1c": "N1c bu coin'in son 3 ✅ ana sinyali kazandı", "N1d": "N1d bu coin'in son 3 ✅ ana sinyali kaybetti",
      "N2a": "N2a son 4 s uzun ALT fitil (alıcı dipten topladı)", "N2b": "N2b son 4 s uzun ÜST fitil (yukarıda satıcı)",
      "N3a": "N3a coin hacmi patlamış (z ≥ 2)", "N3b": "N3b coin hacmi ilgisiz (z ≤ −1)",
      "N4a": "N4a 30 günlük zirveye %1 yakın (kırılım)", "N4b": "N4b 30 günlük dibe %3 yakın (destek)",
      "N5a": "N5a düşüşte alıcı ağır (gizli toplama)", "N5b": "N5b yükselişte satıcı ağır (gizli dağıtım)",
      "N6a": "N6a ABD 24 saattir aralıksız alıyor", "N6b": "N6b ABD alıma yeni döndü",
      "N7a": "N7a BTC fırladı, coin henüz takip etmedi", "N7b": "N7b coin fırladı, BTC yerinde",
      "N8a": "N8a yuvarlak sayının %1 altında (direnç)", "N8b": "N8b yuvarlak sayının %1 üstünde (destek)",
      "N9a": "N9a coin BTC'den kopuk (korelasyon ≤ 0,3)", "N9b": "N9b coin BTC'ye kilitli (korelasyon ≥ 0,85)",
      "N10a": "N10a ABD coin'lerin ≥ %70'ini alıyor", "N10b": "N10b ABD coin'lerin ≤ %30'unu alıyor",
      "N11a": "N11a BTC 4 s modeli güçlü AŞAĞI", "N11b": "N11b BTC 24 s modeli yukarı"}
# N1: karne (yalnız SONUÇLANMIŞ ✅ ana sinyaller: çıkış zamanı ≤ bakılan an)
EXIT = (tz_ + pd.to_timedelta(Ez.H.values.astype(int), unit="h")).asi8; OKv = Ez.ok.values.astype(float); ia = np.where(ANA)[0]
o_ = np.argsort(EXIT[ia]); EXS = EXIT[ia][o_]; CSO = np.concatenate([[0.0], np.cumsum(OKv[ia][o_])])
COIN_K = {}
for nm in np.unique(nmv):
    j = ia[nmv[ia] == nm]
    if len(j) >= 3: o2 = np.argsort(EXIT[j]); COIN_K[nm] = (EXIT[j][o2], np.concatenate([[0.0], np.cumsum(OKv[j][o2])]))
def kosullar(kay):
    tt = tz_ - pd.Timedelta(hours=kay); ti = tt.asi8; K = {}
    hi_ = np.searchsorted(EXS, ti, side="right"); lo_ = np.searchsorted(EXS, ti - 7 * 24 * 3600 * 10**9, side="right"); n_ = hi_ - lo_
    hr = np.where(n_ >= 15, (CSO[hi_] - CSO[lo_]) / np.maximum(n_, 1), np.nan)
    K["N1a"] = hr >= 0.65; K["N1b"] = hr <= 0.45
    s3 = np.full(len(Ez), np.nan)
    for nm, (ex_, cs_) in COIN_K.items():
        m = nmv == nm; h_ = np.searchsorted(ex_, ti[m], side="right"); s3[m] = np.where(h_ >= 3, (cs_[h_] - cs_[np.maximum(h_ - 3, 0)]) / 3, np.nan)
    K["N1c"] = s3 >= 0.999; K["N1d"] = s3 <= 0.001
    for c in ("N2a", "N2b", "N3a", "N3b", "N4a", "N4b", "N5a", "N5b", "N6a", "N6b", "N7a", "N7b", "N8a", "N8b", "N9a", "N9b"):
        v = np.zeros(len(Ez), bool)
        for nm, P in PC.items():
            if c not in P.columns: continue
            m = nmv == nm
            if m.any(): v[m] = P[c].reindex(tt[m]).fillna(False).values.astype(bool)
        K[c] = v
    br = BR.reindex(tt).values; K["N10a"] = br >= 0.7; K["N10b"] = br <= 0.3
    s4 = SFB.reindex(tt); K["N11a"] = ((s4.S4 < 0) & (s4.C4 >= s4.T304)).fillna(False).values.astype(bool)
    K["N11b"] = (B24.S24.reindex(tt) > 0).fillna(False).values.astype(bool) if B24 is not None else np.zeros(len(Ez), bool)
    return {AD[k]: np.asarray(v, bool) for k, v in K.items()}
DN = (("2022-06→2023", (tz_ >= P0) & (tz_ < A24_), (A24_ - P0).days / 7), ("2024+", tz_ >= A24_, HAF["2024+"]), ("2026", tz_ >= A26_, HAF["2026"]))
BEN = {"2022-06→2023": (55.9, 0.30), "2024+": (58.6, 0.647), "2026": (59.1, 0.589)}; MIN = {"2022-06→2023": 30, "2024+": 30, "2026": 10}
def ist(m):
    return {dn: (int((m & md).sum()), 100 * Ez.ok.values[m & md].mean() if (m & md).any() else np.nan, 100 * Ez.net.values[m & md].mean() if (m & md).any() else np.nan) for dn, md, _ in DN}
def yazi(o): return " | ".join(f"{o[dn][0]/hf:5.1f}/hf · %{o[dn][1]:4.1f} · {o[dn][2]:+.2f}" if o[dn][0] >= 5 else f"{o[dn][0]:5d} az    " for dn, _, hf in DN)
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
K0 = kosullar(0); print(f"koşullar hazır · {time.time()-T0:.0f} sn", flush=True)
yaz("_haftada sinyal · isabet · işlem başı net % (komisyon sonrası) — 2022-06→2023 | 2024+ | 2026_\n```")
yaz(f"{'✅ ANA (hepsi)':46s}{yazi(OANA)}\n{'🔸 YEDEK (hepsi)':46s}{yazi(ist(YED))}\n{'GÖNDERİLMEYEN (hepsi)':46s}{yazi(ist(GON))}")
for ad, c in K0.items():
    yaz(f"\n{ad}\n  {'✅ ana + koşul':44s}{yazi(ist(ANA & c))}\n  {'🔸 yedek + koşul':44s}{yazi(ist(YED & c))}\n  {'gönderilmeyen + koşul':44s}{yazi(ist(GON & c))}")
yaz("```")
G0 = kurallar(K0); GP1 = kurallar(kosullar(720)); GP2 = kurallar(kosullar(1440)); PS = set(GP1) | set(GP2)
yaz(f"\n**Gerçek veride geçen:** {len(G0)} · **plasebo:** 30 gün kaydırılmış {len(GP1)}, 60 gün kaydırılmış {len(GP2)}")
for gr, ad in G0: yaz(f"- {gr}: {ad}" + ("  _(plaseboda da geçti)_" if (gr, ad) in PS else ""))
if PS: yaz("Plaseboda geçenler: " + " · ".join(f"{gr} {ad.split(' ')[0]}" for gr, ad in sorted(PS)))
GENEL = len(G0) >= (len(GP1) + len(GP2)) / 2 + 2; KAB = [(gr, ad) for gr, ad in G0 if (gr, ad) not in PS] if GENEL else []
yaz("\n## Önceden yazılı karar")
yaz(f"- Genel plasebo kontrolü: gerçek {len(G0)} · plasebo ortalaması {(len(GP1) + len(GP2)) / 2:.1f} → " + ("✅ şanstan fazlası var" if GENEL else "❌ şanstan ayırt edilemiyor — hiçbir bulgu canlıya alınmaz"))
yaz("\n".join(f"- ✅ KABUL {gr}: **{ad}**" for gr, ad in KAB) if KAB else "- Kabul edilen kural yok")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("teknik2_sonuc.md", "w").write("\n".join(L) + "\n")
