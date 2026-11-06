# pompaonce.py — PROTOKOL_pompaonce.md: +%50 yükselişlerden önce ne oluyor → pompaonce_sonuc.md
import json, re, numpy as np, pandas as pd
from scipy.stats import spearmanr
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
K = pd.read_parquet("yeniliste_mum.parquet"); F = pd.read_parquet("yeniliste_fon.parquet")
K["t"] = pd.to_datetime(K.t, utc=True).dt.floor("D"); K = K.drop_duplicates(["s", "t"])
VB = {x["s"]: x for x in json.load(open("vadeli_bilgi.json"))}
HARIC = re.compile(r"^(USDC|FDUSD|TUSD|BUSD|USDP|DAI|BTCDOM|DEFI|FOOTBALL|BLUEBIRD)USDT$")
K = K[[s.endswith("USDT") and not HARIC.match(s) and ((s not in VB) or (VB[s]["ut"] == "COIN" and VB[s]["ct"] == "PERPETUAL")) for s in K.s]]
O, Hh, L, C, V = (K.pivot(index="t", columns="s", values=k) for k in ("o", "h", "l", "c", "v"))
F["t"] = pd.to_datetime(F.t, utc=True); FP = F.pivot_table(index=F.t.dt.floor("D"), columns="s", values="fr", aggfunc="sum").reindex(index=O.index, columns=O.columns)
ilk = K.groupby("s").t.min(); lc = np.log(C); lr = lc.diff()
o1, h1, l1, c1 = O.shift(-1), Hh.shift(-1), L.shift(-1), C.shift(-1)
Y = (h1 >= 1.5 * o1); Yp = Y & (c1 >= 1.3 * o1); Dd = (l1 <= 0.7 * o1) & ~Y; gecerli = o1.notna() & h1.notna() & lr.rolling(30, min_periods=10).std().notna()
yesil = (C > O).astype(int); seri = yesil.groupby((yesil != yesil.shift()).cumsum(), axis=0).cumcount() if False else None
ard = yesil.copy() * 0
for c in yesil.columns:
    g = yesil[c]; ard[c] = g.groupby((g != g.shift()).cumsum()).cumcount().add(1).where(g == 1, 0)
btc = lc["BTCUSDT"]; nY = Y.where(gecerli).sum(axis=1)
FE = {"fonlama t (%)": 100 * FP, "fonlama 3 g (%)": 100 * FP.rolling(3, min_periods=1).sum(), "getiri t (%)": 100 * (C / O - 1), "getiri t−1 (%)": 100 * (C / O - 1).shift(1),
      "getiri t−2 (%)": 100 * (C / O - 1).shift(2), "getiri 7 g (%)": 100 * (C / C.shift(7) - 1), "art arda yeşil gün": ard,
      "hacim oranı t": V / V.rolling(30, min_periods=10).mean().shift(1), "hacim oranı t−1": (V / V.rolling(30, min_periods=10).mean().shift(1)).shift(1),
      "yaş (gün)": pd.DataFrame((O.index.tz_convert(None).values[:, None] - ilk.reindex(O.columns).dt.tz_convert(None).values[None, :]) / np.timedelta64(1, "D"), index=O.index, columns=O.columns),
      "30 g dipten (%)": 100 * (C / L.rolling(30, min_periods=5).min() - 1), "30 g zirveye (%)": 100 * (C / Hh.rolling(30, min_periods=5).max() - 1),
      "30 g oynaklık (%)": 100 * lr.rolling(30, min_periods=10).std(),
      "BTC 1 g (%)": pd.DataFrame(np.repeat(100 * btc.diff().values[:, None], C.shape[1], 1), index=O.index, columns=O.columns),
      "BTC 7 g (%)": pd.DataFrame(np.repeat(100 * btc.diff(7).values[:, None], C.shape[1], 1), index=O.index, columns=O.columns),
      "aynı gün Y sayısı (bilgi)": pd.DataFrame(np.repeat(nY.shift(-1).values[:, None], C.shape[1], 1), index=O.index, columns=O.columns)}
