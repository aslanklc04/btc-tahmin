# ab_prim.py — AVRUPA PRİMİ + ABD PRİMİ BİRLİKTE (yalnız test; canlıya dokunmaz)
# ABD primi (canlıdaki): log(Coinbase COIN-USD / Binance COINUSDT), z son 720 saat.
# AVRUPA primi: log(Bitvavo COIN-EUR × Binance EURUSDT / Binance COINUSDT), z son 720 saat.  Bitvavo = AB'nin en büyük bireysel kripto borsası (yalnız Avrupalı müşteri, EUR).
#   (EUR → USDT çevirisi aynı saatin Binance EURUSDT kapanışıyla; böylece USDT'nin dolardan sapması da kendiliğinden düşer.)
# Sinyaller: canlıda mesajı giden tüm türler (prim_pencere.py ile aynı olaylar), her coin kendi primiyle. Dönemler: 2022-06→2023 · 2024+ · 2026.
# ÖNCEDEN YAZILI KARARLAR (tüm türler birlikte, iki prim de biliniyorken):
#   K1 "İkisi birden alıyor" filtresi: ABD z > 0 olan sinyallerde, Avrupa z > 0 olanların isabeti olmayanlardan ≥ 2 puan yüksek — HEM 22-06→23 HEM 2024+ · 2026'da ≥ 0 ·
#      2024+ 7 türün ≥ 4'ünde pozitif · 2024+ haftalık blok bootstrap %5 alt sınır > 0.
#   K2 Avrupa ⛔ ek uyarısı: ABD ⛔ olmayan (ABD z > −1) sinyallerde, Avrupa z ≤ −1 olanlar diğerlerinden ≥ 3 puan kötü — iki dönemde de · 2026 ≥ 0 · 2024+ alt sınır > 0.
#   K3 "İkisi de güçlü alıyor": ABD z ≥ 1 olan sinyallerde, Avrupa z ≥ 1 olanlar olmayanlardan ≥ 3 puan iyi — iki dönemde de · 2026 ≥ 0 · 2024+ alt sınır > 0.
#   K4 Tek başına 💵: ABD z ≥ 2 olaylarında, Avrupa z ≥ 1 olanların işlem başı neti olmayanlardan yüksek — 4/8/24 s'nin ≥ 2'sinde iki dönemde de, 2026'da ters dönmeden.
import os, glob, gzip, json, pickle, time, threading, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
f = lambda p: glob.glob(p, recursive=True)
RAW = {k: v.astype("float64") for k, v in pd.read_pickle(f("art3/**/prim_veri.pkl")[0]).items()}; RAW = {k: v for k, v in RAW.items() if len(v) >= 3000}
for k, v in RAW.items(): v.index = pd.DatetimeIndex(v.index).tz_convert("UTC").as_unit("ns")
BAS, SON = pd.Timestamp("2022-04-01", tz="UTC"), pd.Timestamp.now(tz="UTC").floor("h")
zf = lambda p: (p - p.rolling(720, min_periods=168).mean()) / (p.rolling(720, min_periods=168).std() + 1e-12)
# ---------------- Avrupa verisi ----------------
_kilit, _son = threading.Lock(), [0.0]
def bv_get(market, a, b):
    for k in range(6):
        with _kilit:
            w = 0.11 - (time.time() - _son[0])
            if w > 0: time.sleep(w)
            _son[0] = time.time()
        try:
            r = requests.get(f"https://api.bitvavo.com/v2/{market}/candles", params=dict(interval="1h", limit=1440, start=a, end=b), timeout=30, headers={"User-Agent": "btc-tahmin-arastirma"})
            if r.status_code == 429: time.sleep(2 + 2 * k); continue
            return r
        except Exception: time.sleep(2)
    return None
def bitvavo(market):
    out, cur = [], BAS
    while cur < SON:
        nx = min(cur + pd.Timedelta(hours=1440), SON); r = bv_get(market, int(cur.timestamp() * 1000), int(nx.timestamp() * 1000) - 1)
        if r is not None and r.status_code == 200 and isinstance(r.json(), list): out += r.json()
        elif r is not None and r.status_code in (400, 404): return None, f"{r.status_code} {r.text[:80]}"
        cur = nx
    if not out: return None, "boş"
    d = pd.DataFrame([x[:6] for x in out], columns=["t", "o", "h", "l", "c", "v"]).drop_duplicates("t")
    s = pd.Series(d.c.astype(float).values, index=pd.to_datetime(d.t.astype("int64"), unit="ms", utc=True) + pd.Timedelta(hours=1)).sort_index(); s.index = s.index.as_unit("ns"); return s, "ok"
