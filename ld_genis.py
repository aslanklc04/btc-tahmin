# ld_genis.py — 💧 LİKİDİTE DİPTE, geniş liste (🌐 ~126 coin) ve 💵 ABD alıyor coin'lerinin ✅ ana sinyallerinde (yalnız test, 12.10.2026; kullanıcı isteği).
# Ana sinyaller (canlı kurallar): 🌐 🤝 (BTC 4s çok güçlü ↑ ve coin'in kendi primi z ≥ 2) · 🌐 🧪 24 s (kendi primi z ≥ 1,5) · 💵 (durum/prim_acik.csv kuralları).
# LD = coin'in kendi ±%1 derinliği (Binance vadeli arşivi, saatlik ortalama) son 30 güne göre z ≤ −2 (ld_kontrol.py ile aynı).
# ÖNCEDEN YAZILI KARAR (sonuçlar görülmeden; ld_kontrol / gate_ld ile aynı ölçütler, yeni coin'ler BİRLİKTE değerlendirilir):
#   K0 ANA+: üç dönemde (2023 · 2024+ · 2026) isabet ≥ ana +2 puan VE net ≥ ana +0,10 (en az 30 / 30 / 10)
#   K1 40 kaydırmalı plasebo: 2024+ isabet ve net farkı %95'lik değerin üstünde · K2 dipten bağımsızlık (|24 s z| < 2; 20/20/10, 2026 < 10 ise yalnız 2023 ve 2024+)
#   K3 haftalık blok bootstrap 2024+ alt sınır > 0 · K4 ≥ 10 sinyalli coin'lerin ≥ %60'ında daha isabetli (en az 3 coin)
#   → hepsi geçerse 💧 bu coin'lere de genişletilir (Neon ölçümüne eklenir). Geçmezse 💧 yalnız ilk 15 coin'de kalır.
import os, glob, time, numpy as np, pandas as pd
from ortak import events, wboot, DISPLAY_TZ
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
bul = lambda p: (glob.glob(p, recursive=True) or [None])[0]
def utc(ix): ix = pd.DatetimeIndex(ix); return (ix.tz_localize("UTC") if ix.tz is None else ix.tz_convert("UTC")).as_unit("ns")
GEN = {l.strip()[:-4] for l in open("canli/durum/genis_liste.txt") if l.strip()}; PA = pd.read_csv("canli/durum/prim_acik.csv")
DER = {}
for p in glob.glob("**/derinlik_parca*.pkl", recursive=True): DER.update(pd.read_pickle(p))
B = pd.read_pickle(bul("ga/**/disa_BTCUSDT.pkl")); B.index = utc(B.index); KOM = 0.0004; EV = []
def prim(nm):
    p = bul(f"ga/**/prim_{nm}USDT.pkl")
    if not p: return None
    d = pd.read_pickle(p).astype("float64"); d.index = utc(d.index); d = d[~d.index.duplicated()].sort_index(); return d
