# btcneden_veri.py — PROTOKOL_btcneden.md veri toplama → btcneden_saat.parquet (BTC saatlik) · btcneden_gun.parquet (günlük makro/akış) · btcneden_dogrula.parquet (ETH, SOL saatlik)
import io, time, json, zipfile, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
T0 = time.time(); S = requests.Session(); V = "https://data.binance.vision/data"
BAS, SON = pd.Timestamp("2021-10-01", tz="UTC"), pd.Timestamp("2026-10-30", tz="UTC")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36", "Accept-Language": "en-US,en;q=0.9"}
def log(*a): print(f"[{time.time() - T0:5.0f} sn]", *a, flush=True)
def get(u, **kw):
    for k in range(5):
        try:
            r = S.get(u, timeout=60, **kw)
            if r.status_code == 200: return r
            if r.status_code in (400, 404): return None
        except Exception: pass
        time.sleep(2 + 3 * k)
    return None
def zcsv(b, cols, header=None):
    z = zipfile.ZipFile(io.BytesIO(b)); return pd.read_csv(z.open(z.namelist()[0]), header=header, usecols=cols)
AYLAR = pd.period_range("2021-10", "2026-09", freq="M").strftime("%Y-%m")
GUNLER = pd.date_range("2026-10-01", "2026-10-29").strftime("%Y-%m-%d")
def mum(pazar, sym):                                                                     # pazar: "futures/um" | "spot"
    def bir(u):
        r = get(u)
        if r is None: return None
        d = zcsv(r.content, [0, 1, 2, 3, 4, 5, 7, 9, 10]); return d[pd.to_numeric(d[0], errors="coerce").notna()].astype(float)
    U = [f"{V}/{pazar}/monthly/klines/{sym}/1h/{sym}-1h-{a}.zip" for a in AYLAR] + [f"{V}/{pazar}/daily/klines/{sym}/1h/{sym}-1h-{g}.zip" for g in GUNLER]
    with ThreadPoolExecutor(8) as ex: P = [x for x in ex.map(bir, U) if x is not None]
    k = pd.concat(P, ignore_index=True); k.columns = ["ot", "o", "h", "l", "c", "v", "qv", "tbv", "tbqv"]; k.loc[k.ot > 1e14, "ot"] = k.ot / 1000
    k.index = pd.to_datetime(k.ot, unit="ms", utc=True); return k[~k.index.duplicated()].sort_index().drop(columns="ot")
def fonlama(sym):
    F = []
    for a in AYLAR.tolist() + ["2026-10"]:
        r = get(f"{V}/futures/um/monthly/fundingRate/{sym}/{sym}-fundingRate-{a}.zip")
        if r:
            z = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z.open(z.namelist()[0])); d.columns = [c.strip().lower() for c in d.columns]
            F.append(pd.DataFrame({"t": pd.to_numeric(d[[c for c in d.columns if "time" in c][0]], errors="coerce"), "r": pd.to_numeric(d[[c for c in d.columns if "rate" in c][-1]], errors="coerce")}))
    f = pd.concat(F, ignore_index=True).dropna(); f.loc[f.t > 1e14, "t"] = f.t / 1000; f.index = pd.to_datetime(f.t, unit="ms", utc=True).dt.floor("h")
    return f.r[~f.index.duplicated()].sort_index()
def metrik(sym):
    def gun(g):
        r = get(f"{V}/futures/um/daily/metrics/{sym}/{sym}-metrics-{g}.zip")
        if r is None: return None
        try:
            z = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z.open(z.namelist()[0])); d.columns = [c.strip().lower() for c in d.columns]
            d["t"] = pd.to_datetime(d.create_time, utc=True).dt.floor("h")                  # 5 dk anlık görüntüler → saat içinde son / ort.
            for c in d.columns:
                if c not in ("create_time", "symbol", "t"): d[c] = pd.to_numeric(d[c], errors="coerce")
            g_ = d.groupby("t")
            return pd.DataFrame({"oi": g_.sum_open_interest.last(), "oiv": g_.sum_open_interest_value.last(), "top_ls": g_.sum_toptrader_long_short_ratio.mean(),
                                 "top_ls_hesap": g_.count_toptrader_long_short_ratio.mean(), "ls": g_.count_long_short_ratio.mean(), "taker_oran": g_.sum_taker_long_short_vol_ratio.mean()})
        except Exception as e: log("metrik", g, e); return None
    G = pd.date_range("2021-12-01", "2026-10-29").strftime("%Y-%m-%d")
    with ThreadPoolExecutor(16) as ex: P = [x for x in ex.map(gun, G) if x is not None]
    m = pd.concat(P); m = m[~m.index.duplicated(keep="last")].sort_index(); m.index = m.index + pd.Timedelta(hours=0)
    return m                                                                                # m.loc[t] = saat t içindeki son anlık görüntü (≈ t+1 saat başı)
