# uzun_kisa.py — KÜÇÜK yatırımcı kaldıraçlı LONG'a koşuyor → düşüş habercisi mi? BÜYÜK yatırımcı LONG açıyor + kaldıraç artıyor → yükseliş habercisi mi?
# Veri: Binance USDⓈ-M vadeli arşivi (data.binance.vision, günlük metrik dosyaları, 2021-12'den):
#   küçük  = tüm hesapların uzun/kısa oranı (count_long_short_ratio — hesap sayısıyla, çoğunluk küçük yatırımcı)
#   büyük  = büyük hesapların POZİSYON uzun/kısa oranı (sum_toptrader_long_short_ratio — en büyük teminatlı hesaplar, pozisyon ağırlıklı)
#   kaldıraç artışı = açık pozisyonun (coin cinsinden) 7 günlük artışı. Hepsi: 7 günlük değişim, son 90 güne göre z.
# Önceden sabit kurallar (yön sabit, 3 ve 7 gün):
#   K1 küçük long artıyor (z ≥ 1) + açık pozisyon artıyor (z ≥ 1) → SAT       B1 büyük long artıyor (z ≥ 1) + açık pozisyon artıyor (z ≥ 1) → AL
#   A1 büyük long artıyor (z ≥ 1) + küçük long azalıyor (z ≤ −1) → AL       A2 küçük long artıyor (z ≥ 1) + büyük long azalıyor (z ≤ −1) → SAT
#   K2 / B2: aynı kurallar seviyeyle (oranın kendisi z ≥ 1,5) + açık pozisyon artıyor
# Giriş: gün d verisi → d+1 kapanışı, limit komisyon %0,02 × 2. Seçim 2022–23 · doğrulama 2024+ · 2026 ayrıca.
# ✅ (coin başına): seçim net > 0 · doğrulama ≥ 8 işlem, net > 0, %90 alt sınır > 0. Ayrıca TÜM coin'ler havuzlanmış (genel kural mı?). Plasebo ile şans payı.
import os, io, re, time, zipfile, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
t_ = open("turev.py").read(); exec(t_[t_.index("S3, BV = "):t_.index("KL = [")])                       # s3_list, zcsv, load, ms2ts
COINS = [("BTC", "BTCUSDT"), ("ETH", "ETHUSDT"), ("SOL", "SOLUSDT"), ("XRP", "XRPUSDT"), ("BNB", "BNBUSDT"), ("DOGE", "DOGEUSDT"),
         ("ADA", "ADAUSDT"), ("LINK", "LINKUSDT"), ("AVAX", "AVAXUSDT"), ("SUI", "SUIUSDT"), ("NEAR", "NEARUSDT"), ("OP", "OPUSDT")]
def gunluk(sym):
    rows, cur = [], int(pd.Timestamp("2021-09-01", tz="UTC").timestamp() * 1000)
    while True:
        r = requests.get(EP[0], params=dict(symbol=sym, interval="1d", startTime=cur, limit=1000), timeout=20).json()
        if not r: break
        rows += r; cur = r[-1][0] + 86_400_000
        if len(r) < 1000: break
    d = pd.DataFrame([x[:5] for x in rows], columns=["t", "o", "h", "l", "c"]).astype(float); return pd.Series(d.c.values, index=pd.to_datetime(d.t, unit="ms", utc=True))
def zs(s, n=90): return (s - s.rolling(n, min_periods=30).mean()) / (s.rolling(n, min_periods=30).std() + 1e-12)
def lg(x): return np.log(x.where(x > 0))
VERI = {}
for nm, FS in COINS:
    try:
        MT = load(f"data/futures/um/daily/metrics/{FS}/")
        MT["d"] = pd.to_datetime(MT.create_time, utc=True, errors="coerce").dt.floor("D"); MT = MT.dropna(subset=["d"])
        for c in ("sum_open_interest", "count_long_short_ratio", "sum_toptrader_long_short_ratio", "count_toptrader_long_short_ratio"): MT[c] = pd.to_numeric(MT[c], errors="coerce")
        g = MT.groupby("d"); px = gunluk(FS)
        ix = px.index[(px.index >= g.size().index.min()) & (px.index <= g.size().index.max())]
        D = pd.DataFrame(index=ix); D["c"] = px.reindex(ix)
        kc, by, oi = lg(g.count_long_short_ratio.mean()).reindex(ix), lg(g.sum_toptrader_long_short_ratio.mean()).reindex(ix), lg(g.sum_open_interest.last()).reindex(ix)
        D["kucuk_art"], D["buyuk_art"], D["oi_art"] = zs(kc.diff(7)), zs(by.diff(7)), zs(oi.diff(7))
        D["kucuk_sev"], D["buyuk_sev"] = zs(kc), zs(by)
        VERI[nm] = D.replace([np.inf, -np.inf], np.nan)
        yaz(f"- {nm}: {ix[0]:%Y-%m-%d} → {ix[-1]:%Y-%m-%d} · küçük↔büyük long değişimi korelasyonu {D.kucuk_art.corr(D.buyuk_art):+.2f} · küçük long değişimi ↔ fiyat 7 g {D.kucuk_art.corr(np.log(D.c).diff(7)):+.2f} · büyük ↔ fiyat {D.buyuk_art.corr(np.log(D.c).diff(7)):+.2f} · {time.time()-T0:.0f} sn")
    except Exception as e: yaz(f"- {nm}: veri alınamadı ({type(e).__name__}: {str(e)[:80]})")
