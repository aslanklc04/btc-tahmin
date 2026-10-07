# ufuk24_kontrol.py — 24 saatlik sonucun sağlamlık kontrolleri (karar değişmez; yalnız "şans mı / piyasa yönü mü?" sorusu)
# 1) Aynı coin'lerde rastgele saatte almanın getirisi (taban) · 2) Zaman kaydırma testi: sinyal deseni bütün coin'lerde AYNI miktarda kaydırılır
#    (coin'ler arası kümelenme ve sinyal sıklığı korunur), 1000 kez → gerçek sonuç kaymışların yüzde kaçından iyi? · 3) Yıl yıl · 4) Kâr birkaç haftadan mı geliyor?
# 5) Gerçekçi portföy: her coin'e eşit pay (10 coin → %10), pay yalnız o coin'in sinyalinde 24 saat piyasada; yıllık getiri ve en büyük düşüş · al-tut ile karşılaştırma
import os, glob, time, numpy as np, pandas as pd
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
EX = {os.path.basename(p)[7:-4][:-4]: pd.read_pickle(p) for p in glob.glob("art/**/disa24_*USDT.pkl", recursive=True)}
A0, A24 = pd.Timestamp("2020-01-01", tz="UTC"), pd.Timestamp("2024-01-01", tz="UTC"); FEE = 0.0002; D_ = 1
yaz(f"# 🔎 Uzun ufuk — sağlamlık kontrolleri — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n")
def hazirla(H):
    out = {}
    for s, X in EX.items():
        if f"S{H}" not in X: continue
        X = X.reindex(pd.date_range(X.index[0], X.index[-1], freq="1h", tz="UTC")); c = X.close.ffill(limit=3).values; n = len(X)
        S, C_, T10 = X[f"S{H}"].values, X[f"C{H}"].values, X[f"T10_{H}"].values
        mk = np.nan_to_num((S > 0) & (C_ >= T10)).astype(bool) & np.isfinite(T10) & (np.arange(n) + H + D_ < n)
        g = np.full(n, np.nan); g[:n - H - D_] = c[H + D_:] / c[D_:n - H] - 1                   # i'de sinyal → i+1'de al, i+H+1'de sat
        out[s] = dict(idx=X.index, mk=mk, g=g)
    return out
def secim(P, H):
    sec = []
    for s, v in P.items():
        ev = events(v["mk"], H); t = v["idx"][ev]; m = (t >= A0) & (t < A24); r = v["g"][ev][m]; r = r[np.isfinite(r)]
        if len(r) >= 30 and r.mean() - 2 * FEE > 0: sec.append(s)
    return sorted(sec)
