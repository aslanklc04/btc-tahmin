# btcyon5.py — PROTOKOL_btcyon5.md: V1 emir defteri · V2 opsiyon akışı · V3 birleşik → btcyon5_sonuc.md
import io, time, contextlib, numpy as np, pandas as pd
with contextlib.redirect_stdout(io.StringIO()): import btcyon4 as W
N = W.N; T0 = time.time(); out = []
def yaz(s=""): out.append(s); print(s, flush=True)
TS = lambda s: pd.Timestamp(s, tz="UTC")
KB, H = N.KB, N.H
KT = pd.read_parquet("btcyon5_kitap.parquet").set_index("t").sort_index()
try: OP = pd.read_parquet("btcyon5_opsiyon.parquet")
except Exception: OP = None
bas = KT.dropna(how="all").index.min()
if bas <= TS("2022-02-01"): DON = [("K 2022–23", TS("2022-01-01"), TS("2024-01-01")), ("C1 2024", TS("2024-01-01"), TS("2025-01-01")), ("C2 2025–26", TS("2025-01-01"), TS("2026-10-28"))]
else:
    k0 = bas.floor("D"); DON = [(f"K {k0:%Y-%m}…", k0, k0 + pd.DateOffset(months=12)), (f"C1 {k0 + pd.DateOffset(months=12):%Y-%m}…", k0 + pd.DateOffset(months=12), k0 + pd.DateOffset(months=24)),
                                (f"C2 {k0 + pd.DateOffset(months=24):%Y-%m}…", k0 + pd.DateOffset(months=24), TS("2026-10-28"))]
K_END, C1_END = DON[0][2], DON[1][2]
def donem(ix):
    ix = pd.DatetimeIndex(ix); d = np.full(len(ix), None, object)
    for ad, a, b in DON: d[(ix >= a) & (ix < b)] = ad
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
def baslik(): yaz("| kural | " + " | ".join(a for a, _, _ in DON) + " | |"); yaz("|---|---|---|---|---|")
def plasebo(aile, n=20, seed=21):
    rng = np.random.default_rng(seed); kur = [s for s in SONUC if s[0] == aile]; a0, a1 = KB.index[0], KB.index[-1]; span = int((a1 - a0).total_seconds() // 3600); say = []
    for _ in range(n):
        off = pd.Timedelta(hours=int(rng.integers(90 * 24, span - 90 * 24))); g = 0
        for _, _, sig, nsaat, minn, esik, _, _ in kur:
            t = sig.t + off; t = t.where(t <= a1, t - pd.Timedelta(hours=span + 1)); g += ozet(deg(pd.DataFrame({"t": t.dt.floor("h"), "yon": sig.yon.values}), nsaat), minn, esik)[1]
        say.append(g)
    yaz(f"\n**{aile}: yön şartı ✅ {sum(s[6] for s in kur)} / {len(kur)} · sinyal adayı {sum(s[7] for s in kur)}** · plasebo (zaman kaydırma ×{n}) ortalama {np.mean(say):.1f}, en çok {max(say)}")
dn = donem(KB.index); kK = dn == DON[0][0]
def esikli(aile, ad, v, ufuklar, gunluk=False):
    for hs in ufuklar:
        fw = np.log(KB.c.shift(-hs) / KB.o.shift(-1))
        if gunluk:                                                                             # günlük değer → ertesi gün 00:00 girişi
            vv = v.dropna(); tt = vv.index + pd.Timedelta(days=1) - pd.Timedelta(hours=1)          # sinyal saati = D 23:00 → giriş D+1 00:00
            vs = pd.Series(vv.values, index=tt).reindex(KB.index)
        else: vs = v.reindex(KB.index)
        qa, qb = vs[kK].quantile(0.2), vs[kK].quantile(0.8)
        for kad, m in (("alt %20", vs <= qa), ("üst %20", vs > qb)):
            m = m.fillna(False); kar = 1 if fw[m & kK].mean() > 0 else -1
            kural(aile, f"{ad} {kad} → {hs} s {'AL' if kar == 1 else 'SAT'} (K ort. {100 * fw[m & kK].mean():+.2f})", pd.DataFrame({"t": KB.index[m.values] + pd.Timedelta(hours=1), "yon": kar}), hs)
yaz("# 🧭 BTC'nin YÖNÜ — 5. tur: emir defteri · opsiyon · PROTOKOL_btcyon5.md")
yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · emir defteri arşivi {bas:%Y-%m-%d} → {KT.index.max():%Y-%m-%d} · dönemler: " + " · ".join(f"{a} ({x:%Y-%m}→{y:%Y-%m})" for a, x, y in DON)
    + (f" · opsiyon işlemi {len(OP):,} ({OP.t.min():%Y-%m-%d} → {OP.t.max():%Y-%m-%d})" if OP is not None else " · opsiyon verisi yok") + "_\n")
