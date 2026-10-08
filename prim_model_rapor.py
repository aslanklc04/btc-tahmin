# prim_model_rapor.py — prim_model.py sonuçları: Coinbase primi modelin GİRDİSİ olunca 4 / 8 saatlik tahmin iyileşiyor mu?
# ÖNCEDEN SABİT karar (her ufuk için, coin ortalaması): AUC farkı (prim − temel) seçimde (2022–23) ve kararda (2024+) > 0, kararda tüm karıştırmalardan büyük,
# ve 2024+ 'Çok güçlü ↑' (son 30 günün en güçlü %10'u, yukarı) isabeti ile limit-komisyonlu net'i temelden yüksek → ✅ (2026 ayrıca)
import os, glob, re, numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score
from ortak import *
L = []
def yaz(s=""): print(s, flush=True); L.append(s)
FEE = 0.0002
DON = {"2022–23 (seçim)": ("2022-01-01", "2024-01-01"), "2024+ (karar)": ("2024-01-01", "2030-01-01"), "2026": ("2026-01-01", "2030-01-01")}
DON = {k: (pd.Timestamp(a, tz="UTC"), pd.Timestamp(b, tz="UTC")) for k, (a, b) in DON.items()}
FL = {}
for pth in glob.glob("art/**/pm_*USDT_*.pkl", recursive=True):
    m = re.match(r"pm_(\w+USDT)_(\d+)\.pkl", os.path.basename(pth)); FL.setdefault(int(m.group(2)), {})[m.group(1)] = pd.read_pickle(pth)
yaz(f"# 💵🧠 Coinbase primi modelin içinde — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n" + " · ".join(f"{H} saat: {len(v)} coin ({' '.join(sorted(s[:-4] for s in v))})" for H, v in sorted(FL.items())) + "\n")
for H, EX in sorted(FL.items()):
    VAR = sorted({c[2:] for X in EX.values() for c in X.columns if c.startswith("S_")}, key=lambda v: (v != "temel", v != "prim", v))
    au, ev = [], []
    for s, X in EX.items():
        X = X.reindex(pd.date_range(X.index[0], X.index[-1], freq="1h", tz="UTC")); c = X.close.ffill(limit=3).values; n = len(X)
        y = np.r_[np.log(c[H:] / c[:-H]), np.full(H, np.nan)]
        for v in VAR:
            if f"S_{v}" not in X: continue
            S, C_, T10 = X[f"S_{v}"].values, X[f"C_{v}"].values, X[f"T10_{v}"].values
            pos = np.where(np.isfinite(S) & np.isfinite(y))[0][::H]
            mk = np.nan_to_num((S > 0) & (C_ >= T10)).astype(bool) & np.isfinite(T10) & (np.arange(n) + H < n)
            for i in events(mk, H): ev.append((s, v, X.index[i], c[i + H] / c[i] - 1))
            for pn, (a, b) in DON.items():
                p_ = pos[(X.index[pos] >= a) & (X.index[pos] < b)]
                if len(p_) > 50 and len(set(y[p_] > 0)) == 2: au.append(dict(coin=s, v=v, donem=pn, auc=roc_auc_score(y[p_] > 0, S[p_])))
    AU = pd.DataFrame(au); EV = pd.DataFrame(ev, columns=["coin", "v", "t", "g"]).dropna(); EV["net"] = EV.g - 2 * FEE
    P = AU.pivot_table(index="coin", columns=["donem", "v"], values="auc")
    yaz(f"## {H} saat\n### Coin başına AUC farkı (prim − temel)\n```\n" + pd.DataFrame({pn: P[(pn, "prim")] - P[(pn, "temel")] for pn in DON if (pn, "prim") in P}).round(4).to_string() + "\n```")
    M = AU.groupby(["donem", "v"]).auc.mean().unstack(); d = M.sub(M["temel"], axis=0)
    yaz("### Coin ortalaması AUC ve temel'e göre fark\n```\n" + M.round(4).to_string() + "\n```\n```\n" + d.round(4).to_string() + "\n```")
    rows = []
    for v in VAR:
        for pn, (a, b) in DON.items():
            x = EV[(EV.v == v) & (EV.t >= a) & (EV.t < b)]
            if len(x): lo, _ = wboot(x.net.values, x.t.values); rows.append(dict(v=v, donem=pn, sinyal=len(x), haftada=len(x) / max(1, (min(b, EV.t.max()) - a).days / 7), isabet=100 * (x.g > 0).mean(), net=100 * x.net.mean(), alt=100 * lo))
    R = pd.DataFrame(rows).set_index(["donem", "v"])
    yaz(f"### 'Çok güçlü ↑' sinyali ({H} saat tut, limit komisyon) — coin'ler toplamı\n```\n" + R.round(2).to_string() + "\n```")
    sec, kar = "2022–23 (seçim)", "2024+ (karar)"; ks = [v for v in VAR if v.startswith("k")]
    c1, c2 = d.loc[sec, "prim"] > 0, d.loc[kar, "prim"] > 0; c3 = all(d.loc[kar, "prim"] > d.loc[kar, k] for k in ks)
    rt, rb = R.loc[(kar, "prim")], R.loc[(kar, "temel")]; c4 = rt.isabet > rb.isabet and rt.net > rb.net
    yaz(f"### Karar ({H} saat): {'✅ prim modelin içinde işe yarıyor' if (c1 and c2 and c3 and c4) else '❌ tutarlı kazanç yok'}")
    yaz(f"- AUC farkı seçimde {d.loc[sec, 'prim']:+.4f} ({'✓' if c1 else '✗'}) · kararda {d.loc[kar, 'prim']:+.4f} ({'✓' if c2 else '✗'})")
    yaz("- Karıştırmalar kararda: " + " ".join(f"{d.loc[kar, k]:+.4f}" for k in ks) + f" → gerçek fark hepsinden büyük mü: {'✓' if c3 else '✗'}")
    yaz(f"- 2024+ 'Çok güçlü ↑': isabet %{rb.isabet:.1f} → %{rt.isabet:.1f} · net {rb.net:+.2f} → {rt.net:+.2f} · haftada {rb.haftada:.1f} → {rt.haftada:.1f} ({'✓' if c4 else '✗'})")
    if ("2026", "prim") in R.index: yaz(f"- 2026: AUC farkı {d.loc['2026', 'prim']:+.4f} · isabet %{R.loc[('2026','temel')].isabet:.1f} → %{R.loc[('2026','prim')].isabet:.1f} · net {R.loc[('2026','temel')].net:+.2f} → {R.loc[('2026','prim')].net:+.2f}\n")
open("prim_model_sonuc.md", "w").write("\n".join(L) + "\n")
