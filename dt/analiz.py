# dt/analiz.py — BAĞIMSIZ DENETİM: geçmiş veride sinyal sınıflarını CANLI KODUN KURALLARIYLA yeniden kurar ve ölçer (yalnız ölçüm).
# Girdi: model çıktıları (yürüyen test dışa aktarımları: art1 / ga / art2 / art4) + KENDİ indirdiğim Binance 1s fiyat ve Coinbase primi (dveri*).
# Kurallar main dalındaki tahmin_coin.py / tahmin24.py / prim_canli.py / gonder.py / ortak.py'den okunup burada SIFIRDAN yazıldı.
import os, sys, glob, gzip, pickle, time, json, numpy as np, pandas as pd, requests
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "canli")                                                  # yalnız model dosyalarını açmak için (pickle sınıfları)
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
g = lambda p: sorted(glob.glob(p, recursive=True))
P1, P2, P3 = pd.Timestamp("2022-06-01", tz="UTC"), pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")
DON = [("2022-06→2023", P1, P2), ("2024–25", P2, P3), ("2026", P3, pd.Timestamp("2030-01-01", tz="UTC"))]
KOM = [0.04, 0.10, 0.20]                                                     # gidiş-dönüş maliyet %: testteki · vadeli taker çıkış · spot standart (%0,1 × 2)
# ---------------- 0) veri ----------------
V = {}
for f in g("dveri/**/veri_*.pkl"): V.update(pickle.load(open(f, "rb")))
def full_idx(df):
    ix = pd.date_range(df.index[0], df.index[-1], freq="1h", tz="UTC"); return df.reindex(ix)
BN, Z = {}, {}
for sym, d in V.items():
    if d["bn"] is None or len(d["bn"]) < 3000: continue
    BN[sym] = full_idx(d["bn"])
    cb = d["cb"]
    if cb is not None and len(cb) > 200:
        p = np.log(cb / d["bn"].c.reindex(cb.index)).dropna()
        z = (p - p.rolling(720, min_periods=168).mean()) / (p.rolling(720, min_periods=168).std() + 1e-12)
        Z[sym] = z.reindex(BN[sym].index).ffill(limit=2)                     # canlı: son prim satırı ≤ 3 saat eskiyse kullanılır
yaz(f"# Bağımsız denetim — geçmiş test ({pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M})")
yaz(f"_Kendi verim: {len(BN)} coin Binance 1s · {len(Z)} coin Coinbase primi_")
# ---------------- 1) model çıktıları ----------------
EXC = {os.path.basename(p)[5:-4]: pd.read_pickle(p) for p in g("art1/**/disa_*USDT.pkl")}
EXW = {os.path.basename(p)[5:-4]: pd.read_pickle(p) for p in g("ga/**/disa_*USDT.pkl")}
E24M = {os.path.basename(p)[7:-4]: pd.read_pickle(p) for p in g("art2/**/disa24_*USDT.pkl")}
E24W = {os.path.basename(p)[7:-4]: pd.read_pickle(p) for p in g("ga/**/disa24_*USDT.pkl")}
SFB = pd.read_pickle(g("art4/**/sf_BTCUSDT.pkl")[0]).astype("float64")
GEN = [l.strip() for l in open("dt/genis.txt") if l.strip()]; GEN24 = [l.strip() for l in open("dt/genis24.txt") if l.strip()]
MAIN = open("canli/durum/coin_listesi.txt").read().split()
MAIN24 = [os.path.basename(p)[8:-7] for p in g("canli/durum/model24_*.pkl.gz")]
JO = pd.read_csv("canli/durum/ortak_acik.csv").groupby("sym").sinyal.apply(set).to_dict()
TK = pd.read_csv("canli/durum/tek_acik.csv").groupby("sym").sinyal.apply(set).to_dict()
PA = pd.read_csv("canli/durum/prim_acik.csv")
SIG = {}
for s in MAIN:
    with gzip.open(f"canli/durum/model_{s}.pkl.gz", "rb") as fh: M = pickle.load(fh)
    SIG[s] = {k: (bool(v["on"]), int(v["H"])) for k, v in M["SIG"].items()}
