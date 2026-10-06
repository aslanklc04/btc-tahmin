# arastirma.py — PARA TESTİ (canlı sisteme dokunmaz). v35 yürüyen testini yeniden kurar, sinyallerin
# komisyon + gecikme sonrası NET sonucunu ölçer. Kural seçimi 2020–23, hüküm 2024–26. Sonuç: arastirma_sonuc.md
import os, time, io, zipfile, numpy as np, pandas as pd, lightgbm as lgb
from concurrent.futures import ThreadPoolExecutor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from ortak import *
from ortak import _mzip
T0 = time.time(); OUT = []
def yaz(s=""): print(s, flush=True); OUT.append(s)
def tablo(df): s = df.to_string(); print(s, flush=True); OUT.append("```\n" + s + "\n```")
# ---------------- 1) veri ----------------
if os.environ.get("VERI") == "bitstamp":
    o = pd.read_pickle("data/o_1h.pkl"); o = o[o.index <= "2026-10-06 03:00+00:00"]
    M1 = pd.read_pickle("data/m_1m.pkl"); M1 = M1[M1.index >= pd.Timestamp(MICRO_START, tz="UTC")]; KAYNAK = "Bitstamp"
else:
    o = fetch_1h(pd.Timestamp("2017-08-17", tz="UTC").timestamp() * 1000, time.time() * 1000)
    now_ = pd.Timestamp.now(tz="UTC"); cur_m = now_.normalize().replace(day=1)
    yms = [d.strftime("%Y-%m") for d in pd.date_range(pd.Timestamp(MICRO_START, tz="UTC"), cur_m - pd.Timedelta(days=1), freq="MS")]
    with ThreadPoolExecutor(8) as ex: parts = list(ex.map(_mzip, yms))
    mins = [to_min(p) for p in parts if p is not None]
    tail_ = fetch_1m(mins[-1].index[-1].timestamp() * 1000, time.time() * 1000)
    M1 = pd.concat(mins + ([tail_] if tail_ is not None else [])); M1 = M1[~M1.index.duplicated(keep="last")].sort_index(); KAYNAK = "Binance"
o = o[o.index <= M1.index[-1]]
yaz(f"# 💰 Para testi ({KAYNAK}) — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}")
yaz(f"Veri: {len(o):,} saat ({o.index[0]:%Y-%m-%d} → {o.index[-1]:%Y-%m-%d %H:%M} UTC) · {len(M1):,} dakika")
FA = features(o); FEATS = list(FA.columns)
MIC = micro_features(M1); FA1 = FA.join(MIC.reindex(FA.index)); FEATS1 = FEATS + list(MIC.columns)
HHM = hourly_cv(M1); P2 = path2_features(o.close, HHM, MIC); FA4 = FA.join(P2); FEATS4 = FEATS + list(P2.columns)
# ---------------- 2) yürüyen test (egit.py ile aynı) ----------------
WF = {}
for H, cf in CFG.items():
    D = (FA1 if H == 1 else FA4 if H == 4 else FA).copy(); D["y"] = np.log(o.close.shift(-H) / o.close); D = D.iloc[720:]; DL = D.dropna(subset=["y"])
    FE = FEATS1 if H == 1 else FEATS4 if H == 4 else FEATS
    def train_month(ms):
        parts = []
        for yrs in cf["years"]:
            tr = DL[DL.index < ms - pd.Timedelta(hours=H)]; tr = tr[tr.index >= tr.index[-1] - pd.Timedelta(days=365 * yrs)]
            yb = (tr.y > 0).astype(int); k = int(len(tr) * .85)
            g = lgb.LGBMClassifier(n_estimators=600, learning_rate=0.03, num_leaves=15, min_child_samples=300, subsample=0.7, subsample_freq=1,
                                   colsample_bytree=0.5, reg_lambda=10, verbose=-1).fit(tr[FE].iloc[:k - H], yb.iloc[:k - H],
                                   eval_set=[(tr[FE].iloc[k:], yb.iloc[k:])], callbacks=[lgb.early_stopping(50, verbose=False)])
            z = ZF(tr[FE]); lo = LogisticRegression(C=0.01, max_iter=500).fit(z(tr[FE]), yb); parts.append((g, z, lo))
        return HModel(parts, FE)
    months = pd.date_range(pd.Timestamp(TEST_START, tz="UTC"), D.index[-1], freq="MS"); PG = pd.Series(np.nan, index=D.index); PL = PG.copy()
    for i, ms in enumerate(months):
        me = months[i + 1] if i + 1 < len(months) else D.index[-1] + pd.Timedelta(hours=1); rows = D[(D.index >= ms) & (D.index < me)]
        if len(rows): pg, pl = train_month(ms)(rows); PG.loc[rows.index], PL.loc[rows.index] = pg, pl
    WF[H] = dict(PG=PG.dropna(), PL=PL.dropna(), y=D.y); print(f"  {H}s yürüyen test bitti · {time.time()-T0:.0f} sn", flush=True)
