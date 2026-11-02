# pompa.py — PROTOKOL_pompa.md: 24 saat içinde +%10 yükselecek coin'i önceden bulmak → pompa_sonuc.md
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
    F["y"], F["net"], F["coin"] = y, cik, nm
    P.append(F.astype({k: "float32" for k in F.columns if k not in ("coin",)}))
X = pd.concat(P); X = X[X.y.notna()].reset_index().rename(columns={"index": "t"}); del P, A
FE = [c for c in X.columns if c not in ("t", "y", "net", "coin")]
print(f"[{time.time() - T0:.0f} sn] {len(X):,} coin-saat · {X.coin.nunique()} coin · olay oranı %{100 * X.y.mean():.2f}", flush=True)
CEY = pd.date_range("2024-01-01", "2026-10-01", freq="QS", tz="UTC"); rng = np.random.default_rng(10)
X["p"] = np.nan; X["esik"] = np.nan; tv = X.t.values
for q in CEY:
    tr = tv < (q - pd.Timedelta(days=2)).to_datetime64(); te = (tv >= q.to_datetime64()) & (tv < (q + pd.offsets.QuarterBegin(1, startingMonth=1)).to_datetime64())
    if not te.any(): continue
    ytr = X.y.values[tr]; keep = (ytr == 1) | (rng.random(len(ytr)) < 0.10); w = np.where(ytr[keep] == 1, 1.0, 10.0)
    md = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=63, min_samples_leaf=200, random_state=0).fit(X.loc[tr, FE].values[keep], ytr[keep], sample_weight=w)
    X.loc[te, "p"] = md.predict_proba(X.loc[te, FE].values)[:, 1]; X.loc[te, "esik"] = 3 * ytr.mean()
    print(f"[{time.time() - T0:.0f} sn] {q:%Y-%m} eğitim {tr.sum():,} · taban %{100 * ytr.mean():.2f}", flush=True)
T = X[X.p.notna()].copy(); T["gun"] = T.t.dt.floor("D"); T["saat"] = T.t.dt.hour; T["yil"] = T.t.dt.year
def sec_gun(g, kol="p", esik=True):
    g = g.sort_values(kol, ascending=False);
    if esik: g = g[g.p >= g.esik]
    s, h_, c_ = [], set(), set()
    for r in g.itertuples():
        if r.saat in h_ or r.coin in c_: continue
        s.append(r.Index); h_.add(r.saat); c_.add(r.coin)
        if len(s) == 4: break
    return s
SEC = [i for _, g in T.groupby("gun") for i in sec_gun(g)]; S = T.loc[SEC]
nsec = S.groupby("gun").size()
def rastgele(T):
    idx = []
    for gn, g in T.groupby("gun"):
        k = int(nsec.get(gn, 0))
        if k: g = g.assign(rr=rng.random(len(g))); idx += sec_gun(g, "rr", False)[:k]
    return T.loc[idx]
PL = [rastgele(T) for _ in range(20)]
yaz("# 🚀 24 saatte +%10 yükselecek coin — PROTOKOL_pompa.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {X.coin.nunique()} coin · çeyreklik yürüyen test (eğitim yalnız geçmiş) · giriş sonraki saat açılışı +%0,1 · 🎯 +%10 limit, değmezse 24 s sonra çıkış · vadeli ücret + fonlama · stop yok_\n")
yaz("| yıl | taban olay oranı (tüm coin-saat) | seçilen sinyal · günde | **isabet (+%10'a değdi)** | işlem başı net | günlük ort. toplam | en kötü işlem | rastgele seçim (20 tekrar) isabet · net: ort. / en iyi |"); yaz("|---|---|---|---|---|---|---|---|")
BUL = True; HED = True
for yl in (2024, 2025, 2026):
    t_, s_ = T[T.yil == yl], S[S.yil == yl]; gn = t_.gun.nunique()
    pi = [p[p.yil == yl].y.mean() for p in PL]; pn = [p[p.yil == yl].net.mean() for p in PL]
    g_ = s_.groupby("gun").net.sum().reindex(t_.gun.unique(), fill_value=0)
    yaz(f"| {yl} | %{100 * t_.y.mean():.2f} | {len(s_)} · {len(s_) / gn:.1f} | **%{100 * s_.y.mean():.1f}** | {100 * s_.net.mean():+.2f}% | {100 * g_.mean():+.2f}% | {100 * s_.net.min():.1f}% | %{100 * np.mean(pi):.1f} · {100 * np.mean(pn):+.2f} / %{100 * max(pi):.1f} · {100 * max(pn):+.2f} |")
    BUL &= (s_.y.mean() >= 3 * t_.y.mean()) and (s_.y.mean() > max(pi)) and (s_.net.mean() > 0) and (len(s_) / gn >= 2); HED &= s_.y.mean() >= 0.5
yaz(f"\n**Bulundu şartı (3 yılda: isabet ≥ 3× taban, rastgeleden iyi, net > 0, günde ≥ 2): {'✅ GEÇTİ' if BUL else '❌ GEÇMEDİ'} · kullanıcı hedefi (isabet ≥ %50): {'✅' if HED else '✘'}**")
# bilgi: −%10 stoplu sürüm (saatlik sıra; aynı saatte ikisi → stop)
A2 = pd.concat([pd.read_parquet(f, columns=["t", "coin", "o", "h", "l", "c"]) for f in sorted(glob.glob("teknik3_mum_*.parquet"))]); A2["t"] = pd.to_datetime(A2.t, utc=True)
A2 = A2.drop_duplicates(["coin", "t"]).set_index(["coin", "t"]).sort_index(); st = []
for r in S.itertuples():
    try: w = A2.loc[r.coin].loc[r.t:].iloc[1:25]
    except KeyError: st.append(np.nan); continue
    Pe = w.o.iloc[0] * 1.001; up = np.where(w.h.values >= 1.1 * Pe)[0]; dn = np.where(w.l.values <= 0.9 * Pe)[0]
    if len(dn) and (not len(up) or dn[0] <= up[0]): st.append(-0.10 * 1.0005 - 0.001 - 0.0003)
    elif len(up): st.append(0.10 - 0.0007 - 0.0003)
    else: st.append(w.c.iloc[-1] / Pe - 1 - 0.001 - 0.0003)
S["net_stop"] = st
yaz("\n**Bilgi — −%10 stoplu:** " + " · ".join(f"{yl}: {100 * S[S.yil == yl].net_stop.mean():+.2f}% (stop oranı %{100 * (S[S.yil == yl].net_stop < -0.09).mean():.0f})" for yl in (2024, 2025, 2026)))
yaz("\n**Seçilenlerin özellik ortalaması (bilgi):** " + ", ".join(f"{k} {S[k].mean():.3f}" for k in ("r24", "r168", "vz", "vor", "dh168", "olay30")))
yaz(f"\n_süre {time.time() - T0:.0f} sn_"); open("pompa_sonuc.md", "w").write("\n".join(out) + "\n")
S[["t", "coin", "p", "y", "net", "net_stop"]].to_csv("pompa_secilen.csv", index=False)
