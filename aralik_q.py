# aralik_q.py — PROTOKOL_aralik.md: 4 saatlik fiyat aralığı modelinin (q10/q50/q90 + QC) çeyreklik YÜRÜYEN yeniden eğitimi. Kullanım: python aralik_q.py PARÇA TOPLAM
import sys, time, numpy as np, pandas as pd, lightgbm as lgb
sys.path.insert(0, "canli"); from ortak import fetch_1h, features
I, N = int(sys.argv[1]), int(sys.argv[2]); T0 = time.time(); H = 4
V = pd.read_csv("veri_seti.csv.gz"); V["t"] = pd.to_datetime(V.t, utc=True)
S = V[(V.H == 4) & (V.tur.isin(["🤝", "🌐🤝", "G"]))][["t", "nm", "sinif"]]
COINS = sorted(S.nm.unique())[I::N]; OUT = []
for c in COINS:
    try:
        o = fetch_1h(pd.Timestamp("2018-06-01", tz="UTC").timestamp() * 1000, time.time() * 1000, sym=f"{c}USDT")
        FA = features(o); FE = list(FA.columns); D = FA.copy(); D["y"] = np.log(o.close.shift(-H) / o.close); D = D.iloc[720:]; DL = D.dropna(subset=["y"])
        s = S[S.nm == c]
        for qs in pd.date_range(pd.Timestamp("2022-04-01", tz="UTC"), pd.Timestamp.now(tz="UTC"), freq="QS"):
            qe = qs + pd.offsets.QuarterBegin(1); ss = s[(s.t >= qs) & (s.t < qe)]
            if ss.empty: continue
            cut = qs - pd.Timedelta(days=30); trq = DL[(DL.index < cut - pd.Timedelta(hours=H)) & (DL.index >= qs - pd.Timedelta(days=365 * 3))]
            cal = DL[(DL.index >= cut) & (DL.index < qs - pd.Timedelta(hours=H))]
            if len(trq) < 24 * 200 or len(cal) < 24 * 20: continue
            QM = {q: lgb.LGBMRegressor(objective="quantile", alpha=q, n_estimators=400, learning_rate=0.03, num_leaves=15, min_child_samples=300,
                                       subsample=0.7, subsample_freq=1, colsample_bytree=0.5, verbose=-1).fit(trq[FE], trq.y) for q in (0.1, 0.5, 0.9)}
            qc = np.sort(np.column_stack([QM[q].predict(cal[FE]) for q in (0.1, 0.5, 0.9)]), axis=1)
            QC = float(np.quantile(np.maximum(qc[:, 0] - cal.y.values, cal.y.values - qc[:, 2]), 0.8 * (1 + 1 / len(cal))))
            tt = pd.DatetimeIndex(ss.t).intersection(FA.index)
            if len(tt) == 0: continue
            pr = np.sort(np.column_stack([QM[q].predict(FA.loc[tt, FE]) for q in (0.1, 0.5, 0.9)]), axis=1)
            OUT.append(pd.DataFrame({"t": tt, "nm": c, "q10": pr[:, 0], "q50": pr[:, 1], "q90": pr[:, 2], "QC": QC}))
        print(f"{c} tamam · {time.time() - T0:.0f} sn", flush=True)
    except Exception as e: print(f"{c} HATA {type(e).__name__}: {str(e)[:150]}", flush=True)
(pd.concat(OUT) if OUT else pd.DataFrame(columns=["t", "nm", "q10", "q50", "q90", "QC"])).to_csv(f"aralik_q_{I}.csv", index=False)
print("bitti", len(OUT), time.time() - T0)