st = lambda D: D.where(gecerli).stack()
X = pd.DataFrame({k: st(v) for k, v in FE.items()}); X["Y"] = st(Y.astype(float)); X["Yp"] = st(Yp.astype(float)); X["D"] = st(Dd.astype(float))
X["gd"] = st(c1 / C - 1); X["boy"] = st(h1 / o1 - 1); X["r1"], X["r3"], X["r7"] = st(C.shift(-2) / c1 - 1), st(C.shift(-4) / c1 - 1), st(C.shift(-8) / c1 - 1)
X = X.reset_index().rename(columns={"level_0": "t", "level_1": "s"}); X["don"] = np.select([X.t.dt.year <= 2023, X.t.dt.year == 2024, X.t.dt.year == 2025], ["2021–23", "2024", "2025"], "2026")
X["dow"] = X.t.dt.dayofweek; DON = ["2021–23", "2024", "2025", "2026"]; FC = list(FE)
yaz("# 🔬 +%50 yükselişlerden önce ne oluyor? — PROTOKOL_pompaonce.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {X.s.nunique()} coin · {len(X):,} coin-gün · Y = ertesi gün en yüksek ≥ açılış × 1,5 · D = en düşük ≤ × 0,7 · K = diğerleri_\n")
yaz("| dönem | Y (yükseliş) | Y+ (kapanışta ≥ +%30 tutunan) | D (çöküş) | K |"); yaz("|---|---|---|---|---|")
for d in DON:
    x = X[X.don == d]; yaz(f"| {d} | {int(x.Y.sum())} | {int(x.Yp.sum())} | {int(x.D.sum())} | {int((x.Y + x.D == 0).sum()):,} |")
yaz("\n## 1. Ortak durumlar — medyanlar (Y / D / K), dönem dönem")
yaz("| özellik | " + " | ".join(DON) + " |"); yaz("|---|---|---|---|---|")
for f in FC:
    cells = []
    for d in DON:
        x = X[X.don == d]; cells.append(f"{x[x.Y == 1][f].median():.2f} / {x[x.D == 1][f].median():.2f} / {x[(x.Y + x.D) == 0][f].median():.2f}")
    yaz(f"| {f} | " + " | ".join(cells) + " |")
yaz("\n## 2. Yön ayrımı — yukarı payı Y / (Y + D), keşifte beşte birlik dilimler (dilim sınırları keşiften)")
yaz("| özellik | dilim | keşif 2021–23 | 2024 | 2025 | 2026 | işaret |"); yaz("|---|---|---|---|---|---|---|")
YD = X[(X.Y + X.D) > 0]; genel = {d: YD[YD.don == d].Y.mean() for d in DON}
yaz("| (genel) | — | " + " | ".join(f"%{100 * genel[d]:.0f} ({len(YD[YD.don == d])})" for d in DON) + " | |")
BUL = []
for f in FC[:-1] + ["dow"]:
    k = YD[YD.don == "2021–23"][f].dropna()
    if k.nunique() < 5: kes = sorted(k.unique()); bins = [-np.inf] + [v + 0.5 for v in kes[:-1]] + [np.inf] if f != "dow" else [-0.5 + i for i in range(8)]
    else: bins = [-np.inf] + list(np.unique(np.quantile(k, [0.2, 0.4, 0.6, 0.8]))) + [np.inf]
    YD_ = YD.assign(b=pd.cut(YD[f], bins, labels=False))
    for b in sorted(YD_.b.dropna().unique()):
        z = YD_[YD_.b == b]; pay = {d: (z[z.don == d].Y.mean(), len(z[z.don == d])) for d in DON}
        isaret = pay["2021–23"][1] >= 30 and pay["2021–23"][0] >= 0.6 and all(pay[d][1] >= 30 and pay[d][0] >= 0.6 and pay[d][0] >= genel[d] + 0.10 for d in DON[1:])
        if isaret: BUL.append((f, b))
        lo, hi = bins[int(b)], bins[int(b) + 1]
        yaz(f"| {f} | {lo:.2f} … {hi:.2f} | " + " | ".join(f"%{100 * pay[d][0]:.0f} ({pay[d][1]})" if pay[d][1] else "—" for d in DON) + f" | {'✅' if isaret else ''} |")
