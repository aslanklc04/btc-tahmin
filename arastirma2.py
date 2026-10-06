# arastirma2.py — TAHMİN GÜCÜ ARAŞTIRMASI (canlı sisteme dokunmaz)
# Kullanım:  python arastirma2.py 4   |   python arastirma2.py 8   |   python arastirma2.py rapor
# Her aile: v35 yürüyen testine (egit.py ile aynı ayarlar) eklenir. Seçim 2020–23 (ΔAUC ≥ +0,002), hüküm 2024+.
import os, sys, time, json, pickle, requests, numpy as np, pandas as pd, lightgbm as lgb
from concurrent.futures import ThreadPoolExecutor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from ortak import *
from ortak import _mzip
T0 = time.time(); MODE = sys.argv[1] if len(sys.argv) > 1 else "4"
def log(*a): print(f"[{time.time()-T0:5.0f} sn]", *a, flush=True)
UA = {"User-Agent": "btc-tahmin-arastirma"}
# ---------------------------------------------------------------- veri
def klines_full(sym, start="2017-08-17"):
    for url in EP:
        try:
            rows, cur, end = [], int(pd.Timestamp(start, tz="UTC").timestamp() * 1000), int(time.time() * 1000)
            while cur < end:
                r = requests.get(url, params=dict(symbol=sym, interval="1h", startTime=cur, endTime=end, limit=1000), timeout=20); r.raise_for_status(); dt = r.json()
                if not dt: break
                rows += dt; cur = dt[-1][0] + 3_600_000
                if len(dt) < 1000: break
            df = pd.DataFrame([x[:11] for x in rows], columns=["t", "open", "high", "low", "close", "volume", "ct", "qv", "trades", "tbb", "tbq"]).astype(float)
            df.index = pd.to_datetime(df.t, unit="ms", utc=True) + pd.Timedelta(hours=1); df = df[df.index <= pd.Timestamp.now(tz="UTC")]
            return df[~df.index.duplicated()].sort_index()
        except Exception as e: log("⚠️", sym, url.split("/")[2], str(e)[:80])
    return None
def coinbase_1h():
    out, cur, end = [], pd.Timestamp("2017-08-01", tz="UTC"), pd.Timestamp.now(tz="UTC")
    s = requests.Session(); s.headers.update(UA); fails = 0; t_ = time.time()
    while cur < end and time.time() - t_ < 600:
        nx = min(cur + pd.Timedelta(hours=300), end)
        try:
            r = s.get("https://api.exchange.coinbase.com/products/BTC-USD/candles", params=dict(granularity=3600, start=cur.isoformat(), end=nx.isoformat()), timeout=20)
            if r.status_code == 429: time.sleep(1); fails += 0.2; continue
            r.raise_for_status(); out += r.json(); cur = nx; time.sleep(0.12)
        except Exception as e:
            fails += 1; log("⚠️ coinbase", str(e)[:80]); time.sleep(2)
            if fails > 20: return None
    if not out: return None
    df = pd.DataFrame(out, columns=["t", "low", "high", "open", "close", "volume"]).drop_duplicates("t")
    df.index = pd.to_datetime(df.t, unit="s", utc=True) + pd.Timedelta(hours=1); return df.sort_index().close
def deribit_dvol():
    out, end = [], int(time.time() * 1000); st = int(pd.Timestamp("2021-03-01", tz="UTC").timestamp() * 1000)
    t_ = time.time()
    for _ in range(400):
        if time.time() - t_ > 300: break
        try:
            r = requests.get("https://www.deribit.com/api/v2/public/get_volatility_index_data", params=dict(currency="BTC", start_timestamp=st, end_timestamp=end, resolution="3600"), headers=UA, timeout=20)
            r.raise_for_status(); res = r.json()["result"]; out += res["data"]
            if not res.get("continuation") or not res["data"]: break
            end = int(res["continuation"])
        except Exception as e: log("⚠️ deribit", str(e)[:80]); time.sleep(2)
    if not out: return None
    df = pd.DataFrame(out, columns=["t", "o", "h", "l", "c"]).drop_duplicates("t")
    df.index = pd.to_datetime(df.t, unit="ms", utc=True) + pd.Timedelta(hours=1); return df.sort_index().c
