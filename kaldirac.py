# kaldirac.py — SPOT'TA UZUN VADELİ ALICI + VADELİDE KALDIRAÇ NORMALDEN YÜKSEK → ne olur? (BTC, ETH; günlük)
# Kaldıraç oranı (CryptoQuant'ın "tahmini kaldıraç oranı" mantığı) = Binance vadeli açık pozisyon (coin) / borsalardaki coin (Coin Metrics SplyExNtv). z: son 90 güne göre.
# Spot uzun vadeli alıcı = coin'ler borsadan soğuk cüzdana çıkıyor: 7 g net çıkış / borsadaki miktar (z) — zincir2.py ile aynı. Fonlama oranı (7 g ort.) ve küçük hesapların uzun/kısa oranı ek.
# Veri: data.binance.vision (vadeli metrikler 2021-12'den, fonlama) + Coin Metrics topluluk API + Binance spot günlük mum.
# Zamanlama: gün d verisi → d+1 kapanışında gir, 3 / 7 gün tut, limit komisyon %0,02 × 2. Seçim 2022–2023 · doğrulama 2024+ · 2026 ayrıca.
# 1) "Ne olur" tablosu: her durumda sonraki 3 / 7 günün ortalama getirisi, 3 gün içinde %5+ sert düşüş ve %5+ sert yükseliş olasılığı (tüm günlere göre).
# 2) Para testi: önceden sabit kurallar (yön sabit) + kullanıcı kombinasyonu (yön seçim döneminden) · ✅: seçim net > 0, doğrulama ≥ 8 işlem, net > 0, alt sınır > 0. Plasebo ile şans payı.
import os, io, re, time, zipfile, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
t_ = open("turev.py").read(); exec(t_[t_.index("S3, BV = "):t_.index("KL = [")])                       # s3_list, zcsv, load, ms2ts
z1 = open("zincir.py").read(); exec(z1[z1.index('CM = "https'):z1.index('M = ["FlowInExNtv"')])          # cm(), gunluk() (yalnız kapanış)
def gunluk_tam(sym):
    rows, cur = [], int(pd.Timestamp("2021-06-01", tz="UTC").timestamp() * 1000)
    while True:
        r = requests.get(EP[0], params=dict(symbol=sym, interval="1d", startTime=cur, limit=1000), timeout=20).json()
        if not r: break
        rows += r; cur = r[-1][0] + 86_400_000
        if len(r) < 1000: break
    d = pd.DataFrame([x[:5] for x in rows], columns=["t", "o", "h", "l", "c"]).astype(float); d.index = pd.to_datetime(d.t, unit="ms", utc=True); return d[["h", "l", "c"]]
