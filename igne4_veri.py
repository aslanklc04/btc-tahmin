# igne4_veri.py — PROTOKOL_igne4.md: iğne adayları (kr ≥ 3) + 64 çıkış kuralının sonucu, Binance VADELİ 5 dk. Parça I / N (sembole göre).
import sys, io, re, time, zipfile, numpy as np, pandas as pd, requests
I, N = int(sys.argv[1]), int(sys.argv[2]); T0 = time.time()
FL, FP, FON, KAY = 0.0002, 0.0005, 0.0001, 0.003
FS = (0.5, 0.75, 1.0, 1.25); STOPS = ("yok", "S0", "S1", "S2"); HS = (4, 8, 24, 48)
ADLAR = [f"f{f}_{s}_H{h}" for f in FS for s in STOPS for h in HS]
GOR = set([x.strip()[:-4] for x in open("igne2_evren.txt") if x.strip()] + ["BTC", "ADA", "APT", "ARB", "BNB", "DOGE", "DOT", "ETH", "FLOKI", "LINK", "NEAR", "OP", "PEPE", "SHIB", "SUI"])
HARIC = {"USDC", "BUSD", "TUSD", "FDUSD", "USDP", "DAI", "USDE", "BTCDOM", "DEFI", "FOOTBALL", "BLUEBIRD"}
BAS, SON = pd.Timestamp("2022-06-01", tz="UTC"), pd.Timestamp("2026-10-26", tz="UTC")
A0 = pd.Timestamp("2022-05-01", tz="UTC"); a_m = int(A0.timestamp() // 60); b_m = int(SON.timestamp() // 60) + 3 * 1440
NB = (b_m - a_m) // 5; NH = NB // 12
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
def liste():
    out, mk = [], ""
    while True:
        r = S.get("https://s3-ap-northeast-1.amazonaws.com/data.binance.vision", params=dict(delimiter="/", prefix="data/futures/um/monthly/klines/", marker=mk), timeout=60).text
        ps = re.findall(r"<Prefix>data/futures/um/monthly/klines/([^/<]+)/</Prefix>", r); out += ps
        if "<IsTruncated>true</IsTruncated>" not in r or not ps: break
        mk = f"data/futures/um/monthly/klines/{ps[-1]}/"
    return sorted(set(out))
def taban(sym): return re.sub(r"^(1000000|100000|10000|1000|1M)(?=[A-Z])", "", sym[:-4])
SY = [s for s in liste() if s.endswith("USDT") and "_" not in s and taban(s) not in HARIC]
SY = [(s, "gor" if taban(s) in GOR else "yeni") for s in SY]
if I == 0: pd.DataFrame(SY, columns=["sym", "grup"]).to_csv("igne4_semboller.csv", index=False)
benim = SY[I::N]; print(f"toplam {len(SY)} sembol ({sum(g == 'gor' for _, g in SY)} görülmüş) · parça {I}/{N}: {len(benim)}", flush=True)
def yukle(sym):
    parts = []
    for ay in pd.period_range("2022-04", "2026-09", freq="M").strftime("%Y-%m"):
        b = indir(f"{URL}/monthly/klines/{sym}/5m/{sym}-5m-{ay}.zip")
        if b: parts.append(b)
    for g in pd.date_range("2026-10-01", "2026-10-25").strftime("%Y-%m-%d"):
        b = indir(f"{URL}/daily/klines/{sym}/5m/{sym}-5m-{g}.zip")
        if b: parts.append(b)
    if not parts: return None
    L = []
    for b in parts:
        z = zipfile.ZipFile(io.BytesIO(b)); d = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=[0, 1, 2, 3, 4, 7])
        d = d[pd.to_numeric(d[0], errors="coerce").notna()].astype(float); L.append(d)
    d = pd.concat(L); d.columns = ["ot", "o", "h", "l", "c", "qv"]
    d.loc[d.ot > 1e14, "ot"] = d.ot / 1000; d["b"] = ((d.ot // 60000).astype(np.int64) - a_m) // 5
    d = d[(d.b >= 0) & (d.b < NB)].drop_duplicates("b").set_index("b").reindex(np.arange(NB))
    O, H, L_, C, QV = d.o.values, d.h.values, d.l.values, d.c.values, d.qv.fillna(0).values
    Cf = pd.Series(C).ffill().values
    O_h = O.reshape(NH, 12)[:, 0]; H_h = np.where(np.isnan(H), -np.inf, H).reshape(NH, 12).max(1); L_h = np.where(np.isnan(L_), np.inf, L_).reshape(NH, 12).min(1)
    C_h = Cf.reshape(NH, 12)[:, 11]; QV_h = QV.reshape(NH, 12).sum(1)
    return dict(O=O, Hn=np.nan_to_num(H, nan=-np.inf), Ln=np.nan_to_num(L_, nan=np.inf), Cf=Cf, O_h=O_h, L_h=L_h, C_h=C_h, QV_h=QV_h)
def nfon(b0, b1): return (a_m + b1 * 5) // 480 - (a_m + b0 * 5) // 480                        # bar indeksleri → geçilen 00-08-16 UTC
BT = yukle("BTCUSDT"); RB = pd.Series(BT["C_h"]).pct_change().values
print("BTC hazır", f"{time.time() - T0:.0f} sn", flush=True)
META, XS = [], []
h0 = int((BAS.timestamp() // 60 - a_m) // 60)
for sym, grup in benim:
    X = BT if sym == "BTCUSDT" else yukle(sym)
    if X is None: print(sym, "veri yok", flush=True); continue
    O, Hn, Ln, Cf, O_h, L_h, C_h, QV_h = X["O"], X["Hn"], X["Ln"], X["Cf"], X["O_h"], X["L_h"], X["C_h"], X["QV_h"]
    with np.errstate(invalid="ignore", divide="ignore"):
        sd = pd.Series(np.log(C_h)).diff().rolling(720, min_periods=600).std().shift(1).values
        kr = (O_h - L_h) / (O_h * sd); rr = (C_h - L_h) / (O_h - L_h)
    liq = pd.Series(QV_h).rolling(168, min_periods=120).sum().shift(1).values / 7
    n0 = len(META)
    for i in np.where(np.isfinite(kr) & (kr >= 3) & np.isfinite(O_h))[0]:
        if i < h0 or (i + 1) * 12 + 48 * 12 + 2 >= NB: continue
        e = (i + 1) * 12 + 2; Pe = O[e]
        if not np.isfinite(Pe) or Pe <= 0: continue
        Lw, Ow, s1 = L_h[i], O_h[i], sd[i]; emax = (i + 1) * 12 + 48 * 12 - 1
        hi, lo = Hn[e:emax + 1], Ln[e:emax + 1]; n = len(hi)
        ends = {H: (i + 1) * 12 + H * 12 - 1 - e for H in HS}                                  # göreli son bar
        cm = np.minimum.accumulate(lo)
        def ilk(mask): return int(np.argmax(mask)) if mask.any() else n + 10
        sv = {"yok": None, "S0": Lw * 0.998, "S1": Lw * (1 - s1), "S2": Lw * (1 - 2 * s1)}
        js_ = {k: (ilk(lo <= v) if v is not None else n + 10) for k, v in sv.items()}
        vals = []
        for f in FS:
            tp = Lw + f * (Ow - Lw); jt = ilk(hi >= tp) if tp > Pe else -1
            for sn in STOPS:
                js = js_[sn]; st = sv[sn]
                for H in HS:
                    en = ends[H]
                    if tp <= Pe: net, w = -2 * FP, 0.0
                    elif js <= en and js <= jt:
                        p = min(st, O[e + js] if np.isfinite(O[e + js]) else st, (st + lo[js]) / 2) * (1 - KAY)
                        net = p / Pe - 1 - 2 * FP - FON * nfon(e, e + js + 1); w = p / Pe - 1
                    elif jt <= en:
                        net = tp / Pe - 1 - FP - FL - FON * nfon(e, e + jt + 1); w = cm[jt] / Pe - 1
                    else:
                        net = Cf[e + en] / Pe - 1 - 2 * FP - FON * nfon(e, e + en + 1); w = cm[en] / Pe - 1
                    vals += [net, w]
        META.append(dict(t=pd.Timestamp((a_m + (i + 1) * 60) * 60, unit="s", tz="UTC"), sym=sym, taban=taban(sym), grup=grup, kr=kr[i], rr=rr[i], rb=RB[i],
                         r7=C_h[i - 1] / C_h[i - 169] - 1 if i >= 169 else np.nan, liq=liq[i], Pe=Pe, O=Ow, L=Lw, s1=s1))
        XS.append(np.array(vals, dtype="float32"))
    print(f"{sym} ({grup}) · {len(META) - n0} aday · {time.time() - T0:.0f} sn", flush=True)
pd.DataFrame(META).to_csv(f"igne4_meta_p{I}.csv.gz", index=False, compression="gzip")
np.save(f"igne4_X_p{I}.npy", np.stack(XS) if XS else np.zeros((0, 2 * len(ADLAR)), "float32"))
print("bitti", len(META), f"{time.time() - T0:.0f} sn")