def zr(x, w=720): return (x - x.rolling(w, min_periods=168).mean()) / (x.rolling(w, min_periods=168).std() + 1e-12)
if os.environ.get("YEREL"):
    _O = pd.read_pickle("/home/claude/lab2/data/o_1h.pkl"); _O = _O[_O.index <= "2026-10-06 03:00+00:00"]; _rg = np.random.default_rng(0)
    def klines_full(sym, start=None):
        d = _O.copy() * (1 if sym == SYMBOL else 0.05 * (1 + 0.01 * _rg.standard_normal(len(_O)))[:, None])
        d["tbb"] = d.volume * _rg.uniform(0.3, 0.7, len(d)); d["trades"] = _rg.integers(100, 1000, len(d)); return d
    def coinbase_1h(): return _O.close * (1 + 0.0005 * _rg.standard_normal(len(_O)))
    def deribit_dvol(): x = 50 + 5 * _rg.standard_normal(len(_O)); return pd.Series(x, index=_O.index)[_O.index >= "2021-03-24"]
    TEST_START = "2026-06-01"
    def _mzip(ym): return None
    def fetch_1m(a, b): return None
def get_data(need_min):
    K = klines_full(SYMBOL); o = K[["open", "high", "low", "close", "volume"]]
    log(f"BTC {len(o):,} saat")
    FAM = {}
    # 1) alıcı-satıcı baskısı (taker) + işlem sayısı
    v, tb, tr = K.volume, K.tbb, K.trades; T = pd.DataFrame(index=o.index)
    for k in [1, 4, 8, 24, 72]: T[f"tk_imb{k}"] = (2 * tb.rolling(k).sum() - v.rolling(k).sum()) / (v.rolling(k).sum() + 1e-12)
    T["tk_imb1_z"] = zr(T.tk_imb1); T["tk_imb24_z"] = zr(T.tk_imb24)
    T["tk_trades_z"] = np.log(tr + 1) - np.log(tr.rolling(168).mean() + 1); T["tk_size_z"] = zr(np.log(v / (tr + 1) + 1e-12))
    FAM["taker"] = T.replace([np.inf, -np.inf], np.nan)
    # 2) çapraz coin
    alts = {}
    for a in ["ETHUSDT", "BNBUSDT", "XRPUSDT", "SOLUSDT", "DOGEUSDT", "ADAUSDT"]:
        d = klines_full(a)
        if d is not None: alts[a] = d.close.reindex(o.index)
    log("alt coinler:", list(alts))
    lb = np.log(o.close); C = pd.DataFrame(index=o.index)
    if "ETHUSDT" in alts:
        le = np.log(alts["ETHUSDT"])
        for k in [1, 4, 24]: C[f"x_eth_rel{k}"] = (le - le.shift(k)) - (lb - lb.shift(k))
        C["x_ethbtc_z"] = zr(le - lb)
    for k in [1, 4, 24]:
        R = pd.DataFrame({a: np.log(c / c.shift(k)) for a, c in alts.items()})
        C[f"x_breadth{k}"] = (R > 0).sum(1) / R.notna().sum(1).replace(0, np.nan); C[f"x_relmean{k}"] = R.mean(1) - (lb - lb.shift(k))
    FAM["capraz"] = C.replace([np.inf, -np.inf], np.nan)
    # 3) Coinbase primi
    cb = coinbase_1h()
    if cb is not None:
        p = np.log(cb.reindex(o.index).ffill(limit=3) / o.close); P = pd.DataFrame(index=o.index)
        P["cb_prem"] = p; P["cb_prem_z"] = zr(p)
        for k in [1, 4, 24]: P[f"cb_dprem{k}"] = p - p.shift(k)
        FAM["coinbase"] = P; log(f"Coinbase {cb.notna().sum():,} saat")
    # 4) DVOL
    dv = deribit_dvol()
    if dv is not None:
        d = dv.reindex(o.index).ffill(limit=3); V = pd.DataFrame(index=o.index); rv = np.log(o.close).diff().rolling(24).std() * np.sqrt(24 * 365) * 100
        for k in [1, 4, 24]: V[f"dv_chg{k}"] = np.log(d / d.shift(k))
        V["dv_lvl_z"] = zr(d); V["dv_vrp"] = d - rv
        FAM["dvol"] = V.replace([np.inf, -np.inf], np.nan); log(f"DVOL {dv.notna().sum():,} saat")
    M1 = None
    if need_min:
        now_ = pd.Timestamp.now(tz="UTC"); cur_m = now_.normalize().replace(day=1)
        yms = [d.strftime("%Y-%m") for d in pd.date_range(pd.Timestamp(MICRO_START, tz="UTC"), cur_m - pd.Timedelta(days=1), freq="MS")]
        if os.environ.get("YEREL"): M1 = pd.read_pickle("/home/claude/lab2/data/m_1m.pkl")[["close", "volume"]]
        else:
          with ThreadPoolExecutor(8) as ex: parts = list(ex.map(_mzip, yms))
          mins = [to_min(p) for p in parts if p is not None]; tail_ = fetch_1m(mins[-1].index[-1].timestamp() * 1000, time.time() * 1000)
          M1 = pd.concat(mins + ([tail_] if tail_ is not None else [])); M1 = M1[~M1.index.duplicated(keep="last")].sort_index(); log(f"dakika {len(M1):,}")
    return o, FAM, M1