for nm in sorted(DER):
    PR = prim(nm)
    if PR is None: continue
    z = PR.z
    if nm in GEN:
        p = bul(f"ga/**/disa_{nm}USDT.pkl")
        if p:
            X = pd.read_pickle(p); X.index = utc(X.index); st_, u4_, ac_ = (X[k].fillna(False).astype(bool).values for k in ("star", "u4", "acls"))
            ev = events((st_ | u4_ | ac_) & X.y4.notna().values, 4); t = X.index[ev]; bu4 = B.u4.reindex(t).fillna(False).astype(bool).values; zz = z.reindex(t).values
            m = bu4 & (zz >= 2); EV.append(pd.DataFrame({"nm": nm, "aile": "🌐🤝", "t": t[m], "H": 4, "net": np.exp(X.y4.values[ev][m]) - 1 - KOM}))
        p = bul(f"ga/**/disa24_{nm}USDT.pkl")
        if p:
            D = pd.read_pickle(p).astype("float64"); D.index = utc(D.index); D = D.reindex(pd.date_range(D.index[0], D.index[-1], freq="1h")); c = D.close.ffill(limit=3).values; n = len(D)
            mk = np.nan_to_num(((D.S24 > 0) & (D.C24 >= D.T10_24)).values).astype(bool) & D.T10_24.notna().values & (np.arange(n) + 25 < n)
            ev = events(mk, 24); t = D.index[ev]; zz = z.reindex(t).values; m = zz >= 1.5
            EV.append(pd.DataFrame({"nm": nm, "aile": "🌐🧪", "t": t[m], "H": 24, "net": (c[ev + 24] / c[ev] - 1)[m] - KOM}))
    for r in PA[PA.coin == nm].itertuples():
        H = int(r.saat); ev = events((z >= r.esik).fillna(False).values, H); ev = ev[ev + H < len(PR)]; c = PR.c.values
        EV.append(pd.DataFrame({"nm": nm, "aile": "💵", "t": PR.index[ev], "H": H, "net": c[ev + H] / c[ev] - 1 - KOM}))
E = pd.concat(EV, ignore_index=True); E = E[np.isfinite(E.net)].reset_index(drop=True); E["ok"] = E.net > 0; E["t"] = utc(E.t)
RZ = np.full(len(E), np.nan)
for nm, g in E.groupby("nm"):
    c = prim(nm).c; lr = np.log(c); sg = lr.diff().rolling(720, min_periods=168).std(); RZ[g.index] = ((lr - lr.shift(24)) / (sg * np.sqrt(24))).reindex(pd.DatetimeIndex(g.t)).values
def z720(s): return (s - s.rolling(720, min_periods=168).mean()) / (s.rolling(720, min_periods=168).std() + 1e-12)
LDS = {}
for nm, D in DER.items():
    if not {"ask1", "bid1"} <= set(D.columns): continue
    D = D.reindex(pd.date_range(D.index.min(), D.index.max(), freq="1h")); LDS[nm] = (z720(np.log(D.ask1 + D.bid1)) <= -2).fillna(False)
tz_, nmv = pd.DatetimeIndex(E.t), E.nm.values; OK, NET = E.ok.values, E.net.values
def ara(kay=0):
    v = np.zeros(len(E), bool)
    for nm, s in LDS.items():
        m = nmv == nm
        if m.any(): v[m] = s.reindex(tz_[m] - pd.Timedelta(hours=kay)).fillna(False).values.astype(bool)
    return v
P23, A24, A26 = (pd.Timestamp(x, tz="UTC") for x in ("2023-01-01", "2024-01-01", "2026-01-01"))
D3 = (("2023", (tz_ >= P23) & (tz_ < A24)), ("2024+", tz_ >= A24), ("2026", tz_ >= A26))
def st(m): return {dn: (int((m & md).sum()), 100 * OK[m & md].mean() if (m & md).any() else np.nan, 100 * NET[m & md].mean() if (m & md).any() else np.nan) for dn, md in D3}
def sat(ad, o): return f"{ad:40s}" + " | ".join(f"{o[dn][0]:5d} · %{o[dn][1]:4.1f} · {o[dn][2]:+.2f}" for dn in o)
def ustun(oc, ob, mins, gevsek=False):
    ks = [dn for dn in oc if not (gevsek and dn == "2026" and oc[dn][0] < mins[dn])]
    return len(ks) >= 2 and all(oc[dn][0] >= mins[dn] for dn in ks) and all(oc[dn][1] >= ob[dn][1] + 2 and oc[dn][2] >= ob[dn][2] + 0.10 for dn in ks)
