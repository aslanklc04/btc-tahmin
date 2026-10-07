# cb_kontrol.py — COINBASE PRİMİ sağlamlık kontrolleri (bosluklar2.py'de üç dönemde de tutan tek boşluk)
# Prim = log(Coinbase BTC-USD / Binance BTCUSDT), son 30 güne göre z. Olay: z ≥ +2 → AL, z ≤ −2 → SAT (ilk saat, 24 saat tekrar yok, giriş 1 saat sonra).
# 1) Eşik (1,5 / 2 / 2,5) ve süre (4 / 8 / 24 / 72 saat) değişince sonuç duruyor mu (seçilmiş tek ayar değil mi)?
# 2) Zaman kaydırma: olay deseni rastgele (≥ 30 gün) kaydırılır, 1000 kez → gerçek fazla, kaydırılmışların yüzde kaçından iyi?
# 3) Momentum mu? Olay saatlerini, BTC'nin son 24 saatlik getirisi AYNI ondalık dilimde olan olaysız saatlerle karşılaştır.
# 4) Yıl yıl · 5) Altcoin'ler: aynı BTC olayında coin'lerin 24 saati · 6) Para: yalnız AL, yalnız SAT, ikisi — yıllık getiri ve en büyük düşüş.
import time, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
src = open("bosluklar2.py").read(); exec(src[src.index("UA = "):src.index("def upbit_1h")])          # kl() ve coinbase_1h() aynen
COINS = ["ETHUSDT", "ADAUSDT", "BNBUSDT", "DOGEUSDT", "DOTUSDT", "LINKUSDT", "NEARUSDT", "OPUSDT", "SHIBUSDT", "XRPUSDT", "SOLUSDT"]
with ThreadPoolExecutor(12) as ex:
    fb = ex.submit(kl, "BTCUSDT"); fc = ex.submit(coinbase_1h); fk = {s: ex.submit(kl, s) for s in COINS}
    BTC, CB = fb.result(), fc.result(); K = {s: f.result() for s, f in fk.items()}
idx = pd.date_range(BTC.index[0], BTC.index[-1], freq="1h", tz="UTC"); c = BTC.reindex(idx).ffill(limit=3)
p = np.log(CB.reindex(idx) / c); z = (p - p.rolling(720, min_periods=168).mean()) / (p.rolling(720, min_periods=168).std() + 1e-12)
A24, A26 = pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC"); LMT = 0.0002
DON = {"≤2023": (idx[0], A24), "2024+": (A24, idx[-1]), "2026": (A26, idx[-1])}
def fwd(pr, H): return np.log(pr.shift(-(H + 1)) / pr.shift(-1))
yaz(f"# 🔎 Coinbase primi — sağlamlık kontrolleri — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nVeri: {idx[0]:%Y-%m} → {idx[-1]:%Y-%m-%d %H:%M} · prim ortalama {p.mean()*1e4:+.1f} bp, sapma {p.std()*1e4:.1f} bp\n")
def olaylar(esik, yon, H):
    m = ((z >= esik) if yon > 0 else (z <= -esik)).fillna(False).values; return idx[events(m, H)]
# 1) eşik × süre
rows = []
for H in (4, 8, 24, 72):
    y = fwd(c, H)
    for esik in (1.5, 2.0, 2.5):
        for yon, ad in ((1, "z ≥ +e → AL"), (-1, "z ≤ −e → SAT")):
            ev = olaylar(esik, yon, H); r = dict(sure=f"{H}s", esik=esik, olay=ad)
            for pn, (a, b) in DON.items():
                m = (idx >= a) & (idx < b); base = y[m].mean(); e = ev[(ev >= a) & (ev < b)]; ye = y.reindex(e).dropna()
                r[f"{pn} n"] = len(ye); r[f"{pn} fazla%"] = 100 * yon * (ye.mean() - base) if len(ye) else np.nan
            rows.append(r)
yaz("## 1) Eşik ve süre değişince (fazla = olay yönünde, rastgele saate göre fark, %)\n```\n" + pd.DataFrame(rows).set_index(["sure", "esik", "olay"]).round(2).to_string() + "\n```")
# 2) zaman kaydırma (24 saat, eşik 2)
y24 = fwd(c, 24); rg = np.random.default_rng(0); out = []
for yon, ad in ((1, "AL (z ≥ +2)"), (-1, "SAT (z ≤ −2)")):
    m0 = ((z >= 2) if yon > 0 else (z <= -2)).fillna(False).values
    for pn, (a, b) in DON.items():
        w = np.where((idx >= a) & (idx < b))[0]; mm = m0[w]; yy = y24.values[w]; base = np.nanmean(yy)
        def fz(mk): e = events(mk, 24); v = yy[e]; v = v[np.isfinite(v)]; return yon * (v.mean() - base) if len(v) else np.nan
        real = fz(mm); sh = np.array([fz(np.roll(mm, int(rg.integers(720, len(w) - 720)))) for _ in range(1000)]) if len(w) > 2000 else np.array([np.nan])
        out.append(dict(olay=ad, donem=pn, gercek=100 * real, kaydirilmis_ort=100 * np.nanmean(sh), yuzde95=100 * np.nanquantile(sh, .95), daha_iyi=100 * np.nanmean(sh < real)))
