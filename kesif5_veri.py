# kesif5_veri.py — PROTOKOL_kesif5.md: 5 olay ailesinin adayları + 18 çıkış kuralı (vadeli 1 s mum + gerçek fonlama). Parça I / N.
import sys, io, time, zipfile, numpy as np, pandas as pd, requests
from numpy.lib.stride_tricks import sliding_window_view as swv
I, N = int(sys.argv[1]), int(sys.argv[2]); T0 = time.time()
FL, FP, KAY, SLIP = 0.0002, 0.0005, 0.003, 0.001
TS = (0.03, 0.05, 0.08); STOPS = ("yok", "S"); HS = (24, 72, 120)
ADLAR = [f"T{t}_{s}_H{h}" for t in TS for s in STOPS for h in HS]
A0 = pd.Timestamp("2022-04-01", tz="UTC"); BAS = pd.Timestamp("2022-06-01", tz="UTC"); SON = pd.Timestamp("2026-10-26", tz="UTC")
NH = int((SON - A0) / pd.Timedelta(hours=1)); h0 = int((BAS - A0) / pd.Timedelta(hours=1))
URL = "https://data.binance.vision/data/futures/um"
S = requests.Session()
def indir(u):
    for k in range(5):
        try:
            r = S.get(u, timeout=60)
            if r.status_code == 404: return None
            if r.status_code == 200: return r.content
        except Exception: pass
        time.sleep(2 + 3 * k)
    return None
def zcsv(b, cols):
    z = zipfile.ZipFile(io.BytesIO(b)); d = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=cols)
    return d[pd.to_numeric(d[cols[0]], errors="coerce").notna()].astype(float)
