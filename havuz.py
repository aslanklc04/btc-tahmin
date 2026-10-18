# havuz.py — ARAŞTIRMA (18.10.2026, kullanıcı isteği "daha isabetli yöntem bul"; canlıya dokunmaz)
# (A) HAVUZ MODEL: ~140 coin'den birlikte öğrenen tek LightGBM (coin başına model yerine) · girdiler: features() + BTC'ye göre güç + coin'ler arası sıra
# (B) BTC'DEN BAĞIMSIZ HEDEF: "coin 4 saatte BTC'den iyi gider mi" (aynı girdiler)
# Yürüyen test: her ay yalnız geçmiş 2 yılla eğitim (ay başından 4 saat önceye kadar), parametreler egit_coin.py ile aynı (ayar yok).
# Sinyal: canlıyla aynı mantık — olasılığın son 30 güne göre z'si > 0 ve |z| son 30 günün en güçlü %10'unda (ortak.signal_frame), ilk saat sayılır, 4 saat tekrar yok.
# Karşılaştırma: şimdiki coin modellerinin 4s Çok güçlü ↑ (u4) sinyali, AYNI coin'ler ve AYNI dönem (disa_*.pkl, yürüyen test).
# ÖNCEDEN YAZILI ŞART — (A): 2024, 2025, 2026'nın ÜÇÜNDE isabet ≥ şimdiki + 2 puan · sinyal sayısı ≥ %70 · BTC 4s ÇG saatlerinde (🤝) 2025 ve 2026'da ≥ +2 puan.
#   (B): BTC'nin düştüğü 4 saatlerde isabet 2025 ve 2026'da ≥ şimdiki + 5 puan · genel isabet 2025 ve 2026'da şimdikinden düşük değil · sayı ≥ %70.
import os, glob, time, numpy as np, pandas as pd, lightgbm as lgb
from concurrent.futures import ThreadPoolExecutor
from ortak import fetch_1h, features, signal_frame, events
from sklearn.metrics import roc_auc_score
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(str(s))
def utc(ix): ix = pd.DatetimeIndex(ix); return (ix.tz_localize("UTC") if ix.tz is None else ix.tz_convert("UTC")).as_unit("ns")
GEN = [l.strip()[:-4] for l in open("canli/durum/genis_liste.txt") if l.strip()]
COR = [l.strip().replace("USDT", "") for l in open("canli/durum/coin_listesi.txt") if l.strip()]
DIS = {os.path.basename(p)[5:-8]: p for p in glob.glob("ga/**/disa_*USDT.pkl", recursive=True)}
DIS.update({os.path.basename(p)[5:-8]: p for p in glob.glob("art1/**/disa_*USDT.pkl", recursive=True)})
CO = sorted((set(GEN) | set(COR) | set(DIS)) - {"BTC"}); BAS = pd.Timestamp("2021-01-01", tz="UTC")
yaz(f"# 🧠 Havuz model + BTC'den bağımsız hedef — {pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M}\naday coin {len(CO)} · karşılaştırma dosyası (disa) {len(DIS)}")
def veri(nm):
    try: o = fetch_1h(BAS.timestamp() * 1000, time.time() * 1000, sym=f"{nm}USDT"); o.index = utc(o.index); return nm, o.astype("float64")
    except Exception as e: print(nm, "veri yok", e); return nm, None
with ThreadPoolExecutor(8) as ex: O = {k: v for k, v in ex.map(veri, CO + ["BTC"]) if v is not None and len(v) > 24 * 400}
B = O.pop("BTC"); yaz(f"veri: {len(O)} coin · {(time.time() - T0) / 60:.0f} dk")
bc = np.log(B.close); BF = pd.DataFrame({f"b_r{k}": bc - bc.shift(k) for k in (1, 4, 24, 168)}); BF["b_vol24"] = bc.diff().rolling(24).std(); by4 = (bc.shift(-4) - bc)
P = []
for nm, o in O.items():
    F = features(o).astype("float32"); c = np.log(o.close); y4 = c.shift(-4) - c
    F = F.join(BF.reindex(F.index).astype("float32"))
    for k in (4, 24, 168): F[f"rel{k}"] = (F[f"r{k}"] - F[f"b_r{k}"]).astype("float32")
    F["y"] = y4.astype("float32"); F["yx"] = (y4 - by4.reindex(F.index)).astype("float32"); F["nm"] = nm; F = F.iloc[720:]
    P.append(F)
