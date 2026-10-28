# kesif7.py — PROTOKOL_kesif7.md: BTC/ETH çok günlük olaylar (DVOL · CoinMetrics akış · korku endeksi · fonlama) → kesif7_sonuc.md
import io, time, zipfile, itertools, json, numpy as np, pandas as pd, requests
out = []; yaz = lambda s="": (out.append(s), print(s, flush=True))
S = requests.Session(); URL = "https://data.binance.vision/data/futures/um"
FL, FP, KAY, SLIP = 0.0002, 0.0005, 0.003, 0.001
TS = (0.03, 0.05, 0.08); STOPS = (None, 0.08, 0.12); HS = (3, 7, 14)
ADLAR = [f"T{t}_{'yok' if s is None else f'S{s}'}_{h}g" for t in TS for s in STOPS for h in HS]
def get(u, **kw):
    for k in range(5):
        try:
            r = S.get(u, timeout=60, **kw)
            if r.status_code == 200: return r
            if r.status_code == 404: return None
        except Exception: pass
        time.sleep(2 + 3 * k)
    return None
def zcsv(b, cols, header=None):
    z = zipfile.ZipFile(io.BytesIO(b)); return pd.read_csv(z.open(z.namelist()[0]), header=header, usecols=cols)
AY = pd.period_range("2022-01", "2026-09", freq="M").strftime("%Y-%m")
def binance(sym):
    P = []
    for ay in AY:
        r = get(f"{URL}/monthly/klines/{sym}/1h/{sym}-1h-{ay}.zip")
        if r: d = zcsv(r.content, [0, 1, 2, 3, 4]); P.append(d[pd.to_numeric(d[0], errors="coerce").notna()].astype(float))
    for g in pd.date_range("2026-10-01", "2026-10-25").strftime("%Y-%m-%d"):
        r = get(f"{URL}/daily/klines/{sym}/1h/{sym}-1h-{g}.zip")
        if r: d = zcsv(r.content, [0, 1, 2, 3, 4]); P.append(d[pd.to_numeric(d[0], errors="coerce").notna()].astype(float))
    k = pd.concat(P); k.columns = ["ot", "o", "h", "l", "c"]; k.loc[k.ot > 1e14, "ot"] = k.ot / 1000
    k["t"] = pd.to_datetime(k.ot, unit="ms", utc=True); k = k.drop_duplicates("t").set_index("t").sort_index()
    F = []
    for ay in AY:
        r = get(f"{URL}/monthly/fundingRate/{sym}/{sym}-fundingRate-{ay}.zip")
        if r:
            z = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z.open(z.namelist()[0])); d.columns = [c.strip().lower() for c in d.columns]
            F.append(pd.DataFrame({"t": pd.to_numeric(d[[c for c in d.columns if "time" in c][0]]), "r": pd.to_numeric(d[[c for c in d.columns if "rate" in c][-1]])}))
    f = pd.concat(F).dropna(); f.loc[f.t > 1e14, "t"] = f.t / 1000; f["t"] = pd.to_datetime(f.t, unit="ms", utc=True)
    return k, f.drop_duplicates("t").set_index("t").r.sort_index()
def dvol(cur):
    P = []; a = int(pd.Timestamp("2021-06-01", tz="UTC").timestamp() * 1000); son = int(pd.Timestamp("2026-10-27", tz="UTC").timestamp() * 1000)
    while a < son:
        b = min(a + 900 * 86400000, son)
        r = get("https://www.deribit.com/api/v2/public/get_volatility_index_data", params=dict(currency=cur, start_timestamp=a, end_timestamp=b, resolution=86400))
        if r: P += r.json().get("result", {}).get("data", [])
        a = b
    d = pd.DataFrame(P, columns=["ts", "o", "h", "l", "c"]); d["t"] = pd.to_datetime(d.ts, unit="ms", utc=True)
    return d.drop_duplicates("t").set_index("t").sort_index().o                                 # günün açılışı = 00:00 değeri
def akis():
    u = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"; p = dict(assets="btc,eth", metrics="FlowInExNtv,FlowOutExNtv", frequency="1d", start_time="2020-06-01", page_size=10000)
    D = []; r = get(u, params=p)
    while r is not None:
        j = r.json(); D += j.get("data", []); nx = j.get("next_page_url")
        r = get(nx) if nx else None
    d = pd.DataFrame(D); d["t"] = pd.to_datetime(d.time, utc=True)
    for c in ("FlowInExNtv", "FlowOutExNtv"): d[c] = pd.to_numeric(d[c], errors="coerce")
    return {a: g.set_index("t").sort_index()[["FlowInExNtv", "FlowOutExNtv"]] for a, g in d.groupby("asset")}
