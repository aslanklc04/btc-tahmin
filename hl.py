# hl.py — PROTOKOL_hl.md: Hyperliquid'de kazanan büyük hesaplarda kalıcılık → hl_sonuc.md
import numpy as np, pandas as pd
from scipy.stats import spearmanr
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
D = pd.read_parquet("hl_seri.parquet").sort_values(["adr", "t"]); M = pd.read_parquet("hl_meta.parquet")
TOL = pd.Timedelta(days=15)
def an(X):
    """X tarihindeki (son gözlem ≤ X, ≤ 15 gün eski) pnl ve av"""
    d = D[D.t <= X].groupby("adr").last(); d = d[X - d.t <= TOL]; return d.pnl, d.av
FS = pd.date_range("2025-03-01", "2026-09-01", freq="MS", tz="UTC"); G = pd.Timedelta(days=30); R = []
for F in FS:
    P = {k: an(F - k * G) for k in range(0, 7)}; pf, _ = an(F + G)
    df = pd.DataFrame({"p0": P[0][0], "a0": P[0][1], "p3": P[3][0], "pf": pf})
    for k in (1, 2, 3, 4, 5, 6): df[f"p{k}"] = P[k][0]; df[f"a{k}"] = P[k][1]
    df = df[df.p0.notna() & df.p3.notna() & df.pf.notna() & (df.a0 >= 50000) & (df.p0 != df.p3)].copy()
    df["s1"] = df.p0 - df.p3; av_ort = df[["a0", "a1", "a2", "a3"]].where(lambda x: x > 0).mean(axis=1); df["s2"] = df.s1 / av_ort
    ch = pd.concat([(df[f"p{k}"] - df[f"p{k + 1}"]) > 0 for k in range(0, 6)], axis=1); tam = df[[f"p{k}" for k in range(0, 7)]].notna().all(axis=1)
    df["s3"] = np.where(tam, ch.sum(axis=1) + df.s2.rank(pct=True) * 0.5, np.nan)
    pay = np.maximum(df.a0, df[["a0", "a1"]].mean(axis=1)); df["f"] = ((df.pf - df.p0) / pay).clip(-1, 3); df["F"] = F
    R.append(df[["F", "s1", "s2", "s3", "f", "a0"]])
A = pd.concat(R)
yaz("# 🐋 Hyperliquid'de kazanan büyük hesaplar sonraki ay da kazanıyor mu? — PROTOKOL_hl.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · evren: hacme göre ilk 3.000 hesap (47.798 içinden) · {len(FS)} oluşum tarihi (2025-03 → 2026-09) · uygun: hesap değeri ≥ 50.000 $, ≥ 90 gün geçmiş, etkin · ileri 30 gün getirisi (kâr / hesap değeri) · takip maliyeti yok (iyimser)_\n")
yaz(f"_Tarih başına uygun hesap: ort. {A.groupby('F').size().mean():.0f} (en az {A.groupby('F').size().min()}, en çok {A.groupby('F').size().max()}) · tüm uygun hesapların ileri getirisi: medyan {100 * A.f.median():+.2f}% · ort. {100 * A.f.mean():+.2f}% · kârlı %{100 * (A.f > 0).mean():.0f}_\n")
AD = {"s1": "S1 son 90 gün kârı ($)", "s2": "S2 son 90 gün getirisi (%)", "s3": "S3 istikrar (6 ayın kaçı kârlı)"}; SON = {}
for s, ad in AD.items():
    yaz(f"## {ad}"); yaz("| oluşum | uygun | hepsi medyan | en iyi %10: medyan · ort. · kârlı | en iyi 50: medyan · ort. | Spearman |"); yaz("|---|---|---|---|---|---|")
    okd, sp, T10, T50 = [], [], [], []
    for F, g in A.groupby("F"):
        g = g[g[s].notna()]
        if len(g) < 50: continue
        t10 = g[g[s] >= g[s].quantile(0.9)]; t50 = g.nlargest(50, s); r = spearmanr(g[s], g.f)[0]; sp.append(r); T10.append(t10); T50.append(t50)
        okd.append(t10.f.median() > 0 and t10.f.median() > g.f.median())
        yaz(f"| {F:%Y-%m} | {len(g)} | {100 * g.f.median():+.2f}% | {100 * t10.f.median():+.2f}% · {100 * t10.f.mean():+.2f}% · %{100 * (t10.f > 0).mean():.0f} | {100 * t50.f.median():+.2f}% · {100 * t50.f.mean():+.2f}% | {r:+.2f} |")
    t10, t50 = pd.concat(T10), pd.concat(T50); sp = np.array(sp); tsp = sp.mean() / (sp.std(ddof=1) / np.sqrt(len(sp)))
    gec = np.mean(okd) >= 0.70 and t10.f.mean() > 0 and t10.f.median() > 0 and (t10.f > 0).mean() >= 0.55 and tsp >= 2; SON[s] = gec
    yaz(f"\n**Tüm tarihler — en iyi %10:** {len(t10)} · medyan {100 * t10.f.median():+.2f}% · ort. {100 * t10.f.mean():+.2f}% · kârlı %{100 * (t10.f > 0).mean():.0f} · ≤ −%20 %{100 * (t10.f <= -0.2).mean():.0f} · **en iyi 50:** medyan {100 * t50.f.median():+.2f}% · ort. {100 * t50.f.mean():+.2f}% · kârlı %{100 * (t50.f > 0).mean():.0f}")
    yaz(f"**Şartlar:** tarihlerin %{100 * np.mean(okd):.0f}'inde en iyi %10 medyanı > 0 ve > hepsi (≥ %70 gerekli) · Spearman ort. {sp.mean():+.3f}, t {tsp:.1f} (≥ 2 gerekli) → {'✅ KALICILIK VAR' if gec else '❌'}\n")
