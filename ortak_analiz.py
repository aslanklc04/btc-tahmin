# ortak_analiz.py — "BTC 4s Çok güçlü ↑ ile AYNI SAATTE gelen coin sinyali" (kullanıcının hipotezi) · seçim 2020–23, hüküm 2024+
import glob, os, numpy as np, pandas as pd
from ortak import *
L = []
def yaz(s=""): print(s, flush=True); L.append(s)
f = lambda p: glob.glob(f"art/**/{p}", recursive=True)
EXB = pd.read_pickle(f("disa_BTCUSDT.pkl")[0]); PER = {"2020–23": ("2020-01-01", "2024-01-01"), "2024+": ("2024-01-01", "2030-01-01")}
rows = []
for p in sorted(f("disa_*USDT.pkl")):
    sym = os.path.basename(p)[5:-4]
    if sym == "BTCUSDT": continue
    X = pd.read_pickle(p); B = EXB.reindex(X.index); bs = B.u4.fillna(False).values.astype(bool)
    bany = (B.star.fillna(False) | B.u4.fillna(False) | B.acls.fillna(False)).values.astype(bool)
    for k, H in [("star", 8), ("u4", 4), ("acls", 4)]:
        for kosul, c in [("🤝 ortak (BTC 4s ÇG↑)", bs), ("tek (BTC sessiz)", ~bany), ("hepsi", np.ones(len(X), bool))]:
            m = X[k].values.astype(bool) & c & X.y4.notna().values; ev = events(m, H); t = X.index[ev]
            for per, (a, b) in PER.items():
                s = (t >= pd.Timestamp(a, tz="UTC")) & (t < pd.Timestamp(b, tz="UTC"))
                if s.sum() == 0: continue
                r = np.exp(X.y4.values[ev][s]) - 1; rb = np.exp(B.y4.values[ev][s]) - 1; tt = t[s]; md = tt[len(tt) // 2]
                wk = max(1, (min(pd.Timestamp(b, tz="UTC"), X.index[-1]) - max(pd.Timestamp(a, tz="UTC"), X.index[0])).days / 7)
                rows.append(dict(coin=sym[:-4], sinyal={"star": "⭐", "u4": "4s ÇG↑", "acls": "A"}[k], kosul=kosul, donem=per, n=int(s.sum()), haftada=s.sum() / wk,
                                 isabet=(r > 0).mean() * 100, y1=(r[tt < md] > 0).mean() * 100, y2=(r[tt >= md] > 0).mean() * 100,
                                 brut=r.mean() * 100, btc_brut=np.nanmean(rb) * 100, btc_isabet=np.nanmean(rb > 0) * 100))
D = pd.DataFrame(rows)
yaz(f"# 🤝 BTC + coin ortak sinyal analizi — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}")
yaz("Hipotez (kullanıcıdan, veriye bakmadan önce): coin sinyali BTC'nin 4s Çok güçlü ↑ sinyaliyle AYNI SAATTE gelirse daha isabetli. Sonuç: coin'in 4 saat sonraki fiyatı.\n")
P = D.assign(k=D.n * D.isabet / 100, g=D.n * D.brut / 100, gb=D.n * D.btc_brut / 100).groupby(["sinyal", "kosul", "donem"]).agg(n=("n", "sum"), k=("k", "sum"), g=("g", "sum"), gb=("gb", "sum"), haftada=("haftada", "sum"))
P["isabet %"] = (100 * P.k / P.n).round(1); P["coin brüt %"] = (100 * P.g / P.n).round(3); P["BTC brüt % (aynı saat)"] = (100 * P.gb / P.n).round(3); P["haftada"] = P.haftada.round(1)
yaz("## 1) Tüm coin'ler birlikte (seçim 2020–23 → hüküm 2024+)\n```\n" + P.drop(columns=["k", "g", "gb"]).to_string() + "\n```")
J = D[D.kosul.str.startswith("🤝")].copy()
S = J[J.donem == "2020–23"].set_index(["coin", "sinyal"]); Hh = J[J.donem == "2024+"].set_index(["coin", "sinyal"])
T = Hh[["n", "haftada", "isabet", "y1", "y2", "brut", "btc_brut"]].join(S[["n", "isabet"]].rename(columns={"n": "n 20–23", "isabet": "isabet 20–23"}))
T["AÇ"] = (T.n >= 50) & (T.isabet >= 58) & (T.y1 >= 55) & (T.y2 >= 55)
yaz("\n## 2) Coin bazında 🤝 ortak sinyal (2024+; kural: isabet ≥ %58, ≥ 50 sinyal, iki yarıda ≥ %55) · yanında 2020–23\n```\n" + T.round(1).sort_values("isabet", ascending=False).to_string() + "\n```")
yaz("\nAçılacak 🤝 ortak sinyaller: " + (", ".join(f"{c} {s}" for c, s in T[T.AÇ].index) or "yok"))
open("ortak_sonuc.md", "w").write("\n".join(L) + "\n"); T[T.AÇ].reset_index()[["coin", "sinyal"]].to_csv("ortak_acik.csv", index=False)
