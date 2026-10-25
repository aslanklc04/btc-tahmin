# sekil_isle.py — PROTOKOL_sekil.md: 5 dk arşivden şekil etiketleri + etkenler → sayım tabloları (parça I / N)
import io, sys, json, time, zipfile, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from numpy.lib.stride_tricks import sliding_window_view as swv
I, N = int(sys.argv[1]), int(sys.argv[2]); T0 = time.time(); S = requests.Session(); A = "https://data.binance.vision/data/spot/monthly/klines"
LS = json.load(open("sekil_liste.json")); IS = [("A", c) for c in LS["A"]] + [("B", c) for c in LS["B"]]; IS = IS[I::N]
AYLAR = pd.date_range("2022-04-01", "2026-09-01", freq="MS"); WS = (1, 4, 8, 24); K25, K22 = pd.Timestamp("2025-01-01", tz="UTC"), pd.Timestamp("2022-06-01", tz="UTC")
def ay(arg):
    c, m = arg
    for k in range(4):
        try:
            r = S.get(f"{A}/{c}USDT/5m/{c}USDT-5m-{m:%Y-%m}.zip", timeout=40)
            if r.status_code == 404: return None
            if r.status_code == 200:
                z = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=[0, 1, 2, 3, 4, 7])
                if not str(d.iloc[0, 0]).isdigit(): d = d.iloc[1:].astype(float)
                return d
        except Exception: time.sleep(2 + 2 * k)
    return None
def yukle(c):
    with ThreadPoolExecutor(12) as ex: P = [p for p in ex.map(ay, [(c, m) for m in AYLAR]) if p is not None]
    if not P: return None
    d = pd.concat(P); d.columns = ["t", "o", "h", "l", "c", "qv"]; d["t"] = d.t.astype("int64"); d.loc[d.t > 10**14, "t"] //= 1000   # 2025+: mikro saniye
    d.index = pd.to_datetime(d.t, unit="ms", utc=True); d = d[~d.index.duplicated()].sort_index().drop(columns="t").astype(float)
    return d.reindex(pd.date_range(d.index[0], d.index[-1], freq="5min"))
def etken(d):
    h = d.resample("1h").agg({"o": "first", "h": "max", "l": "min", "c": "last", "qv": "sum"})       # indeks = saat başlangıcı
    ce = h.c.ffill(); lr = np.log(ce).diff(); s720 = lr.rolling(720, min_periods=168).std(); s24 = lr.rolling(24).std()
    F = pd.DataFrame(index=h.index)
    F["s1"] = s720; F["r1"] = lr / s720; F["r4"] = np.log(ce / ce.shift(4)) / (s720 * 2); F["r24"] = np.log(ce / ce.shift(24)) / (s720 * np.sqrt(24))
    F["vol"] = s24 / s720; F["hacim"] = np.log(h.qv.rolling(24).sum() / (h.qv.rolling(720, min_periods=168).mean() * 24))
    H24, L24 = h.h.rolling(24).max(), h.l.rolling(24).min(); F["konum"] = (ce - L24) / (H24 - L24)
    return F.shift(1)                                                                       # pencere s'de başlar → s'ye kadar biten saatler
B3 = lambda x, a, b: np.where(np.isnan(x), -1, np.where(x <= a, 0, np.where(x < b, 1, 2)))
def kodla(F, Fb, idx):
    E = pd.DataFrame(index=idx)
    for k in ("r1", "r4", "r24"): E[k] = B3(F[k].reindex(idx).values, -1, 1)
    E["vol"] = B3(F.vol.reindex(idx).values, 0.8, 1.25 + 1e-12); E["hacim"] = B3(F.hacim.reindex(idx).values, -0.4, 0.4 + 1e-12); E["konum"] = B3(F.konum.reindex(idx).values, 0.2, 0.8 + 1e-12)
    E["btc_r4"] = B3(Fb.r4.reindex(idx).values, -1, 1); E["btc_r24"] = B3(Fb.r24.reindex(idx).values, -1, 1); E["btc_vol"] = B3(Fb.vol.reindex(idx).values, 0.8, 1.25 + 1e-12)
    tr = idx + pd.Timedelta(hours=3); E["saat"] = tr.hour // 6; E["gun"] = (tr.dayofweek >= 5).astype(int)
    return E