yaz(f"_Model çıktıları: ana coin {len(EXC)} · geniş {len(EXW)} · 24 s ana {len(E24M)} · 24 s geniş {len(E24W)} · canlı geniş liste {len(GEN)} · ana {len(MAIN)} · 24 s ana {len(MAIN24)}_\n")
def bflag(x): return x.astype(object).fillna(False).astype(bool)
# ---------------- 2) hizalama / geleceğe bakma denetimleri ----------------
yaz("## A) Hizalama ve geleceğe bakma denetimleri")
def lagcheck(name, a, b):
    """a, b: aynı anlamda iki seri; gecikme -1/0/+1 saatte eşleşme."""
    out = []
    for lag in (-1, 0, 1):
        x = pd.concat([a, b.shift(lag)], axis=1).dropna()
        out.append(f"gecikme {lag:+d}: n={len(x)} ort.|fark|={np.abs(x.iloc[:, 0] - x.iloc[:, 1]).mean():.4g} kor={x.corr().iloc[0, 1]:.4f}" if len(x) > 10 else f"gecikme {lag:+d}: veri yok")
    yaz(f"- {name}: " + " · ".join(out))
for s in ("ETHUSDT", "DOGEUSDT"):
    if s in E24M and s in BN:
        e = E24M[s]; lagcheck(f"{s} dışa aktarım 'close' ↔ benim Binance kapanışım (log getiri)", np.log(e.close.astype(float)).diff(), np.log(BN[s].c).diff())
for s in ("ETHUSDT", "AAVEUSDT"):
    ex = EXC.get(s, EXW.get(s))
    if ex is not None and s in BN:
        mine = np.log(BN[s].c.shift(-4) / BN[s].c); lagcheck(f"{s} dışa aktarım y4 ↔ benim log(c[t+4]/c[t])", ex.y4.astype(float), mine)
try:
    RAWP = pd.read_pickle(g("art3/**/prim_veri.pkl")[0])
    for nm in ("BTC", "ETH", "FIL", "NEAR"):
        if nm in RAWP and nm + "USDT" in Z:
            zz = RAWP[nm].z.astype(float); zz.index = pd.DatetimeIndex(zz.index).tz_convert("UTC"); lagcheck(f"{nm} önceki araştırmanın prim z'si ↔ benim prim z'm", zz, Z[nm + "USDT"])
except Exception as e: yaz(f"- prim karşılaştırması yapılamadı: {e}")
def cz(x): return (x - x.rolling(720, min_periods=168).mean().shift(1)) / (x.rolling(720, min_periods=168).std().shift(1) + 1e-9)
def sframe(PG, PL):
    lg = lambda p: np.log(p / (1 - p)); S = (cz(lg(PG)) + cz(lg(PL))) / 2; C = S.abs()
    return pd.DataFrame({"S": S, "C": C, "T10": C.rolling(720, min_periods=168).quantile(0.90).shift(1)})
try:
    with gzip.open("canli/durum/model.pkl.gz", "rb") as fh: MB = pickle.load(fh)
    sf = sframe(MB["R"][4]["PG"], MB["R"][4]["PL"]); u4l = ((sf.S > 0) & (sf.C >= sf.T10))[sf.T10.notna()]
    u4e = bflag(EXC["BTCUSDT"].u4).reindex(u4l.index)
    ok = u4e.notna(); a, b = u4l[ok].astype(bool), u4e[ok].astype(bool)
    yaz(f"- BTC 4s Çok güçlü ↑: CANLI BTC modeli (model.pkl.gz, {u4l.index[0]:%d.%m}–{u4l.index[-1]:%d.%m}) ↔ araştırmanın kullandığı dışa aktarım: {len(a)} saat, uyum %{100*(a == b).mean():.1f}, canlı {int(a.sum())} saat ↑ · dışa aktarım {int(b.sum())} saat ↑ · ikisi birden {int((a & b).sum())}")