def coinbase():
    P = []; a = BAS
    while a < SON:
        b = min(a + pd.Timedelta(hours=299), SON)
        r = get("https://api.exchange.coinbase.com/products/BTC-USD/candles", params=dict(granularity=3600, start=a.isoformat(), end=b.isoformat()), headers=UA)
        if r is not None: P += r.json()
        a = b; time.sleep(0.15)
    d = pd.DataFrame(P, columns=["ts", "l", "h", "o", "c", "v"]); d.index = pd.to_datetime(d.ts, unit="s", utc=True)
    return d[~d.index.duplicated()].sort_index()[["o", "c", "v"]].add_prefix("cb_")
def dvol():
    P = []; a = int(BAS.timestamp() * 1000); son = int(SON.timestamp() * 1000)
    while a < son:
        b = min(a + 40 * 86400000, son); c = b
        while True:
            r = get("https://www.deribit.com/api/v2/public/get_volatility_index_data", params=dict(currency="BTC", start_timestamp=a, end_timestamp=c, resolution="3600"))
            if r is None: break
            j = r.json().get("result", {}); P += j.get("data", []); cont = j.get("continuation")
            if not cont or cont <= a: break
            c = cont
        a = b
    d = pd.DataFrame(P, columns=["ts", "o", "h", "l", "c"]); d.index = pd.to_datetime(d.ts, unit="ms", utc=True)
    return d[~d.index.duplicated()].sort_index().c.rename("dvol")
# ---------- saatlik BTC ----------
F = mum("futures/um", "BTCUSDT"); log("vadeli mum", len(F), F.index.min(), F.index.max())
SP = mum("spot", "BTCUSDT"); log("spot mum", len(SP), SP.index.min(), SP.index.max())
FR = fonlama("BTCUSDT"); log("fonlama", len(FR))
M = metrik("BTCUSDT"); log("metrik", len(M), M.index.min(), M.index.max())
CB = coinbase(); log("coinbase", len(CB), CB.index.min() if len(CB) else None, CB.index.max() if len(CB) else None)
try: DV = dvol(); log("dvol", len(DV), DV.index.min(), DV.index.max())
except Exception as e: DV = pd.Series(dtype=float, name="dvol"); log("dvol hata", e)
X = F.add_prefix("f_").join(SP[["c", "qv", "tbqv"]].add_prefix("s_"), how="left").join(CB, how="left").join(M, how="left").join(DV, how="left")
X["fon"] = FR.reindex(X.index)                                                              # yalnız ödeme saatlerinde dolu; analizde ffill
X = X[X.index < SON].astype("float64"); X.index.name = "t"; X.reset_index().to_parquet("btcneden_saat.parquet", index=False); log("saat yazıldı", X.shape)
# ---------- doğrulama coin'leri ----------
D = []
for sym in ("ETHUSDT", "SOLUSDT"):
    try:
        k = mum("futures/um", sym)[["o", "h", "l", "c"]]; k["fon"] = fonlama(sym).reindex(k.index); k["coin"] = sym[:-4]; D.append(k)
        log(sym, len(k))
    except Exception as e: log(sym, "hata", e)
pd.concat(D).rename_axis("t").reset_index().to_parquet("btcneden_dogrula.parquet", index=False)
# ---------- günlük ----------
G = {}
try:
    import yfinance as yf
    for ad, tk in (("nasdaq", "^IXIC"), ("sp500", "^GSPC"), ("dxy", "DX-Y.NYB"), ("faiz10", "^TNX"), ("vix", "^VIX"), ("altin", "GC=F")):
        for k in range(3):
            try:
                h = yf.Ticker(tk).history(start="2021-06-01", interval="1d", auto_adjust=True)
                if len(h): G[ad] = pd.Series(h.Close.values, index=pd.DatetimeIndex(h.index.tz_localize(None).normalize()).tz_localize("UTC")); break
            except Exception as e: log(tk, e)
            time.sleep(3)
        log("yahoo", ad, len(G.get(ad, [])))