A_ = np.ones(len(E), bool) & np.isin(nmv, list(LDS)); NOR = np.isfinite(RZ) & (np.abs(RZ) < 2); m24 = tz_ >= A24; L0 = ara()
yaz(f"# 💧 Likidite dipte — geniş liste ve 💵 coin'leri — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n"
    f"Vadeli emir defteri arşivi olan coin: {len(LDS)} · ✅ ana sinyal: {A_.sum():,} (" + " · ".join(f"{k} {v:,}" for k, v in E.aile[A_].value_counts().items()) + f") · {time.time()-T0:.0f} sn\n")
OA = st(A_); yaz("_sinyal sayısı · isabet · işlem başı net % — 2023 | 2024+ | 2026_\n```"); yaz(sat("✅ ana (yeni coin'ler)", OA)); yaz(sat("✅ ana + 💧 LD", st(A_ & L0)))
for a in ("🌐🤝", "🌐🧪", "💵"):
    ma = A_ & (E.aile.values == a); yaz(sat(f"  {a}", st(ma))); yaz(sat(f"  {a} + 💧", st(ma & L0)))
yaz(sat("dip/momentum dışı", st(A_ & NOR))); yaz(sat("dip/momentum dışı + 💧", st(A_ & NOR & L0))); yaz("```")
K0 = ustun(st(A_ & L0), OA, {"2023": 30, "2024+": 30, "2026": 10})
def fark(c): a = A_ & m24; b = a & c; return (100 * (OK[b].mean() - OK[a].mean()), 100 * (NET[b].mean() - NET[a].mean())) if b.sum() >= 10 else (np.nan, np.nan)
G1 = fark(L0); PLS = np.array([fark(ara(int(g * 24))) for g in np.linspace(30, 400, 40)])
p95h, p95n = np.nanpercentile(PLS[:, 0], 95), np.nanpercentile(PLS[:, 1], 95); K1 = G1[0] > p95h and G1[1] > p95n
K2 = ustun(st(A_ & NOR & L0), st(A_ & NOR), {"2023": 20, "2024+": 20, "2026": 10}, gevsek=True)
b = A_ & L0 & m24; lo_, hi_ = wboot(NET[b] - NET[A_ & m24].mean(), tz_[b]); K3 = lo_ > 0
sk = []
for nm in sorted(LDS):
    mc = (nmv == nm) & A_ & (tz_ >= P23); mb = mc & L0
    if mb.sum() >= 10: sk.append((nm, int(mb.sum()), 100 * OK[mb].mean(), 100 * OK[mc].mean()))
K4 = len(sk) >= 3 and np.mean([a > b2 for _, _, a, b2 in sk]) >= 0.6
yaz(f"\n- **K0 ANA+:** {'✅' if K0 else '❌'}")
yaz(f"- **K1 plasebo (2024+, 40 kaydırma):** isabet farkı {G1[0]:+.1f} (plasebo %95 {p95h:+.1f}) · net farkı {G1[1]:+.2f} (plasebo %95 {p95n:+.2f}) → {'✅' if K1 else '❌'}")
yaz(f"- **K2 dipten bağımsızlık:** {'✅' if K2 else '❌'}")
yaz(f"- **K3 bootstrap (2024+ net farkı %90):** {100*lo_:+.2f} … {100*hi_:+.2f} → {'✅' if K3 else '❌'}")
yaz(f"- **K4 yaygınlık:** {sum(a > b2 for _, _, a, b2 in sk)}/{len(sk)} coin → {'✅' if K4 else '❌'} · " + " · ".join(f"{nm} {n} %{a:.0f} vs %{b2:.0f}" for nm, n, a, b2 in sk))
OKG = K0 and K1 and K2 and K3 and K4
yaz("\n## Önceden yazılı karar\n" + (f"- ✅ **GEÇTİ** → 💧 bu {len(LDS)} coin'e de genişletilir" if OKG else "- ❌ geçmedi → 💧 yalnız ilk 15 coin'de kalır"))
yaz(f"\nCoin listesi (arşivi olan): {', '.join(sorted(LDS))}")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("ld_genis_sonuc.md", "w").write("\n".join(L) + "\n")
