# bist.py — PROTOKOL_bist.md: BIST fizibilite (taban · 250 teknik kombinasyon × 4 çıkış · model · plasebo), saatlik ve günlük → bist_sonuc.md
import sys, time, numpy as np, pandas as pd
from numba import njit
from sklearn.ensemble import HistGradientBoostingClassifier
T0 = time.time(); out = []
def yaz(s=""): out.append(s); print(s, flush=True)
FP, SLIP = 0.0005, 0.0005                                                                       # komisyon+BSMV / taraf · kayma (piyasa giriş, süre/stop çıkış)
def ema(x, n): return x.ewm(span=n, adjust=False).mean()
cx = lambda a, b: (a > b) & (a.shift() <= b.shift())

@njit(cache=True)
def cikis(o, h, l, c, U, X, sig, atr, W, mult, tip):
    """i+1 açılışında giriş → (dolar net, TL net, XU030'a göre fazla, çıkış indeksi, 🎯 vurdu). tip 0: 🎯 mult·σ, en fazla W mum · 1: 🎯 2 ATR / stop 1 ATR"""
    n = len(o); nu = np.full(n, np.nan); nt = np.full(n, np.nan); fz = np.full(n, np.nan); ci = np.full(n, -1, np.int64); vur = np.zeros(n, np.bool_)
    for i in range(n - W - 1):
        e = i + 1; Pe = o[e] * (1 + SLIP)
        if not (Pe > 0) or np.isnan(sig[i]) or np.isnan(atr[i]) or np.isnan(U[i]) or np.isnan(X[i]): continue
        if tip == 0: tp = Pe * (1 + mult * sig[i]); sl = -1.0
        else: tp = Pe + 2 * atr[i]; sl = Pe - atr[i]
        px = np.nan; jj = -1; fee = FP + FP
        for j in range(e, e + W):
            if sl > 0 and l[j] <= sl: px = sl * (1 - SLIP); jj = j; break
            if h[j] >= tp: px = tp; jj = j; vur[i] = True; break
        if jj < 0: jj = e + W - 1; px = c[jj] * (1 - SLIP)
        if np.isnan(U[jj]) or np.isnan(X[jj]): continue
        g = px / Pe; nt[i] = g - 1 - fee; nu[i] = g * U[i] / U[jj] - 1 - fee; fz[i] = nt[i] - (X[jj] / X[i] - 1); ci[i] = jj
    return nu, nt, fz, ci, vur
@njit(cache=True)
def acgozlu(idx, ci):
    sec = np.zeros(len(idx), np.bool_); serbest = -1
    for k in range(len(idx)):
        i = idx[k]
        if i + 1 > serbest and ci[i] >= 0: sec[k] = True; serbest = ci[i]
    return sec

