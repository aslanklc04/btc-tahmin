# fon_gecikme.py — YÜKSEK FONLAMA koşulunu CANLIDA kullanmanın yolu: Binance vadeli API ABD sunucularından kapalı → (1) Binance arşivinin günlük dosyalarından GECİKMELİ fonlama, (2) ABD dışı borsaların anlık fonlaması (yalnız test)
# ÖNCEDEN YAZILI ADAYLAR (z: coin'in kendi Coinbase primi; ⛔ = z ≤ −1):
#   R0 bugün: ⛔ hariç hepsi · R1 hepsi, z ≥ 0,5 · R2 BTC saatlik/⭐/A ailesi yok, ⛔ hariç · R3 BTC ailesi yok, z ≥ 0 · R4 BTC ve coin-tek-başına yok, ⛔ hariç ·
#   R5 BTC ve coin-tek yok, z ≥ 0 · R6 hepsi, z ≥ 1 · R7 BTC ailesi yok, z ≥ 0,5.
# SEÇİM: 2024+ haftalık sayısı 30–60 olan adaylar içinden 2022-06→2023'te işlem başı neti en yüksek olan (sayı performans değildir; performans yalnız seçim döneminden).
# KARAR: seçilen 2024+'da R0'a göre isabet ≥ +3 puan ve net ≥ 1,5 kat · 2026'da isabet ve net R0'dan düşük değil → canlıya aday. Ayrıca tüm adaylar şeffaf tablo.
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
yaz(f"# 🎯 Haftada ~45 sinyal: isabet ve kâr için seçim — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nOlay: {len(E):,} · tip: {E.tip.nunique()} · {time.time()-T0:.0f} sn\n")
BTC_A, TEK_A = "BTC 1/4/8 s + ⭐ + A", "coin tek başına"
Ez = E[E.zb != "?"].copy(); tz_ = pd.DatetimeIndex(Ez.t); btc = (Ez.aile == BTC_A).values; tek = (Ez.aile == TEK_A).values; z = Ez.z.values
# ÖNCEDEN YAZILI (11.10.2026): secim5.py T2 ile aynı yükseltme şartı (yedek, ⛔ hariç): seçimde ve 2024+'da ≥ 30 sinyal, isabet ≥ %57, net ≥ +%0,35; 2024+ alt sınır > 0; 2026 (≥ 10) net > 0.
#   A anlık Binance fonlaması (secim5'teki — canlıda alınamıyor, karşılaştırma) · B aynı fonlama GECİKMELİ (günlük dosya gün d → d+1 08:00 UTC'den itibaren)
#   C prim endeksinden hesaplanan fonlama (canlıda data.binance.vision günlük premiumIndexKlines ile hesaplanabilir), aynı gecikmeyle → C geçerse canlıya alınır.
import io, zipfile, requests
from concurrent.futures import ThreadPoolExecutor
KEEP = Ez.aile.isin(["💵 ABD alıyor (tek başına)", "🔻 BTC kısa", "⛓️ ETH", "🧑 küçük yatırımcı"]).values
nb = ~btc & ~tek; ANA = (nb & (z >= 0)) | KEEP; ANA &= ~(Ez.aile == "coin 🔇 sessiz").values; YED = ~ANA & (z > -1)   # canlı düzen: 🔇 artık yedek
KV = pd.read_pickle(f("**/kosul_veri.pkl")[0]); fb = KV["fon_BTC"].sort_index()
def zip1(url):
    try:
        r = requests.get(url, timeout=30)
        if r.status_code != 200: return None
        zf = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(zf.open(zf.namelist()[0]), header=None)
        if not str(d.iloc[0, 0]).isdigit(): d = d.iloc[1:]
        return d.iloc[:, :5].astype(float)
    except Exception: return None
aylar = pd.date_range("2022-04-01", pd.Timestamp.now(tz="UTC").normalize() - pd.offsets.MonthBegin(1), freq="MS")
gunler = pd.date_range(pd.Timestamp.now(tz="UTC").normalize().replace(day=1), pd.Timestamp.now(tz="UTC").normalize() - pd.Timedelta(days=1), freq="D")
U = [f"https://data.binance.vision/data/futures/um/monthly/premiumIndexKlines/BTCUSDT/1h/BTCUSDT-1h-{a:%Y-%m}.zip" for a in aylar] + \
    [f"https://data.binance.vision/data/futures/um/daily/premiumIndexKlines/BTCUSDT/1h/BTCUSDT-1h-{g:%Y-%m-%d}.zip" for g in gunler]
