# vadeli.py — PROTOKOL_vadeli.md (Ek 1 dahil): Binance vadeli arşivinden saatlik özellikler → A) mevcut sinyallere filtre · B) N1–N4 yeni sinyal. Kod sonuçtan önce kaydedildi.
import io, os, json, time, zipfile, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
T0 = time.time(); A = "https://data.binance.vision/data/futures/um"; S = requests.Session()
L = []; yaz = lambda s="": (print(s, flush=True), L.append(s))
COINS = sorted({l.strip()[:-4] for f in ("canli/durum/genis_liste.txt", "canli/durum/coin_listesi.txt") for l in open(f) if l.strip()})
GUN = pd.date_range("2022-01-01", pd.Timestamp.now(tz="UTC").normalize() - pd.Timedelta(days=2), freq="D")
def al(url):
    for k in range(4):
        try:
            r = S.get(url, timeout=30)
            if r.status_code == 404: return None
            if r.status_code == 200: return r.content
        except Exception: pass
        time.sleep(1 + 2 * k)
    return None
def metrik(arg):
    c, g = arg; b = al(f"{A}/daily/metrics/{c}USDT/{c}USDT-metrics-{g:%Y-%m-%d}.zip")
    if b is None: return None
    try:
        z = zipfile.ZipFile(io.BytesIO(b)); d = pd.read_csv(z.open(z.namelist()[0]))
        return c, d[["create_time", "sum_open_interest", "count_long_short_ratio", "sum_toptrader_long_short_ratio", "sum_taker_long_short_vol_ratio"]]
    except Exception: return None
var = [c for c in COINS if al(f"{A}/daily/metrics/{c}USDT/{c}USDT-metrics-{GUN[-1]:%Y-%m-%d}.zip") is not None]
yaz(f"arşivde metrics olan coin: {len(var)} / {len(COINS)}")
P = {}
with ThreadPoolExecutor(32) as ex:
    for n_, r in enumerate(ex.map(metrik, [(c, g) for c in var for g in GUN])):
        if r: P.setdefault(r[0], []).append(r[1])
        if n_ % 20000 == 0: print(f"metrics {n_:,} · {time.time() - T0:.0f} sn", flush=True)
def fon(c):
    out = []
    for m in pd.date_range("2022-01-01", pd.Timestamp.now(tz="UTC"), freq="MS"):
        b = al(f"{A}/monthly/fundingRate/{c}USDT/{c}USDT-fundingRate-{m:%Y-%m}.zip")
        if b is None: continue
        try: z = zipfile.ZipFile(io.BytesIO(b)); out.append(pd.read_csv(z.open(z.namelist()[0])))
        except Exception: pass
    if not out: return c, None
    d = pd.concat(out); s = pd.Series(d.last_funding_rate.values.astype(float), index=pd.to_datetime(d.calc_time.astype("int64"), unit="ms", utc=True)).sort_index()
    s = s[~s.index.duplicated()]; return c, (s - s.rolling(90, min_periods=30).mean()) / (s.rolling(90, min_periods=30).std() + 1e-12)
with ThreadPoolExecutor(16) as ex: FR = {c: v for c, v in ex.map(fon, var) if v is not None}
def kl(c):
    out, cur, son = [], int(pd.Timestamp("2021-11-01", tz="UTC").timestamp() * 1000), int(time.time() * 1000)
    while cur < son:
        try: x = S.get("https://data-api.binance.vision/api/v3/klines", params=dict(symbol=f"{c}USDT", interval="1h", startTime=cur, limit=1000), timeout=20).json()
        except Exception: x = None
        if not isinstance(x, list) or not x: break
        out += x; cur = x[-1][0] + 3_600_000
        if len(x) < 1000: break
    if not out: return c, None
    d = pd.Series([float(r[4]) for r in out], index=pd.to_datetime([r[0] for r in out], unit="ms", utc=True) + pd.Timedelta(hours=1)); return c, d[~d.index.duplicated()]
