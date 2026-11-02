# pompa2.py — PROTOKOL_pompa.md Ek 1: büyük hareket + YÖN modeli → pompa2_sonuc.md
import glob, time, numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
T0 = time.time(); out = []
def yaz(s=""): out.append(s); print(s, flush=True)
A = pd.concat([pd.read_parquet(f, columns=["t", "coin", "o", "h", "l", "c", "qv"]) for f in sorted(glob.glob("teknik3_mum_*.parquet"))], ignore_index=True)
A["t"] = pd.to_datetime(A.t, utc=True); A = A.drop_duplicates(["coin", "t"]).sort_values(["coin", "t"])
B = A[A.coin == "BTC"].set_index("t").c.astype(float); blr = np.log(B).diff()
BT = pd.DataFrame({"b_r4": np.log(B).diff(4), "b_r24": np.log(B).diff(24), "b_vor": blr.rolling(24).std() / blr.rolling(168).std()})
def rsi(c, n=14):
    d = c.diff(); u = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean(); w = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean(); return 100 - 100 / (1 + u / w)
P = []
for nm, d in A.groupby("coin"):
    d = d.set_index("t")[["o", "h", "l", "c", "qv"]].astype(float); d = d[~d.index.duplicated()]
    if len(d) < 3000: continue
    o, h, l, c, q = d.o, d.h, d.l, d.c, d.qv; lc = np.log(c); lr = lc.diff(); F = pd.DataFrame(index=d.index)
    for k in (1, 4, 12, 24, 72, 168): F[f"r{k}"] = lc.diff(k)
    F["v24"] = lr.rolling(24).std(); F["v168"] = lr.rolling(168).std(); F["vor"] = F.v24 / F.v168
    q24 = q.rolling(24).sum(); F["vz"] = (q24 - q24.rolling(720).mean().shift(24)) / q24.rolling(720).std().shift(24); F["v1"] = q / q.rolling(24).mean()
    F["dh24"] = c / h.rolling(24).max() - 1; F["dl24"] = c / l.rolling(24).min() - 1; F["dh168"] = c / h.rolling(168).max() - 1; F["dl168"] = c / l.rolling(168).min() - 1
    F["rsi"] = rsi(c); m20, s20 = c.rolling(20).mean(), c.rolling(20).std(); F["pb"] = (c - (m20 - 2 * s20)) / (4 * s20); F["bw"] = 4 * s20 / m20
    F["ustg"] = ((h - np.maximum(o, c)) / c).rolling(4).sum(); F["altg"] = ((np.minimum(o, c) - l) / c).rolling(4).sum()
    F = F.join(BT); F["rel24"] = F.r24 - F.b_r24; F["hod"] = F.index.hour; F["dow"] = F.index.dayofweek
    Pe = o.shift(-1) * 1.001; fmax = h.rolling(24).max().shift(-24); y = (fmax >= 1.10 * Pe).astype(float); y[fmax.isna() | Pe.isna()] = np.nan
    F["olay30"] = y.shift(24).rolling(720, min_periods=100).sum()
    cik = np.where(y == 1, 0.10 - 0.0005 - 0.0002, c.shift(-24) / Pe - 1 - 0.001) - 0.0003
    hv, lv, cv = h.values, l.values, c.values; n = len(d); pe = Pe.values; up = np.full(n, 99); dn = np.full(n, 99)
    for k in range(24, 0, -1):
        hh = np.full(n, np.nan); ll = np.full(n, np.nan); hh[:n - k] = hv[k:]; ll[:n - k] = lv[k:]
        up = np.where(hh >= 1.10 * pe, k, up); dn = np.where(ll <= 0.90 * pe, k, dn)
    yd = np.where((up == 99) & (dn == 99), np.nan, np.where(up < dn, 1.0, 0.0)); yd[np.isnan(y.values)] = np.nan
    c24 = np.full(n, np.nan); c24[:n - 24] = cv[24:]
    nt = np.where(up < dn, 0.10 - 0.0007, np.where(dn < 99, -0.10 * 1.0005 - 0.001, c24 / pe - 1 - 0.001)) - 0.0003   # 🎯 +%10 / stop −%10 / süre
    F["y"], F["net"], F["coin"], F["yd"], F["net2"] = y, cik, nm, yd, nt
    P.append(F.astype({k: "float32" for k in F.columns if k not in ("coin",)}))
