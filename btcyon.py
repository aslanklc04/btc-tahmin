# btcyon.py — PROTOKOL_btcyon.md: BTC'nin YÖNÜ (Y1–Y6) → btcyon_sonuc.md · btcneden.py'nin türettiği verileri kullanır
import sys, io, time, contextlib, numpy as np, pandas as pd
with contextlib.redirect_stdout(io.StringIO()): import btcneden as N                     # btcneden aynen yeniden çalışır (çıktısı değişmez)
import lightgbm as lgb
T0 = time.time(); out = []
def yaz(s=""): out.append(s); print(s, flush=True)
D, B, H, X, Z, E, KB, KD, X4 = N.D, N.B, N.H, N.X, N.Z, N.E, N.KB, N.KD, N.X4
DON = [d[0] for d in N.DON]; donem = N.donem; zprev = N.zprev
TS = lambda s: pd.Timestamp(s, tz="UTC")
K_END, C1_END = TS("2024-01-01"), TS("2025-01-01")
o_, c_ = KB.o.values, KB.c.values
def degerlendir(sig, nsaat, K=KB):
    """sig: DataFrame t (giriş saati) · yon (±1). Aynı anda tek işlem, süre sonu çıkış."""
    R = []; serbest = None; ix = K.index; o, c = K.o.values, K.c.values
    for t, yon in sig.sort_values("t")[["t", "yon"]].itertuples(index=False):
        if serbest is not None and t < serbest: continue
        i = ix.searchsorted(t)
        if i >= len(ix) or ix[i] != t or i + nsaat > len(ix): continue
        net, j = N.islem(K, i, int(yon), 10.0, None, nsaat); ham = yon * (c[i + nsaat - 1] / o[i] - 1)
        R.append((t, yon, ham, net)); serbest = ix[j] + pd.Timedelta(hours=1)
    R = pd.DataFrame(R, columns=["t", "yon", "ham", "net"]); R["don"] = donem(R.t) if len(R) else []
    return R
def ozet(R, minn, esik):
    hs, yok, aok = [], True, True
    for ad in DON:
        x = R[R.don == ad] if len(R) else R
        if not len(x): hs.append("0"); yok = aok = False; continue
        yi, ii, nt = (x.ham > 0).mean(), (x.net > 0).mean(), x.net.mean()
        hs.append(f"{len(x)} · yön %{100 * yi:.0f} · isabet %{100 * ii:.0f} · {100 * nt:+.2f}")
        if not (len(x) >= minn and yi >= 0.57 and nt > 0): yok = False
        if not (len(x) >= minn and ii >= 0.65 and nt >= esik): aok = False
    return hs, yok, aok
SONUC = []                                                                                   # (aile, ad, sig, nsaat, minn, esik)
def kural(aile, ad, sig, nsaat, minn=30, esik=0.005, yazdir=True):
    R = degerlendir(sig, nsaat); hs, yok, aok = ozet(R, minn, esik)
    if yazdir: yaz(f"| {ad} | " + " | ".join(hs) + f" | {'🎯' if aok else ('✅' if yok else '')} |")
    SONUC.append((aile, ad, sig, nsaat, minn, esik, yok, aok)); return yok, aok
def baslik(): yaz("| kural | K 2022–23 | C1 2024 | C2 2025–26 | |"); yaz("|---|---|---|---|---|")
def plasebo(aile, n=20, seed=3):
    rng = np.random.default_rng(seed); kur = [s for s in SONUC if s[0] == aile]; a0, a1 = KB.index[0], KB.index[-1]; span = (a1 - a0).total_seconds() / 3600
    sayi = []
    for _ in range(n):
        off = pd.Timedelta(hours=int(rng.integers(90 * 24, span - 90 * 24))); g = 0
        for _, _, sig, nsaat, minn, esik, _, _ in kur:
            t = sig.t + off; t = t.where(t <= a1, t - pd.Timedelta(hours=span + 1)); s2 = pd.DataFrame({"t": t.dt.floor("h"), "yon": sig.yon.values})
            g += ozet(degerlendir(s2, nsaat), minn, esik)[1]
        sayi.append(g)
    gec = sum(s[6] for s in kur); yaz(f"\n**{aile}: yön şartını geçen {gec} / {len(kur)} · sinyal adayı {sum(s[7] for s in kur)}** · plasebo (rastgele zaman kaydırma ×{n}) ortalama {np.mean(sayi):.1f}, en çok {max(sayi)}")
    return gec, np.mean(sayi)