with ThreadPoolExecutor(12) as ex: PX = {c: v for c, v in ex.map(kl, var) if v is not None}
yaz(f"indirme bitti: metrics {len(P)} coin · fonlama {len(FR)} · fiyat {len(PX)} · {time.time() - T0:.0f} sn")
z_ = lambda x: (x - x.rolling(720, min_periods=168).mean()) / (x.rolling(720, min_periods=168).std() + 1e-12)
F = {}
for c, parca in P.items():
    d = pd.concat(parca); d["t"] = pd.to_datetime(d.create_time, utc=True); d = d.drop_duplicates("t").set_index("t").sort_index()
    rs = lambda s, f: getattr(s.resample("1h", label="right", closed="right"), f)()
    oi = np.log(rs(d.sum_open_interest.astype(float), "last")); tk = np.log(d.sum_taker_long_short_vol_ratio.astype(float).clip(lower=1e-6))
    H = pd.DataFrame({"doi1": z_(oi.diff(1)), "doi4": z_(oi.diff(4)), "doi24": z_(oi.diff(24)),
                      "tk1": z_(rs(tk, "mean")), "tk4": z_(rs(tk, "mean").rolling(4).mean()),
                      "gls": z_(np.log(rs(d.count_long_short_ratio.astype(float), "last"))), "tls": z_(np.log(rs(d.sum_toptrader_long_short_ratio.astype(float), "last")))})
    if c in FR: H["fr"] = FR[c].reindex(H.index, method="ffill")
    else: H["fr"] = np.nan
    F[c] = H
OZ = ["doi1", "doi4", "doi24", "tk1", "tk4", "gls", "tls", "fr"]
# ======================= A) mevcut sinyallere filtre =======================
V = pd.read_csv("veri_seti.csv.gz"); V["t"] = pd.to_datetime(V.t, utc=True)
D = pd.read_csv("karal2_veri.csv.gz"); D["t"] = pd.to_datetime(D.t, utc=True)
X = D[["t", "nm", "sinif", "H", "B_T0"]].dropna(subset=["B_T0"]).copy()
for o in OZ: X[o] = np.nan
for c, g in X.groupby("nm"):
    if c in F: X.loc[g.index, OZ] = F[c].reindex(pd.DatetimeIndex(g.t))[OZ].values
X = X.dropna(subset=OZ, how="any")
A25, A26, Y2, K0 = (pd.Timestamp(x, tz="UTC") for x in ("2025-01-01", "2026-01-01", "2023-07-01", "2022-01-01"))
SON = X.t.max() + pd.Timedelta(hours=1)
def olc(d):
    if len(d) == 0: return dict(n=0, ii=np.nan, si=np.nan, net=np.nan)
    sp = d.groupby("t").B_T0.mean(); return dict(n=len(d), ii=100 * (d.B_T0 > 0).mean(), si=100 * (sp > 0).mean(), net=100 * d.B_T0.mean())
def sart(o, b): return o["n"] >= 0.4 * b["n"] and o["ii"] >= b["ii"] and o["si"] >= b["si"] - 0.5 and o["net"] >= b["net"] + 0.05
yaz(f"\n# 📈 Vadeli piyasa verisi — PROTOKOL_vadeli.md · {pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M}")
yaz(f"_Özelliği olan sinyal: {len(X):,} · giriş B (mesaj fiyatına limit), vadeli ücret + fonlama, şimdiki 🎯 · ii işlem isabeti · si saat isabeti · net işlem başı %_\n")
yaz("## A) Mevcut sinyallere filtre"); SEC = {}
for sn in ["✅ ana (+0,75σ)", "🔸 yedek (+0,50σ)", "📋 panelden (+0,45σ)"]:
    d = X[X.sinif == sn]; k = d[d.t < A25]; h1, h2 = k[k.t < Y2], k[k.t >= Y2]; b1, b2 = olc(h1), olc(h2)
    yaz(f"### {sn} — keşif tabanı: ½-1 n {b1['n']} · ii %{b1['ii']:.1f} · si %{b1['si']:.1f} · net {b1['net']:+.3f} | ½-2 n {b2['n']} · %{b2['ii']:.1f} · %{b2['si']:.1f} · {b2['net']:+.3f}")
    gec = []
    for o in OZ:
        q1, q2 = k[o].quantile([1 / 3, 2 / 3]).values
        for ad, f in ((f"{o} alt⅓", lambda x: x <= q1), (f"{o} üst⅓", lambda x: x > q2), (f"{o} alt⅓'ü at", lambda x: x > q1), (f"{o} üst⅓'ü at", lambda x: x <= q2)):
            o1, o2 = olc(h1[f(h1[o])]), olc(h2[f(h2[o])])
            if sart(o1, b1) and sart(o2, b2): gec.append(((o1["net"] * o1["n"] + o2["net"] * o2["n"]) / (o1["n"] + o2["n"]), ad, o, (q1, q2), o1, o2))
    yaz(f"Keşif şartını geçen filtre: {len(gec)} / 32")
    for g_ in sorted(gec, reverse=True)[:5]: yaz(f"- {g_[1]} (eşik {g_[3][0]:.2f} / {g_[3][1]:.2f}): ½-1 n {g_[4]['n']} · %{g_[4]['ii']:.1f} · %{g_[4]['si']:.1f} · {g_[4]['net']:+.3f} | ½-2 n {g_[5]['n']} · %{g_[5]['ii']:.1f} · %{g_[5]['si']:.1f} · {g_[5]['net']:+.3f}")
    if gec:
        en = max(gec); SEC[sn] = dict(ad=en[1], oz=en[2], q=list(en[3]))
        o, (q1, q2) = en[2], en[3]; f = {"alt⅓": lambda x: x <= q1, "üst⅓": lambda x: x > q2, "alt⅓'ü at": lambda x: x > q1, "üst⅓'ü at": lambda x: x <= q2}[en[1].split(" ", 1)[1]]
        for dn, a in (("2025+", A25), ("2026", A26)):
            kk = d[d.t >= a]; b, r = olc(kk), olc(kk[f(kk[o])])
            yaz(f"**KONTROL {dn}** {en[1]}: n {r['n']} · ii %{r['ii']:.1f} · si %{r['si']:.1f} · net {r['net']:+.3f} | taban n {b['n']} · %{b['ii']:.1f} · %{b['si']:.1f} · {b['net']:+.3f} → {'✅' if sart(r, b) else '❌'}")
    else: yaz("**Kontrole giden yok.**")