except Exception as e: yaz(f"- BTC model karşılaştırması yapılamadı: {type(e).__name__} {e}")
yaz("")
# ---------------- 3) olaylar (canlı kurallar) ----------------
def rz_ser(c):
    lr = np.log(c).diff(); return (np.log(c) - np.log(c.shift(24))) / (lr.rolling(720, min_periods=168).std() * np.sqrt(24))
RZ = {s: rz_ser(BN[s].c) for s in BN}
def zat(sym, t):
    z = Z.get(sym);
    if z is None: return np.nan
    v = z.get(t, np.nan); return float(v) if v is not None else np.nan
B = EXC["BTCUSDT"]; B_u4 = bflag(B.u4); B_acls = bflag(B.acls); B_q = (~B_u4) & (~B_acls)
ZB = Z.get("BTCUSDT")
EV = []                                                                      # (sınıf, tür, sym, t, H, k)
def add(sinif, tur, sym, t, H):
    k = {"ana": 0.75, "yedek": 0.50, "panelden": 0.45, "panel": 0.75}[sinif]; EV.append((sinif, tur, sym, t, H, k))
ORDER = ("star", "u4", "acls")
def coin_events(sym, ex, wide):
    if sym not in BN: return
    F = {k: bflag(ex[k]) for k in ORDER}; idx = ex.index
    bu4 = B_u4.reindex(idx).fillna(False).values; bq = B_q.reindex(idx).fillna(False).values
    any_ = np.zeros(len(idx), bool)
    for k in ORDER: any_ |= F[k].values
    last = {}; sg = SIG.get(sym, {}); jo = JO.get(sym, set()); tk = TK.get(sym, set())
    Fv = {k: F[k].values for k in ORDER}
    for i in np.where(any_)[0]:
        t = idx[i]
        yeni = lambda k: last.get(k) is None or (t - last[k]) >= pd.Timedelta(hours=8 if k == "star" else 4)
        fo = [k for k in ORDER if Fv[k][i] and bu4[i] and (k in jo or wide) and yeni(k)]
        ft = [] if wide else [k for k in ORDER if Fv[k][i] and (sg.get(k, (False, 4))[0] or (k in tk and bq[i])) and k not in fo and yeni(k)]
        for k in fo + ft: last[k] = t
        z = zat(sym, t); rz = float(RZ[sym].get(t, np.nan))
        if fo:
            if wide:
                if np.isfinite(z) and z >= 2: add("ana", "🌐🤝", sym, t, 4)
                elif np.isfinite(z) and z >= 0: add("yedek", "🌐🤝 eşik altı", sym, t, 4)
            else:
                if np.isfinite(z) and z >= 0: add("ana", "🤝", sym, t, 4)
                elif np.isfinite(rz) and rz >= 2: add("ana", "🚀🤝", sym, t, 4)
                else: add("panel", "🤝 prim<0", sym, t, 4)
        if ft:
            k0 = ft[0]; on0, h0 = sg.get(k0, (False, 4)); sessiz = (not on0) or (k0 in tk and bq[i])
            H0 = h0 if on0 else 4; zb = float(ZB.get(t, np.nan)) if ZB is not None else np.nan
            zit = bool(sessiz and np.isfinite(z) and z > 0 and np.isfinite(zb) and -1 < zb <= 0)
            mom = (not zit) and not (np.isfinite(z) and z >= 0) and np.isfinite(rz) and rz >= 2
            if zit: add("ana", "🔀", sym, t, 4)
            elif mom: add("ana", "🚀", sym, t, H0)
            elif np.isfinite(z) and z >= 0: add("panelden", "🔇/🪙", sym, t, H0)
            else: add("panel", "🔇/🪙 prim<0", sym, t, H0)
