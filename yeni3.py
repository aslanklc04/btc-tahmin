# yeni3.py — PROTOKOL_yeni3.md: Y1 gecikmeli takip · Y2 göreli güç · Y3 hacim kırılımı → yeni3_sonuc.md
import glob, hashlib, time, numpy as np, pandas as pd
T0 = time.time(); out = []
def yaz(s=""): out.append(s); print(s, flush=True)
A = pd.concat([pd.read_parquet(f, columns=["t", "coin", "o", "h", "l", "c", "qv"]) for f in sorted(glob.glob("teknik3_mum_*.parquet"))], ignore_index=True)
A["t"] = pd.to_datetime(A.t, utc=True); A = A.drop_duplicates(["coin", "t"])
W = {k: A.pivot(index="t", columns="coin", values=k).sort_index().astype(float) for k in ("o", "h", "l", "c", "qv")}; del A
idx = W["c"].index; idx_full = pd.date_range(idx.min(), idx.max(), freq="1h"); W = {k: v.reindex(idx_full) for k, v in W.items()}; idx = idx_full
O, Hh, L, C, Q = W["o"], W["h"], W["l"], W["c"], W["qv"]; COINS = [c for c in C.columns if c != "BTC"]
lr = np.log(C).diff(); sig = lr.rolling(720, min_periods=480).std(); sig1 = sig.shift(1)
rb = lr["BTC"]; sb = rb.rolling(720, min_periods=480).std().shift(1)
beta = lr[COINS].rolling(720, min_periods=480).cov(rb).div(rb.rolling(720, min_periods=480).var(), axis=0).shift(1)
print(f"[{time.time() - T0:.0f} sn] veri {C.shape}", flush=True)
UC_HIT, UC_END = 0.0005 + 0.0002, 0.0005 + 0.0005
def sonuc(coin, i, H):
    """i: sinyal satırı (t kapanışı) → (net, çıkış satırı) ya da None"""
    j = C.columns.get_loc(coin); n = len(idx)
    if i + H >= n: return None
    pe = O.iat[i + 1, j] * 1.001; s = sig.iat[i, j]
    if not (np.isfinite(pe) and np.isfinite(s)): return None
    tp = pe * (1 + 0.75 * s * np.sqrt(H)); hh = Hh.iloc[i + 1:i + H + 1, j].values; fn = 0.0001 * H / 8
    w = np.where(hh >= tp)[0]
    if len(w): return tp / pe - 1 - UC_HIT - fn, i + 1 + w[0]
    ce = C.iat[i + H, j]
    if not np.isfinite(ce): return None
    return ce / pe - 1 - UC_END - fn, i + H
B4 = np.log(C["BTC"]).diff(4); R4 = np.log(C[COINS]).diff(4)
ust = (C - L) / (Hh - L); qm = Q.rolling(168, min_periods=120).mean().shift(1); hmax = Hh.rolling(168, min_periods=120).max().shift(1)
def adaylar(ad):
    """her saat için [(coin, sıra puanı)] (yüksek puan önce)"""
    if ad == "Y1":
        ev = (rb >= 3 * sb) & (rb >= 0.01); E = {}
        for i in np.where(ev.values)[0]:
            b = beta.iloc[i]; ra = lr[COINS].iloc[i]; m = (b >= 0.5) & (ra <= 0.5 * b * rb.iat[i]) & ra.notna()
            if m.any(): E[i] = list((-(ra[m] / (b[m] * rb.iat[i]))).items())
        return E, 4
    if ad == "Y2":
        ev = B4 <= np.log(1 - 0.025); E = {}
        for i in np.where(ev.values)[0]:
            ra = R4.iloc[i]; m = (ra >= 0) & ra.notna()
            if m.any(): E[i] = list((ra[m] - B4.iat[i]).items())
        return E, 12
    m = (Q >= 5 * qm) & (lr >= 3 * sig1) & (ust >= 0.75) & (C > hmax); m = m[COINS]; E = {}
    r = (Q[COINS] / qm[COINS])
    for i in np.where(m.values.any(axis=1))[0]:
        mm = m.iloc[i]; E[i] = list(r.iloc[i][mm].items())
    return E, 4
