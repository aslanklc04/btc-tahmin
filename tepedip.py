# tepedip.py — PROTOKOL_tepedip.md (kod sonuçtan önce kaydedildi)
import sys, json, time, numpy as np, pandas as pd
sys.path.insert(0, "canli"); from ortak import fetch_1h
from concurrent.futures import ThreadPoolExecutor
T0 = time.time(); L = []; yaz = lambda s="": (print(s, flush=True), L.append(s))
V = pd.read_csv("veri_seti.csv.gz"); V["t"] = pd.to_datetime(V.t, utc=True)
D = pd.read_csv("karal2_veri.csv.gz"); D["t"] = pd.to_datetime(D.t, utc=True)
LS = json.load(open("sekil_liste.json")); COINS = sorted(set(V.nm) | set(LS["A"]) | set(LS["B"]) | {"BTC"})
def ohl(c):
    try: o = fetch_1h(pd.Timestamp("2022-03-01", tz="UTC").timestamp() * 1000, time.time() * 1000, sym=f"{c}USDT"); return c, o[["high", "low", "close"]].astype(float)
    except Exception: return c, None
with ThreadPoolExecutor(10) as ex: OH = {c: o for c, o in ex.map(ohl, COINS) if o is not None}
yaz(f"fiyat: {len(OH)} coin · {time.time() - T0:.0f} sn")
def etk(o):
    lc = np.log(o.close); s1 = lc.diff().rolling(720, min_periods=168).std()
    return pd.DataFrame({"konum": (o.close - o.low.rolling(24).min()) / (o.high.rolling(24).max() - o.low.rolling(24).min()), "r1z": lc.diff() / s1,
                         "r4z": lc.diff(4) / (s1 * 2), "r24z": lc.diff(24) / (s1 * np.sqrt(24)), "s1": s1})
E = {c: etk(o) for c, o in OH.items()}; EB = E["BTC"]
A25, A26, Y2, P0 = (pd.Timestamp(x, tz="UTC") for x in ("2025-01-01", "2026-01-01", "2023-07-01", "2022-06-01"))
# ---------------- A) tepe filtresi ----------------
X = D[["t", "nm", "sinif", "H", "B_T0"]].dropna(subset=["B_T0"]).copy()
for k in ("konum", "r1z", "r4z"): X[k] = np.nan
for c, g in X.groupby("nm"):
    if c in E: X.loc[g.index, ["konum", "r1z", "r4z"]] = E[c].reindex(pd.DatetimeIndex(g.t))[["konum", "r1z", "r4z"]].values
X = X.dropna(subset=["konum", "r1z", "r4z"]); SON = X.t.max() + pd.Timedelta(hours=1)
def olc(d):
    if len(d) == 0: return dict(n=0, ii=np.nan, si=np.nan, net=np.nan)
    sp = d.groupby("t").B_T0.mean(); return dict(n=len(d), ii=100 * (d.B_T0 > 0).mean(), si=100 * (sp > 0).mean(), net=100 * d.B_T0.mean())
def sart(o, b): return o["n"] >= 0.4 * b["n"] and o["ii"] >= b["ii"] - 0.5 and o["si"] >= b["si"] - 0.5 and o["net"] >= b["net"] + 0.03
FL = {"F1 tepeye yakını at (konum > 0,8)": lambda d: d[~(d.konum > 0.8)], "F2 son 4 s sert yükseleni at": lambda d: d[~(d.r4z >= 1)],
      "F3 son 1 s sert yükseleni at": lambda d: d[~(d.r1z >= 1)], "F4 F1 veya F2'yi at": lambda d: d[~((d.konum > 0.8) | (d.r4z >= 1))]}
