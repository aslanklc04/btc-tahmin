# v36_coin.py — MODEL GELİŞTİRME DENEYİ (canlıya dokunmaz). Kullanım: python v36_coin.py ETHUSDT
# Mevcut coin modeli yalnız coin'in KENDİ fiyat/hacim verisine bakıyor. Testlerde işe yarayan bilgiler (prim, akış, işlem büyüklüğü, BTC durumu) modelin içinde değil.
# Bu deney aynı coin için iki modeli AYNI yürüyen testte (aylık yeniden eğitim, yalnız geçmiş veri) eğitir:
#   b = mevcut girdiler (egit_coin.py / ufuk24.py ile birebir)   n = mevcut + YENİ girdiler
# YENİ girdiler (hepsi yalnız geçmişten, canlıda her saat hesaplanabilir):
#   A) Binance spot akışı: alıcı payı (taker alış / hacim) 1/4/24 s ve 24 s z · ortalama işlem büyüklüğü 24 s z ve 1 s sapma · işlem sayısı 24 s z
#   B) Coinbase primi: coin'in kendi primi z (720 s), 4/24 saatlik değişimi, ham baz puan · BTC'nin primi z
#   C) BTC bağlamı (BTC dışı coin'ler): BTC getirisi 1/4/24 s · coin'in BTC'ye göre 24/72 s göreli getirisi · BTC işlem büyüklüğü z
# Çıktı v36_{SYM}.pkl: her varyant için saatlik u4 / star / acls + y4 / y8, 24 s S / C / T10, AUC; coin ve BTC primi.
import os, sys, pickle, requests, lightgbm as lgb
from concurrent.futures import ThreadPoolExecutor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from ortak import *
from ortak import _mzip
SYM = sys.argv[1]; NM = SYM[:-4]; T0 = time.time(); HOLD = pd.Timestamp(HOLD_START, tz="UTC"); BAS = pd.Timestamp("2017-08-17", tz="UTC")
COINS = {"ETHUSDT": dict(micro="2017-09-01", test="2020-01-01"), "BNBUSDT": dict(micro="2017-12-01", test="2020-01-01"),
         "DOGEUSDT": dict(micro="2019-08-01", test="2021-01-01"), "BTCUSDT": dict(micro="2017-09-01", test="2020-01-01")}
def log(*a): print(f"[{time.time()-T0:5.0f} sn] {NM}:", *a, flush=True)
def kline(sym):                                                                                    # 1 s mum + işlem sayısı + taker alış (fetch_1h'tan farklı olarak)
    rows, cur, end = [], int(BAS.timestamp() * 1000), time.time() * 1000
    while cur < end:
        for k in range(6):
            try:
                r = requests.get(EP[0], params=dict(symbol=sym, interval="1h", startTime=cur, limit=1000), timeout=20); r.raise_for_status(); dt = r.json(); break
            except Exception: time.sleep(2 + 2 * k); dt = None
        if not dt: break
        rows += dt; cur = dt[-1][0] + 3_600_000
        if len(dt) < 1000: break
    d = pd.DataFrame([x[:11] for x in rows], columns=["t", "open", "high", "low", "close", "volume", "ct", "qv", "n", "tbv", "tbq"]).astype(float)
    d.index = pd.DatetimeIndex(pd.to_datetime(d.t, unit="ms", utc=True) + pd.Timedelta(hours=1)).as_unit("ns"); d = d[d.index <= pd.Timestamp.now(tz="UTC")]
    return d[~d.index.duplicated()].sort_index()[["open", "high", "low", "close", "volume", "qv", "n", "tbq"]]