yaz("# 🧭 BTC'nin YÖNÜ — PROTOKOL_btcyon.md")
yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · hücre: işlem · yön isabeti (fiyat tahmin yönünde gitti) · isabet (masraf sonrası kâr) · işlem başı net % · ✅ yön şartı (her dönemde yön ≥ %57, net > 0) · 🎯 sinyal adayı_\n")
# ======================= Y1 =======================
yaz("## Y1 — Bileşik yön skoru (günlük, D−1 sonunda bilinen 19 durum)")
F1 = B[["ls", "top_ls", "fon3", "oi7", "fimb3", "simb3", "prim3", "prim_d3", "dvol3", "sikisma", "zirve30", "r7", "stabil7", "borsa7z", "nasdaq5", "dxy5", "faiz5", "vix", "korku"]].copy()
for c in ("ls", "top_ls", "fon3", "prim3", "vix", "korku"): F1[c] = zprev(F1[c], 180)
lc = np.log(D.c)
YH = {h: (lc.shift(h - 1) - lc.shift(1)) for h in (1, 3, 7)}                                  # D 00:00 (≈ D−1 kapanışı) → D+h−1 kapanışı
def ridge_fit(Xtr, ytr, lam=10.0):
    m, s = Xtr.mean(), Xtr.std().replace(0, 1); Xs = ((Xtr - m) / s).fillna(0).values; yc = ytr.values - ytr.mean()
    b = np.linalg.solve(Xs.T @ Xs + lam * np.eye(Xs.shape[1]), Xs.T @ yc); return m, s, b, ytr.mean()
def ridge_pred(mdl, Xx): m, s, b, a = mdl; return pd.Series(((Xx - m) / s).fillna(0).values @ b + a, index=Xx.index)
for h in (1, 3, 7):
    y = YH[h]; sig = []; agir = None
    for test_a, test_b, egit_b in ((TS("2022-01-01"), K_END, K_END), (K_END, C1_END, K_END), (C1_END, TS("2026-10-28"), C1_END)):
        tr = (F1.index >= TS("2022-01-01")) & (F1.index < egit_b - pd.Timedelta(days=h)) & y.notna().values
        mdl = ridge_fit(F1[tr], y[tr]); ptr = ridge_pred(mdl, F1[tr]); q20, q80 = ptr.quantile(0.2), ptr.quantile(0.8)
        te = (F1.index >= test_a) & (F1.index < test_b); p = ridge_pred(mdl, F1[te])
        sig.append(pd.DataFrame({"t": p.index[p >= q80], "yon": 1})); sig.append(pd.DataFrame({"t": p.index[p <= q20], "yon": -1}))
        if test_a == K_END: agir = pd.Series(mdl[2], index=F1.columns)
    S = pd.concat(sig)
    if h == 1: baslik()
    kural("Y1", f"skor {h} g (K ile eğitim; C2 için K+C1)", S, h * 24, 30, 0.005)
    if h == 3:
        en = agir.abs().sort_values(ascending=False).head(6); Y1_AGIR = ", ".join(f"{k} {v * 1e4:+.0f}" for k, v in agir[en.index].items())
yaz(f"\n_K'de 3 g modelinin en ağır 6 durumu (katsayı, baz puan / 1 std): {Y1_AGIR}_")
lsz = zprev(B.ls, 180); kq = B.dxy5[B.index < K_END].quantile([0.2, 0.8]).values
oy = (np.where(lsz >= 1, -1, 0) + np.where(lsz <= -1, 1, 0) + np.where(B.dxy5 >= kq[1], -1, 0) + np.where(B.dxy5 <= kq[0], 1, 0) + np.where(B.borsa7z >= 1.5, -1, 0))
oy = pd.Series(oy, index=B.index)
for h in (1, 3, 7):
    S = pd.concat([pd.DataFrame({"t": oy.index[oy >= 2], "yon": 1}), pd.DataFrame({"t": oy.index[oy <= -2], "yon": -1})])
    kural("Y1-bilgi", f"oy kuralı {h} g (BİLGİ — yönler tüm dönemler görülerek seçildi)", S, h * 24, 15, 0.005)
