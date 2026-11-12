# yeni80.py — PROTOKOL_yeni80.md: modelden bağımsız olay + limit giriş + yakın hedef → yeni80_sonuc.md
import glob, hashlib, itertools, os, time, numpy as np, pandas as pd
T0 = time.time(); out = []
def yaz(s=""): out.append(s); print(s, flush=True)
A = pd.concat([pd.read_parquet(f, columns=["t", "coin", "o", "h", "l", "c"]) for f in sorted(glob.glob("teknik3_mum_*.parquet"))], ignore_index=True)
A["t"] = pd.to_datetime(A.t, utc=True); A = A.drop_duplicates(["coin", "t"])
W = {k: A.pivot(index="t", columns="coin", values=k).sort_index().astype(float) for k in ("o", "h", "l", "c")}; del A
idx = pd.date_range(W["c"].index.min(), W["c"].index.max(), freq="1h"); W = {k: v.reindex(idx) for k, v in W.items()}
O, Hh, L, C = (W[k] for k in ("o", "h", "l", "c")); COL = list(C.columns); n = len(idx)
lc = np.log(C); lr = lc.diff(); sig = lr.rolling(720, min_periods=480).std().shift(1)
rb = lr["BTC"]; bvr = (rb.rolling(24).std() / rb.rolling(720, min_periods=480).std()); sb = rb.rolling(720, min_periods=480).std().shift(1)
r24, r4, r1 = lc.diff(24), lc.diff(4), lr
d_ = C.diff(); up = d_.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean(); dn = (-d_.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean(); rsi = 100 - 100 / (1 + up / dn)
kir = (C < O); k3 = kir & kir.shift(1) & kir.shift(2); s3 = lc.diff(3)
BV = pd.DataFrame(np.repeat((bvr >= 1.25).values[:, None], len(COL), 1), index=idx, columns=COL)
BTCok = pd.DataFrame(np.repeat((rb >= -0.5 * sb).values[:, None], len(COL), 1), index=idx, columns=COL)
z24 = r24 / (sig * np.sqrt(24)); z1 = r1 / sig; z3 = s3 / (sig * np.sqrt(3))
OLAY = {"E1 dip (24 s ≤ −2σ)": (z24 <= -2, -z24), "E2 derin dip (≤ −3σ)": (z24 <= -3, -z24), "E3 saatlik iğne (1 s ≤ −3σ)": (z1 <= -3, -z1), "E4 dip ∧ BTC oynak": ((z24 <= -2) & BV, -z24),
        "E5 BTC oynak ∧ coin 4 s ≤ −%1": (BV & (r4 <= np.log(0.99)), -r4), "E6 RSI14 ≤ 25": (rsi <= 25, -rsi), "E7 3 kırmızı saat ≤ −2σ√3": (k3 & (z3 <= -2), -z3), "E8 coin'e özgü iğne": ((z1 <= -3) & BTCok, -z1)}
Cv, Hv, Lv, Sv = C.values, Hh.values, L.values, sig.values; FL, FP, FON = 0.0002, 0.0005, 0.0001
def sonuc(j, i, k, H):
    if i + H >= n: return None
    G, s = Cv[i, j], Sv[i, j]
    if not (np.isfinite(G) and np.isfinite(s) and np.isfinite(Lv[i + 1, j])) or Lv[i + 1, j] > G: return None
    tp = G * (1 + k * s * np.sqrt(H))
    if Cv[i + 1, j] >= tp: ex, net = i + 1, tp / G - 1 - 2 * FL
    else:
        w = np.where(Hv[i + 2:i + H + 1, j] >= tp)[0]
        if len(w): ex, net = i + 2 + w[0], tp / G - 1 - 2 * FL
        else:
            ce = Cv[i + H, j]
            if not np.isfinite(ce): return None
            ex, net = i + H, ce / G - 1 - FL - FP
    return net - FON * (ex - i) / 8, ex
i0 = idx.searchsorted(pd.Timestamp("2022-06-01", tz="UTC"))
yari = np.array([int(hashlib.md5(c.encode()).hexdigest(), 16) % 2 for c in COL]); yil = idx.year.values
don_i = np.where(yil <= 2024, 0, np.where(yil == 2025, 1, 2)); AD = ["2022-06→24", "2025", "2026"]
def adaylar(mask, sev):
    mv, sv = mask.values, sev.values; E = {}
    for i in np.where(mv[i0:].any(axis=1))[0] + i0:
        js = np.where(mv[i])[0]; E[i] = js[np.argsort(-sv[i, js])]
    return E
def calistir(E, k, H):
    mes = np.full(len(COL), -1); R = []
    for i in sorted(E):
        say = 0
        for j in E[i]:
            if mes[j] >= i: continue
            say += 1
            v = sonuc(j, i, k, H)
            if v: R.append((i, j, v[0])); mes[j] = v[1]
            if say == 5: break
    D = pd.DataFrame(R, columns=["i", "j", "net"]); D["don"] = don_i[D.i.values]; D["yari"] = yari[D.j.values]
    return D
st = lambda v: (len(v), (v > 0).mean() if len(v) else np.nan, v.mean() if len(v) else np.nan)
f3 = lambda v: "{} · %{:.0f} · {:+.2f}".format(st(v)[0], 100 * st(v)[1], 100 * st(v)[2]) if len(v) else "—"
V = pd.read_csv("veri_seti.csv.gz", usecols=["t", "nm", "sinif", "tur", "rz", "fon", "b_vr"]); V["t"] = pd.to_datetime(V.t, utc=True); V = V[V.sinif.str.startswith("✅") & ~V.tur.isin(["🤝", "💵"])]
EL = set(V.t[(V.rz <= -2) | (V.fon >= 2) | (V.tur == "🔀") | ((V.tur == "🌐🧪") & (V.b_vr >= 1.25))])
AY = list(itertools.product((0.3, 0.45, 0.6), (4, 24))); rng = np.random.default_rng(808); gun_i = (idx.values.astype("datetime64[D]") - idx.values[0].astype("datetime64[D]")).astype(int)
yaz("# 🆕 Modelden bağımsız yeni sinyaller, %80+ hedef — PROTOKOL_yeni80.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {len(COL)} coin · saatlik veri · limit alış kapanıştan (1 saat), 🎯 = k·σ·√H · saat başına ≤ 5 coin · hücre: dolan işlem · isabet · net %_\n")
GEC = []
for ad, (mask, sev) in OLAY.items():
    E = adaylar(mask, sev); T = {a: calistir(E, *a) for a in AY}
    yaz(f"## {ad}"); yaz("| k | H | 2022-06→24 | 2025 | 2026 |"); yaz("|---|---|---|---|---|")
    for (k, H), D in T.items(): yaz(f"| {k} | {H} | " + " | ".join(f3(D[D.don == d].net) for d in range(3)) + " |")
    best = None
    for a, D in T.items():
        nn, ii, rr = st(D[(D.yari == 0) & (D.don == 0)].net)
        if nn >= 40 and ii >= 0.80 and rr >= 0.0015 and (best is None or rr > best[1]): best = (a, rr)
    if best is None: yaz("**Keşif: şartı sağlayan ayar yok → elendi**\n"); continue
    (k, H), D = best[0], T[best[0]]; ok = True
    for h, d in [(0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]:
        nn, ii, rr = st(D[(D.yari == h) & (D.don == d)].net); ok &= nn >= 30 and ii >= 0.75 and rr > 0
    for d in (1, 2):
        nn, ii, rr = st(D[D.don == d].net); ok &= ii >= 0.80 and rr >= 0.0015
    # plasebo: aynı gün aynı sayıda rastgele coin-saat
    gs = pd.Series(gun_i[D.i.values]).value_counts(); PLn = [[] for _ in range(3)]
    gun_bas = {g: np.searchsorted(gun_i, g) for g in gs.index}
    for _ in range(20):
        P = []
        for g, c in gs.items():
            got = 0
            for _t in range(c * 6):
                i = gun_bas[g] + rng.integers(24); j = rng.integers(len(COL))
                v = sonuc(j, i, k, H) if i + H < n else None
                if v: P.append((i, v[0])); got += 1
                if got == c: break
        P = pd.DataFrame(P, columns=["i", "net"]); P["don"] = don_i[P.i.values]
        for d in range(3): PLn[d].append(P[P.don == d].net.mean())
    pl = []
    for d in range(3):
        g_ = D[D.don == d].net.mean() > np.nanmax(PLn[d]); ok &= bool(g_); pl.append(f"{AD[d]} {100 * D[D.don == d].net.mean():+.2f} / rastgele en iyi {100 * np.nanmax(PLn[d]):+.2f} {'✔' if g_ else '✘'}")
    hc = " · ".join(f"yarı{h} {AD[d]} {f3(D[(D.yari == h) & (D.don == d)].net)}" for h in (0, 1) for d in range(3))
    yaz(f"**Seçilen k {k} · H {H} · {hc}**"); yaz("- rastgele coin-saat (aynı kural): " + " · ".join(pl)); yaz(f"**→ {'✅ GEÇTİ' if ok else '❌ kaldı'}**\n")
    if ok: GEC.append((ad, k, H, D))
    print(f"[{time.time() - T0:.0f} sn] {ad}", flush=True)
yaz(f"## Sonuç: {'✅ geçen: ' + ', '.join(g[0] for g in GEC) if GEC else '❌ hiçbir olay tüm şartları geçmedi'}")
hf = (idx.max() - pd.Timestamp("2025-01-01", tz="UTC")).days / 7
for ad, k, H, D in GEC:
    yaz(f"\n### Risk tablosu — {ad} · k {k} · H {H}"); yaz("| dönem | isabet · net | ort. kazanç | ort. kayıp | bir kaybı kaç kazanç siler | en kötü işlem | en kötü %5 ort. |"); yaz("|---|---|---|---|---|---|---|")
    for d in range(3):
        v = D[D.don == d].net; w, l = v[v > 0], v[v <= 0]
        yaz(f"| {AD[d]} | {f3(v)} | {100 * w.mean():+.2f}% | {100 * l.mean():+.2f}% | {abs(l.mean() / w.mean()):.1f} | {100 * v.min():.1f}% | {100 * v.nsmallest(max(1, len(v) // 20)).mean():.2f}% |")
    y2 = D[D.don > 0]; t2 = idx[y2.i.values]
    yaz(f"_2025+ haftada {len(y2) / hf:.1f} dolan işlem · farklı gün/hafta {pd.Series(t2.floor('D')).nunique() / hf:.1f} · ELİT/🌪️ ile aynı saatte %{100 * np.mean([t in EL for t in t2]):.0f}_")
    D.assign(t=idx[D.i.values], coin=[COL[j] for j in D.j]).to_csv(f"yeni80_{ad.split()[0]}.csv", index=False)
open("yeni80_sonuc.md", "w").write("\n".join(out) + "\n")
