# ld_dip.py — 💧 LİKİDİTE DİPTE + 📉 DİP birlikte, 💵 (ve diğer 🌐 olmayan) coin'lerde (kullanıcı isteği 14.10.2026; yalnız test).
# 15 ana coin'de (ld_kontrol.py): ana %59 · %59 · %60 → 💧+📉 %87 · %78 · %73. Burada aynı ölçüm ld_genis.py olaylarında (118 coin), 💵'nin 9 coin'i (XRP, AAVE, SOL, ALGO, AVAX, CRV, FIL, INJ, UNI) geniş listede de var → 💵 olayları coin listesinden bağımsız ölçülür (14.10 düzeltme, sonuç görülmeden: ilk çalışmada 💵 olayları yanlışlıkla 🌐 diye dışlandı, 0 olay).
# 📉 dip = coin'in son 24 saatlik getirisi kendi oynaklığına göre z ≤ −2 (canlıdaki dip_mi ile aynı).
# ÖNCEDEN YAZILI KARAR (sonuçlar görülmeden): 💧 canlıya girdiğinde "💧 + 📉 birlikte" en üst öncelik olur, ancak 💵 coin'lerinde de
#   💧+📉 isabeti ve neti hem yalnız 💧'den hem yalnız 📉'den yüksekse (2023 ve 2024+'da; 2026'da en az 10 sinyal varsa o da) — en az 10 / 10 sinyal.
#   Az sinyal varsa (2023 veya 2024+'da < 10) karar 15 coin sonucuna göre verilir, burada "veri az" yazılır.
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

P23, A24, A26 = (pd.Timestamp(x, tz="UTC") for x in ("2023-01-01", "2024-01-01", "2026-01-01"))
tz_, nmv = pd.DatetimeIndex(E.t), E.nm.values; OK, NET = E.ok.values, E.net.values
def ara():
    v = np.zeros(len(E), bool)
    for nm, s in LDS.items():
        m = nmv == nm
        if m.any(): v[m] = s.reindex(tz_[m]).fillna(False).values.astype(bool)
    return v
D3 = (("2023", (tz_ >= P23) & (tz_ < A24)), ("2024+", tz_ >= A24), ("2026", tz_ >= A26))
def st(m): return {dn: (int((m & md).sum()), 100 * OK[m & md].mean() if (m & md).any() else np.nan, 100 * NET[m & md].mean() if (m & md).any() else np.nan) for dn, md in D3}
def sat(ad, o): return f"{ad:34s}" + " | ".join(f"{o[dn][0]:5d} · %{o[dn][1]:4.1f} · {o[dn][2]:+.2f}" for dn in o)
L0 = ara(); DIP = np.nan_to_num(RZ, nan=0) <= -2; GN = np.isin(nmv, list(GEN)); A_ = np.isin(nmv, list(LDS))
yaz(f"# 💧 + 📉 birlikte — 💵 ve 🌐 olmayan coin'ler — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n_sinyal sayısı · isabet · işlem başı net % — 2023 | 2024+ | 2026_\n")
SON = {}
for ad, g in (("💵 ABD alıyor", A_ & (E.aile.values == "💵")), ("🌐🤝 / 🌐🧪 (bilgi)", A_ & (E.aile.values != "💵"))):
    yaz(f"**{ad}** (coin: {', '.join(sorted(set(nmv[g])))})\n```")
    o = {k: st(g & m) for k, m in (("hepsi", np.ones(len(E), bool)), ("💧", L0), ("📉", DIP), ("💧+📉", L0 & DIP))}
    for k, v in o.items(): yaz(sat(f"{ad[:2]} {k}", v))
    yaz("```"); SON[ad] = o
o = SON["💵 ABD alıyor"]; az = any(o["💧+📉"][dn][0] < 10 for dn in ("2023", "2024+"))
ks = [dn for dn in ("2023", "2024+", "2026") if o["💧+📉"][dn][0] >= 10]
ust = all(o["💧+📉"][dn][1] > max(o["💧"][dn][1], o["📉"][dn][1]) and o["💧+📉"][dn][2] > max(o["💧"][dn][2], o["📉"][dn][2]) for dn in ks)
yaz("\n## Önceden yazılı karar\n" + ("- 💵'de veri az → karar 15 coin sonucuna göre (💧+📉 en üstte)" if az else (f"- ✅ 💵 coin'lerinde de 💧+📉 en iyisi ({', '.join(ks)}) → 💧 canlıya girince en üst öncelik" if ust else "- ❌ 💵 coin'lerinde 💧+📉 her ikisinden de iyi değil → 💵'de ayrı öncelik verilmez")))
open("ld_dip_sonuc.md", "w").write("\n".join(L) + "\n")
