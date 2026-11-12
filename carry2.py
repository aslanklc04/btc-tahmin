# carry2.py — PROTOKOL_carry2.md → carry2_sonuc.md
import numpy as np, pandas as pd
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
F = pd.read_parquet("yeniliste_fon.parquet"); F["t"] = pd.to_datetime(F.t, utc=True)
CO = ["BTC", "ETH", "SOL", "BNB", "XRP", "DOGE", "ADA", "LINK", "AVAX", "LTC"]
D = F[F.s.isin([c + "USDT" for c in CO])].pivot_table(index=F.t.dt.floor("D"), columns="s", values="fr", aggfunc="sum"); D.columns = [c[:-4] for c in D.columns]; D = D[CO]
D = D[D.index >= "2021-01-01"]; KAP, UC = 1.5, 0.003
ay = lambda s: s.groupby(s.index.tz_convert(None).to_period("M")).sum()
def satir(ad, g):
    m = ay(g); hc = []; ok = True
    for y in range(2021, 2027):
        a = m[m.index.year == y]; v = a.sum() * (12 / len(a)) if y == 2026 and len(a) else a.sum()
        hc.append(f"{100 * v:+.1f}%"); 
        if y >= 2022: ok &= v >= 0.06
    neg = (m[m.index.year >= 2022] < 0).mean(); ok &= neg <= 0.25
    yaz(f"| {ad} | " + " | ".join(hc) + f" | %{100 * neg:.0f} · {100 * m.min():+.2f}% | {'✅' if ok else '❌'} |")
yaz("# 💰 Büyük coin'lerde fonlama geliri (spot al + vadeli sat) — PROTOKOL_carry2.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · Binance gerçek fonlama · sermaye üzerinden yıllık net (sermaye = spot × 1,5) · 2026 ilk 10 aydan yıllığa çevrildi_\n")
yaz("| kural | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 (yıllık) | negatif ay (2022+) · en kötü ay | ≥ %6 her yıl |"); yaz("|---|---|---|---|---|---|---|---|---|")
for c in CO: satir(f"K1 {c}", D[c] / KAP)
sep = D.mean(axis=1); satir("K2 10 coin sepeti", sep / KAP)
aylar = pd.period_range("2021-02", "2026-10", freq="M"); g = pd.Series(0.0, index=D.index); onceki = None; per = D.index.tz_convert(None).to_period("M")
for a in aylar:
    b0 = a.to_timestamp().tz_localize("UTC"); gec = D[(D.index >= b0 - pd.Timedelta(days=30)) & (D.index < b0)].sum(); sec = gec.idxmax(); msk = per == a
    g[msk] = D.loc[msk, sec].values / KAP
    if sec != onceki and msk.any(): g.iloc[np.where(msk)[0][0]] -= UC / KAP
    onceki = sec
satir("K3 aylık dönüş (önceki ay en yüksek)", g)
t7 = sep.rolling(7).mean().shift(1); ic = t7 > 0.0003; g4 = (sep.where(ic, 0.0)) / KAP; g4 -= (ic.astype(int).diff().abs().fillna(0) * UC / 2) / KAP
satir("K4 sepet, yalnız fonlama yüksekken", g4)
yaz(f"\n_K4'te pozisyonda geçen gün oranı: " + " · ".join(f"{y}: %{100 * ic[ic.index.year == y].mean():.0f}" for y in range(2021, 2027)) + "_")
yaz("\n_Karşılaştırma: USDT Earn ~%3–6 (borsa riski var, piyasa riski yok). Bu strateji ek olarak iki bacaklı işlem, teminat yönetimi ve sert yükselişte teminat ekleme gerektirir._")
open("carry2_sonuc.md", "w").write("\n".join(out) + "\n")