AYLAR = pd.period_range("2022-04", "2026-09", freq="M").strftime("%Y-%m")
def mumlar(sym):
    P = []
    for ay in AYLAR:
        b = indir(f"{URL}/monthly/klines/{sym}/1h/{sym}-1h-{ay}.zip")
        if b: P.append(zcsv(b, [0, 1, 2, 3, 4, 7]))
    for g in pd.date_range("2026-10-01", "2026-10-25").strftime("%Y-%m-%d"):
        b = indir(f"{URL}/daily/klines/{sym}/1h/{sym}-1h-{g}.zip")
        if b: P.append(zcsv(b, [0, 1, 2, 3, 4, 7]))
    if not P: return None
    d = pd.concat(P); d.columns = ["ot", "o", "h", "l", "c", "qv"]; d.loc[d.ot > 1e14, "ot"] = d.ot / 1000
    d["i"] = ((d.ot / 1000 - A0.timestamp()) // 3600).astype(np.int64)
    d = d[(d.i >= 0) & (d.i < NH)].drop_duplicates("i").set_index("i").reindex(np.arange(NH))
    return d
def fonlama(sym):
    P = []
    for ay in AYLAR:
        b = indir(f"{URL}/monthly/fundingRate/{sym}/{sym}-fundingRate-{ay}.zip")
        if b:
            z = zipfile.ZipFile(io.BytesIO(b)); d = pd.read_csv(z.open(z.namelist()[0]))
            d.columns = [c.strip().lower() for c in d.columns]
            tc = [c for c in d.columns if "time" in c][0]; rc = [c for c in d.columns if "rate" in c][-1]
            P.append(pd.DataFrame({"t": pd.to_numeric(d[tc], errors="coerce"), "r": pd.to_numeric(d[rc], errors="coerce")}).dropna())
    if not P: return None
    f = pd.concat(P).drop_duplicates("t").sort_values("t"); f.loc[f.t > 1e14, "t"] = f.t / 1000
    return f.reset_index(drop=True)
SY = pd.read_csv("igne4_semboller.csv"); SY = list(zip(SY.sym, SY.grup)); benim = SY[I::N]
print(f"parça {I}/{N}: {len(benim)} sembol", flush=True)
B = mumlar("BTCUSDT"); Bc = B.c.ffill().values
btc24 = Bc / np.roll(Bc, 24) - 1; btc7 = Bc / np.roll(Bc, 168) - 1
print("BTC hazır", f"{time.time() - T0:.0f} sn", flush=True)
FON_SON = pd.Timestamp("2026-10-01", tz="UTC").timestamp() * 1000
META, XS = [], []
for sym, grup in benim:
    d = B if sym == "BTCUSDT" else mumlar(sym)
    if d is None: print(sym, "veri yok", flush=True); continue
    F = fonlama(sym)
    O, Hh, Lo, C, QV = d.o.values, d.h.values, d.l.values, d.c.values, d.qv.fillna(0).values
    Cf = pd.Series(C).ffill().values; Hn = np.nan_to_num(Hh, nan=-np.inf); Ln = np.nan_to_num(Lo, nan=np.inf)
    lc = np.log(pd.Series(Cf)); sd = lc.diff().rolling(720, min_periods=600).std().shift(1).values
    with np.errstate(invalid="ignore", divide="ignore"):
        r24 = Cf / np.roll(Cf, 24) - 1; r7 = Cf / np.roll(Cf, 168) - 1
        z72 = (lc - lc.shift(72)).values / (sd * np.sqrt(72))
        q24 = pd.Series(QV).rolling(24).sum().values; q30 = pd.Series(QV).rolling(720).sum().shift(24).values / 30; vr = q24 / q30
        hmax30 = pd.Series(Hn).rolling(720).max().shift(1).values; pos30 = Cf / hmax30
        pb = Cf / pd.Series(Hn).rolling(24).max().values - 1
        liq = pd.Series(QV).rolling(168).sum().values / 7
    low72 = pd.Series(Ln).rolling(72).min().values
    W = swv(np.concatenate([np.full(71, np.inf), Ln]), 72); lowage = 71 - W.argmin(1)               # 72 saatin dibinden bu yana geçen saat
    # fonlama: saat i kapanışında bilinen son oran ve son 90 ödemedeki yüzdeliği
    fr = np.full(NH, np.nan); fp = np.full(NH, np.nan)
    if F is not None and len(F) > 30:
        ft = F.t.values; rv = F.r.values; pct = pd.Series(rv).rolling(90, min_periods=30).apply(lambda x: (x <= x[-1]).mean(), raw=True).values
        kap = (A0.timestamp() + (np.arange(NH) + 1) * 3600) * 1000; ix = np.searchsorted(ft, kap, side="right") - 1
        ok = ix >= 0; fr[ok] = rv[ix[ok]]; fp[ok] = pct[ix[ok]]
    kapT = (A0.timestamp() + (np.arange(NH) + 1) * 3600) * 1000                               # saat kapanışları (ms)
    cumF = np.concatenate([[0.0], np.cumsum(F.r.values)])[np.searchsorted(F.t.values, kapT, side="right")] if F is not None and len(F) else np.zeros(NH)
    def fon_maliyet(a_i, b_i):                                                                  # giriş saati açılışı → çıkış saati kapanışı arasındaki ödemeler
        s = cumF[b_i] - cumF[a_i - 1]; tb = kapT[b_i]; ta = kapT[a_i - 1]
        if tb > FON_SON: s += 0.0001 * max(0, (tb - max(ta, FON_SON)) / 28_800_000)          # Ekim 2026: arşiv yok → %0,01 / 8 s
        return s
    with np.errstate(invalid="ignore"):
        tet = ((z72 <= -3) | ((fr < 0) & (fp <= 0.05)) | ((vr >= 3) & (pos30 >= 0.98)) | ((r7 - btc7 >= 0.15) & (pb <= -0.05)) | ((btc24 >= 0.03) & (r24 - btc24 <= -0.02))) & (liq >= 2e6)
    n0 = len(META)
    for i in np.where(tet)[0]:
        if i < h0 or i + 121 >= NH or not np.isfinite(O[i + 1]) or not np.isfinite(Cf[i + 120]) or np.isnan(C[i]): continue
        Pe = O[i + 1] * (1 + SLIP); st = low72[i] * 0.99
        st = st if (np.isfinite(st) and st < Pe) else None
        hi, lo, op = Hn[i + 1:i + 121], Ln[i + 1:i + 121], O[i + 1:i + 121]
        js_all = int(np.argmax(lo <= st)) if st is not None and (lo <= st).any() else 999
        vals = []
        for T in TS:
            tp = Pe * (1 + T); jt_all = int(np.argmax(hi >= tp)) if (hi >= tp).any() else 999
            for sn in STOPS:
                js = js_all if sn == "S" else 999
                for H in HS:
                    en = H - 1
                    if js <= en and js <= jt_all:
                        p = min(st, op[js] if np.isfinite(op[js]) else st) * (1 - KAY); net = p / Pe - 1 - 2 * FP - fon_maliyet(i + 1, i + 1 + js); w = p / Pe - 1
                    elif jt_all <= en:
                        net = T - FP - FL - fon_maliyet(i + 1, i + 1 + jt_all); w = lo[:jt_all + 1].min() / Pe - 1
                    else:
                        net = Cf[i + 1 + en] / Pe - 1 - 2 * FP - fon_maliyet(i + 1, i + 1 + en); w = lo[:en + 1].min() / Pe - 1
                    vals += [net, w]
        META.append(dict(t=A0 + pd.Timedelta(hours=int(i) + 1), sym=sym, grup=grup, z72=z72[i], lowage=int(lowage[i]), fr=fr[i], fp=fp[i], r24=r24[i], vr=vr[i], pos30=pos30[i],
                         r7rel=r7[i] - btc7[i], pb=pb[i], btc24=btc24[i], liq=liq[i], Pe=Pe))
        XS.append(np.array(vals, dtype="float32"))
    print(f"{sym} ({grup}) · {len(META) - n0} aday · {time.time() - T0:.0f} sn", flush=True)
pd.DataFrame(META).to_csv(f"kesif5_meta_p{I}.csv.gz", index=False, compression="gzip")
np.save(f"kesif5_X_p{I}.npy", np.stack(XS) if XS else np.zeros((0, 2 * len(ADLAR)), "float32"))
print("bitti", len(META), f"{time.time() - T0:.0f} sn")