def base_S(H): return signal_frame(WF[H]["PG"], WF[H]["PL"], FA[f"r{H}"], False).S
JS = pd.DataFrame({"S1": base_S(1), "S4": base_S(4), "S8": base_S(8)}).dropna(); JS["y1"] = WF[1]["y"].reindex(JS.index)
ST = pd.Series(np.nan, index=JS.index); sm = pd.date_range(JS.index[0] + pd.Timedelta(days=90), JS.index[-1], freq="MS")
for i, ms in enumerate(sm):
    me = sm[i + 1] if i + 1 < len(sm) else JS.index[-1] + pd.Timedelta(hours=1)
    tr = JS[JS.index < ms - pd.Timedelta(hours=1)].dropna(subset=["y1"]); te = JS[(JS.index >= ms) & (JS.index < me)]
    if len(tr) < 2000 or not len(te): continue
    stk = LogisticRegression(C=0.1).fit(tr[["S1", "S4", "S8"]].clip(-5, 5), (tr.y1 > 0).astype(int)); ST.loc[te.index] = stk.decision_function(te[["S1", "S4", "S8"]].clip(-5, 5))
SFR = {1: frame_from_S(cz(ST.dropna())), 4: signal_frame(WF[4]["PG"], WF[4]["PL"], FA.r4, False), 8: signal_frame(WF[8]["PG"], WF[8]["PL"], FA.r8, False)}
HOLD = pd.Timestamp(HOLD_START, tz="UTC"); A0 = pd.Timestamp(TEST_START, tz="UTC")
yaz("\n## 1) Model kontrolü (canlı sistemle aynı yöntem)")
for H in (1, 4, 8):
    SF = SFR[H].copy(); SF["y"] = WF[H]["y"].reindex(SF.index); B = SF[SF.index.hour % H == 0].dropna(subset=["S", "T30", "y"]); h = B.index >= HOLD
    yaz(f"- {H} saat: AUC 2024+ {roc_auc_score(B.y[h] > 0, B.S[h]):.4f}")
# ---------------- 3) para testi ----------------
idx = SFR[4].dropna(subset=["S", "T30"]).index.intersection(SFR[8].dropna(subset=["S", "T30"]).index).intersection(SFR[1].dropna(subset=["S", "T30"]).index)
def lv(H): sf = SFR[H].reindex(idx); return pd.Series(np.where(sf.C >= sf.T10, 2, np.where(sf.C >= sf.T30, 1, 0)), index=idx)
def dr(H): return np.sign(SFR[H].S.reindex(idx))
acls = sum(rpct(SFR[H].S).reindex(idx) for H in (1, 4, 8)) / 3 >= 0.85
star = (lv(4) == 2) & (dr(4) > 0) & (lv(8) == 2) & (dr(8) > 0)
RULES = {"4s Çok güçlü ↑ · 4s tut": ((lv(4) == 2) & (dr(4) > 0), 4, 1), "8s Çok güçlü ↑ · 8s tut": ((lv(8) == 2) & (dr(8) > 0), 8, 1),
         "⭐ · 8s tut": (star, 8, 1), "⭐ · 4s tut": (star, 4, 1), "A sınıfı · 4s tut": (acls, 4, 1),
         "4s Güçlü+ ↑ · 4s tut": ((lv(4) >= 1) & (dr(4) > 0), 4, 1), "8s Güçlü+ ↑ · 8s tut": ((lv(8) >= 1) & (dr(8) > 0), 8, 1),
         "1s Çok güçlü ↑ · 1s tut": ((lv(1) == 2) & (dr(1) > 0), 1, 1),
         "4s Çok güçlü ↓ açığa · 4s": ((lv(4) == 2) & (dr(4) < 0), 4, -1), "8s Çok güçlü ↓ açığa · 8s": ((lv(8) == 2) & (dr(8) < 0), 8, -1)}
FEES = {"spot %0,10": 0.0010, "spot BNB %0,075": 0.00075, "vadeli %0,05": 0.0005, "vadeli yapıcı %0,02": 0.0002}; FUND = 0.0001 / 8
MC = M1.close; END = MC.index[-1]
def px(ts): return MC.reindex(ts, method="ffill").values
def trades(mask, H, sg, delay):
    t = idx[np.asarray(mask.fillna(False))]; out = []; busy = None
    for ti in t:
        if busy is not None and ti < busy: continue
        te = ti + pd.Timedelta(hours=H)
        if te + pd.Timedelta(minutes=delay) > END: break
        out.append((ti, te)); busy = te
    T = pd.DataFrame(out, columns=["t", "te"]); T["g"] = sg * (px(T.te + pd.Timedelta(minutes=delay)) / px(T.t + pd.Timedelta(minutes=delay)) - 1); return T
