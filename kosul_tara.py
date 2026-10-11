# kosul_tara.py — BİNLERCE KOŞUL TARAMASI (yalnız test): hangi piyasa / borsalar arası / kurumsal koşul sinyallerin isabetini ve kârını değiştiriyor?
# Sinyaller: genis.yml'deki ~140 coin + BTC (coin 🤝 / 🔇 / tek başına · BTC ⭐ / 4s / A · 🧪 24 saat). Sınıf: ✅ ana (🤝 🔇 🧪 ve kendi primi z ≥ 0) · 🔸 yedek (⛔ değil) · ⛔ (kendi primi z ≤ −1).
# Koşullar: ~35 gösterge × 4 eşik (z ≥ 2, ≥ 1, ≤ −1, ≤ −2 · zaman dilimleri) — her gösterge sinyal saatinde YALNIZ GEÇMİŞ veriyle (saatlik: o saatin kapanışı; günlük: bir önceki gün).
# ÖNCEDEN YAZILI TESTLER (11.10.2026, sonuçları görmeden):
#   YÜKSELT (🔸 yedek ve ⛔ grupları): koşullu alt küme seçimde (2022-06→2023) ≥ 30 sinyal · isabet ≥ %57 · net ≥ +%0,35; 2024+ aynı + haftalık blok %5 alt sınır > 0; 2026 (≥ 10 sinyal) net > 0
#   İYİLEŞTİR (✅ ana): koşullu alt küme, aynı dönemin ana ortalamasına göre isabet ≥ +3 puan ve net ≥ +0,15 puan (seçim ve 2024+), 2024+ alt sınır > 0, 2026 net ≥ ana ortalaması
#   ELE (✅ ana): koşullu alt küme seçimde ve 2024+'da isabet ≤ %52 ve net ≤ 0 (≥ 30 sinyal), 2026'da (≥ 10) net ≤ 0
#   ŞANS PAYI: tüm göstergeler zamanda dairesel kaydırılarak (60–400 gün, 20 kez) aynı testler → tesadüfen kaç test geçiyor. Gerçek geçen sayısı plasebonun %95'lik değerini aşmazsa bulgu sayılmaz.
import glob, os, pickle, time, numpy as np, pandas as pd
from ortak import events, wboot, DISPLAY_TZ
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
def bul(p):
    x = glob.glob(p, recursive=True); return x[0] if x else None
P0, A24, A26 = (pd.Timestamp(x, tz="UTC") for x in ("2022-06-01", "2024-01-01", "2026-01-01")); KOM = 0.0004
# ---------------- saatlik ortak ızgara ----------------
SY = sorted({os.path.basename(p)[5:-4] for p in glob.glob("ga/**/disa_*USDT.pkl", recursive=True)})
PR = {}
for sym in SY:
    p = bul(f"ga/**/prim_{sym}.pkl")
    if p: z = pd.read_pickle(p).astype("float64"); z.index = pd.DatetimeIndex(z.index).tz_convert("UTC"); PR[sym[:-4]] = z
H = pd.date_range(pd.Timestamp("2022-05-01", tz="UTC"), max(v.index[-1] for v in PR.values()), freq="1h"); NH = len(H)
def hiz(s, lim=6):                                                                            # saatlik seriyi ızgaraya (yalnız geçmiş: asof)
    s = s.dropna(); s = s[~s.index.duplicated()].sort_index(); return s.reindex(H, method="ffill", limit=lim)
def z720(s): return (s - s.rolling(720, min_periods=168).mean()) / (s.rolling(720, min_periods=168).std() + 1e-12)
def gunluk(s, n=60):                                                                          # günlük seri → z (n gün) → 1 gün gecikmeli saatlik
    s = s.dropna(); s.index = pd.DatetimeIndex(s.index).tz_localize("UTC") if s.index.tz is None else s.index
    zz = (s - s.rolling(n, min_periods=20).mean()) / (s.rolling(n, min_periods=20).std() + 1e-12); zz.index = zz.index + pd.Timedelta(days=1)   # gün d kapanışı (ABD ~21:00 UTC) → d+1 00:00 UTC'den itibaren kullanılır
    return zz.reindex(H, method="ffill")
