# dusus.py — MODELLER DÜŞÜŞÜ NE KADAR İYİ GÖRÜYOR? (yalnız test; canlıya dokunmaz)
# Modeller zaten iki yönlü (fiyat H saat sonra yukarı mı aşağı mı): S > 0 yukarı, S < 0 aşağı; güç |S| son 30 güne göre (Çok güçlü = en güçlü %10, Güçlü = %30).
# Canlıda coin'lerde yalnız ↑ tarafı gönderiliyor. Burada aynı sinyallerin AYNA ↓ (kısa pozisyon) tarafı ölçülür:
#   1/4/8 saat Çok güçlü ve Güçlü ↓ · ⭐↓ (4 s ve 8 s birlikte Çok güçlü ↓) · A↓ (üç ufkun ortalama yüzdeliği ≤ 0,15) · 24 saat Çok güçlü ↓ (ufuk24 modeli).
# Kısa pozisyon getirisi = fiyat düşüşü; komisyon limit %0,02 × 2 (fonlama dahil değil: çoğu zaman pozitif fonlama kısaya ödenir, 4–8 saatte çok küçük).
# ÖNCEDEN KARAR (canlıdaki ↑ öz-denetimiyle AYNI): bir ↓ sinyali bir coin için aday sayılır ancak — 2024+ (ya da coin'in test başlangıcından beri) isabet ≥ %58, ≥ 50 sinyal,
#   dönemin iki yarısında da ≥ %55 · ek olarak 2024+ komisyon sonrası net > 0 ve 2026'da net ≥ 0.
import os, glob, numpy as np, pandas as pd
from ortak import *
L = []
def yaz(s=""): print(s, flush=True); L.append(s)
f = lambda p: glob.glob(p, recursive=True)
SF = {os.path.basename(p)[3:-4]: pd.read_pickle(p).astype("float64") for p in f("art/**/sf_*USDT.pkl")}
E24 = {os.path.basename(p)[7:-4]: pd.read_pickle(p).astype("float64") for p in f("art2/**/disa24_*USDT.pkl")}
LMT = 0.0002; A24, A26 = pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")
DON = (("≤2023", lambda i: i < A24), ("2024+", lambda i: i >= A24), ("2026", lambda i: i >= A26))
yaz(f"# 🔻 Modeller düşüşü ne kadar iyi görüyor? — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nModel çıktısı gelen: {len(SF)} coin ({', '.join(sorted(s[:-4] for s in SF))}) · 24 saat modeli: {len(E24)} coin\n")
OL = []                                                                                                # (coin, sinyal, yön, t, r)
def ekle(coin, sinyal, sg, idx, ev, ylog=None, rbasit=None):
    r = (np.exp(ylog[ev]) - 1) if ylog is not None else rbasit[ev]
    for t, x in zip(idx[ev], sg * r):
        if np.isfinite(x): OL.append((coin, sinyal, sg, t, x))
for sym, X in SF.items():
    nm = sym[:-4]; C_ = {}
    for H in (1, 4, 8):
        S, C, T10, T30, y = X[f"S{H}"], X[f"C{H}"], X[f"T10{H}"], X[f"T30{H}"], X[f"y{H}"]
        for sg in (1, -1):
            for lad, lm in (("Çok güçlü", C >= T10), ("Güçlü", (C >= T30) & (C < T10))):
                m = ((np.sign(S) == sg) & lm & T10.notna() & y.notna()).values; ekle(nm, f"{H} s {lad}", sg, X.index, events(m, H), ylog=y.values)
    for sg in (1, -1):
        st = ((np.sign(X.S4) == sg) & (X.C4 >= X.T104) & (np.sign(X.S8) == sg) & (X.C8 >= X.T108) & X.y4.notna() & X.y8.notna()).values; ev = events(st, 8)
        ekle(nm, "⭐ (4 s sonucu)", sg, X.index, ev, ylog=X.y4.values); ekle(nm, "⭐ (8 s sonucu)", sg, X.index, ev, ylog=X.y8.values)
        a = ((X.am >= 0.85) if sg > 0 else (X.am <= 0.15)) & X.y4.notna(); ekle(nm, "A sınıfı (4 s)", sg, X.index, events(a.values, 4), ylog=X.y4.values)
for sym, X in E24.items():
    nm = sym[:-4]; X = X.reindex(pd.date_range(X.index[0], X.index[-1], freq="1h", tz="UTC")); c = X.close.ffill(limit=3).values; n = len(X)
    r24 = np.full(n, np.nan); r24[:n - 24] = c[24:] / c[:n - 24] - 1
    for sg in (1, -1):
        m = np.nan_to_num(((np.sign(X.S24) == sg) & (X.C24 >= X.T10_24)).values).astype(bool) & X.T10_24.notna().values & np.isfinite(r24); ekle(nm, "24 s Çok güçlü", sg, X.index, events(m, 24), rbasit=r24)
E = pd.DataFrame(OL, columns=["coin", "sinyal", "sg", "t", "r"]); E["net"] = E.r - 2 * LMT; E["yon"] = E.sg.map({1: "↑", -1: "↓"}); tt = pd.DatetimeIndex(E.t)
SIRA = ["1 s Çok güçlü", "1 s Güçlü", "4 s Çok güçlü", "4 s Güçlü", "8 s Çok güçlü", "8 s Güçlü", "⭐ (4 s sonucu)", "⭐ (8 s sonucu)", "A sınıfı (4 s)", "24 s Çok güçlü"]
# ---- 1) tüm coin'ler birlikte: ↑ ve ↓ yan yana ----
yaz("## 1) Tüm coin'ler birlikte — yükseliş (↑) ve düşüş (↓) tahminleri yan yana\n_hücre: isabet % · işlem başı net % (komisyon sonrası) · işlem sayısı_")
T = {}
for (sn, yn), g in E.groupby(["sinyal", "yon"]):
    gt = pd.DatetimeIndex(g.t); T[(sn, yn)] = {pn: (f"%{100*(g.r[fd(gt)]>0).mean():.0f} · {100*g.net[fd(gt)].mean():+.2f} · {int(fd(gt).sum())}" if fd(gt).sum() >= 10 else "—") for pn, fd in DON}
