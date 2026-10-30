# btcyon2.py — PROTOKOL_btcyon2.md: Y7 trend · Y8 vadeli prim endeksi · Y9 tasfiye mıknatısı · Y10 uyumsuzluk · Y11 zincir üstü değerleme → btcyon2_sonuc.md
import io, time, contextlib, numpy as np, pandas as pd
with contextlib.redirect_stdout(io.StringIO()): import btcneden as N
T0 = time.time(); out = []
def yaz(s=""): out.append(s); print(s, flush=True)
TS = lambda s: pd.Timestamp(s, tz="UTC")
H, KB, KD = N.H, N.KB, N.KD
GD = pd.read_parquet("btcyon2_gun.parquet"); PI = pd.read_parquet("btcyon2_prim.parquet").set_index("t").sort_index()
DON_S = [("K 2022–23", "2022-01-01", "2024-01-01"), ("C1 2024", "2024-01-01", "2025-01-01"), ("C2 2025–26", "2025-01-01", "2026-10-28")]
DON_U = [("K 2018–21", "2018-01-01", "2022-01-01"), ("C1 2022–23", "2022-01-01", "2024-01-01"), ("C2 2024–26", "2024-01-01", "2026-10-28")]
def donem(ix, DON):
    ix = pd.DatetimeIndex(ix); d = np.full(len(ix), None, object)
    for ad, a, b in DON: d[(ix >= TS(a)) & (ix < TS(b))] = ad
    return d
def ozet(R, DON, minn, esik):
    hs, yok, aok = [], True, True
    for ad, _, _ in DON:
        x = R[R.don == ad] if len(R) else R
        if not len(x): hs.append("0"); yok = aok = False; continue
        yi, ii, nt = (x.ham > 0).mean(), (x.net > 0).mean(), x.net.mean()
        hs.append(f"{len(x)} · yön %{100 * yi:.0f} · isabet %{100 * ii:.0f} · {100 * nt:+.2f}")
        if not (len(x) >= minn and yi >= 0.57 and nt > 0): yok = False
        if not (len(x) >= minn and ii >= 0.65 and nt >= esik): aok = False
    return hs, yok, aok
SONUC = []
def satir(aile, ad, R, DON, minn, esik):
    hs, yok, aok = ozet(R, DON, minn, esik); yaz(f"| {ad} | " + " | ".join(hs) + f" | {'🎯' if aok else ('✅' if yok else '')} |"); SONUC.append((aile, ad, yok, aok))
def baslik(DON): yaz("| kural | " + " | ".join(a for a, _, _ in DON) + " | |"); yaz("|---|" + "---|" * len(DON) + "---|")
# ---- saatlik değerlendirme (btcyon ile aynı) ----
def deg_saat(sig, nsaat, K=KB):
    R = []; serbest = None; ix = K.index; o, c = K.o.values, K.c.values
    for t, yon in sig.sort_values("t")[["t", "yon"]].itertuples(index=False):
        if serbest is not None and t < serbest: continue
        i = ix.searchsorted(t)
        if i >= len(ix) or ix[i] != t or i + nsaat > len(ix): continue
        net, j = N.islem(K, i, int(yon), 10.0, None, nsaat); R.append((t, yon, yon * (c[i + nsaat - 1] / o[i] - 1), net)); serbest = ix[j] + pd.Timedelta(hours=1)
    R = pd.DataFrame(R, columns=["t", "yon", "ham", "net"]); R["don"] = donem(R.t, DON_S) if len(R) else []; return R
# ---- günlük değerlendirme (uzun geçmiş: sabit fonlama %0,01/8 s varsayımı) ----
def deg_gun(sig, hg, K):
    R = []; serbest = None; ix = K.index; o, c = K.o.values, K.c.values
    for t, yon in sig.sort_values("t")[["t", "yon"]].itertuples(index=False):
        if serbest is not None and t < serbest: continue
        i = ix.searchsorted(t)
        if i >= len(ix) or ix[i] != t or i + hg > len(ix): continue
        ham = yon * (c[i + hg - 1] / (o[i] * (1 + 0.001 * yon)) - 1); net = ham - 0.001 - yon * 0.0003 * hg
        R.append((t, yon, yon * (c[i + hg - 1] / o[i] - 1), net)); serbest = ix[i + hg - 1] + pd.Timedelta(days=1)
    R = pd.DataFrame(R, columns=["t", "yon", "ham", "net"]); R["don"] = donem(R.t, DON_U) if len(R) else []; return R
