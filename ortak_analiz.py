# ortak_analiz.py — 🤝 BTC + coin ORTAK SİNYAL denetimi (aylık, coin eğitimlerinden sonra).
# Ortak sinyal: coin'in ⭐ / 4s Çok güçlü ↑ / A sınıfı sinyali, BTC'nin 4s Çok güçlü ↑ sinyaliyle AYNI SAATTE gelirse.
# Bulgu (07.10.2026 taraması, 19 coin): tüm coin'ler birlikte isabet 2020–23'te %63–64,5, 2024+'da %59–61 (BTC sessizken %53–56).
# Ayrıca 🔇 BTC SESSİZKEN: coin sinyali, BTC'de ⭐ / 4s Çok güçlü ↑ / A sınıfı YOKKEN gelirse (BTC'de fırsat yokken coin'de fırsat).
# Açma kuralı (coin + sinyal başına, iki liste için aynı): 2024+ isabet ≥ %58, ≥ 50 sinyal, 2024+ döneminin iki yarısında da ≥ %55,
#   ve 2020–23'te ≥ 30 sinyal varsa orada da ≥ %55. Sonuç: durum/ortak_acik.csv ve durum/tek_acik.csv (tahmin_coin.py okur).
import glob, os, numpy as np, pandas as pd
from ortak import *
L = []
def yaz(s=""): print(s, flush=True); L.append(s)
f = lambda p: glob.glob(f"art/**/{p}", recursive=True)
EXB = pd.read_pickle(f("disa_BTCUSDT.pkl")[0]); A24 = pd.Timestamp("2024-01-01", tz="UTC"); A20 = pd.Timestamp("2020-01-01", tz="UTC")
AD = {"star": "⭐", "u4": "4s ÇG↑", "acls": "A"}; rows, havuz = [], []
for p in sorted(f("disa_*USDT.pkl")):
    sym = os.path.basename(p)[5:-4]
    if sym == "BTCUSDT": continue
    X = pd.read_pickle(p); B = EXB.reindex(X.index); bs = B.u4.fillna(False).values.astype(bool)
    bany = (B.star.fillna(False) | B.u4.fillna(False) | B.acls.fillna(False)).values.astype(bool)
    for k, H in [("star", 8), ("u4", 4), ("acls", 4)]:
        for kosul, c in [("ortak", bs), ("tek", ~bany)]:
            m = X[k].values.astype(bool) & c & X.y4.notna().values; ev = events(m, H); t = X.index[ev]; r = np.exp(X.y4.values[ev]) - 1
            for per, s in [("2020–23", (t >= A20) & (t < A24)), ("2024+", t >= A24)]:
                if s.any(): havuz.append(dict(sinyal=AD[k], kosul=kosul, donem=per, n=int(s.sum()), k=int((r[s] > 0).sum()), g=float(r[s].sum())))
            s24 = t >= A24; r24 = r[s24]; t24 = t[s24]; md = t24[len(t24) // 2] if len(t24) else None; s20 = (t >= A20) & (t < A24)
            wk = max(1, (X.index[-1] - max(A24, X.index[0])).days / 7)
            rows.append(dict(sym=sym, sinyal=k, kosul=kosul, n=int(s24.sum()), haftada=s24.sum() / wk, isabet=(r24 > 0).mean() * 100 if len(r24) else np.nan,
                             y1=(r24[t24 < md] > 0).mean() * 100 if len(r24) else np.nan, y2=(r24[t24 >= md] > 0).mean() * 100 if len(r24) else np.nan,
                             n20=int(s20.sum()), isabet20=(r[s20] > 0).mean() * 100 if s20.any() else np.nan, brut=r24.mean() * 100 if len(r24) else np.nan))
D = pd.DataFrame(rows)
D["ac"] = (D.n >= 50) & (D.isabet >= 58) & (D.y1 >= 55) & (D.y2 >= 55) & ((D.n20 < 30) | (D.isabet20 >= 55))
P = pd.DataFrame(havuz).groupby(["sinyal", "kosul", "donem"]).sum(); P["isabet %"] = (100 * P.k / P.n).round(1); P["brüt %"] = (100 * P.g / P.n).round(3)
yaz(f"# 🤝 BTC + coin ortak sinyal denetimi — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}")
yaz("Tüm coin'ler birlikte (ortak = BTC 4s Çok güçlü ↑ aynı saatte · tek = BTC'de hiç sinyal yok):\n```\n" + P.drop(columns=["k", "g"]).to_string() + "\n```")
os.makedirs("durum", exist_ok=True); ACIK = {}
for kos, ad, dosya in [("ortak", "🤝 BTC ile ortak (BTC 4s Çok güçlü ↑ aynı saatte)", "ortak_acik.csv"), ("tek", "🔇 BTC sessizken (BTC'de ⭐ / 4s ÇG↑ / A yok)", "tek_acik.csv")]:
    Dk = D[D.kosul == kos]; T = Dk.assign(coin=Dk.sym.str.replace("USDT", ""), sinyal_=Dk.sinyal.map(AD)).set_index(["coin", "sinyal_"])[["n", "haftada", "isabet", "y1", "y2", "n20", "isabet20", "brut", "ac"]]
    yaz(f"\n### {ad} — coin bazında (2024+; kural: ≥ %58, ≥ 50 sinyal, iki yarıda ≥ %55, 2020–23'te ≥ 30 sinyal varsa orada da ≥ %55)\n```\n" + T.round(1).sort_values("isabet", ascending=False).to_string() + "\n```")
    A_ = Dk[Dk.ac]; ACIK[kos] = A_; yaz(f"Açık ({len(A_)}): " + (", ".join(f"{s.replace('USDT','')} {AD[k]}" for s, k in zip(A_.sym, A_.sinyal)) or "yok"))
    A_[["sym", "sinyal", "n", "haftada", "isabet", "isabet20"]].to_csv(f"durum/{dosya}", index=False)
A, B_ = ACIK["ortak"], ACIK["tek"]
open("durum/ortak_rapor.md", "w").write("\n".join(L) + "\n")
if os.environ.get("TELEGRAM_TOKEN"):
    tg_send(f"🤝🧠 Coin sinyal denetimi tamamlandı.\n🤝 BTC ile ortak açık: {len(A)} · 🔇 BTC sessizken açık: {len(B_)}\n"
            + "\n".join(f"• 🤝 {s.replace('USDT','')} {AD[k]}: %{i:.0f} (haftada ~{w:.1f})" for s, k, i, w in zip(A.sym, A.sinyal, A.isabet, A.haftada))
            + ("\n" if len(B_) else "") + "\n".join(f"• 🔇 {s.replace('USDT','')} {AD[k]}: %{i:.0f} (haftada ~{w:.1f})" for s, k, i, w in zip(B_.sym, B_.sinyal, B_.isabet, B_.haftada)))