def cb_gecmis(nm, o):                                                                              # canlıdaki ortak.cb_prim ile aynı tanım: p = log(Coinbase USD / Binance USDT), z = son 720 saat
    out, cur, end, s = [], max(o.index[0], BAS), pd.Timestamp.now(tz="UTC").floor("h"), requests.Session(); s.headers.update({"User-Agent": "btc-tahmin-arastirma"})
    while cur < end:
        nx = min(cur + pd.Timedelta(hours=300), end)
        for k in range(8):
            try:
                r = s.get(f"https://api.exchange.coinbase.com/products/{nm}-USD/candles", params=dict(granularity=3600, start=cur.isoformat(), end=nx.isoformat()), timeout=20)
                if r.status_code == 404: return None
                if r.status_code == 429: time.sleep(1 + k); continue
                if r.status_code == 200: out += r.json()
                break
            except Exception: time.sleep(2)
        cur = nx; time.sleep(0.12)
    if not out: return None
    d = pd.DataFrame(out, columns=["t", "low", "high", "open", "close", "volume"]).drop_duplicates("t")
    c_ = pd.Series(d.close.values.astype(float), index=pd.DatetimeIndex(pd.to_datetime(d.t, unit="s", utc=True) + pd.Timedelta(hours=1)).as_unit("ns")).sort_index()
    c_ = c_[~c_.index.duplicated()]
    p = np.log(c_.reindex(o.index) / o.close); p = p.where(p.abs() < 0.3)
    z = (p - p.rolling(720, min_periods=168).mean()) / (p.rolling(720, min_periods=168).std() + 1e-12)
    return pd.DataFrame({"p": p, "z": z})
def z720(s): return (s - s.rolling(720, min_periods=168).mean()) / (s.rolling(720, min_periods=168).std() + 1e-12)
# ---------------- 1) veri ----------------
o = kline(SYM); B = o if NM == "BTC" else kline("BTCUSDT")
log(f"{len(o):,} saat · {o.index[0]:%Y-%m-%d} → {o.index[-1]:%Y-%m-%d %H:%M}")
PC = cb_gecmis(NM, o); PB = PC if NM == "BTC" else cb_gecmis("BTC", B)
log(f"Coinbase primi: coin {0 if PC is None else int(PC.z.notna().sum())} saat · BTC {0 if PB is None else int(PB.z.notna().sum())} saat")
E = pd.DataFrame(index=o.index)
for k in (1, 4, 24): E[f"x_tb{k}"] = o.tbq.rolling(k).sum() / (o.qv.rolling(k).sum() + 1e-9) - 0.5
E["x_tb24z"] = z720(E.x_tb24)
ats = np.log(o.qv / (o.n + 1) + 1e-9); E["x_ats24z"] = z720(np.log(o.qv.rolling(24).sum() / (o.n.rolling(24).sum() + 1) + 1e-9)); E["x_ats1"] = ats - ats.rolling(168).mean()
E["x_n24z"] = z720(np.log(o.n.rolling(24).sum() + 1))
if PC is not None:
    E["x_pz"] = PC.z; E["x_pz_d4"] = PC.z - PC.z.shift(4); E["x_pz_d24"] = PC.z - PC.z.shift(24); E["x_pbp"] = PC.p * 1e4
if NM != "BTC":
    if PB is not None: E["x_bpz"] = PB.z.reindex(o.index)
    bc = B.close.reindex(o.index)
    for k in (1, 4, 24): E[f"x_btc_r{k}"] = np.log(bc / bc.shift(k))
    E["x_rel24"] = np.log(o.close / o.close.shift(24)) - E.x_btc_r24; E["x_rel72"] = np.log(o.close / o.close.shift(72)) - np.log(bc / bc.shift(72))
    E["x_btc_ats24z"] = z720(np.log(B.qv.rolling(24).sum() / (B.n.rolling(24).sum() + 1) + 1e-9)).reindex(o.index)
E = E.replace([np.inf, -np.inf], np.nan)
for c_ in ("x_pz", "x_pz_d4", "x_pz_d24", "x_pbp", "x_bpz"):                                   # Coinbase'de listelenmeden önce / veri yokken nötr (0); lojistik tüm-NaN sütunla çalışmaz
    if c_ in E: E[c_] = E[c_].fillna(0)
E = E.astype("float32"); EK = list(E.columns); log(f"yeni girdi: {len(EK)} — {', '.join(EK)}")
if SYM in COINS: CF = COINS[SYM]
else:
    l0 = o.index[0]; mic = (l0 + pd.offsets.MonthBegin(1)).normalize(); tst = max(pd.Timestamp("2020-01-01", tz="UTC"), (l0 + pd.Timedelta(days=365) + pd.offsets.MonthBegin(1)).normalize())
    CF = dict(micro=mic.strftime("%Y-%m-%d"), test=tst.strftime("%Y-%m-%d"))
