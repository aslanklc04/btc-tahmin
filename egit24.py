# egit24.py — AYLIK: 🧪 24 SAAT DENEME modelleri (ufuk24.py araştırmasıyla birebir aynı yöntem). Kullanım: python egit24.py ETHUSDT
# Coin'ler (durum/deneme24_liste.txt) yalnız 2020–23 sonucuna göre seçildi; 2024+ sonucu önceden sabit testi geçti (isabet %55, işlem başı net +%0,46, limit emir)
# ama 2026'da zayıf. Bu yüzden canlıda yalnız DENEME: gerçek para için değil, 4–6 hafta canlı takip edilir.
# Kayıt: durum/model24_{SYM}.pkl.gz = son ayın modeli + yürüyen testin son 2000 saatlik tahminleri (canlıda z-skoru ve eşikler için) + geçmiş istatistikler.
import os, sys, gzip, pickle, lightgbm as lgb
from sklearn.linear_model import LogisticRegression
from ortak import *
SYM = sys.argv[1]; H, YL, FEE, D1 = 24, [3, 5], 0.0002, 1; T0 = time.time()
PRESET = {"ETHUSDT": "2020-01-01", "BNBUSDT": "2020-01-01", "DOGEUSDT": "2021-01-01", "BTCUSDT": "2020-01-01"}
def log(*a): print(f"[{time.time()-T0:5.0f} sn] {SYM}:", *a, flush=True)
o = fetch_1h(pd.Timestamp("2017-08-17", tz="UTC").timestamp() * 1000, time.time() * 1000, sym=SYM)
l0 = o.index[0]; TEST = pd.Timestamp(PRESET[SYM], tz="UTC") if SYM in PRESET else max(pd.Timestamp("2020-01-01", tz="UTC"), (l0 + pd.Timedelta(days=365) + pd.offsets.MonthBegin(1)).normalize())
log(f"{len(o):,} saat · {l0:%Y-%m-%d} → {o.index[-1]:%Y-%m-%d %H:%M} · test {TEST:%Y-%m}+")
FA = features(o); FEATS = list(FA.columns)
D = FA.copy(); D["y"] = np.log(o.close.shift(-H) / o.close); D = D.iloc[720:]; DL = D.dropna(subset=["y"])
def train_month(ms):
    parts_ = []
    for yrs in YL:
        tr = DL[DL.index < ms - pd.Timedelta(hours=H)]; tr = tr[tr.index >= tr.index[-1] - pd.Timedelta(days=365 * yrs)]
        yb = (tr.y > 0).astype(int); k = int(len(tr) * .85)
        g = lgb.LGBMClassifier(n_estimators=600, learning_rate=0.03, num_leaves=15, min_child_samples=300, subsample=0.7, subsample_freq=1,
                               colsample_bytree=0.5, reg_lambda=10, verbose=-1).fit(tr[FEATS].iloc[:k - H], yb.iloc[:k - H],
                               eval_set=[(tr[FEATS].iloc[k:], yb.iloc[k:])], callbacks=[lgb.early_stopping(50, verbose=False)])
        z = ZF(tr[FEATS]); lo = LogisticRegression(C=0.01, max_iter=500).fit(z(tr[FEATS]), yb); parts_.append((g, z, lo))
    return HModel(parts_, FEATS)
months = pd.date_range(TEST, D.index[-1], freq="MS"); PG = pd.Series(np.nan, index=D.index); PL = PG.copy(); model = None
for i, ms in enumerate(months):
    me = months[i + 1] if i + 1 < len(months) else D.index[-1] + pd.Timedelta(hours=1); rows = D[(D.index >= ms) & (D.index < me)]
    if not len(rows): continue
    model = train_month(ms); pg, pl = model(rows); PG.loc[rows.index], PL.loc[rows.index] = pg, pl
PG, PL = PG.dropna(), PL.dropna(); log(f"yürüyen test bitti ({len(months)} ay)")
SF = signal_frame(PG, PL, FA.r24, False)
# ---- geçmiş istatistikler (araştırmayla aynı: ilk saat sayılır, 24 saat tekrar sayılmaz; giriş 1 saat sonra, limit komisyon) ----
ix = pd.date_range(o.index[0], o.index[-1], freq="1h", tz="UTC"); c = o.close.reindex(ix).ffill(limit=3).values; S_ = SF.reindex(ix)
mk = np.nan_to_num(((S_.S > 0) & (S_.C >= S_.T10)).values).astype(bool) & S_.T10.notna().values & (np.arange(len(ix)) + H + D1 < len(ix))
ev = events(mk, H); EV = pd.DataFrame({"t": ix[ev], "g": c[ev + H + D1] / c[ev + D1] - 1}).dropna(); EV["net"] = EV.g - 2 * FEE
def st(x): return dict(n=len(x), acc=100 * (x.g > 0).mean() if len(x) else float("nan"), net=100 * x.net.mean() if len(x) else float("nan"))
A24 = pd.Timestamp("2024-01-01", tz="UTC"); wk24 = max(1.0, (ix[-1] - A24).days / 7)
STATS = {"2020–23": st(EV[EV.t < A24]), "2024+": st(EV[EV.t >= A24]), "yil": {int(y): st(g) for y, g in EV.groupby(EV.t.dt.year)}, "haftada": len(EV[EV.t >= A24]) / wk24}
log("2024+: " + str({k: round(v, 2) for k, v in STATS["2024+"].items()}) + " · yıllar: " + " ".join(f"{y}: %{v['acc']:.0f}/{v['net']:+.2f}" for y, v in STATS["yil"].items()))
# ---- canlıyla aynı mı? son 2000 saatlik kuyruktan hesaplanan sinyal, tüm geçmişten hesaplananla karşılaştırılır ----
TP, TL = PG.iloc[-2000:], PL.iloc[-2000:]; S2 = signal_frame(TP, TL, FA.r24, False)
fark = float((S2.S - SF.S).iloc[-200:].abs().max()); fark_t = float((S2.T10 - SF.T10).iloc[-200:].abs().max())
log(f"kuyruk kontrolü: S farkı {fark:.2e} · eşik farkı {fark_t:.2e}"); assert fark < 1e-6 and fark_t < 1e-6, "kuyruk yetersiz"
sf = SF.iloc[-1]; log(f"son saat {SF.index[-1]:%Y-%m-%d %H:%M}: S {sf.S:+.2f} · C {sf.C:.2f} · T10 {sf.T10:.2f} → {'ÇOK GÜÇLÜ ↑' if sf.S > 0 and sf.C >= sf.T10 else '-'}")
os.makedirs("durum", exist_ok=True)
with gzip.open(f"durum/model24_{SYM}.pkl.gz", "wb") as f:
    pickle.dump(dict(sym=SYM, created=pd.Timestamp.now(tz="UTC"), H=H, model=model, month=months[-1], FEATS=FEATS, PG=TP, PL=TL, STATS=STATS, TEST=TEST), f)
log("kaydedildi")
