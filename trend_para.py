# trend_para.py — PARA TESTİ: BTC trend/momentum kuralı (yukselis.py bulgusu) · canlı sisteme dokunmaz
# Kurallar ÖNCEDEN sabit; eşikler yalnız 2017–23'ten (seçim dönemi) · karar 2024+.
#   A: ema720 üst %10 — fiyat 30 günlük üstel ortalamanın en çok üstünde olduğu %10'luk dilim
#   B: r168 üst %10   — son 7 günün en güçlü %10'luk yükselişi
#   C: A ve B birlikte · D: A veya B
#   Karşılaştırma: ⭐ (mevcut BTC sinyali) · ⭐ + D · koşulsuz her 8 saatte al (taban) · al-tut
# İki tutma biçimi: "8 saat tut" (olay 8 saat tekrar sayılmaz) ve "koşul sürdükçe tut" (koşulun bozulduğu ilk saat kapanışında çık).
# Giriş/çıkış: saat kapanışı (0 dk) ve mesajın geldiği an (6 dk) — dakikalık Binance fiyatı. Komisyon her yön: spot %0,10 · BNB %0,075 · vadeli %0,05 · limit %0,02.
import os, glob, time, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
def kl(sym="BTCUSDT"):
    end = int(time.time() * 1000); rows = []
    for url in EP:
        try:
            rows, cur = [], int(pd.Timestamp("2017-08-17", tz="UTC").timestamp() * 1000)
            while cur < end:
                r = requests.get(url, params=dict(symbol=sym, interval="1h", startTime=cur, endTime=end, limit=1000), timeout=20); r.raise_for_status(); dt = r.json()
                if not dt: break
                rows += dt; cur = dt[-1][0] + 3_600_000
                if len(dt) < 1000: break
            if rows: break
        except Exception: rows = []
    d = pd.DataFrame([x[:6] for x in rows], columns=["t", "open", "high", "low", "close", "volume"]).astype(float)
    d.index = pd.to_datetime(d.t, unit="ms", utc=True) + pd.Timedelta(hours=1); d = d[d.index <= pd.Timestamp.now(tz="UTC")]
    return d[~d.index.duplicated()].sort_index()[["open", "high", "low", "close", "volume"]]
YEREL = bool(os.environ.get("YEREL"))
B = pd.read_pickle("/home/claude/lab2/data/o_1h.pkl") if YEREL else kl()
F = features(B); C = B.close; LAST = F.index[-1]
A24 = pd.Timestamp("2024-01-01", tz="UTC"); BAS = F.index[720]
sel = (F.index >= BAS) & (F.index < A24); okF = pd.Series(F.index >= BAS, index=F.index)
qE, qR = F.ema720[sel].quantile(0.9), F.r168[sel].quantile(0.9)
mA = (F.ema720 >= qE) & okF; mB = (F.r168 >= qR) & okF
KUR = {"A · ema720 üst %10": mA, "B · r168 üst %10": mB, "C · A ve B": mA & mB, "D · A veya B": mA | mB}
BASL = {k: BAS for k in KUR}
KAR = {"Taban · koşulsuz her 8 saatte al-sat": okF}; BASL[list(KAR)[0]] = BAS
EXP = glob.glob("art/**/disa_BTCUSDT.pkl", recursive=True)
if EXP:
    X = pd.read_pickle(EXP[0]); ST = X.star.reindex(F.index).fillna(False).astype(bool)
    KAR["⭐ (mevcut sinyal)"] = ST; KAR["⭐ + D (trend de varken)"] = ST & (mA | mB)
    BASL["⭐ (mevcut sinyal)"] = BASL["⭐ + D (trend de varken)"] = max(BAS, X.index[0])
yaz(f"# 📈 BTC trend kuralı — para testi — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}")
yaz(f"Veri: {F.index[0]:%Y-%m-%d} → {LAST:%Y-%m-%d %H:%M} UTC · seçim (eşikler) {BAS:%Y-%m} → 2023-12 · karar 2024-01 → bugün")
yaz(f"Eşikler (yalnız seçim döneminden): ema720 ≥ {100*qE:.2f}% (fiyat 30g ortalamanın bu kadar üstünde) · r168 ≥ {100*(np.exp(qR)-1):.2f}% (7 günlük yükseliş)\n")
# ---- işlemler ----
H8 = pd.Timedelta(hours=8)
def islem_8(m):
    m = (m & pd.Series(F.index <= LAST - H8, index=F.index)).values
    return [(F.index[i], F.index[i] + H8) for i in events(m, 8)]
