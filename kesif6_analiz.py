# kesif6_analiz.py — PROTOKOL_kesif6.md: 576 SHORT kural → keşif + kontrol (görülmüş 141) → doğrulama (bakılmamış) → kesif6_sonuc.md
import glob, io, zipfile, itertools, json, numpy as np, pandas as pd, requests
out = []; yaz = lambda s="": (out.append(s), print(s, flush=True))
TS = (0.03, 0.05, 0.08); STOPS = ("yok", "S"); HS = (24, 72, 120)
ADLAR = [f"T{t}_{s}_H{h}" for t in TS for s in STOPS for h in HS]
M, X = [], []
for f in sorted(glob.glob("parca/kesif6-p-*/kesif6_meta_p*.csv.gz")):
    p = f.split("_p")[-1].split(".")[0]
    try: m = pd.read_csv(f)
    except pd.errors.EmptyDataError: continue
    x = np.load(f.replace(f"kesif6_meta_p{p}.csv.gz", f"kesif6_X_p{p}.npy")); assert len(m) == len(x); M.append(m); X.append(x)
M = pd.concat(M, ignore_index=True); X = np.concatenate(X); M["t"] = pd.to_datetime(M.t, utc=True)
# BTC 200 gün trendi (vadeli günlük)
U_ = "https://data.binance.vision/data/futures/um"; S = requests.Session(); P = []
def al(u):
    for _ in range(5):
        try:
            r = S.get(u, timeout=60)
            if r.status_code == 200:
                z = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=[0, 4])
                return d[pd.to_numeric(d[0], errors="coerce").notna()].astype(float)
            if r.status_code == 404: return None
        except Exception: pass
for ay in pd.period_range("2021-08", "2026-09", freq="M").strftime("%Y-%m"):
    d = al(f"{U_}/monthly/klines/BTCUSDT/1d/BTCUSDT-1d-{ay}.zip"); P += [d] if d is not None else []
for g in pd.date_range("2026-10-01", "2026-10-26").strftime("%Y-%m-%d"):
    d = al(f"{U_}/daily/klines/BTCUSDT/1d/BTCUSDT-1d-{g}.zip"); P += [d] if d is not None else []
B = pd.concat(P); B[0] = B[0].where(B[0] < 1e14, B[0] / 1000); B["gun"] = pd.to_datetime(B[0], unit="ms", utc=True)
B = B.drop_duplicates("gun").set_index("gun")[4].sort_index(); ust = (B < B.rolling(200, min_periods=200).mean()).shift(1, freq="D")   # short: BTC 200 g ortalamanın ALTINDA
M["trend"] = M.t.dt.floor("D").map(ust).fillna(False).astype(bool); M["gun"] = M.t.dt.floor("D")
U = lambda s: pd.Timestamp(s, tz="UTC")
DON = {"½-1": (U("2022-06-01"), U("2023-07-01")), "½-2": (U("2023-07-01"), U("2025-01-01")), "2025+": (U("2025-01-01"), U("2027-01-01")), "2026": (U("2026-01-01"), U("2027-01-01"))}
FIL = []
for x, b in itertools.product((4, 6), (0, 6)): FIL.append(("S1 pompa yorgunluğu", f"z72≥+{x} · tepeden ≥{b} s", lambda m, x=x, b=b: (m.z72 >= x) & (m.highage >= b)))
for x, b in itertools.product((0.98, 0.95), (np.inf, 0.0)): FIL.append(("S2 fonlama aşırı +", f"yüzdelik≥{x} · r24≤{'—' if b == np.inf else '0'}", lambda m, x=x, b=b: (m.fr > 0) & (m.fp >= x) & (m.r24 <= b)))
for x in (3, 5): FIL.append(("S3 hacimli çöküş kırılımı", f"hacim×≥{x}", lambda m, x=x: (m.vr >= x) & (m.neg30 <= 1.02)))
for x, b in itertools.product((-0.03, -0.05), (0.02, 0.04)): FIL.append(("S4 geç düşen", f"BTC24≤{x:.0%} · coin−BTC≥+{b:.0%}", lambda m, x=x, b=b: (m.btc24 <= x) & (m.r24 - m.btc24 >= b)))
FIL = [(ai, ad + (" · trend" if tr else ""), (lambda m, f=f, tr=tr: f(m) & (m.trend if tr else True))) for ai, ad, f in FIL for tr in (False, True)]
def sec(grup, f):
    x = M[(M.grup == grup) & f(M).fillna(False)].sort_values("t"); keep, son = [], {}
    for i, t, s in zip(x.index.values, x.t.values, x.sym.values):
        if s in son and t - son[s] < np.timedelta64(24, "h"): continue
        son[s] = t; keep.append(i)
    return np.array(keep, dtype=int)