EUR = None
try:
    e = fetch_1h(BAS.timestamp() * 1000, time.time() * 1000, sym="EURUSDT"); EUR = e.close.astype(float); EUR.index = pd.DatetimeIndex(EUR.index).as_unit("ns"); kur = "Binance EURUSDT"
except Exception as ex: print("EURUSDT yok", ex)
if EUR is None or len(EUR) < 5000:
    u, _ = bitvavo("USDC-EUR"); EUR = (1 / u) if u is not None else None; kur = "Bitvavo USDC-EUR (ters)"
def ab(nm):
    s, durum = bitvavo(f"{nm}-EUR")
    if s is None: return nm, None, durum
    D = RAW[nm]; ix = D.index; p = np.log(s.reindex(ix) * EUR.reindex(ix) / D.c)
    p = p.where(p.abs() < 0.05)                                                                       # %5'ten büyük sapma = veri hatası / işlem yok saati
    if p.notna().sum() < 3000: return nm, None, f"az veri ({p.notna().sum()})"
    return nm, pd.DataFrame({"bp_ab": 1e4 * p, "z_ab": zf(p)}), "ok"
with ThreadPoolExecutor(6) as ex: AB_ = list(ex.map(ab, list(RAW)))
AB = {nm: d for nm, d, _ in AB_ if d is not None}; YOK = {nm: du for nm, d, du in AB_ if d is None}
pd.to_pickle(AB, "ab_veri.pkl")
yaz(f"# 🇪🇺🇺🇸 Avrupa primi + ABD primi — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nKur: {kur} · Avrupa verisi gelen: {len(AB)}/{len(RAW)} coin ({', '.join(sorted(AB))})\n"
    + (f"Gelmeyen: {', '.join(f'{k} ({v})' for k, v in sorted(YOK.items()))}\n" if YOK else ""))
OZ = []
for nm, d in AB.items():
    u = RAW[nm].z; a = d.z_ab; m = (u.index >= pd.Timestamp("2024-01-01", tz="UTC")) & u.notna().values & a.notna().values
    OZ.append(dict(coin=nm, saat=int(m.sum()), ab_prim_bp_ort=d.bp_ab[m].mean(), abd_prim_bp_ort=RAW[nm].bp[m].mean(), z_uyum=np.corrcoef(u[m], a[m])[0, 1] if m.sum() > 100 else np.nan,
                   ikisi_pozitif=100 * ((u[m] > 0) & (a[m] > 0)).mean(), son_abd_z=u.dropna().iloc[-1], son_ab_z=a.dropna().iloc[-1] if a.notna().any() else np.nan))
OZ = pd.DataFrame(OZ).sort_values("z_uyum", ascending=False)
yaz("## 0) Veri: Avrupa ve ABD primi ne kadar birlikte hareket ediyor (2024+)\n_z_uyum: iki primin z'si arasındaki korelasyon (1 = hep birlikte) · ikisi_pozitif: iki primin aynı anda normalin üstünde olduğu saat oranı %_\n```\n" + OZ.round(2).to_string(index=False) + "\n```")
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
zu, za = np.full(len(E), np.nan), np.full(len(E), np.nan)
for nm, g in E.groupby("nm"):
    ti = pd.DatetimeIndex(g.t).tz_convert("UTC").as_unit("ns")
    if nm in RAW: zu[g.index.values] = RAW[nm].z.reindex(ti).values
    if nm in AB: za[g.index.values] = AB[nm].z_ab.reindex(ti).values
E["zu"], E["za"] = zu, za; E["net"] = E.r - 2 * LMT; E["ok"] = E.r > 0; E["hafta"] = pd.DatetimeIndex(E.t).floor("7D")
E2 = E[np.isfinite(E.zu) & np.isfinite(E.za)].copy(); AILE = list(E2.aile.value_counts().index)
yaz(f"\nCanlıda mesajı giden AL sinyalleri (2022-06+): {len(E):,} · iki primi de bilinen: {len(E2):,} · " + " · ".join(f"{a} {n:,}" for a, n in E2.aile.value_counts().items()) + "\n")
# ---------------- 1) filtre ----------------
def isb(g, m): return (100 * g.ok.values[m].mean() if m.any() else np.nan, int(m.sum()))
GR = (("🇺🇸✅🇪🇺✅ ikisi de alıyor", lambda u, a: (u > 0) & (a > 0)), ("🇺🇸✅ yalnız ABD", lambda u, a: (u > 0) & (a <= 0)), ("🇪🇺✅ yalnız Avrupa", lambda u, a: (u <= 0) & (a > 0)),
      ("ikisi de almıyor", lambda u, a: (u <= 0) & (a <= 0)), ("💪 ikisi de güçlü (z ≥ 1)", lambda u, a: (u >= 1) & (a >= 1)), ("🇺🇸⛔ ABD satıyor", lambda u, a: u <= -1),
      ("🇪🇺⛔ yalnız Avrupa satıyor", lambda u, a: (u > -1) & (a <= -1)), ("🇺🇸⛔🇪🇺⛔ ikisi de satıyor", lambda u, a: (u <= -1) & (a <= -1)))
