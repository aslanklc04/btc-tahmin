# secim4.py — (1) coin primi vs BTC primi: aynı/zıt yön ve fark büyüdükçe isabet · (2) SESSİZ GÜN OLMAYAN en kârlı sinyal seti (yalnız test; olaylar secim2.py ile aynı)
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
DOLGU = "🔻 dolgu: BTC kısa (z ≤ −1)"
D_ = RAW["BTC"]; ev_ = D_.index[events((D_.z <= -1).fillna(False).values, 24)]
E = pd.concat([E, pd.DataFrame({"aile": DOLGU, "sinyal": DOLGU, "canli": "📨", "H": 24, "t": pd.DatetimeIndex(ev_).as_unit("ns"), "r": np.nan, "nm": "BTC", "z": D_.z.reindex(ev_).values, "yon": -1})], ignore_index=True)
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
# ======================= ANALİZ =======================
Ez["zB"] = RAW["BTC"].z.reindex(tz_).values; Ez["fark"] = Ez.z - Ez.zB
dol = (Ez.aile == DOLGU).values; COINA = ["coin tek başına", "coin 🤝 ortak", "coin 🔇 sessiz", "🧪 24 saat"]
coin = Ez.aile.isin(COINA).values & (Ez.nm != "BTC").values & np.isfinite(Ez.zB.values)
DN = (("2022-06→2023", (tz_ >= P0) & (tz_ < A24_), (A24_ - P0).days / 7), ("2024+", tz_ >= A24_, HAF["2024+"]), ("2026", tz_ >= A26_, HAF["2026"]))
def oz(x, hf, alt=True):
    if len(x) < 5: return f"{len(x)/hf:5.1f}/hf · az örnek"
    lo = wboot(x.net.values, x.t.values, 400)[0] if alt else np.nan
    return f"{len(x)/hf:5.1f}/hf · %{100*x.ok.mean():.1f} · {100*x.net.mean():+.3f}" + (f" (alt {100*lo:+.2f})" if alt else "")
yaz(f"# 🔀 Coin primi vs BTC primi + sessiz günü olmayan sinyal seti — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}")
yaz("_Coin sinyalleri: 🤝 BTC ile ortak · 🔇 BTC sessizken · coin tek başına · 🧪 24 saat (BTC hariç). Hücre: haftada · isabet · işlem başı net % (komisyon sonrası) · alt = haftalık blok %5 alt sınır_\n")
# (1) aynı / zıt yön
zo, zb_ = Ez.z.values, Ez.zB.values
DURUM = (("ikisi de alıyor (coin z>0, BTC z>0)", (zo > 0) & (zb_ > 0)), ("ABD coin'i alıyor, BTC'yi satıyor (coin z>0, BTC z≤0)", (zo > 0) & (zb_ <= 0)),
         ("ABD coin'i satıyor, BTC'yi alıyor (coin z≤0, BTC z>0)", (zo <= 0) & (zb_ > 0)), ("ikisi de satıyor (coin z≤0, BTC z≤0)", (zo <= 0) & (zb_ <= 0)))
yaz("## 1) Coin ve BTC primi aynı yönde mi, zıt yönde mi?\n```")
for ad, m in DURUM: yaz(f"{ad}\n   " + "\n   ".join(f"{dn:13s} {oz(Ez[coin & m & md], hf)}" for dn, md, hf in DN))
yaz("```\n**Güçlü haller** (z ≥ 1 alıyor / z ≤ −1 satıyor):\n```")
for ad, m in (("coin güçlü alınıyor, BTC güçlü satılıyor (coin ≥1, BTC ≤−1)", (zo >= 1) & (zb_ <= -1)), ("ikisi de güçlü alınıyor (≥1, ≥1)", (zo >= 1) & (zb_ >= 1)),
              ("coin güçlü satılıyor, BTC güçlü alınıyor (≤−1, ≥1)", (zo <= -1) & (zb_ >= 1)), ("ikisi de güçlü satılıyor (≤−1, ≤−1)", (zo <= -1) & (zb_ <= -1))):
    yaz(f"{ad}\n   " + "\n   ".join(f"{dn:13s} {oz(Ez[coin & m & md], hf)}" for dn, md, hf in DN))
yaz("```")
# (2) fark büyüdükçe
fk = Ez.fark.values; BIN = [(-99, -2), (-2, -1), (-1, 0), (0, 1), (1, 2), (2, 99)]
yaz("\n## 2) Coin primi BTC priminden ne kadar yüksek? (fark = coin z − BTC z)\n```")
for alt_ad, mm in (("tüm coin sinyalleri", coin), ("yalnız coin z ≥ 0 olanlar", coin & (zo >= 0)), ("yalnız BTC z ≤ −1 iken (ABD BTC satıyor)", coin & (zb_ <= -1))):
    yaz(f"[{alt_ad}]")
    for a, b in BIN:
        m = mm & (fk > a) & (fk <= b); yaz(f"  fark {('≤ ' + str(b)) if a == -99 else ('> ' + str(a)) if b == 99 else f'{a}…{b}':8s} " + " | ".join(f"{dn}: {oz(Ez[m & md], hf, False)}" for dn, md, hf in DN))