def olc(idx):
    R = {}
    for dn, (a, z) in DON.items():
        ii = idx[(M.t.values[idx] >= a.to_datetime64()) & (M.t.values[idx] < z.to_datetime64())]; n = len(ii)
        if n == 0: R[dn] = None; continue
        net = X[ii][:, 0::2]; w = X[ii][:, 1::2]; g = pd.DataFrame(net).groupby(M.gun.values[ii]).mean()
        R[dn] = dict(n=n, i=100 * (net > 0).mean(0), net=100 * net.mean(0), gi=100 * (g.values > 0).mean(0), liq=(w >= 0.45).sum(0), kotu=100 * net.min(0), ay=n / max((min(z, M.t.max()) - a).days / 30.4, 1))
    return R
def uygun(R, j, dons, mn):
    for dn in dons:
        r = R[dn]
        if r is None or r["n"] < mn or r["i"][j] < 70 or r["net"][j] < 2.0 or r["gi"][j] < 60 or r["liq"][j] > 0: return False
    return True
hucre = lambda r, j: (f"{r['n']} · %{r['i'][j]:.0f} · {r['net'][j]:+.2f} · gün %{r['gi'][j]:.0f} · en kötü {r['kotu'][j]:+.1f} · liq {int(r['liq'][j])} · ayda {r['ay']:.1f}" if r else "0")
yaz("# 🔭 kesif6 — SHORT aileleri · PROTOKOL_kesif6.md · Binance vadeli 1 s + gerçek fonlama")
yaz(f"aday: {len(M):,} · görülmüş {M[M.grup == 'gor'].sym.nunique()} sembol · bakılmamış {M[M.grup == 'yeni'].sym.nunique()} sembol · son {M.t.max()}")
yaz("_hücre: işlem · işlem isabeti · işlem başı net % · gün isabeti · en kötü işlem % · 2x likidasyon · ayda işlem_\n")
RG, aday, yakin = {}, [], []
for k, (aile, ad, f) in enumerate(FIL):
    idx = sec("gor", f); R = olc(idx); RG[k] = R
    for j in range(len(ADLAR)):
        kes = uygun(R, j, ("½-1", "½-2"), 20); kon = kes and uygun(R, j, ("2025+", "2026"), 15)
        if kon: aday.append((min(R[d]["net"][j] for d in DON), k, j))
        if all(R[d] is not None and R[d]["n"] >= 15 for d in DON):
            yakin.append((min(R[d]["i"][j] for d in DON), min(R[d]["net"][j] for d in DON), k, j))
aday.sort(key=lambda x: -x[0])
yaz(f"## Keşif + kontrol (görülmüş 141) — geçen: {len(aday)} / {len(FIL) * len(ADLAR)}")
for mn, k, j in aday[:10]: yaz(f"- {FIL[k][0]} · {FIL[k][1]} · {ADLAR[j]}: " + " | ".join(f"{d} {hucre(RG[k][d], j)}" for d in DON))
sonuc = []
if aday:
    yaz("\n## DOĞRULAMA — bakılmamış coin'ler (bir kez), ilk 5")
    for mn, k, j in aday[:5]:
        R = olc(sec("yeni", FIL[k][2])); g = uygun(R, j, tuple(DON), 20); sonuc.append((g, k, j))
        yaz(f"- {'✅' if g else '❌'} {FIL[k][0]} · {FIL[k][1]} · {ADLAR[j]}: " + " | ".join(f"{d} {hucre(R[d], j)}" for d in DON))
    if any(g for g, _, _ in sonuc):
        g, k, j = next(x for x in sonuc if x[0]); yaz(f"\n**✅ GEÇEN: {FIL[k][0]} · {FIL[k][1]} · {ADLAR[j]}**")
        json.dump(dict(aile=FIL[k][0], filtre=FIL[k][1], cikis=ADLAR[j]), open("kesif6_secim.json", "w"), ensure_ascii=False)
    else: yaz("\n**❌ Doğrulamayı geçen yok.**")
else: yaz("\n**❌ Keşif + kontrolü geçen kural yok.**")
yaz("\n## Bilgi (karar değil) — en yakınlar: dört dönemin en kötü isabeti en yüksek, en kötü dönem neti ≥ +%1")
for mi, mn, k, j in sorted([y for y in yakin if y[1] >= 1.0], key=lambda y: -y[0])[:12]:
    yaz(f"- {FIL[k][0]} · {FIL[k][1]} · {ADLAR[j]}: " + " | ".join(f"{d} {hucre(RG[k][d], j)}" for d in DON))
yaz("\n## Bilgi — aile başına en iyi (en kötü dönem neti en yüksek), görülmüş")
for aile in dict.fromkeys(a for a, _, _ in FIL):
    c = [y for y in yakin if FIL[y[2]][0] == aile]
    if c:
        mi, mn, k, j = max(c, key=lambda y: y[1]); yaz(f"- {aile} · {FIL[k][1]} · {ADLAR[j]}: " + " | ".join(f"{d} {hucre(RG[k][d], j)}" for d in DON))
open("kesif6_sonuc.md", "w").write("\n".join(out) + "\n")