plasebo("Y1")
# ======================= Y2 =======================
yaz("\n## Y2 — Hareketi kim sürdü → devam mı, dönüş mü?")
x = X4.copy(); x["yon"] = np.where(x.dus, -1, np.where(x.yuk, 1, 0)); x = x[x.yon != 0]
yz = lambda c: x[c] * x.yon
x["sinif"] = np.where(x.z_oi_d <= -1.5, "T tasfiye", np.where(x.z_oi_d >= 1.5, "L yeni kaldıraç", np.where((yz("z_s_imb") >= 1.5) | (yz("z_prim_d") >= 1.5), "S spot/ABD sürdü", "D diğer")))
lcH = np.log(KB.c)
yaz("_K'de her sınıf için ortalama sonraki getiri (hareket yönünde, %) → seçilen yön; sonra test_\n"); baslik()
Y2SEC = []
for yon, yad in ((-1, "düşüş"), (1, "yükseliş")):
    for sn in ("T tasfiye", "L yeni kaldıraç", "S spot/ABD sürdü", "D diğer"):
        ev = x[(x.yon == yon) & (x.sinif == sn)]; gir = ev.index + pd.Timedelta(hours=4)
        for hs in (4, 24, 72):
            i = KB.index.searchsorted(gir); ok = i + hs <= len(KB); fw = pd.Series(np.nan, index=ev.index)
            fw[ok] = np.log(c_[i[ok] + hs - 1] / o_[i[ok]]) * yon
            kk = fw[ev.index < K_END].dropna()
            if len(kk) < 5: continue
            karar = 1 if kk.mean() > 0 else -1                                            # +1 devam, −1 dönüş
            S = pd.DataFrame({"t": gir, "yon": yon * karar})
            kural("Y2", f"4 s {yad} · {sn} · {hs} s · {'DEVAM' if karar == 1 else 'DÖNÜŞ'} (K ort. {100 * kk.mean():+.2f}, n {len(kk)})", S, hs, 30, 0.002 if hs < 24 else 0.005)
for yon, yad in ((-1, "düşüş"), (1, "yükseliş")):
    for et in ("💥", "🎰", "🇺🇸", "🏛️", "🪙", "❓"):
        ev = E[(E.yon == yon) & E.e.apply(lambda l: et in l)]
        if not len(ev): continue
        gir = pd.DatetimeIndex(ev.t) + pd.Timedelta(days=1)
        for hg in (1, 3, 7):
            fw = np.array([yon * np.log(D.c.get(g + pd.Timedelta(days=hg - 1), np.nan) / D.c.get(g - pd.Timedelta(days=1), np.nan)) for g in gir])
            kk = fw[(gir < K_END) & ~np.isnan(fw)]
            if len(kk) < 3: continue
            karar = 1 if kk.mean() > 0 else -1
            kural("Y2", f"büyük gün {yad} {et} · {hg} g · {'DEVAM' if karar == 1 else 'DÖNÜŞ'} (K ort. {100 * kk.mean():+.2f}, n {len(kk)})", pd.DataFrame({"t": gir, "yon": yon * karar}), hg * 24, 30, 0.005)
plasebo("Y2")
# ======================= Y3 =======================
yaz("\n## Y3 — ABD seansının yönü (13:00 → 21:00 UTC = TR 16:00 → 24:00, hafta içi)")
Hh = H.copy(); Hh["fi"] = 2 * Hh.f_al - Hh.f_qv; Hh["si"] = 2 * Hh.s_al - Hh.s_qv
pz720 = zprev(Hh.p, 720)
gunler = pd.date_range(TS("2022-01-03"), TS("2026-10-27"), freq="D"); gunler = gunler[gunler.dayofweek < 5]
Y3 = []
for d in gunler:
    t12, t20, t23p = d + pd.Timedelta(hours=12), d + pd.Timedelta(hours=20), d - pd.Timedelta(hours=1)
    if t20 not in Hh.index or t12 not in Hh.index or t23p not in Hh.index: continue
    w = Hh.loc[d:t12]
    Y3.append(dict(t=d, hedef=np.log(Hh.f_c[t20] / Hh.f_c[t12]), r_asya=np.log(Hh.f_c[t12] / Hh.f_c[t23p]), prim_d=Hh.p[t12] - Hh.p[t23p], prim_z=pz720[t12],
                   fimb=w.fi.sum() / w.f_qv.sum(), simb=w.si.sum() / w.s_qv.sum(), oi_d=Hh.oi[t12] / Hh.oi[t23p] - 1, fon=Hh.fon[t12],
                   asya=np.log(Hh.f_c[d + pd.Timedelta(hours=7)] / Hh.f_c[t23p]), avrupa=np.log(Hh.f_c[t12] / Hh.f_c[d + pd.Timedelta(hours=7)]), gece=np.log(Hh.f_c[d + pd.Timedelta(hours=23)] / Hh.f_c[t20]) if d + pd.Timedelta(hours=23) in Hh.index else np.nan))
