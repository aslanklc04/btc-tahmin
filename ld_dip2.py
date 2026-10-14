# ld_dip2.py — 🌐 GENİŞ LİSTEDE "💧 LİKİDİTE DİPTE + 📉 DİP BİRLİKTE" ÖNCELİĞİ (kullanıcı onayı 14.10.2026 "tm yap"; yalnız test).
# Olaylar: 🌐🤝 ve 🌐🧪 ✅ ana sinyaller (ld_genis.py ile aynı). 💧 = ±%1 derinlik z720 ≤ −2 · 📉 = son 24 s getiri / oynaklık z ≤ −2.
# Not: ld_dip.py'de bilgi olarak %78 · %74 · %88 görüldü; ölçütler bundan sonra ama sonuç tekrar çalıştırılmadan yazıldı → şans payı plasebo + bootstrap ile sınanır.
# ÖNCEDEN YAZILI KARAR (dönemler 2023 · 2024+ · 2026):
#   K0 ANA+: 💧+📉 isabeti ≥ 🌐 ana +2 puan VE net ≥ +0,10, üç dönemde (en az 30 / 30 / 10)
#   K1 PLASEBO: 💧 ve 📉 birlikte 30–400 gün kaydırılır (40 kez); 2024+ isabet ve net farkı plasebo %95'in üstünde
#   K2 İKİSİNDEN DE İYİ: üç dönemde isabet VE net hem yalnız 💧'den hem yalnız 📉'den yüksek (öncelik sırası için gerekli)
#   K3 haftalık blok bootstrap 2024+ net farkı %90 alt sınırı > 0
#   K4 YAYGINLIK: 2023+'da en az 5 💧+📉 sinyali olan coin'lerin ≥ %60'ında 🌐 ana isabetinden yüksek (en az 5 coin; geniş listede coin başına sinyal az)
#   → hepsi geçerse: 💧 canlıya girince 🌐 coin'lerinde de "💧+📉 birlikte" en üst öncelik (📉 tek başına 🌐'de yine kullanılmaz).
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
G_ = np.isin(E.aile.values, ["🌐🤝", "🌐🧪"]) & np.isin(E.nm.values, list(LDS)); E = E[G_].reset_index(drop=True); RZ = RZ[G_]
tz_, nmv = pd.DatetimeIndex(E.t), E.nm.values; OK, NET = E.ok.values, E.net.values
RZS = {}
for nm in pd.unique(nmv):
    c = prim(nm).c; lr = np.log(c); sg = lr.diff().rolling(720, min_periods=168).std(); RZS[nm] = (lr - lr.shift(24)) / (sg * np.sqrt(24))
def kosul(kay=0):
    ld = np.zeros(len(E), bool); dp = np.zeros(len(E), bool)
    for nm in pd.unique(nmv):
        m = nmv == nm; tt = tz_[m] - pd.Timedelta(hours=kay)
        if nm in LDS: ld[m] = LDS[nm].reindex(tt).fillna(False).values.astype(bool)
        dp[m] = np.nan_to_num(RZS[nm].reindex(tt).values, nan=0) <= -2
    return ld, dp