def gosterge(d, N, gunluk):
    c, h, l, o, q = d.c, d.h, d.l, d.o, d.v
    dl = c.diff(); up = dl.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean(); dn = (-dl.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean(); rsi = 100 - 100 / (1 + up / dn)
    macd = ema(c, 12) - ema(c, 26); hist = macd - ema(macd, 9)
    m20, s20 = c.rolling(20).mean(), c.rolling(20).std(); ub, lb = m20 + 2 * s20, m20 - 2 * s20; pb = (c - lb) / (ub - lb); bw = (ub - lb) / m20
    e20, e50, e200 = ema(c, 20), ema(c, 50), ema(c, 200)
    ll14, hh14 = l.rolling(14).min(), h.rolling(14).max(); k = 100 * (c - ll14) / (hh14 - ll14); kk = k.rolling(3).mean(); dd = kk.rolling(3).mean()
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1); atr = tr.ewm(alpha=1 / 14, adjust=False).mean()
    upm, dnm = h.diff(), -l.diff(); pdm = np.where((upm > dnm) & (upm > 0), upm, 0.0); ndm = np.where((dnm > upm) & (dnm > 0), dnm, 0.0)
    pdi = 100 * pd.Series(pdm, index=d.index).ewm(alpha=1 / 14, adjust=False).mean() / atr; ndi = 100 * pd.Series(ndm, index=d.index).ewm(alpha=1 / 14, adjust=False).mean() / atr
    adx = (100 * (pdi - ndi).abs() / (pdi + ndi)).ewm(alpha=1 / 14, adjust=False).mean()
    qn = q.rolling(N).sum(); vz = (qn - qn.rolling(30 * N).mean().shift(N)) / qn.rolling(30 * N).std().shift(N)
    nO, nV, nS, qW = (5, 5, 5, 250) if gunluk else (N, N, N, 30 * N)                           # OBV eğimi · VWAP · sıkışma penceresi · bant genişliği dağılımı
    sgn = np.sign(c.diff()).fillna(0); obv = (sgn * q).cumsum(); obvs = obv - obv.shift(nO)
    vwap = (c * q).rolling(nV).sum() / q.rolling(nV).sum()
    bwq = bw.rolling(qW, min_periods=qW // 2).quantile(0.2); sik = (bw <= bwq).astype(float).rolling(nS).max() > 0
    one = pd.Series(True, index=d.index)
    M = {"M1 MACD hist 0'ı yukarı": cx(hist, 0 * hist), "M2 RSI 30'u yukarı": cx(rsi, 0 * rsi + 30), "M3 RSI 50'yi yukarı": cx(rsi, 0 * rsi + 50),
         "M4 Stoch %K↑%D (<20)": cx(kk, dd) & (kk < 20), "M5 Donchian 20 kırılım": c > h.rolling(20).max().shift(), "M6 Donchian 55 kırılım": c > h.rolling(55).max().shift(),
         "M7 üst Bollinger kırılım": cx(c, ub), "M8 alt Bollinger'den dönüş": cx(c, lb), "M9 EMA20↑EMA50": cx(e20, e50), "M10 VWAP yukarı kesiş": cx(c, vwap)}
    Tr = {"trend yok": one, "T1 >EMA200": c > e200, "T2 EMA20>50>200": (e20 > e50) & (e50 > e200), "T3 ADX>25 +DI>−DI": (adx > 25) & (pdi > ndi)}
    Vt = {"teyit yok": one, "V1 hacim z≥2": vz >= 2, "V2 OBV↑": obvs > 0, "V3 sıkışma sonrası": sik, "V4 >VWAP": c > vwap}
    F = pd.DataFrame(dict(rsi=rsi, hist_s=hist / c, pb=pb, bw=bw, adx=adx, dip=pdi - ndi, kk=kk, vz=vz, ue20=c / e20 - 1, ue50=c / e50 - 1, ue200=c / e200 - 1, atr_s=atr / c))
    return M, Tr, Vt, F, atr

def hazirla(mod):
    A = pd.read_parquet(f"bist_{'gun' if mod == 'gun' else 'saat'}.parquet"); A["t"] = pd.to_datetime(A.t, utc=True)
    if mod == "gun": A["t"] = A.t.dt.tz_convert("Europe/Istanbul").dt.normalize().dt.tz_localize(None)       # günlük: takvim günü
    ser = lambda k: A[A.kod == k].set_index("t").sort_index().pipe(lambda x: x[~x.index.duplicated()])
    U, XU = ser("USDTRY"), ser("XU030")
    if mod == "gun": DON = [("K 2010–18", "2010-01-01", "2019-01-01"), ("C1 2019–22", "2019-01-01", "2023-01-01"), ("C2 2023–26", "2023-01-01", "2027-01-01")]
    else:
        b0 = A[A.grup == "B30"].t.min(); b1 = b0 + pd.Timedelta(days=365)
        DON = [(f"S1 {b0:%m.%Y}–{b1:%m.%Y}", b0, b1), (f"S2 {b1:%m.%Y}–", b1, A.t.max() + pd.Timedelta(days=1))]
    CO = {}; atilan = {}
    for kod, g in A[A.grup.isin(["B30", "DOG"])].groupby("kod"):
        d = ser(kod)[["open", "high", "low", "close", "volume"]].astype(float); d.columns = ["o", "h", "l", "c", "v"]
        d = d[(d.c > 0) & (d.o > 0)]
        if len(d) < (500 if mod == "gun" else 1000): continue
        N = 1 if mod == "gun" else int(pd.Series(d.index.tz_convert("Europe/Istanbul").date).value_counts().median())
        r = d.c.pct_change(); bad = ((r < -0.25) | (r > 0.30)).astype(float); kirli = bad.rolling(61, center=True, min_periods=1).max().fillna(0).values > 0; atilan[kod] = int(bad.sum())
        M, Tr, Vt, F, atr = gosterge(d, N, mod == "gun")
        xc = XU.close.reindex(d.index, method="ffill"); Tr["T4 XU030>EMA200"] = (XU.close > ema(XU.close, 200)).reindex(d.index, method="ffill").fillna(False)
        uu = U.close.reindex(d.index, method="ffill")
        lr = np.log(d.c).diff(); sig = lr.rolling(250, min_periods=125).std() if mod == "gun" else lr.rolling(60 * N, min_periods=30 * N).std()
        if mod == "gun": EXP = [(3, 0.75, 0), (5, 0.75 * 2 ** .5, 0), (10, 1.5, 0), (10, 0, 1)]
        else: EXP = [(4, 1.5, 0), (8, 1.5, 0), (24, 1.5, 0), (24, 0, 1)]
        EX = [cikis(d.o.values, d.h.values, d.l.values, d.c.values, uu.values, xc.values, sig.values, atr.values, W, m, tp) for W, m, tp in EXP]
        grp = A[A.kod == kod].grup.iloc[0]; cell = np.full(len(d), -1, np.int64); ix = d.index
        for p, (_, a, b) in enumerate(DON):
            a, b = pd.Timestamp(a), pd.Timestamp(b)
            if mod != "gun": a, b = a.tz_convert("UTC") if a.tzinfo else a.tz_localize("UTC"), b.tz_convert("UTC") if b.tzinfo else b.tz_localize("UTC")
            cell[(ix >= a) & (ix < b)] = p + (0 if grp == "B30" else len(DON))
        cell[kirli] = -1
        # model özellikleri
        F["sig"] = sig; F["r1"] = lr; ku = [1, 4, 8, 24] if mod != "gun" else [1, 3, 5, 20]
        for k_ in ku: F[f"r{k_}"] = np.log(d.c).diff(k_)
        for j_, k_ in enumerate([3 * N, 5 * N, 20 * N] if mod != "gun" else [60, 120]): F[f"rs_{j_}"] = np.log(d.c).diff(k_)
        xr = np.log(xc); F["x1"] = xr.diff(); F["x5s"] = xr.diff(5 * N); F["gorece5"] = np.log(d.c).diff(5 * N) - xr.diff(5 * N)
        F["u1"] = np.log(uu).diff(N); F["u5"] = np.log(uu).diff(5 * N); F["gun"] = ix.dayofweek
        if mod != "gun": F["saat"] = ix.tz_convert("Europe/Istanbul").hour
        CO[kod] = dict(d=d, M=M, Tr=Tr, Vt=Vt, EX=EX, cell=cell, F=F.replace([np.inf, -np.inf], np.nan), grp=grp)
    return CO, DON, atilan

def hesapla(CO, nmM, nmT, nmV, NC, kaydir=False, rng=None, N_min=30):
    NR = len(nmM) * len(nmT) * len(nmV); S = np.zeros((NR, 4, NC, 3))
    for kod, X in CO.items():
        off = int(rng.integers(N_min, len(X["cell"]) - N_min)) if kaydir else 0
        Mv = {k: np.roll(v.fillna(False).values.astype(bool), off) for k, v in X["M"].items()}
        Tv = {k: v.fillna(False).values.astype(bool) for k, v in X["Tr"].items()}; Vv = {k: v.fillna(False).values.astype(bool) for k, v in X["Vt"].items()}
        r = 0
        for m in nmM:
            for t_ in nmT:
                mt = Mv[m] & Tv[t_]
                for v in nmV:
                    idx = np.where(mt & Vv[v] & (X["cell"] >= 0))[0]
                    if len(idx):
                        for e in range(4):
                            nu, nt, fz, ci, vur = X["EX"][e]; sec = idx[acgozlu(idx, ci)]; sec = sec[~np.isnan(nu[sec])]
                            if len(sec):
                                cl = X["cell"][sec]; nn = nu[sec]
                                S[r, e, :, 0] += np.bincount(cl, minlength=NC); S[r, e, :, 1] += np.bincount(cl, weights=(nn > 0).astype(float), minlength=NC); S[r, e, :, 2] += np.bincount(cl, weights=nn, minlength=NC)
                    r += 1
    return S
def karar(S, nsec):
    n, w, s = S[..., 0], S[..., 1], S[..., 2]
    with np.errstate(invalid="ignore", divide="ignore"): isa, net = w / n, s / n
    sec = (isa[:, :, 0] >= 0.65) & (net[:, :, 0] >= 0.003) & (n[:, :, 0] >= nsec)
    aday = sec & np.all((isa[:, :, 1:] >= 0.70) & (net[:, :, 1:] >= 0.003) & (n[:, :, 1:] >= 30), axis=2)
    umut = sec & np.all((isa[:, :, 1:] >= 0.65) & (net[:, :, 1:] >= 0.0015) & (n[:, :, 1:] >= 30), axis=2)
    return n, isa, net, sec, aday, umut

def calis(mod):
    CO, DON, atilan = hazirla(mod); X0 = next(iter(CO.values()))
    nmM, nmT, nmV = list(X0["M"]), list(X0["Tr"]), list(X0["Vt"]); KUR = [(m, t_, v) for m in nmM for t_ in nmT for v in nmV]
    ND = len(DON); CELLAD = [f"B30 {a.split()[0]}" for a, _, _ in DON] + [f"doğr. {a.split()[0]}" for a, _, _ in DON]
    # sıralama: hücre 0 = B30 × seçim dönemi; testler = geri kalan (saatlikte 3, günlükte 5)
    perm = list(range(2 * ND)); NC = 2 * ND
    EXAD = ["🎯0,75σ·3g", "🎯0,75σ√2·5g", "🎯0,75σ√4·10g", "🎯2ATR/stop1ATR·10g"] if mod == "gun" else ["🎯0,75σ√4·4m", "🎯0,75σ√4·8m", "🎯0,75σ√4·24m", "🎯2ATR/stop1ATR·24m"]
    nsec = 100 if mod == "gun" else 50
    baslik = "GÜNLÜK (2010 →)" if mod == "gun" else "SAATLİK (son ≈ 2 yıl)"
    yaz(f"\n# {'📅' if mod == 'gun' else '⏱️'} {baslik}")
    yaz(f"_{len(CO)} hisse (BIST 30: {sum(x['grp'] == 'B30' for x in CO.values())} · doğrulama: {sum(x['grp'] == 'DOG' for x in CO.values())}) · dönemler: " + " · ".join(f"{a}" for a, _, _ in DON) + f" · bölünme/hata şüphesi atılan nokta: {sum(atilan.values())} ({', '.join(f'{k} {v}' for k, v in atilan.items() if v)})_")
    yaz("_hücre: işlem · isabet (dolar net > 0) · işlem başı dolar net %_\n")
    # ---- A taban
    yaz("## A — Taban: her mumda koşulsuz AL")
    yaz("| çıkış | " + " | ".join(CELLAD) + " |"); yaz("|---|" + "---|" * NC)
    for e in range(4):
        hc = []
        for k in range(NC):
            nu_, nt_, fz_, vr_ = [], [], [], []
            for X in CO.values():
                nu, nt, fz, ci, vur = X["EX"][e]; m = (X["cell"] == k) & ~np.isnan(nu); nu_.append(nu[m]); nt_.append(nt[m]); fz_.append(fz[m]); vr_.append(vur[m])
            a = np.concatenate(nu_); b = np.concatenate(nt_); f = np.concatenate(fz_); v = np.concatenate(vr_)
            hc.append(f"{len(a)} · %{100 * (a > 0).mean():.0f} · {100 * a.mean():+.2f} (TL {100 * b.mean():+.2f} · endekse göre {100 * f.mean():+.2f} · 🎯 %{100 * v.mean():.0f})" if len(a) else "—")
        yaz(f"| {EXAD[e]} | " + " | ".join(hc) + " |")
    # ---- B kurallar
    S = hesapla(CO, nmM, nmT, nmV, NC); n, isa, net, sec, aday, umut = karar(S, nsec)
    yaz(f"\n## B — Teknik kombinasyonlar ({len(KUR)} × 4 çıkış = {4 * len(KUR)} kural)")
    yaz(f"**Seçim ({CELLAD[0]}: isabet ≥ %65, dolar net ≥ +%0,30, ≥ {nsec} işlem): {int(sec.sum())} kural · umut verici (tüm testler ≥ %65 ve ≥ +%0,15): {int(umut.sum())} · SİNYAL ADAYI (tüm testler ≥ %70 ve ≥ +%0,30, ≥ 30): {int(aday.sum())}**\n")
    def satir(r, e): return " | ".join(f"{int(n[r, e, k])} · %{100 * isa[r, e, k]:.0f} · {100 * net[r, e, k]:+.2f}" if n[r, e, k] else "0" for k in range(NC))
    if sec.any():
        yaz("| kural | çıkış | " + " | ".join(CELLAD) + " | |"); yaz("|---|---|" + "---|" * NC + "---|")
        for r, e in sorted(zip(*np.where(sec)), key=lambda x: -np.nanmin(np.where(n[x[0], x[1], 1:] > 0, isa[x[0], x[1], 1:], 0)))[:40]:
            m, t_, v = KUR[r]; yaz(f"| {m} · {t_} · {v} | {EXAD[e]} | {satir(r, e)} | {'🎯 ADAY' if aday[r, e] else ('✅ umut' if umut[r, e] else '')} |")
        if sec.sum() > 40: yaz(f"_(+{int(sec.sum()) - 40} seçilen kural daha; en zayıf test hücresine göre ilk 40)_")
    ok = n[:, :, 0] >= nsec
    for bas, sk in (("en yüksek isabetli", np.where(ok, isa[:, :, 0], -1)), ("en kârlı", np.where(ok, net[:, :, 0], -9))):
        yaz(f"\n**Bilgi — {CELLAD[0]}'de {bas} 10 kural (≥ {nsec} işlem)**"); top = np.dstack(np.unravel_index(np.argsort(-sk.ravel())[:10], sk.shape))[0]
        yaz("| kural | çıkış | " + " | ".join(CELLAD) + " |"); yaz("|---|---|" + "---|" * NC)
        for r, e in top: m, t_, v = KUR[r]; yaz(f"| {m} · {t_} · {v} | {EXAD[e]} | {satir(r, e)} |")
    rng = np.random.default_rng(1101); PL = []
    for k in range(10):
        _, _, _, s2, a2, u2 = karar(hesapla(CO, nmM, nmT, nmV, NC, True, rng, 30 * (1 if mod == "gun" else 9)), nsec); PL.append((int(s2.sum()), int(u2.sum()), int(a2.sum())))
        print(f"plasebo {mod} {k}: {PL[-1]} · {time.time() - T0:.0f} sn", flush=True)
    yaz(f"\n**Plasebo (tetikler hisse içinde rastgele kaydırılmış ×10):** seçilen ort. {np.mean([p[0] for p in PL]):.1f} (en çok {max(p[0] for p in PL)}) · umut verici ort. {np.mean([p[1] for p in PL]):.1f} (en çok {max(p[1] for p in PL)}) · aday ort. {np.mean([p[2] for p in PL]):.1f} (en çok {max(p[2] for p in PL)})")
    # ---- C model
    eh = 1 if mod == "gun" else 2                                                                # hedef: G2 / E3
    rows = []
    for kod, X in CO.items():
        nu, nt, fz, ci, vur = X["EX"][eh]; F = X["F"].copy(); F["y"] = vur; F["nu"] = nu; F["cell"] = X["cell"]; F["kod"] = kod; F["i"] = np.arange(len(F)); rows.append(F[(F.cell >= 0) & F.nu.notna()])
    Z = pd.concat(rows); cols = [c for c in Z.columns if c not in ("y", "nu", "cell", "kod", "i")]
    tr = Z[Z.cell == 0]; dus = [c for c in cols if tr[c].nunique() < 2]; cols = [c for c in cols if c not in dus]; print("modelden düşen sütun:", dus); mdl = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=31, min_samples_leaf=200, random_state=0).fit(tr[cols], tr.y)
    Z["p"] = mdl.predict_proba(Z[cols])[:, 1]; thr = np.quantile(Z.loc[Z.cell == 0, "p"], 0.90)
    hc = []; okm = []
    for k in range(NC):
        nn = []
        for kod, g in Z[(Z.cell == k) & (Z.p >= thr)].groupby("kod"):
            idx = g.i.values; ci = CO[kod]["EX"][eh][3]; s_ = idx[acgozlu(idx, ci)]; nn.append(CO[kod]["EX"][eh][0][s_])
        a = np.concatenate(nn) if nn else np.array([]); hc.append(f"{len(a)} · %{100 * (a > 0).mean():.0f} · {100 * a.mean():+.2f}" if len(a) else "0")
        okm.append((len(a) >= (nsec if k == 0 else 30)) and ((a > 0).mean() >= (0.65 if k == 0 else 0.70)) and (a.mean() >= 0.003) if len(a) else False)
    yaz(f"\n## C — Model (fiyat/hacim/endeks/dolar özellikleri · HistGradientBoosting · hedef {EXAD[eh]} 🎯 · eşik = eğitimde en üst %10, p ≥ {thr:.2f})")
    yaz("| | " + " | ".join(CELLAD) + " | karar |"); yaz("|---|" + "---|" * NC + "---|")
    yaz(f"| model sinyalleri | " + " | ".join(hc) + f" | {'🎯 ADAY' if all(okm) else 'geçmedi'} |")
    yaz(f"_{CELLAD[0]} eğitim hücresidir (örneklem içi); karar test hücrelerine göre._")
    return dict(sec=int(sec.sum()), umut=int(umut.sum()), aday=int(aday.sum()), model=all(okm), PL=PL)

yaz("# 🇹🇷 BIST fizibilite — PROTOKOL_bist.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · net = dolar bazında, komisyon+BSMV %0,05/taraf, kayma %0,05 · yalnız AL_")
SON = {m: calis(m) for m in (sys.argv[1:] or ["saat", "gun"])}
yaz("\n# Özet"); [yaz(f"- **{'saatlik' if m == 'saat' else 'günlük'}:** seçilen {r['sec']} · umut verici {r['umut']} · sinyal adayı {r['aday']} · model {'ADAY' if r['model'] else 'geçmedi'} · plasebo umut/aday en çok {max(p[1] for p in r['PL'])}/{max(p[2] for p in r['PL'])}") for m, r in SON.items()]
yaz(f"\n_süre {time.time() - T0:.0f} sn_"); open("bist_sonuc.md" if len(SON) > 1 else f"bist_sonuc_{list(SON)[0]}.md", "w").write("\n".join(out) + "\n")