DON = [("keşif ½-1", P0, Y2), ("keşif ½-2", Y2, A25), ("KONTROL 2025+", A25, SON), ("KONTROL 2026", A26, SON)]
yaz(f"# ⛰️ Tepe filtresi ve dip sinyali — PROTOKOL_tepedip.md · {pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M}\n")
yaz(f"## A) Tepe filtresi — {len(X):,} sinyal (giriş B, vadeli ücret + fonlama) · n · işlem isabeti · saat isabeti · işlem başı net %")
for sn in ["✅ ana (+0,75σ)", "🔸 yedek (+0,50σ)", "📋 panelden (+0,45σ)"]:
    d = X[X.sinif == sn]; yaz(f"### {sn}"); yaz("| Kural | " + " | ".join(a for a, _, _ in DON) + " | keşif |"); yaz("|---|" + "---|" * 5)
    b = [olc(d[(d.t >= a) & (d.t < z)]) for _, a, z in DON]
    yaz("| taban | " + " | ".join(f"{o['n']} · %{o['ii']:.1f} · %{o['si']:.1f} · {o['net']:+.3f}" for o in b) + " | — |"); gec = []
    for ad, f in FL.items():
        o = [olc(f(d[(d.t >= a) & (d.t < z)])) for _, a, z in DON]; ok = sart(o[0], b[0]) and sart(o[1], b[1])
        if ok: gec.append((o[0]["net"] + o[1]["net"], ad, o))
        yaz(f"| {ad} | " + " | ".join(f"{x['n']} · %{x['ii']:.1f} · %{x['si']:.1f} · {x['net']:+.3f}" for x in o) + f" | {'✅' if ok else '❌'} |")
    if gec:
        _, ad, o = max(gec); yaz(f"\n**Kontrole giden: {ad}** → 2025+ {'✅' if sart(o[2], b[2]) else '❌'} · 2026 {'✅' if sart(o[3], b[3]) else '❌'}\n")
    else: yaz("\n**Kontrole giden yok.**\n")
# ---------------- B) dip sinyali ----------------
yaz("## B) Dip sinyali (coin ve BTC son 24 s sert düşmüş, coin 24 s dibinde) — uzun")
def olaylar(c, H, tp):
    o, e = OH[c], E[c]; eb = EB.reindex(e.index); m = ((e.r24z <= -1) & (eb.r24z <= -1) & (e.konum <= 0.2)).fillna(False).values
    cl, hi = o.close.values, o.high.values; s1 = e.s1.values; n = len(cl)
    def net_i(i):
        if i + H >= n or not np.isfinite(s1[i]): return np.nan
        P = cl[i] * 1.001; fon = 0.0001 * H / 8
        if tp:
            hed = cl[i] * (1 + 0.75 * s1[i] * np.sqrt(H))
            if hed > P and (hi[i + 1:i + H + 1] >= hed).any(): return hed / P - 1 - 0.0005 - 0.0002 - fon
        return cl[i + H] / P - 1 - 0.001 - fon
    idx, son = [], -10**9
    for i in np.where(m)[0]:
        if i - son >= H: idx.append(i); son = i
    ev = pd.DataFrame({"t": o.index[idx], "net": [net_i(i) for i in idx]})
    ay = pd.Series([net_i(i) for i in range(0, n, 3)], index=o.index[::3]); plc = ay.groupby(ay.index.to_period("M")).mean()   # plasebo: her 3 saatte bir, aynı ay
    ev["plc"] = plc.reindex(ev.t.dt.to_period("M")).values; ev["c"] = c; return ev.dropna()
for H in (4, 24):
    for tp in (False, True):
        R = {g: pd.concat([olaylar(c, H, tp) for c in LS[g] if c in OH and c != "BTC"] or [pd.DataFrame(columns=["t", "net", "plc", "c"])]) for g in ("A", "B")}
        sat, ok = [], True
        for dn, g, a, z in (("keşif ½-1", "A", P0, Y2), ("keşif ½-2", "A", Y2, A25), ("KONTROL A 2025+", "A", A25, SON), ("KONTROL B dokunulmamış", "B", P0, SON)):
            e = R[g][(R[g].t >= a) & (R[g].t < z)]; hf = len(e) / max(1, (z - a).days / 7)
            nt = 100 * e.net.mean() if len(e) else np.nan; pl = 100 * e.plc.mean() if len(e) else np.nan; ii = 100 * (e.net > 0).mean() if len(e) else np.nan
            g_ = len(e) > 0 and nt > 0.15 and nt - pl >= 0.15 and ii >= 55 and hf >= 2; ok &= g_
            sat.append(f"{dn}: {len(e)} ({hf:.1f}/hf) · isabet %{ii:.0f} · net {nt:+.2f} · plasebo {pl:+.2f} {'✅' if g_ else '❌'}")
        yaz(f"- **{H} s, {'🎯 0,75σ' if tp else '🎯 yok'}**: " + " | ".join(sat) + f" → {'**GEÇTİ**' if ok else 'geçmedi'}")
yaz(f"\n_16 deneme (12 filtre + 4 dip varyantı) · süre {time.time() - T0:.0f} sn_")
open("tepedip_sonuc.md", "w").write("\n".join(L) + "\n")