yaz("```")
# (3) sessiz gün olmayan setler
KEEP = Ez.aile.isin(["💵 ABD alıyor (tek başına)", "🔻 BTC kısa", "⛓️ ETH", "🧑 küçük yatırımcı"]).values
nb = ~btc & ~tek & ~dol
BASE = {"R5 (BTC ve coin-tek yok, coin z ≥ 0)": (nb & (z >= 0)) | KEEP,
        "S1 (R5 + fark ≥ 1 ve coin z > −1)": (nb & ((z >= 0) | ((fk >= 1) & (z > -1)))) | KEEP,
        "S2 (fark ≥ 0,5 ve coin z > −1)": (nb & (fk >= 0.5) & (z > -1)) | KEEP}
POOL = {"dolgu yok": None, "F1 dolgu: R4 (BTC/coin-tek yok, ⛔ hariç)": nb & (z > -1), "F2 dolgu: R0 (⛔ hariç hepsi)": ~dol & (z > -1),
        "F3 dolgu: R4 + ABD satarken BTC kısa": (nb & (z > -1)) | dol}
R0m = (~dol & (z > -1)) | KEEP
ORD = np.argsort(tz_.values, kind="stable"); TT = tz_.values[ORD]
def sim(base, pool, gap=np.timedelta64(24, "h")):
    out = np.zeros(len(Ez), np.int8); son = np.datetime64("1970-01-01T00:00", "ns"); b_, p_ = base[ORD], (pool[ORD] if pool is not None else np.zeros(len(ORD), bool))
    for j, i in enumerate(ORD):
        if b_[j]: out[i] = 1; son = TT[j]
        elif p_[j] and TT[j] - son >= gap: out[i] = 2; son = TT[j]
    return out
def gun(sec, md, bas, bit):
    tt = (tz_[(sec > 0) & md] + pd.Timedelta(hours=3)).floor("D").tz_convert(None); gunler = pd.date_range(bas, bit, freq="D")
    sess = (~gunler.isin(tt)).mean(); t_ = np.sort(tz_[(sec > 0) & md].values); bos = np.diff(t_).max() / np.timedelta64(1, "h") if len(t_) > 1 else np.nan
    return sess, bos
GB = {"2022-06→2023": (P0.tz_convert(None), A24_.tz_convert(None) - pd.Timedelta(days=1)), "2024+": (A24_.tz_convert(None), SONT.tz_convert(None).floor("D") - pd.Timedelta(days=1)),
      "2026": (A26_.tz_convert(None), SONT.tz_convert(None).floor("D") - pd.Timedelta(days=1))}
yaz("\n## 3) Her gün sinyal: dolgu kuralları (son 24 saatte hiç sinyal gitmediyse bir sonraki 'dolgu' sinyali gönderilir)\n"
    "_hücre: haftada · isabet · işlem başı net % · haftalık toplam % · sessiz gün % · en uzun sessizlik (saat) · dolgu sinyallerinin kendi net %'si_\n```")
ST, SEC = {}, {}
for dn, md, hf in DN:
    x = Ez[R0m & md]; s, b = gun(R0m.astype(int), md, *GB[dn]); ST[("R0 bugün", dn)] = (len(x) / hf, 100 * x.ok.mean(), 100 * x.net.mean(), s, b)
yaz("R0 bugün (⛔ hariç hepsi): " + " | ".join(f"{dn}: {ST[('R0 bugün', dn)][0]:.0f}/hf · %{ST[('R0 bugün', dn)][1]:.1f} · {ST[('R0 bugün', dn)][2]:+.3f} · sessiz gün %{100*ST[('R0 bugün', dn)][3]:.0f} · en uzun {ST[('R0 bugün', dn)][4]:.0f} s" for dn, _, _ in DN))
for ba, bm in BASE.items():
    for pa, pm in POOL.items():
        ad = f"{ba} + {pa}"; sec = sim(bm, pm); SEC[ad] = sec; parca = []
        for dn, md, hf in DN:
            x = Ez[(sec > 0) & md]; xd = Ez[(sec == 2) & md]; s, b = gun(sec, md, *GB[dn])
            ST[(ad, dn)] = (len(x) / hf, 100 * x.ok.mean(), 100 * x.net.mean(), s, b)
            parca.append(f"{dn}: {len(x)/hf:4.0f}/hf · %{100*x.ok.mean():.1f} · {100*x.net.mean():+.3f} · top {100*x.net.sum()/hf:+.1f} · sessiz %{100*s:.1f} · en uzun {b:.0f} s · dolgu {len(xd)/hf:.1f}/hf {100*xd.net.mean():+.2f}")
        yaz(f"{ad}\n   " + "\n   ".join(parca))
