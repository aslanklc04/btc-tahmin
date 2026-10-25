# btc_yerine.py — PROTOKOL_btcyerine.md (kod sonuçtan önce kaydedildi)
import sys, time, numpy as np, pandas as pd
sys.path.insert(0, "canli"); from ortak import fetch_1h
from concurrent.futures import ThreadPoolExecutor
T0 = time.time(); L = []; yaz = lambda s="": (print(s, flush=True), L.append(s))
V = pd.read_csv("veri_seti.csv.gz"); V["t"] = pd.to_datetime(V.t, utc=True)
KS = {"✅ ana (+0,75σ)": 0.75, "🔸 yedek (+0,50σ)": 0.5, "📋 panelden (+0,45σ)": 0.45}
def ohl(c):
    try: o = fetch_1h(pd.Timestamp("2022-03-01", tz="UTC").timestamp() * 1000, time.time() * 1000, sym=f"{c}USDT"); return c, o[["high", "close"]].astype(float)
    except Exception: return c, None
with ThreadPoolExecutor(10) as ex: OH = {c: o for c, o in ex.map(ohl, sorted(set(V.nm) | {"BTC"})) if o is not None}
SG = {c: np.log(o.close).diff().rolling(720, min_periods=168).std() for c, o in OH.items()}
def islem(c, t, H, k, ceza):
    o = OH.get(c)
    if o is None or t not in o.index: return np.nan, np.nan
    i = o.index.get_loc(t); s = SG[c].iloc[i]
    if i + H >= len(o) or not np.isfinite(s): return np.nan, np.nan
    P = o.close.iloc[i] * (1 + ceza); hed = o.close.iloc[i] * (1 + k * s * np.sqrt(H)); fon = 0.0001 * H / 8
    if hed > P and (o.high.values[i + 1:i + H + 1] >= hed).any(): return hed / P - 1 - 0.0005 - 0.0002 - fon, s * np.sqrt(H)
    return o.close.iloc[i + H] / P - 1 - 0.001 - fon, s * np.sqrt(H)
R = []
for (t, sn), g in V.groupby(["t", "sinif"]):
    k = KS[sn]; cn = [islem(r.nm, t, int(r.H), k, 0.001) for r in g.itertuples()]; cn = [x for x in cn if np.isfinite(x[0])]
    if not cn: continue
    H = int(g.H.mode().iloc[0]); b, bs = islem("BTC", t, H, k, 0.0002)
    if not np.isfinite(b): continue
    R.append((t, sn, np.mean([x[0] for x in cn]), np.mean([x[1] for x in cn]), b, bs))
X = pd.DataFrame(R, columns=["t", "sinif", "coin", "coin_s", "btc", "btc_s"]); SON = X.t.max() + pd.Timedelta(hours=1)
A25, A26, Y2, P0 = (pd.Timestamp(x, tz="UTC") for x in ("2025-01-01", "2026-01-01", "2023-07-01", "2022-06-01"))
yaz(f"# ₿ Sinyal saatlerinde coin yerine BTC — PROTOKOL_btcyerine.md · {pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M}")
yaz(f"_{len(X):,} saat sepeti · her hücre: saat isabeti · saat başı net % · risk başına kâr (net ÷ σ√H) · COIN → BTC_\n")
for sn in KS:
    d = X[X.sinif == sn]; sat = []; ok = True
    for dn, a, z in (("keşif ½-1", P0, Y2), ("keşif ½-2", Y2, A25), ("KONTROL 2025+", A25, SON), ("KONTROL 2026", A26, SON)):
        x = d[(d.t >= a) & (d.t < z)]
        if len(x) == 0: sat.append(f"{dn}: 0"); ok = False; continue
        ci, bi = 100 * (x.coin > 0).mean(), 100 * (x.btc > 0).mean(); cr, br = (x.coin / x.coin_s).mean(), (x.btc / x.btc_s).mean()
        g_ = bi >= ci + 3 and br >= cr; ok &= g_
        sat.append(f"{dn}: {len(x)} saat · %{ci:.0f}→%{bi:.0f} · {100 * x.coin.mean():+.2f}→{100 * x.btc.mean():+.2f} · risk başına {cr:+.3f}→{br:+.3f} {'✅' if g_ else '❌'}")
    yaz(f"- **{sn}**: " + " | ".join(sat) + f" → {'**GEÇTİ**' if ok else 'geçmedi'}")
yaz(f"\n_3 deneme · süre {time.time() - T0:.0f} sn_")
open("btc_yerine_sonuc.md", "w").write("\n".join(L) + "\n")