def plasebo_saat(kurallar, n=10, seed=4):
    rng = np.random.default_rng(seed); a0, a1 = KB.index[0], KB.index[-1]; span = int((a1 - a0).total_seconds() // 3600); say = []
    for _ in range(n):
        off = pd.Timedelta(hours=int(rng.integers(90 * 24, span - 90 * 24))); g = 0
        for sig, nsaat, minn, esik in kurallar:
            t = sig.t + off; t = t.where(t <= a1, t - pd.Timedelta(hours=span + 1)); g += ozet(deg_saat(pd.DataFrame({"t": t.dt.floor("h"), "yon": sig.yon.values}), nsaat), DON_S, minn, esik)[1]
        say.append(g)
    return np.mean(say), max(say)
yaz("# 🧭 BTC'nin YÖNÜ — 2. tur · PROTOKOL_btcyon2.md")
yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · hücre: işlem · yön isabeti · isabet (masraf sonrası kâr) · işlem başı net % · ✅ yön şartı · 🎯 sinyal adayı_\n")
# ======================= Y7 =======================
yaz("## Y7 — Haftalık/aylık trend (günlük spot, 2018 → 2026)")
GK = {c: g.set_index("t").sort_index() for c, g in GD.groupby("coin")}; BG = GK["BTC"]
c = BG.c; ma50, ma200 = c.rolling(50).mean(), c.rolling(200).mean(); r28, r7, r3 = c / c.shift(28) - 1, c / c.shift(7) - 1, c / c.shift(3) - 1
KUR = {"T1 fiyat > 200 g ort.": np.sign(c - ma200), "T2 50 g ort. > 200 g ort.": np.sign(ma50 - ma200), "T3 28 g getiri işareti": np.sign(r28), "T4 7 g getiri işareti": np.sign(r7),
       "T5 yükseliş trendinde %5+ geri çekilme → AL": pd.Series(np.where((c > ma200) & (r3 <= -0.05), 1, 0), index=c.index),
       "T6 düşüş trendinde %5+ tepki → SAT": pd.Series(np.where((c < ma200) & (r3 >= 0.05), -1, 0), index=c.index)}
baslik(DON_U); Y7SIG = {}
for ad, s in KUR.items():
    s = s.dropna(); s = s[s != 0]; sig = pd.DataFrame({"t": s.index + pd.Timedelta(days=1), "yon": s.values.astype(int)}); Y7SIG[ad] = sig
    for hg in (7, 14, 28): satir("Y7", f"{ad} · {hg} g", deg_gun(sig, hg, BG), DON_U, 15 if hg < 28 else 8, 0.005)
yaz("\n_bilgi — yalnız AL tarafı (SAT yerine nakit) toplam getiri vs al-tut, dönem başına (BTC):_")
for ad in ("T1 fiyat > 200 g ort.", "T2 50 g ort. > 200 g ort.", "T3 28 g getiri işareti"):
    sg = KUR[ad].shift(1).reindex(BG.index); g = np.log(BG.c / BG.c.shift(1)); p = []
    for dad, a, b in DON_U:
        m = (BG.index >= TS(a)) & (BG.index < TS(b)); p.append(f"{dad}: kural %{100 * (np.exp(g[m][sg[m] > 0].sum()) - 1):+.0f} / al-tut %{100 * (np.exp(g[m].sum()) - 1):+.0f} · piyasada %{100 * (sg[m] > 0).mean():.0f}")
    yaz(f"- {ad}: " + " ‖ ".join(p))
yaz("\n_ETH ve SOL'da aynı BTC kuralı (14 g, tüm dönemler):_")
for ad, sig in Y7SIG.items():
    yaz(f"- {ad}: " + " ‖ ".join(f"{cn} " + " · ".join(ozet(deg_gun(sig, 14, GK[cn]), DON_U, 1, 0)[0]) for cn in ("ETH", "SOL")))
# ======================= Y8 =======================
yaz("\n## Y8 — Vadeli prim endeksi (vadeli işaret fiyatı − spot endeks)")
pi = PI.c.reindex(KB.index); p24 = pi.rolling(24).mean(); pz = (p24 - p24.rolling(720, min_periods=360).mean()) / p24.rolling(720, min_periods=360).std()
dn = donem(KB.index, DON_S); K8 = []; baslik(DON_S)
for v, vad in ((p24, "prim 24 s ort."), (pz, "prim z (720 s)")):
    for hs in (4, 24):
        fw = np.log(KB.c.shift(-hs) / KB.o.shift(-1)); k = dn == "K 2022–23"; qa, qb = v[k].quantile(0.2), v[k].quantile(0.8)
        for kad, m in (("alt %20", v <= qa), ("üst %20", v > qb)):
            kar = 1 if fw[m & k].mean() > 0 else -1; sig = pd.DataFrame({"t": KB.index[m.values] + pd.Timedelta(hours=1), "yon": kar})
            esik = 0.002 if hs < 24 else 0.005; satir("Y8", f"{vad} {kad} → {hs} s {'AL' if kar == 1 else 'SAT'}", deg_saat(sig, hs), DON_S, 30, esik); K8.append((sig, hs, 30, esik))
pd3 = pi.resample("1D").mean().rolling(3).mean(); dD = pd3.index; dnD = donem(dD, DON_S); 
fw3 = (np.log(KB.c.resample("1D").last()).shift(-3) - np.log(KB.c.resample("1D").last())).reindex(dD)
k = dnD == "K 2022–23"; qa, qb = pd3[k].quantile(0.2), pd3[k].quantile(0.8)
for kad, m in (("alt %20", pd3 <= qa), ("üst %20", pd3 > qb)):
    kar = 1 if fw3[m & k].mean() > 0 else -1; sig = pd.DataFrame({"t": dD[m.values] + pd.Timedelta(days=1), "yon": kar})
    satir("Y8", f"prim 3 g ort. {kad} → 3 g {'AL' if kar == 1 else 'SAT'}", deg_saat(sig, 72), DON_S, 30, 0.005); K8.append((sig, 72, 30, 0.005))
m_, M_ = plasebo_saat(K8); yaz(f"\n**Y8 plasebo:** ortalama {m_:.1f}, en çok {M_} geçerdi")
# ======================= Y9 =======================
yaz("\n## Y9 — Tasfiye mıknatısı")
grid = np.exp(np.arange(np.log(5000), np.log(400000), 0.0025)); nb = len(grid)
UZ, KS = np.zeros(nb), np.zeros(nb); dec = 0.5 ** (1 / (30 * 24))
oi, al, qv, cc, hh, ll = H.oi.values, H.f_al.values, H.f_qv.values, H.f_c.values, H.f_h.values, H.f_l.values
ORAN = np.full(len(H), np.nan); onceki = np.nan
for i in range(len(H)):
    UZ *= dec; KS *= dec
    if not np.isnan(ll[i]):
        UZ[grid >= ll[i]] = 0; KS[grid <= hh[i]] = 0                                            # tetiklenen tasfiyeler silinir
    if not np.isnan(oi[i]) and not np.isnan(onceki) and onceki > 0:
        d = oi[i] - onceki
        if d < 0: f = oi[i] / onceki; UZ *= f; KS *= f
        elif d > 0 and qv[i] > 0:
            uzun = al[i] / qv[i] > 0.5
            for L in (10, 25, 50):
                lp = cc[i] * (1 - 1 / L) if uzun else cc[i] * (1 + 1 / L); j = min(max(np.searchsorted(grid, lp), 0), nb - 1)
                (UZ if uzun else KS)[j] += d / 3
    if not np.isnan(oi[i]): onceki = oi[i]
    if i % 1 == 0 and not np.isnan(cc[i]):
        a, b_, e = np.searchsorted(grid, cc[i]), np.searchsorted(grid, cc[i] * 1.05), np.searchsorted(grid, cc[i] * 0.95)
        ORAN[i] = np.log((KS[a:b_].sum() + 1) / (UZ[e:a].sum() + 1))
OR = pd.Series(ORAN, index=H.index).reindex(KB.index); K9 = []
yaz(f"_oran = log(yukarıdaki kısa tasfiye / aşağıdaki uzun tasfiye, ±%5) · K medyanı {OR[dn == 'K 2022–23'].median():+.2f}_"); baslik(DON_S)
for hs in (24, 72):
    fw = np.log(KB.c.shift(-hs) / KB.o.shift(-1)); k = dn == "K 2022–23"; qa, qb = OR[k].quantile(0.2), OR[k].quantile(0.8)
    for kad, m in (("alt %20 (aşağıda uzun kümesi)", OR <= qa), ("üst %20 (yukarıda kısa kümesi)", OR > qb)):
        kar = 1 if fw[m & k].mean() > 0 else -1; sig = pd.DataFrame({"t": KB.index[m.values] + pd.Timedelta(hours=1), "yon": kar})
        satir("Y9", f"{kad} → {hs} s {'AL' if kar == 1 else 'SAT'} (K ort. {100 * fw[m & k].mean():+.2f})", deg_saat(sig, hs), DON_S, 30, 0.005); K9.append((sig, hs, 30, 0.005))
m_, M_ = plasebo_saat(K9); yaz(f"\n**Y9 plasebo:** ortalama {m_:.1f}, en çok {M_} geçerdi")
# ======================= Y10 =======================
yaz("\n## Y10 — Fiyat / akış uyumsuzluğu (72 s)")
cvd = (2 * H.f_al - H.f_qv).fillna(0).cumsum(); pp = H.p; c_ = H.f_c
mn72, mx72 = c_.rolling(72).min(), c_.rolling(72).max(); amin = c_.rolling(72).apply(np.argmin, raw=True); amax = c_.rolling(72).apply(np.argmax, raw=True)
onc_min = c_.shift(24).rolling(48).min(); onc_max = c_.shift(24).rolling(48).max()                 # önceki dip/tepe: 24–72 s önce
ix_min = c_.shift(24).rolling(48).apply(np.argmin, raw=True); ix_max = c_.shift(24).rolling(48).apply(np.argmax, raw=True)
n = np.arange(len(H)); jmin = (n - 71 + ix_min.values).astype("float"); jmax = (n - 71 + ix_max.values).astype("float")
def deger(seri, j): v = np.full(len(j), np.nan); ok = ~np.isnan(j) & (j >= 0); v[ok] = seri.values[j[ok].astype(int)]; return v
dip = (c_ <= mn72) & (c_ < onc_min); tepe = (c_ >= mx72) & (c_ > onc_max)
K10 = []; baslik(DON_S); dnH = donem(H.index, DON_S)
for ad, akis in (("vadeli kümülatif agresif", cvd), ("Coinbase primi", pp)):
    pos = dip & (akis.values > deger(akis, jmin)); neg = tepe & (akis.values < deger(akis, jmax))
    for kad, m, bek in (("pozitif (yeni dip, akış güçlü)", pos, 1), ("negatif (yeni tepe, akış zayıf)", neg, -1)):
        for hs in (24, 72):
            fw = np.log(H.f_c.shift(-hs) / H.f_o.shift(-1)); kk = m.values & (dnH == "K 2022–23")
            kar = (1 if fw[kk].mean() > 0 else -1) if kk.sum() >= 5 else bek
            sig = pd.DataFrame({"t": H.index[m.values] + pd.Timedelta(hours=1), "yon": kar})
            satir("Y10", f"{ad} · {kad} → {hs} s {'AL' if kar == 1 else 'SAT'} (K {int(kk.sum())} saat)", deg_saat(sig, hs), DON_S, 30, 0.005); K10.append((sig, hs, 30, 0.005))
m_, M_ = plasebo_saat(K10); yaz(f"\n**Y10 plasebo:** ortalama {m_:.1f}, en çok {M_} geçerdi")
# ======================= Y11 =======================
yaz("\n## Y11 — Zincir üstü değerleme (uzun vade, bilgi)")
if "CapMVRVCur" in BG:
    mv = BG.CapMVRVCur; V11 = {"MVRV z (4 yıl)": (mv - mv.rolling(1460, min_periods=730).mean()) / mv.rolling(1460, min_periods=730).std(),
                               "aktif adres 30g/365g": BG.AdrActCnt.rolling(30).mean() / BG.AdrActCnt.rolling(365).mean(),
                               "transfer hacmi 30g/365g": BG.TxTfrValAdjUSD.rolling(30).mean() / BG.TxTfrValAdjUSD.rolling(365).mean()}
    baslik(DON_U); dU = donem(BG.index, DON_U)
    for vad, v in V11.items():
        v = v.shift(1)                                                                       # yayın gecikmesi
        for hg in (28, 90):
            fw = np.log(BG.c.shift(-hg) / BG.c); k = dU == "K 2018–21"; qa, qb = v[k].quantile(0.2), v[k].quantile(0.8)
            for kad, m in (("alt %20", v <= qa), ("üst %20", v > qb)):
                kar = 1 if fw[m & k].mean() > 0 else -1; sig = pd.DataFrame({"t": BG.index[m.values], "yon": kar})
                satir("Y11", f"{vad} {kad} → {hg} g {'AL' if kar == 1 else 'SAT'}", deg_gun(sig, hg, BG), DON_U, 6, 0.005)
else: yaz("CoinMetrics değerleme verisi alınamadı.")
yaz("\n## Özet")
for a in ("Y7", "Y8", "Y9", "Y10", "Y11"):
    k = [s for s in SONUC if s[0] == a]; yaz(f"- {a}: {len(k)} kural · yön ✅ {sum(s[2] for s in k)} · sinyal adayı 🎯 {sum(s[3] for s in k)}" + "".join(f"\n  - {'🎯' if s[3] else '✅'} {s[1]}" for s in k if s[2] or s[3]))
yaz(f"\n_süre {time.time() - T0:.0f} sn_")
open("btcyon2_sonuc.md", "w").write("\n".join(out) + "\n")