oo = o[["open", "high", "low", "close", "volume"]]; FA = features(oo); FEATS = list(FA.columns)
cur_m = pd.Timestamp.now(tz="UTC").normalize().replace(day=1)
yms = [d.strftime("%Y-%m") for d in pd.date_range(pd.Timestamp(CF["micro"], tz="UTC"), cur_m - pd.Timedelta(days=1), freq="MS")]
with ThreadPoolExecutor(8) as ex: parts = list(ex.map(lambda ym: _mzip(ym, SYM), yms))
mins = [to_min(p) for p in parts if p is not None]
tail_ = fetch_1m(mins[-1].index[-1].timestamp() * 1000, time.time() * 1000, sym=SYM)
M1 = pd.concat(mins + ([tail_] if tail_ is not None else [])); M1 = M1[~M1.index.duplicated(keep="last")].sort_index()
MIC = micro_features(M1); HHM = hourly_cv(M1); P2 = path2_features(oo.close, HHM, MIC)
log(f"{len(M1):,} dakika · test {CF['test']}+")
# ---------------- 2) aynı hat, iki varyant ----------------
def egit(D, FE, H, yrs_list):
    DL = D.dropna(subset=["y"])
    def train_month(ms):
        parts_ = []
        for yrs in yrs_list:
            tr = DL[DL.index < ms - pd.Timedelta(hours=H)]; tr = tr[tr.index >= tr.index[-1] - pd.Timedelta(days=365 * yrs)]
            yb = (tr.y > 0).astype(int); k = int(len(tr) * .85)
            g = lgb.LGBMClassifier(n_estimators=600, learning_rate=0.03, num_leaves=15, min_child_samples=300, subsample=0.7, subsample_freq=1,
                                   colsample_bytree=0.5, reg_lambda=10, verbose=-1).fit(tr[FE].iloc[:k - H], yb.iloc[:k - H],
                                   eval_set=[(tr[FE].iloc[k:], yb.iloc[k:])], callbacks=[lgb.early_stopping(50, verbose=False)])
            z = ZF(tr[FE]); lo = LogisticRegression(C=0.01, max_iter=500).fit(z(tr[FE]), yb); parts_.append((g, z, lo))
        return HModel(parts_, FE)
    months = pd.date_range(pd.Timestamp(CF["test"], tz="UTC"), D.index[-1], freq="MS"); PG = pd.Series(np.nan, index=D.index); PL = PG.copy()
    for i, ms in enumerate(months):
        me = months[i + 1] if i + 1 < len(months) else D.index[-1] + pd.Timedelta(hours=1); rows = D[(D.index >= ms) & (D.index < me)]
        if not len(rows): continue
        pg, pl = train_month(ms)(rows); PG.loc[rows.index], PL.loc[rows.index] = pg, pl
    return PG.dropna(), PL.dropna()
