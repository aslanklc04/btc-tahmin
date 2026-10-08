# cikis.py — GİRİŞ ZAMANI ve ÇIKIŞ STRATEJİSİ TESTİ, tüm canlı sinyal türleri (yalnız test; canlıya dokunmaz).
# Fiyat yolu: Binance saatlik OHLC (yüksek/düşük ile kâr-al / zarar-kes dokunuşu). Giriş = sinyal saatinin kapanışı (canlıda ~5 dk sonra limit).
# Komisyon: limit (maker) %0,02 her bacak · zarar-kes / iz süren stop çıkışı piyasa (taker) %0,05 + %0,02 kayma. Aynı saatte hem hedef hem stop → STOP sayılır (temkinli).
# σ = coin'in son 720 saatlik saatlik oynaklığı × √(ana süre) (giriş anında bilinir).
# ÖNCEDEN YAZILI STRATEJİLER (ana süre Hb = sinyalin bugünkü tutma süresi): süre ×0,5 / ×1 (bugün) / ×1,5 / ×2 / ×3 · kâr-al: beklenen fiyat (türün seçim dönemi ort.), +0,5σ, +1σ, +2σ ·
#   zarar-kes −1σ, −2σ · kâr-al/zarar-kes +1σ/−1σ, +2σ/−1σ, +2σ/−2σ, +1σ/−2σ · kârdaysa 2 katına uzat · kârdaysa iz süren stop (1σ, en fazla 3 kat) · iz süren stop 1σ (en fazla 2 kat), 2σ (en fazla 3 kat).
# ÖNCEDEN KARAR: her tür için seçim döneminde (2024 öncesi) işlem başı neti en yüksek strateji seçilir; ancak 2024+'da bugünküne göre (aynı işlemler, eşli) fark > 0 ve haftalık blok %5 alt sınır > 0
#   VE 2026'da fark ≥ 0 ise "kanıtlanmış" sayılır; yoksa bugünkü (süre dolunca sat) kalır. Ayrıca: giriş gecikmesi 0 / 1 / 2 saat · prim z ≥ 3 iken 4 saatte çıkış.
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
yaz(f"# 🚪 Giriş zamanı ve çıkış stratejisi — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nOlay: {len(E):,} · " + " · ".join(f"{a} {n:,}" for a, n in E.aile.value_counts().items()) + f" · fiyat verisi {len(OH)}/{len(COINS)} coin · {time.time()-T0:.0f} sn\n")
MK, TK_, SLP = 0.0002, 0.0005, 0.0002
STR = ["Süre ×0,5", "Süre ×1 (bugün)", "Süre ×1,5", "Süre ×2", "Süre ×3", "Kâr-al: beklenen fiyat", "Kâr-al +0,5σ", "Kâr-al +1σ", "Kâr-al +2σ", "Zarar-kes −1σ", "Zarar-kes −2σ",
       "+1σ / −1σ", "+2σ / −1σ", "+2σ / −2σ", "+1σ / −2σ", "Kârdaysa 2 katına uzat", "Kârdaysa iz süren stop 1σ (≤3 kat)", "İz süren stop 1σ (≤2 kat)", "İz süren stop 2σ (≤3 kat)"]
BASE = "Süre ×1 (bugün)"
def yol(nm, t, Hmax, gec=0):
    o = OH.get(nm)
    if o is None: return None
    i = o.index.searchsorted(t)
    if i >= len(o) or o.index[i] != t: return None
    i += gec
    if i + Hmax >= len(o): return None
    c0 = o.close.values[i]; s1 = SIG1[nm].values[i]
    return c0, o.high.values[i + 1:i + 1 + Hmax] / c0 - 1, o.low.values[i + 1:i + 1 + Hmax] / c0 - 1, o.close.values[i + 1:i + 1 + Hmax] / c0 - 1, s1
def zaman(c, h, yon): return yon * c[h - 1] - 2 * MK, h
def tp_sl(hi, lo, c, Hb, yon, tp=None, sl=None):
    fav, adv = (hi, lo) if yon > 0 else (-lo, -hi)
    for k in range(Hb):
        if sl is not None and -adv[k] >= sl: return -sl - MK - TK_ - SLP, k + 1                       # önce stop (temkinli)
        if tp is not None and fav[k] >= tp: return tp - 2 * MK, k + 1
    return yon * c[Hb - 1] - 2 * MK, Hb
def iz(hi, lo, c, yon, kat, Hmax, bas=0, tepe0=0.0):
    fav, adv = (hi, lo) if yon > 0 else (-lo, -hi); cc = yon * c; tepe = tepe0
    for k in range(bas, Hmax):
        dur = (1 + tepe) * (1 - kat) - 1
        if adv[k] <= dur: return dur - MK - TK_ - SLP, k + 1
        tepe = max(tepe, fav[k])
    return cc[Hmax - 1] - 2 * MK, Hmax