yaz(f"\n**Yön işareti → {'✅ bulundu: ' + ', '.join(f'{a} dilim {int(b) + 1}' for a, b in BUL) if BUL else '❌ hiçbir dilim dört dönemde de yükselişi çöküşten ayırmıyor'}**")
yaz("\n## 3. Büyütenler — Y içinde yükseliş boyu ile Spearman ilişkisi")
yaz("| özellik | " + " | ".join(DON) + " |"); yaz("|---|---|---|---|---|")
for f in FC:
    yaz(f"| {f} | " + " | ".join(f"{X[(X.Y == 1) & (X.don == d)][[f, 'boy']].corr(method='spearman').iloc[0, 1]:+.2f}" for d in DON) + " |")
yaz("\n## 4. Sonrası — Y gününün kapanışından sonra (medyan · pozitif oranı)")
yaz("| dönem | 1 gün | 3 gün | 7 gün | Y günü medyan boy |"); yaz("|---|---|---|---|---|")
for d in DON:
    x = X[(X.Y == 1) & (X.don == d)]; yaz(f"| {d} | " + " | ".join(f"{100 * x[c].median():+.1f}% · %{100 * (x[c] > 0).mean():.0f}" for c in ("r1", "r3", "r7")) + f" | +%{100 * x.boy.median():.0f} |")
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
yaz("\n## 5. (Ek 1) +%30'dan fazla yükselenler (B30) ↔ normal en fazla +%10 yükselenler (N10) ve ↔ −%30 düşenler (Ç30)")
X["B30"], X["N10"], X["C30"] = (X.gd >= 0.30), (X.gd > 0) & (X.gd <= 0.10), (X.gd <= -0.30)
yaz("| dönem | B30 | N10 | Ç30 |"); yaz("|---|---|---|---|")
for d in DON: x = X[X.don == d]; yaz(f"| {d} | {int(x.B30.sum())} | {int(x.N10.sum()):,} | {int(x.C30.sum())} |")
def auc(a, b):
    a, b = a.dropna(), b.dropna()
    if len(a) < 20 or len(b) < 20: return np.nan
    return roc_auc_score(np.r_[np.ones(len(a)), np.zeros(len(b))], np.r_[a.values, b.values])
FE5 = [f for f in FC if not f.startswith("aynı gün")]; AY = {"N10": [], "C30": []}
for kars, ad in (("N10", "normal yükselen (≤ +%10)"), ("C30", "−%30 düşen")):
    yaz(f"\n**B30 ↔ {ad}: medyan B30 / {kars} · AUC** (0,5 = ayırt edemiyor; ≥ 0,60 ya da ≤ 0,40 anlamlı)")
    yaz("| özellik | " + " | ".join(DON) + " | ayırt edici |"); yaz("|---|---|---|---|---|---|")
    for f in FE5:
        cells, au = [], []
        for d in DON:
            x = X[X.don == d]; a, b = x[x.B30][f], x[x[kars]][f]; u = auc(a, b); au.append(u)
            cells.append(f"{a.median():.2f} / {b.median():.2f} · {u:.2f}")
        ok = all(np.isfinite(u) and abs(u - 0.5) >= 0.10 for u in au) and (all(u > 0.5 for u in au) or all(u < 0.5 for u in au))
        if ok: AY[kars].append(f)
        yaz(f"| {f} | " + " | ".join(cells) + f" | {'✅' if ok else ''} |")
    XX = X[X.B30 | X[kars]].copy(); XX["yy"] = XX.B30.astype(int); r = []
    for yl in (2024, 2025, 2026):
        tr, te = XX[XX.t.dt.year < yl], XX[XX.t.dt.year == yl]
        if te.yy.nunique() < 2: continue
        m = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=31, min_samples_leaf=50, random_state=0).fit(tr[FE5], tr.yy)
        r.append(f"{yl}: {roc_auc_score(te.yy, m.predict_proba(te[FE5])[:, 1]):.2f}")
    yaz(f"_Bilgi — tüm özelliklerle model, yürüyen test AUC (B30 ↔ {kars}): " + " · ".join(r) + "_")
yaz(f"\n**B30 ↔ normal yükselen: dört dönemde de ayırt eden → {', '.join(AY['N10']) or 'yok'}**")
yaz(f"**B30 ↔ −%30 düşen (yön): dört dönemde de ayırt eden → {', '.join(AY['C30']) or 'yok'}**")
open("pompaonce_sonuc.md", "w").write("\n".join(out) + "\n")
