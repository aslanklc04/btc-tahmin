# yeni3c.py — PROTOKOL_yeni3.md Ek 2: Y3 TERSİ (short) + stop/hedef ızgarası (kumarbazın iflası), keşif → doğrulama → yeni3b_sonuc.md
import glob, hashlib, itertools, time, numpy as np, pandas as pd
T0 = time.time(); out = []
def yaz(s=""): out.append(s); print(s, flush=True)
A = pd.concat([pd.read_parquet(f, columns=["t", "coin", "o", "h", "l", "c", "qv"]) for f in sorted(glob.glob("teknik3_mum_*.parquet"))], ignore_index=True)
A["t"] = pd.to_datetime(A.t, utc=True); A = A.drop_duplicates(["coin", "t"])
W = {k: A.pivot(index="t", columns="coin", values=k).sort_index().astype(float) for k in ("o", "h", "l", "c", "qv")}; del A
idx = pd.date_range(W["c"].index.min(), W["c"].index.max(), freq="1h"); W = {k: v.reindex(idx) for k, v in W.items()}
O, Hh, L, C, Q = (W[k] for k in ("o", "h", "l", "c", "qv")); COINS = [c for c in C.columns if c != "BTC"]
lr = np.log(C).diff(); sig = lr.rolling(720, min_periods=480).std(); sig1 = sig.shift(1)
ust = (C - L) / (Hh - L); qm = Q.rolling(168, min_periods=120).mean().shift(1); hmax = Hh.rolling(168, min_periods=120).max().shift(1)
M = ((Q >= 5 * qm) & (lr >= 3 * sig1) & (ust >= 0.75) & (C > hmax))[COINS]; RQ = (Q / qm)[COINS]
Ov, Hv, Lv, Cv, Sv = O.values, Hh.values, L.values, C.values, sig.values; CI = {c: j for j, c in enumerate(C.columns)}; n = len(idx)
def sonuc(j, i, k, m, H):  # SHORT (PROTOKOL_yeni3 Ek 2)
    if i + H >= n: return None
    pe = Ov[i + 1, j] * 0.999; s = Sv[i, j]
    if not (np.isfinite(pe) and np.isfinite(s)): return None
    d = s * np.sqrt(H); tp, sl = pe * (1 - k * d), pe * (1 + m * d); fn = 0.0001 * H / 8
    hh, ll = Hv[i + 1:i + H + 1, j], Lv[i + 1:i + H + 1, j]
    a = np.where(ll <= tp)[0]; b = np.where(hh >= sl)[0]; a0 = a[0] if len(a) else 99; b0 = b[0] if len(b) else 99
    if b0 <= a0 and b0 < 99: return (pe - sl * 1.001) / pe - 0.001 - fn, i + 1 + b0, 0
    if a0 < 99: return (pe - tp) / pe - 0.0007 - fn, i + 1 + a0, 1
    ce = Cv[i + H, j]
    return ((pe - ce * 1.001) / pe - 0.001 - fn, i + H, 0) if np.isfinite(ce) else None
yari = {c: int(hashlib.md5(c.encode()).hexdigest(), 16) % 2 for c in COINS}
don = lambda t: "A" if t.year <= 2024 else ("B" if t.year == 2025 else "C"); AD = {"A": "2022-06→24", "B": "2025", "C": "2026"}
i0 = idx.searchsorted(pd.Timestamp("2022-06-01", tz="UTC"))
EV = {i: sorted(((c, RQ.iat[i, COINS.index(c)]) for c in np.array(COINS)[M.values[i]]), key=lambda x: -x[1]) for i in np.where(M.values.any(axis=1))[0] if i >= i0}
def calistir(EV, k, m, H):
    mesgul, R = {}, []
    for i in sorted(EV):
        for c, _ in [x for x in EV[i] if mesgul.get(x[0], -1) < i][:3]:
            s_ = sonuc(CI[c], i, k, m, H)
            if s_ is None: continue
            R.append((idx[i], c, s_[0], s_[2])); mesgul[c] = s_[1]
    D = pd.DataFrame(R, columns=["t", "coin", "net", "tp"])
    if len(D): D["ok"] = D.net > 0; D["don"] = D.t.map(don); D["yari"] = D.coin.map(yari)
    return D
IZ = list(itertools.product((0.75, 1.0, 1.5), (1.0, 1.5, 2.0), (4, 12)))
hf = lambda y: f"{len(y)} · %{100 * y.ok.mean():.0f} · {100 * y.net.mean():+.2f}" if len(y) else "—"
def sec(EV):
    best, tab = None, []
    for k, m, H in IZ:
        D = calistir(EV, k, m, H); y = D[(D.yari == 0) & (D.don == "A")] if len(D) else D; tab.append((k, m, H, y, D))
        if len(y) >= 40 and (best is None or y.net.mean() > best[3].net.mean()): best = (k, m, H, y, D)
    return best, tab
