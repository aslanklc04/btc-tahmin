# igne_veri.py — PROTOKOL_igne.md: Binance VADELİ 1 dk mumla A (sinyallere ikinci kademe) ve B (günlük derin limit) işlemleri. Parça I / N (coin'e göre).
import sys, io, time, zipfile, numpy as np, pandas as pd, requests
I, N = int(sys.argv[1]), int(sys.argv[2]); T0 = time.time()
FL, FP, FON = 0.0002, 0.0005, 0.0001
KS = {"✅ ana (+0,75σ)": 0.75, "🔸 yedek (+0,50σ)": 0.5, "📋 panelden (+0,45σ)": 0.45}
DA = (0.5, 1.0, 1.5, 2.0); DB = (2, 3, 4)
EVREN_B = ["BTC", "ADA", "APT", "ARB", "BNB", "DOGE", "DOT", "ETH", "FLOKI", "LINK", "NEAR", "OP", "PEPE", "SHIB", "SUI"]
BAS, SON = pd.Timestamp("2022-06-01", tz="UTC"), pd.Timestamp("2026-10-26", tz="UTC")
URL = "https://data.binance.vision/data/futures/um"
V = pd.read_csv("veri_seti.csv.gz", usecols=["t", "nm", "sinif", "H", "s"]); V["t"] = pd.to_datetime(V.t, utc=True)
yuk = V.groupby("nm").size().to_dict()
for c in EVREN_B: yuk[c] = yuk.get(c, 0) + 3000
coins = sorted(yuk, key=lambda c: -yuk[c]); benim = coins[I::N]
print(f"parça {I}/{N}: {len(benim)} coin", flush=True)
S = requests.Session(); EKSIK = []
def indir(u):
    for k in range(5):
        try:
            r = S.get(u, timeout=60)
            if r.status_code == 404: return None
            if r.status_code == 200: return r.content
        except Exception: pass
        time.sleep(2 + 3 * k)
    return None