def islem_rejim(m):
    v = m.values; out = []; i = 0; n = len(v)
    while i < n:
        if v[i]:
            j = i + 1
            while j < n and v[j]: j += 1
            if j < n: out.append((F.index[i], F.index[j]))                       # j: koşulun bozulduğu ilk saat kapanışı
            i = j
        else: i += 1
    return out
TR = {}
for k, m in {**KUR, **KAR}.items(): TR[("8 saat tut", k)] = islem_8(m)
for k, m in KUR.items(): TR[("koşul sürdükçe tut", k)] = islem_rejim(m)
# ---- dakikalık fiyatlar (yalnız gereken dakikalar) ----
NEED = sorted({t + pd.Timedelta(minutes=d) for v in TR.values() for a, b in v for t in (a, b) for d in (0, 6)}); NI = pd.DatetimeIndex(NEED)
cur_m = pd.Timestamp.now(tz="UTC").normalize().replace(day=1)
def ay(ym):
    a = pd.Timestamp(ym + "-01", tz="UTC"); b = a + pd.offsets.MonthBegin(1)
    if YEREL: s = ay.M
    else:
        z = _mzip(ym, "BTCUSDT") if a < cur_m else None
        if z is not None: s = to_min(z).close
        else: m = fetch_1m(a.timestamp() * 1000, min(b, pd.Timestamp.now(tz="UTC")).timestamp() * 1000, sym="BTCUSDT"); s = m.close if m is not None else None
    if s is None: return None
    return s[(s.index >= a) & (s.index <= b) & s.index.isin(NI)]
if YEREL: ay.M = pd.read_pickle("/home/claude/lab2/data/m_1m.pkl").close
with ThreadPoolExecutor(1 if YEREL else 12) as ex: parts = [p for p in ex.map(ay, sorted({t.strftime("%Y-%m") for t in NEED})) if p is not None]
PX = pd.concat(parts); PX = PX[~PX.index.duplicated()].sort_index()
yaz(f"Dakikalık fiyat: {len(PX)}/{len(NEED)} dakika bulundu (eksik %{100*(1-len(PX)/len(NEED)):.2f}) · {time.time()-T0:.0f} sn\n")
# ---- özet ----
FEES = {"spot %0,10": 0.0010, "BNB %0,075": 0.00075, "vadeli %0,05": 0.0005, "limit %0,02": 0.0002}
SEC = f"{BAS.year}–23 (seçim)"; DON = {SEC: (BAS, A24), "2024+ (karar)": (A24, LAST)}
def tablo(mod, k, d):
    rows = []
    for a, b in TR[(mod, k)]:
        pa, pb = PX.get(a + pd.Timedelta(minutes=d), np.nan), PX.get(b + pd.Timedelta(minutes=d), np.nan)
        if np.isfinite(pa) and np.isfinite(pb): rows.append((a, b, pb / pa - 1))
    return pd.DataFrame(rows, columns=["t", "c", "g"])
def alt_ust(x):
    lo, hi = wboot(x.g.values, x.t.values); return lo, hi
S = []; YIL = []
for d in (0, 6):
    for (mod, k) in TR:
        T = tablo(mod, k, d)
        for pn, (a, b) in DON.items():
            a = max(a, BASL[k]); x = T[(T.t >= a) & (T.t < b)]
            if len(x) < 10: continue
            wk = (b - a).days / 7; yrs = (b - a).days / 365.25; lo, hi = alt_ust(x); r = dict(gecikme=d, mod=mod, kural=k, donem=pn, islem=len(x), haftada=len(x) / wk,
                 isabet=100 * (x.g > 0).mean(), brut=100 * x.g.mean(), piyasada=100 * ((x.c - x.t).sum() / (b - a)))
            for fn, fee in FEES.items():
                net = x.g.values - 2 * fee; eq = np.cumprod(1 + net)
                r[f"net {fn}"] = 100 * net.mean(); r[f"yıllık {fn}"] = 100 * (eq[-1] ** (1 / yrs) - 1); r[f"maxDD {fn}"] = 100 * (eq / np.maximum.accumulate(np.r_[1, eq])[1:] - 1).min()
                r[f"alt {fn}"], r[f"üst {fn}"] = 100 * (lo - 2 * fee), 100 * (hi - 2 * fee)
            S.append(r)
            if d == 6:
                for y, g in x.groupby(x.t.dt.year): YIL.append(dict(mod=mod, kural=k, yil=y, getiri=100 * (np.prod(1 + g.g.values - 2 * 0.0005) - 1), islem=len(g)))