# ======================= V1 =======================
yaz("## V1 — Emir defteri dengesizliği (±%1 / %2 / %5 içindeki alım − satım emri)")
def d(k):
    a, b = f"p-{k:g}", f"p+{k:g}"
    return (KT[a] - KT[b]) / (KT[a] + KT[b]) if a in KT and b in KT else None
F = pd.DataFrame(index=KT.index)
for k in (1, 2, 5):
    x = d(k)
    if x is not None: F[f"d{k}"] = x
if "d2" in F: F["d2_24"] = F.d2 - F.d2.shift(24)
if "d1" in F and "d5" in F: F["yakin_uzak"] = F.d1 - F.d5
yaz(f"_bantlar: {', '.join(KT.columns)} · K medyanları: " + ", ".join(f"{c} {F[c].reindex(KB.index)[kK].median():+.3f}" for c in F.columns) + "_"); baslik()
AD1 = {"d1": "dengesizlik ±%1", "d2": "dengesizlik ±%2", "d5": "dengesizlik ±%5", "d2_24": "±%2 dengesizlik 24 s değişim", "yakin_uzak": "yakın − uzak (±%1 − ±%5)"}
for c in F.columns: esikli("V1", AD1[c], F[c], (4, 24))
plasebo("V1")
# ======================= V2 =======================
yaz("\n## V2 — Opsiyon akışı (Deribit işlem örneklemi, günlük)")
G = pd.DataFrame()
if OP is not None and len(OP):
    O = OP.copy(); O["prim"] = O.fiyat * O.miktar * O.endeks; O["gun"] = O.t.dt.floor("D"); O["vg"] = (O.vade - O.t).dt.total_seconds() / 86400; O["m"] = O.kul / O.endeks - 1
    gb = O.groupby("gun")
    def top(mask): return O[mask].groupby("gun").prim.sum()
    pb, cb, ps, cs = top((O.tur == "P") & (O.yon == 1)), top((O.tur == "C") & (O.yon == 1)), top((O.tur == "P") & (O.yon == -1)), top((O.tur == "C") & (O.yon == -1))
    G = pd.DataFrame({"pc_alim": np.log(pb / cb), "net": ((cb - cs) - (pb - ps)) / gb.prim.sum()})
    orta = (O.vg >= 7) & (O.vg <= 60)
    ivp = O[orta & (O.tur == "P") & (O.m >= -0.15) & (O.m <= -0.05) & (O.iv > 0)].groupby("gun").iv.mean(); ivc = O[orta & (O.tur == "C") & (O.m >= 0.05) & (O.m <= 0.15) & (O.iv > 0)].groupby("gun").iv.mean()
    atm = O[orta & (O.m.abs() <= 0.02) & (O.iv > 0)].groupby("gun").iv.mean()
    G["skew"] = ivp - ivc; G["atm3"] = atm - atm.shift(3); G = G.sort_index()
    yaz(f"_gün {len(G)} · K medyanları: put/call alım log {G.pc_alim[G.index < K_END].median():+.2f}, net {G.net[G.index < K_END].median():+.3f}, çarpıklık {G.skew[G.index < K_END].median():+.1f} IV puanı_"); baslik()
    AD2 = {"pc_alim": "put/call agresif alım oranı", "net": "agresif net yön (call − put)", "skew": "çarpıklık (OTM put IV − call IV)", "atm3": "ATM IV 3 g değişim"}
    for c in AD2: esikli("V2", AD2[c], G[c], (24, 72), gunluk=True)
    plasebo("V2")
