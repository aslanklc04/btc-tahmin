# zit_aile.py — "ABD coin'i alıyor, BTC'yi satıyor" (coin kendi primi z > 0, BTC primi z ≤ 0): canlıdaki ana coin'lerde HER AİLE ayrı (yalnız test).
# secim4: bu durumda tüm coin sinyalleri %61 · %60 · %66, net +0,54 · +0,47 · +0,75. Canlıda 🤝 ve 🧪 zaten ana (coin z ≥ 0); 🪙 coin tek başına ve 🔇 sessiz ise yedek.
# ÖNCEDEN YAZILI KARAR (12.10.2026): 🪙 tek ve 🔇 için adaylar: coin z > 0 / ≥ 0,5 / ≥ 1  ×  BTC z ≤ 0 / −1 < BTC z ≤ 0 / BTC z ≤ −1.
#   Aday üç dönemin hepsinde ana set ölçütünü geçerse (isabet ≥ %55,9 · %58,6 · %59,1 VE net ≥ +0,30 · +0,647 · +0,589; ≥ 30 / 30 / 10 sinyal) bu durumda ✅ ana olur.
#   Birden çok geçerse 2024+'ta en çok sinyal veren. Haftalık blok %5 alt sınırı bilgi için.
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
CAN24 = {os.path.basename(p)[8:-11] for p in glob.glob(f"{CD}/model24_*USDT.pkl.gz")}
Ez["zB"] = RAW["BTC"].z.reindex(tz_).values; zB = Ez.zB.values; nmv = Ez.nm.values; ail = Ez.aile.values
ok_ = np.isfinite(zB) & (nmv != "BTC")
yaz(f"# 🔀 ABD coin'i alıyor, BTC'yi satıyor — aile bazında (canlı ana coin'ler) — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n"
    "_hücre: sinyal (haftada) · isabet · işlem başı net % (komisyon sonrası) · alt = haftalık blok %5 alt sınır · ★ = üç dönemde de ana setten iyi_\n")
MIN = {"2022-06→2023": 30, "2024+": 30, "2026": 10}
def olc(m):
    o, s = {}, []
    for dn, md, hf in DN:
        x = Ez[m & md]
        if len(x) < 5: o[dn] = (len(x), np.nan, np.nan); s.append(f"{len(x):4d} az"); continue
        lo = wboot(x.net.values, x.t.values, 400)[0]
        o[dn] = (len(x), 100 * x.ok.mean(), 100 * x.net.mean()); s.append(f"{len(x):4d} ({len(x)/hf:4.1f}/hf) %{o[dn][1]:4.1f} {o[dn][2]:+.3f} (alt {100*lo:+.2f})")
    gec = all(o[dn][0] >= MIN[dn] and o[dn][1] >= BEN[dn][0] and o[dn][2] >= BEN[dn][1] for dn in MIN)
    return gec, o, " | ".join(s)
AIL = (("🤝 BTC ile ortak (canlıda zaten ana)", ail == "coin 🤝 ortak"), ("🧪 24 saat (canlıda zaten ana)", (ail == "🧪 24 saat") & np.isin(nmv, list(CAN24))),
       ("🪙 coin tek başına (canlıda yedek)", ail == "coin tek başına"), ("🔇 BTC sessizken (canlıda yedek)", ail == "coin 🔇 sessiz"),
       ("🪙 + 🔇 birlikte", (ail == "coin tek başına") | (ail == "coin 🔇 sessiz")))
COIN = (("coin z > 0", z > 0), ("coin z ≥ 0,5", z >= 0.5), ("coin z ≥ 1", z >= 1))
BTCK = (("BTC z ≤ 0", zB <= 0), ("−1 < BTC z ≤ 0", (zB > -1) & (zB <= 0)), ("BTC z ≤ −1", zB <= -1))
yaz("```\n" + f"{'':38s}" + " | ".join(f"{dn:^40s}" for dn, _, _ in DN))
SEC = {}
for ad, fm in AIL:
    yaz(f"\n{ad}")
    _, _, s = olc(fm & ok_); yaz(f"  {'(her durum)':36s}{s}")
    for ca, cm in COIN:
        for ba, bm in BTCK:
            g, o, s = olc(fm & ok_ & cm & bm); yaz(f"  {ca + ' · ' + ba:34s}{'★ ' if g else '  '}{s}")
            if g and ("tek" in ad or "🔇" in ad) and "birlikte" not in ad: SEC.setdefault(ad, []).append((o["2024+"][0], ca, ba))
yaz("```\n## Önceden yazılı karar")
for ad in ("🪙 coin tek başına (canlıda yedek)", "🔇 BTC sessizken (canlıda yedek)"):
    if ad in SEC: n_, ca, ba = max(SEC[ad]); yaz(f"- **{ad.split(' (')[0]}:** geçti → **{ca} ve {ba}** iken ✅ ana olur (geçen adaylar: {len(SEC[ad])})")
    else: yaz(f"- **{ad.split(' (')[0]}:** hiçbir aday üç dönemde ana seti geçmedi → 🔸 yedekte kalır")
open("zit_aile_sonuc.md", "w").write("\n".join(L) + "\n")
