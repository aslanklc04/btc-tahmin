# pompa50.py — PROTOKOL_pompa50.md: 1 günde +%50 → pompa50_sonuc.md
import json, re, numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
K = pd.read_parquet("yeniliste_mum.parquet"); F = pd.read_parquet("yeniliste_fon.parquet")
K["t"] = pd.to_datetime(K.t, utc=True).dt.floor("D"); K = K.drop_duplicates(["s", "t"])
VB = {x["s"]: x for x in json.load(open("vadeli_bilgi.json"))}
HARIC = re.compile(r"^(USDC|FDUSD|TUSD|BUSD|USDP|DAI|BTCDOM|DEFI|FOOTBALL|BLUEBIRD)USDT$")
ok = [s for s in K.s.unique() if s.endswith("USDT") and not HARIC.match(s) and ((s not in VB) or (VB[s]["ut"] == "COIN" and VB[s]["ct"] == "PERPETUAL"))]
K = K[K.s.isin(ok)]
O, Hh, L, C, V = (K.pivot(index="t", columns="s", values=k) for k in ("o", "h", "l", "c", "v"))
F["t"] = pd.to_datetime(F.t, utc=True); FP = F.pivot_table(index=F.t.dt.floor("D"), columns="s", values="fr", aggfunc="sum").reindex(index=O.index, columns=O.columns)
ilk = K.groupby("s").t.min()
lc = np.log(C); lr = lc.diff()
o1, h1, l1, c1 = O.shift(-1), Hh.shift(-1), L.shift(-1), C.shift(-1)
y = (h1 >= 1.5 * o1).astype(float).where(o1.notna() & h1.notna())
yas = pd.DataFrame((O.index.tz_convert(None).values[:, None] - ilk.reindex(O.columns).dt.tz_convert(None).values[None, :]) / np.timedelta64(1, "D"), index=O.index, columns=O.columns)
FE = {"f1 fonlama t": FP, "f2 fonlama 3 g": FP.rolling(3, min_periods=1).sum(), "f3 getiri 1 g": lc.diff(1), "f3 getiri 3 g": lc.diff(3), "f3 getiri 7 g": lc.diff(7),
      "f4 hacim oranı": V / V.rolling(30, min_periods=10).mean().shift(1), "f5 yaş (gün)": yas, "f6 30 g zirveye uzaklık": C / Hh.rolling(30, min_periods=5).max() - 1,
      "f6 30 g dibe uzaklık": C / L.rolling(30, min_periods=5).min() - 1, "f7 30 g oynaklık": lr.rolling(30, min_periods=10).std(),
      "f8 BTC 1 g": pd.DataFrame(np.repeat(lc["BTCUSDT"].diff().values[:, None], len(O.columns), 1), index=O.index, columns=O.columns),
      "f9 üst gölge / gövde": (Hh - np.maximum(O, C)) / ((C - O).abs() + 1e-12 * C), "f10 son 90 g olay": y.shift(1).rolling(90, min_periods=1).sum()}
# işlem sonucu (long t+1 açılış, 🎯 +%50, stop −%20)
pe = o1 * 1.002; fon1 = FP.shift(-1).fillna(0)
hit = h1 >= pe * 1.5; stp = l1 <= pe * 0.8
net = np.where(stp, -0.20 - 0.001, np.where(hit, 0.50 - 0.0007, c1 / pe - 1 - 0.001)) - fon1.values
net_s = np.where(hit, 0.50 - 0.0007, np.maximum(c1 / pe - 1, -1) - 0.001) - fon1.values
st = lambda D: D.stack(future_stack=True)
X = pd.DataFrame({k: st(v) for k, v in FE.items()}); X["y"] = st(y); X["net"] = st(pd.DataFrame(net, index=O.index, columns=O.columns)); X["net_s"] = st(pd.DataFrame(net_s, index=O.index, columns=O.columns))
X = X[X.y.notna() & X["f7 30 g oynaklık"].notna()].reset_index().rename(columns={"level_0": "t", "level_1": "s"}); X["yil"] = X.t.dt.year
FC = list(FE)
yaz("# 🚀 1 günde +%50 — PROTOKOL_pompa50.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {X.s.nunique()} coin vadelisi (kapatılanlar dahil) · {len(X):,} coin-gün · olay: ertesi gün en yüksek ≥ açılış × 1,5_\n")
yaz("**Olay sıklığı:** " + " · ".join(f"{yl}: %{100 * g.y.mean():.2f} · günde {g.groupby('t').y.sum().mean():.2f} olay" for yl, g in X.groupby("yil")) + "\n")
k = X[X.yil < 2024]; taban = k.y.mean()
yaz("## A) Tek özellik — keşif (2021–23) on dilim: olay oranı / taban (en düşük dilim … en yüksek dilim)"); yaz("| özellik | lift dilim 1 … 10 |"); yaz("|---|---|")
for f in FC:
    q = pd.qcut(k[f].rank(method="first"), 10, labels=False); lf = k.groupby(q).y.mean() / taban; yaz(f"| {f} | " + " · ".join(f"{v:.1f}" for v in lf.values) + " |")
yaz("\n## B) Model — yıllık yürüyen test, her gün en olası 3 coin")
yaz("| yıl | taban olay oranı | seçilen · günde | **olay oranı (kat)** | işlem başı net (stop −%20) | stopsuz | en kötü | rastgele 3 (×50): olay % · net en iyi |"); yaz("|---|---|---|---|---|---|---|---|")
rng = np.random.default_rng(50); BUL = True
for yl in (2024, 2025, 2026):
    tr, te = X[X.yil < yl], X[X.yil == yl].copy()
    md = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=31, min_samples_leaf=100, random_state=0).fit(tr[FC], tr.y)
    te["p"] = md.predict_proba(te[FC])[:, 1]; S = te.sort_values("p", ascending=False).groupby("t").head(3)
    PL = []
    for _ in range(50):
        R = te.assign(r=rng.random(len(te))).sort_values("r").groupby("t").head(3); PL.append((R.y.mean(), R.net.mean()))
    tb = te.y.mean(); g = S.y.mean() >= 5 * tb and S.net.mean() > 0 and S.y.mean() > max(p[0] for p in PL) and S.net.mean() > max(p[1] for p in PL); BUL &= g
    yaz(f"| {yl} | %{100 * tb:.2f} | {len(S)} · {len(S) / te.t.nunique():.1f} | **%{100 * S.y.mean():.1f} ({S.y.mean() / tb:.1f}×)** | {100 * S.net.mean():+.2f}% | {100 * S.net_s.mean():+.2f}% | {100 * S.net.min():.0f}% | %{100 * max(p[0] for p in PL):.2f} · {100 * max(p[1] for p in PL):+.2f}% |")
    if yl == 2026: imp = sorted(((c, abs(te.p.rank().corr(te[c].rank()))) for c in FC), key=lambda x: -x[1])
    stp_ = (S.net <= -0.20).mean(); yaz(f"|  | _bilgi: seçilenlerde −%20 stop oranı %{100 * stp_:.0f} · +%50'ye değen %{100 * S.y.mean():.1f}_ | | | | | | |")
yaz(f"\n**Sonuç → {'✅ BULUNDU' if BUL else '❌ bulunamadı'}**")
yaz("\n_Bilgi — 2026 modelinin olasılığıyla en ilişkili özellikler (|Spearman|):_ " + ", ".join(f"{a} {b:.2f}" for a, b in imp[:6]))
open("pompa50_sonuc.md", "w").write("\n".join(out) + "\n")