V = pd.read_pickle(bul("**/kosul_veri.pkl")); yaz(f"# 🔬 Koşul taraması — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nVeri: {', '.join(f'{k} {len(v)}' for k, v in V.items())}")
G = {}                                                                                         # piyasa göstergeleri (saatlik z)
bn, cb_ = V.get("bn_BTC"), V.get("cb_BTC")
if bn is not None:
    q24 = bn.qv.rolling(24).sum(); G["Binance BTC hacmi (24 s)"] = z720(np.log(hiz(q24)))
    G["Binance BTC alıcı payı (24 s)"] = z720(hiz(bn.tbq.rolling(24).sum() / q24))
    G["Binance BTC ort. işlem büyüklüğü"] = z720(np.log(hiz(q24 / bn.trades.rolling(24).sum())))
    G["BTC 24 s getiri"] = z720(np.log(hiz(bn.close)).diff(24)); G["BTC 7 g getiri"] = z720(np.log(hiz(bn.close)).diff(168))
    r1 = np.log(hiz(bn.close)).diff(); G["BTC oynaklık (24 s / 30 g)"] = z720(r1.rolling(24).std() / r1.rolling(720, min_periods=168).std())
if cb_ is not None and bn is not None:
    G["Coinbase BTC hacim payı (ABD payı, 24 s)"] = z720(np.log(hiz(cb_.volume.rolling(24).sum()) / hiz(bn.vol.rolling(24).sum())))
    G["Coinbase BTC hacmi (24 s)"] = z720(np.log(hiz(cb_.volume.rolling(24).sum())))
if V.get("bs_BTC") is not None and bn is not None:
    bs = V["bs_BTC"]; G["Bitstamp primi (BTC)"] = z720(np.log(hiz(bs.close) / hiz(bn.close)).where(lambda x: x.abs() < 0.05))
    G["Bitstamp hacim payı (24 s)"] = z720(np.log(hiz(bs.volume.rolling(24).sum()) / hiz(bn.vol.rolling(24).sum())))
if V.get("cb_ETH") is not None and V.get("bn_ETH") is not None:
    G["Coinbase ETH primi"] = z720(np.log(hiz(V["cb_ETH"].close) / hiz(V["bn_ETH"].close)).where(lambda x: x.abs() < 0.05))
    G["ETH/BTC 24 s göreli getiri"] = z720(np.log(hiz(V["bn_ETH"].close) / hiz(bn.close)).diff(24))
m = V.get("met_BTC")
if m is not None:
    G["Vadeli açık pozisyon 24 s değişim"] = z720(np.log(hiz(m.sum_open_interest_value)).diff(24))
    G["Büyük trader pozisyon uzun/kısa"] = z720(hiz(m.sum_toptrader_long_short_ratio)); G["Tüm hesaplar uzun/kısa (küçük yat.)"] = z720(hiz(m.count_long_short_ratio))
    G["Vadeli alıcı/satıcı oranı (24 s ort.)"] = z720(hiz(m.sum_taker_long_short_vol_ratio).rolling(24).mean())
if V.get("fon_BTC") is not None:
    f = V["fon_BTC"]; G["Fonlama oranı"] = hiz((f - f.rolling(90, min_periods=30).mean()) / (f.rolling(90, min_periods=30).std() + 1e-12), lim=10)
for c in ("BTC", "ETH"):
    if V.get(f"dvol_{c}") is not None:
        d = hiz(V[f"dvol_{c}"]); G[f"DVOL {c} (opsiyon korkusu)"] = z720(d); G[f"DVOL {c} 24 s değişim"] = z720(d.diff(24))
y = {k[2:]: v for k, v in V.items() if k.startswith("y_")}
if "cme" in y and "btcusd" in y:
    a = pd.concat([y["cme"], y["btcusd"]], axis=1, keys=["c", "s"]).dropna(); G["CME vadeli farkı (kurumsal)"] = gunluk(np.log(a.c / a.s))
for k, ad in (("dxy", "Dolar endeksi 5 g"), ("tnx", "ABD 10 yıl faiz 5 g"), ("spx", "S&P 500 5 g"), ("altin", "Altın 5 g"), ("hyg", "Yüksek getirili tahvil 5 g")):
    if k in y: G[ad] = gunluk(np.log(y[k]).diff(5) if k != "tnx" else y[k].diff(5))