with ThreadPoolExecutor(12) as ex: parts = [p for p in ex.map(zip1, U) if p is not None]
PI = pd.concat(parts); PI.index = pd.to_datetime(PI[0], unit="ms", utc=True) + pd.Timedelta(hours=1); PI = PI[~PI.index.duplicated()].sort_index()[4]
P8 = PI.rolling("8h").mean(); FP = (P8 + (0.0001 - P8).clip(-0.0005, 0.0005)); FP = FP[FP.index.hour % 8 == 0]
yaz(f"# 💸 Yüksek fonlama canlıda: gecikmeli ve hesaplanan fonlama — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nPrim endeksi: {len(PI):,} saat ({len(parts)} dosya, son {PI.index[-1]:%d.%m %H:%M}) · "
    f"hesaplanan ↔ gerçek fonlama ilişkisi: {FP.reindex(fb.index, method='nearest', tolerance=pd.Timedelta(hours=1)).corr(fb):+.3f}\n")
def zser(s): return (s - s.rolling(90, min_periods=30).mean()) / (s.rolling(90, min_periods=30).std() + 1e-12)
ZA, ZC_ = zser(fb), zser(FP.dropna())
t_ = tz_.floor("h"); kul = (t_ - pd.Timedelta(hours=8)).floor("D")                                 # gecikme: gün d'nin dosyası d+1 08:00 UTC'den sonra kullanılabilir
def asof(s, zaman): s = s.dropna(); i = s.index.searchsorted(zaman, side="right") - 1; return np.where(i >= 0, s.values[np.clip(i, 0, None)], np.nan)
KE = {"A anlık Binance fonlaması (canlıda yok)": asof(ZA, t_) >= 2, "B gecikmeli Binance fonlaması": asof(ZA, kul) >= 2, "C hesaplanan fonlama, gecikmeli (CANLIDA YAPILABİLİR)": asof(ZC_, kul) >= 2}
KE = {k: np.nan_to_num(v, nan=0).astype(bool) for k, v in KE.items()}
DN = (("2022-06→2023", (tz_ >= P0) & (tz_ < A24_)), ("2024+", tz_ >= A24_), ("2026", tz_ >= A26_))
def ist(m): x = Ez[m]; return len(x), (100 * x.ok.mean() if len(x) else np.nan), (100 * x.net.mean() if len(x) else np.nan)
yaz("_haftada değil toplam: sinyal · isabet · işlem başı net %_\n```")
for k, km in KE.items():
    S = [ist(YED & km & md) for _, md in DN]; mm = YED & km & DN[1][1]; lo = 100 * wboot(Ez.net.values[mm], Ez.t.values[mm], 400)[0] if mm.sum() >= 8 else np.nan
    (ns, hs, xs), (nd, hd, xd), (ny, hy, xy) = S; ok = ns >= 30 and nd >= 30 and hs >= 57 and xs >= 0.35 and hd >= 57 and xd >= 0.35 and lo > 0 and (ny < 10 or xy > 0)
    yaz(f"{k}\n   🔸 yedek (koşul var): " + " | ".join(f"{dn}: {s[0]} · %{s[1]:.1f} · {s[2]:+.3f}" for (dn, _), s in zip(DN, S)) + f" · alt {lo:+.2f} → {'✅ yedek → ana' if ok else '❌'}")
    yaz("   ✅ ana   (koşul var): " + " | ".join(f"{dn}: {ist(ANA & km & md)[0]} · %{ist(ANA & km & md)[1]:.1f} · {ist(ANA & km & md)[2]:+.3f}" for dn, md in DN))
yaz("```")
yaz("\n## ABD sunucusundan anlık fonlama erişimi (GitHub sunucusu ABD'de)\n```")
for ad, url in (("Binance vadeli (fapi)", "https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT"), ("Binance arşiv günlük prim endeksi (dün)", U[-1] if gunler.size else U[-1]),
                ("OKX", "https://www.okx.com/api/v5/public/funding-rate?instId=BTC-USDT-SWAP"), ("Bybit", "https://api.bybit.com/v5/market/tickers?category=linear&symbol=BTCUSDT"),
                ("Bitget", "https://api.bitget.com/api/v2/mix/market/current-fund-rate?symbol=BTCUSDT&productType=usdt-futures"), ("Gate", "https://api.gateio.ws/api/v4/futures/usdt/contracts/BTC_USDT"),
                ("MEXC", "https://contract.mexc.com/api/v1/contract/funding_rate/BTC_USDT"), ("KuCoin", "https://api-futures.kucoin.com/api/v1/funding-rate/XBTUSDTM/current"),
                ("Hyperliquid", "https://api.hyperliquid.xyz/info")):
    try:
        r = requests.post(url, json={"type": "metaAndAssetCtxs"}, timeout=15) if "hyperliquid" in url else requests.get(url, timeout=15)
        yaz(f"{ad:42s} HTTP {r.status_code} · {r.text[:90].replace(chr(10), ' ')}")
    except Exception as e: yaz(f"{ad:42s} hata {type(e).__name__}")
yaz("```")
open("fon_gecikme_sonuc.md", "w").write("\n".join(L) + "\n")