T = pd.DataFrame(T).T; T.index.names = ["sinyal", "yön"]; T = T.reindex([(s, y) for s in SIRA for y in ("↑", "↓")]).dropna(how="all")
yaz("```\n" + T.to_string() + "\n```")
# ---- 2) yıl yıl (4 s Çok güçlü, tüm coin'ler): piyasa yönü etkisi ----
yaz("\n## 2) Yıl yıl — 4 saat Çok güçlü, tüm coin'ler (isabet % · net %) ve BTC'nin o yılki değişimi")
Y = []
B = SF.get("BTCUSDT")
for yr in range(2020, pd.Timestamp.now().year + 1):
    row = {"yıl": yr}
    for yn in ("↑", "↓"):
        g = E[(E.sinyal == "4 s Çok güçlü") & (E.yon == yn) & (tt.year == yr)]; row[yn] = f"%{100*(g.r>0).mean():.0f} · {100*g.net.mean():+.2f} ({len(g)})" if len(g) else "—"
    if B is not None:
        p = np.exp(B.y1.fillna(0)[B.index.year == yr].sum()) - 1 if "y1" in B else np.nan; row["BTC yıl içi"] = f"{100*p:+.0f}%"
    Y.append(row)
yaz("```\n" + pd.DataFrame(Y).to_string(index=False) + "\n```")
# ---- 3) coin coin, canlıdaki öz-denetimle ----
def denet(g, ev0):
    g = g[pd.DatetimeIndex(g.t) >= ev0].sort_values("t"); n = len(g)
    if n == 0: return dict(n=0, isabet=np.nan, y1=np.nan, y2=np.nan, net=np.nan, net26=np.nan, ok=False)
    h = n // 2; a1, a2 = g.r.iloc[:h], g.r.iloc[h:]; g26 = g[pd.DatetimeIndex(g.t) >= A26]
    d = dict(n=n, isabet=100 * (g.r > 0).mean(), y1=100 * (a1 > 0).mean() if len(a1) else np.nan, y2=100 * (a2 > 0).mean(), net=100 * g.net.mean(), net26=100 * g26.net.mean() if len(g26) else np.nan)
    d["ok"] = bool(n >= 50 and d["isabet"] >= 58 and d["y1"] >= 55 and d["y2"] >= 55 and d["net"] > 0 and (not np.isfinite(d["net26"]) or d["net26"] >= 0)); return d
DEN = []
for coin, gc in E.groupby("coin"):
    ev0 = max(A24, pd.DatetimeIndex(gc.t).min())
    for (sn, yn), g in gc.groupby(["sinyal", "yon"]):
        d = denet(g, ev0); DEN.append(dict(coin=coin, sinyal=sn, yon=yn, **d))
DEN = pd.DataFrame(DEN); DEN.to_csv("dusus_tum.csv", index=False)
ANA = ["4 s Çok güçlü", "⭐ (4 s sonucu)", "A sınıfı (4 s)", "1 s Çok güçlü", "8 s Çok güçlü", "24 s Çok güçlü"]
yaz("\n## 3) Coin coin — 2024+ isabet % (işlem) · ✅ = canlıdaki öz-denetimi geçer (isabet ≥ %58, ≥ 50 işlem, iki yarı ≥ %55) + net > 0, 2026 net ≥ 0")
P_ = {}
for _, r in DEN[DEN.sinyal.isin(ANA)].iterrows():
    P_.setdefault(r.coin, {})[f"{r.sinyal.replace(' (4 s sonucu)', '').replace(' (4 s)', '')} {r.yon}"] = (f"{'✅' if r.ok else ''}%{r.isabet:.0f} ({int(r.n)})" if r.n else "—")
cols = [f"{s.replace(' (4 s sonucu)', '').replace(' (4 s)', '')} {y}" for s in ANA for y in ("↑", "↓")]
yaz("```\n" + pd.DataFrame(P_).T.reindex(columns=cols).to_string() + "\n```")
yaz("\n### Öz-denetimi geçen sayısı (coin × sinyal)\n```\n" + DEN.groupby(["sinyal", "yon"]).ok.sum().unstack().reindex(SIRA).dropna(how="all").astype(int).to_string() + "\n```")
G = DEN[(DEN.yon == "↓") & DEN.ok].sort_values("net", ascending=False)
yaz("\n## 4) Önceden yazılı karar — geçen ↓ (kısa) sinyalleri\n" + ("```\n" + G[["coin", "sinyal", "n", "isabet", "y1", "y2", "net", "net26"]].round(2).to_string(index=False) + "\n```" if len(G) else "_yok_"))
Gu = DEN[(DEN.yon == "↑") & DEN.ok]
yaz(f"\nKarşılaştırma: aynı kurallarla geçen ↑ sinyal sayısı {len(Gu)} · ↓ {len(G)} (toplam {len(DEN[DEN.yon=='↓'])} ↓ adayı)")
open("dusus_sonuc.md", "w").write("\n".join(L) + "\n")
