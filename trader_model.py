# trader_model.py — "İnsan / bot" işlem baskısı MEVCUT MODELE ek bilgi katıyor mu? (2 yıllık işlem verisi)
# 1) BTCUSDT aggTrades 2024-10 → 2026-09 (her işlem) → saatlik tip özellikleri (trader_tipleri.py ile aynı tanımlar)
# 2) v35 yürüyen testi (egit.py ile aynı): 1 saat (temel) ve 4 saat sinyali S
# 3) İkinci aşama (aylık, yalnız geçmiş veriyle): yön ~ S  vs  yön ~ S + tip özellikleri → dışarıda kalan ay AUC'si
# Önceden sabit kural: ΔAUC ≥ +0,002 her iki yarıda da (2025-01→2025-11 ve 2025-12→2026-09) → "ek bilgi var".
import io, zipfile, time, requests, numpy as np, pandas as pd, lightgbm as lgb
from concurrent.futures import ThreadPoolExecutor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from ortak import *
from ortak import _mzip
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
# ---------------- 1) işlem verisi → saatlik tip özellikleri ----------------
R_USD = np.array([10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 2500, 5000, 10000], float)
def gun(d):
    x = None
    for _ in range(3):
        try:
            r = requests.get(f"https://data.binance.vision/data/spot/daily/aggTrades/BTCUSDT/BTCUSDT-aggTrades-{d:%Y-%m-%d}.zip", timeout=120); r.raise_for_status()
            z = zipfile.ZipFile(io.BytesIO(r.content)); x = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=[1, 2, 5, 6], names=["p", "q", "ts", "m"], dtype={"p": "float64", "q": "float64", "ts": "int64"}); break
        except Exception: time.sleep(3)
    if x is None: return None
    ts = x.ts.values.astype("float64"); ts = np.where(ts > 1e14, ts / 1000, ts); p, q = x.p.values, x.q.values; v = p * q
    s = np.where(x.m.astype(str).str.lower().isin(["true", "1"]).values, -1.0, 1.0)
    yuv = (np.abs(v[:, None] - R_USD[None, :]) <= (p * 1e-5)[:, None]).any(axis=1) | (np.abs(q * 1000 - np.round(q * 1000)) < 1e-6)
    h = pd.to_datetime(ts, unit="ms", utc=True).floor("h") + pd.Timedelta(hours=1)
    D = pd.DataFrame({"h": h, "v": v, "sv": s * v, "Y": yuv}); g = D.groupby("h"); out = pd.DataFrame({"v": g.v.sum()})
    out["net_hepsi"] = g.sv.sum() / out.v; out["net_Y"] = D[D.Y].groupby("h").sv.sum().reindex(out.index).fillna(0) / out.v
    out["net_N"] = D[~D.Y].groupby("h").sv.sum().reindex(out.index).fillna(0) / out.v; out["insan_eksi_bot"] = out.net_Y - out.net_N
    return out[["net_hepsi", "net_N", "insan_eksi_bot"]]