S = pd.DataFrame(S); Y = pd.DataFrame(YIL).drop_duplicates(["mod", "kural", "yil"])
# al-tut
AT = {}
for pn, (a, b) in DON.items():
    c = C[(C.index >= a) & (C.index <= b)]; yrs = (c.index[-1] - c.index[0]).days / 365.25
    AT[pn] = dict(yillik=100 * ((c.iloc[-1] / c.iloc[0]) ** (1 / yrs) - 1), maxdd=100 * (c / c.cummax() - 1).min())
for d in (6, 0):
    yaz(f"## {'Gerçekçi: mesaj :06’da gelir, giriş-çıkış o dakika (6 dk)' if d == 6 else 'İyimser: saat kapanışında giriş-çıkış (0 dk)'}")
    for pn in DON:
        x = S[(S.gecikme == d) & (S.donem == pn)].copy(); x["ad"] = x["mod"].str.slice(0, 6) + " · " + x.kural
        tb = x.set_index("ad")[["islem", "haftada", "isabet", "brut", "piyasada", "net spot %0,10", "net BNB %0,075", "net vadeli %0,05", "net limit %0,02",
                                "alt vadeli %0,05", "üst vadeli %0,05", "yıllık BNB %0,075", "yıllık vadeli %0,05", "maxDD vadeli %0,05"]]
        tb.columns = ["işlem", "haftada", "isabet%", "brüt%", "piyasada%", "net spot", "net BNB", "net vadeli", "net limit", "vadeli alt", "vadeli üst", "yıllık% BNB", "yıllık% vadeli", "maxDD% vadeli"]
        yaz(f"\n### {pn} · al-tut: yıllık %{AT[pn]['yillik']:.1f}, maxDD %{AT[pn]['maxdd']:.1f}\n```\n" + tb.round(3).to_string() + "\n```")
    yaz("")
yaz("## Yıl yıl getiri (6 dk, vadeli %0,05, bileşik %) — al-tut ile karşılaştırma")
Y["ad"] = Y["mod"].str.slice(0, 6) + " · " + Y.kural; P = Y.pivot_table(index="ad", columns="yil", values="getiri")
AY = {y: 100 * (C[C.index.year == y].iloc[-1] / C[C.index.year == y].iloc[0] - 1) for y in P.columns if (C.index.year == y).any()}
P.loc["AL-TUT (BTC)"] = pd.Series(AY); yaz("```\n" + P.round(1).to_string() + "\n```")
# ---- otomatik karar (önceden sabit) ----
yaz("\n## Karar (6 dk gecikme · önceden sabit ölçüt)")
yaz("Ölçüt: iki dönemde de BNB-komisyonlu net > 0 · 2024+ vadeli net alt sınır > 0 · 2024+ brüt, tabandan (koşulsuz al) yüksek · 2024+ yıllık (vadeli) al-tut'tan yüksek ya da maxDD'si belirgin küçük")
for (mod, k) in TR:
    if k.startswith("Taban"): continue
    x = S[(S.gecikme == 6) & (S["mod"] == mod) & (S.kural == k)].set_index("donem")
    if "2024+ (karar)" not in x.index or SEC not in x.index: continue
    s1, s2 = x.loc[SEC], x.loc["2024+ (karar)"]; tb_ = S[(S.gecikme == 6) & S.kural.str.startswith("Taban") & (S.donem == "2024+ (karar)")].brut.iloc[0]
    c1 = s1["net BNB %0,075"] > 0 and s2["net BNB %0,075"] > 0; c2 = s2["alt vadeli %0,05"] > 0; c3 = s2.brut > tb_
    c4 = s2["yıllık vadeli %0,05"] > AT["2024+ (karar)"]["yillik"] or s2["maxDD vadeli %0,05"] > 0.6 * AT["2024+ (karar)"]["maxdd"]
    ok = c1 and c2 and c3 and c4
    yaz(f"- {'✅' if ok else '❌'} {mod} · {k}: net>0 iki dönem {'✓' if c1 else '✗'} · güven alt>0 {'✓' if c2 else '✗'} · tabandan iyi {'✓' if c3 else '✗'} · al-tut'a göre {'✓' if c4 else '✗'} "
        f"(2024+: {s2.islem:.0f} işlem, haftada {s2.haftada:.1f}, isabet %{s2['isabet']:.0f}, net vadeli %{s2['net vadeli %0,05']:.3f}, yıllık %{s2['yıllık vadeli %0,05']:.0f}, maxDD %{s2['maxDD vadeli %0,05']:.0f})")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn · brüt/net = işlem başı ortalama % · alt/üst = haftalık blok bootstrap %90 aralığı · piyasada = zamanın yüzde kaçı pozisyonda_")
open("trend_para_sonuc.md", "w").write("\n".join(L) + "\n")
