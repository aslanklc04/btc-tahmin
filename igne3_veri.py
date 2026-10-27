# igne3_veri.py — PROTOKOL_igne3.md: iğne SONRASI alım (saatlik iğne + toparlanma), Binance VADELİ 1 dk. Parça I / N.
# k ≥ 4 adayları kaydedilir; k 6, BTC filtresi ve 24 s bekleme analizde uygulanır.
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
def saatlik(nm):
    sym, d = yukle(nm)
    if sym is None: return None
    a_m = int((BAS - pd.Timedelta(days=31)).timestamp() // 60); b_m = int(SON.timestamp() // 60) + 2 * 1440
    d = d.set_index("ot").reindex(np.arange(a_m, b_m)); On, Hh, Lo, C = d.o.values, d.h.values, d.l.values, d.c.values
    Cf = pd.Series(C).ffill().values; nh = (b_m - a_m) // 60
    O_h = On.reshape(nh, 60)[:, 0]; H_h = np.nanmax(np.where(np.isnan(Hh), -np.inf, Hh).reshape(nh, 60), 1); L_h = np.nanmin(np.where(np.isnan(Lo), np.inf, Lo).reshape(nh, 60), 1)
    C_h = Cf.reshape(nh, 60)[:, 59]
    return dict(sym=sym, a_m=a_m, On=On, Hn=np.nan_to_num(Hh, nan=-np.inf), Ln=np.nan_to_num(Lo, nan=np.inf), Cf=Cf, O_h=O_h, H_h=H_h, L_h=L_h, C_h=C_h)
BT = saatlik("BTC"); rb = pd.Series(BT["C_h"]).pct_change().values
print("BTC hazır", f"{time.time() - T0:.0f} sn", flush=True)
R = []
for nm, grup in benim:
    X = BT if nm == "BTC" else saatlik(nm)
    if X is None: EKSIK.append(nm); print(nm, "vadeli veri yok", flush=True); continue
    a_m, On, Hn, Ln, Cf, O_h, L_h, C_h = X["a_m"], X["On"], X["Hn"], X["Ln"], X["Cf"], X["O_h"], X["L_h"], X["C_h"]
    sd = pd.Series(np.log(C_h)).diff().rolling(720, min_periods=600).std().shift(1).values
    h0 = int((BAS.timestamp() // 60 - a_m) // 60)
    with np.errstate(invalid="ignore", divide="ignore"):
        kr = (O_h - L_h) / (O_h * sd); ok = (kr >= 4) & (C_h >= L_h + 0.5 * (O_h - L_h)) & np.isfinite(O_h) & np.isfinite(sd)
    n0 = len(R)
    for i in np.where(ok)[0]:
        if i < h0: continue
        m0 = (i + 1) * 60; e = m0 + 7
        if m0 + 24 * 60 >= len(On) or not np.isfinite(On[e]): continue
        Pe, tp = On[e], O_h[i]
        row = dict(t=pd.Timestamp((a_m + m0) * 60, unit="s", tz="UTC"), nm=nm, grup=grup, kr=kr[i], rb=rb[i], P=Pe, hedef=tp)
        for H in (4, 24):
            end = m0 + H * 60 - 1
            if tp <= Pe: net, je = -2 * FP, e
            else:
                w = np.where(Hn[e:end + 1] >= tp)[0]
                if len(w): je = e + int(w[0]); net = tp / Pe - 1 - FP - FL - FON * nfon(a_m + e, a_m + je + 1)
                else: je = end; net = Cf[end] / Pe - 1 - FP - FP - FON * nfon(a_m + e, a_m + je + 1)
            seg = Ln[e:je + 1]; seg = seg[np.isfinite(seg)]
            row[f"n{H}"] = net; row[f"mae{H}"] = seg.min() / Pe - 1 if len(seg) else np.nan
        R.append(row)
    print(f"{nm} ({X['sym']}, {grup}) · {len(R) - n0} aday · {time.time() - T0:.0f} sn", flush=True)
pd.DataFrame(R).to_csv(f"igne3_p{I}.csv.gz", index=False, compression="gzip")
open(f"igne3_eksik_p{I}.txt", "w").write("\n".join(EKSIK))
print("bitti", len(R), f"{time.time() - T0:.0f} sn")