# ---------------------------------------------------------------- yürüyen test
def walk(H, D, FE, years, variant="temel"):
    DL = D.dropna(subset=["y"])
    def train_month(ms):
        parts = []
        for yrs in years:
            tr = DL[DL.index < ms - pd.Timedelta(hours=H)]; tr = tr[tr.index >= tr.index[-1] - pd.Timedelta(days=365 * yrs)]
            w = None
            if variant == "temizle": tr = tr[tr.y.abs() > 0.3 * tr._sd * np.sqrt(H)]
            if variant == "agirlik": w = np.clip(tr.y.abs() / (tr._sd * np.sqrt(H) + 1e-12), 0, 3).values
            yb = (tr.y > 0).astype(int); k = int(len(tr) * .85)
            seeds = [0, 1, 2] if variant == "tohum3" else [None]
            z = ZF(tr[FE]); z.med, z.mu, z.sd = z.med.fillna(0), z.mu.fillna(0), z.sd.fillna(1)   # eğitim penceresinde hiç verisi olmayan sütun (ör. DVOL 2021 öncesi)
            lo = LogisticRegression(C=0.01, max_iter=500).fit(z(tr[FE]), yb, sample_weight=w)
            for sd_ in seeds:
                kw = {} if sd_ is None else dict(random_state=sd_)
                g = lgb.LGBMClassifier(n_estimators=600, learning_rate=0.03, num_leaves=15, min_child_samples=300, subsample=0.7, subsample_freq=1,
                                       colsample_bytree=0.5, reg_lambda=10, verbose=-1, **kw).fit(tr[FE].iloc[:k - H], yb.iloc[:k - H], sample_weight=None if w is None else w[:k - H],
                                       eval_set=[(tr[FE].iloc[k:], yb.iloc[k:])], callbacks=[lgb.early_stopping(50, verbose=False)])
                parts.append((g, z, lo))
        return HModel(parts, FE)
    months = pd.date_range(pd.Timestamp(TEST_START, tz="UTC"), D.index[-1], freq="MS"); PG = pd.Series(np.nan, index=D.index); PL = PG.copy()
    for i, ms in enumerate(months):
        me = months[i + 1] if i + 1 < len(months) else D.index[-1] + pd.Timedelta(hours=1); rows = D[(D.index >= ms) & (D.index < me)]
        if len(rows): pg, pl = train_month(ms)(rows); PG.loc[rows.index], PL.loc[rows.index] = pg, pl
    return PG.dropna(), PL.dropna()
import traceback
def _hata(*a):
    traceback.print_exc(); sys.stdout.flush()
