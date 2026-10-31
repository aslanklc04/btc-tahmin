# btcyon7.py — PROTOKOL_btcyon7.md: "yön saati" oy birliği → btcyon7_sonuc.md
import io, time, contextlib, numpy as np, pandas as pd
with contextlib.redirect_stdout(io.StringIO()): import btcyon4 as W
N = W.N; T0 = time.time(); out = []
def yaz(s=""): out.append(s); print(s, flush=True)
TS = lambda s: pd.Timestamp(s, tz="UTC"); D, B, KB, KD, F = N.D, N.B, N.KB, N.KD, W.F
DON = [("K 2022–23", TS("2022-01-01"), TS("2024-01-01")), ("C1 2024", TS("2024-01-01"), TS("2025-01-01")), ("C2 2025–26", TS("2025-01-01"), TS("2026-10-28"))]
def donem(ix):
    ix = pd.DatetimeIndex(ix); d = np.full(len(ix), None, object)
    for ad, a, b in DON: d[(ix >= a) & (ix < b)] = ad
    return d
def deg(sig, nsaat, K=KB):
    R = []; serbest = None; ix = K.index
    for t, yon in sig.sort_values("t")[["t", "yon"]].itertuples(index=False):
        if serbest is not None and t < serbest: continue
        i = ix.searchsorted(t)
        if i >= len(ix) or ix[i] != t or i + nsaat > len(ix): continue
        net, j = N.islem(K, i, int(yon), 10.0, None, nsaat); R.append((t, yon, yon * (K.c.values[i + nsaat - 1] / K.o.values[i] - 1), net)); serbest = ix[j] + pd.Timedelta(hours=1)
    R = pd.DataFrame(R, columns=["t", "yon", "ham", "net"]); R["don"] = donem(R.t) if len(R) else []; return R
def ozet(R, minn=20, esik=0.005):
    hs, yok, aok = [], True, True
    for ad, _, _ in DON:
        x = R[R.don == ad] if len(R) else R
        if not len(x): hs.append("0"); yok = aok = False; continue
        yi, ii, nt = (x.ham > 0).mean(), (x.net > 0).mean(), x.net.mean()
        hs.append(f"{len(x)} · yön %{100 * yi:.0f} · isabet %{100 * ii:.0f} · {100 * nt:+.2f}")
        if not (len(x) >= minn and yi >= 0.57 and nt > 0): yok = False
        if not (len(x) >= minn and ii >= 0.65 and nt >= esik): aok = False
    return hs, yok, aok
g = D.index; kK = (g >= DON[0][1]) & (g < DON[0][2])
dv = D.dvol; dv3 = dv / dv.shift(3) - 1; dvz = (dv - dv.rolling(90, min_periods=60).mean().shift(1)) / dv.rolling(90, min_periods=60).std().shift(1)
lsz = N.zprev(D.ls, 180); dxy5 = pd.Series(N.son_islem(N.GD.dxy, lambda s_: s_ / s_.shift(5) - 1), index=D.index).shift(-1)      # B.dxy5[D+1] = D'ye kadar bilinen son değer
h23 = lambda c: F[c].reindex(g + pd.Timedelta(hours=23)).values
kz, uz = pd.Series(h23("kz"), index=g), pd.Series(h23("uz"), index=g)
neg = F.negdiv.groupby(F.index.floor("D")).max().reindex(g).fillna(0); pos = F.posdiv.groupby(F.index.floor("D")).max().reindex(g).fillna(0)
ma200 = D.c.rolling(200).mean(); trend = D.c > ma200
fw = np.log(D.c.shift(-3) / D.c)                                                              # D sonu → D+3 sonu (K'de oy yönü için)
q = lambda s, p: s[kK].quantile(p)
DUR = {"😨 korku": [((dvz >= 2) | (dv3 >= q(dv3, 0.9)))], "👥 kalabalık": [lsz >= 1, lsz <= -1], "💵 dolar 5 g": [dxy5 >= q(dxy5, 0.8), dxy5 <= q(dxy5, 0.2)],
       "🇰🇷 Kore primi": [kz >= q(kz, 0.8), kz <= q(kz, 0.2)], "🪙 USDT primi": [uz >= q(uz, 0.8), uz <= q(uz, 0.2)], "🔻🔺 uyumsuzluk": [neg == 1, pos == 1], "📈 trend": [trend, ~trend & ma200.notna()]}