def fng():
    r = get("https://api.alternative.me/fng/", params=dict(limit=0, format="json")); d = pd.DataFrame(r.json()["data"])
    d["t"] = pd.to_datetime(pd.to_numeric(d.timestamp), unit="s", utc=True); return pd.to_numeric(d.set_index("t").value).sort_index()
AK = akis(); FG = fng(); yaz("# 🔭 kesif7 — BTC / ETH çok günlük · PROTOKOL_kesif7.md")
yaz(f"veri: CoinMetrics {', '.join(f'{a} {len(v)} gün' for a, v in AK.items())} · korku endeksi {len(FG)} gün")
OLAY = []; XS = []
for cur, sym, ak in (("BTC", "BTCUSDT", "btc"), ("ETH", "ETHUSDT", "eth")):
    K, F = binance(sym); DV = dvol(cur); A = AK.get(ak)
    yaz(f"{cur}: mum {K.index.min().date()} → {K.index.max().date()} · fonlama {len(F)} · DVOL {len(DV)} gün · akış {len(A) if A is not None else 0} gün")
    gun = pd.date_range("2022-06-01", "2026-10-25", tz="UTC"); C = K.c; Cd = C.resample("1D").last()
    net7 = (A.FlowOutExNtv - A.FlowInExNtv).rolling(7).sum(); z_net = (net7 - net7.rolling(365, min_periods=200).mean().shift(1)) / net7.rolling(365, min_periods=200).std().shift(1)
    z_in = (A.FlowInExNtv - A.FlowInExNtv.rolling(365, min_periods=200).mean().shift(1)) / A.FlowInExNtv.rolling(365, min_periods=200).std().shift(1)
    fon3 = F.rolling("3D").mean()
    Hh, Lo, Op, Cl = K.h.values, K.l.values, K.o.values, K.c.values; tix = K.index
    cumF = F.cumsum()
    for D in gun:
        dv0, dv3 = DV.get(D, np.nan), DV.get(D - pd.Timedelta(days=3), np.nan)
        e = dict(t=D, varlik=cur,
                 dvol3=dv0 / dv3 - 1 if dv3 > 0 else np.nan,
                 znet=z_net.get(D - pd.Timedelta(days=2), np.nan), zin=z_in.get(D - pd.Timedelta(days=2), np.nan),
                 fg=FG.get(D - pd.Timedelta(days=1), np.nan),
                 r3=Cd.get(D - pd.Timedelta(days=1), np.nan) / Cd.get(D - pd.Timedelta(days=4), np.nan) - 1,
                 r7=Cd.get(D - pd.Timedelta(days=1), np.nan) / Cd.get(D - pd.Timedelta(days=8), np.nan) - 1,
                 fon3=fon3[:D - pd.Timedelta(seconds=1)].iloc[-1] if len(fon3[:D - pd.Timedelta(seconds=1)]) else np.nan)
        g0 = tix.searchsorted(D + pd.Timedelta(hours=1))
        if g0 + 14 * 24 >= len(tix) or tix[g0] != D + pd.Timedelta(hours=1): continue
        Pe = Op[g0] * (1 + SLIP); vals = []
        def fon(j):                                                                             # girişten j saatinin sonuna kadar ödenen fonlama
            a_, b_ = tix[g0], tix[g0 + j] + pd.Timedelta(hours=1)
            s = cumF[:b_].iloc[-1] - cumF[:a_].iloc[-1] if len(cumF[:a_]) else cumF[:b_].iloc[-1]
            son_ = pd.Timestamp("2026-10-01", tz="UTC")
            if b_ > son_: s += 0.0001 * (b_ - max(a_, son_)).total_seconds() / 28800
            return float(s)
        for T in TS:
            tp = Pe * (1 + T)
            for st in STOPS:
                sp = Pe * (1 - st) if st is not None else None
                for H in HS:
                    n = H * 24; hi, lo = Hh[g0:g0 + n], Lo[g0:g0 + n]
                    jt = int(np.argmax(hi >= tp)) if (hi >= tp).any() else 10 ** 6
                    js = int(np.argmax(lo <= sp)) if sp is not None and (lo <= sp).any() else 10 ** 6
                    if js < 10 ** 6 and js <= jt: p = min(sp, Op[g0 + js]) * (1 - KAY); net = p / Pe - 1 - 2 * FP - fon(js); w = p / Pe - 1
                    elif jt < 10 ** 6: net = T - FP - FL - fon(jt); w = lo[:jt + 1].min() / Pe - 1
                    else: net = Cl[g0 + n - 1] / Pe - 1 - 2 * FP - fon(n - 1); w = lo.min() / Pe - 1
                    vals += [net, w]
        OLAY.append(e); XS.append(vals)