for H in (24, 72, 8):
    P = hazirla(H); sec = secim(P, H); yaz(f"## {H} saat 'Çok güçlü ↑' · seçilen coin'ler (yalnız 2020–23'e göre): {' '.join(sec)}")
    G = pd.DatetimeIndex(sorted(set().union(*[set(P[s]["idx"]) for s in sec]))); G = G[G >= A24]
    def toplam(shift=0):
        rs, ts = [], []
        for s in sec:
            v = P[s]; ix = v["idx"]; m24 = ix >= A24; mk = v["mk"].copy()
            if shift:
                w = np.where(m24)[0]; mk[w] = np.roll(mk[w], shift)                          # yalnız 2024+ kısmı kaydırılır
            ev = events(mk, H); ev = ev[ix[ev] >= A24]; r = v["g"][ev]; ok = np.isfinite(r); rs.append(r[ok]); ts.append(ix[ev][ok])
        return np.concatenate(rs), np.concatenate(ts)
    r, ts = toplam(); net = r - 2 * FEE
    taban = np.concatenate([P[s]["g"][(P[s]["idx"] >= A24) & np.isfinite(P[s]["g"])] for s in sec])
    yaz(f"- 2024+ sinyal: {len(r)} · isabet %{100*(r>0).mean():.1f} · brüt %{100*r.mean():.3f} · net (limit) %{100*net.mean():.3f}")
    yaz(f"- Taban (aynı coin'ler, HER saatte al, {H} s tut): isabet %{100*(taban>0).mean():.1f} · brüt %{100*taban.mean():.3f} → sinyalin fazlası %{100*(r.mean()-taban.mean()):.3f} puan")
    rg = np.random.default_rng(0); n24 = min(int((P[s]["idx"] >= A24).sum()) for s in sec); kay = []
    for _ in range(1000):
        sh = int(rg.integers(24 * 30, n24 - 24 * 30)); rr, _t = toplam(sh); kay.append(rr.mean())
    kay = np.array(kay); yaz(f"- Zaman kaydırma testi (1000 kez): gerçek brüt, kaydırılmışların %{100*(kay < r.mean()).mean():.1f}'inden iyi · kaydırılmış ort. %{100*kay.mean():.3f} (%95'lik: %{100*np.quantile(kay, .95):.3f})")
    T = pd.DataFrame({"t": ts, "g": r, "net": net})
    yy = T.groupby(T.t.dt.year).agg(sinyal=("g", "size"), isabet=("g", lambda x: 100 * (x > 0).mean()), net=("net", lambda x: 100 * x.mean()))
    yaz("- Yıl yıl (2024+):  " + " · ".join(f"{y}: {int(a.sinyal)} sinyal, isabet %{a.isabet:.0f}, net %{a.net:.2f}" for y, a in yy.iterrows()))
    TB = pd.concat([pd.DataFrame({"t": P[s]["idx"], "g": P[s]["g"]}) for s in sec]); TB = TB[(TB.t >= A24) & TB.g.notna()]; tby = TB.groupby(TB.t.dt.year).g.agg(["mean", lambda x: (x > 0).mean()])
    yaz("- Yıl yıl TABAN (her saatte al) ve sinyalin fazlası:  " + " · ".join(f"{y}: taban brüt %{100*tby.loc[y, 'mean']:.2f} (isabet %{100*tby.iloc[:, 1].loc[y]:.0f}) → fazla %{100*(T[T.t.dt.year == y].g.mean() - tby.loc[y, 'mean']):.2f}" for y in yy.index))
    q_ = T.t.dt.to_period("Q"); tq = TB.groupby(TB.t.dt.to_period("Q")).g.mean()
    yaz("- Çeyrek çeyrek (sinyal sayısı · isabet · sinyalin tabana göre fazlası):  " + " · ".join(f"{q}: {len(g)} · %{100*(g.g>0).mean():.0f} · {100*(g.g.mean()-tq.get(q, np.nan)):+.2f}" for q, g in T.groupby(q_)))
    wk = T.groupby(T.t.dt.to_period("W")).net.sum().sort_values(ascending=False); top = wk.head(5).sum() / wk.sum() if wk.sum() > 0 else np.nan
    yaz(f"- Kâr dağılımı: {len(wk)} hafta · kârlı hafta %{100*(wk>0).mean():.0f} · en iyi 5 haftanın toplam kârdaki payı %{100*top:.0f}")
    # portföy: coin başına eşit pay, pay yalnız sinyalde piyasada (aynı coin'de işlemler çakışmaz)
    days = pd.date_range(A24.normalize(), T.t.max().normalize() + pd.Timedelta(days=2), freq="1D", tz="UTC"); eqs, bh = [], []
    for s in sec:
        v = P[s]; ix = v["idx"]; mk = v["mk"]; ev = events(mk, H); ev = ev[ix[ev] >= A24]; rr = v["g"][ev] - 2 * FEE; ok = np.isfinite(rr)
        cik = ix[ev][ok] + pd.Timedelta(hours=H + D_); e = pd.Series(np.cumprod(1 + rr[ok]), index=cik)
        eqs.append(e.reindex(days.union(cik)).ffill().fillna(1.0).reindex(days))
        cl = EX[s].close; cl = cl[cl.index >= A24]; bh.append((cl / cl.iloc[0]).reindex(days, method="ffill"))
    E = pd.concat(eqs, axis=1).mean(axis=1); B = pd.concat(bh, axis=1).mean(axis=1); yrs = (days[-1] - days[0]).days / 365.25
    f = lambda e: (100 * ((e.iloc[-1] / e.iloc[0]) ** (1 / yrs) - 1), 100 * (e / e.cummax() - 1).min())
    (ey, ed), (by, bd) = f(E), f(B)
    yaz(f"- Portföy (her coin'e %{100/len(sec):.0f} pay, yalnız sinyalde piyasada, limit komisyon): yıllık %{ey:.1f} · en büyük düşüş %{ed:.1f} · zamanın %{100*len(T)*H/ (len(sec)*(days[-1]-days[0]).total_seconds()/3600):.0f}'inde piyasada")
    yaz(f"- Karşılaştırma — aynı coin'leri eşit al-tut (2024+): yıllık %{by:.1f} · en büyük düşüş %{bd:.1f}\n")
yaz(f"_Süre: {time.time()-T0:.0f} sn · giriş sinyalden 1 saat sonra · komisyon limit %0,02 her yön_")
open("ufuk24_kontrol_sonuc.md", "w").write("\n".join(L) + "\n")