def events_h(mask, H):
    out, last = [], -10**9
    for i in np.where(mask)[0]:
        if i - last >= H: out.append(i); last = i
    return np.array(out, int)
for s in MAIN:
    if s in EXC: coin_events(s, EXC[s], False)
for s in GEN:
    if s in EXW: coin_events(s, EXW[s], True)
DIS = sorted(set(EXW) - set(GEN) - set(MAIN))                                # araştırmada olup canlı geniş listeye ALINMAYAN coin'ler (seçim etkisi için)
EV_DIS = []
_EV = EV; EV = EV_DIS
for s in DIS:
    if s in EXW: coin_events(s, EXW[s], True)
EV = _EV
def ev24(sym, X, wide):
    if sym not in BN: return
    X = X.reindex(pd.date_range(X.index[0], X.index[-1], freq="1h", tz="UTC"))
    m = np.nan_to_num(((X.S24 > 0) & (X.C24 >= X.T10_24)).values.astype(float)).astype(bool) & X.T10_24.notna().values
    for i in events_h(m, 24):
        t = X.index[i]; z = zat(sym, t); rz = float(RZ[sym].get(t, np.nan))
        if wide:
            if np.isfinite(z) and z >= 1.5: add("ana", "🌐🧪", sym, t, 24)
        else:
            if np.isfinite(z) and z >= 0: add("ana", "📉🔥🧪", sym, t, 24) if (np.isfinite(rz) and rz <= -2) else add("panelden", "🧪 ana coin", sym, t, 24)
            elif np.isfinite(rz) and rz >= 2: add("ana", "🚀🧪", sym, t, 24)
            else: add("panel", "🧪 prim<0", sym, t, 24)
for s in MAIN24:
    if s in E24M: ev24(s, E24M[s], False)
for s in GEN24:
    if s in E24W: ev24(s, E24W[s], True)
END_EXPORT = max(x.index[-1] for x in list(EXW.values()) + list(EXC.values()))
for _, r in PA.iterrows():
    s = r.coin + "USDT"
    if s not in Z or s not in BN: continue
    z = Z[s]; z = z[z.index <= END_EXPORT]; m = (z >= r.esik).fillna(False).values
    for i in events_h(m, int(r.saat)):
        t = z.index[i]; rz = float(RZ[s].get(t, np.nan))
        add("ana", "📉🔥💵", s, t, int(r.saat)) if (np.isfinite(rz) and rz <= -2) else add("panelden", "💵", s, t, int(r.saat))
E = pd.DataFrame(EV, columns=["sinif", "tur", "sym", "t", "H", "k"]); E = E[E.t >= P1].reset_index(drop=True)
yaz(f"## B) Canlı kurallarla yeniden kurulan sinyaller ({P1:%d.%m.%Y} → {END_EXPORT:%d.%m.%Y}, model dışa aktarımlarının bittiği gün)")
yaz("```"); yaz(E.groupby(["sinif", "tur"]).size().to_string()); yaz("```")
# ---------------- 4) sonuç (test yöntemi: saat kapanışı giriş, saatlik YÜKSEK ile 🎯, süre sonu kapanış) ----------------
CACHE = {}
def outc(sym, H, k):
    key = (sym, H, k)
    if key in CACHE: return CACHE[key]
    d = BN[sym]; c, h = d.c, d.h; lr = np.log(c).diff(); sig = lr.rolling(720, min_periods=168).std()
    fmax = h.shift(-1).rolling(H).max().shift(-(H - 1)); cH = c.shift(-H); r_end = cH / c - 1
    if k > 0:
        tr = k * sig * np.sqrt(H); hit = (fmax >= c * (1 + tr)); ret = pd.Series(np.where(hit, tr, r_end), index=c.index); ret[fmax.isna() | cH.isna() | sig.isna()] = np.nan
    else: ret = r_end; hit = pd.Series(False, index=c.index)
    CACHE[key] = (ret, r_end, hit); return CACHE[key]
