# btcyon4.py — PROTOKOL_btcyon4.md: W1 balina · W2 Kore primi · W3 stablecoin talebi · W4 birleşik → btcyon4_sonuc.md
import io, time, contextlib, numpy as np, pandas as pd
with contextlib.redirect_stdout(io.StringIO()): import btcneden as N
T0 = time.time(); out = []
def yaz(s=""): out.append(s); print(s, flush=True)
TS = lambda s: pd.Timestamp(s, tz="UTC")
H, B, D, KB, KD = N.H, N.B, N.D, N.KB, N.KD
DON = [("K 2022–23", "2022-01-01", "2024-01-01"), ("C1 2024", "2024-01-01", "2025-01-01"), ("C2 2025–26", "2025-01-01", "2026-10-28")]
K_END, C1_END = TS("2024-01-01"), TS("2025-01-01")
def donem(ix):
    ix = pd.DatetimeIndex(ix); d = np.full(len(ix), None, object)
    for ad, a, b in DON: d[(ix >= TS(a)) & (ix < TS(b))] = ad
    return d
o_, c_, fp_ = KB.o.values, KB.c.values, np.nan_to_num(KB.fonp.values)
def deg(sig, nsaat):
    R = []; serbest = None; ix = KB.index
    for t, yon in sig.sort_values("t")[["t", "yon"]].itertuples(index=False):
        if serbest is not None and t < serbest: continue
        i = ix.searchsorted(t)
        if i >= len(ix) or ix[i] != t or i + nsaat > len(ix): continue
        j = i + nsaat - 1; Pe = o_[i] * (1 + 0.001 * yon); net = yon * (c_[j] / Pe - 1) - 0.001 - yon * fp_[i + 1:j + 1].sum()
        R.append((t, yon, yon * (c_[j] / o_[i] - 1), net)); serbest = ix[j] + pd.Timedelta(hours=1)
    R = pd.DataFrame(R, columns=["t", "yon", "ham", "net"]); R["don"] = donem(R.t) if len(R) else []; return R
def ozet(R, minn, esik):
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
def kural(aile, ad, sig, nsaat, minn=30):
    esik = 0.002 if nsaat < 24 else 0.005; hs, yok, aok = ozet(deg(sig, nsaat), minn, esik)
    yaz(f"| {ad} | " + " | ".join(hs) + f" | {'🎯' if aok else ('✅' if yok else '')} |"); SONUC.append((aile, ad, sig, nsaat, minn, esik, yok, aok))