if MODE in ("4", "8"):
    H = int(MODE); o, FAM, M1 = get_data(need_min=(H == 4))
    FA = features(o); FEATS = list(FA.columns)
    if H == 4:
        M1 = M1[M1.index >= pd.Timestamp(MICRO_START, tz="UTC")]; MIC = micro_features(M1); HHM = hourly_cv(M1); P2 = path2_features(o.close, HHM, MIC)
        BASE = FA.join(P2); BFE = FEATS + list(P2.columns)
    else: BASE = FA; BFE = FEATS
    BASE = BASE.copy(); BASE["y"] = np.log(o.close.shift(-H) / o.close); BASE["_sd"] = np.log(o.close).diff().rolling(720, min_periods=168).std(); BASE = BASE.iloc[720:]
    years = CFG[H]["years"]; OUT = {"y": BASE.y, "r": FA[f"r{H}"]}
    runs = [("temel", [], "temel"), ("taker", ["taker"], "temel"), ("capraz", ["capraz"], "temel"), ("coinbase", ["coinbase"], "temel"), ("dvol", ["dvol"], "temel"),
            ("temizle", [], "temizle"), ("agirlik", [], "agirlik"), ("tohum3", [], "tohum3"), ("tum_veri", ["taker", "capraz", "coinbase", "dvol"], "temel")]
    for name, fams, var in runs:
        fams = [f for f in fams if f in FAM]
        if name not in ("temel", "temizle", "agirlik", "tohum3") and not fams: log(f"– {name}: veri yok, atlandı"); continue
        D = BASE.join([FAM[f] for f in fams]) if fams else BASE; FE = BFE + [c for f in fams for c in FAM[f].columns]
        PG, PL = walk(H, D, FE, years, var); OUT[name] = (PG, PL); log(f"✅ {H}s {name} ({len(FE)} özellik)")
    pickle.dump(OUT, open(f"wf2_{H}.pkl", "wb"))
    if H == 4: M1.close.to_pickle("m1close.pkl")
