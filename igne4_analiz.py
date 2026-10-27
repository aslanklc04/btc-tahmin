# igne4_analiz.py — PROTOKOL_igne4.md: 4.608 formül taraması (görülmüş 141 coin) → ilk 5 → bakılmamış coin'lerde doğrulama → igne4_sonuc.md
import glob, json, itertools, numpy as np, pandas as pd
out = []; yaz = lambda s="": (out.append(s), print(s, flush=True))
FS = (0.5, 0.75, 1.0, 1.25); STOPS = ("yok", "S0", "S1", "S2"); HS = (4, 8, 24, 48)
ADLAR = [f"f{f}_{s}_H{h}" for f in FS for s in STOPS for h in HS]
M, X = [], []
for f in sorted(glob.glob("parca/igne4-p-*/igne4_meta_p*.csv.gz")):
    p = f.split("_p")[-1].split(".")[0]
    try: m = pd.read_csv(f)
    except pd.errors.EmptyDataError: continue
    x = np.load(f.replace(f"igne4_meta_p{p}.csv.gz", f"igne4_X_p{p}.npy")); assert len(m) == len(x); M.append(m); X.append(x)
M = pd.concat(M, ignore_index=True); X = np.concatenate(X); M["t"] = pd.to_datetime(M.t, utc=True)
yaz("# 🪡 İğne sonrası alım — formül taraması + doğrulama · PROTOKOL_igne4.md · Binance vadeli 5 dk")
yaz(f"aday (kr ≥ 3): {len(M):,} · sembol: görülmüş {M[M.grup == 'gor'].sym.nunique()} · bakılmamış {M[M.grup == 'yeni'].sym.nunique()} · son {M.t.max()}")
ok = M.liq >= 2e6; M, X = M[ok].reset_index(drop=True), X[ok.values]
yaz(f"likidite ≥ 2 M$/gün sonrası: {len(M):,} aday (görülmüş {int((M.grup == 'gor').sum()):,} · bakılmamış {int((M.grup == 'yeni').sum()):,})\n")
ns = M[(M.grup == "gor") & (M.kr >= 4)].groupby("t").taban.nunique(); M["nsame"] = M.t.map(ns).fillna(0)
U = lambda s: pd.Timestamp(s, tz="UTC")
DON = {"½-1": (U("2022-06-01"), U("2023-07-01")), "½-2": (U("2023-07-01"), U("2025-01-01")), "2025+": (U("2025-01-01"), U("2027-01-01")), "2026": (U("2026-01-01"), U("2027-01-01"))}
FIL = list(itertools.product((4, 6, 8), (0.5, 0.75), (np.inf, 2, 5), (-np.inf, -0.01), (-np.inf, 0.0)))
fad = lambda F: f"k≥{F[0]} · rr≥{F[1]} · nsame≤{'∞' if F[2] == np.inf else int(F[2])} · BTC≥{'—' if F[3] == -np.inf else '-1%'} · r7>{'—' if F[4] == -np.inf else '0'}"
def sec(grup, F):
    k, r, n, b, t7 = F
    x = M[(M.grup == grup) & (M.kr >= k) & (M.rr >= r) & (M.nsame <= n) & (M.rb.fillna(0) >= b) & ((M.r7 > t7) if t7 != -np.inf else True)].sort_values("t")
    keep, son = [], {}
    for i, t, s in zip(x.index.values, x.t.values, x.sym.values):
        if s in son and t - son[s] < np.timedelta64(24, "h"): continue
        son[s] = t; keep.append(i)
    return np.array(keep, dtype=int)
def olc(idx):
    """idx → {dönem: (n, isabet[64], net[64], saat isabeti[64], liq[64], en kötü[64], haftada)}"""
    R = {}
    for dn, (a, z) in DON.items():
        ii = idx[(M.t.values[idx] >= a.to_datetime64()) & (M.t.values[idx] < z.to_datetime64())]; n = len(ii)
        if n == 0: R[dn] = None; continue
        net = X[ii][:, 0::2]; w = X[ii][:, 1::2]
        sa = pd.DataFrame(net).groupby(M.t.values[ii]).mean()
        R[dn] = dict(n=n, i=100 * (net > 0).mean(0), net=100 * net.mean(0), si=100 * (sa.values > 0).mean(0), liq=(w <= -0.45).sum(0), kotu=100 * net.min(0),
                     hf=n / max((min(z, M.t.max()) - a).days / 7, 1))
    return R
