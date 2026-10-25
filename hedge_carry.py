# hedge_carry.py — PROTOKOL_hedge_carry.md (kod sonuçtan önce kaydedildi)
import io, sys, json, time, zipfile, requests, numpy as np, pandas as pd
sys.path.insert(0, "canli"); from ortak import fetch_1h
from concurrent.futures import ThreadPoolExecutor
T0 = time.time(); S = requests.Session(); L = []; yaz = lambda s="": (print(s, flush=True), L.append(s))
A = "https://data.binance.vision/data/futures/um/monthly"
V = pd.read_csv("veri_seti.csv.gz"); V["t"] = pd.to_datetime(V.t, utc=True)
LS = json.load(open("sekil_liste.json")); COINS = sorted(set(V.nm) | set(LS["A"]) | set(LS["B"]) | {"BTC"})
def spot(c):
    try: o = fetch_1h(pd.Timestamp("2021-12-01", tz="UTC").timestamp() * 1000, time.time() * 1000, sym=f"{c}USDT"); return c, o.close.astype(float)
    except Exception: return c, None
with ThreadPoolExecutor(10) as ex: SP = {c: s for c, s in ex.map(spot, COINS) if s is not None}
yaz(f"spot fiyat: {len(SP)} coin · {time.time() - T0:.0f} sn")
A25, A26, Y2, P0, K0 = (pd.Timestamp(x, tz="UTC") for x in ("2025-01-01", "2026-01-01", "2023-07-01", "2022-06-01", "2022-01-01"))
yaz(f"# 🛡️ BTC korumalı sinyal + 💰 fonlama kazancı — PROTOKOL_hedge_carry.md · {pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M}\n")
# ======================= (1) BTC korumalı sinyal =======================
B = SP["BTC"]; R = []
for r in V.itertuples():
    c = SP.get(r.nm)
    if c is None: continue
    t1 = r.t + pd.Timedelta(hours=int(r.H))
    if r.t not in c.index or t1 not in c.index or r.t not in B.index or t1 not in B.index: continue
    cr = c[t1] / (c[r.t] * 1.001) - 1; br = B[t1] / (B[r.t] * 0.9998) - 1
    R.append((r.t, r.sinif, cr - 0.001 - 0.0001 * r.H / 8, cr - br - 0.002))
H1 = pd.DataFrame(R, columns=["t", "sinif", "yalin", "koru"]); SON = H1.t.max() + pd.Timedelta(hours=1)
def olc(d, c):
    if len(d) == 0: return dict(n=0, ii=np.nan, si=np.nan, net=np.nan)
    sp = d.groupby("t")[c].mean(); return dict(n=len(d), ii=100 * (d[c] > 0).mean(), si=100 * (sp > 0).mean(), net=100 * d[c].mean())
yaz(f"## (1) BTC'ye karşı korumalı sinyal — {len(H1):,} sinyal · n · işlem isabeti · saat isabeti · işlem başı net % (korumasız → korumalı)")
DON = [("keşif ½-1", P0, Y2), ("keşif ½-2", Y2, A25), ("KONTROL 2025+", A25, SON), ("KONTROL 2026", A26, SON)]
for sn in ["✅ ana (+0,75σ)", "🔸 yedek (+0,50σ)", "📋 panelden (+0,45σ)"]:
    d = H1[H1.sinif == sn]; sat = []; ok = True
    for dn, a, z in DON:
        x = d[(d.t >= a) & (d.t < z)]; u, k = olc(x, "yalin"), olc(x, "koru")
        g = k["n"] > 0 and k["ii"] >= u["ii"] + 5 and k["net"] > 0 and k["si"] >= u["si"] + 5; ok &= g
        sat.append(f"{dn}: {k['n']} · %{u['ii']:.0f}→%{k['ii']:.0f} · saat %{u['si']:.0f}→%{k['si']:.0f} · {u['net']:+.2f}→{k['net']:+.2f} {'✅' if g else '❌'}")
    yaz(f"- **{sn}**: " + " | ".join(sat) + f" → {'**GEÇTİ**' if ok else 'geçmedi'}")
# ======================= (2) fonlama kazancı =======================
def zipcsv(url):
    for k in range(4):
        try:
            r = S.get(url, timeout=40)
            if r.status_code == 404: return None
            if r.status_code == 200: z = zipfile.ZipFile(io.BytesIO(r.content)); return pd.read_csv(z.open(z.namelist()[0]))
        except Exception: time.sleep(2 + 2 * k)
    return None
