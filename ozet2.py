# ozet_tum.py — TEK ÖLÇÜM: canlıdaki BÜTÜN sinyal kuralları (12.10.2026 itibarıyla, 🔀 dahil) aynı yöntemle, aynı üç dönemde (yalnız ölçüm, karar yok).
# Her tür: haftada sinyal · isabet · işlem başı net % (kapanış→kapanış, %0,04 maliyet) · 2024+ haftalık blok %5 alt sınır. Ayrıca ✅ ana toplamı, 🔸 yedek toplamı ve sinyalli gün oranı.
# Ana coin'ler: secim3 düzeneği (art1/art2/art3/sf-btc) · 🌐 geniş liste: genis.yml artifact'leri (ga/g-*) · 🔥: kosul-veri (işlem büyüklüğü) + KuCoin fonlaması.
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
import requests
CAN24 = {os.path.basename(p)[8:-11] for p in glob.glob(f"{CD}/model24_*USDT.pkl.gz")}
GENIS = {l.strip()[:-4] for l in open(f"{CD}/genis_liste.txt") if l.strip()}
Ez["zB"] = RAW["BTC"].z.reindex(tz_).values; zB = Ez.zB.values; nmv = Ez.nm.values; ail = Ez.aile.values
c24 = (ail == "🧪 24 saat") & np.isin(nmv, list(CAN24)); dis24 = (ail == "🧪 24 saat") & ~c24
TUR = {"🤝 BTC ile birlikte · ana coin'ler (kendi primi ≥ 0)": (ail == "coin 🤝 ortak") & (z >= 0),
       "🧪 24 saat · ana 10 coin (kendi primi ≥ 0)": c24 & (z >= 0),
       "🔇🔀 BTC sessiz + coin alınıyor + BTC hafif satılıyor": (ail == "coin 🔇 sessiz") & (z > 0) & np.isfinite(zB) & (zB > -1) & (zB <= 0),
       "💵 ABD güçlü alıyor (coin'in kendi primi)": ail == "💵 ABD alıyor (tek başına)",
       "⛓️ ETH arz/talep": ail == "⛓️ ETH",
       "🧑 küçük yatırımcı kaçıyor": ail == "🧑 küçük yatırımcı",
}
ANA0 = np.zeros(len(Ez), bool)
for v in TUR.values(): ANA0 |= v
key = pd.Series(nmv).astype(str) + "|" + pd.Series(tz_.floor("h").astype(str)); kset = set(key[((ail == "coin 🤝 ortak") | (ail == "coin 🔇 sessiz"))])
tek_dup = (ail == "coin tek başına") & key.isin(kset).values                                   # canlıda aynı coin-saat tek mesaj: 🤝 / 🔇 öncelikli
YED = ~ANA0 & ~dis24 & ~tek_dup & (z > -1) & (ail != "🔻 BTC kısa")
# 🔥 koşulları
HG = pd.date_range(pd.Timestamp("2022-05-01", tz="UTC"), tz_.max().ceil("h"), freq="1h")
def hz(s, lim=6): s = s.dropna(); s = s[~s.index.duplicated()].sort_index(); return s.reindex(HG, method="ffill", limit=lim)
def z720(s): return (s - s.rolling(720, min_periods=168).mean()) / (s.rolling(720, min_periods=168).std() + 1e-12)
KV = pd.read_pickle(f("**/kosul_veri.pkl")[0]); bn = KV["bn_BTC"]
kis = (z720(np.log(hz(bn.qv.rolling(24).sum() / bn.trades.rolling(24).sum()))) >= 2).values
ix = HG.get_indexer(tz_.floor("h")); K1 = np.where(ix >= 0, kis[np.clip(ix, 0, None)], False).astype(bool)
out, a = [], pd.Timestamp("2022-03-01", tz="UTC")
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
TERFI = YED & (K1 | K2); YED_G = YED & ~TERFI
# 🌐 geniş liste olayları (genis_esik.py ile aynı)
def bul(p):
    x = glob.glob(p, recursive=True); return x[0] if x else None