def hat(ek):
    FAx = FA.join(E) if ek else FA; FEx = FEATS + (EK if ek else [])
    FA1 = FAx.join(MIC.reindex(FAx.index)); FE1 = FEx + list(MIC.columns); FA4 = FAx.join(P2); FE4 = FEx + list(P2.columns)
    R = {}
    for H, cf in CFG.items():
        D = (FA1 if H == 1 else FA4 if H == 4 else FAx).copy(); D["y"] = np.log(oo.close.shift(-H) / oo.close); D = D.iloc[720:]
        PG, PL = egit(D, FE1 if H == 1 else FE4 if H == 4 else FEx, H, cf["years"]); R[H] = dict(PG=PG, PL=PL, D=D); log(f"{'yeni' if ek else 'mevcut'} {H}s bitti")
    def base_S(H): return signal_frame(R[H]["PG"], R[H]["PL"], FA[f"r{H}"], False).S
    JS = pd.DataFrame({"S1": base_S(1), "S4": base_S(4), "S8": base_S(8)}).dropna(); JS["y1"] = R[1]["D"].y.reindex(JS.index)
    ST = pd.Series(np.nan, index=JS.index); sm = pd.date_range(JS.index[0] + pd.Timedelta(days=90), JS.index[-1], freq="MS")
    for i, ms in enumerate(sm):
        me = sm[i + 1] if i + 1 < len(sm) else JS.index[-1] + pd.Timedelta(hours=1)
        tr = JS[JS.index < ms - pd.Timedelta(hours=1)].dropna(subset=["y1"]); te = JS[(JS.index >= ms) & (JS.index < me)]
        if len(tr) < 2000 or not len(te): continue
        ST.loc[te.index] = LogisticRegression(C=0.1).fit(tr[["S1", "S4", "S8"]].clip(-5, 5), (tr.y1 > 0).astype(int)).decision_function(te[["S1", "S4", "S8"]].clip(-5, 5))
    SF = {1: frame_from_S(cz(ST.dropna())), 4: signal_frame(R[4]["PG"], R[4]["PL"], FA.r4, False), 8: signal_frame(R[8]["PG"], R[8]["PL"], FA.r8, False)}
    for H in CFG: SF[H]["y"] = R[H]["D"].y.reindex(SF[H].index)
    AUC = {}
    for H in CFG:
        Bq = SF[H][SF[H].index.hour % H == 0].dropna(subset=["S", "T30", "y"])
        AUC[H] = {dn: (roc_auc_score(Bq.y[m] > 0, Bq.S[m]) if m.sum() > 100 else np.nan) for dn, m in
                  (("22-06→23", (Bq.index >= pd.Timestamp("2022-06-01", tz="UTC")) & (Bq.index < HOLD)), ("2024+", Bq.index >= HOLD), ("2026", Bq.index >= pd.Timestamp("2026-01-01", tz="UTC")))}
    A4 = SF[4].dropna(subset=["S", "T30", "y"]); u4m = (A4.S > 0) & (A4.C >= A4.T10)
    J = SF[4].join(SF[8], lsuffix="4", rsuffix="8").dropna(subset=["S4", "T104", "S8", "T108"])
    AC = pd.DataFrame({H: rpct(SF[H].S) for H in CFG}).dropna(); AC["m"] = AC.mean(axis=1)
    EX = pd.DataFrame({"u4": u4m.reindex(SF[4].index).fillna(False)}, index=SF[4].index)
    EX["star"] = ((J.S4 > 0) & (J.C4 >= J.T104) & (J.S8 > 0) & (J.C8 >= J.T108)).reindex(EX.index).fillna(False); EX["acls"] = (AC.m >= 0.85).reindex(EX.index).fillna(False)
    EX["y4"] = R[4]["D"].y.reindex(EX.index); EX["y8"] = R[8]["D"].y.reindex(EX.index)
    # 24 saat (ufuk24.py SADECE24 ile aynı: yalnız günlük çerçeve girdileri, 3 ve 5 yıllık pencere)
    D24 = FAx.copy(); D24["y"] = np.log(oo.close.shift(-24) / oo.close); D24 = D24.iloc[720:]
    PG, PL = egit(D24, FEx, 24, [3, 5]); S24 = signal_frame(PG, PL, FA.r24, False)
    X24 = pd.DataFrame({"close": oo.close}); X24["S24"], X24["C24"], X24["T10_24"] = S24.S.reindex(X24.index), S24.C.reindex(X24.index), S24.T10.reindex(X24.index)
    B24 = S24.join(D24.y).dropna(subset=["S", "y"]).iloc[::24]
    AUC[24] = {dn: (roc_auc_score(B24.y[m] > 0, B24.S[m]) if m.sum() > 50 else np.nan) for dn, m in
               (("22-06→23", (B24.index >= pd.Timestamp("2022-06-01", tz="UTC")) & (B24.index < HOLD)), ("2024+", B24.index >= HOLD), ("2026", B24.index >= pd.Timestamp("2026-01-01", tz="UTC")))}
    log(f"{'yeni' if ek else 'mevcut'} AUC 2024+: " + " · ".join(f"{H}s {AUC[H]['2024+']:.4f}" for H in AUC))
    return EX, X24.astype("float32"), AUC
EXb, X24b, AUCb = hat(False)
EXn, X24n, AUCn = hat(True)
pickle.dump(dict(sym=SYM, EK=EK, EXb=EXb, EXn=EXn, X24b=X24b, X24n=X24n, AUCb=AUCb, AUCn=AUCn, PC=None if PC is None else PC.astype("float32"),
                 PB=None if PB is None else PB.astype("float32")), open(f"v36_{SYM}.pkl", "wb"))
log(f"kaydedildi · {(time.time()-T0)/60:.1f} dk")
