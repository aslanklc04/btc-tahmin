# ana_esik.py — CANLIDAKİ ANA coin'lerde (14 coin + 10 coin'lik 🧪) coin'in KENDİ Coinbase primi eşiği: z ≥ 0 / 1 / 1,5 (ve hepsi, −1, 0,5, 2) — her sinyal ailesi için ayrı (yalnız test).
# ÖNCEDEN YAZILI KARAR (12.10.2026). Ana set ölçütü: 2022-06→2023 %55,9 · +0,30 (kullanıcı kararı) | 2024+ %58,6 · +0,647 | 2026 %59,1 · +0,589. En az 30 / 30 / 10 sinyal.
#  A) Bugün ✅ ana olan aileler (🤝 ortak, 🧪 24 s; eşik z ≥ 0):
#     • Eşiği YÜKSELT (t > 0): z ≥ t, üç dönemin hepsinde z ≥ 0'dan hem isabette hem nette yüksekse geçer. Birden çok geçerse en düşük t (en çok sinyal).
#       (t altında kalanlar silinmez, 🔸 yedek olarak gider.)
#     • Eşiği DÜŞÜR (hepsi / z ≥ −1 / −0,5): yalnız EKLENEN dilim (t ≤ z < 0) üç dönemde de ana set ölçütünü geçerse.
#  B) Bugün 🔸 yedek olan aileler (coin tek başına, 🔇 sessiz, BTC 1/4/8 s+⭐+A — BTC'nin primi): z ≥ t üç dönemde de ana set ölçütünü geçerse en düşük t ana olur.
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
yaz(f"# 🎯 Ana coin'lerde kendi prim eşiği (0 / 1 / 1,5) — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nOlay: {len(Ez):,} · 🧪 canlı coin'ler: {', '.join(sorted(CAN24))}\n"
    "_her satır: sinyal sayısı (haftada) · isabet · işlem başı net % (komisyon sonrası) · saat-olayı isabeti_\n")
nmv = Ez.nm.values; ail = Ez.aile.values
AIL = (("coin 🤝 ortak", "ana", ail == "coin 🤝 ortak"), ("🧪 24 saat", "ana", (ail == "🧪 24 saat") & np.isin(nmv, list(CAN24))),
       ("coin tek başına", "yedek", ail == "coin tek başına"), ("coin 🔇 sessiz", "yedek", ail == "coin 🔇 sessiz"), ("BTC 1/4/8 s + ⭐ + A", "yedek", ail == "BTC 1/4/8 s + ⭐ + A"))
ESIK = (None, -1, -0.5, 0, 0.5, 1, 1.5, 2)
def olc(m):
    out = {}
    for dn, md, hf in DN:
        x = Ez[m & md]
        if len(x) == 0: out[dn] = (0, 0, np.nan, np.nan, np.nan); continue
        e = x.groupby(pd.DatetimeIndex(x.t).floor("h")).net.mean(); out[dn] = (len(x), len(x) / hf, 100 * x.ok.mean(), 100 * x.net.mean(), 100 * (e > 0).mean())
    return out
MIN = {"2022-06→2023": 30, "2024+": 30, "2026": 10}
def yeter(o): return all(o[dn][0] >= MIN[dn] for dn in MIN)
def bench(o): return yeter(o) and all(o[dn][2] >= BEN[dn][0] and o[dn][3] >= BEN[dn][1] for dn in MIN)
def satir(et, o, isr=""): return f"{et:<11} " + " | ".join(f"{o[dn][0]:4d} ({o[dn][1]:4.1f}/hf) %{o[dn][2]:4.1f} {o[dn][3]:+.3f}" for dn, _, _ in DN) + f" {isr}"
KAR = []
for ad, durum, fm in AIL:
    yaz(f"## {ad} — bugün {'✅ ana (z ≥ 0)' if durum == 'ana' else '🔸 yedek'}\n```\n{'eşik':<11} " + " | ".join(f"{dn:^29}" for dn, _, _ in DN))
    R = {}
    for t in ESIK:
        m = fm & (np.isfinite(z) if t is None else (z >= t)); R[t] = olc(m)
        isr = ""
        if durum == "yedek": isr = "★ ana setten iyi" if bench(R[t]) else ""
        yaz(satir("hepsi" if t is None else f"z ≥ {t}", R[t], isr))
    gec, not_ = [], ""
    if durum == "ana":
        b0 = R[0]
        for t in (0.5, 1, 1.5, 2):
            if yeter(R[t]) and all(R[t][dn][2] > b0[dn][2] and R[t][dn][3] > b0[dn][3] for dn in MIN): gec.append(t)
        yaz("— dilimler (eşiği değiştirince yer değiştirenler) —")
        for a, b in ((-1, 0), (0, 0.5), (0, 1), (0, 1.5), (0.5, 1), (1, 1.5), (1.5, 99)):
            o = olc(fm & (z >= a) & (z < b)); yaz(satir(f"{a}≤z<{b if b < 99 else '∞'}", o, "★ ana setten iyi" if bench(o) else ""))
        dus = [t for t in (None, -1, -0.5) if bench(olc(fm & (z < 0) & (np.isfinite(z) if t is None else (z >= t))))]
        yaz("```")
        if gec: KAR.append(f"**{ad}:** eşiği yükseltmek geçti → **z ≥ {min(gec)}** (geçenler {gec}); z ≥ 0–{min(gec)} arası 🔸 yedeğe iner")
        elif dus: KAR.append(f"**{ad}:** eşiği düşürmek geçti → {'hepsi' if dus[0] is None else f'z ≥ {dus[0]}'}")
        else: KAR.append(f"**{ad}:** değişiklik yok — hiçbir eşik z ≥ 0'ı üç dönemde birden hem isabette hem kârda geçmedi")
    else:
        gec = [t for t in ESIK if t is not None and bench(R[t])]; yaz("```")
        KAR.append(f"**{ad}:** " + (f"**z ≥ {min(gec)}** ana setten iyi → ✅ ana olabilir (geçenler {gec})" if gec else "hiçbir eşik ana seti üç dönemde geçmedi → 🔸 yedekte kalır"))
yaz("\n## Önceden yazılı karar\n" + "\n".join(f"- {k}" for k in KAR))
open("ana_esik_sonuc.md", "w").write("\n".join(L) + "\n")