BASE = {}
def base(sym, H, k, cost):                                                   # rastgele giriş tabanı: aynı coin, ±30 gün, her saat
    key = (sym, H, k, cost)
    if key not in BASE:
        ret = outc(sym, H, k)[0]; n = 100 * ret - cost
        BASE[key] = ((n > 0).astype(float).where(ret.notna()).rolling(1464, center=True, min_periods=300).mean(), n.rolling(1464, center=True, min_periods=300).mean())
    return BASE[key]
def olc(E):
    R = np.full(len(E), np.nan); RE = R.copy(); HIT = np.zeros(len(E), bool); BH = {c: R.copy() for c in KOM}; BN_ = {c: R.copy() for c in KOM}
    for (sym, H, k), gi in E.groupby(["sym", "H", "k"]).groups.items():
        ret, r_end, hit = outc(sym, H, k); tt = E.loc[gi, "t"]
        R[gi] = ret.reindex(tt).values; RE[gi] = r_end.reindex(tt).values; HIT[gi] = hit.reindex(tt).fillna(False).values
        for c in KOM:
            bh, bnn = base(sym, H, k, c); BH[c][gi] = bh.reindex(tt).values; BN_[c][gi] = bnn.reindex(tt).values
    E = E.copy(); E["r"] = R * 100; E["r_end"] = RE * 100; E["tp"] = HIT
    for c in KOM: E[f"bh{c}"] = BH[c] * 100; E[f"bn{c}"] = BN_[c]
    return E[np.isfinite(E.r)]
E = olc(E)
def boot_ci(v, t, reps=500):
    if len(v) < 10: return (np.nan, np.nan)
    wk = pd.DatetimeIndex(t).floor("7D"); gi = pd.Series(np.arange(len(v))).groupby(wk).indices; ks = list(gi); rg = np.random.default_rng(1)
    bs = [v[np.concatenate([gi[ks[j]] for j in rg.integers(0, len(ks), len(ks))])].mean() for _ in range(reps)]; return np.percentile(bs, 5), np.percentile(bs, 95)
def satir(G, ad):
    out = []
    for dn, a, b in DON:
        x = G[(G.t >= a) & (G.t < b)]
        if not len(x): out.append(f"{dn}: —"); continue
        hr = x.groupby("t").agg(r=("r", "mean")); n = len(x); nh = len(hr)
        s = (f"{dn}: n={n} ({nh} ayrı saat) · süre sonu %{100*(x.r_end - 0.04 > 0).mean():.0f} · 🎯 ile %{100*(x.r - 0.04 > 0).mean():.0f} "
             f"[rastgele giriş, aynı hedef: %{x['bh0.04'].mean():.0f}] · saat-kümeli 🎯 %{100*(hr.r - 0.04 > 0).mean():.0f} · net/işlem "
             + " / ".join(f"{x.r.mean() - c:+.2f}" for c in KOM) + f" (maliyet {'/'.join(str(c) for c in KOM)}) [rastgele: {x['bn0.04'].mean():+.2f} / {x['bn0.2'].mean():+.2f}]")
        lo, hi = boot_ci((x.r - 0.20).values, x.t.values); s += f" · %90 GA (maliyet 0,20, haftalık blok): {lo:+.2f}…{hi:+.2f}"
        out.append(s)
    return f"**{ad}**\n" + "\n".join("  - " + o for o in out)
yaz("\n## C) Sınıf sınıf sonuç — test yöntemiyle (giriş = sinyal saati kapanışı)")
yaz("_isabet = net > 0 (maliyet %0,04 ile, testteki gibi) · [rastgele giriş] = aynı coin'de ±30 gün içindeki TÜM saatlerde aynı 🎯 kuralı · saat-kümeli = aynı saatteki sinyallerin ortalaması tek gözlem_\n")
for sn in ("ana", "yedek", "panelden"):
    G = E[E.sinif == sn]; yaz(satir(G, f"{sn} (hepsi, 🎯 {G.k.iloc[0] if len(G) else ''}σ)"))
    for tur, GG in G.groupby("tur"):
        if len(GG) >= 30: yaz(satir(GG, f"  ↳ {sn} · {tur}"))
