# lider.py — GECİKMELİ TAKİP + PRİM SIÇRAMASI ailesi, %65 hedefi (20.10.2026, kullanıcı: 'isabet 65 üzeri olmalı'; yalnız test) · tabanı yeni_sinyal.py (20.10.2026, kullanıcı: "daha isabetli, daha kârlı, FARKLI SAATLERDE gelen sinyal bul"; yalnız test)
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
# ÖNCEDEN YAZILI ŞART (sonuç görülmeden): doğrulama 2024–25 VE 2026 isabet ≥ %65 · seçim 2021–23 net > 0 · doğrulama net > 0 ve haftalık blok alt sınır > 0 · 2026 net > 0 ·
#   doğrulamada haftada ≥ 3 sinyal · BTC güçlü saat ≤ %30 · SAAT bazında (aynı saatteki coin'ler tek olay) doğrulama isabeti ≥ %60 · plasebo (20 kaydırma) %95'lik < gerçek geçen sayısı.
PZ = {}                                                                                      # coin'in kendi Coinbase primi z (ga prim_*.pkl + art3 prim_veri)
for p in glob.glob("ga/**/prim_*USDT.pkl", recursive=True):
    d = pd.read_pickle(p).astype("float64"); d.index = utc(d.index); PZ[os.path.basename(p)[5:-8]] = d.z[~d.index.duplicated()].reindex(IX)
for p in glob.glob("art3/**/prim_veri.pkl", recursive=True):
    for k, v in pd.read_pickle(p).items():
        if k not in PZ: v = v.astype("float64"); v.index = utc(v.index); PZ[k] = v.z[~v.index.duplicated()].reindex(IX)
yaz(f"prim verisi olan coin: {len(PZ)}")
bzr24 = br24 / (bsig * np.sqrt(24))
nanz = pd.Series(np.nan, index=IX)
def pz(nm): return PZ.get(nm, nanz)
BAZ = lambda f: (f["zr24"] <= -2.5) & (f["r1"] > 0)
bz1 = bc.diff() / bsig                                                                        # BTC son saat z
def pzd(nm, k): x = pz(nm); return x - x.shift(k)
KURAL = {
 "L1 BTC son saatte sert ↑ (z ≥ 2), coin henüz kıpırdamadı (z < 0,5) → 2s": (lambda f, nm: (bz1 >= 2) & (f["zr1"] < 0.5), 2),
 "L2 aynı → 4s": (lambda f, nm: (bz1 >= 2) & (f["zr1"] < 0.5), 4),
 "L3 BTC çok sert ↑ (z ≥ 3), coin geride → 4s": (lambda f, nm: (bz1 >= 3) & (f["zr1"] < 0.5), 4),
 "L4 BTC sert ↑, coin geride + coin primi ≥ 0 → 4s": (lambda f, nm: (bz1 >= 2) & (f["zr1"] < 0.5) & (pz(nm) >= 0), 4),
 "L5 BTC 4 saatte sert ↑ (z ≥ 2), coin 4 saatte yerinde → 8s": (lambda f, nm: (zbr4 >= 2) & (f["zr4"].abs() < 0.5), 8),
 "P1 coin primi 1 saatte sıçradı (+1,5 z), fiyat sakin → 4s": (lambda f, nm: (pzd(nm, 1) >= 1.5) & (f["zr1"].abs() < 1), 4),
 "P2 aynı → 8s": (lambda f, nm: (pzd(nm, 1) >= 1.5) & (f["zr1"].abs() < 1), 8),
 "P3 coin primi 4 saatte sıçradı (+2 z) ve ≥ 1, fiyat sakin → 8s": (lambda f, nm: (pzd(nm, 4) >= 2) & (pz(nm) >= 1) & (f["zr4"].abs() < 1), 8),
 "C1 K1c + K5 (coin'e özel derin düşüş + ilk yeşil saat) → 8s": (lambda f, nm: (f["zrel"] <= -3) & (f["r1"] > 0), 8),
 "C2 K1c + K5 → 24s": (lambda f, nm: (f["zrel"] <= -3) & (f["r1"] > 0), 24)}
