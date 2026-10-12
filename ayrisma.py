# ayrisma.py — BİNANCE'TE UZUN/KISA KALABALIK ↔ ABD (COINBASE) TERS TARAFTA (kullanıcı sorusu 12.10.2026; yalnız test).
# Binance: tüm hesapların uzun/kısa oranı (küçük yatırımcı kalabalığı) ve büyük hesapların pozisyon oranı — vadeli arşiv metrikleri, saatlik, son 30 güne göre z.
# ABD: coin'in kendi Coinbase primi z (Coinbase long/short yayınlamıyor; ABD'nin alım/satımı bununla ölçülür).
# Kurallar: R1 Binance kalabalık long (z ≥ 1,5) + ABD satıyor (prim z ≤ −1) → SAT · R2 Binance kalabalık short (z ≤ −1,5) + ABD alıyor (z ≥ 1) → AL · R3/R4 aynısı büyük hesaplarla.
# ÖNCEDEN YAZILI KARAR (sonuçlar görülmeden): TEK: süre (4/8/24 s) yalnız 2022–23'ten seçilir; üç dönemde ana set ölçütü (isabet ≥ %55,9 · %58,6 · %59,1 VE net ≥ +0,30 · +0,647 · +0,589; 30/30/10) → yeni sinyal.
#   FİLTRE: ✅ ana sinyallerde koşul varken ANA+ (isabet ≥ +2, net ≥ +0,10 üç dönemde → öne al) · ANA− (net < 0 üç dönemde → yedeğe indir).
#   PLASEBO: 30 ve 60 gün kaydırılmış; gerçek geçen sayısı plasebo ortalamasından ≥ 2 fazla olmalı YA DA plaseboda hiçbiri geçmemeli; plaseboda geçen kural eklenmez.
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
# ---------------- Binance vadeli metrikleri (uzun/kısa oranları) ----------------
import io, zipfile, requests
from concurrent.futures import ThreadPoolExecutor
VADS = {"SHIB": "1000SHIBUSDT", "PEPE": "1000PEPEUSDT", "FLOKI": "1000FLOKIUSDT", "BONK": "1000BONKUSDT"}
SS = requests.Session()
def gunm(arg):
    sym, g = arg
    for k in range(3):
        try:
            r = SS.get(f"https://data.binance.vision/data/futures/um/daily/metrics/{sym}/{sym}-metrics-{g}.zip", timeout=40)
            if r.status_code == 404: return None
            if r.status_code != 200: time.sleep(1 + k); continue
            z_ = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z_.open(z_.namelist()[0]))
            d["t"] = pd.to_datetime(d.create_time, utc=True).dt.ceil("h")
            return d.groupby("t")[["count_long_short_ratio", "sum_toptrader_long_short_ratio"]].last()
        except Exception: time.sleep(1 + k)
    return None
GUNLER = [d.strftime("%Y-%m-%d") for d in pd.date_range("2022-04-01", "2026-09-30", freq="D")]
COINS = sorted(set(nmv[ANA | YED | GON]) & set(RAW))
MET = {}
for nm in COINS:
    sym = VADS.get(nm, nm + "USDT")
    with ThreadPoolExecutor(24) as ex: parts = [p for p in ex.map(gunm, [(sym, g) for g in GUNLER]) if p is not None and len(p)]
    if parts:
        D = pd.concat(parts).sort_index(); D = D[~D.index.duplicated()]; D.index = pd.DatetimeIndex(D.index).as_unit("ns"); MET[nm] = D.reindex(pd.date_range(D.index.min(), D.index.max(), freq="1h"))
    print(nm, len(parts), f"{time.time()-T0:.0f} sn", flush=True)
def z720(s): return (s - s.rolling(720, min_periods=168).mean()) / (s.rolling(720, min_periods=168).std() + 1e-12)
KS = {}
for nm, D in MET.items():
    zk = z720(np.log(D.count_long_short_ratio)); zb = z720(np.log(D.sum_toptrader_long_short_ratio)); zp = RAW[nm].z.reindex(D.index)
    KS[nm] = pd.DataFrame({"R1 Binance KALABALIK long + ABD satıyor": (zk >= 1.5) & (zp <= -1), "R2 Binance KALABALIK short + ABD alıyor": (zk <= -1.5) & (zp >= 1),
                           "R3 Binance BÜYÜK hesaplar long + ABD satıyor": (zb >= 1.5) & (zp <= -1), "R4 Binance BÜYÜK hesaplar short + ABD alıyor": (zb <= -1.5) & (zp >= 1)}).fillna(False)