yaz("")
A24, A26, LMT = pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC"), 0.0002
DON = (("seçim 2022–23", lambda i: i < A24), ("doğrulama 2024+", lambda i: i >= A24), ("2026", lambda i: i >= A26))
KUR = {"K1 küçük long artıyor + açık pozisyon artıyor → SAT": (lambda D: (D.kucuk_art >= 1) & (D.oi_art >= 1), -1),
       "B1 büyük long artıyor + açık pozisyon artıyor → AL": (lambda D: (D.buyuk_art >= 1) & (D.oi_art >= 1), 1),
       "A1 büyük long artıyor + küçük long azalıyor → AL": (lambda D: (D.buyuk_art >= 1) & (D.kucuk_art <= -1), 1),
       "A2 küçük long artıyor + büyük long azalıyor → SAT": (lambda D: (D.kucuk_art >= 1) & (D.buyuk_art <= -1), -1),
       "K2 küçük long çok yüksek (seviye z ≥ 1,5) + açık pozisyon artıyor → SAT": (lambda D: (D.kucuk_sev >= 1.5) & (D.oi_art >= 1), -1),
       "B2 büyük long çok yüksek (seviye z ≥ 1,5) + açık pozisyon artıyor → AL": (lambda D: (D.buyuk_sev >= 1.5) & (D.oi_art >= 1), 1)}
def olaylar(D, m, HD):
    y = D.c.shift(-(1 + HD)) / D.c.shift(-1) - 1; ev = D.index[events(m.fillna(False).values, HD)]; return y.reindex(ev).dropna()
def ozet(net, reps=800):
    out = {}
    for pn, f in DON:
        x = net[f(net.index)]; out[pn] = (len(x), 100 * (x > 0).mean() if len(x) else np.nan, 100 * x.mean() if len(x) else np.nan, 100 * wboot(x.values, x.index.values, reps)[0] if len(x) >= 8 else np.nan)
    return out
def fmt(o): return " · ".join(("—" if not np.isfinite(v) else (f"{v:.0f}" if i < 2 else f"{v:+.2f}")) for i, v in enumerate(o))
def gecti(o): s, d = o[DON[0][0]], o[DON[1][0]]; return bool(s[0] >= 3 and np.isfinite(s[2]) and s[2] > 0 and d[0] >= 8 and d[2] > 0 and d[3] > 0)
yaz("## 1. Havuzlanmış (12 coin birlikte — genel bir kural mı?) · işlem · isabet % · işlem başı net % · alt sınır %")
HV = []
for k, (fn, yon) in KUR.items():
    for HD in (3, 7):
        parts = [yon * olaylar(D, fn(D), HD) - 2 * LMT for D in VERI.values()]
        net = pd.concat(parts).sort_index() if parts else pd.Series(dtype=float); o = ozet(net)
        HV.append(dict(kural=k, gun=HD, **{pn: fmt(o[pn]) for pn, _ in DON}, karar="✅" if gecti(o) else "❌"))
yaz("```\n" + pd.DataFrame(HV).set_index(["kural", "gun"]).to_string() + "\n```")
yaz("\n## 2. Coin başına")
rows, rng, pl_ok, pl_n = [], np.random.default_rng(0), 0, 0
for nm, D in VERI.items():
    for k, (fn, yon) in KUR.items():
        m = fn(D).fillna(False)
        for HD in (3, 7):
            o = ozet(yon * olaylar(D, m, HD) - 2 * LMT); rows.append(dict(coin=nm, kural=k.split(" ")[0], gun=HD, **{pn: fmt(o[pn]) for pn, _ in DON}, ok=gecti(o)))
            for _ in range(10):
                sh = int(rng.integers(60, len(m) - 60)); pm = pd.Series(np.roll(m.values, sh), index=m.index)
                po = ozet(yon * olaylar(D, pm, HD) - 2 * LMT, reps=200); pl_n += 1; pl_ok += gecti(po)
R = pd.DataFrame(rows)
yaz(f"Toplam {len(R)} deneme · ✅ geçen **{int(R.ok.sum())}** · plasebo geçme oranı %{100*pl_ok/max(1,pl_n):.1f} → tesadüfen beklenen ≈ **{pl_ok/max(1,pl_n)*len(R):.1f}**")
yaz("### ✅ Geçenler\n```\n" + (R[R.ok].drop(columns="ok").to_string(index=False) if R.ok.any() else "(yok)") + "\n```")
for k in KUR:
    kk = k.split(" ")[0]; G = R[R.kural == kk]
    yaz(f"### {k}\n```\n" + G.drop(columns=["kural"]).assign(ok=G.ok.map({True: "✅", False: "❌"})).to_string(index=False) + "\n```")
yaz("\n## Şu an (son gün)\n" + "\n".join(f"- {nm} ({D.dropna(subset=['kucuk_art']).index[-1]:%d.%m}): küçük long değişimi z {D.kucuk_art.dropna().iloc[-1]:+.2f} · büyük long değişimi z {D.buyuk_art.dropna().iloc[-1]:+.2f} · açık pozisyon değişimi z {D.oi_art.dropna().iloc[-1]:+.2f}"
                                       for nm, D in VERI.items() if D.kucuk_art.notna().any()))
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("uzun_kisa_sonuc.md", "w").write("\n".join(L) + "\n")
