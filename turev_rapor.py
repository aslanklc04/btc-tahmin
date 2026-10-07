# turev_rapor.py — turev.py sonuçlarını birleştirir: vadeli pozisyonlanma özellikleri 24 saatlik tahmini iyileştiriyor mu?
# ÖNCEDEN SABİT karar: 10 coin ortalamasında AUC farkı (türev − temel) seçimde (2022–23) ve kararda (2024+) > 0, kararda 6 karıştırmanın HEPSİNDEN büyük,
# ve 2024+ 'Çok güçlü ↑' isabeti ile limit-komisyonlu net'i temelden yüksek → ✅
import os, glob, numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score
from ortak import *
L = []
def yaz(s=""): print(s, flush=True); L.append(s)
EX = {os.path.basename(p)[6:-4][:-4]: pd.read_pickle(p) for p in glob.glob("art/**/turev_*USDT.pkl", recursive=True)}
H, D1, FEE = 24, 1, 0.0002
DON = {"2022–23 (seçim)": ("2022-01-01", "2024-01-01"), "2024+ (karar)": ("2024-01-01", "2030-01-01"), "2026": ("2026-01-01", "2030-01-01")}
DON = {k: (pd.Timestamp(a, tz="UTC"), pd.Timestamp(b, tz="UTC")) for k, (a, b) in DON.items()}
VAR = sorted({c[2:] for X in EX.values() for c in X.columns if c.startswith("S_")}, key=lambda v: (v != "temel", v != "turev", v))
au, ev = [], []
for s, X in EX.items():
    X = X.reindex(pd.date_range(X.index[0], X.index[-1], freq="1h", tz="UTC")); c = X.close.ffill(limit=3).values; n = len(X)
    y = np.r_[np.log(c[H:] / c[:-H]), np.full(H, np.nan)]
    for v in VAR:
        S, C_, T10 = X[f"S_{v}"].values, X[f"C_{v}"].values, X[f"T10_{v}"].values
        pos = np.where(np.isfinite(S) & np.isfinite(y))[0][::H]
        mk = np.nan_to_num((S > 0) & (C_ >= T10)).astype(bool) & np.isfinite(T10) & (np.arange(n) + H + D1 < n)
        for i in events(mk, H): ev.append((s, v, X.index[i], c[i + H + D1] / c[i + D1] - 1))
        for pn, (a, b) in DON.items():
            p_ = pos[(X.index[pos] >= a) & (X.index[pos] < b)]
            if len(p_) > 50 and len(set(y[p_] > 0)) == 2: au.append(dict(coin=s, v=v, donem=pn, auc=roc_auc_score(y[p_] > 0, S[p_])))
AU = pd.DataFrame(au); EV = pd.DataFrame(ev, columns=["coin", "v", "t", "g"]).dropna(); EV["net"] = EV.g - 2 * FEE
yaz(f"# 🏦 Vadeli piyasa pozisyonlanması → 24 saat tahmin — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nCoin'ler ({len(EX)}): {' '.join(sorted(EX))} · varyantlar: {', '.join(VAR)}\n")
P = AU.pivot_table(index=["coin"], columns=["donem", "v"], values="auc")
yaz("## Coin başına AUC farkı (türev − temel)\n```\n" + pd.DataFrame({pn: P[(pn, "turev")] - P[(pn, "temel")] for pn in DON if (pn, "turev") in P}).round(4).to_string() + "\n```")
M = AU.groupby(["donem", "v"]).auc.mean().unstack()
d = M.sub(M["temel"], axis=0)
yaz("## 10 coin ortalaması AUC ve fark (temel'e göre)\n```\n" + M.round(4).to_string() + "\n```\n```\n" + d.round(4).to_string() + "\n```")
rows = []
for (v, pn), _ in pd.MultiIndex.from_product([VAR, DON]).to_frame().iterrows():
    a, b = DON[pn]; x = EV[(EV.v == v) & (EV.t >= a) & (EV.t < b)]
    if len(x): lo, _ = wboot(x.net.values, x.t.values); rows.append(dict(v=v, donem=pn, sinyal=len(x), haftada=len(x) / ((min(b, EV.t.max()) - a).days / 7), isabet=100 * (x.g > 0).mean(), net=100 * x.net.mean(), alt=100 * lo))
R = pd.DataFrame(rows)
yaz("## 'Çok güçlü ↑' sinyali (24 saat, giriş 1 saat sonra, limit komisyon) — 10 coin toplamı\n```\n" + R.set_index(["donem", "v"]).round(2).to_string() + "\n```")
sec, kar = "2022–23 (seçim)", "2024+ (karar)"; ks = [v for v in VAR if v.startswith("k")]
c1 = d.loc[sec, "turev"] > 0; c2 = d.loc[kar, "turev"] > 0; c3 = all(d.loc[kar, "turev"] > d.loc[kar, k] for k in ks)
rt, rb = R.set_index(["donem", "v"]).loc[(kar, "turev")], R.set_index(["donem", "v"]).loc[(kar, "temel")]; c4 = rt.isabet > rb.isabet and rt.net > rb.net
yaz(f"\n## Karar: {'✅ vadeli piyasa bilgisi işe yarıyor' if (c1 and c2 and c3 and c4) else '❌ tutarlı kazanç yok'}")
yaz(f"- AUC farkı seçimde {d.loc[sec, 'turev']:+.4f} ({'✓' if c1 else '✗'}) · kararda {d.loc[kar, 'turev']:+.4f} ({'✓' if c2 else '✗'})")
yaz(f"- Karıştırmalar (bilgisiz) kararda: " + " ".join(f"{d.loc[kar, k]:+.4f}" for k in ks) + f" → gerçek fark hepsinden büyük mü: {'✓' if c3 else '✗'}")
yaz(f"- 2024+ 'Çok güçlü ↑': isabet %{rb.isabet:.1f} → %{rt.isabet:.1f} · net {rb.net:+.2f} → {rt.net:+.2f} · haftada {rb.haftada:.1f} → {rt.haftada:.1f} ({'✓' if c4 else '✗'})")
if "2026" in d.index: yaz(f"- 2026: AUC farkı {d.loc['2026', 'turev']:+.4f}" + (f" · isabet %{R.set_index(['donem','v']).loc[('2026','temel')].isabet:.1f} → %{R.set_index(['donem','v']).loc[('2026','turev')].isabet:.1f}" if ("2026", "turev") in R.set_index(["donem", "v"]).index else ""))
open("turev_sonuc.md", "w").write("\n".join(L) + "\n")
