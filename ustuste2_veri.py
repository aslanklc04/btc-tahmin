# ustuste2_veri.py — PROTOKOL_ustuste.md Ek 1: her üst üste S2 için S1 hedefi S2'den önce değdi mi, S2 anında S1 kârda mı (coin saatlik vadeli mum, yoksa spot)
import io, time, zipfile, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
T0 = time.time(); S = requests.Session(); V = "https://data.binance.vision/data"
K = ["t", "nm", "sinif", "H"]; KAT = {"✅": 0.75, "🔸": 0.50, "📋": 0.45}
X = pd.read_csv("veri_seti.csv.gz", usecols=K + ["G", "P", "s"]).drop_duplicates(K); X["t"] = pd.to_datetime(X.t, utc=True); X = X.sort_values(["t", "nm"]).reset_index(drop=True)
X["son"] = X.t + pd.to_timedelta(X.H, unit="h"); X["tp"] = X.G * (1 + X.sinif.str[0].map(KAT) * X.s)
def get(u):
    for k in range(4):
        try:
            r = S.get(u, timeout=60)
            if r.status_code == 200: return r.content
            if r.status_code == 404: return None
        except Exception: pass
        time.sleep(2 + 2 * k)
    return None
AY = pd.period_range("2022-05", "2026-09", freq="M").strftime("%Y-%m"); GUN = pd.date_range("2026-10-01", "2026-10-29").strftime("%Y-%m-%d")
def mum(nm):
    for pazar, sym in (("futures/um", f"{nm}USDT"), ("futures/um", f"1000{nm}USDT"), ("spot", f"{nm}USDT")):
        P = []
        for u in [f"{V}/{pazar}/monthly/klines/{sym}/1h/{sym}-1h-{a}.zip" for a in AY] + [f"{V}/{pazar}/daily/klines/{sym}/1h/{sym}-1h-{g}.zip" for g in GUN]:
            b = get(u)
            if b:
                z = zipfile.ZipFile(io.BytesIO(b)); d = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=[0, 2, 4]); P.append(d[pd.to_numeric(d[0], errors="coerce").notna()].astype(float))
        if P:
            k = pd.concat(P, ignore_index=True); k.columns = ["ot", "h", "c"]; k.loc[k.ot > 1e14, "ot"] = k.ot / 1000; k.index = pd.to_datetime(k.ot, unit="ms", utc=True)
            k = k[~k.index.duplicated()].sort_index()
            if sym.startswith("1000"): k[["h", "c"]] /= 1000                                            # sinyal fiyatları 1 adet üzerinden
            return nm, pazar, k
    return nm, None, None
with ThreadPoolExecutor(8) as ex: MUM = {nm: (p, k) for nm, p, k in ex.map(mum, X.nm.unique())}
print(f"[{time.time() - T0:.0f} sn] mum: {sum(1 for p, k in MUM.values() if k is not None)} / {len(MUM)} coin", flush=True)
R = []
for nm, g in X.groupby("nm"):
    p, k = MUM.get(nm, (None, None))
    t, s, ix = g.t.values, g.son.values, g.index.values
    for a in range(len(g)):
        m = np.where((t[:a] < t[a]) & (s[:a] > t[a]))[0]
        if not len(m): continue
        j = m[-1]; S1 = g.iloc[j]; S2t = g.t.iloc[a]; hit, ret, olcek = np.nan, np.nan, np.nan
        if k is not None:
            w = k.loc[S1.t:S2t - pd.Timedelta(hours=1)]                                             # S2'den önce BİTMİŞ saatler (açılış t1 … t2−1 s)
            if len(w):
                olcek = float(w.c.iloc[0] / S1.G) if S1.G else np.nan                               # fiyat ölçeği denetimi (≈ 1 olmalı)
                hit = float((w.h >= S1.tp).any()); ret = float(w.c.iloc[-1] / S1.P - 1)
        R.append(dict(t=g.t.iloc[a], nm=nm, sinif=g.sinif.iloc[a], H=g.H.iloc[a], s1_t=S1.t, s1_H=S1.H, s1_sinif=S1.sinif, s1_zaten=hit, s1_getiri_t2=ret, olcek=olcek, kaynak=p))
R = pd.DataFrame(R); R.to_csv("ustuste2_veri.csv.gz", index=False, compression="gzip")
print(f"[{time.time() - T0:.0f} sn] üst üste S2: {len(R)} · S1 zaten tuttu %{100 * R.s1_zaten.mean():.0f} · ölçek medyanı {R.olcek.median():.4f} (%5–95 {R.olcek.quantile(0.05):.3f}–{R.olcek.quantile(0.95):.3f}) · kaynak {R.kaynak.value_counts().to_dict()}")
