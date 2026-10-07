# ufuk24_rapor.py — ufuk24.py çıktılarını birleştirir: 8 / 24 / 72 saatlik sinyallerin isabeti, sayısı ve komisyon sonrası kârı (canlı sisteme dokunmaz)
# Giriş/çıkış: sinyal saatinin kapanışı (0 s, iyimser) ve 1 saat sonrası (1 s, temkinli; gerçek mesaj :06'da gelir). Komisyon her yön: vadeli %0,05 · limit %0,02.
# ÖNCEDEN SABİT karar: 24 saatlik 'Çok güçlü ↑'. Coin'ler YALNIZ 2020–23 sonucuna göre seçilir (≥ 30 sinyal ve limit-komisyonlu net > 0, 1 s gecikme),
# seçilenlerin 2024+ toplamı: net > 0 ve %90 alt sınır > 0 ise ✅.
import os, glob, time, numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
EX = {os.path.basename(p)[7:-4]: pd.read_pickle(p) for p in glob.glob("art/**/disa24_*USDT.pkl", recursive=True)}
A0, A24 = pd.Timestamp("2020-01-01", tz="UTC"), pd.Timestamp("2024-01-01", tz="UTC"); FEES = {"vadeli %0,05": 0.0005, "limit %0,02": 0.0002}
HS = sorted({int(c[1:]) for X in EX.values() for c in X.columns if c.startswith("S") and c[1:].isdigit()})
yaz(f"# ⏳ Uzun ufuk (8 / 24 / 72 saat) — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nCoin'ler ({len(EX)}): {' '.join(sorted(s[:-4] for s in EX))} · ufuklar: {HS}\n")
rows, auc = [], []
for s, X in EX.items():
    X = X.reindex(pd.date_range(X.index[0], X.index[-1], freq="1h", tz="UTC")); c = X.close.ffill(limit=3).values; n = len(X)
    for H in HS:
        if f"S{H}" not in X: continue
        S, C_, T30, T10 = (X[f"{k}"].values for k in (f"S{H}", f"C{H}", f"T30_{H}", f"T10_{H}"))
        y = np.r_[np.log(c[H:] / c[:-H]), np.full(H, np.nan)]
        ok = np.isfinite(S) & np.isfinite(y); pos = np.where(ok)[0][::H]
        for pn, m in (("2020–23", X.index[pos] < A24), ("2024+", X.index[pos] >= A24)):
            p_ = pos[m]
            if len(p_) > 50 and len(set(y[p_] > 0)) == 2: auc.append(dict(coin=s[:-4], H=H, donem=pn, auc=roc_auc_score(y[p_] > 0, S[p_])))
        for lvl, mk in (("Çok güçlü ↑", (S > 0) & (C_ >= T10)), ("Güçlü ve üstü ↑", (S > 0) & (C_ >= T30))):
            mk = np.nan_to_num(mk).astype(bool) & np.isfinite(T10) & (np.arange(n) + H + 1 < n)
            for i in events(mk, H):
                t = X.index[i]
                if t < A0: continue
                for d in (0, 1):
                    a, b = c[i + d], c[i + H + d]
                    if np.isfinite(a) and np.isfinite(b): rows.append((s[:-4], H, lvl, t, d, b / a - 1))
R = pd.DataFrame(rows, columns=["coin", "H", "lvl", "t", "d", "g"]); AU = pd.DataFrame(auc)
yaz(f"Olay sayısı: {len(R[R.d == 0]):,} · {time.time()-T0:.0f} sn\n")
yaz("## Yön bilgisi (AUC, 0,50 = yazı tura) — coin × ufuk\n```\n" + AU.pivot_table(index="coin", columns=["H", "donem"], values="auc").round(3).to_string() + "\n```")
yaz("Ortalama AUC: " + " · ".join(f"{H}s ≤2023 {AU[(AU.H == H) & (AU.donem == '2020–23')].auc.mean():.3f} / 2024+ {AU[(AU.H == H) & (AU.donem == '2024+')].auc.mean():.3f}" for H in HS))
END = R.t.max(); DON = {"2020–23": (A0, A24), "2024+": (A24, END)}
def ozet(x, a, b):
    wk = (b - a).days / 7; r = dict(sinyal=len(x), haftada=len(x) / wk, isabet=100 * (x.g > 0).mean(), brut=100 * x.g.mean())
    for fn, fee in FEES.items():
        net = x.g.values - 2 * fee; lo, hi = wboot(net, x.t.values) if len(x) >= 5 else (np.nan, np.nan); r[f"net {fn}"] = 100 * net.mean(); r[f"alt {fn}"] = 100 * lo
    return r