yaz("## 1) Filtre: sinyal geldiğinde iki prim nasıldı? — _isabet % (işlem)_")
for dn, fd in DON:
    T = {}
    for aile in AILE + ["HEPSİ"]:
        g = E2 if aile == "HEPSİ" else E2[E2.aile == aile]; md = fd(pd.DatetimeIndex(g.t)); u, a = g.zu.values, g.za.values
        T[aile] = {gn: (lambda x: f"%{x[0]:.0f} ({x[1]})" if x[1] >= 5 else (f"({x[1]})" if x[1] else "—"))(isb(g, md & fg(u, a))) for gn, fg in GR}
    yaz(f"\n### {dn}\n```\n" + pd.DataFrame(T).T.reindex(columns=[gn for gn, _ in GR]).to_string() + "\n```")
def fark(g, ma, mb, md): a, b = isb(g, md & ma), isb(g, md & mb); return a[0] - b[0] if a[1] and b[1] else np.nan
def alt(g, ma, mb, md, reps=1000):
    rng = np.random.default_rng(0); d = pd.DataFrame({"ok": g.ok.values.astype(float), "a": md & ma, "b": md & mb, "h": g.hafta.values})
    C = pd.DataFrame({"na": d.a.groupby(d.h).sum(), "oa": (d.ok * d.a).groupby(d.h).sum(), "nb": d.b.groupby(d.h).sum(), "ob": (d.ok * d.b).groupby(d.h).sum()}).values.astype(float)
    S_ = C[rng.integers(0, len(C), (reps, len(C)))].sum(axis=1)
    with np.errstate(all="ignore"): fr = 100 * (S_[:, 1] / S_[:, 0] - S_[:, 3] / S_[:, 2])
    fr = fr[np.isfinite(fr)]; return float(np.percentile(fr, 5)) if len(fr) else np.nan
def karar(ad, kosul, ma_f, mb_f, esik):
    u, a = E2.zu.values, E2.za.values; tt = pd.DatetimeIndex(E2.t); r = {dn: fark(E2, ma_f(u, a) & kosul(u, a), mb_f(u, a) & kosul(u, a), fd(tt)) for dn, fd in DON}
    lb = alt(E2, ma_f(u, a) & kosul(u, a), mb_f(u, a) & kosul(u, a), DON[1][1](tt))
    tur = 0
    for aile in AILE:
        g = E2[E2.aile == aile]; uu, aa = g.zu.values, g.za.values; x = fark(g, ma_f(uu, aa) & kosul(uu, aa), mb_f(uu, aa) & kosul(uu, aa), DON[1][1](pd.DatetimeIndex(g.t))); tur += bool(np.isfinite(x) and x > 0)
    ok = r["22-06→23"] >= esik and r["2024+"] >= esik and r["2026"] >= 0 and lb > 0 and (tur >= 4 if ad.startswith("K1") else True)
    yaz(f"- {ad}: fark {r['22-06→23']:+.1f} (22-06→23) · {r['2024+']:+.1f} (2024+) · {r['2026']:+.1f} (2026) · 2024+ alt sınır {lb:+.1f} · 2024+ pozitif tür {tur}/{len(AILE)} → {'✅ GEÇTİ' if ok else '❌'}")
