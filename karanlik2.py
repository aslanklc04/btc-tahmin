# karanlik2.py — BTC DÜŞERKEN YÜKSELENLERİN SIRRI, YENİ VERİYLE (21.10.2026, kullanıcı: "BTC düşerken yükselenlerin sırrını bul"; yalnız test)
# karanlik.py: ≥ +%5 yükselenlerin %53'ünde pencere içinde hacim patlaması → patlama NEREDEN? Yeni veri: Upbit (Kore primi, Kore hacmi, Kore payı) ·
#   Binance vadeli metrikleri (açık pozisyon değişimi, tüm hesaplar / büyük hesaplar long-short, vadeli agresif alıcı oranı) + coin fonlaması (short sıkışması).
# (1) BETİMLEME: BTC sonradan 24 s düştüğünde yükselen vs düşen — t anındaki izler (yeni özellikler dahil) ve pencere İÇİNDE ne oldu.
# (2) KURAL: karanlik.py ile aynı arama (KA/KB/KC × 4/8/24 s × uç dilim + ikili) + ÖNCEDEN SABİT 4 "erken yakalama" kuralı (seçim kapısı yok):
#     E1 coin BTC'den kopuyor (BTC'ye göre 4 s güç z ≥ 1,5) + Kore hacim patlaması (Upbit saatlik hacim z ≥ 3)
#     E2 kopuyor (z ≥ 1,5) + Kore primi z ≥ 1,5 · E3 short sıkışması: fonlama z ≤ −1,5 + açık pozisyon 24 s z ≥ 1 + son 4 s getiri z ≥ 1
#     E4 hacimli kopuş: saatlik hacim z ≥ 3 + BTC'ye göre 4 s güç z ≥ 2 + alıcı oranı (1 s) ≥ 0,6
# Seçim 2022-03→2023 (vadeli arşivi 2022'den) · doğrulama 2024–25 · 2026 (veri ~15.10.2026'ya kadar).
# ÖNCEDEN YAZILI ŞART (sonuç görülmeden): karanlik.py'nin şartları (doğrulama ve 2026 isabet ≥ %65, saat bazında ≥ %65, net > 0, n ≥ 40 / 10, blok alt sınır > 0,
#   plasebo 20 kaydırma) + ÇÖKÜŞ DİBİ DERSİ: GÜN bazında isabet (aynı UTC günündeki sinyaller tek olay) doğrulamada ve 2026'da ≥ %65.
#   Geçen olursa ayrıca listeden çıkan coin'lerle (hayatta kalan yanılgısı) test edilir; o da geçmeden canlıya önerilmez.
import os, glob, io, time, zipfile, requests, numpy as np, pandas as pd, lightgbm as lgb
from concurrent.futures import ThreadPoolExecutor
from ortak import EP, wboot
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(str(s))
def kaydet(): open("karanlik2_sonuc.md", "w").write("\n".join(L) + "\n")
def dk(): return f"{(time.time() - T0) / 60:.0f} dk"
def utc(ix): ix = pd.DatetimeIndex(ix); return (ix.tz_localize("UTC") if ix.tz is None else ix.tz_convert("UTC")).as_unit("ns")
KURU = os.environ.get("KURU") == "1"
BAS = pd.Timestamp("2021-01-01", tz="UTC"); MAL = 0.0004; HS = (4, 8, 24)