D_SEL, D_VAL, D_26 = (IX >= pd.Timestamp("2021-03-01", tz="UTC")) & (IX < pd.Timestamp("2024-01-01", tz="UTC")), (IX >= pd.Timestamp("2024-01-01", tz="UTC")) & (IX < pd.Timestamp("2026-01-01", tz="UTC")), IX >= pd.Timestamp("2026-01-01", tz="UTC")
MASK = {k: {nm: np.nan_to_num(fn(FT[nm], nm).values.astype(float), nan=0).astype(bool) for nm in FT} for k, (fn, H) in KURAL.items()}
def degerlendir(kaydir=None, rg=None):
    out = {}
    for k, (fn, H) in KURAL.items():
        ts, nets = [], []
        for nm, m in MASK[k].items():
            if kaydir: m = np.roll(m, int(rg.integers(72, 2000)))
            c = C[nm]; n = len(c); ok = np.isfinite(c) & (np.arange(n) + H < n); ok[:-H] &= np.isfinite(c[H:]); ev = events(m & ok, H)
            if len(ev): ts.append(ev); nets.append(c[ev + H] / c[ev] - 1 - 0.0004)
        if not ts: continue
        ev = np.concatenate(ts); r = np.concatenate(nets); t = IX[ev]; res = {}
        for dn, dm in (("sel", D_SEL), ("val", D_VAL), ("y26", D_26)):
            s = dm[ev]; res[dn] = (int(s.sum()), 100 * (r[s] > 0).mean() if s.any() else np.nan, 100 * r[s].mean() if s.any() else np.nan)
        s = D_VAL[ev]; res["lo"] = wboot(r[s] * 100, t[s])[0] if s.sum() >= 5 else np.nan; res["b4"] = 100 * bu4.values[ev].mean(); res["hf"] = s.sum() / 104
        g = pd.Series(r[s], index=t[s]).groupby(level=0).mean(); res["saat"] = (len(g), 100 * (g > 0).mean() if len(g) else np.nan, s.sum() / max(len(g), 1))
        s6 = D_26[ev]; g6 = pd.Series(r[s6], index=t[s6]).groupby(level=0).mean(); res["saat26"] = 100 * (g6 > 0).mean() if len(g6) else np.nan
        res["gec"] = bool(res["val"][1] >= 65 and res["y26"][1] >= 65 and res["sel"][2] > 0 and res["val"][2] > 0 and res["lo"] > 0 and res["y26"][2] > 0
                          and res["hf"] >= 3 and res["b4"] <= 30 and res["saat"][1] >= 60)
        out[k] = res
    return out
R = degerlendir(); ng = sum(v["gec"] for v in R.values())
yaz("## Gerçek veri\n```")
yaz(f"{'kural':46s} | seçim n·isabet·net | doğrulama 2024–25 n·isabet·net (alt) | 2026 n·isabet·net | hf | saat: sayı·isabet·coin/saat (2026 saat isabet) | sonuç")
for k, v in R.items():
    yaz(f"{k[:46]:46s} | {v['sel'][0]:5d} %{v['sel'][1]:4.1f} {v['sel'][2]:+.2f} | {v['val'][0]:5d} %{v['val'][1]:4.1f} {v['val'][2]:+.2f} ({v['lo']:+.2f}) | {v['y26'][0]:4d} %{v['y26'][1]:4.1f} {v['y26'][2]:+.2f} | {v['hf']:4.1f} | {v['saat'][0]:4d} %{v['saat'][1]:4.1f} {v['saat'][2]:3.1f} (%{v['saat26']:4.1f}) | {'✅' if v['gec'] else '—'}")
yaz("```")
rg = np.random.default_rng(13); PL = [sum(v["gec"] for v in degerlendir(True, rg).values()) for _ in range(20)]; p95 = np.percentile(PL, 95)
yaz(f"\n## Plasebo (20 kaydırma): geçen ortalama {np.mean(PL):.1f} · %95'lik {p95:.1f} · en çok {max(PL)}")
yaz(f"\n**Karar (önceden yazılı, %65 şartı):** " + (f"✅ {ng} kural geçti (plasebo %95 {p95:.1f}): " + ", ".join(k for k, v in R.items() if v["gec"]) if ng > p95 and ng > 0 else f"❌ %65 şartını geçen kural yok ya da şanstan ayırt edilemiyor (gerçek {ng}, plasebo %95 {p95:.1f})"))
yaz(f"_süre {(time.time() - T0) / 60:.0f} dk_")
open("lider_sonuc.md", "w").write("\n".join(L) + "\n")