Y3 = pd.DataFrame(Y3).set_index("t")
onc = lambda s: s.dropna().reindex(Y3.index - pd.Timedelta(days=1), method="ffill").values   # D'den önceki son ABD günü
Y3["etf_z"] = onc(Z.etf); Y3["nasdaq_d"] = onc(D.nasdaq_r); Y3["dxy_d"] = onc(D.dxy_r); Y3["onceki_abd"] = Y3.hedef.shift(1)
Y3["don"] = donem(Y3.index)
yaz("_bilgi — seansların ortalama getirisi % ve yükselen gün oranı (hafta içi):_")
for ad in DON:
    q = Y3[Y3.don == ad]; yaz(f"- {ad}: Asya 00→08 {100 * q.asya.mean():+.3f} (%{100 * (q.asya > 0).mean():.0f}) · Avrupa 08→13 {100 * q.avrupa.mean():+.3f} (%{100 * (q.avrupa > 0).mean():.0f}) · **ABD 13→21 {100 * q.hedef.mean():+.3f} (%{100 * (q.hedef > 0).mean():.0f})** · gece 21→24 {100 * q.gece.mean():+.3f} (%{100 * (q.gece > 0).mean():.0f})")
V3 = {"r_asya": "00→13 getiri", "prim_d": "Coinbase primi 00→13 değişim", "prim_z": "Coinbase primi z (12:00)", "fimb": "vadeli agresif 00→13", "simb": "spot agresif 00→13",
      "oi_d": "açık poz. 00→13", "fon": "fonlama", "etf_z": "önceki gün ETF akışı z", "nasdaq_d": "önceki gün Nasdaq", "dxy_d": "önceki gün dolar", "onceki_abd": "önceki ABD seansı"}
yaz(""); baslik()
gir13 = Y3.index + pd.Timedelta(hours=13)
for v, vad in V3.items():
    s = Y3[v]; ilk = (Y3.don == ("C1 2024" if v == "etf_z" else "K 2022–23")); qa, qb = s[ilk].quantile(0.2), s[ilk].quantile(0.8)
    for kad, m in (("alt %20", s <= qa), ("üst %20", s > qb)):
        mm = m & ilk; kar = 1 if Y3.hedef[mm].mean() > 0 else -1
        kural("Y3", f"{vad} {kad} → {'AL' if kar == 1 else 'SAT'} (K ort. {100 * Y3.hedef[mm].mean():+.3f})", pd.DataFrame({"t": gir13[m.values], "yon": kar}), 8, 30, 0.002)
F3 = Y3[["r_asya", "prim_d", "prim_z", "fimb", "simb", "oi_d", "fon", "nasdaq_d", "dxy_d", "onceki_abd"]]; sig = []
for a, b_, eb in ((TS("2022-01-01"), K_END, K_END), (K_END, C1_END, K_END), (C1_END, TS("2026-10-28"), C1_END)):
    tr = (F3.index < eb) & Y3.hedef.notna().values; mdl = ridge_fit(F3[tr], Y3.hedef[tr]); ptr = ridge_pred(mdl, F3[tr]); q20, q80 = ptr.quantile(0.2), ptr.quantile(0.8)
    te = (F3.index >= a) & (F3.index < b_); p = ridge_pred(mdl, F3[te]); gi = p.index + pd.Timedelta(hours=13)
    sig += [pd.DataFrame({"t": gi[(p >= q80).values], "yon": 1}), pd.DataFrame({"t": gi[(p <= q20).values], "yon": -1})]
