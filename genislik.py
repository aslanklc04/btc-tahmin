# genislik.py — "PİYASA GENİŞLİĞİ" örüntüsü: aynı saatte KAÇ coin güçlü sinyal veriyor? (kullanıcının 🤝 bulgusunun genellemesi)
# H1: Coin sinyali, aynı saatte çok sayıda coin de sinyal verirken daha mı isabetli? (BTC güçlü / sessiz ayrımıyla)
# H2: Çok sayıda coin aynı anda güçlüyken BTC'nin kendisi 4 saatte yükseliyor mu? (yeni BTC sinyali adayı)
# Seçim 2020–23, hüküm 2024+. Sonuç: 4 saat sonra (coin'in / BTC'nin kendi fiyatı).
import glob, os, numpy as np, pandas as pd
from ortak import *
L = []
def yaz(s=""): print(s, flush=True); L.append(s)
f = lambda p: glob.glob(f"art/**/{p}", recursive=True)
EX = {os.path.basename(p)[5:-4]: pd.read_pickle(p) for p in f("disa_*USDT.pkl")}; B = EX.pop("BTCUSDT"); S_ = sorted(EX)
idx = B.index; A20, A24 = pd.Timestamp("2020-01-01", tz="UTC"), pd.Timestamp("2024-01-01", tz="UTC")
SIGM = pd.DataFrame({s: (EX[s][["star", "u4", "acls"]].fillna(False).astype(bool).any(axis=1)).reindex(idx) for s in S_})   # coin güçlü mü (NaN = verisi yok)
VAR = pd.DataFrame({s: EX[s].y4.reindex(idx).notna() | EX[s].u4.reindex(idx).notna() for s in S_}); N = SIGM.fillna(False).sum(axis=1); M_ = VAR.sum(axis=1)
oran = N / M_.replace(0, np.nan)
bstr = B.u4.fillna(False).astype(bool); bany = (B.star.fillna(False) | B.u4.fillna(False) | B.acls.fillna(False)).astype(bool)
def kova(n): return pd.cut(n, [-1, 0, 1, 3, 6, 100], labels=["0", "1", "2–3", "4–6", "7+"])
yaz(f"# 🌊 Piyasa genişliği — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n19 coin · her saatte güçlü sinyal (⭐/4s ÇG↑/A) veren coin sayısı\n")
# ---- H1: coin sinyali isabeti, genişlik kovasına göre ----
rows = []
for s in S_:
    X = EX[s]; m = X[["star", "u4", "acls"]].fillna(False).astype(bool).any(axis=1).values & X.y4.notna().values; ev = events(m, 4); t = X.index[ev]
    r = np.exp(X.y4.values[ev]) - 1; n_ = N.reindex(t).values - 1                                  # kendisi hariç kaç coin
    rows.append(pd.DataFrame(dict(t=t, coin=s, r=r, digerleri=n_, btc=np.where(bstr.reindex(t).fillna(False), "BTC 4s ÇG↑", np.where(bany.reindex(t).fillna(False), "BTC diğer sinyal", "BTC sessiz")))))
D = pd.concat(rows); D["donem"] = np.where(D.t < A24, "2020–23", "2024+"); D = D[D.t >= A20]; D["diğer coin"] = kova(D.digerleri)
T = D.groupby(["donem", "btc", "diğer coin"], observed=True).agg(n=("r", "size"), isabet=("r", lambda v: 100 * (v > 0).mean()), brut=("r", lambda v: 100 * v.mean())).round(2)
yaz("## H1) Coin sinyalinin isabeti — aynı saatte kaç BAŞKA coin de güçlü?\n```\n" + T.unstack("donem").to_string() + "\n```")
# ---- H2: genişlik → BTC'nin 4 saatlik getirisi ----
yb = np.exp(B.y4) - 1; G = pd.DataFrame({"N": N, "oran": oran, "y": yb, "bstr": bstr, "bany": bany}).dropna(subset=["y"]); G = G[G.index >= A20]
rows = []
for esik in [3, 5, 7, 9]:
    for kos, mm in [("BTC sessiz", ~G.bany), ("tümü", pd.Series(True, index=G.index))]:
        m = (G.N >= esik) & mm; ev = events(m.values, 4); x = G.iloc[ev]
        for per, sel in [("2020–23", x.index < A24), ("2024+", x.index >= A24)]:
            xx = x[sel]; wk = ((G.index[-1] if per == "2024+" else A24) - (A24 if per == "2024+" else A20)).days / 7
            rows.append(dict(kural=f"≥{esik} coin güçlü", btc=kos, donem=per, n=len(xx), haftada=len(xx) / wk, isabet=100 * (xx.y > 0).mean() if len(xx) else np.nan, brut=100 * xx.y.mean() if len(xx) else np.nan))
base = {per: 100 * (G.y[(G.index < A24) if per == "2020–23" else (G.index >= A24)] > 0).mean() for per in ("2020–23", "2024+")}
H2 = pd.DataFrame(rows).set_index(["kural", "btc", "donem"]).unstack("donem").round(2)
yaz(f"\n## H2) Çok coin aynı anda güçlüyken BTC 4 saat sonra (taban: rastgele saat 2020–23 %{base['2020–23']:.1f} · 2024+ %{base['2024+']:.1f})\n```\n" + H2.to_string() + "\n```")
open("genislik_sonuc.md", "w").write("\n".join(L) + "\n")