if "vix" in y: G["VIX seviyesi"] = gunluk(y["vix"], 90)
try:
    UP, BT, U, VP = pickle.load(open(bul("**/desen_veri.pkl"), "rb"))
    if bn is not None and UP.get("BTC") is not None and UP.get("USDT") is not None:
        G["Kore primi (BTC)"] = z720((np.log(hiz(UP["BTC"]) / (hiz(UP["USDT"]) * hiz(bn.close)))).where(lambda x: x.abs() < 0.3))
    if U is not None: G["USDT primi (Coinbase USDT-USD)"] = z720(np.log(hiz(U)).where(lambda x: x.abs() < 0.05))
except Exception as e: yaz(f"_desen verisi yok: {e}_")
C = pd.DataFrame({nm: hiz(v.c) for nm, v in PR.items()}); r24 = np.log(C).diff(24)
G["Piyasa genişliği (24 s yükselen coin oranı)"] = z720(r24.gt(0).sum(axis=1) / r24.notna().sum(axis=1).replace(0, np.nan))
G["Coin'ler arası ayrışma (24 s getiri yayılımı)"] = z720(r24.std(axis=1))
G["BTC Coinbase primi"] = z720(hiz(PR["BTC"].bp)) if "BTC" in PR else None
G = {k: v.reindex(H) for k, v in G.items() if v is not None}
yaz(f"Piyasa göstergesi: {len(G)} · {time.time()-T0:.0f} sn")
# ---------------- olaylar ----------------
B = pd.read_pickle(bul("ga/**/disa_BTCUSDT.pkl")); B.index = pd.DatetimeIndex(B.index).tz_convert("UTC")
EV = []
def ekle(nm, aile, t, r):
    EV.append(pd.DataFrame({"nm": nm, "aile": aile, "t": pd.DatetimeIndex(t), "r": np.asarray(r, float)}))
for sym in SY:
    nm = sym[:-4]
    if nm not in PR: continue
    X = pd.read_pickle(bul(f"ga/**/disa_{sym}.pkl")); X.index = pd.DatetimeIndex(X.index).tz_convert("UTC"); X = X[X.index >= H[0]]
    st_, u4_, ac_ = (X[k].fillna(False).astype(bool).values for k in ("star", "u4", "acls")); ok4 = X.y4.notna().values
    if nm == "BTC":
        ev = events(st_ & X.y8.notna().values, 8); ekle(nm, "BTC ailesi", X.index[ev], np.exp(X.y8.values[ev]) - 1)
        ev = events((u4_ | ac_) & ok4, 4); ekle(nm, "BTC ailesi", X.index[ev], np.exp(X.y4.values[ev]) - 1)
    else:
        Bx = B.reindex(X.index); bu4 = Bx.u4.fillna(False).astype(bool).values; bany = bu4 | Bx.star.fillna(False).astype(bool).values | Bx.acls.fillna(False).astype(bool).values
        ev = events((st_ | u4_ | ac_) & ok4, 4); sinif = np.where(bu4[ev], "🤝", np.where(~bany[ev], "🔇", "coin tek"))
        EV.append(pd.DataFrame({"nm": nm, "aile": sinif, "t": X.index[ev], "r": np.exp(X.y4.values[ev]) - 1}))
    d24 = bul(f"ga/**/disa24_{sym}.pkl")
    if d24:
        D = pd.read_pickle(d24).astype("float64"); D.index = pd.DatetimeIndex(D.index).tz_convert("UTC"); D = D.reindex(pd.date_range(D.index[0], D.index[-1], freq="1h", tz="UTC"))
        c = D.close.ffill(limit=3).values; n = len(D); mk = np.nan_to_num(((D.S24 > 0) & (D.C24 >= D.T10_24)).values).astype(bool) & D.T10_24.notna().values & (np.arange(n) + 25 < n)
        ev = events(mk, 24); ok = ev[D.index[ev] >= H[0]]; ekle(nm, "🧪", D.index[ok], c[ok + 24] / c[ok] - 1)