def oku(b):
    z = zipfile.ZipFile(io.BytesIO(b)); d = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=[0, 1, 2, 3, 4])
    d = d[pd.to_numeric(d[0], errors="coerce").notna()].astype(float); d.columns = ["ot", "o", "h", "l", "c"]
    d.loc[d.ot > 1e14, "ot"] = d.ot / 1000; d["ot"] = (d.ot // 60000).astype(np.int64); return d
def sembol(nm):
    tt = sorted(V.t[V.nm == nm]); ornek = [x.strftime("%Y-%m-%d") for x in (tt[:1] + tt[len(tt) // 2:len(tt) // 2 + 1] + tt[-1:])] if tt else []
    for s in (f"{nm}USDT", f"1000{nm}USDT"):
        for gun in ornek + ["2024-06-03", "2025-06-02", "2026-09-01", "2023-08-01"]:
            if indir(f"{URL}/daily/klines/{s}/1m/{s}-1m-{gun}.zip") is not None: return s
    return None
class Mum:
    """Dakika dizisi önbelleği: aylık zip (eski aylar) ya da günlük zip."""
    def __init__(s, sym): s.sym, s.ay, s.gun = sym, {}, {}
    def ay_yukle(s, ay):
        if ay not in s.ay:
            b = indir(f"{URL}/monthly/klines/{s.sym}/1m/{s.sym}-1m-{ay}.zip"); s.ay[ay] = oku(b) if b else None
        return s.ay[ay]
    def gun_yukle(s, g):
        if g not in s.gun:
            b = indir(f"{URL}/daily/klines/{s.sym}/1m/{s.sym}-1m-{g}.zip"); s.gun[g] = oku(b) if b else None
        return s.gun[g]
    def aralik(s, a_m, b_m, aylik=False):
        """[a_m, b_m) dakika aralığı (epoch dakika) → O, H, L, C dizileri (eksik dakika NaN)."""
        gunler = pd.date_range(pd.Timestamp(a_m * 60, unit="s", tz="UTC").normalize(), pd.Timestamp((b_m - 1) * 60, unit="s", tz="UTC").normalize())
        parts = []
        for g in gunler:
            d = None
            if aylik and g < pd.Timestamp("2026-10-01", tz="UTC"):
                m = s.ay_yukle(g.strftime("%Y-%m"))
                if m is not None:
                    a0 = int(g.timestamp() // 60); d = m[(m.ot >= a0) & (m.ot < a0 + 1440)]
            if d is None or not len(d): d = s.gun_yukle(g.strftime("%Y-%m-%d"))
            if d is not None and len(d): parts.append(d)
        if not parts: return None
        d = pd.concat(parts).drop_duplicates("ot").set_index("ot").reindex(np.arange(a_m, b_m))
        return d.o.values, d.h.values, d.l.values, d.c.values
def nfon(a, b): return b // 480 - a // 480                                                     # a, b: epoch dakika (giriş, çıkış)
def cik(Hh, C, j0, end, tp, Pe, fin, e_m, t0m):
    """j0'dan end'e kadar Hh ≥ tp → tp (limit), yoksa C[end] (piyasa). Dönüş (net, çıkış indeksi)."""
    if tp <= Pe: return Pe / Pe - 1 - fin - FP, j0
    if j0 <= end:
        w = np.where(Hh[j0:end + 1] >= tp)[0]
        if len(w): j = j0 + int(w[0]); return tp / Pe - 1 - fin - FL - FON * nfon(e_m, t0m + j + 1), j
    return C[end] / Pe - 1 - fin - FP - FON * nfon(e_m, t0m + end + 1), end
RA, RB = [], []
for nm in benim:
    sym = sembol(nm)
    if sym is None: EKSIK.append(nm); print(nm, "vadeli sembol yok", flush=True); continue
    M = Mum(sym); aylik = nm in EVREN_B
    # ---- A: sinyaller
    for r in V[V.nm == nm].itertuples():
        H = int(r.H); Hb = H * 60; t0m = int(r.t.timestamp() // 60); x = M.aralik(t0m, t0m + Hb + 70, aylik)
        if x is None: continue
        O, Hh, Lo, C = x
        if np.isnan(O[:Hb]).mean() > 0.01 or np.isnan(O[0]) or np.isnan(C[Hb - 1]): continue
        Hh = np.nan_to_num(Hh, nan=-np.inf); Lo = np.nan_to_num(Lo, nan=np.inf); C = pd.Series(C).ffill().values
        Gf = O[0]; k = KS[r.sinif]; tp = Gf * (1 + k * r.s); end = Hb - 1
        row = dict(t=r.t, nm=nm, sinif=r.sinif, H=H)
        if not np.isnan(O[7]) and O[7] <= Gf: b, _ = cik(Hh, C, 7, end, tp, O[7], FP, t0m + 7, t0m)
        else:
            w = np.where(Lo[8:67] < Gf)[0]
            b = cik(Hh, C, 9 + int(w[0]), end, tp, Gf, FL, t0m + 8 + int(w[0]), t0m)[0] if len(w) else np.nan
        row["B"] = b
        for d in DA:
            L = Gf * (1 - d * r.s); w = np.where(Lo[7:end + 1] < L)[0]
            if not len(w): row[f"d{d}_E1"] = row[f"d{d}_E2"] = row[f"d{d}_mae"] = np.nan; continue
            j = 7 + int(w[0])
            n1, j1 = cik(Hh, C, j + 1, end, tp, L, FL, t0m + j, t0m); n2, j2 = cik(Hh, C, j + 1, end, Gf, L, FL, t0m + j, t0m)
            row[f"d{d}_E1"], row[f"d{d}_E2"] = n1, n2; row[f"d{d}_mae"] = np.nanmin(Lo[j:j1 + 1][np.isfinite(Lo[j:j1 + 1])]) / L - 1
        RA.append(row)
    print(f"{nm} A bitti · {len(RA)} satır · {time.time() - T0:.0f} sn", flush=True)
    # ---- B: günlük derin limit
    if nm in EVREN_B:
        a_m = int((BAS - pd.Timedelta(days=31)).timestamp() // 60); b_m = int(SON.timestamp() // 60) + 2 * 1440
        x = M.aralik(a_m, b_m, True)
        if x is None: print(nm, "B verisi yok", flush=True); continue
        O, Hh, Lo, C = x; idx = np.arange(a_m, b_m)
        Ch = pd.Series(C, index=idx).ffill(); hc = Ch[(idx % 60) == 59]                       # saat kapanışları (dakika 59 kapanışı)
        lr = np.log(hc).diff(); sd = lr.rolling(720, min_periods=600).std()                  # indeks: saatin son dakikası
        Hn = np.nan_to_num(Hh, nan=-np.inf); Ln = np.nan_to_num(Lo, nan=np.inf); Cf = Ch.values
        for D in pd.date_range(BAS, SON - pd.Timedelta(days=1)):
            d0 = int(D.timestamp() // 60); i0 = d0 - a_m
            if i0 + 2 * 1440 >= len(O) or np.isnan(O[i0]): continue
            s_ = sd.get(d0 - 1, np.nan)
            if not np.isfinite(s_): continue
            P = O[i0]; sg = s_ * np.sqrt(24)
            for d in DB:
                L = P * (1 - d * sg); w = np.where(Ln[i0:i0 + 1440] < L)[0]
                row = dict(gun=D.date(), nm=nm, d=d, P=P, L=L, sg=sg)
                if len(w):
                    j = i0 + int(w[0]); end = min(j + 1440, len(O) - 1)
                    for X, tp in (("X1", L + 0.5 * (P - L)), ("X2", P)):
                        n_, je = cik(Hn, Cf, j + 1, end, tp, L, FL, a_m + j, a_m)
                        row[X] = n_; row[X + "_mae"] = np.min(Ln[j:je + 1][np.isfinite(Ln[j:je + 1])]) / L - 1; row[X + "_dk"] = je - j
                RB.append(row)
        print(f"{nm} B bitti · {len(RB)} satır · {time.time() - T0:.0f} sn", flush=True)
    M.ay.clear(); M.gun.clear()
pd.DataFrame(RA).to_csv(f"igneA_p{I}.csv.gz", index=False, compression="gzip")
pd.DataFrame(RB).to_csv(f"igneB_p{I}.csv.gz", index=False, compression="gzip")
open(f"igne_eksik_p{I}.txt", "w").write("\n".join(EKSIK))
print("bitti", len(RA), len(RB), f"{time.time() - T0:.0f} sn")