yari = lambda s: int(hashlib.md5(s.encode()).hexdigest(), 16) % 2
don = lambda t: "A" if t.year <= 2024 else ("B" if t.year == 2025 else "C"); AD = {"A": "2022-06→24", "B": "2025", "C": "2026"}
V = pd.read_csv("veri_seti.csv.gz", usecols=["t", "nm", "sinif", "tur", "rz", "fon", "b_vr"]); V["t"] = pd.to_datetime(V.t, utc=True); V = V[V.sinif.str.startswith("✅")]
ANA = set(V.t); ELI = set(V.t[(V.rz <= -2) | (V.fon >= 2) | (V.tur == "🔀")]); OYN = set(V.t[(V.tur == "🌐🧪") & (V.b_vr >= 1.25)])
rng = np.random.default_rng(33); BAS = pd.Timestamp("2022-06-01", tz="UTC"); i0 = idx.searchsorted(BAS)
yaz("# 🔭 Üç yeni fikir — PROTOKOL_yeni3.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {len(COINS) + 1} coin · 2022-06 → {idx.max():%d.%m.%Y} · giriş sonraki saat açılışı +%0,1 · 🎯 0,75·σ720·√H · vadeli ücret · hücre: işlem · isabet · net %_\n")
AD_Y = {"Y1": "Y1 gecikmeli takip (BTC sıçradı, coin geride kaldı) · H 4", "Y2": "Y2 göreli güç (BTC 4 s ≤ −%2,5, coin düşmedi) · H 12", "Y3": "Y3 hacim kırılımı (5× hacim, 3σ mum, 168 s zirve kırıldı) · H 4"}
for ad in ("Y1", "Y2", "Y3"):
    E, H = adaylar(ad); mesgul = {}; R = []
    for i in sorted(E):
        if i < i0: continue
        sec = [(c_, p) for c_, p in sorted(E[i], key=lambda x: -x[1]) if mesgul.get(c_, -1) < i][:3]
        for c_, _ in sec:
            s_ = sonuc(c_, i, H)
            if s_ is None: continue
            R.append((idx[i], c_, s_[0])); mesgul[c_] = s_[1]
    D = pd.DataFrame(R, columns=["t", "coin", "net"])
    yaz(f"## {AD_Y[ad]}")
    if not len(D): yaz("sinyal yok\n"); continue
    D["ok"] = D.net > 0; D["don"] = D.t.map(don); D["yari"] = D.coin.map(yari)
    hc, bul = [], True
    for h in (0, 1):
        for d in "ABC":
            y = D[(D.yari == h) & (D.don == d)]; hc.append(f"{len(y)} · %{100 * y.ok.mean():.0f} · {100 * y.net.mean():+.2f}" if len(y) else "—")
            bul &= len(y) >= 20 and y.ok.mean() >= 0.70 and y.net.mean() >= 0.003
    # plasebo: aynı gün aynı sayıda rastgele coin-saat
    D["gun"] = D.t.dt.floor("D"); PLi, PLn = {d: [] for d in "ABC"}, {d: [] for d in "ABC"}
    gunler = D.groupby("gun").size()
    for _ in range(20):
        P = []
        for g, k in gunler.items():
            g0 = idx.searchsorted(g)
            for _k in range(k):
                for _try in range(20):
                    c_ = COINS[rng.integers(len(COINS))]; i = g0 + rng.integers(24); s_ = sonuc(c_, i, H) if i + H < len(idx) else None
                    if s_ is not None: P.append((g, s_[0])); break
        P = pd.DataFrame(P, columns=["gun", "net"]); P["don"] = P.gun.map(don)
        for d in "ABC": p = P[P.don == d]; PLi[d].append((p.net > 0).mean()); PLn[d].append(p.net.mean())
    pl = []
    for d in "ABC":
        y = D[D.don == d]; ok_ = len(y) and y.ok.mean() > max(PLi[d]) and y.net.mean() > max(PLn[d]); bul &= bool(ok_)
        pl.append(f"{AD[d]} {len(y)} · %{100 * y.ok.mean():.0f} · {100 * y.net.mean():+.2f} / rastgele en iyi %{100 * max(PLi[d]):.0f} · {100 * max(PLn[d]):+.2f} {'✔' if ok_ else '✘'}")
    yaz("| yarı0 22–24 | yarı0 2025 | yarı0 2026 | yarı1 22–24 | yarı1 2025 | yarı1 2026 |"); yaz("|---|---|---|---|---|---|"); yaz("| " + " | ".join(hc) + " |")
    yaz("- dönem / rastgele: " + " · ".join(pl))
    y2 = D[D.t >= pd.Timestamp("2025-01-01", tz="UTC")]; hf = (idx.max() - pd.Timestamp("2025-01-01", tz="UTC")).days / 7
    yaz(f"- bilgi (2025+): haftada {len(y2) / hf:.1f} sinyal · farklı gün {y2.gun.nunique() / hf:.1f} · farklı saat {y2.t.nunique() / hf:.1f} · ✅ ana saatiyle aynı %{100 * y2.t.isin(ANA).mean():.0f} · ELİT %{100 * y2.t.isin(ELI).mean():.0f} · 🌪️ %{100 * y2.t.isin(OYN).mean():.0f} · en kötü {100 * D.net.min():.1f}% · tümü {len(D)} · %{100 * D.ok.mean():.0f} · {100 * D.net.mean():+.2f}")
    yaz(f"**{ad} → {'✅ BULUNDU (sağlamlık testleri sonraki adım)' if bul else '❌ bulunamadı'}**\n")
    D.to_csv(f"yeni3_{ad}.csv", index=False)
    print(f"[{time.time() - T0:.0f} sn] {ad} bitti", flush=True)
open("yeni3_sonuc.md", "w").write("\n".join(out) + "\n")