yaz("```")
# ÖNCEDEN YAZILI SEÇİM: 2024+ sessiz gün ≤ %2 ve haftada 35–80 olanlardan 2022-06→2023 işlem başı neti en yüksek olan.
# KARAR: 2024+ ve 2026'da net ≥ 1,5 × R0 ve isabet ≥ R0 ve 2026 sessiz gün ≤ %2 → canlıya aday.
uy = [a for a in SEC if ST[(a, "2024+")][3] <= 0.02 and 35 <= ST[(a, "2024+")][0] <= 80]
if not uy: yaz("\nKoşulları (sessiz gün ≤ %2, haftada 35–80) sağlayan aday yok")
else:
    sec = max(uy, key=lambda a: ST[(a, "2022-06→2023")][2]); r0 = "R0 bugün"
    ok = all(ST[(sec, d)][2] >= 1.5 * ST[(r0, d)][2] and ST[(sec, d)][1] >= ST[(r0, d)][1] for d in ("2024+", "2026")) and ST[(sec, "2026")][3] <= 0.02
    yaz(f"\nKoşulu sağlayanlar: {len(uy)} · **Seçimde (2022-06→2023) en kârlı: {sec}**\n" + " · ".join(f"{d}: isabet {ST[(sec, d)][1]:.1f} vs {ST[(r0, d)][1]:.1f} · net {ST[(sec, d)][2]:+.3f} vs {ST[(r0, d)][2]:+.3f} (×{ST[(sec, d)][2]/ST[(r0, d)][2]:.2f}) · sessiz gün %{100*ST[(sec, d)][3]:.1f}" for d in ("2024+", "2026"))
        + f"\n→ {'✅ CANLIYA ADAY' if ok else '❌ aday değil'}")
    x = Ez[(SEC[sec] > 0) & (tz_ >= A24_)]
    yaz("\nSeçilen setin içi (2024+, aile bazında):\n```\n" + "\n".join(f"{a:32s} {oz(g, HAF['2024+'], False)}" for a, g in x.groupby(np.where(SEC[sec][(SEC[sec] > 0) & (tz_ >= A24_)] == 2, "DOLGU · " + x.aile, x.aile))) + "\n```")
# (4) TAKVİM GÜNÜ DOLGUSU: o gün (TR) henüz hiç sinyal gitmediyse havuzdaki ilk sinyal gönderilir. Kademeli: 00–12 yalnız R4 · 12–18 R0'a kadar · 18–24 her şey (⛔, BTC ailesi, BTC kısa dahil)
HER = ~dol | dol; R4p = nb & (z > -1); R0p = ~dol & (z > -1)
def sim_gun(base, kademe):
    out = np.zeros(len(Ez), np.int8); gun_ = None; gitti = False; b_ = base[ORD]; saat = ((tz_ + pd.Timedelta(hours=3)).hour.values)[ORD]; gn = (tz_ + pd.Timedelta(hours=3)).floor("D").values[ORD]
    pk = [(p[ORD], h0) for p, h0 in kademe]
    for j, i in enumerate(ORD):
        if gn[j] != gun_: gun_ = gn[j]; gitti = False
        if b_[j]: out[i] = 1; gitti = True; continue
        if not gitti:
            for k_, (p_, h0) in enumerate(pk):
                if p_[j] and saat[j] >= h0: out[i] = 2 + k_; gitti = True; break
    return out
R5b = BASE["R5 (BTC ve coin-tek yok, coin z ≥ 0)"]
GUN = {"G1: gün boşsa R4": [(R4p, 0)], "G2: gün boşsa R0": [(R0p, 0)], "G3: gün boşsa her şey": [(HER, 0)],
       "G4: kademeli (R4 → 12:00'den sonra R0 → 18:00'den sonra her şey)": [(R4p, 0), (R0p, 12), (HER, 18)]}
yaz("\n## 4) Takvim günü dolgusu — o gün hiç sinyal gitmediyse (temel: R5)\n_hücre: haftada · isabet · net · sessiz gün % · dolgu: haftada / isabet / net_\n```")
for ga, kd in GUN.items():
    sec = sim_gun(R5b, kd); parca = []
    for dn, md, hf in DN:
        x = Ez[(sec > 0) & md]; xd = Ez[(sec >= 2) & md]; s_, b_ = gun(sec, md, *GB[dn])
        parca.append(f"{dn}: {len(x)/hf:4.0f}/hf · %{100*x.ok.mean():.1f} · {100*x.net.mean():+.3f} · sessiz %{100*s_:.1f} · en uzun {b_:.0f} s · dolgu {len(xd)/hf:.1f}/hf %{100*xd.ok.mean():.0f} {100*xd.net.mean():+.3f}")
    yaz(f"{ga}\n   " + "\n   ".join(parca))
    if ga.startswith("G4"):
        for k_, ad in enumerate(("R4 kademesi", "R0 kademesi", "her şey kademesi")):
            yaz(f"   ↳ {ad}: " + " | ".join(f"{dn}: {oz(Ez[(sec == 2 + k_) & md], hf, False)}" for dn, md, hf in DN))
yaz("```")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("secim4_sonuc.md", "w").write("\n".join(L) + "\n")
