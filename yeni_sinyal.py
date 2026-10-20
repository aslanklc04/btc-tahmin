# yeni_sinyal.py — YENİ SİNYAL TARAMASI (20.10.2026, kullanıcı: "daha isabetli, daha kârlı, FARKLI SAATLERDE gelen sinyal bul"; yalnız test)
# BTC'den bağımsız, coin'in kendi fiyat/hacim davranışından gelen 16 kural · ~140 coin · saatlik 2021+ · yalnız AL (spot) · giriş = sinyal saati kapanışı, maliyet %0,04.
# ÖNCEDEN YAZILI ŞART (sonuç görülmeden): seçim 2021–23 net > 0 · doğrulama 2024–25 isabet ≥ %55, net > 0, haftalık blok %90 alt sınır > 0 ·
#   2026 net ≥ 0 · sinyallerin ≤ %30'u BTC 4s Çok güçlü ↑ saatinde ("farklı saat") · ve gerçek veride geçen kural sayısı, 20 plasebonun (her coin'de kural
#   maskesi rastgele 72–2000 saat kaydırılmış) %95'lik değerinden büyük olmalı. Aksi halde hiçbir kural önerilmez.
import os, glob, time, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import fetch_1h, events, wboot
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(str(s))
def utc(ix): ix = pd.DatetimeIndex(ix); return (ix.tz_localize("UTC") if ix.tz is None else ix.tz_convert("UTC")).as_unit("ns")
GEN = [l.strip()[:-4] for l in open("canli/durum/genis_liste.txt") if l.strip()]; COR = [l.strip().replace("USDT", "") for l in open("canli/durum/coin_listesi.txt") if l.strip()]
CO = sorted((set(GEN) | set(COR)) - {"BTC"}); BAS = pd.Timestamp("2021-01-01", tz="UTC")
def veri(nm):
    try: o = fetch_1h(BAS.timestamp() * 1000, time.time() * 1000, sym=f"{nm}USDT"); o.index = utc(o.index); return nm, o.astype("float64")
    except Exception as e: print(nm, e); return nm, None
with ThreadPoolExecutor(8) as ex: O = {k: v for k, v in ex.map(veri, CO + ["BTC"]) if v is not None and len(v) > 24 * 400}
B = O.pop("BTC"); IX = pd.date_range(BAS, B.index[-1], freq="1h", tz="UTC").as_unit("ns")
bu4 = pd.Series(False, index=IX)
for p in glob.glob("ga/**/disa_BTCUSDT.pkl", recursive=True): x = pd.read_pickle(p); x.index = utc(x.index); bu4 = x.u4.fillna(False).astype(bool).reindex(IX).fillna(False)
yaz(f"# 🔎 Yeni sinyal taraması (BTC'den bağımsız) — {pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M}\n{len(O)} coin · {(time.time() - T0) / 60:.0f} dk veri\n")
def zroll(x, w=720): return (x - x.rolling(w, min_periods=168).mean()) / (x.rolling(w, min_periods=168).std() + 1e-12)
bc = np.log(B.close.reindex(IX).ffill(limit=3)); bsig = bc.diff().rolling(720, min_periods=168).std()
br4, br24 = bc - bc.shift(4), bc - bc.shift(24); zbr4 = br4 / (bsig * 2)
C = {}; FT = {}
for nm, o in O.items():
    o = o.reindex(IX); c = np.log(o.close.ffill(limit=3)); lr = c.diff(); sig = lr.rolling(720, min_periods=168).std()
    r1, r4, r24, r168 = lr, c - c.shift(4), c - c.shift(24), c - c.shift(168)
    qv = np.log(o.volume * o.close + 1); v24 = np.log((o.volume * o.close).rolling(24).sum() + 1)
    vr = np.log(lr.rolling(24).std() / (sig + 1e-12) + 1e-9)
    FT[nm] = dict(zrel=zroll(r24 - br24), zr1=r1 / sig, zr4=r4 / (sig * 2), zr24=r24 / (sig * np.sqrt(24)), vz1=zroll(qv), vz24=zroll(v24), r1=r1, r24=r24,
                  hh=(o.close >= o.close.rolling(720, min_periods=700).max()), zvr=zroll(vr).shift(1))
    C[nm] = o.close.ffill(limit=3).values; FT[nm]["r168"] = r168
RK = pd.DataFrame({nm: FT[nm]["r168"] for nm in FT}).rank(axis=1, pct=True)
yaz(f"özellikler hazır · {(time.time() - T0) / 60:.0f} dk")
KURAL = {
 "K1a BTC'ye göre aşırı geride (z ≤ −2) → 8s": (lambda f, nm: f["zrel"] <= -2, 8), "K1b BTC'ye göre aşırı geride (z ≤ −2) → 24s": (lambda f, nm: f["zrel"] <= -2, 24),
 "K1c BTC'ye göre çok aşırı geride (z ≤ −3) → 24s": (lambda f, nm: f["zrel"] <= -3, 24),
 "K2a BTC'ye göre aşırı güçlü (z ≥ 2) → 8s": (lambda f, nm: f["zrel"] >= 2, 8), "K2b BTC'ye göre aşırı güçlü (z ≥ 2) → 24s": (lambda f, nm: f["zrel"] >= 2, 24),
 "K3a sessiz hacim patlaması (hacim z ≥ 3, fiyat sakin) → 8s": (lambda f, nm: (f["vz1"] >= 3) & (f["zr1"].abs() < 0.5), 8),
 "K3b sessiz hacim patlaması → 24s": (lambda f, nm: (f["vz1"] >= 3) & (f["zr1"].abs() < 0.5), 24),
 "K4a 30 günlük zirve + hacim (z ≥ 1,5) → 24s": (lambda f, nm: f["hh"] & (f["vz24"] >= 1.5), 24), "K4b 30 günlük zirve + hacim → 72s": (lambda f, nm: f["hh"] & (f["vz24"] >= 1.5), 72),
 "K5a sert düşüş sonrası ilk yeşil saat → 8s": (lambda f, nm: (f["zr24"] <= -2.5) & (f["r1"] > 0), 8), "K5b sert düşüş sonrası ilk yeşil saat → 24s": (lambda f, nm: (f["zr24"] <= -2.5) & (f["r1"] > 0), 24),
 "K6a BTC düşerken yükselen coin → 8s": (lambda f, nm: (zbr4 <= -1) & (f["zr4"] >= 1), 8), "K6b BTC düşerken yükselen coin → 24s": (lambda f, nm: (zbr4 <= -1) & (f["zr4"] >= 1), 24),
 "K7a 7 günün en çok geride kalanı (%5) + bugün yeşil → 24s": (lambda f, nm: (RK[nm] <= 0.05) & (f["r24"] > 0), 24),
 "K7b 7 günün en çok geride kalanı + bugün yeşil → 72s": (lambda f, nm: (RK[nm] <= 0.05) & (f["r24"] > 0), 72),
 "K8 uzun sessizlik sonrası güçlü hareket ↑ → 24s": (lambda f, nm: (f["zvr"] <= -1.3) & (f["zr4"] >= 1.5), 24)}