E = pd.concat(EV, ignore_index=True); E = E[np.isfinite(E.r) & (E.t >= H[0]) & (E.t <= H[-1])].reset_index(drop=True)
E["pos"] = H.get_indexer(E.t); E = E[E.pos >= 0].reset_index(drop=True)
ZO = np.full(len(E), np.nan)
for nm, g in E.groupby("nm"): ZO[g.index] = hiz(PR[nm].z).values[g.pos.values]
E["z"] = ZO; E = E[np.isfinite(E.z)].reset_index(drop=True); E["net"] = E.r - KOM; E["ok"] = E.net > 0
E["sinif"] = np.where(E.z <= -1, "⛔", np.where(E.aile.isin(["🤝", "🔇", "🧪"]) & (E.z >= 0), "✅ ana", "🔸 yedek"))
yaz(f"Sinyal: {len(E):,} · coin {E.nm.nunique()} · " + " · ".join(f"{k} {v:,}" for k, v in E.sinif.value_counts().items()) + f" · {time.time()-T0:.0f} sn")
# coin düzeyi göstergeler (her coin kendi serisi)
CG = {"Coin'in kendi primi 24 s değişimi": {}, "Coin primi − BTC primi (fark)": {}, "Coin 24 s getiri": {}, "Coin 7 g getiri (BTC'ye göre)": {}, "Coin oynaklık (24 s / 30 g)": {}}
zb = hiz(PR["BTC"].z) if "BTC" in PR else None
for nm in E.nm.unique():
    zc = hiz(PR[nm].z); c = np.log(hiz(PR[nm].c)); rr = c.diff()
    CG["Coin'in kendi primi 24 s değişimi"][nm] = zc.diff(24).values; CG["Coin primi − BTC primi (fark)"][nm] = (zc - zb).values if zb is not None else zc.values * np.nan
    CG["Coin 24 s getiri"][nm] = z720(c.diff(24)).values; CG["Coin 7 g getiri (BTC'ye göre)"][nm] = z720(c.diff(168) - np.log(hiz(PR["BTC"].c)).diff(168)).values
    CG["Coin oynaklık (24 s / 30 g)"][nm] = z720(rr.rolling(24).std() / rr.rolling(720, min_periods=168).std()).values
# ---------------- koşul matrisleri ----------------
ad_l, gm = list(G), np.vstack([G[k].values for k in G])                                         # piyasa: [gösterge × saat]
cad_l = list(CG); NMI = {nm: i for i, nm in enumerate(E.nm.unique())}
cm = np.full((len(cad_l), len(NMI), NH), np.nan)
for j, k in enumerate(cad_l):
    for nm, i in NMI.items(): cm[j, i] = CG[k][nm]
ei = E.nm.map(NMI).values; pos = E.pos.values
ESIK = (("z ≥ 2", lambda v: v >= 2), ("z ≥ 1", lambda v: v >= 1), ("z ≤ −1", lambda v: v <= -1), ("z ≤ −2", lambda v: v <= -2))
saat = (E.t + pd.Timedelta(hours=3)).dt.hour.values; hs = (E.t.dt.dayofweek >= 5).values
ZAMAN = {"Saat 00–05 (TR)": (saat <= 5), "Saat 06–11 (TR)": (saat >= 6) & (saat <= 11), "Saat 12–17 (TR)": (saat >= 12) & (saat <= 17), "Saat 18–23 (TR)": saat >= 18, "Hafta sonu": hs}
def kosullar(kay):                                                                             # kay: saat kaydırması (plasebo)
    gv = np.roll(gm, kay, axis=1)[:, pos] if kay else gm[:, pos]; cv = (np.roll(cm, kay, axis=2) if kay else cm)[:, ei, pos]
    K = {}
    for j, a in enumerate(ad_l):
        v = gv[j]
        for en, f in ESIK: K[f"{a} {en}"] = np.nan_to_num(f(v), nan=0).astype(bool) & np.isfinite(v)
    for j, a in enumerate(cad_l):
        v = cv[j]
        for en, f in ESIK: K[f"{a} {en}"] = np.nan_to_num(f(v), nan=0).astype(bool) & np.isfinite(v)
    if not kay: K.update(ZAMAN)
    return K
t_ = E.t.values; net = E.net.values; okv = E.ok.values
DONEM = {"s": (E.t >= P0) & (E.t < A24), "d": E.t >= A24, "y": E.t >= A26}; DONEM = {k: v.values for k, v in DONEM.items()}
HEDEF = {"✅ ana": E.sinif.eq("✅ ana").values, "🔸 yedek (hepsi)": E.sinif.eq("🔸 yedek").values, "🔸 yedek · BTC ailesi": (E.sinif.eq("🔸 yedek") & E.aile.eq("BTC ailesi")).values,
         "🔸 yedek · coin tek": (E.sinif.eq("🔸 yedek") & E.aile.eq("coin tek")).values, "🔸 yedek · 🤝🔇🧪 (prim −1…0)": (E.sinif.eq("🔸 yedek") & E.aile.isin(["🤝", "🔇", "🧪"])).values,
         "⛔ (ABD satıyor)": E.sinif.eq("⛔").values}