else: yaz("Opsiyon verisi alınamadı.")
# ======================= V3 =======================
yaz("\n## V3 — Birleşik (ridge, 24 s): emir defteri + opsiyon + W4 skoru")
Fw, cols4, y = W.F, W.cols, W.y; w4 = pd.Series(np.nan, index=Fw.index)
for a, b_, eb in ((TS("2022-01-01"), TS("2024-01-01"), TS("2024-01-01")), (TS("2024-01-01"), TS("2025-01-01"), TS("2024-01-01")), (TS("2025-01-01"), TS("2026-10-28"), TS("2025-01-01"))):
    tr = (Fw.index < eb - pd.Timedelta(hours=25)) & y.notna().values & (Fw.index >= TS("2022-01-01")); md = W.rf(Fw.loc[tr, cols4], y[tr])
    te = (Fw.index >= a) & (Fw.index < b_); w4[te] = W.rp(md, Fw.loc[te, cols4]).values
X3 = pd.DataFrame(index=KB.index); X3["w4"] = w4.reindex(KB.index)
for c in ("d2", "yakin_uzak"):
    if c in F: X3[c] = F[c].reindex(KB.index)
for c in ("pc_alim", "net", "skew"):
    if c in G: X3[c] = G[c].shift(1).reindex(KB.index.floor("D")).values                          # dünün opsiyon değeri bugün 00:00'dan itibaren
yy = np.log(KB.c.shift(-24) / KB.o.shift(-1)); sig = []; cl = list(X3.columns)
for a, b_, eb in ((DON[0][1], K_END, K_END), (K_END, C1_END, K_END), (C1_END, DON[2][2], C1_END)):
    tr = (X3.index >= DON[0][1]) & (X3.index < eb - pd.Timedelta(hours=25)) & yy.notna().values; md = W.rf(X3.loc[tr, cl], yy[tr]); ptr = W.rp(md, X3.loc[tr, cl]); q10, q90 = ptr.quantile(0.1), ptr.quantile(0.9)
    te = (X3.index >= a) & (X3.index < b_); p = W.rp(md, X3.loc[te, cl]); ti = p.index + pd.Timedelta(hours=1)
    sig += [pd.DataFrame({"t": ti[(p >= q90).values], "yon": 1}), pd.DataFrame({"t": ti[(p <= q10).values], "yon": -1})]
    if a == K_END: yaz("_K modeli katsayıları (baz puan / 1 std): " + ", ".join(f"{c} {1e4 * v:+.1f}" for c, v in zip(cl, md[2])) + "_")
baslik(); kural("V3", "birleşik skor üst/alt %10 → 24 s", pd.concat(sig), 24); plasebo("V3")
yaz("\n## Özet")
for a in ("V1", "V2", "V3"):
    k = [s for s in SONUC if s[0] == a]; yaz(f"- {a}: {len(k)} kural · yön ✅ {sum(s[6] for s in k)} · sinyal adayı 🎯 {sum(s[7] for s in k)}" + "".join(f"\n  - {'🎯' if s[7] else '✅'} {s[1]}" for s in k if s[6] or s[7]))
yaz(f"\n_süre {time.time() - T0:.0f} sn_")
open("btcyon5_sonuc.md", "w").write("\n".join(out) + "\n")