yaz("## 2) Zaman kaydırma testi (24 saat, eşik 2) — 'daha_iyi' = gerçek sonucun kaydırılmışlardan iyi olduğu oran (%)\n```\n" + pd.DataFrame(out).set_index(["olay", "donem"]).round(2).to_string() + "\n```")
# 3) momentum kontrolü
r24 = np.log(c / c.shift(24)); qs = r24[idx < A24].quantile(np.linspace(0, 1, 11)).to_numpy(copy=True); qs[0], qs[-1] = -np.inf, np.inf
dil = pd.cut(r24, qs, labels=False); out = []
for yon, ad in ((1, "AL (z ≥ +2)"), (-1, "SAT (z ≤ −2)")):
    ev = olaylar(2.0, yon, 24); evs = set(ev)
    for pn, (a, b) in DON.items():
        e = [t for t in ev if a <= t < b and np.isfinite(y24.get(t, np.nan)) and np.isfinite(dil.get(t, np.nan))]
        if not e: continue
        m = (idx >= a) & (idx < b) & ~idx.isin(ev); ref = pd.DataFrame({"y": y24[m], "d": dil[m]}).dropna().groupby("d").y.mean()
        eş = np.mean([y24[t] - ref.get(dil[t], np.nan) for t in e]); ham = np.mean([y24[t] for t in e]) - y24[(idx >= a) & (idx < b)].mean()
        out.append(dict(olay=ad, donem=pn, n=len(e), ham_fazla=100 * yon * ham, momentum_esli_fazla=100 * yon * eş, olay_aninda_ort_r24=100 * np.mean([r24[t] for t in e])))
yaz("## 3) Momentum kontrolü — olay, BTC'nin son 24 saatlik getirisi aynı dilimdeki olaysız saatlerle karşılaştırılır (%)\n```\n" + pd.DataFrame(out).set_index(["olay", "donem"]).round(2).to_string() + "\n```")
# 4) yıl yıl
out = []
for yon, ad in ((1, "AL"), (-1, "SAT")):
    ev = olaylar(2.0, yon, 24); ye = y24.reindex(ev).dropna(); base = y24.groupby(idx.year).mean()
    for yr, g in ye.groupby(ye.index.year): out.append(dict(olay=ad, yil=yr, n=len(g), fazla=100 * yon * (g.mean() - base.get(yr, np.nan)), isabet=100 * ((yon * g) > 0).mean()))
yaz("## 4) Yıl yıl (24 saat, eşik 2): fazla % ve olay yönünde isabet\n```\n" + pd.DataFrame(out).pivot_table(index="yil", columns="olay", values=["n", "fazla", "isabet"]).round(2).to_string() + "\n```")
# 5) altcoin'ler
out = []
for s, pr in K.items():
    if pr is None: continue
    cc = pr.reindex(idx).ffill(limit=3); yc = fwd(cc, 24); r = dict(coin=s[:-4])
    for yon, ad in ((1, "AL"), (-1, "SAT")):
        ev = olaylar(2.0, yon, 24)
        for pn, (a, b) in (("≤2023", DON["≤2023"]), ("2024+", DON["2024+"])):
            m = (idx >= a) & (idx < b); e = ev[(ev >= a) & (ev < b)]; ye = yc.reindex(e).dropna(); r[f"{ad} {pn}"] = 100 * yon * (ye.mean() - yc[m].mean()) if len(ye) > 5 else np.nan
    out.append(r)
yaz("## 5) Aynı BTC olayında altcoin'lerin sonraki 24 saati (olay yönünde fazla %)\n```\n" + pd.DataFrame(out).set_index("coin").round(2).to_string() + "\n```")
# 6) para: BTC, limit komisyon
out = []
for ad, yons in (("yalnız AL", [1]), ("yalnız SAT (vadeli)", [-1]), ("ikisi", [1, -1])):
    T = pd.concat([pd.DataFrame({"t": olaylar(2.0, yo, 24), "yon": yo}) for yo in yons]).sort_values("t"); T["g"] = T.yon * y24.reindex(T.t).values; T = T.dropna(); T["net"] = np.exp(T.g) - 1 - 2 * LMT
    for pn, (a, b) in DON.items():
        x = T[(T.t >= a) & (T.t < b)]
        if len(x) < 5: continue
        e = np.cumprod(1 + x.net.values); yrs = (b - a).days / 365.25; lo, _ = wboot(x.net.values, x.t.values)
        out.append(dict(strateji=ad, donem=pn, islem=len(x), haftada=len(x) / ((b - a).days / 7), isabet=100 * (x.g > 0).mean(), net=100 * x.net.mean(), alt=100 * lo, yillik=100 * (e[-1] ** (1 / yrs) - 1), maxDD=100 * (e / np.maximum.accumulate(np.r_[1, e])[1:] - 1).min()))
yaz("## 6) Para testi (BTC, 24 saat tut, limit komisyon %0,02 × 2, giriş olaydan 1 saat sonra)\n```\n" + pd.DataFrame(out).set_index(["strateji", "donem"]).round(2).to_string() + "\n```")
z_now = z.dropna(); yaz(f"\nŞu an: prim {p.dropna().iloc[-1]*1e4:+.1f} bp · z {z_now.iloc[-1]:+.2f} ({z_now.index[-1].tz_convert(DISPLAY_TZ):%d.%m %H:%M})\n_Süre: {time.time()-T0:.0f} sn_")
open("cb_kontrol_sonuc.md", "w").write("\n".join(L) + "\n")