D3 = (("2023", (tz_ >= P23) & (tz_ < A24)), ("2024+", tz_ >= A24), ("2026", tz_ >= A26)); m24 = tz_ >= A24
def st(m): return {dn: (int((m & md).sum()), 100 * OK[m & md].mean() if (m & md).any() else np.nan, 100 * NET[m & md].mean() if (m & md).any() else np.nan) for dn, md in D3}
def sat(ad, o): return f"{ad:26s}" + " | ".join(f"{o[dn][0]:5d} · %{o[dn][1]:4.1f} · {o[dn][2]:+.2f}" for dn in o)
A_ = np.ones(len(E), bool); LD, DP = kosul(); C = LD & DP
OA, OL, OD, OC = st(A_), st(LD), st(DP), st(C)
yaz(f"# 🌐 Geniş listede 💧 + 📉 birlikte — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n✅ 🌐 ana sinyal: {len(E):,} · coin {len(set(nmv))} · {time.time()-T0:.0f} sn\n")
yaz("_sinyal sayısı · isabet · işlem başı net % — 2023 | 2024+ | 2026_\n```")
for ad, o in (("🌐 ana (hepsi)", OA), ("+ 💧 yalnız", OL), ("+ 📉 yalnız", OD), ("+ 💧 ve 📉 birlikte", OC)): yaz(sat(ad, o))
for a in ("🌐🤝", "🌐🧪"):
    ma = E.aile.values == a; yaz(sat(f"  {a}", st(ma))); yaz(sat(f"  {a} + 💧📉", st(ma & C)))
yaz("```")
K0 = all(OC[dn][0] >= mn and OC[dn][1] >= OA[dn][1] + 2 and OC[dn][2] >= OA[dn][2] + 0.10 for dn, mn in (("2023", 30), ("2024+", 30), ("2026", 10)))
def fark(c): a = A_ & m24; b = a & c; return (100 * (OK[b].mean() - OK[a].mean()), 100 * (NET[b].mean() - NET[a].mean())) if b.sum() >= 10 else (np.nan, np.nan)
G1 = fark(C); PLS = []
for g in np.linspace(30, 400, 40):
    l_, d_ = kosul(int(g * 24)); PLS.append(fark(l_ & d_))
PLS = np.array(PLS); p95h, p95n = np.nanpercentile(PLS[:, 0], 95), np.nanpercentile(PLS[:, 1], 95); K1 = bool(G1[0] > p95h and G1[1] > p95n)
K2 = all(OC[dn][1] > max(OL[dn][1], OD[dn][1]) and OC[dn][2] > max(OL[dn][2], OD[dn][2]) for dn in ("2023", "2024+", "2026"))
b = C & m24; lo_, hi_ = wboot(NET[b] - NET[A_ & m24].mean(), tz_[b]); K3 = bool(lo_ > 0)
sk = []
for nm in sorted(set(nmv)):
    mc = (nmv == nm) & (tz_ >= P23); mb = mc & C
    if mb.sum() >= 5: sk.append((nm, int(mb.sum()), 100 * OK[mb].mean(), 100 * OK[mc].mean()))
K4 = len(sk) >= 5 and np.mean([a > b2 for _, _, a, b2 in sk]) >= 0.6
i = lambda x: "✅" if x else "❌"
yaz(f"\n- **K0 ANA+:** {i(K0)}")
yaz(f"- **K1 plasebo (2024+, 40 kaydırma):** isabet farkı {G1[0]:+.1f} (plasebo %95 {p95h:+.1f}) · net farkı {G1[1]:+.2f} (plasebo %95 {p95n:+.2f}) → {i(K1)}")
yaz(f"- **K2 ikisinden de iyi:** {i(K2)}")
yaz(f"- **K3 bootstrap (2024+ net farkı %90):** {100*lo_:+.2f} … {100*hi_:+.2f} → {i(K3)}")
yaz(f"- **K4 yaygınlık:** {sum(a > b2 for _, _, a, b2 in sk)}/{len(sk)} coin → {i(K4)} · " + " · ".join(f"{nm} {n} %{a:.0f} vs %{b2:.0f}" for nm, n, a, b2 in sk))
GEC = K0 and K1 and K2 and K3 and K4
yaz("\n## Önceden yazılı karar\n" + ("- ✅ **GEÇTİ** → 💧 canlıya girince 🌐 coin'lerinde de 💧+📉 birlikte en üst öncelik" if GEC else "- ❌ geçmedi → 🌐'de 💧+📉 ayrı öncelik verilmez (💧 tek başına yine eklenir)"))
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("ld_dip2_sonuc.md", "w").write("\n".join(L) + "\n")
