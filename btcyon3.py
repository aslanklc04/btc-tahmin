# btcyon3.py — PROTOKOL_btcyon3.md: ZAMAN + YÖN (Z1 model + pencere · Z2 uyumsuzluk + filtre · Z3 büyük hareketin yönü · Z4 skor + trend) → btcyon3_sonuc.md
import io, time, contextlib, numpy as np, pandas as pd
with contextlib.redirect_stdout(io.StringIO()): import btcneden as N
import lightgbm as lgb
T0 = time.time(); out = []
def yaz(s=""): out.append(s); print(s, flush=True)
TS = lambda s: pd.Timestamp(s, tz="UTC")
H, B, D, X, KB, KD = N.H, N.B, N.D, N.X, N.KB, N.KD
DON = [("K 2022–23", "2022-01-01", "2024-01-01"), ("C1 2024", "2024-01-01", "2025-01-01"), ("C2 2025–26", "2025-01-01", "2026-10-28")]
K_END, C1_END = TS("2024-01-01"), TS("2025-01-01")
def donem(ix):
    ix = pd.DatetimeIndex(ix); d = np.full(len(ix), None, object)
    for ad, a, b in DON: d[(ix >= TS(a)) & (ix < TS(b))] = ad
    return d
o_, c_, fp_ = KB.o.values, KB.c.values, np.nan_to_num(KB.fonp.values)
def deg(sig, nsaat, maker=False):
    R = []; serbest = None; ix = KB.index
    for t, yon in sig.sort_values("t")[["t", "yon"]].itertuples(index=False):
        if serbest is not None and t < serbest: continue
        i = ix.searchsorted(t)
        if i >= len(ix) or ix[i] != t or i + nsaat > len(ix): continue
        j = i + nsaat - 1; Pe = o_[i] * (1 if maker else 1 + 0.001 * yon); fon = fp_[i + 1:j + 1].sum()
        net = yon * (c_[j] / Pe - 1) - (0.0004 if maker else 0.001) - yon * fon
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
def kural(aile, ad, sig, nsaat, minn=30, esik=None, maker_bilgi=False):
    esik = esik if esik is not None else (0.002 if nsaat < 24 else 0.005)
    R = deg(sig, nsaat); hs, yok, aok = ozet(R, minn, esik)
    ek = ""
    if maker_bilgi: ek = " ‖ limit emirle net: " + " · ".join(f"{100 * x.net.mean():+.2f}" if len(x) else "—" for x in (Rm[Rm.don == a] for Rm in [deg(sig, nsaat, True)] for a, _, _ in DON))
    yaz(f"| {ad} | " + " | ".join(hs) + f" | {'🎯' if aok else ('✅' if yok else '')} |{ek}"); SONUC.append((aile, ad, sig, nsaat, minn, esik, yok, aok)); return yok