kural("Y3", "bileşik ABD seansı skoru (ridge)", pd.concat(sig), 8, 30, 0.002)
plasebo("Y3")
# ======================= Y4 =======================
yaz("\n## Y4 — Hafta sonu ve CME boşluğu")
cum = KB.index[(KB.index.dayofweek == 4) & (KB.index.hour == 21)]; W = []
for f in cum:
    s_ = f + pd.Timedelta(hours=50); fs = f + pd.Timedelta(days=7)
    if s_ not in KB.index or fs not in KB.index: continue
    F_, S_ = KB.o[f], KB.o[s_]; hf = KB.loc[s_ + pd.Timedelta(hours=1):fs]; g = S_ / F_ - 1
    dol = (hf.l.min() <= F_) if g > 0 else (hf.h.max() >= F_)
    W.append(dict(t=f, gap=g, dolum=dol, cuma_abd=np.log(KB.c[f - pd.Timedelta(hours=1)] / KB.c[f - pd.Timedelta(hours=9)]), hs=np.log(S_ / F_), pzt=np.log(KB.c[s_ + pd.Timedelta(hours=22)] / S_)))
W = pd.DataFrame(W).set_index("t"); W["don"] = donem(W.index)
yaz("_hafta içinde fiyatın cuma 21:00 seviyesine geri dönme oranı (boşluk büyüklüğüne göre):_")
yaz("| |boşluk| | K 2022–23 | C1 2024 | C2 2025–26 |"); yaz("|---|---|---|---|")
for a, b_ in ((0, 0.005), (0.005, 0.01), (0.01, 0.02), (0.02, 0.03), (0.03, 1)):
    yaz(f"| %{100 * a:.1f}–{'%' + format(100 * b_, '.0f') if b_ < 1 else '…'} | " + " | ".join(f"%{100 * q.dolum.mean():.0f} ({len(q)})" if len(q) else "—" for q in (W[(W.don == ad) & (W.gap.abs() >= a) & (W.gap.abs() < b_)] for ad in DON)) + " |")
yaz(""); baslik()
for stop in (None, "boşluk"):
    R = []
    for t, r_ in W[W.gap.abs() >= 0.01].iterrows():
        s_ = t + pd.Timedelta(hours=50); i = KB.index.searchsorted(s_); yon = -1 if r_.gap > 0 else 1; T = abs(KB.o.iloc[i] / KB.o[t] - 1) - 0.001
        if T <= 0: continue
        net, j = N.islem(KB, i, yon, T, (T if stop else None), 118); R.append((s_, yon, yon * (KB.c.iloc[j] / KB.o.iloc[i] - 1), net))
    R = pd.DataFrame(R, columns=["t", "yon", "ham", "net"]); R["don"] = donem(R.t); hs, yok, aok = ozet(R, 15, 0.005)
    yaz(f"| boşluk ≥ %1 → F'ye doğru · 🎯 F · stop {'yok' if stop is None else 'boşluk kadar'} | " + " | ".join(hs) + f" | {'🎯' if aok else ('✅' if yok else '')} |")
    SONUC.append(("Y4", f"CME boşluğu stop {stop}", None, 118, 15, 0.005, yok, aok))
for ad in DON:
    q = W[W.don == ad]; yaz(f"- {ad}: cuma ABD seansı ile hafta sonu aynı yönde %{100 * (np.sign(q.cuma_abd) == np.sign(q.hs)).mean():.0f} · hafta sonu ile pazartesi aynı yönde %{100 * (np.sign(q.hs) == np.sign(q.pzt)).mean():.0f} (n {len(q)})")
# ======================= Y5 =======================
yaz("\n## Y5 — Makine öğrenmesi yön modeli (LightGBM, aylık yürüyen eğitim)")
Bh = B.reindex(X.index.floor("D")).set_index(X.index); Bh.columns = ["g_" + c for c in Bh.columns]
F5 = pd.concat([X[[c for c in X.columns if not c.startswith("saat")]], Bh], axis=1); F5["saat"] = F5.index.hour; F5["gun"] = F5.index.dayofweek
F5 = F5.replace([np.inf, -np.inf], np.nan).astype("float32")
lcK = np.log(KB.c); P5 = dict(objective="binary", learning_rate=0.03, num_leaves=15, min_data_in_leaf=200, feature_fraction=0.8, bagging_fraction=0.8, bagging_freq=1, verbose=-1, seed=5, num_threads=2)
AY5 = pd.date_range("2023-01-01", "2026-10-01", freq="MS", tz="UTC")
baslik()
for hs in (4, 24):
    yy = (lcK.shift(-hs) - lcK).reindex(F5.index); lab = (yy > 0).astype(float).where(yy.notna())
    for plas in (False, True):
        sig = []; rng = np.random.default_rng(9)
        for m in AY5:
            tr = (F5.index < m - pd.Timedelta(hours=hs + 1)) & lab.notna().values
            yt = lab[tr].values.copy()
            if plas: rng.shuffle(yt)
            mdl = lgb.train(P5, lgb.Dataset(F5[tr].values, label=yt), num_boost_round=250)
            ptr = mdl.predict(F5[tr].values); q10, q90 = np.quantile(ptr, [0.1, 0.9])
            te = (F5.index >= m) & (F5.index < m + pd.DateOffset(months=1)); p = mdl.predict(F5[te].values); ti = F5.index[te] + pd.Timedelta(hours=1)
            sig += [pd.DataFrame({"t": ti[p >= q90], "yon": 1}), pd.DataFrame({"t": ti[p <= q10], "yon": -1})]
        S = pd.concat(sig); ad = f"{'PLASEBO ' if plas else ''}model {hs} s (yalnız 2023 K'de)"
        kural("Y5" + ("p" if plas else ""), ad, S, hs, 30, 0.002 if hs < 24 else 0.005)
        print(ad, f"{time.time() - T0:.0f} sn", flush=True)