def zs(s, n=90): return (s - s.rolling(n, min_periods=30).mean()) / (s.rolling(n, min_periods=30).std() + 1e-12)
A22, A24, A26, LMT = pd.Timestamp("2022-01-01", tz="UTC"), pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC"), 0.0002
DON = (("seçim 2022–23", lambda i: i < A24), ("doğrulama 2024+", lambda i: i >= A24), ("2026", lambda i: i >= A26))
yaz(f"# ⚖️ Spot uzun vadeli alıcı + vadeli kaldıraç — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n")
VERI = {}
for a, FS in (("btc", "BTCUSDT"), ("eth", "ETHUSDT")):
    MT = load(f"data/futures/um/daily/metrics/{FS}/"); FR = load(f"data/futures/um/monthly/fundingRate/{FS}/", ["calc_time", "funding_interval_hours", "last_funding_rate"])
    MT["t"] = pd.to_datetime(MT.create_time, utc=True, errors="coerce"); MT = MT.dropna(subset=["t"]); MT["d"] = MT.t.dt.floor("D")
    for c in ("sum_open_interest", "count_long_short_ratio"): MT[c] = pd.to_numeric(MT[c], errors="coerce")
    g = MT.groupby("d"); oi = g.sum_open_interest.last(); ls = g.count_long_short_ratio.mean().where(lambda v: v > 0)
    FR["t"] = ms2ts(FR.calc_time); FR["v"] = pd.to_numeric(FR.last_funding_rate, errors="coerce"); fr = FR.dropna(subset=["v"]).groupby(FR.t.dt.floor("D")).v.mean()
    cmd = cm(a, ["FlowInExNtv", "FlowOutExNtv", "SplyExNtv", "SplyCur"]); px = gunluk_tam(FS)
    ix = px.index[(px.index >= oi.index.min()) & (px.index <= min(oi.index.max(), cmd.index.max()))]
    D = pd.DataFrame(index=ix); D["c"], D["h"], D["l"] = px.c.reindex(ix), px.h.reindex(ix), px.l.reindex(ix)
    cmd = cmd.reindex(ix)
    D["kaldirac"] = zs(np.log((oi.reindex(ix) / cmd.SplyExNtv).where(lambda v: v > 0)))                                              # OI / borsa rezervi
    D["kaldirac_arz"] = zs(np.log((oi.reindex(ix) / cmd.SplyCur).where(lambda v: v > 0)))                                            # OI / toplam arz (yedek ölçü)
    D["spot_alici"] = zs(-(cmd.FlowInExNtv - cmd.FlowOutExNtv).rolling(7).sum() / cmd.SplyExNtv)            # + = borsadan çıkış (uzun vadeli alıcı)
    D["fonlama"] = zs(fr.reindex(ix).rolling(7).mean()); D["kucuk_uzun"] = zs(np.log(ls.reindex(ix)).rolling(3).mean())
    D = D.replace([np.inf, -np.inf], np.nan); VERI[a] = D
    yaz(f"**{a.upper()}**: {ix[0]:%Y-%m-%d} → {ix[-1]:%Y-%m-%d} ({len(ix)} gün) · kaldıraç ile spot alıcı korelasyonu {D.kaldirac.corr(D.spot_alici):+.2f} · kaldıraç ile fonlama {D.kaldirac.corr(D.fonlama):+.2f} · {time.time()-T0:.0f} sn")
def ileri(D, HD):
    c = D.c; y = c.shift(-(1 + HD)) / c.shift(-1) - 1
    lo = pd.concat([D.l.shift(-(1 + k)) for k in range(1, 4)], axis=1).min(axis=1) / c.shift(-1) - 1     # 3 gün içindeki en düşük
    hi = pd.concat([D.h.shift(-(1 + k)) for k in range(1, 4)], axis=1).max(axis=1) / c.shift(-1) - 1
    return y, lo, hi
DURUM = {"Kaldıraç çok yüksek (z ≥ 1,5)": lambda D: D.kaldirac >= 1.5, "Kaldıraç çok düşük (z ≤ −1,5)": lambda D: D.kaldirac <= -1.5,
         "Spot uzun vadeli alıcı (z ≥ 1)": lambda D: D.spot_alici >= 1,
         "SENİN FİKRİN: spot alıcı (z ≥ 1) + kaldıraç yüksek (z ≥ 1)": lambda D: (D.spot_alici >= 1) & (D.kaldirac >= 1),
         "Spot alıcı (z ≥ 1) + kaldıraç düşük (z ≤ 0) — 'sağlıklı' yükseliş": lambda D: (D.spot_alici >= 1) & (D.kaldirac <= 0),
         "Spot satıcı (z ≤ −1) + kaldıraç yüksek (z ≥ 1)": lambda D: (D.spot_alici <= -1) & (D.kaldirac >= 1),
         "Fonlama çok yüksek (z ≥ 1,5)": lambda D: D.fonlama >= 1.5, "Fonlama çok düşük (z ≤ −1,5)": lambda D: D.fonlama <= -1.5,
         "Spot alıcı (z ≥ 1) + fonlama yüksek (z ≥ 1)": lambda D: (D.spot_alici >= 1) & (D.fonlama >= 1),
         "Küçük hesaplar çok uzun (z ≥ 1,5)": lambda D: D.kucuk_uzun >= 1.5, "Kaldıraç yüksek (z ≥ 1) + küçük hesaplar uzun (z ≥ 1)": lambda D: (D.kaldirac >= 1) & (D.kucuk_uzun >= 1)}