yaz("\n**Önceden yazılı kararlar (filtre):**")
karar("K1 ikisi birden alıyor (ABD z > 0 içinde: Avrupa z > 0 / ≤ 0)", lambda u, a: u > 0, lambda u, a: a > 0, lambda u, a: a <= 0, 2)
karar("K2 Avrupa ⛔ ek uyarı (ABD z > −1 içinde: Avrupa z > −1 / ≤ −1)", lambda u, a: u > -1, lambda u, a: a > -1, lambda u, a: a <= -1, 3)
karar("K3 ikisi de güçlü (ABD z ≥ 1 içinde: Avrupa z ≥ 1 / < 1)", lambda u, a: u >= 1, lambda u, a: a >= 1, lambda u, a: a < 1, 3)
# ---------------- 2) birlikte doz-yanıt (tüm saatler, 24 s fazla getiri) ----------------
yaz("\n## 2) İki prim birlikte yüksekse fiyat ne yapıyor? (tüm saatler, coin'ler eşit ağırlık, 24 saatlik getiri − coin'in dönem ortalaması, %)")
DL = ((-np.inf, -1, "≤−1"), (-1, 1, "−1…1"), (1, 2, "1…2"), (2, np.inf, "≥2"))
for dn, fd in DON[:2]:
    acc = {}
    for nm, d in AB.items():
        D = RAW[nm]; y = D.c.shift(-25) / D.c.shift(-1) - 1; md = fd(D.index) & y.notna().values & D.z.notna().values & d.z_ab.notna().values
        if md.sum() < 500: continue
        base = y.values[md].mean()
        for ul, uh, un in DL:
            for al, ah, an in DL:
                m = md & (D.z.values > ul) & (D.z.values <= uh) & (d.z_ab.values > al) & (d.z_ab.values <= ah)
                if m.sum() >= 20: acc.setdefault((un, an), []).append(100 * (y.values[m].mean() - base))
    T = pd.DataFrame({an: {un: (f"{np.mean(acc[(un, an)]):+.2f} ({len(acc[(un, an)])})" if (un, an) in acc else "—") for _, _, un in DL} for _, _, an in DL})
    T.index.name = "ABD z ↓ / Avrupa z →"; yaz(f"\n### {dn} _(parantez: coin sayısı)_\n```\n" + T.to_string() + "\n```")
# ---------------- 3) tek başına 💵: ABD z ≥ 2 olayları Avrupa'ya göre ----------------
yaz("\n## 3) Tek başına 💵 (ABD z ≥ 2 → AL), Avrupa primine göre ayrılmış — _işlem · isabet % · işlem başı net %_")
K4 = {}; TB = []
for H in (4, 8, 24):
    parca = {"ABD z ≥ 2 (hepsi)": [], "ABD z ≥ 2 & Avrupa z ≥ 1": [], "ABD z ≥ 2 & Avrupa z < 1": [], "Avrupa z ≥ 2 (tek başına)": [], "ikisi de z ≥ 2": []}
    for nm, d in AB.items():
        D = RAW[nm]; y = D.c.shift(-(1 + H)) / D.c.shift(-1) - 1; u, a = D.z, d.z_ab
        ev = D.index[events((u >= 2).fillna(False).values, H)]; au = a.reindex(ev)
        parca["ABD z ≥ 2 (hepsi)"].append(y.reindex(ev)); parca["ABD z ≥ 2 & Avrupa z ≥ 1"].append(y.reindex(ev[(au >= 1).values])); parca["ABD z ≥ 2 & Avrupa z < 1"].append(y.reindex(ev[(au < 1).values]))
        parca["Avrupa z ≥ 2 (tek başına)"].append(y.reindex(D.index[events((a >= 2).fillna(False).values, H)]))
        parca["ikisi de z ≥ 2"].append(y.reindex(D.index[events(((u >= 2) & (a >= 2)).fillna(False).values, H)]))
    for k, v in parca.items():
        x = (pd.concat(v).dropna() - 2 * LMT).sort_index(); row = dict(saat=H, kural=k)
        for dn, fd in DON:
            xx = x[fd(x.index)]; row[dn] = f"{len(xx)} · {100*(xx>0).mean():.0f} · {100*xx.mean():+.2f}" if len(xx) >= 8 else "—"; K4[(H, k, dn)] = xx.mean() if len(xx) >= 8 else np.nan
        TB.append(row)
yaz("```\n" + pd.DataFrame(TB).set_index(["saat", "kural"]).to_string() + "\n```")
iyi = [H for H in (4, 8, 24) if all(np.isfinite(K4[(H, 'ABD z ≥ 2 & Avrupa z ≥ 1', dn)]) and K4[(H, 'ABD z ≥ 2 & Avrupa z ≥ 1', dn)] > K4[(H, 'ABD z ≥ 2 & Avrupa z < 1', dn)] for dn in ("22-06→23", "2024+"))
       and not (K4[(H, 'ABD z ≥ 2 & Avrupa z ≥ 1', '2026')] < K4[(H, 'ABD z ≥ 2 & Avrupa z < 1', '2026')])]
yaz(f"\n**K4 (tek başına 💵, Avrupa onayı):** iki dönemde de daha iyi ve 2026'da ters dönmeyen süreler: {iyi or 'yok'} → {'✅ GEÇTİ' if len(iyi) >= 2 else '❌'}")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("ab_prim_sonuc.md", "w").write("\n".join(L) + "\n")
