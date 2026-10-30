# model4_egit.py — PROTOKOL_dortyol YOL 4: kesitsel LightGBM, aylık yürüyen test (2024-01 → 2026-10), plasebo + rastgele coin kıyası
import glob, time, numpy as np, pandas as pd, lightgbm as lgb
T0 = time.time(); out = []; yaz = lambda s="": (out.append(s), print(s, flush=True))
D = pd.concat([pd.read_parquet(f) for f in sorted(glob.glob("parca/**/model4_p*.parquet", recursive=True))], ignore_index=True)
D["t"] = pd.to_datetime(D.t, utc=True); D = D.sort_values(["t", "coin"]).reset_index(drop=True)
FP, FL, SLIP = 0.0005, 0.0002, 0.001
D["el"] = (D.liq >= 2e6) & D.sd.notna() & (D.sd > 0)
for c in ("r4", "r24", "hc"): D[f"k_{c}"] = D.groupby("t")[c].rank(pct=True).astype("float32")
hr = D.t.dt.hour.values; D["hs"], D["hcz"] = np.sin(2 * np.pi * hr / 24).astype("float32"), np.cos(2 * np.pi * hr / 24).astype("float32")
y = np.log(D.c4 / D.o1) / (D.sd * 2); D["y"] = (y - y.groupby(D.t).transform("mean")).astype("float32")
Pe = D.o1 * (1 + SLIP); tp = Pe * (1 + 0.75 * D.sd * 2)
hit = np.zeros(len(D), bool)
for j in range(1, 5): hit |= (D[f"h{j}"] >= tp).values
fon = 0.0001 * 4 / 8
D["net_tp"] = np.where(hit, tp / Pe - 1 - FP - FL - fon, D.c4 / Pe - 1 - 2 * FP - fon).astype("float32")
D["net_t"] = (D.c4 / Pe - 1 - 2 * FP - fon).astype("float32")
OZ = ["r1", "r4", "r24", "r72", "r168", "vo", "hc", "tepe", "dip", "fr", "fz", "b1", "b4", "b24", "rel24", "k_r4", "k_r24", "k_hc", "hs", "hcz"]
yaz(f"# 🧠 YOL 4 — kesitsel sıralama modeli · PROTOKOL_dortyol.md\nsatır {len(D):,} · coin {D.coin.nunique()} · {D.t.min():%Y-%m} → {D.t.max():%Y-%m-%d} · {time.time() - T0:.0f} sn\n")
P = dict(objective="regression", learning_rate=0.05, num_leaves=31, min_data_in_leaf=500, bagging_fraction=0.8, bagging_freq=1, feature_fraction=0.8, verbose=-1, seed=7)
AYLAR = pd.date_range("2024-01-01", "2026-10-01", freq="MS", tz="UTC")
rng = np.random.default_rng(7)
def yuru(plasebo=False):
    SEC = []
    for m in AYLAR:
        a = m - pd.DateOffset(months=18); b = m - pd.Timedelta(hours=5)
        tr = D[(D.t >= a) & (D.t < b) & D.el].dropna(subset=["y"])
        yt = tr.y.values.copy()
        if plasebo: yt = tr.groupby("t").y.transform(lambda s: s.sample(frac=1, random_state=1).values).values
        mod = lgb.train(P, lgb.Dataset(tr[OZ].values, label=yt), num_boost_round=300)
        thr = np.percentile(mod.predict(tr[OZ].values), 90)
        te = D[(D.t >= m) & (D.t < m + pd.DateOffset(months=1)) & D.el].copy()
        if not len(te): continue
        te["p"] = mod.predict(te[OZ].values); best = te.sort_values(["t", "p"], ascending=[True, False]).groupby("t").head(1)
        son = {}
        for r in best.itertuples():
            if r.p < thr or (r.coin in son and r.t - son[r.coin] < pd.Timedelta(hours=4)): continue
            son[r.coin] = r.t
            el = te[te.t == r.t]; rr = el.iloc[rng.integers(len(el))]
            SEC.append((r.t, r.coin, r.net_tp, r.net_t, rr.net_tp, rr.net_t))
        print(f"{'plasebo' if plasebo else 'model'} {m:%Y-%m}: eğitim {len(tr):,} · seçilen toplam {len(SEC)} · {time.time() - T0:.0f} sn", flush=True)
    return pd.DataFrame(SEC, columns=["t", "coin", "tp", "zaman", "r_tp", "r_zaman"])
G, PL = yuru(False), yuru(True)
YIL = [("2024", "2024-01-01", "2025-01-01"), ("2025", "2025-01-01", "2026-01-01"), ("2026", "2026-01-01", "2027-01-01")]
def satir(x, c):
    v = x[c]; return f"{len(v)} · %{100 * (v > 0).mean():.1f} · {100 * v.mean():+.2f}" if len(v) else "0"
yaz("_hücre: işlem · isabet · işlem başı net % (🎯 0,75σ ya da 4 s sonu; giriş piyasa + %0,1 kayma)_\n")
yaz("| | " + " | ".join(y_ for y_, _, _ in YIL) + " |"); yaz("|---|" + "---|" * len(YIL))
ok_m, ok_p = True, True
for ad, X_, c in (("MODEL 🎯", G, "tp"), ("model 4 s sonu", G, "zaman"), ("rastgele coin (aynı saatler) 🎯", G, "r_tp"), ("PLASEBO 🎯", PL, "tp")):
    hs = []
    for y_, a, b in YIL:
        x = X_[(X_.t >= pd.Timestamp(a, tz="UTC")) & (X_.t < pd.Timestamp(b, tz="UTC"))]; hs.append(satir(x, c))
        if ad == "MODEL 🎯":
            g = len(x) and x.tp.mean() >= 0.004 and (x.tp > 0).mean() >= 0.60 and x.tp.mean() - x.r_tp.mean() >= 0.003
            ok_m = ok_m and bool(g)
        if ad == "PLASEBO 🎯":
            r = X_[(X_.t >= pd.Timestamp(a, tz="UTC")) & (X_.t < pd.Timestamp(b, tz="UTC"))]
            ok_p = ok_p and bool(len(r) and r.tp.mean() >= 0.004 and (r.tp > 0).mean() >= 0.60)
    yaz(f"| {ad} | " + " | ".join(hs) + " |")
gun = max((G.t.max() - G.t.min()).days, 1); yaz(f"\nmodel sıklığı: günde {len(G) / gun:.1f} işlem · en sık coin'ler: {', '.join(G.coin.value_counts().head(8).index)}")
yaz(f"\n**Karar YOL 4: {'✅ GEÇTİ' if ok_m and not ok_p else '❌ geçmedi'}** (model şartı: {'✅' if ok_m else '❌'} · plasebo şartı sağlamıyor mu: {'✅' if not ok_p else '❌'})")
open("model4_sonuc.md", "w").write("\n".join(out) + "\n"); G.to_csv("model4_secim.csv.gz", index=False, compression="gzip")