else:
    # ---------------------------------------------------------------- rapor
    W4, W8 = pickle.load(open("wf2_4.pkl", "rb")), pickle.load(open("wf2_8.pkl", "rb")); MC = pd.read_pickle("m1close.pkl")
    HOLD = pd.Timestamp(os.environ.get("HOLDX", HOLD_START), tz="UTC"); A0 = pd.Timestamp(TEST_START, tz="UTC"); L = []
    def yaz(s=""): print(s, flush=True); L.append(s)
    def sframe(Wd, name): PG, PL = Wd[name]; sf = signal_frame(PG, PL, Wd["r"], False); sf["y"] = Wd["y"].reindex(sf.index); return sf
    def boot_dauc(a, b, y, wk, reps=300):
        rg = np.random.default_rng(0); g = pd.Series(np.arange(len(y))).groupby(wk).indices; ks = list(g); ds = []
        for _ in range(reps):
            ix = np.concatenate([g[ks[j]] for j in rg.integers(0, len(ks), len(ks))])
            if len(set(y[ix])) < 2: continue
            ds.append(roc_auc_score(y[ix], b[ix]) - roc_auc_score(y[ix], a[ix]))
        return np.percentile(ds, 5), np.percentile(ds, 95)
    yaz(f"# 🔬 Tahmin gücü araştırması (Binance) — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}")
    yaz("Kural: seçim 2020–23 ΔAUC ≥ +0,002 → hüküm 2024+: ΔAUC > 0 (aynı yön) ve güçlü kanıt için %90 güven aralığının alt sınırı > 0.")
    rows = []
    for H, Wd in [(4, W4), (8, W8)]:
        b = sframe(Wd, "temel")
        for name in [k for k in Wd if k not in ("y", "r")]:
            f = sframe(Wd, name); X = pd.DataFrame({"a": b.S, "b": f.S, "y": b.y}).dropna(); X = X[X.index.hour % H == 0]
            r = {"ufuk": f"{H}s", "yöntem": name}
            for lab, a_, c_ in [("seçim", A0, HOLD), ("hüküm", HOLD, X.index[-1] + pd.Timedelta(hours=1))]:
                x = X[(X.index >= a_) & (X.index < c_)]; yy = (x.y > 0).values
                r[f"AUC {lab}"] = roc_auc_score(yy, x.b); r[f"Δ {lab}"] = r[f"AUC {lab}"] - roc_auc_score(yy, x.a)
                if lab == "hüküm" and name != "temel": lo, hi = boot_dauc(x.a.values, x.b.values, yy, np.asarray(x.index.floor("7D").astype("int64"))); r["Δ hüküm alt"], r["Δ hüküm üst"] = lo, hi
            AH = f.dropna(subset=["S", "T30", "y"]); lv = np.where(AH.C >= AH.T10, 2, np.where(AH.C >= AH.T30, 1, 0)); ev = events((lv == 2) & (AH.S.values > 0), H)
            g = np.exp(AH.y.values[ev]) - 1; hh = AH.index[ev] >= HOLD
            r["ÇG↑ isabet 24+"] = 100 * (g[hh] > 0).mean(); r["ÇG↑ brüt 24+"] = 100 * g[hh].mean(); r["ÇG↑ haftada"] = len(ev) / ((AH.index[-1] - AH.index[0]).days / 7)
            r["SEÇİLDİ"] = name != "temel" and r["Δ seçim"] >= 0.002; r["GEÇTİ (aynı yön)"] = r["SEÇİLDİ"] and r["Δ hüküm"] > 0; r["GÜÇLÜ (alt>0)"] = r["SEÇİLDİ"] and r.get("Δ hüküm alt", -1) > 0
            rows.append(r)
    R = pd.DataFrame(rows).set_index(["ufuk", "yöntem"]); s = R.round(4).to_string(); yaz("\n## 1) AUC farkları ve 'Çok güçlü ↑' sinyali\n```\n" + s + "\n```")
    # ⭐ ve para testi (her yöntem 4s ve 8s'e birlikte uygulanır)
    yaz("\n## 2) ⭐ (4s+8s Çok güçlü ↑) — 8 saat tut · giriş/çıkış :06 · vadeli %0,05 komisyon + fonlama")
    def px(ts): return MC.reindex(ts, method="ffill").values
    rows = []
    for name in [k for k in W4 if k not in ("y", "r") and k in W8]:
        f4, f8 = sframe(W4, name), sframe(W8, name); idx = f4.dropna(subset=["S", "T30"]).index.intersection(f8.dropna(subset=["S", "T30"]).index)
        m = ((f4.C >= f4.T10) & (f4.S > 0)).reindex(idx) & ((f8.C >= f8.T10) & (f8.S > 0)).reindex(idx)
        t = idx[m.values]; out = []; busy = None
        for ti in t:
            if busy is not None and ti < busy: continue
            te = ti + pd.Timedelta(hours=8)
            if te + pd.Timedelta(minutes=6) > MC.index[-1]: break
            out.append((ti, te)); busy = te
        T = pd.DataFrame(out, columns=["t", "te"]); T["g"] = px(T.te + pd.Timedelta(minutes=6)) / px(T.t + pd.Timedelta(minutes=6)) - 1; T["net"] = T.g - 2 * 0.0005 - 0.0001
        for lab, a_, c_ in [("2020–23", A0, HOLD), ("2024+", HOLD, MC.index[-1])]:
            x = T[(T.t >= a_) & (T.t < c_)]; lo, hi = wboot(x.net.values, x.t.values); eq = (1 + x.net).cumprod(); yrs = (c_ - a_).days / 365.25
            rows.append({"yöntem": name, "dönem": lab, "işlem": len(x), "haftada": len(x) / ((c_ - a_).days / 7), "isabet %": 100 * (x.g > 0).mean(), "brüt %": 100 * x.g.mean(),
                         "net %": 100 * x.net.mean(), "net alt": 100 * lo, "net üst": 100 * hi, "yıllık %": 100 * (eq.iloc[-1] ** (1 / yrs) - 1), "maxDD %": 100 * (eq / eq.cummax() - 1).min()})
    yaz("```\n" + pd.DataFrame(rows).set_index(["yöntem", "dönem"]).round(3).to_string() + "\n```")
    yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
    open("arastirma2_sonuc.md", "w").write("\n".join(L) + "\n")