M = pd.DataFrame(OLAY); X = np.array(XS, dtype="float64")
FIL = []
for a in (0.15, 0.25): FIL.append(("D1 DVOL korku sıçraması", f"DVOL 3g ≥ +{a:.0%}", lambda m, a=a: m.dvol3 >= a))
for a in (1.5, 2.5): FIL.append(("D2 borsadan net çıkış", f"z ≥ {a}", lambda m, a=a: m.znet >= a))
for a, b in itertools.product((2.5, 3.5), (0.0, -0.05)): FIL.append(("D3 giriş patlaması + düşüş", f"giriş z ≥ {a} · 3g ≤ {b:.0%}", lambda m, a=a, b=b: (m.zin >= a) & (m.r3 <= b)))
for a in (15, 25): FIL.append(("D4 aşırı korku", f"endeks ≤ {a}", lambda m, a=a: m.fg <= a))
for b in (-0.05, -0.10): FIL.append(("D5 negatif fonlama + düşüş", f"7g ≤ {b:.0%}", lambda m, b=b: (m.fon3 < 0) & (m.r7 <= b)))
U = lambda s: pd.Timestamp(s, tz="UTC")
DON = {"keşif 2022-06→2023": (U("2022-06-01"), U("2024-01-01")), "kontrol 2024": (U("2024-01-01"), U("2025-01-01")), "kontrol 2025→": (U("2025-01-01"), U("2027-01-01"))}
def sec(f):
    x = M[f(M).fillna(False)].sort_values("t"); keep, son = [], {}
    for i, t, v in zip(x.index, x.t, x.varlik):
        if v in son and t - son[v] < pd.Timedelta(days=3): continue
        son[v] = t; keep.append(i)
    return np.array(keep, dtype=int)
def olc(idx):
    R = {}
    for dn, (a, z) in DON.items():
        ii = idx[(M.t.values[idx] >= a.to_datetime64()) & (M.t.values[idx] < z.to_datetime64())]
        if not len(ii): R[dn] = None; continue
        net = X[ii][:, 0::2]; w = X[ii][:, 1::2]
        R[dn] = dict(n=len(ii), i=100 * (net > 0).mean(0), net=100 * net.mean(0), liq=(w <= -0.45).sum(0), kotu=100 * net.min(0))
    return R
hucre = lambda r, j: (f"{r['n']} · %{r['i'][j]:.0f} · {r['net'][j]:+.2f} · en kötü {r['kotu'][j]:+.1f}" if r else "0")
yaz(f"\nolay günü: {len(M)} · kural: {len(FIL)} giriş × {len(ADLAR)} çıkış = {len(FIL) * len(ADLAR)}")
yaz("_hücre: işlem · isabet · işlem başı net % · en kötü işlem %_\n")
gec, yak = [], []
for k, (aile, ad, f) in enumerate(FIL):
    R = olc(sec(f))
    for j, an in enumerate(ADLAR):
        rr = [R[d] for d in DON]
        if any(r is None for r in rr): continue
        ok = (rr[0]["n"] >= 8 and all(r["n"] >= 5 for r in rr[1:]) and all(r["i"][j] >= 70 and r["net"][j] >= 2.0 and r["liq"][j] == 0 for r in rr))
        mn = min(r["net"][j] for r in rr); mi = min(r["i"][j] for r in rr)
        (gec if ok else yak).append((mn, mi, k, j, R))
yaz(f"## Geçen: {len(gec)}")
for mn, mi, k, j, R in sorted(gec, key=lambda x: -x[0])[:3]: yaz(f"- ✅ {FIL[k][0]} · {FIL[k][1]} · {ADLAR[j]}: " + " | ".join(f"{d} {hucre(R[d], j)}" for d in DON))
yaz("\n## Bilgi — en yakınlar (üç dönemin en kötü isabeti en yüksek, en kötü dönem neti > 0)")
for mn, mi, k, j, R in sorted([y for y in yak if y[0] > 0], key=lambda x: -x[1])[:12]:
    yaz(f"- {FIL[k][0]} · {FIL[k][1]} · {ADLAR[j]}: " + " | ".join(f"{d} {hucre(R[d], j)}" for d in DON))
yaz("\n## Bilgi — aile başına en iyi (en kötü dönem neti)")
for aile in dict.fromkeys(a for a, _, _ in FIL):
    c = [y for y in gec + yak if FIL[y[2]][0] == aile]
    if c:
        mn, mi, k, j, R = max(c, key=lambda y: y[0]); yaz(f"- {aile} · {FIL[k][1]} · {ADLAR[j]}: " + " | ".join(f"{d} {hucre(R[d], j)}" for d in DON))
open("kesif7_sonuc.md", "w").write("\n".join(out) + "\n")