AY = pd.date_range(K0, pd.Timestamp("2026-09-01", tz="UTC"), freq="MS")
def vadeli(c):
    f = [x for x in (zipcsv(f"{A}/fundingRate/{c}USDT/{c}USDT-fundingRate-{m:%Y-%m}.zip") for m in AY) if x is not None]
    if not f: return c, None, None
    f = pd.concat(f); fr = pd.DataFrame({"r": f.last_funding_rate.astype(float).values, "iv": f.get("funding_interval_hours", pd.Series(8, index=f.index)).astype(float).values},
                                        index=pd.to_datetime(f.calc_time.astype("int64"), unit="ms", utc=True)).sort_index(); fr = fr[~fr.index.duplicated()]
    k = [x for x in (zipcsv(f"{A}/klines/{c}USDT/1h/{c}USDT-1h-{m:%Y-%m}.zip") for m in AY) if x is not None]
    if not k: return c, fr, None
    k = pd.concat(k); k = k[pd.to_numeric(k.iloc[:, 0], errors="coerce").notna()]
    p = pd.Series(k.iloc[:, 4].astype(float).values, index=pd.to_datetime(k.iloc[:, 0].astype("int64"), unit="ms", utc=True) + pd.Timedelta(hours=1)).sort_index()
    return c, fr, p[~p.index.duplicated()]
with ThreadPoolExecutor(8) as ex: VD = {c: (fr, p) for c, fr, p in ex.map(vadeli, [c for c in COINS if c in SP]) if fr is not None and p is not None}
yaz(f"\n_vadeli verisi olan coin: {len(VD)} · {time.time() - T0:.0f} sn_")
def carry(c, X):
    fr, pp = VD[c]; sp = SP[c]; out = []; acik = None; r8 = fr.r * 8 / fr.iv.clip(lower=1); ort3 = r8.rolling(3).mean()
    for i, (tf, row) in enumerate(fr.iterrows()):
        if acik is None:
            if ort3.iloc[i] >= X:
                e = tf.floor("h") + pd.Timedelta(hours=1)
                if e in sp.index and e in pp.index: acik = dict(e=e, se=sp[e], pe=pp[e], fon=0.0)
        else:
            if tf > acik["e"]: acik["fon"] += row.r
            if tf > acik["e"] and (r8.iloc[i] < 0.0001 or tf - acik["e"] >= pd.Timedelta(days=14)):
                x = tf.floor("h") + pd.Timedelta(hours=1)
                if x in sp.index and x in pp.index:
                    net = (sp[x] / acik["se"] - 1) - (pp[x] / acik["pe"] - 1) + acik["fon"] - 0.003 - 0.001
                    out.append((acik["e"], c, net, (x - acik["e"]).total_seconds() / 86400))
                acik = None
    return out
yaz("\n## (2) 💰 Fonlama kazancı (spot al + vadeli sat; fonlama son 3 ort. ≥ X iken gir, son fonlama < %0,01 ya da 14 gün → çık)")
yaz("_n işlem · isabet · işlem başı net % · en kötü % · ort. gün · yaklaşık yıllık (sermaye = spot × 1,5, coin başına sürekli bir pozisyon varsayımıyla değil, işlem başı getiri / gün × 365 / 1,5)_")
for X in (0.0003, 0.0005, 0.001):
    T = pd.DataFrame([z for c in VD for z in carry(c, X)], columns=["t", "c", "net", "gun"]); sat = []; ok = True
    for dn, g, a, z in (("keşif ½-1", "A", K0, Y2), ("keşif ½-2", "A", Y2, A25), ("KONTROL A 2025+", "A", A25, SON), ("KONTROL B dokunulmamış", "B", K0, SON)):
        e = T[T.c.isin(LS[g]) & (T.t >= a) & (T.t < z)]; ay_ = max(1, (z - a).days / 30.4)
        if len(e) == 0: sat.append(f"{dn}: 0 ❌"); ok = False; continue
        ii, nt, kt, gn = 100 * (e.net > 0).mean(), 100 * e.net.mean(), 100 * e.net.min(), e.gun.mean()
        g_ = ii >= 70 and nt >= 0.30 and len(e) / ay_ >= 2 and kt >= -10; ok &= g_
        sat.append(f"{dn}: {len(e)} · %{ii:.0f} · {nt:+.2f} · en kötü {kt:+.1f} · {gn:.1f} gün · yıllık ~%{nt / gn * 365 / 1.5:.0f} {'✅' if g_ else '❌'}")
    yaz(f"- **X = %{100 * X:.2f}**: " + " | ".join(sat) + f" → {'**GEÇTİ**' if ok else 'geçmedi'}")
yaz(f"\n_6 deneme · süre {time.time() - T0:.0f} sn_")
open("hedge_carry_sonuc.md", "w").write("\n".join(L) + "\n")