# ======================= Y6 =======================
yaz("\n## Y6 — Öncü coin ve akış (son saat → BTC'nin sonraki 1 s / 4 s)")
v6 = pd.DataFrame(index=KB.index)
for c_n, K_ in KD.items(): v6[c_n.lower() + "_r"] = np.log(K_.c / K_.o).reindex(KB.index)
v6["prim_d"] = H.p.diff(); v6["fimb"] = (2 * H.f_al - H.f_qv) / H.f_qv; v6["simb"] = (2 * H.s_al - H.s_qv) / H.s_qv; v6["btc_r"] = np.log(KB.c / KB.o)
v6["eth_fark"] = v6.eth_r - v6.btc_r
v6 = v6[v6.index < N.SON - pd.Timedelta(hours=6)]; dn6 = donem(v6.index)
A6 = {"eth_r": "ETH son saat", "sol_r": "SOL son saat", "eth_fark": "ETH − BTC son saat", "prim_d": "Coinbase primi son saat Δ", "fimb": "vadeli agresif son saat", "simb": "spot agresif son saat"}
baslik()
for hs in (1, 4):
    fw = (np.log(KB.c.shift(-hs) / KB.o.shift(-1))).reindex(v6.index)
    for v, vad in A6.items():
        s = v6[v]; k = dn6 == "K 2022–23"; qa, qb = s[k].quantile(0.2), s[k].quantile(0.8)
        for kad, m in (("alt %20", s <= qa), ("üst %20", s > qb)):
            kar = 1 if fw[m & k].mean() > 0 else -1
            kural("Y6", f"{vad} {kad} → {hs} s {'AL' if kar == 1 else 'SAT'}", pd.DataFrame({"t": v6.index[m.values] + pd.Timedelta(hours=1), "yon": kar}), hs, 30, 0.002)
for a in ("Y2", "Y3", "Y6"): pass
plasebo("Y6", n=10)
# ======================= özet =======================
yaz("\n## Özet")
for a in ("Y1", "Y2", "Y3", "Y4", "Y5", "Y5p", "Y6"):
    k = [s for s in SONUC if s[0] == a]; yaz(f"- {a}: {len(k)} kural · yön şartı ✅ {sum(s[6] for s in k)} · sinyal adayı 🎯 {sum(s[7] for s in k)}" + ("".join(f"\n  - {'🎯' if s[7] else '✅'} {s[1]}" for s in k if s[6] or s[7])))
GEC = [s for s in SONUC if (s[6] or s[7]) and s[2] is not None and not s[0].endswith("p") and s[0] != "Y1-bilgi"]
if GEC:
    yaz("\n_ETH ve SOL'da aynı kural (BTC'nin durumuyla, 2024 → 2026):_")
    for a, ad, sig, nsaat, *_ in GEC:
        p = []
        for cn, K_ in KD.items():
            R = degerlendir(sig[sig.t >= K_END], nsaat, K_); p.append(f"{cn} {len(R)} · yön %{100 * (R.ham > 0).mean():.0f} · {100 * R.net.mean():+.2f}" if len(R) else f"{cn} 0")
        yaz(f"- {a} {ad}: " + " ‖ ".join(p))
yaz(f"\n_süre {time.time() - T0:.0f} sn_")
open("btcyon_sonuc.md", "w").write("\n".join(out) + "\n")