yaz("")
# seçim etkisi: araştırmada olup canlıya alınmayan geniş coin'ler
ED = pd.DataFrame(EV_DIS, columns=["sinif", "tur", "sym", "t", "H", "k"]); ED = ED[ED.t >= P1].reset_index(drop=True)
if len(ED):
    ED = olc(ED); yaz("### Seçim etkisi: araştırmada taranıp canlı geniş listeye ALINMAYAN coin'ler (aynı kurallarla)")
    for sn in ("ana", "yedek"):
        if (ED.sinif == sn).any(): yaz(satir(ED[ED.sinif == sn], f"alınmayanlar · {sn}"))
# aynı saatte BTC sinyali varken sinyalsiz geniş coin'ler (🔸 yedek için plasebo): coin'in kendi sinyali bir şey katıyor mu?
yaz("\n### Plasebo: 🔸 yedek saatlerinde, coin sinyali OLMAYAN ama primi aynı aralıkta (0…2) olan geniş coin'ler, aynı 🎯 0,50σ / 4 saat")
Y = E[E.sinif == "yedek"]; PL = []
for t, gy in Y.groupby("t"):
    have = set(gy.sym)
    for s in GEN:
        if s in have or s not in BN: continue
        z = zat(s, t)
        if np.isfinite(z) and 0 <= z < 2: PL.append(("plasebo", "yedek-plasebo", s, t, 4, 0.5))
if PL:
    PP = olc(pd.DataFrame(PL, columns=["sinif", "tur", "sym", "t", "H", "k"])); yaz(satir(PP, "plasebo (sinyalsiz coin'ler, aynı saatler)"))
# ---------------- 5) 1 dakikalık mumla gerçekçi giriş/çıkış (örneklem) ----------------
yaz("\n## D) Gerçekçi uygulama — 1 dakikalık mum (rastgele örneklem)")
yaz("_E0 = test yöntemi 1 dk ile (giriş saat kapanışı, hedef saat başından itibaren) · E1 = mesajdan sonra piyasa alışı (sinyal saati + 6 dk), hedef ve çıkış 1 dk, çıkış saati +6 dk · E2 = mesajdaki fiyattan limit alış (60 dk geçerli), dolmazsa işlem yok_\n")
def k1m(sym, a, b):
    rows, cur = [], int(a.timestamp() * 1000); end = int(b.timestamp() * 1000)
    s = requests.Session()
    while cur < end:
        d = None
        for k in range(4):
            try:
                r = s.get("https://data-api.binance.vision/api/v3/klines", params=dict(symbol=sym, interval="1m", startTime=cur, endTime=end, limit=1000), timeout=20)
                if r.status_code == 200: d = r.json(); break
            except Exception: pass
            time.sleep(1 + k)
        if not d: break
        rows += d; cur = d[-1][0] + 60_000
        if len(d) < 1000: break
    if not rows: return None
    m = pd.DataFrame([x[:5] for x in rows], columns=["t", "o", "h", "l", "c"]).astype(float); m.index = pd.to_datetime(m.t.astype("int64"), unit="ms", utc=True); return m   # indeks = dakikanın AÇILIŞI