OY = pd.DataFrame(0, index=g, columns=list(DUR)); yaz("# 🧭 BTC'nin YÖNÜ — 7. tur: yön saati · PROTOKOL_btcyon7.md\n"); yaz("_Bileşen oy yönleri (K'de durum varken sonraki 3 g ort. getirisi → oy):_")
for ad, ms in DUR.items():
    for m in ms:
        m = m.fillna(False).astype(bool); ort = fw[m & kK].mean(); oy = 1 if ort > 0 else -1; OY.loc[m, ad] += oy
        yaz(f"- {ad}: {int(m[kK].sum())} gün (K) · K ort. {100 * ort:+.2f}% → oy {oy:+d}")
skor = OY.sum(axis=1); yaz(f"\n_skor dağılımı (tüm günler): " + " · ".join(f"{k:+d}: {v}" for k, v in skor.value_counts().sort_index().items()) + "_\n")
yaz("| kural | ufuk | K 2022–23 | C1 2024 | C2 2025–26 | | ETH (C1∪C2) | SOL (C1∪C2) |"); yaz("|---|---|---|---|---|---|---|---|")
SON = []
for esik in (2, 3):
    for yad, m, yon in (("AL", skor >= esik, 1), ("SAT", skor <= -esik, -1), ("AL+SAT", None, None)):
        if m is None: sig = pd.concat([pd.DataFrame({"t": g[(skor >= esik).values] + pd.Timedelta(days=1), "yon": 1}), pd.DataFrame({"t": g[(skor <= -esik).values] + pd.Timedelta(days=1), "yon": -1})])
        else: sig = pd.DataFrame({"t": g[m.values] + pd.Timedelta(days=1), "yon": yon})
        for hs in (24, 72):
            hs_, yok, aok = ozet(deg(sig, hs)); ek = []
            for cn, K_ in KD.items():
                Rc = deg(sig[sig.t >= DON[1][1]], hs, K_); ek.append(f"{len(Rc)} · yön %{100 * (Rc.ham > 0).mean():.0f} · {100 * Rc.net.mean():+.2f}" if len(Rc) else "0")
            yaz(f"| skor {'≥ +' if yad == 'AL' else ('≤ −' if yad == 'SAT' else '±')}{esik} → {yad} | {hs} s | " + " | ".join(hs_) + f" | {'🎯' if aok else ('✅' if yok else '')} | " + " | ".join(ek) + " |"); SON.append((f"{yad} {esik} {hs}", hs, sig, yok, aok))
rng = np.random.default_rng(7); a0, a1 = KB.index[0], KB.index[-1]; span = int((a1 - a0).total_seconds() // 86400); say = []
for _ in range(50):
    off = pd.Timedelta(days=int(rng.integers(90, span - 90))); gg = 0
    for ad, hs, sig, *_ in SON:
        t = sig.t + off; t = t.where(t <= a1, t - pd.Timedelta(days=span + 1)); gg += ozet(deg(pd.DataFrame({"t": t.dt.floor("D"), "yon": sig.yon.values}), hs))[1]
    say.append(gg)
yaz(f"\n**Geçen (yön şartı): {sum(s[3] for s in SON)} / {len(SON)} · sinyal adayı {sum(s[4] for s in SON)}** · plasebo (×50) ortalama {np.mean(say):.2f}, en çok {max(say)}")
for ad, hs, sig, yok, aok in SON:
    if yok or aok: yaz(f"- {'🎯' if aok else '✅'} {ad}")
yaz(f"\n_süre {time.time() - T0:.0f} sn_"); open("btcyon7_sonuc.md", "w").write("\n".join(out) + "\n")