yaz(f"## Sonuç → {'✅ kalıcılık var: ' + ', '.join(AD[k] for k, v in SON.items() if v) if any(SON.values()) else '❌ geçmişte kazanan hesaplar sonraki ay kazanmaya devam etmiyor'}")
b = A[A.a0 >= 1e6]; yaz(f"\n_Bilgi — yalnız hesap değeri ≥ 1 M $ ({len(b)} gözlem): S2'ye göre en iyi %10 ileri medyan " + (lambda t: f"{100 * t.f.median():+.2f}% · kârlı %{100 * (t.f > 0).mean():.0f}")(pd.concat([g[g.s2 >= g.s2.quantile(0.9)] for _, g in b.groupby('F')])) + f" · hepsi medyan {100 * b.f.median():+.2f}%_")
yaz(f"_Bilgi — sıralama tablosu bugün: 47.798 hesabın %{100 * (M.pnl_all < 0).mean():.0f}'ü tüm zamanlarda zararda · ilk 3.000'de (hacme göre) zararda olan %{100 * (M.head(3000).pnl_all < 0).mean():.0f} · ilk 3.000'in toplam kârı {M.head(3000).pnl_all.sum() / 1e9:+.2f} milyar $ (kazananlar {M.head(3000).pnl_all.clip(lower=0).sum() / 1e9:+.2f} · kaybedenler {M.head(3000).pnl_all.clip(upper=0).sum() / 1e9:+.2f})_")
# sağlamlık notu (sonuçtan sonra eklendi, karar kuralını değiştirmez): "hepsi medyan" piyasa yönüyle mi oynuyor?
try:
    K = pd.read_parquet("yeniliste_mum.parquet"); K["t"] = pd.to_datetime(K.t, utc=True).dt.floor("D"); um = A.groupby("F").f.median(); kr = []
    for s_ in ("HYPEUSDT", "BTCUSDT", "ETHUSDT"):
        p = K[K.s == s_].drop_duplicates("t").set_index("t").c.sort_index(); r = pd.Series({F: p.asof(F + G) / p.asof(F) - 1 for F in um.index if p.index.min() <= F})
        kr.append(f"{s_[:-4]} {um.reindex(r.index).corr(r):+.2f} ({len(r)} ay)")
    yaz("_Sağlamlık notu — aylık 'hepsi medyan' değeri ile aynı 30 günün fiyat değişimi arasındaki korelasyon: " + " · ".join(kr) + " → hesap kârı büyük ölçüde piyasa yönünü (elde tutulan coin'leri) yansıtıyor; 'geçmişte kazanan' çoğu zaman 'o dönemde daha çok long olan' demek ve piyasa dönünce sıralama tersine dönüyor._")
except Exception as e: yaz(f"_Sağlamlık notu hesaplanamadı: {e}_")
open("hl_sonuc.md", "w").write("\n".join(out) + "\n")