D_SEL, D_VAL, D_26 = (IX >= pd.Timestamp("2021-03-01", tz="UTC")) & (IX < pd.Timestamp("2024-01-01", tz="UTC")), (IX >= pd.Timestamp("2024-01-01", tz="UTC")) & (IX < pd.Timestamp("2026-01-01", tz="UTC")), IX >= pd.Timestamp("2026-01-01", tz="UTC")
MASK = {k: {nm: np.nan_to_num(fn(FT[nm], nm).values.astype(float), nan=0).astype(bool) for nm in FT} for k, (fn, H) in KURAL.items()}
def degerlendir(kaydir=None, rg=None):
    out = {}
    for k, (fn, H) in KURAL.items():
        ts, nets, b4 = [], [], []
        for nm, m in MASK[k].items():
            if kaydir: m = np.roll(m, int(rg.integers(72, 2000)))
            c = C[nm]; n = len(c); ok = np.isfinite(c) & (np.arange(n) + H < n); ok[:-H] &= np.isfinite(c[H:]); ev = events(m & ok, H)
            if not len(ev): continue
            ts.append(ev); nets.append(c[ev + H] / c[ev] - 1 - 0.0004)
        if not ts: continue
        ev = np.concatenate(ts); r = np.concatenate(nets); t = IX[ev]
        res = {}
        for dn, dm in (("sel", D_SEL), ("val", D_VAL), ("y26", D_26)):
            s = dm[ev]; res[dn] = (int(s.sum()), 100 * (r[s] > 0).mean() if s.any() else np.nan, 100 * r[s].mean() if s.any() else np.nan)
        s = D_VAL[ev]; lo = wboot(r[s] * 100, t[s])[0] if s.sum() >= 5 else np.nan; res["lo"] = lo; res["b4"] = 100 * bu4.values[ev].mean()
        res["gun"] = pd.DatetimeIndex(t[D_VAL[ev]]).floor("D").nunique() / 104; res["hf"] = s.sum() / 104
        res["gec"] = bool(res["sel"][2] > 0 and res["val"][1] >= 55 and res["val"][2] > 0 and lo > 0 and res["y26"][2] >= 0 and res["b4"] <= 30)
        out[k] = res
    return out
R = degerlendir(); ng = sum(v["gec"] for v in R.values())
yaz("## Gerçek veri\n```")
yaz(f"{'kural':58s} | seçim 2021–23 n·isabet·net | doğrulama 2024–25 n·isabet·net (alt) | 2026 n·isabet·net | haftada · BTC güçlü saat % | sonuç")
for k, v in R.items():
    yaz(f"{k[:58]:58s} | {v['sel'][0]:6d} %{v['sel'][1]:4.1f} {v['sel'][2]:+.2f} | {v['val'][0]:6d} %{v['val'][1]:4.1f} {v['val'][2]:+.2f} ({v['lo']:+.2f}) | {v['y26'][0]:5d} %{v['y26'][1]:4.1f} {v['y26'][2]:+.2f} | {v['hf']:5.1f} · %{v['b4']:3.0f} | {'✅' if v['gec'] else '—'}")
yaz("```"); yaz(f"geçen kural: {ng} · {(time.time() - T0) / 60:.0f} dk")
rg = np.random.default_rng(11); PL = []
for i in range(20): PL.append(sum(v["gec"] for v in degerlendir(True, rg).values())); print(f"plasebo {i + 1}: {PL[-1]}", flush=True)
p95 = np.percentile(PL, 95)
yaz(f"\n## Plasebo (20 kez rastgele kaydırılmış): geçen sayısı ortalama {np.mean(PL):.1f} · %95'lik {p95:.1f} · en çok {max(PL)}")
yaz(f"\n**Karar (önceden yazılı):** " + (f"✅ gerçek veride {ng} kural geçti > plasebo %95 ({p95:.1f}) → geçenler ikinci aşamaya (canlı kural + mevcut sinyallerle çakışma) önerilir: " + ", ".join(k for k, v in R.items() if v["gec"]) if ng > p95 else f"❌ gerçek veride {ng} kural geçti, plasebo %95'lik {p95:.1f} → şanstan ayırt edilemiyor, hiçbir şey eklenmez"))
yaz(f"_süre {(time.time() - T0) / 60:.0f} dk_")
open("yeni_sinyal_sonuc.md", "w").write("\n".join(L) + "\n")