YON = {"R1": -1, "R2": 1, "R3": -1, "R4": 1}
yaz(f"# ⚖️ Binance uzun/kısa ↔ ABD (Coinbase primi) ayrışması — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nCoin: {len(MET)} ({', '.join(MET)}) · {time.time()-T0:.0f} sn\n")
DNS = (("2022-06→2023", P0, A24_), ("2024+", A24_, None), ("2026", A26_, None)); MINS = {"2022-06→2023": 30, "2024+": 30, "2026": 10}
BENS = {"2022-06→2023": (55.9, 0.30), "2024+": (58.6, 0.647), "2026": (59.1, 0.589)}
def tek(ka, H, kay=0):
    rows = []
    for nm, K in KS.items():
        o = OH.get(nm)
        if o is None: continue
        m = K[ka].shift(kay).fillna(False).reindex(o.index).fillna(False).values.astype(bool); n = len(o); m &= (np.arange(n) + H < n); ev = events(m, H)
        rows.append(pd.DataFrame({"t": o.index[ev], "net": YON[ka[:2]] * (o.close.values[ev + H] / o.close.values[ev] - 1) - 0.0004}))
    X = pd.concat(rows) if rows else pd.DataFrame(columns=["t", "net"]); X["ok"] = X.net > 0; return X
def olc(X):
    o = {}
    for dn, a, b in DNS:
        x = X[(X.t >= a) & ((X.t < b) if b is not None else True)]; hf = ((b or X.t.max()) - a).days / 7
        o[dn] = (len(x), len(x) / max(hf, 1), 100 * x.ok.mean() if len(x) else np.nan, 100 * x.net.mean() if len(x) else np.nan)
    return o
def yz(o): return " | ".join(f"{o[dn][1]:4.1f}/hf · %{o[dn][2]:4.1f} · {o[dn][3]:+.2f} ({o[dn][0]})" if o[dn][0] >= 5 else f"{o[dn][0]:4d} az" for dn, _, _ in DNS)
def tek_karar(kay=0, yazdir=False):
    gec = []
    for ka in KS[next(iter(KS))].columns:
        R = {H: olc(tek(ka, H, kay)) for H in (4, 8, 24)}
        Hs = max(R, key=lambda H: R[H]["2022-06→2023"][3] if np.isfinite(R[H]["2022-06→2023"][3]) else -9)
        if yazdir:
            for H in (4, 8, 24): yaz(f"{ka[:44]:44s} {'SAT' if YON[ka[:2]] < 0 else 'AL '} {H:>2} s{' ←' if H == Hs else '  '} {yz(R[H])}")
        if all(R[Hs][dn][0] >= MINS[dn] and R[Hs][dn][2] >= BENS[dn][0] and R[Hs][dn][3] >= BENS[dn][1] for dn in MINS): gec.append(f"TEK: {ka} ({Hs} s)")
    return gec
yaz("## 1) Tek başına sinyal (24 coin, tutma süresi yalnız 2022–23'ten seçilir ←)\n_haftada · isabet · işlem başı net % (sinyal) — 2022-06→2023 | 2024+ | 2026_\n```")
G1 = tek_karar(0, True); yaz("```")
def kos_ez(kay):
    K = {}
    for ka in KS[next(iter(KS))].columns:
        arr = np.zeros(len(Ez), bool)
        for nm, Kd in KS.items():
            m = nmv == nm
            if m.any(): arr[m] = Kd[ka].reindex(tz_[m] - pd.Timedelta(hours=kay)).fillna(False).values.astype(bool)
        K[ka] = arr
    return K
def ist(m): return {dn: (int((m & md).sum()), 100 * Ez.ok.values[m & md].mean() if (m & md).any() else np.nan, 100 * Ez.net.values[m & md].mean() if (m & md).any() else np.nan) for dn, md, _ in DN}
def yazi(o): return " | ".join(f"%{o[dn][1]:4.1f} · {o[dn][2]:+.2f} ({o[dn][0]})" if o[dn][0] >= 5 else f"{o[dn][0]:4d} az" for dn, _, _ in DN)
OANA = ist(ANA)
def filt(K, yazdir=False):
    gec = []
    for ka, c in K.items():
        oa = ist(ANA & c)
        if yazdir: yaz(f"{ka[:44]:44s} ✅ ana + koşul: {yazi(oa)}")
        if all(oa[dn][0] >= MINS[dn] for dn in MINS):
            if all(oa[dn][1] >= OANA[dn][1] + 2 and oa[dn][2] >= OANA[dn][2] + 0.10 for dn in MINS): gec.append(f"ANA+: {ka}")
            if all(oa[dn][2] < 0 for dn in MINS): gec.append(f"ANA−: {ka}")
    return gec
yaz("\n## 2) Canlı ✅ ana sinyallere etkisi\n```\n" + f"{'✅ ana (hepsi)':44s}               {yazi(OANA)}"); G2 = filt(kos_ez(0), True); yaz("```")
G0 = G1 + G2; PL = tek_karar(720) + tek_karar(1440) + filt(kos_ez(720)) + filt(kos_ez(1440))
yaz(f"\n**Gerçek veride geçen:** {len(G0)} · **plasebo (30 + 60 gün kaydırılmış):** {len(PL)}")
OK_ = len(G0) >= len(PL) / 2 + 2 or (len(G0) >= 1 and not PL)
yaz("\n## Önceden yazılı karar\n" + ("\n".join(f"- {'✅ KABUL' if OK_ and g not in PL else '❌ (plasebo)'} {g}" for g in G0) if G0 else "- Hiçbir kural geçmedi → eklenmez"))
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("ayrisma_sonuc.md", "w").write("\n".join(L) + "\n")
