# merdiven.py — COINBASE PRİMİ MERDİVENİ: eşik basamak basamak yükselince isabet, işlem başı kâr, sinyal sayısı ve TOPLAM kâr nasıl değişiyor? (yalnız test; canlıya dokunmaz)
# Prim: coin'in KENDİ Coinbase primi (BTC sinyallerinde BTC'nin), z son 720 saat (canlıdaki). Basamak "z ≥ k": sinyal yalnız o anda prim z ≥ k ise alınır.
# A) Canlıda mesajı giden tüm AL sinyalleri (BTC 1/4/8 s + ⭐ + A · coin tek başına / 🤝 / 🔇 · 🧪 24 s · ⛓️ · 🧑) — basamaklar: hepsi, −2, −1 (bugünkü ⛔ sınırı), −0,5, 0 … 3.
# B) Tek başına 💵 (z ≥ k → AL), 49 coin, 4 / 8 / 24 saat tut — basamaklar 0 … 8.  Giriş sinyalden 1 saat sonra (prim_coin.py ile aynı), limit komisyon %0,02 × 2.
# Haftalık toplam kâr = her işleme aynı tutar konduğunda haftada toplanan getiri (% olarak, işlem başı netlerin toplamı / hafta).
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
E = pd.DataFrame(EV, columns=["aile", "sinyal", "canli", "H", "t", "r", "nm"]); E = E[(E.canli == "📨") & (pd.DatetimeIndex(E.t) >= P0)].reset_index(drop=True)
zc = np.full(len(E), np.nan)
for nm, g in E.groupby("nm"):
    if nm in RAW: zc[g.index.values] = RAW[nm].z.reindex(pd.DatetimeIndex(g.t).tz_convert("UTC").as_unit("ns")).values
E["z"] = zc; E["net"] = E.r - 2 * LMT; E = E[np.isfinite(E.z)].reset_index(drop=True); tt = pd.DatetimeIndex(E.t)
SONT = max(D.index[-1] for D in RAW.values()); HAF = {"22-06→23": (A24 - P0).days / 7, "2024+": (SONT - A24).days / 7, "2026": (SONT - A26).days / 7}
yaz(f"# 🪜 Coinbase primi merdiveni — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nVeri sonu {SONT:%Y-%m-%d} · {len(RAW)} coin · primi bilinen AL sinyali (2022-06+): {len(E):,} · " + " · ".join(f"{a} {n:,}" for a, n in E.aile.value_counts().items()) + "\n")
yaz("_hücre: isabet % · işlem başı net % · haftada işlem · haftalık toplam kâr %_  ·  ⬅ = bugünkü uygulama (⛔ z ≤ −1 olanlar alınmıyor)\n")
KM = [(-np.inf, "hepsi"), (-2, "z ≥ −2"), (-1, "z > −1 ⬅"), (-0.5, "z ≥ −0,5"), (0, "z ≥ 0"), (0.5, "z ≥ 0,5"), (1, "z ≥ 1"), (1.5, "z ≥ 1,5"), (2, "z ≥ 2"), (2.5, "z ≥ 2,5"), (3, "z ≥ 3")]
def hucre(x, hf):
    return f"%{100*(x.r>0).mean():.0f} · {100*x.net.mean():+.2f} · {len(x)/hf:.1f} · {100*x.net.sum()/hf:+.1f}" if len(x) >= 10 else (f"({len(x)})" if len(x) else "—")
def merdiven(G, baslik):
    gt = pd.DatetimeIndex(G.t); T = {}
    for k, kad in KM:
        m = (G.z.values > k) if kad.startswith("z > ") else (G.z.values >= k); T[kad] = {dn: hucre(G[m & fd(gt)], HAF[dn]) for dn, fd in DON}
    yaz(f"\n### {baslik}\n```\n" + pd.DataFrame(T).T.to_string() + "\n```")
yaz("## A) Model sinyalleri — prim eşiği yükseldikçe")
merdiven(E, "Tüm AL sinyalleri birlikte")
for aile in E.aile.value_counts().index: merdiven(E[E.aile == aile], aile)
# coin coin (2024+): isabet % (işlem)
yaz("\n### Coin coin — model sinyalleri, 2024+ · _isabet % · işlem başı net % (işlem)_")
P_ = {}
for nm, g in E[pd.DatetimeIndex(E.t) >= A24].groupby("nm"):
    P_[nm] = {kad: (lambda x: f"%{100*(x.r>0).mean():.0f} {100*x.net.mean():+.2f} ({len(x)})" if len(x) >= 10 else (f"({len(x)})" if len(x) else "—"))(g[(g.z.values > k) if kad.startswith("z > ") else (g.z.values >= k)]) for k, kad in KM}
yaz("```\n" + pd.DataFrame(P_).T.to_string() + "\n```")
# ---------------- B) tek başına 💵 ----------------
KS = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8]
yaz("\n## B) Tek başına 💵 (z ≥ k → AL), 49 coin birlikte")
YC = {(nm, H): RAW[nm].c.shift(-(1 + H)) / RAW[nm].c.shift(-1) - 1 for nm in RAW for H in (4, 8, 24)}
BS = {}
for H in (4, 8, 24):
    T = {}
    for k in KS:
        parts = []
        for nm, D in RAW.items():
            ev = D.index[events((D.z >= k).fillna(False).values, H)]; x = (YC[(nm, H)].reindex(ev) - 2 * LMT).dropna()
            parts.append(pd.DataFrame({"coin": nm, "net": x.values, "r": x.values + 2 * LMT}, index=x.index))
        X = pd.concat(parts).sort_index(); X = X[X.index >= P0]; BS[(H, k)] = X
        T[f"z ≥ {k:g}"] = {dn: hucre(X[fd(X.index)], HAF[dn]) for dn, fd in DON}
    yaz(f"\n### {H} saat tut\n```\n" + pd.DataFrame(T).T.to_string() + "\n```")
yaz("\n### Coin coin — tek başına 💵, 24 saat, 2024+ · _işlem başı net % (işlem)_ · sağda: 2026 aynı")
P_ = {}
for k in KS:
    X = BS[(24, k)]
    for dn, fd in DON[1:]:
        for nm, g in X[fd(X.index)].groupby("coin"): P_.setdefault((nm), {})[f"{dn} z≥{k:g}"] = f"{100*g.net.mean():+.2f} ({len(g)})" if len(g) >= 5 else (f"({len(g)})" if len(g) else "—")
cols = [f"2024+ z≥{k:g}" for k in KS] + [f"2026 z≥{k:g}" for k in (2, 3, 4, 5)]
yaz("```\n" + pd.DataFrame(P_).T.reindex(columns=cols).sort_index().to_string() + "\n```")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("merdiven_sonuc.md", "w").write("\n".join(L) + "\n")