def baslik(): yaz("| kural | K 2022–23 | C1 2024 | C2 2025–26 | |"); yaz("|---|---|---|---|---|")
def plasebo(aile, n=20, seed=12):
    rng = np.random.default_rng(seed); kur = [s for s in SONUC if s[0] == aile]; a0, a1 = KB.index[0], KB.index[-1]; span = int((a1 - a0).total_seconds() // 3600); say = []
    for _ in range(n):
        off = pd.Timedelta(hours=int(rng.integers(90 * 24, span - 90 * 24))); g = 0
        for _, _, sig, nsaat, minn, esik, _, _ in kur:
            t = sig.t + off; t = t.where(t <= a1, t - pd.Timedelta(hours=span + 1)); g += ozet(deg(pd.DataFrame({"t": t.dt.floor("h"), "yon": sig.yon.values}), nsaat), minn, esik)[1]
        say.append(g)
    yaz(f"\n**{aile}: yön şartı ✅ {sum(s[6] for s in kur)} / {len(kur)} · sinyal adayı {sum(s[7] for s in kur)}** · plasebo (zaman kaydırma ×{n}) ortalama {np.mean(say):.1f}, en çok {max(say)}")
dn = donem(KB.index); kK = dn == "K 2022–23"
def esikli(aile, ad, v, ufuklar):
    for hs in ufuklar:
        fw = np.log(KB.c.shift(-hs) / KB.o.shift(-1)); qa, qb = v[kK].quantile(0.2), v[kK].quantile(0.8)
        for kad, m in (("alt %20", v <= qa), ("üst %20", v > qb)):
            m = m.fillna(False); kar = 1 if fw[m & kK].mean() > 0 else -1
            kural(aile, f"{ad} {kad} → {hs} s {'AL' if kar == 1 else 'SAT'} (K ort. {100 * fw[m & kK].mean():+.2f})", pd.DataFrame({"t": KB.index[m.values] + pd.Timedelta(hours=1), "yon": kar}), hs)
zp = lambda s, n=720: (s - s.rolling(n, min_periods=n // 2).mean().shift(1)) / s.rolling(n, min_periods=n // 2).std().shift(1)
yaz("# 🧭 BTC'nin YÖNÜ — 4. tur: balina · Kore · stablecoin · PROTOKOL_btcyon4.md")
yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · hücre: işlem · yön isabeti · isabet (masraf sonrası kâr) · işlem başı net % · ✅ yön şartı · 🎯 sinyal adayı_\n")
# ======================= W1 =======================
W = pd.read_parquet("btcyon4_balina.parquet").set_index("t").sort_index().reindex(KB.index)
yaz(f"## W1 — Balina agresif emirleri (balina dakikaları hacmin ort. %{100 * (W.wq / W.qv).mean():.1f}'i)")
wn = 2 * W.wtb - W.wq
F = pd.DataFrame(index=KB.index)
F["imb4"] = wn.rolling(4).sum() / W.wq.rolling(4).sum(); F["imb24"] = wn.rolling(24).sum() / W.wq.rolling(24).sum(); F["wnet24z"] = zp(wn.rolling(24).sum())
F["kucuk24"] = ((2 * W.tb - W.qv) - wn).rolling(24).sum() / (W.qv - W.wq).rolling(24).sum()            # balina dışı (küçük) agresif dengesizlik — bilgi/karşılaştırma
baslik()
for v, ad in (("imb4", "balina dengesizliği 4 s"), ("imb24", "balina dengesizliği 24 s"), ("wnet24z", "balina net 24 s z"), ("kucuk24", "küçük emir dengesizliği 24 s (karşılaştırma)")):
    esikli("W1", ad, F[v], (4, 24, 72))
plasebo("W1")
# ======================= W2 =======================
A = pd.read_parquet("btcyon4_akis.parquet").set_index("t").sort_index().reindex(KB.index)
try:
    kr = pd.read_parquet("btcyon4_kur.parquet").set_index("gun").usdkrw.sort_index(); kur = kr.shift(1).reindex(KB.index.floor("D"), method="ffill").values   # önceki günün kuru (temkinli)
except Exception: kur = np.full(len(KB), np.nan)
yaz("\n## W2 — Kore primi (Upbit KRW-BTC / Binance × USD/KRW)")
if "up_c" in A and np.isfinite(kur).any():
    kim = A.up_c / (H.s_c.reindex(KB.index) * kur) - 1; F["kim"] = kim
    yaz(f"_Kore primi: dolu %{100 * kim.notna().mean():.0f} · medyan %{100 * kim.median():.2f} · K %5–%95: %{100 * kim[kK].quantile(0.05):.2f} … %{100 * kim[kK].quantile(0.95):.2f}_"); baslik()
    k24 = kim.rolling(24).mean(); F["kz"] = zp(k24); F["kd24"] = kim - kim.shift(24)
    esikli("W2", "Kore primi z", F.kz, (24, 72)); esikli("W2", "Kore primi 24 s değişim", F.kd24, (24, 72)); esikli("W2", "Kore primi seviye", kim.rolling(72).mean(), (24, 72))
    plasebo("W2")
else: yaz("Kore verisi alınamadı.")
# ======================= W3 =======================
yaz("\n## W3 — Stablecoin talebi (Coinbase USDT-USD − 1)")
if "usdt_c" in A:
    us = A.usdt_c - 1; F["uz"] = zp(us.rolling(24).mean()); F["ud24"] = us - us.shift(24)
    yaz(f"_USDT primi: dolu %{100 * us.notna().mean():.0f} · medyan {1e4 * us.median():+.1f} baz puan_"); baslik()
    esikli("W3", "USDT primi z", F.uz, (24, 72)); esikli("W3", "USDT primi 24 s değişim", F.ud24, (24, 72)); plasebo("W3")
else: yaz("USDT verisi alınamadı.")
# ======================= W4 =======================
yaz("\n## W4 — Birleşik (ridge, 24 s): balina + Kore + USDT + kalabalık L/S + dolar + vadeli uyumsuzluk")
cvd = (2 * H.f_al - H.f_qv).fillna(0).cumsum(); cc = H.f_c; n = np.arange(len(H))
mn72, mx72 = cc.rolling(72).min(), cc.rolling(72).max(); om, oM = cc.shift(24).rolling(48).min(), cc.shift(24).rolling(48).max()
im, iM = cc.shift(24).rolling(48).apply(np.argmin, raw=True), cc.shift(24).rolling(48).apply(np.argmax, raw=True)
def deger(seri, j):
    j = (n - 71 + j.values).astype(float); v = np.full(len(j), np.nan); ok = ~np.isnan(j) & (j >= 0); v[ok] = seri.values[j[ok].astype(int)]; return v
F["posdiv"] = (((cc <= mn72) & (cc < om)).values & (cvd.values > deger(cvd, im))).astype(float)[:len(F)] if len(H) == len(F) else 0.0
F["negdiv"] = (((cc >= mx72) & (cc > oM)).values & (cvd.values < deger(cvd, iM))).astype(float)[:len(F)] if len(H) == len(F) else 0.0
F["lsz"] = N.zprev(B.ls, 180).reindex(KB.index.floor("D")).values; F["dxy5"] = B.dxy5.reindex(KB.index.floor("D")).values
cols = [c for c in ("imb4", "imb24", "wnet24z", "kz", "kd24", "uz", "ud24", "lsz", "dxy5", "posdiv", "negdiv") if c in F]
y = (np.log(KB.c.shift(-24) / KB.o.shift(-1))); sig = []
def rf(Xt, yt, lam=10.0):
    m, s = Xt.mean(), Xt.std().replace(0, 1); Xs = ((Xt - m) / s).fillna(0).values; return m, s, np.linalg.solve(Xs.T @ Xs + lam * np.eye(Xs.shape[1]), Xs.T @ (yt.values - yt.mean())), yt.mean()
def rp(md, Xx): m, s, b, a = md; return pd.Series(((Xx - m) / s).fillna(0).values @ b + a, index=Xx.index)
for a, b_, eb in ((TS("2022-01-01"), K_END, K_END), (K_END, C1_END, K_END), (C1_END, TS("2026-10-28"), C1_END)):
    tr = (F.index < eb - pd.Timedelta(hours=25)) & y.notna().values & (F.index >= TS("2022-01-01")); md = rf(F.loc[tr, cols], y[tr]); ptr = rp(md, F.loc[tr, cols]); q10, q90 = ptr.quantile(0.1), ptr.quantile(0.9)
    te = (F.index >= a) & (F.index < b_); p = rp(md, F.loc[te, cols]); ti = p.index + pd.Timedelta(hours=1)
    sig += [pd.DataFrame({"t": ti[(p >= q90).values], "yon": 1}), pd.DataFrame({"t": ti[(p <= q10).values], "yon": -1})]
    if a == K_END: yaz("_K modelinin katsayıları (24 s getiri, baz puan / 1 std): " + ", ".join(f"{c} {1e4 * v:+.1f}" for c, v in zip(cols, md[2])) + "_")
baslik(); kural("W4", "birleşik skor üst/alt %10 → 24 s", pd.concat(sig), 24); plasebo("W4")
yaz("\n## Özet")
for a in ("W1", "W2", "W3", "W4"):
    k = [s for s in SONUC if s[0] == a]; yaz(f"- {a}: {len(k)} kural · yön ✅ {sum(s[6] for s in k)} · sinyal adayı 🎯 {sum(s[7] for s in k)}" + "".join(f"\n  - {'🎯' if s[7] else '✅'} {s[1]}" for s in k if s[6] or s[7]))
yaz(f"\n_süre {time.time() - T0:.0f} sn_")
open("btcyon4_sonuc.md", "w").write("\n".join(out) + "\n")