X = pd.concat(P); X = X[X.y.notna()].reset_index().rename(columns={"index": "t"}); del P, A
FE = [c for c in X.columns if c not in ("t", "y", "net", "coin", "yd", "net2")]
print(f"[{time.time() - T0:.0f} sn] {len(X):,} coin-saat · {X.coin.nunique()} coin · olay oranı %{100 * X.y.mean():.2f}", flush=True)
CEY = pd.date_range("2024-01-01", "2026-10-01", freq="QS", tz="UTC"); rng = np.random.default_rng(10)
X["p"] = np.nan; X["pu"] = np.nan; X["esik"] = np.nan; tv = X.t.values
prm = dict(max_iter=300, learning_rate=0.05, max_leaf_nodes=63, min_samples_leaf=200, random_state=0)
for q in CEY:
    tr = tv < (q - pd.Timedelta(days=2)).to_datetime64(); te = (tv >= q.to_datetime64()) & (tv < (q + pd.offsets.QuarterBegin(1, startingMonth=1)).to_datetime64())
    if not te.any(): continue
    ytr = X.y.values[tr]; keep = (ytr == 1) | (rng.random(len(ytr)) < 0.10); w = np.where(ytr[keep] == 1, 1.0, 10.0); Ftr = X.loc[tr, FE].values
    m1 = HistGradientBoostingClassifier(**prm).fit(Ftr[keep], ytr[keep], sample_weight=w)
    ydt = X.yd.values[tr]; k2 = ~np.isnan(ydt); m2 = HistGradientBoostingClassifier(**prm).fit(Ftr[k2], ydt[k2])
    Fte = X.loc[te, FE].values; X.loc[te, "p"] = m1.predict_proba(Fte)[:, 1]; X.loc[te, "pu"] = m2.predict_proba(Fte)[:, 1]; X.loc[te, "esik"] = 3 * ytr.mean()
    print(f"[{time.time() - T0:.0f} sn] {q:%Y-%m} · yön eğitimi {k2.sum():,} (yukarı önce %{100 * np.nanmean(ydt):.0f})", flush=True)
T = X[X.p.notna()].copy(); T["gun"] = T.t.dt.floor("D"); T["saat"] = T.t.dt.hour; T["yil"] = T.t.dt.year
H = T[(T.p >= T.esik)]
def sec(g, kol):
    g = g.sort_values(kol, ascending=False); s, h_, c_ = [], set(), set()
    for r in g.itertuples():
        if r.saat in h_ or r.coin in c_: continue
        s.append(r.Index); h_.add(r.saat); c_.add(r.coin)
        if len(s) == 4: break
    return s
S = T.loc[[i for _, g in H[H.pu >= 0.5].groupby("gun") for i in sec(g, "pu")]]; ns = S.groupby("gun").size()
def rast():
    idx = []
    for gn, g in H.groupby("gun"):
        k = int(ns.get(gn, 0))
        if k: idx += sec(g.assign(rr=rng.random(len(g))), "rr")[:k]
    return T.loc[idx]
PL = [rast() for _ in range(20)]
yaz("# 🧭 Büyük hareket + YÖN — PROTOKOL_pompa.md Ek 1"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · aday = büyük hareket olasılığı ≥ 3× taban · seçim = yukarı olasılığı en yüksek ≤ 4/gün (farklı saat/coin, ≥ 0,5) · işlem 🎯 +%10 / stop −%10 / 24 s · vadeli ücret + fonlama_\n")
yaz("| yıl | aday havuzunda yukarı önce | seçilen · günde | **seçilenlerde yukarı önce (bariyere değenler)** | bariyere değme | işlem başı net | günlük ort. | rastgele (aynı havuz ×20) yukarı önce · net: ort / en iyi |"); yaz("|---|---|---|---|---|---|---|---|")
OK = True
for yl in (2024, 2025, 2026):
    h_, s_ = H[H.yil == yl], S[S.yil == yl]; gn = T[T.yil == yl].gun.nunique(); sd = s_.yd.dropna()
    pu_ = [p[p.yil == yl].yd.dropna().mean() for p in PL]; pn_ = [p[p.yil == yl].net2.mean() for p in PL]
    g_ = s_.groupby("gun").net2.sum().reindex(T[T.yil == yl].gun.unique(), fill_value=0)
    yaz(f"| {yl} | %{100 * h_.yd.dropna().mean():.0f} | {len(s_)} · {len(s_) / gn:.1f} | **%{100 * sd.mean():.0f}** ({len(sd)}) | %{100 * len(sd) / max(len(s_), 1):.0f} | {100 * s_.net2.mean():+.2f}% | {100 * g_.mean():+.2f}% | %{100 * np.mean(pu_):.0f} · {100 * np.mean(pn_):+.2f} / %{100 * max(pu_):.0f} · {100 * max(pn_):+.2f} |")
    OK &= (sd.mean() >= 0.60) and (s_.net2.mean() > 0) and (s_.net2.mean() > max(pn_))
yaz(f"\n**Yön bulundu şartı (3 yılda: yukarı önce ≥ %60, net > 0, rastgeleden iyi): {'✅ GEÇTİ' if OK else '❌ GEÇMEDİ'}**")
yaz("\n**Bilgi — tüm coin-saatlerde yön modelinin ayırt gücü (AUC, bariyere değenler):** " + " · ".join(f"{yl}: {__import__('sklearn.metrics', fromlist=['roc_auc_score']).roc_auc_score(T[(T.yil == yl) & T.yd.notna()].yd, T[(T.yil == yl) & T.yd.notna()].pu):.3f}" for yl in (2024, 2025, 2026)))
yaz(f"\n_süre {time.time() - T0:.0f} sn_"); open("pompa2_sonuc.md", "w").write("\n".join(out) + "\n")
