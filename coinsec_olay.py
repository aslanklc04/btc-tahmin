# coinsec_olay.py — PROTOKOL_coinsec.md: BTC olay saatleri (u4 · star · acls; 4 saat çakışmasız) → coinsec_olay.csv
import glob, pandas as pd
p = glob.glob("art/**/disa_BTCUSDT.pkl", recursive=True)[0]; X = pd.read_pickle(p)
X.index = pd.DatetimeIndex(X.index); X.index = X.index.tz_localize("UTC") if X.index.tz is None else X.index.tz_convert("UTC")
print("sütunlar:", X.columns.tolist()); print("ilk/son:", X.index[:2].tolist(), X.index[-2:].tolist())
cols = [c for c in ("u4", "star", "acls") if c in X]; print("kullanılan işaretler:", cols)
M = X[cols].fillna(False).astype(bool); ev = []; son = None
for t in M.index[M.any(axis=1).values]:
    if son is None or t - son >= pd.Timedelta(hours=4): ev.append(t); son = t
O = M.loc[ev].reset_index(drop=True); O.insert(0, "t", ev); O.to_csv("coinsec_olay.csv", index=False)
print(len(O), "olay"); print(O.groupby(O.t.dt.year).size().to_string())
if "y4" in X: print("BTC y4 ortalaması olaylarda (bilgi):", float(X.y4.reindex(ev).mean()))