def uygun(R, j, isb, net, mn, m26):
    for dn, r in R.items():
        if r is None or r["n"] < (m26 if dn == "2026" else mn): return False
        if r["i"][j] < isb or r["net"][j] < net or r["si"][j] < 65 or r["liq"][j] > 0: return False
    return True
hucre = lambda r, j: (f"{r['n']} · %{r['i'][j]:.1f} · {r['net'][j]:+.2f} · saat %{r['si'][j]:.0f} · en kötü {r['kotu'][j]:+.1f} · liq {int(r['liq'][j])} · haftada {r['hf']:.1f}" if r else "0")
# ---- TARAMA
aday = []; RG = {}
for F in FIL:
    idx = sec("gor", F); R = olc(idx); RG[F] = (idx, R)
    for j in range(len(ADLAR)):
        if uygun(R, j, 72, 0.30, 30, 20): aday.append((min(R[d]["net"][j] for d in DON), F, j))
aday.sort(key=lambda x: -x[0])
yaz(f"## TARAMA — görülmüş 141 coin · {len(FIL) * len(ADLAR):,} formül · uygun: {len(aday)}")
yaz("_hücre: işlem · işlem isabeti · işlem başı net % · saat isabeti · en kötü işlem % · 2x likidasyon · haftada işlem_\n")
yaz("| # | giriş filtresi | çıkış | " + " | ".join(DON) + " |"); yaz("|---|---|---|" + "---|" * len(DON))
for r_, (mn, F, j) in enumerate(aday[:20]):
    R = RG[F][1]; yaz(f"| {r_ + 1} | {fad(F)} | {ADLAR[j]} | " + " | ".join(hucre(R[d], j) for d in DON) + " |")
if not aday:
    yaz("\n**❌ Tarama şartını sağlayan formül yok.** En yakınlar (dört dönemin en kötü isabeti en yüksek, kârlı olanlar):")
    yak = []
    for F, (idx, R) in RG.items():
        if any(R[d] is None for d in DON): continue
        for j in range(len(ADLAR)):
            yak.append((min(R[d]["i"][j] for d in DON), min(R[d]["net"][j] for d in DON), F, j))
    for mi, mnn, F, j in sorted([y for y in yak if y[1] > 0], key=lambda y: -y[0])[:10]:
        R = RG[F][1]; yaz(f"- {fad(F)} · {ADLAR[j]}: " + " | ".join(f"{d} {hucre(R[d], j)}" for d in DON))
# ---- DOĞRULAMA
sonuc = None
if aday:
    yaz(f"\n## DOĞRULAMA — bakılmamış coin'ler (bir kez) · ilk 5")
    yaz("| # | formül | " + " | ".join(DON) + " | sonuç |"); yaz("|---|---|" + "---|" * len(DON) + "---|")
    for r_, (mn, F, j) in enumerate(aday[:5]):
        R = olc(sec("yeni", F)); g = uygun(R, j, 70, 0.20, 30, 30)
        if g and sonuc is None: sonuc = (F, j, R)
        yaz(f"| {r_ + 1} | {fad(F)} · {ADLAR[j]} | " + " | ".join(hucre(R[d], j) for d in DON) + f" | {'✅' if g else '❌'} |")
    if sonuc:
        F, j, R = sonuc; yaz(f"\n**✅ SEÇİLEN: {fad(F)} · {ADLAR[j]}**")
        idx = RG[F][0]; x = M.loc[idx]
        yaz(f"- görülmüş coin'lerde 10.10.2025: " + (lambda ii: f"{len(ii)} işlem · ort. {100 * X[ii, 2 * j].mean():+.2f}" if len(ii) else "işlem yok")(idx[(x.t >= U('2025-10-10')).values & (x.t < U('2025-10-12')).values]))
        json.dump(dict(filtre=[None if (isinstance(v, float) and not np.isfinite(v)) else v for v in F], cikis=ADLAR[j]), open("igne4_secim.json", "w"))
    else: yaz("\n**❌ Doğrulamada hiçbir formül geçmedi → canlıya alınmaz.**")
open("igne4_sonuc.md", "w").write("\n".join(out) + "\n")
