# kopya.py — PROTOKOL_kopya.md: Copy Trading liderlerinde kalıcılık (yürüyen test) → kopya_sonuc.md
import numpy as np, pandas as pd
from scipy.stats import spearmanr
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
S = pd.read_parquet("kopya_roi.parquet"); M = pd.read_parquet("kopya_meta.parquet").set_index("leadPortfolioId")
S.index = S.index.floor("D"); S = S.groupby(level=0).last()
st = pd.to_datetime(M.startTime, unit="ms", utc=True).dt.floor("D")
for c in S.columns:                                                                               # başlangıç öncesi = yok
    S.loc[S.index < st.get(c, S.index[0]), c] = np.nan
W = (1 + S / 100).clip(lower=1e-6)                                                                # servet endeksi
GUN = pd.date_range(S.index.max() - pd.Timedelta(days=364), S.index.max(), freq="D"); W = W.reindex(GUN)
r = W.pct_change(fill_method=None)
F_ = [GUN[i] for i in range(120, 335 + 1, 30) if i + 30 < len(GUN)]
yaz("# 🪞 Binance Copy Trading — en iyi görünen liderleri takip etmek kazandırır mı? (PROTOKOL_kopya.md)")
yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {S.shape[1]} portföy · {GUN[0]:%d.%m.%Y} → {GUN[-1]:%d.%m.%Y} · {len(F_)} oluşum tarihi · ileri 30 gün · kâr payı %10 (pozitif getiriden)_\n")
kp = lambda x: np.where(x > 0, 0.9 * x, x)
R, ok_s1, ok_s2 = [], [], []
yaz("| oluşum | uygun portföy | hepsi medyan | S1 ROI en iyi %10: medyan · ort. · ≤ −%50 | S2 Sharpe en iyi %10: medyan · ort. · ≤ −%50 | vitrin ilk 10 (ROI): medyan · ort. | Spearman S1 / S2 |"); yaz("|---|---|---|---|---|---|---|")
for F in F_:
    i = GUN.get_loc(F); gecmis = W.iloc[:i + 1]; n_g = gecmis.notna().sum()
    uy = [c for c in W.columns if n_g[c] >= 60 and np.isfinite(W.iat[i, W.columns.get_loc(c)])]
    lb = W.iloc[max(0, i - 90):i + 1][uy]; s1 = lb.ffill().iloc[-1] / lb.bfill().iloc[0] - 1
    rr = r.iloc[max(0, i - 90) + 1:i + 1][uy]; s2 = rr.mean() / rr.std()
    son = W.iloc[i:i + 31][uy].ffill().iloc[-1]; ileri = pd.Series(kp(son / W.iloc[i][uy] - 1), index=uy)
    d = pd.DataFrame({"s1": s1, "s2": s2, "f": ileri}).dropna(); hep = d.f.median()
    t1 = d[d.s1 >= d.s1.quantile(0.9)]; t2 = d[d.s2 >= d.s2.quantile(0.9)]; v = d.nlargest(10, "s1")
    ok_s1.append(t1.f.median() > 0 and t1.f.median() > hep); ok_s2.append(t2.f.median() > 0 and t2.f.median() > hep)
    R.append(pd.concat([t1.assign(g="s1"), t2.assign(g="s2"), d.assign(g="hep"), v.assign(g="v")]).assign(F=F))
    yaz(f"| {F:%d.%m.%Y} | {len(d)} | {100 * hep:+.1f}% | {100 * t1.f.median():+.1f}% · {100 * t1.f.mean():+.1f}% · %{100 * (t1.f <= -0.5).mean():.0f} | {100 * t2.f.median():+.1f}% · {100 * t2.f.mean():+.1f}% · %{100 * (t2.f <= -0.5).mean():.0f} | {100 * v.f.median():+.1f}% · {100 * v.f.mean():+.1f}% | {spearmanr(d.s1, d.f)[0]:+.2f} / {spearmanr(d.s2, d.f)[0]:+.2f} |")
A = pd.concat(R)
yaz(f"\n**Tüm tarihler birlikte (kâr payı sonrası, 30 günlük):**")
for g, ad in (("s1", "S1 ROI en iyi %10"), ("s2", "S2 Sharpe en iyi %10"), ("v", "vitrin ilk 10"), ("hep", "tüm portföyler")):
    x = A[A.g == g].f; yaz(f"- {ad}: {len(x)} · medyan {100 * x.median():+.1f}% · ort. {100 * x.mean():+.1f}% · pozitif %{100 * (x > 0).mean():.0f} · ≤ −%50 %{100 * (x <= -0.5).mean():.0f} · ≤ −%90 %{100 * (x <= -0.9).mean():.0f}")
g1 = np.mean(ok_s1) >= 0.7 and A[A.g == "s1"].f.mean() > 0 and (A[A.g == "s1"].f <= -0.5).mean() <= 0.10
g2 = np.mean(ok_s2) >= 0.7 and A[A.g == "s2"].f.mean() > 0 and (A[A.g == "s2"].f <= -0.5).mean() <= 0.10
yaz(f"\n**S1 ROI: şartı sağlayan tarih %{100 * np.mean(ok_s1):.0f} → {'✅' if g1 else '❌'} · S2 Sharpe: %{100 * np.mean(ok_s2):.0f} → {'✅' if g2 else '❌'}**")
yaz(f"\n**Sonuç → {'✅ geçmişte takip kazandırmış (yanlılık nedeniyle canlı ileriye dönük izleme şart)' if (g1 or g2) else '❌ en iyi görünen liderleri takip etmek kazandırmamış'}**")
yaz(f"\n_Bilgi: bugünkü listede 365 günde ROI > 0 olan portföy %{100 * (M.roi > 0).mean():.0f} · ROI ≤ −%90 %{100 * (M.roi <= -90).mean():.0f} · kopyalayanların toplam kârı (copierPnl) {M.copierPnl.sum() / 1e6:+.1f} M$ (pozitif olanlar {M.copierPnl[M.copierPnl > 0].sum() / 1e6:+.1f} · negatif {M.copierPnl[M.copierPnl < 0].sum() / 1e6:+.1f})_")
open("kopya_sonuc.md", "w").write("\n".join(out) + "\n")
