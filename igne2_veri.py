# igne2_veri.py — PROTOKOL_igne2.md: günlük derin limit (d 3/4 · hedef P · stop yok/S½/S1), Binance VADELİ 1 dk. Parça I / N (coin'e göre).
# Trend filtresi analizde uygulanır (burada tüm günler kaydedilir).
import sys, io, time, zipfile, numpy as np, pandas as pd, requests
I, N = int(sys.argv[1]), int(sys.argv[2]); T0 = time.time()
FL, FP, FON, KAY = 0.0002, 0.0005, 0.0001, 0.003
DB = (3, 4); STOP = (("yok", None), ("S05", 0.5), ("S1", 1.0))
ESKI = ["BTC", "ADA", "APT", "ARB", "BNB", "DOGE", "DOT", "ETH", "FLOKI", "LINK", "NEAR", "OP", "PEPE", "SHIB", "SUI"]
YENI = [x.strip()[:-4] for x in open("igne2_evren.txt") if x.strip()]
BAS, SON = pd.Timestamp("2022-06-01", tz="UTC"), pd.Timestamp("2026-10-26", tz="UTC")
URL = "https://data.binance.vision/data/futures/um"
coins = [(c, "yeni") for c in YENI] + [(c, "eski") for c in ESKI]; benim = coins[I::N]
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
def yukle(nm):
    """Coin'in tüm dakika verisi (aylık zip'ler + Ekim 2026 günlük). Sembol: nm+USDT, yoksa 1000+nm+USDT."""
    aylar = pd.period_range("2022-05", "2026-09", freq="M").strftime("%Y-%m")
    for sym in (f"{nm}USDT", f"1000{nm}USDT"):
        parts = []
        for ay in aylar:
            b = indir(f"{URL}/monthly/klines/{sym}/1m/{sym}-1m-{ay}.zip")
            if b: parts.append(oku(b))
        for g in pd.date_range("2026-10-01", "2026-10-25").strftime("%Y-%m-%d"):
            b = indir(f"{URL}/daily/klines/{sym}/1m/{sym}-1m-{g}.zip")
            if b: parts.append(oku(b))
        if parts: return sym, pd.concat(parts).drop_duplicates("ot").sort_values("ot")
    return None, None
def nfon(a, b): return b // 480 - a // 480
def islem(On, Hn, Ln, Cf, j, end, tp, Pe, st, a_m):
    """Dolum j (Pe = L). Dönüş: (net, çıkış fiyatı / Pe − 1, dolumdan sonra en düşük / Pe − 1)."""
    e_m = a_m + j
    js = None
    if st is not None:
        w = np.where(Ln[j:end + 1] <= st)[0]; js = j + int(w[0]) if len(w) else None
    w = np.where(Hn[j + 1:end + 1] >= tp)[0] if j + 1 <= end else []; jt = j + 1 + int(w[0]) if len(w) else None
    if js is not None and (jt is None or js <= jt):
        p = min(st, On[js] if np.isfinite(On[js]) else st, (st + Ln[js]) / 2) * (1 - KAY); je = js          # Ek: çöküş dakikasında stop ile dakikanın dibi arası (kötümser)
        net = p / Pe - 1 - FL - FP - FON * nfon(e_m, a_m + je + 1)
    elif jt is not None:
        p = tp; je = jt; net = p / Pe - 1 - FL - FL - FON * nfon(e_m, a_m + je + 1)
    else:
        p = Cf[end]; je = end; net = p / Pe - 1 - FL - FP - FON * nfon(e_m, a_m + je + 1)
    seg = Ln[j:je + 1]; seg = seg[np.isfinite(seg)]
    return net, p / Pe - 1, (seg.min() / Pe - 1) if len(seg) else np.nan
R = []
for nm, grup in benim:
    sym, d = yukle(nm)
    if sym is None: EKSIK.append(nm); print(nm, "vadeli veri yok", flush=True); continue
    a_m = int((BAS - pd.Timedelta(days=31)).timestamp() // 60); b_m = int(SON.timestamp() // 60) + 2 * 1440
    d = d.set_index("ot").reindex(np.arange(a_m, b_m)); On, Hh, Lo, C = d.o.values, d.h.values, d.l.values, d.c.values
    idx = np.arange(a_m, b_m); Ch = pd.Series(C, index=idx).ffill(); hc = Ch[(idx % 60) == 59]
    sd = np.log(hc).diff().rolling(720, min_periods=600).std()
    Hn = np.nan_to_num(Hh, nan=-np.inf); Ln = np.nan_to_num(Lo, nan=np.inf); Cf = Ch.values
    n0 = len(R)
    for D in pd.date_range(BAS, SON - pd.Timedelta(days=1)):
        d0 = int(D.timestamp() // 60); i0 = d0 - a_m
        if i0 + 2 * 1440 > len(On) or not np.isfinite(On[i0]): continue
        s_ = sd.get(d0 - 1, np.nan)
        if not np.isfinite(s_): continue
        P = On[i0]; sg = s_ * np.sqrt(24)
        for dd in DB:
            L = P * (1 - dd * sg); w = np.where(Ln[i0:i0 + 1440] < L)[0]
            row = dict(gun=D.date(), nm=nm, grup=grup, d=dd, P=P, L=L, sg=sg)
            if len(w):
                j = i0 + int(w[0]); end = min(j + 1440, len(On) - 1)
                for ad, k in STOP:
                    st = None if k is None else L * (1 - k * dd * sg)
                    if st is not None and st <= 0: st = None
                    net, cx, mae = islem(On, Hn, Ln, Cf, j, end, P, L, st, a_m)
                    row[ad] = net; row[ad + "_cik"] = cx; row[ad + "_mae"] = mae
            R.append(row)
    print(f"{nm} ({sym}, {grup}) · {len(R) - n0} satır · {time.time() - T0:.0f} sn", flush=True)
pd.DataFrame(R).to_csv(f"igne2_p{I}.csv.gz", index=False, compression="gzip")
open(f"igne2_eksik_p{I}.txt", "w").write("\n".join(EKSIK))
print("bitti", len(R), f"{time.time() - T0:.0f} sn")
