# filtre_hepsi.py — İSABETİ ARTIRACAK EK FİLTRELER: canlıda mesajı giden AL sinyallerinde, sinyal anındaki piyasa durumu "kötü" iken isabet düşüyor mu? (yalnız test)
# Sinyal aileleri (prim_hepsi.py ile aynı kurulum): BTC 1 saat ↑ · BTC 4/8 saat ↑ + ⭐ + A · coin 🤝 ortak · coin 🔇 BTC sessizken · coin tek başına · 🧪 24 saat.
# Önceden sabit "KÖTÜ" koşullar (sinyal saatinde, yalnız geçmiş veriyle):
#   K1 coin 30 günlük ortalamanın (720 s EMA) altında · K2 BTC 720 s EMA altında · K3 coin son 24 saatte olağandışı yükselmiş (z ≥ 2, peşinden koşma)
#   K4 coin son 24 saatte olağandışı düşmüş (z ≤ −2) · K5 oynaklık patlaması (24 s oynaklık / 30 g ≥ 1,5) · K6 RSI14 ≥ 70 · K7 RSI14 ≤ 30
#   K8 vadeli fonlama 3 g ort. z ≥ 1,5 (kalabalık uzun) · K9 aynı saatte ≥ 4 coin'de birden model sinyali (kalabalık) · K10 hafta sonu (UTC Cmt/Paz)
#   K11 ABD seansı dışında (UTC 13–20 hafta içi DEĞİL) · K12 VIX önceki gün olağandışı yükselmiş (z ≥ 1,5) · K13 stabil coin arzı 7 g zayıf (z ≤ −1)
#   K14 Tether primi yüksek (USDC/USDT z ≤ −1,5: USDT'ye talep) · K15 Tether iskontolu (USDC/USDT z ≥ 1,5)
# Ölçüm: isabet farkı (iyi − kötü) ve işlem başı net farkı · dönemler: seçim 2022-06→2023 · doğrulama 2024+ · 2026. Ayrıca yalnız ⛔ olmayan (prim z > −1) sinyaller içinde (prime EK değer).
# ✅ karar (önceden sabit): kötü pay %5–60 · seçimde fark ≥ +2 puan · 2024+'da fark ≥ +3 puan ve haftalık blok bootstrap %90 alt sınır > 0 · 2026'da (kötü ≥ 20 işlem) fark > 0.
# Plasebo: aynı aile ve aynı kötü payla rastgele "filtre" (haftalara göre karıştırılmış etiket) → tesadüfen geçme oranı.
import os, glob, io, re, time, zipfile, gzip, pickle, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
f = lambda p: glob.glob(p, recursive=True)
ZP = {k: v.astype("float64") for k, v in pd.read_pickle(f("art3/**/prim_veri.pkl")[0]).items()}
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
# ---------- olaylar ----------
EV = []
def ekle(aile, coin, t, r, H):
    for ti, ri in zip(pd.DatetimeIndex(t), np.asarray(r, float)):
        if np.isfinite(ri) and ti >= P0: EV.append((aile, coin, ti, ri, H))
X = SFB
for H in (1, 4, 8):
    S, C, T10, T30, y = X[f"S{H}"], X[f"C{H}"], X[f"T10{H}"], X[f"T30{H}"], X[f"y{H}"]
    for li in (2, 1):
        st = MB["R"][H]["STATS"][(li, 1)]; act, _ = action(H, 1, li, st)
        if act[:1] not in ("✅", "🟢"): continue
        lvl = np.where(C >= T10, 2, np.where(C >= T30, 1, 0)); m = ((S > 0) & (lvl == li) & T10.notna() & y.notna()).values; ev = events(m, H)
        ekle("BTC 1 saat ↑" if H == 1 else "BTC 4/8 saat ↑ + ⭐ + A", "BTC", X.index[ev], np.exp(y.values[ev]) - 1, H)
star = ((X.S4 > 0) & (X.C4 >= X.T104) & (X.S8 > 0) & (X.C8 >= X.T108) & X.y8.notna()).values; ev = events(star, 8); ekle("BTC 4/8 saat ↑ + ⭐ + A", "BTC", X.index[ev], np.exp(X.y8.values[ev]) - 1, 8)
ac = ((X.am >= 0.85) & X.y4.notna()).values; ev = events(ac, 4); ekle("BTC 4/8 saat ↑ + ⭐ + A", "BTC", X.index[ev], np.exp(X.y4.values[ev]) - 1, 4)
B = EX["BTCUSDT"]; AD = {"star": (8, "y8"), "u4": (4, "y4"), "acls": (4, "y4")}
KALAB = pd.Series(0, index=B.index, dtype=float)                                                      # aynı saatte kaç coin'de model sinyali var
for s in CANLI:
    if s in EX: KALAB = KALAB.add((EX[s].star.fillna(False) | EX[s].u4.fillna(False) | EX[s].acls.fillna(False)).astype(float).reindex(KALAB.index).fillna(0), fill_value=0)