def degerlendir(ev, m_bek):
    Hb = int(ev.H); yon = int(ev.yon); p = yol(ev.nm, ev.t, 3 * Hb)
    if p is None: return None
    c0, hi, lo, c, s1 = p
    if not np.isfinite(s1): return None
    sg = s1 * np.sqrt(Hb); out = {}
    out["Süre ×0,5"] = zaman(c, max(1, round(0.5 * Hb)), yon); out[BASE] = zaman(c, Hb, yon); out["Süre ×1,5"] = zaman(c, round(1.5 * Hb), yon)
    out["Süre ×2"] = zaman(c, 2 * Hb, yon); out["Süre ×3"] = zaman(c, 3 * Hb, yon)
    out["Kâr-al: beklenen fiyat"] = tp_sl(hi, lo, c, Hb, yon, tp=m_bek) if m_bek and m_bek > 0 else out[BASE]
    for ad, k in (("Kâr-al +0,5σ", 0.5), ("Kâr-al +1σ", 1), ("Kâr-al +2σ", 2)): out[ad] = tp_sl(hi, lo, c, Hb, yon, tp=k * sg)
    for ad, k in (("Zarar-kes −1σ", 1), ("Zarar-kes −2σ", 2)): out[ad] = tp_sl(hi, lo, c, Hb, yon, sl=k * sg)
    for ad, a, b in (("+1σ / −1σ", 1, 1), ("+2σ / −1σ", 2, 1), ("+2σ / −2σ", 2, 2), ("+1σ / −2σ", 1, 2)): out[ad] = tp_sl(hi, lo, c, Hb, yon, tp=a * sg, sl=b * sg)
    rb = yon * c[Hb - 1]
    out["Kârdaysa 2 katına uzat"] = zaman(c, 2 * Hb, yon) if rb > 0 else out[BASE]
    if rb > 0:
        fav = hi if yon > 0 else -lo; out["Kârdaysa iz süren stop 1σ (≤3 kat)"] = iz(hi, lo, c, yon, sg, 3 * Hb, bas=Hb, tepe0=float(max(0, fav[:Hb].max())))
    else: out["Kârdaysa iz süren stop 1σ (≤3 kat)"] = out[BASE]
    out["İz süren stop 1σ (≤2 kat)"] = iz(hi, lo, c, yon, sg, 2 * Hb); out["İz süren stop 2σ (≤3 kat)"] = iz(hi, lo, c, yon, 2 * sg, 3 * Hb)
    for g in (1, 2):                                                                              # giriş gecikmesi
        q = yol(ev.nm, ev.t, Hb, gec=g); out[f"gec{g}"] = (yon * q[3][Hb - 1] - 2 * MK, Hb) if q is not None else (np.nan, Hb)
    out["4s"] = zaman(c, min(4, Hb), yon)
    return out
A24_, A26_ = pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")
DON2 = (("seçim (2024 öncesi)", lambda i: i < A24_), ("2024+", lambda i: i >= A24_), ("2026", lambda i: i >= A26_))
# türün "beklenen" getirisi: seçim döneminde bugünkü stratejinin ortalama brüt getirisi (canlı mesajdaki gibi geçmiş ortalama)
SON = []
for aile, G in E.groupby("aile"):
    tt_ = pd.DatetimeIndex(G.t); g0 = []
    for _, ev in G[tt_ < A24_].iterrows():
        p = yol(ev.nm, ev.t, int(ev.H))
        if p is not None: g0.append(ev.yon * p[3][int(ev.H) - 1])
    m_bek = float(np.mean(g0)) if len(g0) >= 10 else (float(np.nanmean([ev.yon * yol(ev.nm, ev.t, int(ev.H))[3][int(ev.H) - 1] for _, ev in G.iterrows() if yol(ev.nm, ev.t, int(ev.H)) is not None])) if len(G) else np.nan)
    for _, ev in G.iterrows():
        o = degerlendir(ev, m_bek)
        if o is None: continue
        row = dict(aile=aile, nm=ev.nm, t=ev.t, z=ev.z, H=int(ev.H), m_bek=m_bek)
        for k, (v, h) in o.items(): row[k] = v; row["h_" + k] = h
        SON.append(row)
R = pd.DataFrame(SON); R["hafta"] = pd.DatetimeIndex(R.t).floor("7D"); R.to_pickle("cikis_ham.pkl")
yaz(f"Değerlendirilen olay: {len(R):,} · {time.time()-T0:.0f} sn\n")
def lb_fark(d, h, reps=2000):
    rng = np.random.default_rng(0); x = pd.DataFrame({"d": d, "h": h}).dropna(); C = x.groupby("h").d.agg(["sum", "count"]).values
    if len(C) < 5: return np.nan
    S_ = C[rng.integers(0, len(C), (reps, len(C)))].sum(axis=1); return float(np.percentile(S_[:, 0] / S_[:, 1], 5))