GUN = pd.date_range("2024-10-01", "2026-09-30", freq="D")
with ThreadPoolExecutor(4) as ex: P = [x for x in ex.map(gun, GUN) if x is not None]
TF = pd.concat(P).sort_index(); TF = TF[~TF.index.duplicated()]
for c in list(TF.columns): TF[c + "_z"] = (TF[c] - TF[c].rolling(168, min_periods=48).mean().shift(1)) / (TF[c].rolling(168, min_periods=48).std().shift(1) + 1e-12)
for k in (4, 24): TF[f"insan_eksi_bot_{k}s"] = TF.insan_eksi_bot.rolling(k).mean(); TF[f"net_N_{k}s"] = TF.net_N.rolling(k).mean()
yaz(f"# 🧑🤖 İnsan/bot baskısı → mevcut modele ek bilgi? — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}")
yaz(f"İşlem verisi: {len(P)}/{len(GUN)} gün · {len(TF):,} saat · {time.time()-T0:.0f} sn")
# ---------------- 2) v35 yürüyen testi (1s temel, 4s) ----------------
o = fetch_1h(pd.Timestamp("2017-08-17", tz="UTC").timestamp() * 1000, time.time() * 1000)
cur_m = pd.Timestamp.now(tz="UTC").normalize().replace(day=1)
yms = [d.strftime("%Y-%m") for d in pd.date_range(pd.Timestamp(MICRO_START, tz="UTC"), cur_m - pd.Timedelta(days=1), freq="MS")]
with ThreadPoolExecutor(8) as ex: parts = list(ex.map(_mzip, yms))
mins = [to_min(p) for p in parts if p is not None]; tail_ = fetch_1m(mins[-1].index[-1].timestamp() * 1000, time.time() * 1000)
M1 = pd.concat(mins + ([tail_] if tail_ is not None else [])); M1 = M1[~M1.index.duplicated(keep="last")].sort_index(); o = o[o.index <= M1.index[-1]]
FA = features(o); FEATS = list(FA.columns); MIC = micro_features(M1); FA1 = FA.join(MIC.reindex(FA.index)); FEATS1 = FEATS + list(MIC.columns)
P2 = path2_features(o.close, hourly_cv(M1), MIC); FA4 = FA.join(P2); FEATS4 = FEATS + list(P2.columns)
S = {}
for H in (1, 4):
    D = (FA1 if H == 1 else FA4).copy(); D["y"] = np.log(o.close.shift(-H) / o.close); D = D.iloc[720:]; DL = D.dropna(subset=["y"]); FE = FEATS1 if H == 1 else FEATS4
    def tm(ms):
        parts_ = []
        for yrs in CFG[H]["years"]:
            tr = DL[DL.index < ms - pd.Timedelta(hours=H)]; tr = tr[tr.index >= tr.index[-1] - pd.Timedelta(days=365 * yrs)]; yb = (tr.y > 0).astype(int); k = int(len(tr) * .85)
            g = lgb.LGBMClassifier(n_estimators=600, learning_rate=0.03, num_leaves=15, min_child_samples=300, subsample=0.7, subsample_freq=1, colsample_bytree=0.5, reg_lambda=10, verbose=-1).fit(
                tr[FE].iloc[:k - H], yb.iloc[:k - H], eval_set=[(tr[FE].iloc[k:], yb.iloc[k:])], callbacks=[lgb.early_stopping(50, verbose=False)])
            z = ZF(tr[FE]); lo = LogisticRegression(C=0.01, max_iter=500).fit(z(tr[FE]), yb); parts_.append((g, z, lo))
        return HModel(parts_, FE)
    months = pd.date_range(pd.Timestamp("2024-01-01", tz="UTC"), D.index[-1], freq="MS"); PG = pd.Series(np.nan, index=D.index); PL = PG.copy()
    for i, ms in enumerate(months):
        me = months[i + 1] if i + 1 < len(months) else D.index[-1] + pd.Timedelta(hours=1); rows = D[(D.index >= ms) & (D.index < me)]
        if len(rows): pg, pl = tm(ms)(rows); PG.loc[rows.index], PL.loc[rows.index] = pg, pl
    S[H] = signal_frame(PG.dropna(), PL.dropna(), FA[f"r{H}"], False).S; yaz(f"{H}s yürüyen test bitti · {time.time()-T0:.0f} sn")
# ---------------- 3) ikinci aşama: S tek başına vs S + tip özellikleri (+ şans kontrolü: özellikler haftalık bloklarla karıştırılır) ----------------
ADAY = {"insan−bot": ["insan_eksi_bot", "insan_eksi_bot_z", "insan_eksi_bot_4s", "insan_eksi_bot_24s"], "bot baskısı": ["net_N", "net_N_z", "net_N_4s", "net_N_24s"],
        "toplam baskı": ["net_hepsi", "net_hepsi_z"], "hepsi": ["insan_eksi_bot", "insan_eksi_bot_z", "insan_eksi_bot_4s", "insan_eksi_bot_24s", "net_N", "net_N_z", "net_N_4s", "net_N_24s", "net_hepsi", "net_hepsi_z"]}