yaz("\n## Tüm coin'ler toplamı (BTC dahil) — ufuk × seviye")
for d in (1, 0):
    out = []
    for (H, lvl), g in R[R.d == d].groupby(["H", "lvl"]):
        for pn, (a, b) in DON.items():
            x = g[(g.t >= a) & (g.t < b)]
            if len(x) >= 20: out.append(dict(ufuk=f"{H} saat", seviye=lvl, donem=pn, **ozet(x, a, b)))
    yaz(f"### Giriş {'1 saat gecikmeli (temkinli)' if d else 'sinyal saati kapanışı (iyimser)'}\n```\n" + pd.DataFrame(out).set_index(["ufuk", "seviye", "donem"]).round(3).to_string() + "\n```")
yaz("\n## Coin coin: 24 saat 'Çok güçlü ↑' (1 saat gecikme, limit komisyon)")
cc = []
for coin, g in R[(R.H == 24) & (R.lvl == "Çok güçlü ↑") & (R.d == 1)].groupby("coin"):
    r = dict(coin=coin)
    for pn, (a, b) in DON.items():
        x = g[(g.t >= a) & (g.t < b)]; r[f"{pn} sinyal"] = len(x)
        if len(x): r[f"{pn} isabet"] = 100 * (x.g > 0).mean(); r[f"{pn} net"] = 100 * (x.g.mean() - 2 * FEES["limit %0,02"])
    cc.append(r)
CC = pd.DataFrame(cc).set_index("coin"); yaz("```\n" + CC.round(2).to_string() + "\n```")
# ---- önceden sabit karar ----
sec = [c_ for c_, r in CC.iterrows() if r.get("2020–23 sinyal", 0) >= 30 and r.get("2020–23 net", -1) > 0]
yaz(f"\n## Karar (önceden sabit): 24 saat 'Çok güçlü ↑' · coin'ler yalnız 2020–23'e göre seçildi → 2024+")
yaz(f"Seçilen coin'ler ({len(sec)}): {' '.join(sec) or 'yok'}")
if sec:
    x = R[(R.H == 24) & (R.lvl == "Çok güçlü ↑") & (R.d == 1) & R.coin.isin(sec) & (R.t >= A24)]
    if len(x) >= 20:
        r = ozet(x, A24, END); ok = r["net limit %0,02"] > 0 and r["alt limit %0,02"] > 0; h1 = x[x.t < x.t.quantile(0.5)]; h2 = x[x.t >= x.t.quantile(0.5)]
        yaz(f"{'✅' if ok else '❌'} 2024+: {r['sinyal']} sinyal · haftada {r['haftada']:.1f} · isabet %{r['isabet']:.1f} (yarılar %{100*(h1.g>0).mean():.0f} / %{100*(h2.g>0).mean():.0f}) · "
            f"brüt %{r['brut']:.3f} · net limit %{r['net limit %0,02']:.3f} (alt %{r['alt limit %0,02']:.3f}) · net vadeli %{r['net vadeli %0,05']:.3f}")
    else: yaz("2024+ için yeterli sinyal yok.")
for H in [h for h in HS if h != 24]:
    s2 = []
    for coin, g in R[(R.H == H) & (R.lvl == "Çok güçlü ↑") & (R.d == 1)].groupby("coin"):
        x1 = g[(g.t >= A0) & (g.t < A24)]
        if len(x1) >= 30 and x1.g.mean() - 2 * FEES["limit %0,02"] > 0: s2.append(coin)
    x = R[(R.H == H) & (R.lvl == "Çok güçlü ↑") & (R.d == 1) & R.coin.isin(s2) & (R.t >= A24)]
    if len(x) >= 20:
        r = ozet(x, A24, END); yaz(f"Karşılaştırma — {H} saat, aynı yöntemle seçilen {len(s2)} coin, 2024+: haftada {r['haftada']:.1f} · isabet %{r['isabet']:.1f} · net limit %{r['net limit %0,02']:.3f} (alt %{r['alt limit %0,02']:.3f})")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn · brüt/net % = işlem başı · alt = haftalık blok bootstrap %90 alt sınırı · veri sonu {END:%Y-%m-%d %H:%M} UTC_")
open("ufuk24_sonuc.md", "w").write("\n".join(L) + "\n")