for s in CANLI:
    nm = s[:-4]; Xc = EX.get(s)
    if Xc is None: continue
    Bx = B.reindex(Xc.index); bu4 = Bx.u4.fillna(False).values.astype(bool); bany = (Bx.star.fillna(False) | Bx.u4.fillna(False) | Bx.acls.fillna(False)).values.astype(bool)
    jo, te = set(JOINT[JOINT.sym == s].sinyal), set(TEKL[TEKL.sym == s].sinyal)
    for k, (H0, yc0) in AD.items():
        for aile, kos, acik in (("coin tek başına", np.ones(len(Xc), bool), SIGON[s].get(k, False)), ("coin 🤝 ortak", bu4, k in jo), ("coin 🔇 sessiz", ~bany, k in te)):
            if not acik: continue
            H, yc = (H0, yc0) if aile == "coin tek başına" else (4, "y4")
            m = Xc[k].fillna(False).values.astype(bool) & kos & Xc[yc].notna().values; ev = events(m, H); ekle(aile, nm, Xc.index[ev], np.exp(Xc[yc].values[ev]) - 1, H)
for s, Xd in E24.items():
    nm = s.replace("USDT", ""); Xd = Xd.reindex(pd.date_range(Xd.index[0], Xd.index[-1], freq="1h", tz="UTC")); c = Xd.close.ffill(limit=3).values; n = len(Xd)
    m = np.nan_to_num(((Xd.S24 > 0) & (Xd.C24 >= Xd.T10_24)).values).astype(bool) & Xd.T10_24.notna().values & (np.arange(n) + 25 < n); ev = events(m, 24)
    ekle("🧪 24 saat", nm, Xd.index[ev], c[ev + 24] / c[ev] - 1, 24)
E = pd.DataFrame(EV, columns=["aile", "coin", "t", "r", "H"])
yaz(f"# 🔎 Ek filtre taraması — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nOlay: {len(E):,} (2022-06+) · " + " · ".join(f"{a} {n:,}" for a, n in E.aile.value_counts().items()) + f" · {time.time()-T0:.0f} sn\n")
# ---------- durum değişkenleri ----------
def coin_ozellik(nm):
    D = ZP[nm]; c = D.c; lr = np.log(c).diff()
    ema = c.ewm(span=720, adjust=False).mean(); sd = lr.rolling(720, min_periods=168).std()
    r24z = np.log(c / c.shift(24)) / (sd * np.sqrt(24)); vr = lr.rolling(24).std() / sd
    d = c.diff(); up = d.clip(lower=0).ewm(alpha=1/14, adjust=False).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean(); rsi = 100 - 100 / (1 + up / (dn + 1e-12))
    return pd.DataFrame({"alti": c < ema, "r24z": r24z, "vr": vr, "rsi": rsi, "z": D.z})
OZ = {nm: coin_ozellik(nm) for nm in set(E.coin) if nm in ZP}
BT = OZ.get("BTC") if "BTC" in OZ else coin_ozellik("BTC")
t_ = open("turev.py").read(); exec(t_[t_.index("S3, BV = "):t_.index("KL = [")])                       # s3_list, zcsv, load, ms2ts
FS = {"SHIB": "1000SHIBUSDT", "PEPE": "1000PEPEUSDT", "FLOKI": "1000FLOKIUSDT"}
def fonlama(nm):
    try:
        F = load(f"data/futures/um/monthly/fundingRate/{FS.get(nm, nm + 'USDT')}/", ["calc_time", "funding_interval_hours", "last_funding_rate"])
        F["t"] = ms2ts(F.calc_time); v = pd.Series(pd.to_numeric(F.last_funding_rate, errors="coerce").values, index=F.t).dropna().sort_index(); v = v[~v.index.duplicated()]
        d3 = v.rolling("3D").mean(); return nm, (d3 - d3.rolling("90D").mean()) / (d3.rolling("90D").std() + 1e-12)
    except Exception as e: print(nm, e); return nm, None
with ThreadPoolExecutor(6) as ex: FON = dict(ex.map(fonlama, sorted(set(E.coin))))
try:
    import yfinance as yf
    vx = yf.Ticker("^VIX").history(period="max", interval="1d", auto_adjust=True).Close; vx.index = pd.DatetimeIndex(vx.index.tz_localize(None).normalize()).tz_localize("UTC")
    vr_ = np.log(vx).diff(); VIXZ = (vr_ / vr_.rolling(90, min_periods=40).std())