B = pd.read_pickle(bul("ga/**/disa_BTCUSDT.pkl")); B.index = pd.DatetimeIndex(B.index).tz_convert("UTC"); GV = []
for nm in sorted(GENIS):
    sym = nm + "USDT"; pz, d1, d24 = bul(f"ga/**/prim_{sym}.pkl"), bul(f"ga/**/disa_{sym}.pkl"), bul(f"ga/**/disa24_{sym}.pkl")
    if pz is None: continue
    Z = pd.read_pickle(pz).astype("float64"); Z.index = pd.DatetimeIndex(Z.index).tz_convert("UTC")
    if d1:
        X = pd.read_pickle(d1); X.index = pd.DatetimeIndex(X.index).tz_convert("UTC"); Bx = B.reindex(X.index); bu4 = Bx.u4.fillna(False).astype(bool).values
        any_ = (X.star.fillna(False).astype(bool) | X.u4.fillna(False).astype(bool) | X.acls.fillna(False).astype(bool)).values & X.y4.notna().values
        ev = events(any_ & bu4, 4); t = X.index[ev]; GV.append(pd.DataFrame({"nm": nm, "tur": "🌐🤝", "t": t, "r": np.exp(X.y4.values[ev]) - 1, "z": Z.z.reindex(t).values}))
    if d24:
        D = pd.read_pickle(d24).astype("float64"); D.index = pd.DatetimeIndex(D.index).tz_convert("UTC")
        D = D.reindex(pd.date_range(D.index[0], D.index[-1], freq="1h", tz="UTC")); c = D.close.ffill(limit=3).values; n = len(D)
        m = np.nan_to_num(((D.S24 > 0) & (D.C24 >= D.T10_24)).values).astype(bool) & D.T10_24.notna().values & (np.arange(n) + 25 < n)
        ev = events(m, 24); t = D.index[ev]; GV.append(pd.DataFrame({"nm": nm, "tur": "🌐🧪", "t": t, "r": c[ev + 24] / c[ev] - 1, "z": Z.z.reindex(t).values}))
G = pd.concat(GV, ignore_index=True); G = G[np.isfinite(G.r) & np.isfinite(G.z)].copy(); G["net"] = G.r - 0.0004; G["ok"] = G.net > 0
G = G[((G.tur == "🌐🤝") & (G.z >= 2)) | ((G.tur == "🌐🧪") & (G.z >= 1.5))]; G["t"] = pd.DatetimeIndex(G.t).tz_convert("UTC").as_unit("ns")
# ---------------- öneri: yedeklerden kendi primi ≥ 0 olanlar ana, kalanı gönderilmez ----------------
HF = {"2022-06→2023": (A24_ - P0).days / 7, "2024+": HAF["2024+"], "2026": HAF["2026"]}
def donem(t):
    t = pd.DatetimeIndex(t); return {"2022-06→2023": (t >= P0) & (t < A24_), "2024+": t >= A24_, "2026": t >= A26_}
def satir(x):
    D = donem(x.t); return " | ".join(f"{len(x[D[dn]])/HF[dn]:5.1f}/hf · %{100*x[D[dn]].ok.mean():4.1f} · {100*x[D[dn]].net.mean():+.2f}" for dn in HF)
def gun(x, dn):
    bas = A24_ if dn == "2024+" else A26_; g = pd.date_range(bas.tz_convert(DISPLAY_TZ).normalize(), tz_.max().tz_convert(DISPLAY_TZ).normalize(), freq="D")
    s_ = set(pd.DatetimeIndex(x.t).tz_convert(DISPLAY_TZ).normalize()); return 100 * sum(d_ in s_ for d_ in g) / len(g)
X0 = Ez[["t", "net", "ok", "nm"]].copy(); GG = G[["t", "net", "ok", "nm"]]
SIMDI_ANA = pd.concat([X0[ANA0 | (YED & K2)], GG]); SIMDI_YED = X0[YED & ~K2]
YP = YED & (z >= 0)
YENI_ANA = pd.concat([X0[ANA0 | YP], GG]); KESILEN = X0[YED & ~YP]
yaz("# 🔁 Öneri: yedeklerden coin'in kendi primi ≥ 0 olanlar ✅ ana, primi olmayanlar gönderilmez\n_haftada · isabet · işlem başı net % — 2022-06→2023 | 2024+ | 2026_\n```")
yaz(f"{'ŞİMDİ ✅ ana':44s}{satir(SIMDI_ANA)}")
yaz(f"{'ŞİMDİ 🔸 yedek':44s}{satir(SIMDI_YED)}")
yaz(f"{'ÖNERİ ✅ ana (ana + primli yedekler)':44s}{satir(YENI_ANA)}")
yaz(f"{'  └ ana olacak yedekler (prim ≥ 0)':44s}{satir(X0[YP])}")
for ad, m in (("     🔇 BTC sessiz", ail == "coin 🔇 sessiz"), ("     🪙 coin tek başına", ail == "coin tek başına"), ("     ₿ BTC ⭐ / A / 1-4-8 saat", ail == "BTC 1/4/8 s + ⭐ + A")):
    yaz(f"{ad:44s}{satir(X0[YP & m])}")
yaz(f"{'ÖNERİ ile gönderilmeyecek yedekler (prim < 0)':44s}{satir(KESILEN)}")
yaz("```")
for dn in ("2024+", "2026"):
    yaz(f"- {dn}: sinyalli gün — şimdi ✅ ana %{gun(SIMDI_ANA, dn):.0f} (yedekle %{gun(pd.concat([SIMDI_ANA, SIMDI_YED]), dn):.0f}) · öneri ✅ ana %{gun(YENI_ANA, dn):.0f}")
open("ozet2_sonuc.md", "w").write("\n".join(L) + "\n")