D = pd.concat(P); del P; D.index.name = "t"; D = D.reset_index()
for k in ("r24", "r168", "v24", "rel24"): D[f"cs_{k}"] = D.groupby("t")[k].rank(pct=True).astype("float32")      # coin'ler arası sıra (aynı saat)
FE = [c for c in D.columns if c not in ("t", "y", "yx", "nm")]; yaz(f"satır {len(D):,} · girdi {len(FE)} · {(time.time() - T0) / 60:.0f} dk")
D = D.sort_values("t").reset_index(drop=True); tt = pd.DatetimeIndex(D.t)
def egit(X, yb):
    k = int(len(X) * .85)
    return lgb.LGBMClassifier(n_estimators=600, learning_rate=0.03, num_leaves=15, min_child_samples=300, subsample=0.7, subsample_freq=1, colsample_bytree=0.5,
                              reg_lambda=10, verbose=-1, n_jobs=4).fit(X.iloc[:k], yb.iloc[:k], eval_set=[(X.iloc[k:], yb.iloc[k:])], callbacks=[lgb.early_stopping(50, verbose=False)])
PA, PX = np.full(len(D), np.nan, "float32"), np.full(len(D), np.nan, "float32")
AYLAR = pd.date_range(pd.Timestamp("2023-11-01", tz="UTC"), tt.max(), freq="MS")
for i, ms in enumerate(AYLAR):
    me = AYLAR[i + 1] if i + 1 < len(AYLAR) else tt.max() + pd.Timedelta(hours=1)
    trm = (tt < ms - pd.Timedelta(hours=4)) & (tt >= ms - pd.Timedelta(days=730)) & (tt.hour % 4 == 0) & D.y.notna().values & D.yx.notna().values
    te = np.where((tt >= ms) & (tt < me))[0]; X = D.loc[trm, FE]
    PA[te] = egit(X, (D.y[trm] > 0).astype(int)).predict_proba(D.loc[te, FE])[:, 1]
    PX[te] = egit(X, (D.yx[trm] > 0).astype(int)).predict_proba(D.loc[te, FE])[:, 1]
    print(f"{ms:%Y-%m} eğitildi ({trm.sum():,} satır) · {(time.time() - T0) / 60:.0f} dk", flush=True)
D["pa"], D["px"] = PA, PX
A24 = D[(tt >= pd.Timestamp("2024-01-01", tz="UTC")) & D.y.notna() & D.yx.notna() & D.pa.notna()]
yaz("\n## AUC (tüm saatler, yürüyen test)\n```")
for y_ in (2024, 2025, 2026):
    m = pd.DatetimeIndex(A24.t).year == y_
    yaz(f"{y_}: havuz (A) yön AUC {roc_auc_score(A24.y[m] > 0, A24.pa[m]):.4f} · (B) BTC'yi geçme AUC {roc_auc_score(A24.yx[m] > 0, A24.px[m]):.4f} · (A)'nın BTC'yi geçme AUC {roc_auc_score(A24.yx[m] > 0, A24.pa[m]):.4f}")
yaz("```")
# ---------------- sinyaller ----------------
bu4 = None
for p in glob.glob("ga/**/disa_BTCUSDT.pkl", recursive=True): bu4 = pd.read_pickle(p); bu4.index = utc(bu4.index); bu4 = bu4.u4.fillna(False).astype(bool)
EV = []
for nm, g in D.groupby("nm"):
    g = g.set_index(pd.DatetimeIndex(g.t)).sort_index(); g = g[~g.index.duplicated()]
    for ad, col in (("A", "pa"), ("B", "px")):
        p = g[col].dropna().clip(1e-4, 1 - 1e-4)
        if len(p) < 1500: continue
        sf = signal_frame(p, p, p, False); m = ((sf.S > 0) & (sf.C >= sf.T10) & sf.T10.notna()).reindex(g.index).fillna(False).values & g.y.notna().values
        ev = events(m, 4); t_ = g.index[ev]; EV.append(pd.DataFrame({"kim": ad, "nm": nm, "t": t_, "y": g.y.values[ev], "yx": g.yx.values[ev]}))
    if nm in DIS:
        X = pd.read_pickle(DIS[nm]); X.index = utc(X.index); m = X.u4.fillna(False).astype(bool).values & X.y4.notna().values; ev = events(m, 4); t_ = X.index[ev]
        EV.append(pd.DataFrame({"kim": "ŞİMDİ", "nm": nm, "t": t_, "y": X.y4.values[ev], "yx": X.y4.values[ev] - by4.reindex(t_).values}))