def sekil(up, dn, r):
    o = np.full(len(r), 9, np.int8)
    o[(r <= -0.25) & (up >= 0.5)] = 8; o[(r <= -0.25) & (up < 0.5) & (r + dn >= 0.5)] = 7; o[(r <= -0.25) & (up < 0.5) & (r + dn < 0.5)] = 6
    o[(r >= 0.25) & (dn >= 0.5)] = 5; o[(r >= 0.25) & (dn < 0.5) & (up - r >= 0.5)] = 4; o[(r >= 0.25) & (dn < 0.5) & (up - r < 0.5)] = 3
    o[(up < 0.5) & (dn < 0.5) & (np.abs(r) < 0.25)] = 2; o[(up >= 1) & (dn >= 1)] = 1; return o
DB = yukle("BTC"); FB = etken(DB); T1, T2, T3 = [], [], []
for g, c in IS:
    try:
        d = DB if c == "BTC" else yukle(c)
        if d is None or len(d) < 12 * 24 * 60: print(c, "veri yok"); continue
        F = FB if c == "BTC" else etken(d)
        st = d.index[(d.index.minute == 0)]; st = st[st >= K22]; pos = d.index.get_indexer(st); O = d.o.values[pos]
        E = kodla(F, FB, st); s1 = F.s1.reindex(st).values
        for W in WS:
            n = 12 * W; ok = pos + n <= len(d); p = pos[ok]
            Hw = swv(d.h.values, n)[p]; Lw = swv(d.l.values, n)[p]; Ce = d.c.values[p + n - 1]
            v = ~(np.isnan(Hw).any(1) | np.isnan(Lw).any(1) | np.isnan(Ce)) & np.isfinite(s1[ok]) & (s1[ok] > 0)
            sw = s1[ok] * np.sqrt(W); o_ = O[ok]
            up = (Hw.max(1) / o_ - 1) / sw; dn = -(Lw.min(1) / o_ - 1) / sw; r = (Ce / o_ - 1) / sw
            sh = sekil(up, dn, r).astype(float); sh[~v] = np.nan
            X = E[ok].copy(); X["sh"] = sh; X["r"] = np.where(v, r, np.nan)
            X["once"] = X.sh.shift(W).fillna(-1).astype(int); X["son_sh"] = X.sh.shift(-W); X["son_r"] = X.r.shift(-W)   # aynı W'de önceki / sonraki pencere
            X = X.dropna(subset=["sh"]); X["sh"] = X.sh.astype(int); X["don"] = np.where(X.index < K25, "kesif", "dog"); X["g"] = g; X["W"] = W
            for f in ("r1", "r4", "r24", "vol", "hacim", "konum", "btc_r4", "btc_r24", "btc_vol", "saat", "gun", "once"):
                t_ = X.groupby(["g", "don", "W", f, "sh"]).size().reset_index(name="n").rename(columns={f: "dilim"}); t_["etken"] = f; T1.append(t_)
            T2.append(X.groupby(["g", "don", "W", "sh"]).agg(n=("r", "size"), r_ort=("r", "mean"), son_r=("son_r", "mean"), son_yuk=("son_r", lambda x: (x > 0.25).mean())).reset_index())
            T3.append(X.dropna(subset=["son_sh"]).groupby(["g", "don", "W", "sh", "son_sh"]).size().reset_index(name="n"))
        print(f"{g} {c} tamam · {time.time() - T0:.0f} sn", flush=True)
    except Exception as e: print(f"{c} HATA {type(e).__name__}: {str(e)[:160]}", flush=True)
pd.concat(T1).groupby(["g", "don", "W", "etken", "dilim", "sh"]).n.sum().reset_index().to_csv(f"sekil_t1_{I}.csv", index=False)
T2_ = pd.concat(T2); T2_["r_top"] = T2_.r_ort * T2_.n; T2_["son_top"] = T2_.son_r * T2_.n; T2_["yuk_top"] = T2_.son_yuk * T2_.n
T2_.groupby(["g", "don", "W", "sh"])[["n", "r_top", "son_top", "yuk_top"]].sum().reset_index().to_csv(f"sekil_t2_{I}.csv", index=False)
pd.concat(T3).groupby(["g", "don", "W", "sh", "son_sh"]).n.sum().reset_index().to_csv(f"sekil_t3_{I}.csv", index=False)
print("bitti", time.time() - T0)