def hucre(x, k): return f"{100*x[k].mean():+.2f} · %{100*(x[k]>0).mean():.0f} · {x['h_'+k].mean():.0f}s" if len(x) >= 5 else "—"
KARAR = []
for aile, G in R.groupby("aile"):
    gt = pd.DatetimeIndex(G.t); T = {}
    for k in STR: T[k] = {dn: hucre(G[fd(gt)], k) for dn, fd in DON2}
    sec = G[gt < A24_]
    if len(sec) < 20: sec = G[gt < pd.Timestamp("2025-01-01", tz="UTC")]; not_ = " (seçim örneği az → seçim 2024 sonuna kadar)"
    else: not_ = ""
    best = max(STR, key=lambda k: sec[k].mean() if len(sec) else -9)
    v24 = G[gt >= (A24_ if not not_ else pd.Timestamp("2025-01-01", tz="UTC"))]; v26 = G[gt >= A26_]
    f24 = (v24[best] - v24[BASE]).mean(); lb = lb_fark((v24[best] - v24[BASE]).values, v24.hafta.values); f26 = (v26[best] - v26[BASE]).mean() if len(v26) else np.nan
    ok = best != BASE and f24 > 0 and lb > 0 and (not np.isfinite(f26) or f26 >= 0)
    KARAR.append(dict(tur=aile, n=len(G), secilen=best, fark_2024=100 * f24, alt=100 * lb if np.isfinite(lb) else np.nan, fark_2026=100 * f26 if np.isfinite(f26) else np.nan, karar="✅ kanıtlandı" if ok else ("= bugünkü en iyi" if best == BASE else "❌ kanıtlanmadı → bugünkü kalsın")))
    yaz(f"\n## {aile} — {len(G):,} işlem · ana süre {int(G.H.mode().iloc[0])} saat · beklenen fiyat hedefi +%{100*G.m_bek.iloc[0]:.2f}{not_}\n_hücre: işlem başı net % · isabet · ortalama tutma süresi_\n```\n" + pd.DataFrame(T).T.to_string() + "\n```")
    gc = {dn: (lambda x: f"0 s {100*x[BASE].mean():+.2f} · 1 s gecikme {100*x['gec1'].mean():+.2f} · 2 s gecikme {100*x['gec2'].mean():+.2f}")(G[fd(gt)]) for dn, fd in DON2 if len(G[fd(gt)]) >= 5}
    yaz("Giriş gecikmesi (aynı süre tutulur): " + " | ".join(f"{dn}: {v}" for dn, v in gc.items()))
    z3 = G[(G.z >= 3) & (G.H > 4)]
    if len(z3) >= 10:
        z3t = pd.DatetimeIndex(z3.t); yaz("Prim z ≥ 3 iken 4 saatte çık vs süre dolunca: " + " | ".join(f"{dn}: {len(z3[fd(z3t)])} işlem · 4 s {100*z3[fd(z3t)]['4s'].mean():+.2f} / bugünkü {100*z3[fd(z3t)][BASE].mean():+.2f}" for dn, fd in DON2 if len(z3[fd(z3t)]) >= 3))
    yaz(f"**Seçimde en iyi:** {best} → 2024+ fark {100*f24:+.3f} (alt sınır {100*lb:+.3f}) · 2026 fark {100*f26 if np.isfinite(f26) else float('nan'):+.3f} → {KARAR[-1]['karar']}")
# tek strateji herkese
sec = R[pd.DatetimeIndex(R.t) < A24_]; bestG = max(STR, key=lambda k: sec[k].mean()); v = R[pd.DatetimeIndex(R.t) >= A24_]; v26 = R[pd.DatetimeIndex(R.t) >= A26_]
fG = (v[bestG] - v[BASE]).mean(); lbG = lb_fark((v[bestG] - v[BASE]).values, v.hafta.values); fG26 = (v26[bestG] - v26[BASE]).mean()
z3 = R[(R.z >= 3) & (R.H > 4)]; z3a = z3[pd.DatetimeIndex(z3.t) >= A24_]
yaz(f"\n## Özet\n```\n" + pd.DataFrame(KARAR).round(3).to_string(index=False) + "\n```\nHerkese tek strateji (seçimde en iyi): **{bestG}** → 2024+ fark {100*fG:+.3f} (alt {100*lbG:+.3f}) · 2026 {100*fG26:+.3f}")
yaz(f"Prim z ≥ 3 (tüm türler, ana süre > 4 s), 2024+: {len(z3a)} işlem · 4 saatte çık {100*z3a['4s'].mean():+.2f} · süre dolunca {100*z3a[BASE].mean():+.2f} · fark alt sınır {100*lb_fark((z3a['4s']-z3a[BASE]).values, z3a.hafta.values):+.3f}")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("cikis_sonuc.md", "w").write("\n".join(L) + "\n")