yaz("\n## 1. Ne olur? (o durumdaki GÜNLER, tekrarlar dahil · sonraki getiri ortalaması · 3 gün içinde %5+ düşüş / %5+ yükseliş olasılığı)")
for a, D in VERI.items():
    y3, lo, hi = ileri(D, 3); y7, _, _ = ileri(D, 7); rows = []
    for pn, f in DON[:2]:
        m0 = f(D.index) & y7.notna()
        rows.append(dict(durum="(tüm günler)", donem=pn, gun=int(m0.sum()), ort3=100 * y3[m0].mean(), ort7=100 * y7[m0].mean(), dusus5=100 * (lo[m0] <= -0.05).mean(), yukselis5=100 * (hi[m0] >= 0.05).mean()))
        for k, fn in DURUM.items():
            m = fn(D).fillna(False) & m0
            if m.sum() < 5: continue
            rows.append(dict(durum=k, donem=pn, gun=int(m.sum()), ort3=100 * y3[m].mean(), ort7=100 * y7[m].mean(), dusus5=100 * (lo[m] <= -0.05).mean(), yukselis5=100 * (hi[m] >= 0.05).mean()))
    yaz(f"### {a.upper()}\n_ort3 / ort7: sonraki 3 / 7 gün ortalama getiri % · dusus5 / yukselis5: 3 gün içinde fiyatın en az bir kez %5 düşme / yükselme olasılığı %_\n```\n"
        + pd.DataFrame(rows).set_index(["durum", "donem"]).round(2).to_string() + "\n```")
yaz("\n## 2. Para testi (olay: durumun ilk günü, tutma süresince tekrar yok · işlem · isabet % · net % · alt sınır %)")
SABIT = {"Kaldıraç çok yüksek (z ≥ 1,5)": -1, "Kaldıraç çok düşük (z ≤ −1,5)": 1, "Spot alıcı (z ≥ 1) + kaldıraç düşük (z ≤ 0) — 'sağlıklı' yükseliş": 1,
         "Spot satıcı (z ≤ −1) + kaldıraç yüksek (z ≥ 1)": -1, "Fonlama çok yüksek (z ≥ 1,5)": -1, "Fonlama çok düşük (z ≤ −1,5)": 1, "Küçük hesaplar çok uzun (z ≥ 1,5)": -1,
         "Kaldıraç yüksek (z ≥ 1) + küçük hesaplar uzun (z ≥ 1)": -1}
def sonuc(D, m, yon, HD, reps=800):
    y = D.c.shift(-(1 + HD)) / D.c.shift(-1) - 1; ev = D.index[events(m.fillna(False).values, HD)]; e = y.reindex(ev).dropna(); net = yon * e - 2 * LMT; out = {}
    for pn, f in DON:
        x = net[f(net.index)]; out[pn] = (len(x), 100 * (x > 0).mean() if len(x) else np.nan, 100 * x.mean() if len(x) else np.nan, 100 * wboot(x.values, x.index.values, reps)[0] if len(x) >= 8 else np.nan)
    return out
def fmt(o): return " · ".join(("—" if not np.isfinite(v) else (f"{v:.0f}" if i < 2 else f"{v:+.2f}")) for i, v in enumerate(o))
def gecti(o): s, d = o[DON[0][0]], o[DON[1][0]]; return bool(np.isfinite(s[2]) and s[2] > 0 and d[0] >= 8 and d[2] > 0 and d[3] > 0)
rows, rng, pl_ok, pl_n = [], np.random.default_rng(0), 0, 0
for a, D in VERI.items():
    for k, fn in DURUM.items():
        m = fn(D).fillna(False)
        for HD in (3, 7):
            if k in SABIT: yon, kay = SABIT[k], "sabit"
            else:
                ev = D.index[events(m.values, HD)]; e1 = (D.c.shift(-(1 + HD)) / D.c.shift(-1) - 1).reindex(ev).dropna(); e1 = e1[e1.index < A24]
                if len(e1) < 5: continue
                yon, kay = (1 if e1.mean() > 0 else -1), "seçimden"
            o = sonuc(D, m, yon, HD)
            rows.append(dict(coin=a.upper(), durum=k, gun=HD, yon=("AL" if yon > 0 else "SAT") + f" ({kay})", **{pn: fmt(o[pn]) for pn, _ in DON}, ok="✅" if gecti(o) else "❌"))
            for _ in range(20):
                sh = int(rng.integers(60, len(m) - 60)); pm = pd.Series(np.roll(m.values, sh), index=m.index); po = sonuc(D, pm, yon, HD, reps=200)
                if po[DON[0][0]][0] >= 5: pl_n += 1; pl_ok += gecti(po)