def dogrula(D, k, m):
    ok_, hc = True, []
    for h, d in [(0, "B"), (0, "C"), (1, "A"), (1, "B"), (1, "C")]:
        y = D[(D.yari == h) & (D.don == d)]; ust_ = y.tp.mean() - m / (k + m) if len(y) else np.nan
        g = len(y) >= 20 and y.ok.mean() >= 0.70 and y.net.mean() >= 0.003 and ust_ > 0; ok_ &= bool(g)
        hc.append(f"yarı{h} {AD[d]} {hf(y)} · 🎯-önce %{100 * y.tp.mean():.0f} (teori %{100 * m / (k + m):.0f}) {'✔' if g else '✘'}")
    return ok_, hc
yaz("# 🔻 Y3 tersi: hacim kırılımından sonra SHORT + olasılık stop/hedef — PROTOKOL_yeni3.md Ek 2"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {len(EV)} olay saati · ızgara 18 · seçim yalnız keşif hücresinde (yarı 0 × 2022-06→24)_\n")
best, tab = sec(EV)
yaz("## Keşif hücresi — ızgaranın tamamı"); yaz("| k (🎯) | m (stop) | H | işlem · isabet · net | 🎯-önce / teori m/(k+m) |"); yaz("|---|---|---|---|---|")
for k, m, H, y, _ in tab: yaz(f"| {k} | {m} | {H} | {hf(y)} | %{100 * y.tp.mean():.0f} / %{100 * m / (k + m):.0f} |")
yaz("\n_Bilgi (seçimi değiştirmez) — ızgaranın doğrulama hücrelerinde (5 hücre birlikte) net:_ " + " · ".join(f"k{k_}/m{m_}/H{H_} {hf(D_[~((D_.yari == 0) & (D_.don == 'A'))])}" for k_, m_, H_, _, D_ in tab))
k, m, H, y, D = best; yaz(f"\n**Seçilen: k {k} · m {m} · H {H}** (keşif {hf(y)})\n")
ok_, hc = dogrula(D, k, m); yaz("## Doğrulama (5 hücre)"); [yaz(f"- {x}") for x in hc]
rng = np.random.default_rng(44); D["gun"] = D.t.dt.floor("D"); gn = D.groupby("gun").size(); PLi, PLn = {d: [] for d in "ABC"}, {d: [] for d in "ABC"}
for _ in range(20):
    P = []
    for g, kk in gn.items():
        g0 = idx.searchsorted(g)
        for _k in range(kk):
            for _t in range(20):
                c = COINS[rng.integers(len(COINS))]; s_ = sonuc(CI[c], g0 + rng.integers(24), k, m, H)
                if s_ is not None: P.append((g, s_[0])); break
    P = pd.DataFrame(P, columns=["gun", "net"]); P["don"] = P.gun.map(don)
    for d in "ABC": p = P[P.don == d]; PLi[d].append((p.net > 0).mean()); PLn[d].append(p.net.mean())
pl = []
for d in "ABC":
    yy = D[D.don == d]; g = len(yy) and yy.ok.mean() > max(PLi[d]) and yy.net.mean() > max(PLn[d]); ok_ &= bool(g)
    pl.append(f"{AD[d]} {hf(yy)} / rastgele en iyi %{100 * max(PLi[d]):.0f} · {100 * max(PLn[d]):+.2f} {'✔' if g else '✘'}")
yaz("- dönem / rastgele: " + " · ".join(pl))
y2 = D[D.t >= pd.Timestamp("2025-01-01", tz="UTC")]; w = (idx.max() - pd.Timestamp("2025-01-01", tz="UTC")).days / 7
yaz(f"- bilgi (2025+): haftada {len(y2) / w:.1f} · farklı gün {y2.gun.nunique() / w:.1f} · en kötü işlem {100 * D.net.min():.1f}% · tümü {hf(D)}")
yaz(f"\n**Sonuç → {'✅ GEÇTİ (canlı öncesi sağlamlık testleri ayrıca)' if ok_ else '❌ geçmedi'}**\n")
# plasebo seçimi: rastgele coin-saat olayları ile aynı süreç
say = 0; ns = len(EV); POOL = [i for i in range(i0, n - 13)]
for r in range(20):
    EVp = {}
    for i in rng.choice(POOL, size=ns, replace=False):
        cs = [c for c in rng.choice(COINS, size=3, replace=False)]; EVp[int(i)] = [(c, 1.0) for c in cs]
    bp, _ = sec(EVp)
    if bp and dogrula(bp[4], bp[0], bp[1])[0]: say += 1
    print(f"[{time.time() - T0:.0f} sn] plasebo {r}", flush=True)
yaz(f"_Plasebo seçimi (rastgele olaylar, aynı ızgara ve seçim ×20): doğrulamayı geçen {say}/20_")
open("yeni3c_sonuc.md", "w").write("\n".join(out) + "\n")
