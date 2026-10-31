# teknik3.py — PROTOKOL_teknik3.md: klasik teknik gösterge kombinasyonları (250 × 4 çıkış) + mevcut sinyallere filtre → teknik3_sonuc.md
import glob, hashlib, time, numpy as np, pandas as pd
from numba import njit
T0 = time.time(); out = []
def yaz(s=""): out.append(s); print(s, flush=True)
A = pd.concat([pd.read_parquet(f) for f in sorted(glob.glob("teknik3_mum_*.parquet"))], ignore_index=True); A["coin"] = A.coin.astype(str)
DON = [("K 2022–23", "2022-01-01", "2024-01-01"), ("C1 2024", "2024-01-01", "2025-01-01"), ("C2 2025–26", "2025-01-01", "2026-10-28")]
DB = [pd.Timestamp(a, tz="UTC").value // 10**9 for _, a, _ in DON] + [pd.Timestamp(DON[-1][2], tz="UTC").value // 10**9]
yari = lambda s: int(hashlib.md5(s.encode()).hexdigest(), 16) % 2                                   # 0 = keşif, 1 = doğrulama
FP, FL, SLIP, FON8 = 0.0005, 0.0002, 0.001, 0.0001
def ema(x, n): return x.ewm(span=n, adjust=False).mean()
def gosterge(d):
    c, h, l, o, q = d.c, d.h, d.l, d.o, d.qv
    dl = c.diff(); up = dl.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean(); dn = (-dl.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean(); rsi = 100 - 100 / (1 + up / dn)
    macd = ema(c, 12) - ema(c, 26); hist = macd - ema(macd, 9)
    m20, s20 = c.rolling(20).mean(), c.rolling(20).std(); ub, lb = m20 + 2 * s20, m20 - 2 * s20; pb = (c - lb) / (ub - lb); bw = (ub - lb) / m20
    e20, e50, e200 = ema(c, 20), ema(c, 50), ema(c, 200)
    ll14, hh14 = l.rolling(14).min(), h.rolling(14).max(); k = 100 * (c - ll14) / (hh14 - ll14); kk = k.rolling(3).mean(); dd = kk.rolling(3).mean()
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1); atr = tr.ewm(alpha=1 / 14, adjust=False).mean()
    upm, dnm = h.diff(), -l.diff(); pdm = np.where((upm > dnm) & (upm > 0), upm, 0.0); ndm = np.where((dnm > upm) & (dnm > 0), dnm, 0.0)
    pdi = 100 * pd.Series(pdm, index=d.index).ewm(alpha=1 / 14, adjust=False).mean() / atr; ndi = 100 * pd.Series(ndm, index=d.index).ewm(alpha=1 / 14, adjust=False).mean() / atr
    adx = (100 * (pdi - ndi).abs() / (pdi + ndi)).ewm(alpha=1 / 14, adjust=False).mean()
    vz = (q.rolling(24).sum() - q.rolling(24).sum().rolling(720).mean().shift(24)) / q.rolling(24).sum().rolling(720).std().shift(24)
    sgn = np.sign(c.diff()).fillna(0); obv = (sgn * q).cumsum(); obv24 = obv - obv.shift(24)
    vwap = (c * q).rolling(24).sum() / q.rolling(24).sum()
    bwq = bw.rolling(720, min_periods=360).quantile(0.2); sik = (bw <= bwq).astype(float).rolling(24).max() > 0
    cx = lambda a, b: (a > b) & (a.shift() <= b.shift())
    M = {"M1 MACD hist 0'ı yukarı": cx(hist, 0 * hist), "M2 RSI 30'u yukarı": cx(rsi, pd.Series(30.0, index=d.index)), "M3 RSI 50'yi yukarı": cx(rsi, pd.Series(50.0, index=d.index)),
         "M4 Stoch %K↑%D (<20)": cx(kk, dd) & (kk < 20), "M5 Donchian 20 kırılım": c > h.rolling(20).max().shift(), "M6 Donchian 55 kırılım": c > h.rolling(55).max().shift(),
         "M7 üst Bollinger kırılım": cx(c, ub), "M8 alt Bollinger'den dönüş": cx(c, lb), "M9 EMA20↑EMA50": cx(e20, e50), "M10 VWAP24 yukarı kesiş": cx(c, vwap)}
    Tr = {"trend yok": pd.Series(True, index=d.index), "T1 >EMA200": c > e200, "T2 EMA20>50>200": (e20 > e50) & (e50 > e200), "T3 ADX>25 +DI>−DI": (adx > 25) & (pdi > ndi)}
    Vt = {"teyit yok": pd.Series(True, index=d.index), "V1 hacim z≥2": vz >= 2, "V2 OBV 24s↑": obv24 > 0, "V3 sıkışma sonrası": sik, "V4 >VWAP24": c > vwap}
    st = dict(rsi=rsi, hist=hist, pb=pb, adx=adx, pdi=pdi, ndi=ndi, kk=kk, vz=vz, e200=e200, atr=atr, c=c)
    return M, Tr, Vt, st
@njit(cache=True)
def cikis(o, h, l, c, sig, atr, tip):
    """her saat i için: i+1 açılışında giriş → (net, ham, çıkış indeksi). tip 0/1/2: 🎯 0,75σ√4 en fazla 4/8/24 s · 3: 🎯 2 ATR / stop 1 ATR, 24 s"""
    n = len(o); net = np.full(n, np.nan); ham = np.full(n, np.nan); ci = np.full(n, -1, np.int64)
    W = 4 if tip == 0 else (8 if tip == 1 else 24)
    for i in range(n - W - 1):
        e = i + 1; Pe = o[e] * (1 + SLIP)
        if not (Pe > 0) or np.isnan(sig[i]) or np.isnan(atr[i]): continue
        if tip < 3: tp = Pe * (1 + 0.75 * sig[i] * 2.0); sl = -1.0
        else: tp = Pe + 2 * atr[i]; sl = Pe - atr[i]
        done = False
        for j in range(e, e + W):
            if sl > 0 and l[j] <= sl: net[i] = sl / Pe - 1 - FP - FP; ham[i] = sl / o[e] - 1; ci[i] = j; done = True; break
            if h[j] >= tp: net[i] = tp / Pe - 1 - FP - FL; ham[i] = tp / o[e] - 1; ci[i] = j; done = True; break
        if not done: j = e + W - 1; net[i] = c[j] / Pe - 1 - FP - FP; ham[i] = c[j] / o[e] - 1; ci[i] = j
        net[i] -= FON8 * (ci[i] - e + 1) / 8.0
    return net, ham, ci
@njit(cache=True)
def acgozlu(idx, ci):
    sec = np.zeros(len(idx), np.bool_); serbest = -1
    for k in range(len(idx)):
        i = idx[k]
        if i + 1 > serbest and ci[i] >= 0: sec[k] = True; serbest = ci[i]
    return sec
COINS = sorted(A.coin.unique()); BTC = A[A.coin == "BTC"].set_index("t").c.sort_index(); BTCtr = BTC > ema(BTC, 200)
ST = None; ADLAR = None; EV = {}; CO = {}
for nm in COINS:
    d = A[A.coin == nm].set_index("t").sort_index().astype({"o": float, "h": float, "l": float, "c": float, "qv": float}); d = d[~d.index.duplicated()]
    if len(d) < 2000: continue
    M, Tr, Vt, st = gosterge(d); Tr["T4 BTC>EMA200"] = BTCtr.reindex(d.index).fillna(False)
    sig = np.log(d.c).diff().rolling(720, min_periods=480).std().values
    o_, h_, l_, c_, atr = d.o.values, d.h.values, d.l.values, d.c.values, st["atr"].values
    EX = [cikis(o_, h_, l_, c_, sig, atr, k) for k in range(4)]
    ts = d.index.as_unit("s").asi8
    cell = np.full(len(d), -1, np.int64)
    for p in range(3): cell[(ts >= DB[p]) & (ts < DB[p + 1])] = p
    cell = np.where(cell >= 0, cell + 3 * yari(nm), -1)                                          # 0–2 keşif K/C1/C2 · 3–5 doğrulama K/C1/C2
    CO[nm] = dict(d=d, st=st, M=M, Tr=Tr, Vt=Vt, EX=EX, cell=cell)
nmM, nmT, nmV = list(M), list(Tr), list(Vt)
print(f"[{time.time() - T0:.0f} sn] coin hazır: {len(CO)}", flush=True)
NR = len(nmM) * len(nmT) * len(nmV)
def hesapla(kaydir=None, rng=None):
    S = np.zeros((NR, 4, 6, 3))                                                                  # işlem · kazanan · net toplamı
    for nm, X in CO.items():
        off = int(rng.integers(720, len(X["cell"]) - 720)) if kaydir else 0
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
                            net, ham, ci = X["EX"][e]; sec = idx[acgozlu(idx, ci)]; sec = sec[~np.isnan(net[sec])]
                            if len(sec):
                                cl = X["cell"][sec]; nn = net[sec]
                                S[r, e, :, 0] += np.bincount(cl, minlength=6); S[r, e, :, 1] += np.bincount(cl, weights=(nn > 0).astype(float), minlength=6); S[r, e, :, 2] += np.bincount(cl, weights=nn, minlength=6)
                    r += 1
    return S
S = hesapla(); print(f"[{time.time() - T0:.0f} sn] kurallar hesaplandı", flush=True)
EXAD = ["🎯0,75σ·4s", "🎯0,75σ·8s", "🎯0,75σ·24s", "🎯2ATR/stop1ATR·24s"]; CELL = ["keşif K", "keşif C1", "keşif C2", "doğr. K", "doğr. C1", "doğr. C2"]
KUR = [(m, t_, v) for m in nmM for t_ in nmT for v in nmV]
def karar(S):
    n, w, s = S[..., 0], S[..., 1], S[..., 2]
    with np.errstate(invalid="ignore", divide="ignore"): isa, net = w / n, s / n
    sec = (isa[:, :, 0] >= 0.65) & (net[:, :, 0] >= 0.003) & (n[:, :, 0] >= 100)
    aday = sec & np.all((isa >= 0.70) & (net >= 0.003) & (n >= 30), axis=2)
    umut = sec & np.all((isa >= 0.65) & (net >= 0.0015) & (n >= 30), axis=2)
    return n, isa, net, sec, aday, umut
n, isa, net, sec, aday, umut = karar(S)
yaz("# 📐 Klasik teknik gösterge kombinasyonları — PROTOKOL_teknik3.md")
yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {len(CO)} coin (keşif {sum(yari(c) == 0 for c in CO)} · doğrulama {sum(yari(c) == 1 for c in CO)}) · {NR} kombinasyon × 4 çıkış = {NR * 4} kural · hücre: işlem · isabet · işlem başı net %_\n")
yaz(f"**Seçim (keşif × K: isabet ≥ %65, net ≥ +%0,30, ≥ 100 işlem): {int(sec.sum())} kural · umut verici (6 hücre ≥ %65 ve ≥ +%0,15): {int(umut.sum())} · SİNYAL ADAYI (6 hücre ≥ %70 ve ≥ +%0,30): {int(aday.sum())}**\n")
def satir(r, e): return " | ".join(f"{int(n[r, e, k])} · %{100 * isa[r, e, k]:.0f} · {100 * net[r, e, k]:+.2f}" if n[r, e, k] else "0" for k in range(6))
yaz("| kural | çıkış | " + " | ".join(CELL) + " | |"); yaz("|---|---|" + "---|" * 6 + "---|")
for r, e in sorted(zip(*np.where(sec)), key=lambda x: -np.nanmin(isa[x[0], x[1], :])):
    m, t_, v = KUR[r]; yaz(f"| {m} · {t_} · {v} | {EXAD[e]} | {satir(r, e)} | {'🎯' if aday[r, e] else ('✅' if umut[r, e] else '')} |")
yaz("\n## Bilgi — keşif × K'de en yüksek isabetli 15 kural (seçim şartından bağımsız, ≥ 100 işlem)")
ok = n[:, :, 0] >= 100; sk = np.where(ok, isa[:, :, 0], -1); top = np.dstack(np.unravel_index(np.argsort(-sk.ravel())[:15], sk.shape))[0]
yaz("| kural | çıkış | " + " | ".join(CELL) + " |"); yaz("|---|---|" + "---|" * 6)
for r, e in top: m, t_, v = KUR[r]; yaz(f"| {m} · {t_} · {v} | {EXAD[e]} | {satir(r, e)} |")
yaz("\n## Bilgi — keşif × K'de en kârlı 15 kural (≥ 100 işlem)")
sk = np.where(ok, net[:, :, 0], -9); top = np.dstack(np.unravel_index(np.argsort(-sk.ravel())[:15], sk.shape))[0]
yaz("| kural | çıkış | " + " | ".join(CELL) + " |"); yaz("|---|---|" + "---|" * 6)
for r, e in top: m, t_, v = KUR[r]; yaz(f"| {m} · {t_} · {v} | {EXAD[e]} | {satir(r, e)} |")
rng = np.random.default_rng(31); PL = []
for k in range(10):
    _, _, _, s2, a2, u2 = karar(hesapla(True, rng)); PL.append((int(s2.sum()), int(u2.sum()), int(a2.sum()))); print(f"plasebo {k}: {PL[-1]} · {time.time() - T0:.0f} sn", flush=True)
yaz(f"\n**Plasebo (tetik saatleri coin içinde rastgele kaydırılmış ×10):** seçilen ort. {np.mean([p[0] for p in PL]):.1f} · umut verici ort. {np.mean([p[1] for p in PL]):.1f} (en çok {max(p[1] for p in PL)}) · sinyal adayı ort. {np.mean([p[2] for p in PL]):.1f} (en çok {max(p[2] for p in PL)})")
# ======================= B: mevcut sinyallere filtre =======================
yaz("\n## B — Göstergeler mevcut sinyallere filtre olarak (sinyal saatinden önceki kapanmış mum)")
K_ = ["t", "nm", "sinif", "H"]
v_ = pd.read_csv("veri_seti.csv.gz", usecols=K_).drop_duplicates(K_); k_ = pd.read_csv("karal2_veri.csv.gz", usecols=K_ + ["D_T0"]).drop_duplicates(K_)
Xs = v_.merge(k_, on=K_); Xs["t"] = pd.to_datetime(Xs.t, utc=True); Xs["ok"] = Xs.D_T0 > 0
DB2 = [("A 2022-06→2024", "2022-06-01", "2025-01-01"), ("B 2025", "2025-01-01", "2026-01-01"), ("C 2026", "2026-01-01", "2027-01-01")]
Xs["don"] = None
for ad, a, b in DB2: Xs.loc[(Xs.t >= pd.Timestamp(a, tz="UTC")) & (Xs.t < pd.Timestamp(b, tz="UTC")), "don"] = ad
Xs = Xs[Xs.don.notna()].reset_index(drop=True)
DUR = {}
for nm, g in Xs.groupby("nm"):
    if nm not in CO: continue
    X = CO[nm]; st = X["st"]; ti = g.t - pd.Timedelta(hours=1)
    vals = {"rsi": st["rsi"], "hist": st["hist"], "pb": st["pb"], "adx": st["adx"], "pdi": st["pdi"], "ndi": st["ndi"], "kk": st["kk"]}
    for k, s in vals.items(): DUR.setdefault(k, {}).update(dict(zip(g.index, s.reindex(ti).values)))
    for k, s in list(X["Tr"].items()) + list(X["Vt"].items()): DUR.setdefault(k, {}).update(dict(zip(g.index, s.reindex(ti).fillna(False).astype(bool).values)))
for k, dct in DUR.items(): Xs[k] = pd.Series(dct)
FK = {"T1 fiyat > EMA200": Xs["T1 >EMA200"] == True, "T2 EMA20>50>200": Xs["T2 EMA20>50>200"] == True, "T3 ADX>25 ve +DI>−DI": Xs["T3 ADX>25 +DI>−DI"] == True,
      "T4 BTC > EMA200": Xs["T4 BTC>EMA200"] == True, "V1 hacim z ≥ 2": Xs["V1 hacim z≥2"] == True, "V2 OBV 24 s ↑": Xs["V2 OBV 24s↑"] == True, "V3 sıkışma sonrası": Xs["V3 sıkışma sonrası"] == True,
      "V4 > VWAP24": Xs["V4 >VWAP24"] == True, "RSI < 30": Xs.rsi < 30, "RSI 30–50": (Xs.rsi >= 30) & (Xs.rsi < 50), "RSI 50–70": (Xs.rsi >= 50) & (Xs.rsi < 70), "RSI ≥ 70": Xs.rsi >= 70,
      "MACD hist > 0": Xs.hist > 0, "MACD hist < 0": Xs.hist < 0, "%B > 1 (üst bandın üstü)": Xs.pb > 1, "%B < 0 (alt bandın altı)": Xs.pb < 0, "ADX > 25": Xs.adx > 25, "ADX < 20 (trendsiz)": Xs.adx < 20,
      "Stoch %K < 20": Xs.kk < 20, "Stoch %K > 80": Xs.kk > 80}
def hs(x): return f"{len(x)} · %{100 * x.ok.mean():.0f} · {100 * x.D_T0.mean():+.2f}" if len(x) else "—"
GEC = []
for sad, sp in (("tüm sinyaller", None), ("✅ ana", "✅")):
    Y = Xs if sp is None else Xs[Xs.sinif.str.startswith(sp)]
    yaz(f"\n**{sad}** — taban: " + " · ".join(f"{a} {hs(Y[Y.don == a])}" for a, _, _ in DB2)); yaz("| koşul | " + " | ".join(a for a, _, _ in DB2) + " | geçti |"); yaz("|---|---|---|---|---|")
    for ad, m in FK.items():
        m = m.reindex(Y.index).fillna(False).astype(bool); ok_ = True; hc = []
        for a, _, _ in DB2:
            y = Y[Y.don == a]; mm = m[Y.don == a]; u, z = y[mm], y[~mm]
            if not len(u) or not len(z): hc.append("—"); ok_ = False; continue
            di, dn = 100 * (u.ok.mean() - z.ok.mean()), 100 * (u.D_T0.mean() - z.D_T0.mean()); hc.append(f"{hs(u)} ({di:+.0f} / {dn:+.2f})")
            if not (di >= 5 and dn >= 0.10 and len(u) >= 0.2 * len(y)): ok_ = False
        yaz(f"| {ad} | " + " | ".join(hc) + f" | {'✅' if ok_ else ''} |"); GEC += [f"{sad}: {ad}"] if ok_ else []
yaz(f"\n**B sonucu: geçen filtre {len(GEC)}**" + (": " + "; ".join(GEC) if GEC else ""))
yaz(f"\n_süre {time.time() - T0:.0f} sn_"); open("teknik3_sonuc.md", "w").write("\n".join(out) + "\n")