# ======================= B) N1–N4 =======================
yaz("\n## B) Yeni sinyal adayları (uzun) — giriş kapanış + %0,10 ceza, ücret %0,05 + %0,05 + fonlama")
KUR = {"N1 hırslı alım": (4, lambda h, c: (h.tk1 >= 2) & (h.doi1 >= 2)), "N2 kaldıraç temizliği": (24, lambda h, c: (h.doi24 <= -2) & (np.log(c / c.shift(24)) <= -np.log(c).diff().rolling(720, min_periods=168).std() * np.sqrt(24))),
       "N3 kalabalık kısa": (24, lambda h, c: h.gls <= -2), "N4 büyük oyuncu uzun": (24, lambda h, c: h.tls >= 2)}
for ad, (Hh, kos) in KUR.items():
    R = []
    for c, h in F.items():
        px = PX.get(c)
        if px is None: continue
        px = px.reindex(h.index.union(px.index)).sort_index(); h2 = h.reindex(px.index)
        net = (px.shift(-Hh) / px / 1.001 - 1 - 0.001 - 0.0001 * Hh / 8)
        m = kos(h2, px).fillna(False).values; idx = []; son_ = -10**9
        for i in np.where(m)[0]:
            if i - son_ >= Hh: idx.append(i); son_ = i
        if not idx: continue
        ay = pd.Series(net.values, index=px.index).groupby(px.index.to_period("M")).mean()
        ev = pd.DataFrame({"t": px.index[idx], "net": net.values[idx]}); ev["plc"] = ay.reindex(ev.t.dt.to_period("M")).values; R.append(ev.dropna())
    E = pd.concat(R) if R else pd.DataFrame(columns=["t", "net", "plc"])
    sat = []; ok = True
    for dn, a, b in (("keşif ½-1", K0, Y2), ("keşif ½-2", Y2, A25), ("KONTROL 2025+", A25, SON), ("KONTROL 2026", A26, SON)):
        e = E[(E.t >= a) & (E.t < b)]; hf = len(e) / max(1, (b - a).days / 7)
        n_ = 100 * e.net.mean() if len(e) else np.nan; p_ = 100 * e.plc.mean() if len(e) else np.nan
        g = len(e) > 0 and n_ > 0.15 and n_ - p_ >= 0.15 and hf >= 2; ok &= g
        sat.append(f"{dn}: {len(e)} olay ({hf:.1f}/hf) · isabet %{100 * (e.net > 0).mean() if len(e) else float('nan'):.0f} · net {n_:+.2f} · plasebo {p_:+.2f} {'✅' if g else '❌'}")
    yaz(f"- **{ad}** ({Hh} s): " + " | ".join(sat) + f" → {'**GEÇTİ**' if ok else 'geçmedi'}")
yaz(f"\n_Süre {time.time() - T0:.0f} sn · 100 deneme (96 filtre + 4 yeni sinyal)._")
json.dump(SEC, open("vadeli_secim.json", "w"), ensure_ascii=False)
open("vadeli_sonuc.md", "w").write("\n".join(L) + "\n")
pd.concat({c: h for c, h in F.items()}, names=["nm", "t"]).to_parquet("vadeli_ozellik.parquet")