R = pd.DataFrame(rows)
yaz(f"Toplam {len(R)} deneme · ✅ geçen **{int((R.ok=='✅').sum())}** · plasebo geçme oranı %{100*pl_ok/max(1,pl_n):.1f} → tesadüfen beklenen ≈ **{pl_ok/max(1,pl_n)*len(R):.1f}**\n```\n" + R.to_string(index=False) + "\n```")
for a, D in VERI.items():
    r = D.dropna(subset=["kaldirac"]).iloc[-1]
    yaz(f"Şu an {a.upper()} ({D.dropna(subset=['kaldirac']).index[-1]:%d.%m}): kaldıraç z {r.kaldirac:+.2f} · spot alıcı z {r.spot_alici:+.2f} · fonlama z {r.fonlama:+.2f} · küçük hesaplar uzun z {r.kucuk_uzun:+.2f}")

# ---- 3. ETH: senin fikrin (spot alıcı z ≥ 1 + kaldıraç z ≥ 1 → AL 7 gün) — mevcut ⛓️ kurallarıyla örtüşme ve canlı giriş saati ----
try:
    import zincir_canli as ZC
    D = VERI["eth"]; cme = cm("eth", ["FlowInExNtv", "FlowOutExNtv", "SplyExNtv"]); Zs = ZC.olcu(cme, ZC.stabil()).reindex(D.index)
    OL = ZC.kural_olaylari(Zs); m = ((D.spot_alici >= 1) & (D.kaldirac >= 1)).fillna(False); ev = D.index[events(m.values, 7)]
    mevcut = sorted(set().union(*[set(v) for k, v in OL.items() if k.startswith("AL")]))
    yakin = [d for d in ev if any(abs((d - x).days) <= 3 for x in mevcut)]
    yaz(f"\n## 3. ETH 'senin fikrin' kuralı: {len(ev)} olay · bunların {len(yakin)} tanesi mevcut ⛓️ AL kurallarıyla ±3 gün içinde çakışıyor (yeni olan: {len(ev)-len(yakin)})")
    H1 = fetch_1h(pd.Timestamp("2021-11-01", tz="UTC").timestamp() * 1000, time.time() * 1000, sym="ETHUSDT")
    for ad, sec in (("hepsi", list(ev)), ("yalnız yeni (⛓️ ile çakışmayan)", [d for d in ev if d not in yakin])):
        for gn, dt in (("d+1 TR 09:00", pd.Timedelta(days=1, hours=6)), ("d+1 TR 15:00", pd.Timedelta(days=1, hours=12)), ("d+1 kapanışı", pd.Timedelta(days=2))):
            R_ = []
            for d in sec:
                t1 = d + dt; t2 = t1 + pd.Timedelta(days=7)
                if t2 > H1.index[-1] or t1 not in H1.index: continue
                p1 = H1.close.loc[t1]; w = H1.loc[(H1.index > t1) & (H1.index <= t2)]
                R_.append(dict(t=d, net=w.close.iloc[-1] / p1 - 1 - 2 * LMT, mae=w.low.min() / p1 - 1))
            E = pd.DataFrame(R_).set_index("t") if R_ else None
            if E is None: continue
            parca = []
            for pn, f in DON:
                e = E[f(E.index)]
                if len(e): parca.append(f"{pn}: {len(e)} · %{100*(e.net>0).mean():.0f} · {100*e.net.mean():+.2f}" + (f" (alt {100*wboot(e.net.values, e.index.values)[0]:+.2f})" if len(e) >= 8 else "") + f" · en kötü ara düşüş %{100*e.mae.min():.0f}")
            yaz(f"- {ad} · giriş {gn}: " + " | ".join(parca))
except Exception as e_: import traceback; traceback.print_exc(); yaz(f"_bölüm 3 hata: {e_}_")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("kaldirac_sonuc.md", "w").write("\n".join(L) + "\n")