except Exception as e: print("VIX", e); VIXZ = None
try:
    j = requests.get("https://stablecoins.llama.fi/stablecoincharts/all", timeout=60).json()
    sc = pd.Series({pd.Timestamp(int(x["date"]), unit="s", tz="UTC").floor("D"): float((x.get("totalCirculatingUSD") or {}).get("peggedUSD", np.nan)) for x in j}).sort_index()
    g7 = np.log(sc / sc.shift(7)); STZ = (g7 - g7.rolling(90, min_periods=30).mean()) / (g7.rolling(90, min_periods=30).std() + 1e-12)
except Exception as e: print("stabil", e); STZ = None
try:
    uc = fetch_1h(P0.timestamp() * 1000 - 40 * 86400e3, time.time() * 1000, sym="USDCUSDT").close; lu = np.log(uc)
    TZ = (lu - lu.rolling(720, min_periods=168).mean()) / (lu.rolling(720, min_periods=168).std() + 1e-12)
except Exception as e: print("USDC", e); TZ = None
def asof(s, t):
    if s is None: return np.full(len(t), np.nan)
    s = s.dropna(); s.index = pd.DatetimeIndex(s.index).astype("datetime64[ns, UTC]")
    L_ = pd.DataFrame({"t": pd.DatetimeIndex(t).astype("datetime64[ns, UTC]"), "i": np.arange(len(t))}).sort_values("t")
    m = pd.merge_asof(L_, pd.DataFrame({"t": s.index, "v": s.values}), on="t", direction="backward"); return m.sort_values("i").v.values
cols = {k: np.full(len(E), np.nan) for k in ("alti", "btc_alti", "r24z", "vr", "rsi", "z", "fon", "kal", "vix", "stab", "teth")}
for nm, g in E.groupby("coin"):
    i = g.index.values; t = g.t.values
    if nm in OZ:
        o = OZ[nm]
        for k in ("alti", "r24z", "vr", "rsi", "z"): cols[k][i] = asof(o[k].astype(float), t)
    cols["btc_alti"][i] = asof(BT.alti.astype(float), t); cols["fon"][i] = asof(FON.get(nm), t)
cols["kal"] = asof(KALAB, E.t.values); cols["vix"] = asof(VIXZ, pd.DatetimeIndex(E.t).floor("D") - pd.Timedelta(days=1))
cols["stab"] = asof(STZ, pd.DatetimeIndex(E.t).floor("D") - pd.Timedelta(days=1)); cols["teth"] = asof(TZ, E.t.values)
for k, v in cols.items(): E[k] = v
tt = pd.DatetimeIndex(E.t)
KOT = {"K1 coin 30 g ortalama altında": E.alti == 1, "K2 BTC 30 g ortalama altında": E.btc_alti == 1, "K3 son 24 s olağandışı yükselmiş (z ≥ 2)": E.r24z >= 2,
       "K4 son 24 s olağandışı düşmüş (z ≤ −2)": E.r24z <= -2, "K5 oynaklık patlaması (≥ 1,5×)": E.vr >= 1.5, "K6 RSI ≥ 70": E.rsi >= 70, "K7 RSI ≤ 30": E.rsi <= 30,
       "K8 fonlama yüksek (z ≥ 1,5)": E.fon >= 1.5, "K9 aynı saatte ≥ 4 coin sinyali": E.kal >= 4, "K10 hafta sonu": pd.Series(tt.dayofweek >= 5, index=E.index),
       "K11 ABD seansı dışı": pd.Series(~((tt.dayofweek < 5) & (tt.hour >= 13) & (tt.hour <= 20)), index=E.index), "K12 VIX dün sıçramış (z ≥ 1,5)": E.vix >= 1.5,
       "K13 stabil coin talebi zayıf (z ≤ −1)": E.stab <= -1, "K14 Tether primi yüksek (z ≤ −1,5)": E.teth <= -1.5, "K15 Tether iskontolu (z ≥ 1,5)": E.teth >= 1.5}
yaz(f"Değişkenlerin doluluğu: " + " · ".join(f"{k} %{100*E[k].notna().mean():.0f}" for k in cols) + f" · {time.time()-T0:.0f} sn\n")
E["net"] = E.r - 2 * LMT; E["ok"] = E.r > 0; E["hafta"] = tt.floor("7D")
DON = (("seçim", (tt >= P0) & (tt < A24)), ("2024+", tt >= A24), ("2026", tt >= A26))
rng = np.random.default_rng(0)
def fark_boot(ok, kotu, hafta, reps=1000):
    d = pd.DataFrame({"ok": ok.astype(float), "k": kotu.astype(bool), "h": hafta})
    C = pd.DataFrame({"ni": (~d.k).groupby(d.h).sum(), "oi": (d.ok * ~d.k).groupby(d.h).sum(), "nk": d.k.groupby(d.h).sum(), "ok_": (d.ok * d.k).groupby(d.h).sum()}).values.astype(float)
    idx = rng.integers(0, len(C), (reps, len(C))); S = C[idx].sum(axis=1)
    with np.errstate(all="ignore"): fr = 100 * (S[:, 1] / S[:, 0] - S[:, 3] / S[:, 2])
    fr = fr[np.isfinite(fr)]; return np.percentile(fr, 5) if len(fr) else np.nan