def sim1m(row):
    sym, t, H, k = row.sym, row.t, int(row.H), float(row.k)
    m = k1m(sym, t - pd.Timedelta(minutes=1), t + pd.Timedelta(hours=H, minutes=8))
    if m is None or len(m) < H * 50: return None
    c = BN[sym].c; lr = np.log(c[c.index <= t]).diff().dropna().iloc[-720:]
    if len(lr) < 168 or t not in c.index: return None
    sg = lr.std(); tr = k * sg * np.sqrt(H); p0 = float(c[t]); out = {}
    def run(entry_t, p_in, tgt, exit_t):
        w = m[(m.index >= entry_t) & (m.index < exit_t)]
        if not len(w): return None
        hit = w.index[w.h.values >= tgt]
        if len(hit): return tgt / p_in - 1, True
        last = m[m.index < exit_t]
        return float(last.c.iloc[-1]) / p_in - 1, False
    # E0: test yöntemi (giriş = saat kapanışı, hedef saatin ilk dakikasından)
    out["e0"] = run(t, p0, p0 * (1 + tr), t + pd.Timedelta(hours=H))
    # mesaj fiyatı: 🤝 / 🔇 = saat kapanışı; 🧪 / 💵 = anlık fiyat (≈ +4 dk)
    anlik = ("🧪" in row.tur) or ("💵" in row.tur)
    pm_row = m[m.index == t + pd.Timedelta(minutes=3)]
    pm = float(pm_row.c.iloc[0]) if (anlik and len(pm_row)) else p0
    tgt = pm * (1 + tr); ex_t = t + pd.Timedelta(hours=H, minutes=6)
    e1r = m[m.index == t + pd.Timedelta(minutes=5)]
    out["e1"] = run(t + pd.Timedelta(minutes=6), float(e1r.c.iloc[0]), tgt, ex_t) if len(e1r) else None
    w = m[(m.index >= t + pd.Timedelta(minutes=6)) & (m.index < t + pd.Timedelta(minutes=66))]
    f = w.index[w.l.values <= pm]
    if len(f):
        p_in = min(pm, float(w.o.iloc[0])) if f[0] == w.index[0] else pm          # limit piyasanın üstündeyse hemen piyasadan dolar
        out["e2"] = run(f[0] + pd.Timedelta(minutes=1), p_in, tgt, ex_t)
    else: out["e2"] = "dolmadi"
    return out
rg = np.random.default_rng(7); S = []
for sn in ("ana", "yedek", "panelden"):
    for dn, a, b in DON:
        x = E[(E.sinif == sn) & (E.t >= a) & (E.t < b)]
        if len(x): S.append(x.iloc[rg.choice(len(x), min(150, len(x)), replace=False)])
S = pd.concat(S).reset_index(drop=True)
with ThreadPoolExecutor(12) as ex: RES = list(ex.map(sim1m, [r for r in S.itertuples()]))
S["res"] = RES; S = S[S.res.notna()]
for sn in ("ana", "yedek", "panelden"):
    x = S[S.sinif == sn]
    if not len(x): continue
    def st(key, cost):
        v = [r[key] for r in x.res if r.get(key) not in (None, "dolmadi")]; nd = sum(1 for r in x.res if r.get(key) == "dolmadi")
        if not v: return "—"
        a = np.array([q[0] for q in v]) * 100 - cost
        return f"n={len(v)}{f' (+{nd} dolmadı, dolma %{100*len(v)/(len(v)+nd):.0f})' if nd else ''} · isabet %{100*(a > 0).mean():.0f} · net {a.mean():+.2f}"
    yaz(f"**{sn}** (örneklem {len(x)}, hourly yöntemle aynı sinyaller: isabet %{100*(x.r - 0.04 > 0).mean():.0f}, net {x.r.mean() - 0.04:+.2f})")
    for key, ad in (("e0", "E0 test yöntemi 1 dk"), ("e1", "E1 piyasa +6 dk"), ("e2", "E2 limit (mesaj fiyatı)")):
        yaz(f"  - {ad}: maliyet 0,04 → {st(key, 0.04)} · maliyet 0,20 → {st(key, 0.20)}")
E.drop(columns=[c for c in E.columns if c.startswith("b")]).to_csv("dt/gecmis_olaylar.csv.gz", index=False)
yaz(f"\n_süre {time.time() - T0:.0f} sn_")
open("dt/analiz_sonuc.md", "w").write("\n".join(L) + "\n")