def ist(m):
    n = int(m.sum()); return (n, 100 * okv[m].mean() if n else np.nan, 100 * net[m].mean() if n else np.nan)
TAB = {h: {d: ist(hm & dm) for d, dm in DONEM.items()} for h, hm in HEDEF.items()}
def testler(K, alt=True):
    gec = []
    for kn, km in K.items():
        for h, hm in HEDEF.items():
            S = {d: ist(km & hm & dm) for d, dm in DONEM.items()}
            (ns, hs_, xs), (nd, hd, xd), (ny, hy, xy) = S["s"], S["d"], S["y"]
            if ns < 30 or nd < 30: continue
            tur = None
            if h == "✅ ana":
                bs_, bd, by = TAB[h]["s"], TAB[h]["d"], TAB[h]["y"]
                if hs_ >= bs_[1] + 3 and xs >= bs_[2] + 0.15 and hd >= bd[1] + 3 and xd >= bd[2] + 0.15 and (ny < 10 or xy >= by[2]): tur = "İYİLEŞTİR"
                elif hs_ <= 52 and xs <= 0 and hd <= 52 and xd <= 0 and (ny < 10 or xy <= 0): tur = "ELE"
            elif hs_ >= 57 and xs >= 0.35 and hd >= 57 and xd >= 0.35 and (ny < 10 or xy > 0): tur = "YÜKSELT"
            if tur is None: continue
            if alt and tur != "ELE":
                mm = km & hm & DONEM["d"]; lo = 100 * wboot(net[mm], t_[mm], 300)[0]
                if not lo > 0: continue
            else: lo = np.nan
            gec.append(dict(tur=tur, kosul=kn, hedef=h, s=S["s"], d=S["d"], y=S["y"], alt=lo))
    return gec
K0 = kosullar(0); yaz(f"Koşul: {len(K0)} · hedef: {len(HEDEF)} → test: {len(K0) * len(HEDEF):,} · {time.time()-T0:.0f} sn")
GER = testler(K0); GERK = [g for g in GER if g["kosul"] not in ZAMAN]                       # plaseboyla karşılaştırma: zaman koşulları hariç (kaydırılamaz)
rng = np.random.default_rng(7); PL = []
for i in range(20):
    k = int(rng.integers(60 * 24, 400 * 24)); PL.append(len(testler(kosullar(k), alt=True)))
yaz(f"\n## Şans payı\nGerçek veride geçen: **{len(GERK)}** (zaman koşulları hariç; dahil {len(GER)}) · plasebo (20 kez kaydırılmış): ortalama {np.mean(PL):.1f}, %95'lik {np.percentile(PL, 95):.0f}, en çok {max(PL)} → "
    + ("✅ gerçek sonuç şanstan belirgin fazla" if len(GERK) > np.percentile(PL, 95) else "❌ şanstan ayırt edilemiyor — tek tek bulgular güvenilir değil"))
yaz("\n## Grupların genel durumu (koşulsuz) — _sinyal · isabet · işlem başı net %_\n```")
for h, d in TAB.items(): yaz(f"{h:34s} " + " | ".join(f"{dn}: {d[k][0]:6d} · %{d[k][1]:.1f} · {d[k][2]:+.3f}" for k, dn in (("s", "2022-06→2023"), ("d", "2024+"), ("y", "2026"))))
yaz("```")
yaz("\n## Geçen testler — _seçim | 2024+ | 2026 (sinyal · isabet · net) · alt = 2024+ haftalık blok %5 alt sınır_\n```")
for g in sorted(GER, key=lambda g: (g["tur"], -g["d"][2])):
    f = lambda x: f"{x[0]:5d} · %{x[1]:.1f} · {x[2]:+.2f}"
    yaz(f"{g['tur']:9s} {g['hedef']:30s} {g['kosul']:52s} {f(g['s'])} | {f(g['d'])} | {f(g['y'])} · alt {g['alt']:+.2f}")
yaz("```" + (f"\n_Süre: {time.time()-T0:.0f} sn_"))
open("kosul_tara_sonuc.md", "w").write("\n".join(L) + "\n")