# ---------------- veri ----------------
if KURU:
    rg0 = np.random.default_rng(1); ix0 = pd.date_range(BAS, pd.Timestamp("2026-10-20", tz="UTC"), freq="1h").as_unit("ns"); n0 = len(ix0)
    bl = rg0.normal(0, .006, n0); O = {}
    for k, nm in enumerate(["BTC"] + [f"C{i}" for i in range(12)]):
        b_ = 0 if nm == "BTC" else rg0.uniform(.3, 1.3); lr_ = bl * (1 if nm == "BTC" else b_) + (0 if nm == "BTC" else rg0.normal(0, .01, n0))
        st = 0 if k < 8 else rg0.integers(0, n0 // 2)
        qv = np.exp(rg0.normal(14, 1, n0)); O[nm] = pd.DataFrame({"close": 100 * np.exp(np.cumsum(lr_)), "qv": qv, "n": qv / 50, "tbq": qv * rg0.uniform(.4, .6, n0)}, index=ix0).iloc[st:]
    FON, PZ, MT, UP = {}, {}, {}, {}
    for nm in ["BTC"] + [f"C{i}" for i in range(6)]:
        o_ = O[nm]; UP[nm] = pd.DataFrame({"krw": o_.close * 1300 * np.exp(rg0.normal(0, .002, len(o_))), "krw_hacim": o_.qv * 1300 * rg0.uniform(.2, 2, len(o_)), "usdt": o_.close}, index=o_.index)
        if nm != "BTC": MT[nm] = pd.DataFrame({"oi": np.exp(np.cumsum(rg0.normal(0, .01, len(o_)))) * 1e7, "top_ls": rg0.uniform(.8, 1.5, len(o_)), "ls": rg0.uniform(.8, 2, len(o_)), "taker": rg0.uniform(.8, 1.2, len(o_))}, index=o_.index)
        FON[nm] = pd.Series(rg0.normal(1e-4, 1e-4, len(o_) // 8), index=o_.index[::8][:len(o_) // 8])
else:
    GEN = [l.strip()[:-4] for l in open("canli/durum/genis_liste.txt") if l.strip()]; COR = [l.strip().replace("USDT", "") for l in open("canli/durum/coin_listesi.txt") if l.strip()]
    CO = sorted((set(GEN) | set(COR)) - {"BTC"})
    def kl(nm):
        for url in EP:
            try:
                rows, cur, end = [], int(BAS.timestamp() * 1000), int(time.time() * 1000)
                while cur < end:
                    r = requests.get(url, params=dict(symbol=f"{nm}USDT", interval="1h", startTime=cur, limit=1000), timeout=20); r.raise_for_status(); dt = r.json()
                    if not dt: break
                    rows += dt; cur = dt[-1][0] + 3_600_000
                    if len(dt) < 1000: break
                if not rows: return nm, None
                df = pd.DataFrame([[x[0], x[4], x[7], x[8], x[10]] for x in rows], columns=["t", "close", "qv", "n", "tbq"]).astype(float)
                df.index = pd.DatetimeIndex(pd.to_datetime(df.t, unit="ms", utc=True) + pd.Timedelta(hours=1)).as_unit("ns")
                df = df[~df.index.duplicated()].sort_index(); df = df[df.index <= pd.Timestamp.now(tz="UTC")]
                return nm, df.drop(columns="t")
            except Exception as e: print(nm, url.split("/")[2], e, flush=True)
        return nm, None
    with ThreadPoolExecutor(8) as ex: O = {k: v for k, v in ex.map(kl, CO + ["BTC"]) if v is not None and len(v) > 24 * 400}
    yaz(f"# 🌑🔑 BTC düşerken yükselenlerin sırrı (Kore + vadeli) — {pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M}\nfiyat verisi: {len(O) - 1} coin · {dk()}")
    SS = requests.Session(); AYLAR = [d.strftime("%Y-%m") for d in pd.date_range("2021-01-01", "2026-09-01", freq="MS")]
    VADS = {"SHIB": "1000SHIBUSDT", "PEPE": "1000PEPEUSDT", "FLOKI": "1000FLOKIUSDT", "BONK": "1000BONKUSDT", "LUNC": "1000LUNCUSDT", "XEC": "1000XECUSDT", "SATS": "1000SATSUSDT"}
    def zcsv(url):
        for k in range(4):
            try:
                r = SS.get(url, timeout=30)
                if r.status_code == 404: return None
                if r.status_code == 200: z_ = zipfile.ZipFile(io.BytesIO(r.content)); return pd.read_csv(z_.open(z_.namelist()[0]), header=None, dtype=str)
            except Exception: time.sleep(1 + k)
        return None
    def fon(nm):
        sym = VADS.get(nm, nm + "USDT"); fr = [x for x in (zcsv(f"https://data.binance.vision/data/futures/um/monthly/fundingRate/{sym}/{sym}-fundingRate-{ym}.zip") for ym in AYLAR) if x is not None]
        if not fr: return nm, None
        f_ = pd.concat(fr); f_ = f_[pd.to_numeric(f_[0], errors="coerce").notna()]; ft = f_[0].astype(float).values; ft = np.where(ft > 1e14, ft / 1000, ft)
        s = pd.Series(f_.iloc[:, -1].astype(float).values, index=pd.DatetimeIndex(pd.to_datetime(ft, unit="ms", utc=True)).round("min").as_unit("ns")); return nm, s[~s.index.duplicated()].sort_index()
    with ThreadPoolExecutor(8) as ex: FON = {k: v for k, v in ex.map(fon, sorted(O)) if v is not None}
    yaz(f"fonlama verisi: {len(FON)} coin (aylık arşiv 2026-09 sonuna kadar; Ekim 2026'da boş) · {dk()}")
    PZ = {}
    for p in glob.glob("ga/**/prim_*USDT.pkl", recursive=True):
        d = pd.read_pickle(p).astype("float64"); d.index = utc(d.index); PZ[os.path.basename(p)[5:-8]] = d.z[~d.index.duplicated()].sort_index()
    for p in glob.glob("art3/**/prim_veri.pkl", recursive=True):
        for k, v in pd.read_pickle(p).items():
            if k not in PZ: v = v.astype("float64"); v.index = utc(v.index); PZ[k] = v.z[~v.index.duplicated()].sort_index()
    yaz(f"Coinbase prim verisi: {len(PZ)} coin")
    MT = {}
    for p_ in glob.glob("mt/**/metrik_parca*.pkl", recursive=True): MT.update(pd.read_pickle(p_))
    for k_, v_ in MT.items(): v_.index = utc(v_.index); MT[k_] = v_[~v_.index.duplicated()].sort_index().astype("float64")
    UP = pd.read_pickle(glob.glob("up/**/upbit_veri.pkl", recursive=True)[0])
    for k_, v_ in UP.items(): v_.index = utc(v_.index); UP[k_] = v_[~v_.index.duplicated()].sort_index().astype("float64")
    yaz(f"vadeli metrik: {len(MT)} coin · Upbit: {len(UP)} coin (BTC {'var' if 'BTC' in UP else 'YOK'})")
if KURU: yaz("# KURU TEST")
B = O.pop("BTC"); IX = pd.date_range(BAS, B.index[-1], freq="1h", tz="UTC").as_unit("ns"); NI = len(IX)
def zroll(x, w=720): return (x - x.rolling(w, min_periods=168).mean()) / (x.rolling(w, min_periods=168).std() + 1e-12)
nanS = pd.Series(np.nan, index=IX)
def hiz(s): return s.reindex(IX, method="ffill", tolerance=pd.Timedelta(hours=9)) if s is not None and len(s) else nanS
bc = np.log(B.close.reindex(IX).ffill(limit=3)); blr = bc.diff(); bsig = blr.rolling(720, min_periods=168).std()
BZ = {k: (bc - bc.shift(k)) / (bsig * np.sqrt(k)) for k in (1, 4, 24, 168)}
BFZ = {H: (bc.shift(-H) - bc) / (bsig * np.sqrt(H)) for H in HS}
bvolr = np.log(blr.rolling(24).std() / (bsig + 1e-12) + 1e-9)
bpz = PZ["BTC"].reindex(IX, method="ffill", tolerance=pd.Timedelta(hours=2)) if "BTC" in PZ else nanS
KA, KB, KC = (BZ[4] <= -1).values, (BZ[24] <= -1).values, (BZ[168] <= -1).values; ANY = KA | KB | KC
XP = {H: (BFZ[H] <= -1).values for H in HS}
yaz(f"\nKaranlık saat oranı (t anında bilinen): KA son 4 s %{KA.mean() * 100:.1f} · KB son 24 s %{KB.mean() * 100:.1f} · KC son 7 g %{KC.mean() * 100:.1f} · birleşim %{ANY.mean() * 100:.1f}")

# ---------------- coin özellikleri ----------------
FN = ["zr1", "zr4", "zr24", "zr168", "zrel4", "zrel24", "zrel168", "beta", "kor", "vz1", "vz24", "nz1", "tb1", "tb24", "ztb24", "volr", "dh30", "dl30", "dh90",
      "yas", "boy", "fz", "fr", "pz", "pzd24", "asp", "aspd24", "upv", "upv1", "ups", "oi4", "oi24", "lsz", "tlsz", "tkz"]
CSF = ["zr24", "zr168", "vz24", "zrel24"]; FALL = FN + [f"cs_{k}" for k in CSF]
AD = {"zr1": "son 1 s getiri z", "zr4": "son 4 s getiri z", "zr24": "son 24 s getiri z", "zr168": "son 7 g getiri z", "zrel4": "BTC'ye göre 4 s güç z", "zrel24": "BTC'ye göre 24 s güç z",
      "zrel168": "BTC'ye göre 7 g güç z", "beta": "BTC betası (30 g)", "kor": "BTC korelasyonu (30 g)", "vz1": "saatlik hacim z", "vz24": "24 s hacim z", "nz1": "işlem sayısı z",
      "tb1": "alıcı oranı (1 s)", "tb24": "alıcı oranı (24 s)", "ztb24": "alıcı oranı z (24 s)", "volr": "oynaklık oranı 24 s / 30 g", "dh30": "30 g zirveye uzaklık",
      "dl30": "30 g dibe uzaklık", "dh90": "90 g zirveye uzaklık", "yas": "coin yaşı", "boy": "işlem büyüklüğü (30 g)", "fz": "fonlama z", "fr": "fonlama oranı",
      "pz": "Coinbase prim z", "pzd24": "prim z 24 s değişim", "cs_zr24": "24 s getiri sırası (coin'ler arası)", "cs_zr168": "7 g getiri sırası", "cs_vz24": "hacim z sırası",
      "cs_zrel24": "BTC'ye göre güç sırası", "asp": "Kore primi z", "aspd24": "Kore primi 24 s değişim", "upv": "Kore 24 s hacim z", "upv1": "Kore saatlik hacim z", "ups": "Kore hacim payı z", "oi4": "açık pozisyon 4 s z", "oi24": "açık pozisyon 24 s z", "lsz": "tüm hesaplar long/short z", "tlsz": "büyük hesaplar long/short z", "tkz": "vadeli alıcı oranı z (24 s)"}
NM = sorted(O); NC = len(NM); NF = len(FALL)
FEAT = np.full((NC, NI, NF), np.nan, np.float32); Y = np.full((NC, NI, len(HS)), np.nan, np.float32)
W24 = {k: np.full((NC, NI), np.nan, np.float32) for k in ("fvz", "ftb", "fpzd", "ffr", "fmax", "fupv", "faspd", "foid", "flsd")}      # pencere İÇİ (yalnız betimleme, 24 s)
VAL = np.zeros((NC, NI), bool)
bm, bv = blr.rolling(720, min_periods=168).mean(), blr.rolling(720, min_periods=168).var(ddof=0)
for i, nm in enumerate(NM):
    o = O[nm].reindex(IX); cl = o.close.ffill(limit=3); c = np.log(cl); lr = c.diff(); sig = lr.rolling(720, min_periods=168).std()
    F = {}
    for k in (1, 4, 24, 168): F[f"zr{k}"] = (c - c.shift(k)) / (sig * np.sqrt(k))
    beta = ((lr * blr).rolling(720, min_periods=168).mean() - lr.rolling(720, min_periods=168).mean() * bm) / (bv + 1e-12)
    F["beta"], F["kor"] = beta, lr.rolling(720, min_periods=168).corr(blr)
    for k in (4, 24, 168): F[f"zrel{k}"] = ((c - c.shift(k)) - beta * (bc - bc.shift(k))) / (sig * np.sqrt(k))
    qv = o.qv; F["vz1"] = zroll(np.log(qv + 1)); F["vz24"] = zroll(np.log(qv.rolling(24).sum() + 1)); F["nz1"] = zroll(np.log(o.n + 1))
    F["tb1"] = o.tbq / (qv + 1e-9); tb24 = o.tbq.rolling(24).sum() / (qv.rolling(24).sum() + 1e-9); F["tb24"] = tb24; F["ztb24"] = zroll(tb24)
    F["volr"] = np.log(lr.rolling(24).std() / (sig + 1e-12) + 1e-9)
    F["dh30"] = c - c.rolling(720, min_periods=700).max(); F["dl30"] = c - c.rolling(720, min_periods=700).min(); F["dh90"] = c - c.rolling(2160, min_periods=2000).max()
    fv = cl.first_valid_index(); F["yas"] = pd.Series(np.log1p(np.clip((IX - fv).total_seconds() / 3600, 0, None)), index=IX).where(cl.notna())
    F["boy"] = np.log(qv.rolling(720, min_periods=168).mean() + 1)
    fr = hiz(FON.get(nm)); F["fr"] = fr; F["fz"] = (fr - fr.rolling(720, min_periods=240).mean()) / (fr.rolling(720, min_periods=240).std() + 1e-12)
    pz = PZ[nm].reindex(IX, method="ffill", tolerance=pd.Timedelta(hours=2)) if nm in PZ else nanS; F["pz"] = pz; F["pzd24"] = pz - pz.shift(24)
    if nm in UP and "BTC" in UP:
        d_ = UP[nm].reindex(IX); b_ = UP["BTC"].reindex(IX)
        rel = (np.log(d_.krw / b_.krw) - np.log(d_.usdt / b_.usdt)).ffill(limit=2); F["asp"] = zroll(rel); F["aspd24"] = F["asp"] - F["asp"].shift(24)
        kh = d_.krw_hacim.fillna(0); F["upv"] = zroll(np.log(kh.rolling(24, min_periods=20).sum() + 1)); F["upv1"] = zroll(np.log(kh + 1))
        usd = (kh * (d_.usdt / d_.krw)).rolling(24, min_periods=20).sum(); F["ups"] = zroll(usd / (usd + qv.rolling(24, min_periods=20).sum() + 1e-9))
        W24["fupv"][i] = F["upv1"][::-1].rolling(24, min_periods=12).max()[::-1].shift(-1).values; W24["faspd"][i] = (F["asp"].shift(-24) - F["asp"]).values
    else:
        for k in ("asp", "aspd24", "upv", "upv1", "ups"): F[k] = nanS
    if nm in MT:
        m_ = MT[nm].reindex(IX).ffill(limit=2); oi = np.log(m_.oi.where(m_.oi > 0))
        F["oi4"] = zroll(oi - oi.shift(4)); F["oi24"] = zroll(oi - oi.shift(24)); F["lsz"] = zroll(np.log(m_.ls.where(m_.ls > 0))); F["tlsz"] = zroll(np.log(m_.top_ls.where(m_.top_ls > 0)))
        F["tkz"] = zroll(np.log(m_.taker.where(m_.taker > 0).rolling(24, min_periods=12).mean()))
        W24["foid"][i] = (oi.shift(-24) - oi).values; W24["flsd"][i] = (np.log(m_.ls.where(m_.ls > 0)).shift(-24) - np.log(m_.ls.where(m_.ls > 0))).values
    else:
        for k in ("oi4", "oi24", "lsz", "tlsz", "tkz"): F[k] = nanS
    for j, k in enumerate(FN): FEAT[i, :, j] = F[k].values.astype(np.float32)
    for h, H in enumerate(HS): Y[i, :, h] = (np.exp(c.shift(-H) - c) - 1 - MAL).values.astype(np.float32)
    VAL[i] = (cl.notna() & sig.notna() & c.shift(-1).notna()).values
    rv = lambda s: s[::-1].rolling(24, min_periods=12).max()[::-1].shift(-1)
    W24["fvz"][i] = rv(F["vz1"]).values; W24["fmax"][i] = (np.exp(rv(c) - c) - 1).values
    W24["ftb"][i] = (o.tbq[::-1].rolling(24, min_periods=12).sum()[::-1].shift(-1) / (qv[::-1].rolling(24, min_periods=12).sum()[::-1].shift(-1) + 1e-9)).values
    W24["fpzd"][i] = (pz.shift(-24) - pz).values; W24["ffr"][i] = (fr.shift(-24) - fr).values
for j, k in enumerate(CSF):
    FEAT[:, :, len(FN) + j] = pd.DataFrame(FEAT[:, :, FN.index(k)].T).rank(axis=1, pct=True).values.T.astype(np.float32)
yaz(f"özellikler: {NC} coin × {NI:,} saat × {NF} özellik · {dk()}")

# ---------------- panel (karanlık ∪ sonradan BTC düşen saatler) ----------------
KEEP = ANY | XP[8] | XP[24]
ci, pos = np.nonzero(VAL & KEEP[None, :]); o_ = np.lexsort((pos, ci)); ci, pos = ci[o_], pos[o_]
X = FEAT[ci, pos]; YY = Y[ci, pos]; TT = IX[pos]; YR = TT.year.values
SEL = (TT >= pd.Timestamp("2022-03-01", tz="UTC")) & (TT < pd.Timestamp("2024-01-01", tz="UTC")); DVAL = (TT >= pd.Timestamp("2024-01-01", tz="UTC")) & (TT < pd.Timestamp("2026-01-01", tz="UTC")); D26 = TT >= pd.Timestamp("2026-01-01", tz="UTC")
SEL, DVAL, D26 = np.asarray(SEL), np.asarray(DVAL), np.asarray(D26)
yaz(f"panel satırı: {len(ci):,} · {dk()}"); kaydet()

# ================= (1) BETİMLEME =================
yaz("\n## 1. BTC sonradan düştüğünde coin'lerin ne kadarı yükseldi? (BTC ileri H saat z ≤ −1; isabet = maliyet sonrası > 0)\n```")
for h, H in enumerate(HS):
    m = XP[H][pos] & np.isfinite(YY[:, h]); s = []
    for y_ in range(2021, 2027):
        mm = m & (YR == y_)
        if mm.sum(): s.append(f"{y_} %{(YY[mm, h] > 0).mean() * 100:.0f}")
    big = m & (YY[:, h] >= 0.05)
    yaz(f"H={H:>2} s: BTC düşen pencere {len(np.unique(pos[m])):,} saat · coin yükselme oranı {' · '.join(s)} · ≥ +%5 yükselen coin-saat {big.sum():,} (%{big.sum() / max(m.sum(), 1) * 100:.1f})")
yaz("```\n_Normalde (tüm saatler) coin'lerin yarısı yükselir; BTC düşerken bu oran çok düşer — yükselenler azınlık._")
h24 = HS.index(24); m24 = XP[24][pos] & np.isfinite(YY[:, h24]); up = YY[:, h24] > 0
yaz("\n## 2. Yükselenler ÖNCEDEN (t anında) neye benziyordu? — BTC'nin sonradan 24 s düştüğü pencereler, özelliğin en düşük %10 / en yüksek %10 diliminde yükselme oranı")
yaz("Dilim eşikleri 2021–23'ten. Tutarlı = iki dönemde de aynı yön ve fark ≥ 3 puan.\n```")
yaz(f"{'özellik':<38}| 2022–23: genel  alt%10 üst%10 | 2024+: genel  alt%10 üst%10 | tutarlı")
OUT = []
for j, k in enumerate(FALL):
    x = X[:, j]; ms = m24 & SEL & np.isfinite(x)
    if ms.sum() < 500: continue
    lo, hi = np.nanpercentile(x[ms], [10, 90]); r = []
    for per in (SEL, DVAL | D26):
        mp = m24 & per & np.isfinite(x)
        g, a, b = up[mp].mean() * 100, up[mp & (x <= lo)].mean() * 100 if (mp & (x <= lo)).sum() else np.nan, up[mp & (x >= hi)].mean() * 100 if (mp & (x >= hi)).sum() else np.nan
        r.append((g, a, b))
    d1, d2 = r[0][2] - r[0][1], r[1][2] - r[1][1]; tut = "✅" if np.sign(d1) == np.sign(d2) and abs(d1) >= 3 and abs(d2) >= 3 else ""
    OUT.append((abs(d1), f"{AD.get(k, k)[:37]:<38}| %{r[0][0]:>4.0f}  %{r[0][1]:>5.0f} %{r[0][2]:>5.0f}  | %{r[1][0]:>4.0f}  %{r[1][1]:>5.0f} %{r[1][2]:>5.0f}  | {tut}"))
for _, s in sorted(OUT, reverse=True): yaz(s)
yaz("```")
yaz("\n## 3. Pencere İÇİNDE ne oldu? (BTC 24 s düşerken) — yükselen vs düşen coin'ler, medyan / oran\n```")
WC = {k: v[ci, pos] for k, v in W24.items()}
for ad, k in (("24 s içinde en yüksek saatlik hacim z", "fvz"), ("24 s alıcı oranı", "ftb"), ("Coinbase prim z değişimi", "fpzd"), ("fonlama değişimi", "ffr"), ("24 s içinde en yüksek KORE saatlik hacim z", "fupv"), ("Kore primi z değişimi", "faspd"), ("açık pozisyon değişimi (log)", "foid"), ("tüm hesaplar long/short değişimi (log)", "flsd")):
    a, b = WC[k][m24 & up], WC[k][m24 & ~up]
    yaz(f"{ad:<38}: yükselen {np.nanmedian(a):+.3f} · düşen {np.nanmedian(b):+.3f}")
for per, ad in ((SEL, "2022–23"), (DVAL | D26, "2024+")):
    for nm_, mk in (("yükselen", up), ("düşen", ~up)):
        mm = m24 & per & mk; v = WC["fvz"][mm]
        yaz(f"{ad} {nm_:<9}: pencerede hacim patlaması (z ≥ 3) %{np.nanmean(v >= 3) * 100:.0f} · ≥ +%5 olan %{(YY[mm, h24] >= .05).mean() * 100:.1f}")
big = m24 & (YY[:, h24] >= 0.05)
yaz(f"≥ +%5 yükselenler: Kore hacim patlaması (z ≥ 3) %{np.nanmean(WC['fupv'][big] >= 3) * 100:.0f} (Upbit'te olanlar arasında: %{100 * np.nanmean(WC['fupv'][big & np.isfinite(WC['fupv'])] >= 3):.0f}) · düşenlerde %{100 * np.nanmean(WC['fupv'][m24 & ~up & np.isfinite(WC['fupv'])] >= 3):.0f}")
yaz(f"≥ +%5 yükselenler: açık pozisyon artışı medyan {np.nanmedian(WC['foid'][big]):+.3f} · düşenlerde {np.nanmedian(WC['foid'][m24 & ~up]):+.3f} · Kore primi değişimi {np.nanmedian(WC['faspd'][big]):+.2f} · düşenlerde {np.nanmedian(WC['faspd'][m24 & ~up]):+.2f}")
yaz(f"≥ +%5 yükselenler ({big.sum():,}): hacim patlaması %{np.nanmean(WC['fvz'][big] >= 3) * 100:.0f} · alıcı oranı medyan {np.nanmedian(WC['ftb'][big]):.3f} · prim z değişimi medyan {np.nanmedian(WC['fpzd'][big]):+.2f}")
yaz("```")
yaz("\n## 4. Aynı coin'ler tekrar ediyor mu? (BTC 24 s düşerken coin'in yükselme oranı, 2022–23 → 2024+)\n```")
rs = pd.DataFrame({"nm": np.array(NM)[ci[m24]], "per": np.where(SEL[m24], "a", np.where((DVAL | D26)[m24], "b", "x")), "up": up[m24]})
tb = rs[rs.per != "x"].groupby(["nm", "per"]).up.agg(["mean", "size"]).unstack("per"); tb = tb[(tb["size"]["a"] >= 300) & (tb["size"]["b"] >= 300)]
if len(tb) > 5:
    ra = tb["mean"]["a"]; rb = tb["mean"]["b"]
    yaz(f"{len(tb)} coin · sıra korelasyonu (Spearman) {ra.corr(rb, method='spearman'):+.2f}")
    top = ra.sort_values(ascending=False).head(12)
    yaz("2022–23'te en dirençli 12 coin → 2024+:"); [yaz(f"  {k:<8} %{ra[k] * 100:.0f} → %{rb[k] * 100:.0f}") for k in top.index]
    yaz(f"  (2024+ tüm coin ortalaması %{rb.mean() * 100:.0f}; bu 12'nin ortalaması %{rb[top.index].mean() * 100:.0f})")
yaz("```"); kaydet(); yaz(f"betimleme bitti · {dk()}")

# ================= (2) KURALLAR =================
REG = {"KA": KA, "KB": KB, "KC": KC}; RAD = {"KA": "BTC son 4 s düştü", "KB": "BTC son 24 s düştü", "KC": "BTC son 7 g düştü"}
def tekil(m, H):
    idx = np.flatnonzero(m); out = []; lc, lp = -1, -10**9
    for i, c_, p_ in zip(idx, ci[idx], pos[idx]):
        if c_ != lc or p_ - lp >= H: out.append(i); lc, lp = c_, p_
    return np.array(out, int)
def ist(ev, h, per):
    e = ev[per[ev]]
    if len(e) == 0: return dict(n=0, hit=np.nan, net=np.nan, saat=np.nan, alt=np.nan, gun=np.nan, ng=0)
    v = YY[e, h]; s = pd.Series(v).groupby(pos[e]).mean()
    g = pd.Series(v).groupby(np.asarray(TT[e].floor("D"))).mean()
    return dict(n=len(e), hit=(v > 0).mean() * 100, net=v.mean() * 100, saat=(s > 0).mean() * 100, ns=len(s), gun=(g > 0).mean() * 100, ng=len(g), e=e)
def calistir(XX, plas=False):
    res = []
    for r, RM in REG.items():
        rm = RM[pos]
        for h, H in enumerate(HS):
            base = rm & np.isfinite(YY[:, h]); bs = base & SEL; tek = []
            for j, k in enumerate(FALL):
                x = XX[:, j]; ok = bs & np.isfinite(x)
                if ok.sum() < 2000: continue
                lo, hi = np.nanpercentile(x[ok], [10, 90])
                for yon, mk in (("≤", x <= lo), ("≥", x >= hi)):
                    m = base & mk; ev = tekil(m, H); s = ist(ev, h, SEL)
                    if s["n"] >= 150 and s["hit"] >= 58 and s["net"] > 0: tek.append((s["hit"], f"{AD[k]} {yon} {lo if yon == '≤' else hi:.3g}", m, ev))
            tek.sort(key=lambda z: -z[0]); C = [(a, b, ev) for a, b, m, ev in tek]
            for a in range(min(8, len(tek))):
                for b in range(a + 1, min(8, len(tek))):
                    if tek[a][1].split(" ≤ ")[0].split(" ≥ ")[0] == tek[b][1].split(" ≤ ")[0].split(" ≥ ")[0]: continue
                    m = tek[a][2] & tek[b][2]; ev = tekil(m, H); s = ist(ev, h, SEL)
                    if s["n"] >= 100 and s["hit"] >= 60 and s["net"] > 0: C.append((s["hit"], tek[a][1] + " + " + tek[b][1], ev))
            J = {k: XX[:, FALL.index(k)] for k in ("zrel4", "upv1", "asp", "fz", "oi24", "zr4", "vz1", "tb1")}
            with np.errstate(invalid="ignore"):
                ER = {"E1 kopuş + Kore hacim patlaması": (J["zrel4"] >= 1.5) & (J["upv1"] >= 3), "E2 kopuş + Kore primi": (J["zrel4"] >= 1.5) & (J["asp"] >= 1.5),
                      "E3 short sıkışması": (J["fz"] <= -1.5) & (J["oi24"] >= 1) & (J["zr4"] >= 1), "E4 hacimli kopuş": (J["vz1"] >= 3) & (J["zrel4"] >= 2) & (J["tb1"] >= 0.6)}
            for ad_, mk_ in ER.items(): C.append((0, ad_, tekil(base & mk_, H)))
            for _, ad, ev in C:
                a, b, c = ist(ev, h, SEL), ist(ev, h, DVAL), ist(ev, h, D26)
                alt = wboot(YY[b["e"], h], TT[b["e"]], reps=300)[0] if b["n"] >= 40 and not plas else (0.001 if b["n"] >= 40 else np.nan)
                gec = (b["n"] >= 40 and c["n"] >= 10 and b["hit"] >= 65 and c["hit"] >= 65 and b["net"] > 0 and c["net"] > 0 and b["saat"] >= 65 and c["saat"] >= 65 and b["gun"] >= 65 and c["gun"] >= 65)
                if gec and plas is False: gec = gec and alt > 0
                res.append(dict(rej=r, H=H, kural=ad, a=a, b=b, c=c, alt=alt, gec=gec))
    return res
R0 = calistir(X); G0 = [r for r in R0 if r["gec"]]
yaz(f"\n## 5. Kurallar (t anında bilinen karanlık durum) — seçimden geçen aday {len(R0)} · üç şartı da geçen {len(G0)} · {dk()}")
def satir(r):
    f = lambda s: f"{s['n']:>5} %{s['hit']:>4.0f} {s['net']:+.2f} saat%{s['saat']:>3.0f} gün%{s['gun']:>3.0f}" if s["n"] else f"{0:>5}  —"
    return f"{'✅' if r['gec'] else '  '} {r['rej']} {r['H']:>2}s {r['kural'][:70]:<70}| {f(r['a'])} | {f(r['b'])} | {f(r['c'])}"
yaz("```\n   durum H  kural                                                                 | seçim 2022–23: n isabet net saat gün | doğrulama 2024–25 | 2026")
for r in sorted(R0, key=lambda r: -(r["b"]["hit"] if r["b"]["n"] >= 40 else 0))[:40]: yaz(satir(r))
yaz("```\n\nÖnceden sabit erken yakalama kuralları (E1–E4):\n```")
for r in [r for r in R0 if r["kural"].startswith("E")]: yaz(satir(r))
yaz("```"); kaydet()
rg = np.random.default_rng(7); PL = []
for k in range(0 if KURU else 20):
    s_ = rg.integers(72, 2001, NC); pp = pos - s_[ci]; XP_ = np.where((pp >= 0)[:, None], FEAT[ci, np.clip(pp, 0, None)], np.nan).astype(np.float32)
    PL.append(sum(r["gec"] for r in calistir(XP_, plas=True))); print(f"plasebo {k + 1}: {PL[-1]} · {dk()}", flush=True); del XP_
if PL:
    p95 = np.percentile(PL, 95); yaz(f"\nPlasebo (20 kaydırma) geçen kural sayısı: ortalama {np.mean(PL):.1f} · %95 {p95:.1f} · gerçek {len(G0)} → "
                                   + ("✅ gerçek plasebodan büyük" if len(G0) > p95 else "❌ plasebodan ayırt edilemiyor — kural önerilmez"))
kaydet()

yaz(f"\nBitti · {dk()}"); kaydet()