def baslik(): yaz("| kural | K | C1 2024 | C2 2025–26 | |"); yaz("|---|---|---|---|---|")
def plasebo(aile, n=20, seed=8):
    rng = np.random.default_rng(seed); kur = [s for s in SONUC if s[0] == aile]; a0, a1 = KB.index[0], KB.index[-1]; span = int((a1 - a0).total_seconds() // 3600); say = []
    for _ in range(n):
        off = pd.Timedelta(hours=int(rng.integers(90 * 24, span - 90 * 24))); g = 0
        for _, _, sig, nsaat, minn, esik, _, _ in kur:
            t = sig.t + off; t = t.where(t <= a1, t - pd.Timedelta(hours=span + 1)); g += ozet(deg(pd.DataFrame({"t": t.dt.floor("h"), "yon": sig.yon.values}), nsaat), minn, esik)[1]
        say.append(g)
    yaz(f"\n**{aile}: yön şartı ✅ {sum(s[6] for s in kur)} / {len(kur)} · sinyal adayı {sum(s[7] for s in kur)}** · plasebo (zaman kaydırma ×{n}) ortalama {np.mean(say):.1f}, en çok {max(say)}")
yaz("# 🧭 BTC'nin YÖNÜ — 3. tur: ZAMAN + YÖN · PROTOKOL_btcyon3.md")
yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · hücre: işlem · yön isabeti · isabet (masraf sonrası kâr) · işlem başı net % · ✅ yön şartı · 🎯 sinyal adayı_\n")
# ---- hareket penceresi P ----
dnX = donem(X.index); vthr = X.vr[dnX == "K 2022–23"].quantile(0.7)
P = ((X.vr >= vthr) | (X.saat3 == 1)).fillna(False); yaz(f"_Hareket penceresi P: oynaklık oranı ≥ {vthr:.2f} (K üst %30) veya sonraki blok 12–16 UTC · saatlerin %{100 * P.mean():.0f}'i_\n")
# ---- özellikler (btcyon Y5 ile aynı) ----
Bh = B.reindex(X.index.floor("D")).set_index(X.index); Bh.columns = ["g_" + c for c in Bh.columns]
F5 = pd.concat([X[[c for c in X.columns if not c.startswith("saat")]], Bh], axis=1); F5["saat"] = F5.index.hour; F5["gun"] = F5.index.dayofweek
F5 = F5.replace([np.inf, -np.inf], np.nan).astype("float32"); lcK = np.log(KB.c)
PR = dict(objective="binary", learning_rate=0.03, num_leaves=15, min_data_in_leaf=200, feature_fraction=0.8, bagging_fraction=0.8, bagging_freq=1, verbose=-1, seed=5, num_threads=2)
AY = pd.date_range("2023-01-01", "2026-10-01", freq="MS", tz="UTC")
def yuru(lab, egit_maske, q, plas, mdl_min=200):
    """Aylık yürüyen eğitim → (tahmin serisi, alt eşik serisi, üst eşik serisi)"""
    p = pd.Series(np.nan, index=F5.index); lo = p.copy(); hi = p.copy(); rng = np.random.default_rng(9); pr = dict(PR, min_data_in_leaf=mdl_min)
    for m in AY:
        tr = (F5.index < m - pd.Timedelta(hours=25)) & lab.notna().values & egit_maske
        yt = lab[tr].values.copy()
        if plas: rng.shuffle(yt)
        md = lgb.train(pr, lgb.Dataset(F5[tr].values, label=yt), num_boost_round=250); ptr = md.predict(F5[tr].values)
        te = (F5.index >= m) & (F5.index < m + pd.DateOffset(months=1)); p[te] = md.predict(F5[te].values); lo[te], hi[te] = np.quantile(ptr, [q, 1 - q])
    return p, lo, hi
# ======================= Z1 =======================
yaz("## Z1 — Yön modeli (btcyon Y5) yalnız hareket penceresinde (K = yalnız 2023)"); baslik()
for hs in (4, 24):
    yy = (lcK.shift(-hs) - lcK).reindex(F5.index); lab = (yy > 0).astype(float).where(yy.notna())
    for plas in (False, True):
        p, lo, hi = yuru(lab, np.ones(len(F5), bool), 0.1, plas); ti = F5.index + pd.Timedelta(hours=1)
        for pad, pm in (("tüm saatler", np.ones(len(F5), bool)), ("yalnız P", P.values)):
            S = pd.concat([pd.DataFrame({"t": ti[(p >= hi).values & pm], "yon": 1}), pd.DataFrame({"t": ti[(p <= lo).values & pm], "yon": -1})])
            kural("Z1p" if plas else "Z1", f"{'PLASEBO ' if plas else ''}model {hs} s · {pad}", S, hs, maker_bilgi=not plas)
        print(f"Z1 {hs} {plas} {time.time() - T0:.0f} sn", flush=True)
# ======================= Z2 =======================
yaz("\n## Z2 — Vadeli uyumsuzluk + kalabalık + trend + pencere (yön mantıktan sabit)")
cvd = (2 * H.f_al - H.f_qv).fillna(0).cumsum(); cc = H.f_c
mn72, mx72 = cc.rolling(72).min(), cc.rolling(72).max(); onc_min, onc_max = cc.shift(24).rolling(48).min(), cc.shift(24).rolling(48).max()
ixmin = cc.shift(24).rolling(48).apply(np.argmin, raw=True); ixmax = cc.shift(24).rolling(48).apply(np.argmax, raw=True); n = np.arange(len(H))
def deger(seri, j):
    j = (n - 71 + j.values).astype(float); v = np.full(len(j), np.nan); ok = ~np.isnan(j) & (j >= 0); v[ok] = seri.values[j[ok].astype(int)]; return v
pos = ((cc <= mn72) & (cc < onc_min)).values & (cvd.values > deger(cvd, ixmin)); neg = ((cc >= mx72) & (cc > onc_max)).values & (cvd.values < deger(cvd, ixmax))
lsz = N.zprev(B.ls, 180).reindex(H.index.floor("D")).values; ma200 = D.c.rolling(200).mean().shift(1); trend = (D.c.shift(1) > ma200).reindex(H.index.floor("D")).values
Ph = P.reindex(H.index).fillna(False).values
baslik()
for hs in (24, 72):
    for fad, fs, fa in (("filtresiz", np.ones(len(H), bool), np.ones(len(H), bool)), ("a kalabalık", lsz >= 0, lsz <= 0), ("b trend", trend == False, trend == True),
                        ("c pencere", Ph, Ph), ("a+b", (lsz >= 0) & (trend == False), (lsz <= 0) & (trend == True)), ("a+b+c", (lsz >= 0) & (trend == False) & Ph, (lsz <= 0) & (trend == True) & Ph)):
        S = pd.concat([pd.DataFrame({"t": H.index[neg & fs] + pd.Timedelta(hours=1), "yon": -1}), pd.DataFrame({"t": H.index[pos & fa] + pd.Timedelta(hours=1), "yon": 1})])
        kural("Z2", f"uyumsuzluk (SAT+AL) · {fad} · {hs} s", S, hs, 30)
        kural("Z2", f"yalnız negatif → SAT · {fad} · {hs} s", pd.DataFrame({"t": H.index[neg & fs] + pd.Timedelta(hours=1), "yon": -1}), hs, 30)
plasebo("Z2")
# ======================= Z3 =======================
yaz("\n## Z3 — Büyük hareketin yönü modeli (yalnız büyük hareket saatlerinde eğitilir; işlem P içinde)"); baslik()
YH = N.YH.reindex(F5.index); buyuk = ((YH.dus == 1) | (YH.yuk == 1)).values; lab3 = YH.yuk.where(buyuk)
for plas in (False, True):
    p, lo, hi = yuru(lab3, buyuk, 0.2, plas, mdl_min=30); ti = F5.index + pd.Timedelta(hours=1)
    S = pd.concat([pd.DataFrame({"t": ti[(p >= hi).values & P.values], "yon": 1}), pd.DataFrame({"t": ti[(p <= lo).values & P.values], "yon": -1})])
    kural("Z3p" if plas else "Z3", f"{'PLASEBO ' if plas else ''}büyük hareket yön modeli · 4 s · P içinde", S, 4, maker_bilgi=not plas)
# ======================= Z4 =======================
yaz("\n## Z4 — Günlük bileşik skor (btcyon Y1) yalnız trend yönünde"); baslik()
F1 = B[["ls", "top_ls", "fon3", "oi7", "fimb3", "simb3", "prim3", "prim_d3", "dvol3", "sikisma", "zirve30", "r7", "stabil7", "borsa7z", "nasdaq5", "dxy5", "faiz5", "vix", "korku"]].copy()
for c in ("ls", "top_ls", "fon3", "prim3", "vix", "korku"): F1[c] = N.zprev(F1[c], 180)
lc = np.log(D.c); trD = (D.c.shift(1) > ma200)
def rf(Xt, yt, lam=10.0):
    m, s = Xt.mean(), Xt.std().replace(0, 1); Xs = ((Xt - m) / s).fillna(0).values; b = np.linalg.solve(Xs.T @ Xs + lam * np.eye(Xs.shape[1]), Xs.T @ (yt.values - yt.mean())); return m, s, b, yt.mean()
def rp(md, Xx): m, s, b, a = md; return pd.Series(((Xx - m) / s).fillna(0).values @ b + a, index=Xx.index)
for h in (1, 3, 7):
    y = lc.shift(-(h - 1)) - lc.shift(1); sig = []
    for a, b_, eb in ((TS("2022-01-01"), K_END, K_END), (K_END, C1_END, K_END), (C1_END, TS("2026-10-28"), C1_END)):
        tr = (F1.index < eb - pd.Timedelta(days=h)) & y.notna().values; md = rf(F1[tr], y[tr]); ptr = rp(md, F1[tr]); q20, q80 = ptr.quantile(0.2), ptr.quantile(0.8)
        te = (F1.index >= a) & (F1.index < b_); p = rp(md, F1[te]); tt = trD.reindex(p.index).fillna(False).astype(bool)
        sig += [pd.DataFrame({"t": p.index[(p >= q80) & tt], "yon": 1}), pd.DataFrame({"t": p.index[(p <= q20) & ~tt], "yon": -1})]
    kural("Z4", f"skor {h} g · yalnız trend yönünde", pd.concat(sig), h * 24, 30)
plasebo("Z4")
yaz("\n## Özet")
for a in ("Z1", "Z1p", "Z2", "Z3", "Z3p", "Z4"):
    k = [s for s in SONUC if s[0] == a]; yaz(f"- {a}: {len(k)} kural · yön ✅ {sum(s[6] for s in k)} · sinyal adayı 🎯 {sum(s[7] for s in k)}" + "".join(f"\n  - {'🎯' if s[7] else '✅'} {s[1]}" for s in k if s[6] or s[7]))
GEC = [s for s in SONUC if (s[6] or s[7]) and not s[0].endswith("p")]
if GEC:
    yaz("\n_ETH ve SOL'da aynı BTC sinyali (2024 → 2026):_")
    for a, ad, sig, nsaat, *_ in GEC:
        p = []
        for cn, K_ in KD.items():
            R = []; serbest = None; ix = K_.index
            for t, yon in sig[sig.t >= K_END].sort_values("t")[["t", "yon"]].itertuples(index=False):
                if serbest is not None and t < serbest: continue
                i = ix.searchsorted(t)
                if i >= len(ix) or ix[i] != t or i + nsaat > len(ix): continue
                net, j = N.islem(K_, i, int(yon), 10.0, None, nsaat); R.append((yon * (K_.c.iloc[i + nsaat - 1] / K_.o.iloc[i] - 1), net)); serbest = ix[j] + pd.Timedelta(hours=1)
            R = np.array(R); p.append(f"{cn} {len(R)} · yön %{100 * (R[:, 0] > 0).mean():.0f} · {100 * R[:, 1].mean():+.2f}" if len(R) else f"{cn} 0")
        yaz(f"- {a} {ad}: " + " ‖ ".join(p))
yaz(f"\n_süre {time.time() - T0:.0f} sn_")
open("btcyon3_sonuc.md", "w").write("\n".join(out) + "\n")