except Exception as e: log("yfinance yok", e)
def farside(url):
    try:
        r = requests.get(url, headers=UA, timeout=60)
        if r.status_code != 200: log(url, r.status_code); return None
        for t in pd.read_html(io.StringIO(r.text)):
            t.columns = [" ".join(map(str, c)) if isinstance(c, tuple) else str(c) for c in t.columns]
            tc = [c for c in t.columns if "Total" in c]
            if not tc: continue
            d = pd.to_datetime(t.iloc[:, 0], format="%d %b %Y", errors="coerce")
            v = t[tc[0]].astype(str).str.replace(",", "").str.replace("(", "-").str.replace(")", "").replace({"-": np.nan, "nan": np.nan})
            s = pd.Series(pd.to_numeric(v, errors="coerce").values, index=d).dropna(); s = s[s.index.notna()]
            if len(s) > 100: s.index = pd.DatetimeIndex(s.index).tz_localize("UTC"); return s[~s.index.duplicated()].sort_index()
    except Exception as e: log("farside", e)
    return None
etf = farside("https://farside.co.uk/bitcoin-etf-flow-all-data/"); kay = "Farside"
if etf is None:
    try:
        J = pd.DataFrame(json.load(open("veri_bgeo/etf-flow-btc.json")))
        r = requests.get("https://bitcoin-data.com/v1/etf-flow-btc", timeout=60, headers={"User-Agent": "btc-tahmin-arastirma"})
        if r.status_code == 200 and r.text.lstrip().startswith("["): J = pd.DataFrame(r.json())
        sy = [c for c in J.columns if c not in ("d", "unixTs")]; N = J[sy].apply(pd.to_numeric, errors="coerce"); tc = [c for c in sy if "total" in c.lower()]
        v = N[tc[0]] if tc else N.sum(axis=1, min_count=1); etf = pd.Series(v.values, index=pd.to_datetime(J.d).dt.tz_localize("UTC")).dropna().sort_index(); kay = "BGeometrics"
    except Exception as e: log("bgeo", e)
if etf is not None: G["etf"] = etf[~etf.index.duplicated()]; log("etf", kay, len(etf), etf.index.min(), etf.index.max())
try:
    j = requests.get("https://stablecoins.llama.fi/stablecoincharts/all", timeout=60).json()
    G["stabil"] = pd.Series({pd.Timestamp(int(x["date"]), unit="s", tz="UTC").floor("D"): float((x.get("totalCirculatingUSD") or {}).get("peggedUSD", np.nan)) for x in j}).sort_index(); log("stabil", len(G["stabil"]))
except Exception as e: log("stabil", e)
try:
    u = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"; Dd = []
    r = get(u, params=dict(assets="btc", metrics="FlowInExNtv,FlowOutExNtv", frequency="1d", start_time="2021-06-01", page_size=10000))
    while r is not None:
        jj = r.json(); Dd += jj.get("data", []); nx = jj.get("next_page_url"); r = get(nx) if nx else None
    d = pd.DataFrame(Dd); d.index = pd.to_datetime(d.time, utc=True).dt.floor("D")
    G["borsa_giris"], G["borsa_cikis"] = pd.to_numeric(d.FlowInExNtv, errors="coerce"), pd.to_numeric(d.FlowOutExNtv, errors="coerce"); log("coinmetrics", len(d))
except Exception as e: log("coinmetrics", e)
try:
    r = get("https://api.alternative.me/fng/", params=dict(limit=0, format="json")); d = pd.DataFrame(r.json()["data"])
    G["korku"] = pd.to_numeric(d.value).set_axis(pd.to_datetime(pd.to_numeric(d.timestamp), unit="s", utc=True).dt.floor("D")).sort_index(); log("korku", len(G["korku"]))
except Exception as e: log("korku", e)
GD = pd.DataFrame({k: v[~v.index.duplicated()] for k, v in G.items()}).sort_index(); GD = GD[(GD.index >= "2021-06-01") & (GD.index < SON)]
GD.index.name = "t"; GD.reset_index().to_parquet("btcneden_gun.parquet", index=False)
log("günlük yazıldı", GD.shape, "| dolu sayıları:", GD.notna().sum().to_dict())