E = pd.concat(EV, ignore_index=True); E = E[E.nm.isin(set(DIS))]                               # yalnız karşılaştırılabilir coin'ler
son = min(E[E.kim == "ŞİMDİ"].t.max(), E[E.kim == "A"].t.max()); E = E[(E.t >= pd.Timestamp("2024-01-01", tz="UTC")) & (E.t <= son)]
E["yil"] = pd.DatetimeIndex(E.t).year; E["btc_u4"] = bu4.reindex(pd.DatetimeIndex(E.t)).fillna(False).values if bu4 is not None else False
E["btc_dus"] = by4.reindex(pd.DatetimeIndex(E.t)).values < 0; E["ok"] = E.y > 0; E["okx"] = E.yx > 0
yaz(f"\n## Sinyaller ({E.nm.nunique()} ortak coin · 2024-01 → {son:%d.%m.%Y}) — sayı · isabet · ort. getiri %\n```")
S = {}
for kim in ("ŞİMDİ", "A", "B"):
    for y_ in (2024, 2025, 2026):
        for kos, km in (("hepsi", slice(None)), ("BTC 4s ÇG saatinde", "btc_u4"), ("BTC düşen 4 saatte", "btc_dus")):
            x = E[(E.kim == kim) & (E.yil == y_)]; x = x if kos == "hepsi" else x[x[km]]
            S[(kim, y_, kos)] = (len(x), 100 * x.ok.mean() if len(x) else np.nan, 100 * x.okx.mean() if len(x) else np.nan, 100 * x.y.mean() if len(x) else np.nan)
for kos in ("hepsi", "BTC 4s ÇG saatinde", "BTC düşen 4 saatte"):
    yaz(f"[{kos}]")
    for kim in ("ŞİMDİ", "A", "B"): yaz(f"  {kim:6s} " + " | ".join(f"{y_}: {S[(kim, y_, kos)][0]:6d} · %{S[(kim, y_, kos)][1]:.1f} (BTC'yi geçti %{S[(kim, y_, kos)][2]:.1f}) · {S[(kim, y_, kos)][3]:+.2f}" for y_ in (2024, 2025, 2026)))
yaz("```")
g = lambda k, y_, kos="hepsi", i=1: S[(k, y_, kos)][i]
A_ok = all(g("A", y_) >= g("ŞİMDİ", y_) + 2 for y_ in (2024, 2025, 2026)) and all(g("A", y_, i=0) >= 0.7 * g("ŞİMDİ", y_, i=0) for y_ in (2024, 2025, 2026)) \
       and all(g("A", y_, "BTC 4s ÇG saatinde") >= g("ŞİMDİ", y_, "BTC 4s ÇG saatinde") + 2 for y_ in (2025, 2026))
B_ok = all(g("B", y_, "BTC düşen 4 saatte") >= g("ŞİMDİ", y_, "BTC düşen 4 saatte") + 5 for y_ in (2025, 2026)) and all(g("B", y_) >= g("ŞİMDİ", y_) for y_ in (2025, 2026)) \
       and all(g("B", y_, i=0) >= 0.7 * g("ŞİMDİ", y_, i=0) for y_ in (2024, 2025, 2026))
yaz(f"\n## Önceden yazılı karar\n- (A) havuz model: {'✅ GEÇTİ → canlı için ikinci aşama testi (prim filtresi, 🤝 kuralı) önerilir' if A_ok else '❌ geçmedi'}\n- (B) BTC'den bağımsız hedef: {'✅ GEÇTİ → ikinci aşama önerilir' if B_ok else '❌ geçmedi'}\n_süre {(time.time() - T0) / 60:.0f} dk_")
open("havuz_sonuc.md", "w").write("\n".join(L) + "\n")