Y1 = (pd.Timestamp("2025-01-01", tz="UTC"), pd.Timestamp("2025-12-01", tz="UTC")); Y2 = (pd.Timestamp("2025-12-01", tz="UTC"), pd.Timestamp("2026-10-01", tz="UTC"))
def asama2(H, TFx):
    y = np.log(o.close.shift(-H) / o.close); X = pd.DataFrame({"S": S[H].clip(-5, 5), "y": y}).join(TFx).dropna(); X = X[X.index.hour % H == 0]
    tahmin = {k: pd.Series(np.nan, index=X.index) for k in ["S"] + list(ADAY)}
    for ms in pd.date_range(pd.Timestamp("2025-01-01", tz="UTC"), X.index[-1], freq="MS"):
        tr = X[X.index < ms - pd.Timedelta(hours=H)]; te = X[(X.index >= ms) & (X.index < ms + pd.offsets.MonthBegin(1))]
        if len(tr) < 300 or not len(te): continue
        for k, cols in [("S", [])] + list(ADAY.items()):
            c = ["S"] + cols; mu, sd = tr[c].mean(), tr[c].std() + 1e-12
            m = LogisticRegression(C=0.1, max_iter=500).fit(((tr[c] - mu) / sd).clip(-5, 5), (tr.y > 0).astype(int)); tahmin[k].loc[te.index] = m.decision_function(((te[c] - mu) / sd).clip(-5, 5))
    out = {}
    for k in ADAY:
        for lab, (a, b) in [("1", Y1), ("2", Y2)]:
            m = (X.index >= a) & (X.index < b) & tahmin["S"].notna().values; yy = X.y[m] > 0
            out[(k, lab)] = (roc_auc_score(yy, tahmin["S"][m]), roc_auc_score(yy, tahmin[k][m]))
    return out
def karistir(seed):                                                                           # haftalık blokları karıştır (özellik ↔ fiyat bağı kopar, hafta içi yapı kalır)
    rg = np.random.default_rng(seed); wk = TF.index.floor("7D"); ks = pd.Index(wk.unique()); src = rg.permutation(len(ks)); G_ = {k: TF.index[wk == k] for k in ks}; vals, ids = [], []
    for j_, k in enumerate(ks):
        sv = TF.loc[G_[ks[src[j_]]]].values; tg = G_[k]; n = min(len(tg), len(sv)); vals.append(sv[:n]); ids.append(tg[:n])
    return pd.DataFrame(np.vstack(vals), index=ids[0].append(ids[1:]), columns=TF.columns).sort_index()
rows = []
for H in (1, 4):
    gercek = asama2(H, TF); NUL = [asama2(H, karistir(sd)) for sd in range(20)]
    for k in ADAY:
        r = {"ufuk": f"{H}s", "aile": k}
        for lab in ("1", "2"):
            a0, a1 = gercek[(k, lab)]; d = a1 - a0; nul = np.array([n[(k, lab)][1] - n[(k, lab)][0] for n in NUL])
            r[f"AUC model ({lab}. yarı)"] = a0; r[f"Δ ({lab}. yarı)"] = d; r[f"şans %95 ({lab}. yarı)"] = np.percentile(nul, 95)
        r["EK BİLGİ VAR"] = bool(all(r[f"Δ ({l}. yarı)"] >= max(0.002, r[f"şans %95 ({l}. yarı)"]) for l in ("1", "2"))); rows.append(r)
    yaz(f"{H}s ikinci aşama + 20 karıştırma bitti · {time.time()-T0:.0f} sn")
T = pd.DataFrame(rows).set_index(["ufuk", "aile"]).round(4)
yaz("\n## Mevcut model (S) ile model + insan/bot özellikleri — dışarıda kalan aylar\n(Δ = AUC artışı · 'şans %95' = özellikler rastgele karıştırıldığında 20 denemenin %95'lik artışı: gerçek artış bunu geçmeli)\n```\n" + T.to_string() + "\n```")
yaz(f"\nKural: ΔAUC her iki yarıda da hem ≥ +0,002 hem de şans sınırının üstünde. Sonuç: " + (", ".join(f"{i[0]} {i[1]}" for i in T[T['EK BİLGİ VAR']].index) or "hiçbiri geçmedi") + f" · süre {time.time()-T0:.0f} sn")
open("trader_model_sonuc.md", "w").write("\n".join(L) + "\n")
