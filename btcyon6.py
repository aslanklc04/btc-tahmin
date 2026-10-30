# btcyon6.py — PROTOKOL_btcyon6.md: korku ve rahatlık döngüsü (DVOL) → btcyon6_sonuc.md
import io, time, contextlib, numpy as np, pandas as pd
with contextlib.redirect_stdout(io.StringIO()): import btcneden as N
T0 = time.time(); out = []
def yaz(s=""): out.append(s); print(s, flush=True)
TS = lambda s: pd.Timestamp(s, tz="UTC"); D, KB, KD = N.D, N.KB, N.KD
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
def ozet(R, minn=15, esik=0.005):
    hs, yok, aok = [], True, True
    for ad, _, _ in DON:
        x = R[R.don == ad] if len(R) else R
        if not len(x): hs.append("0"); yok = aok = False; continue
        yi, ii, nt = (x.ham > 0).mean(), (x.net > 0).mean(), x.net.mean()
        hs.append(f"{len(x)} · yön %{100 * yi:.0f} · isabet %{100 * ii:.0f} · {100 * nt:+.2f}")
        if not (len(x) >= minn and yi >= 0.57 and nt > 0): yok = False
        if not (len(x) >= minn and ii >= 0.65 and nt >= esik): aok = False
    return hs, yok, aok
dv = D.dvol; dv3 = dv / dv.shift(3) - 1; dvz = (dv - dv.rolling(90, min_periods=60).mean().shift(1)) / dv.rolling(90, min_periods=60).std().shift(1)
r3 = D.c / D.c.shift(3) - 1; lsz = N.zprev(D.ls, 180); kK = (D.index >= DON[0][1]) & (D.index < DON[0][2])
q80, q90 = dv3[kK].quantile(0.8), dv3[kK].quantile(0.9); z10 = dvz[kK].quantile(0.1)
KUR = {"R1 korku sıçraması (DVOL 3 g ≥ K %80) → AL": (dv3 >= q80, 1), "R1b korku sıçraması (≥ K %90) → AL": (dv3 >= q90, 1),
       "R2 korku + düşüş (panik) → AL": ((dv3 >= q80) & (r3 <= 0), 1), "R3 korku + yükseliş → AL (bilgi)": ((dv3 >= q80) & (r3 > 0), 1),
       "R4 aşırı korku seviyesi (DVOL z ≥ 2) → AL": (dvz >= 2, 1), "R5 rahatlık (DVOL z ≤ K %10) + kalabalık uzun → SAT": ((dvz <= z10) & (lsz >= 1), -1),
       "R6 panik + kalabalık kısa → AL": ((dv3 >= q80) & (r3 <= 0) & (lsz <= 0), 1)}
yaz("# 🧭 BTC'nin YÖNÜ — 6. tur: korku ve rahatlık döngüsü · PROTOKOL_btcyon6.md")
yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · DVOL 3 g eşikleri (K): %80 = {100 * q80:+.1f}%, %90 = {100 * q90:+.1f}% · DVOL z %10 = {z10:.2f} · hücre: işlem · yön isabeti · isabet · işlem başı net %_\n")
yaz("| kural | ufuk | K 2022–23 | C1 2024 | C2 2025–26 | | ETH (C1∪C2) | SOL (C1∪C2) |"); yaz("|---|---|---|---|---|---|---|---|")
SON = []
for ad, (m, yon) in KUR.items():
    m = m.fillna(False); gun = D.index[m.values]; sig = pd.DataFrame({"t": gun + pd.Timedelta(days=1), "yon": yon})
    for hs in (72, 168):
        hs_, yok, aok = ozet(deg(sig, hs)); ek = []
        for cn, K_ in KD.items():
            Rc = deg(sig[sig.t >= DON[1][1]], hs, K_); ek.append(f"{len(Rc)} · yön %{100 * (Rc.ham > 0).mean():.0f} · {100 * Rc.net.mean():+.2f}" if len(Rc) else "0")
        yaz(f"| {ad} | {hs} s | " + " | ".join(hs_) + f" | {'🎯' if aok else ('✅' if yok else '')} | " + " | ".join(ek) + " |"); SON.append((ad, hs, sig, yok, aok))
rng = np.random.default_rng(6); a0, a1 = KB.index[0], KB.index[-1]; span = int((a1 - a0).total_seconds() // 3600); say = []
for _ in range(50):
    off = pd.Timedelta(days=int(rng.integers(90, span // 24 - 90))); g = 0
    for ad, hs, sig, *_ in SON:
        t = sig.t + off; t = t.where(t <= a1, t - pd.Timedelta(days=span // 24 + 1)); g += ozet(deg(pd.DataFrame({"t": t.dt.floor("D"), "yon": sig.yon.values}), hs))[1]
    say.append(g)
yaz(f"\n**Geçen (yön şartı): {sum(s[3] for s in SON)} / {len(SON)} · sinyal adayı {sum(s[4] for s in SON)}** · plasebo (×50 gün kaydırma) ortalama {np.mean(say):.2f}, en çok {max(say)}")
for ad, hs, sig, yok, aok in SON:
    if yok or aok: yaz(f"- {'🎯' if aok else '✅'} {ad} · {hs} s")
yaz(f"\n_süre {time.time() - T0:.0f} sn_"); open("btcyon6_sonuc.md", "w").write("\n".join(out) + "\n")