def stats(T, fee, fut, sg, H, a, b):
    x = T[(T.t >= a) & (T.t < b)]
    if len(x) < 5: return None
    net = x.g - 2 * fee - (sg * FUND * H if fut else 0); eq = (1 + net).cumprod(); yrs = (b - a).days / 365.25; lo, hi = wboot(net.values, x.t.values)
    return dict(n=len(x), hft=len(x) / ((b - a).days / 7), brut=100 * x.g.mean(), net=100 * net.mean(), lo=100 * lo, hi=100 * hi,
                yil=100 * (eq.iloc[-1] ** (1 / yrs) - 1), dd=100 * (eq / eq.cummax() - 1).min())
yaz("\n## 2) Gecikmenin etkisi — işlem başı BRÜT getiri % (komisyon öncesi)")
rows = []
for k, (m, H, sg) in RULES.items():
    r = {"kural": k}
    for dl in (0, 2, 6):
        T = trades(m, H, sg, dl); r[f"2020–23 · {dl} dk"] = 100 * T[(T.t >= A0) & (T.t < HOLD)].g.mean(); r[f"2024+ · {dl} dk"] = 100 * T[T.t >= HOLD].g.mean()
    rows.append(r)
tablo(pd.DataFrame(rows).set_index("kural").round(3))
DELAY = 6
yaz(f"\n## 3) Komisyon sonrası NET (giriş/çıkış :0{DELAY}'da) — seçim 2020–23 (alt sınır > 0), hüküm 2024+ (net > 0 ve alt sınır > 0)")
ema720 = FA.ema720.reindex(idx); vol = FA.vol168.reindex(idx); volmed = FA.vol168.rolling(24 * 365, min_periods=24 * 180).median().shift(1).reindex(idx)
FILT = {"filtre yok": pd.Series(True, index=idx), "fiyat > 30g ort.": ema720 > 0, "oynaklık > 1y medyan": vol > volmed}
rows = []
for k, (m, H, sg) in RULES.items():
    for fk, f in FILT.items():
        T = trades(m & f.fillna(False), H, sg, DELAY)
        for fn, fee in FEES.items():
            if sg < 0 and fn.startswith("spot"): continue
            fut = fn.startswith("vadeli"); s1 = stats(T, fee, fut, sg, H, A0, HOLD); s2 = stats(T, fee, fut, sg, H, HOLD, END)
            if s1 and s2:
                rows.append({"kural": k, "filtre": fk, "komisyon": fn, "20–23 net%": s1["net"], "20–23 alt": s1["lo"], "24+ haftada": s2["hft"], "24+ net%": s2["net"],
                             "24+ alt": s2["lo"], "24+ üst": s2["hi"], "24+ yıllık%": s2["yil"], "24+ maxDD%": s2["dd"], "seçildi": s1["lo"] > 0, "GEÇTİ": s1["lo"] > 0 and s2["net"] > 0 and s2["lo"] > 0})
R = pd.DataFrame(rows)
yaz(f"Denenen: {len(R)} · 2020–23'te seçilen: {int(R['seçildi'].sum())} · 2024+ hükmünü GEÇEN: **{int(R['GEÇTİ'].sum())}**")
yaz("\n### Seçilenler ve hükümleri"); tablo(R[R["seçildi"]].drop(columns=["seçildi"]).round(3).set_index(["kural", "filtre", "komisyon"]))
yaz("\n### Filtresiz tüm kurallar"); tablo(R[R.filtre == "filtre yok"].drop(columns=["filtre", "seçildi"]).round(3).set_index(["kural", "komisyon"]))
b0 = o.close[o.close.index >= HOLD]; yaz(f"\nKarşılaştırma — al-tut 2024+: toplam %{100*(b0.iloc[-1]/b0.iloc[0]-1):.0f} · yıllık %{100*((b0.iloc[-1]/b0.iloc[0])**(365.25/(b0.index[-1]-b0.index[0]).days)-1):.0f} · maxDD %{100*(b0/b0.cummax()-1).min():.0f}")
# ---------------- 4) zayıf dönemler ----------------
yaz("\n## 4) Zayıf dönemler (4 saatlik yön isabeti, haftalık)")
SF = SFR[4].copy(); SF["y"] = WF[4]["y"].reindex(SF.index); B = SF[SF.index.hour % 4 == 0].dropna(subset=["S", "y"])
W = pd.DataFrame({"hit": ((B.S > 0) == (B.y > 0)).astype(float)}).resample("W-SUN").mean().dropna(); W["prev3"] = W.hit.rolling(3).mean().shift(1)
for a, b, lab in [(A0, HOLD, "2020–23"), (HOLD, END, "2024+")]:
    x = W[(W.index >= a) & (W.index < b)].dropna()
    yaz(f"- {lab}: haftalık isabet ort. %{100*x.hit.mean():.1f} · %50 altı hafta oranı %{100*(x.hit<0.5).mean():.0f} · önceki 3 hafta ↔ sonraki hafta korelasyonu {np.corrcoef(x.prev3, x.hit)[0,1]:+.3f}"
        f" · önceki 3 hafta <%50 iken sonraki hafta %{100*x[x.prev3<0.5].hit.mean():.1f} (n={int((x.prev3<0.5).sum())})")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("arastirma_sonuc.md", "w").write("\n".join(OUT) + "\n")