def degerlendir(G, kotu):
    r = {}; kotu = kotu.reindex(G.index).fillna(False).astype(bool)
    for pn, md in DON:
        m = md[G.index] if isinstance(md, np.ndarray) else md
        g, k = G[m], kotu[m]
        r[pn] = dict(n=len(g), pay=100 * k.mean() if len(g) else np.nan, kotu_n=int(k.sum()), iyi_is=100 * g.ok[~k].mean() if (~k).any() else np.nan, kotu_is=100 * g.ok[k].mean() if k.any() else np.nan,
                     iyi_net=100 * g.net[~k].mean() if (~k).any() else np.nan, kotu_net=100 * g.net[k].mean() if k.any() else np.nan, tum_is=100 * g.ok.mean() if len(g) else np.nan)
        r[pn]["fark"] = r[pn]["iyi_is"] - r[pn]["kotu_is"]
    d24 = G[DON[1][1][G.index]]; r["alt"] = fark_boot(d24.ok.values, kotu[d24.index].values, d24.hafta.values) if kotu[d24.index].sum() >= 20 else np.nan
    s, d, z = r["seçim"], r["2024+"], r["2026"]
    r["ok"] = bool(5 <= d["pay"] <= 60 and s["fark"] >= 2 and d["fark"] >= 3 and r["alt"] > 0 and (z["kotu_n"] < 20 or z["fark"] > 0))
    return r
ROWS = []
for kapsam, maske in (("tüm sinyaller", E.z.notna() | True), ("yalnız ⛔ olmayanlar (prime ek)", E.z > -1)):
    for aile, G in E[maske].groupby("aile"):
        for kn, kv in KOT.items():
            if kv.reindex(G.index).isna().all(): continue
            r = degerlendir(G, kv); d, s, z = r["2024+"], r["seçim"], r["2026"]
            ROWS.append(dict(kapsam=kapsam, aile=aile, filtre=kn, kotu_pay=d["pay"], secim=f"{s['iyi_is']:.0f} / {s['kotu_is']:.0f} ({s['kotu_n']})",
                             y2024=f"{d['iyi_is']:.0f} / {d['kotu_is']:.0f} ({d['kotu_n']}) · net {d['iyi_net']:+.2f} / {d['kotu_net']:+.2f}", alt=r["alt"],
                             y2026=f"{z['iyi_is']:.0f} / {z['kotu_is']:.0f} ({z['kotu_n']})", tum24=d["tum_is"], iyi24=d["iyi_is"], fark24=d["fark"], ok=r["ok"]))
        # plasebo
        pl = []
        for _ in range(15):
            W = G.hafta.unique(); lab = dict(zip(W, rng.random(len(W)) < 0.3)); kv = pd.Series(G.hafta.map(lab).values & (rng.random(len(G)) < 0.9), index=G.index)
            pl.append(degerlendir(G, kv)["ok"])
        ROWS.append(dict(kapsam=kapsam, aile=aile, filtre="(plasebo: rastgele %27)", kotu_pay=np.nan, secim="", y2024="", alt=np.nan, y2026="", tum24=np.nan, iyi24=np.nan, fark24=np.nan, ok=f"{sum(pl)}/15"))
R = pd.DataFrame(ROWS); R.to_csv("filtre_hepsi_tum.csv", index=False)
gec = R[R.ok == True]
yaz(f"## Özet\nDenenen filtre × aile: {int((R.filtre.str.startswith('K')).sum())} · ✅ geçen **{len(gec)}** · plasebo geçme: " + ", ".join(f"{a} {o}" for a, o in R[R.filtre.str.startswith('(plasebo')][['aile', 'ok']].drop_duplicates('aile').values))
yaz("\n### ✅ Geçenler (iyi / kötü isabet %, kötü işlem sayısı)\n```\n" + (gec[["kapsam", "aile", "filtre", "kotu_pay", "secim", "y2024", "alt", "y2026", "tum24", "iyi24"]].round(1).to_string(index=False) if len(gec) else "(yok)") + "\n```")
for kapsam, g in R.groupby("kapsam", sort=False):
    yaz(f"\n## {kapsam}\n_sütunlar: kötü pay % (2024+) · seçim iyi/kötü isabet · 2024+ iyi/kötü isabet ve net · fark alt sınırı · 2026 iyi/kötü_\n```\n"
        + g[["aile", "filtre", "kotu_pay", "secim", "y2024", "alt", "y2026", "ok"]].round(1).to_string(index=False) + "\n```")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("filtre_hepsi_sonuc.md", "w").write("\n".join(L) + "\n")
