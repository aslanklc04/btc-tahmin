# ustuste3_veri.py — PROTOKOL_ustuste.md Ek 2: katı vuruş (ilk saat hariç), vuruş saati, S1 sınıfı · ayrıca canlı (karne_gercek.csv) çiftleri
import io, time, zipfile, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
T0 = time.time(); S = requests.Session(); V = "https://data.binance.vision/data"
K = ["t", "nm", "sinif", "H"]; KAT = {"✅": 0.75, "🔸": 0.50, "📋": 0.45}
X = pd.read_csv("veri_seti.csv.gz", usecols=K + ["G", "P", "s"]).drop_duplicates(K); X["t"] = pd.to_datetime(X.t, utc=True); X = X.sort_values(["t", "nm"]).reset_index(drop=True)
X["son"] = X.t + pd.to_timedelta(X.H, unit="h"); X["tp"] = X.G * (1 + X.sinif.str[0].map(KAT) * X.s)
C = pd.read_csv("karne_gercek_main.csv"); C["t"] = pd.to_datetime(C.t0, utc=True); C = C.rename(columns={"coin": "nm"}); C["P"] = C.G; C["tp"] = C.G * (1 + C.tpp / 100)
C["son"] = C.t + pd.to_timedelta(C.H, unit="h"); C = C.sort_values(["t", "nm"]).reset_index(drop=True)
def get(u):
    for k in range(4):
        try:
            r = S.get(u, timeout=60)
            if r.status_code == 200: return r.content
            if r.status_code == 404: return None
        except Exception: pass
        time.sleep(2 + 2 * k)
    return None
AY = pd.period_range("2022-05", "2026-09", freq="M").strftime("%Y-%m"); GUN = pd.date_range("2026-10-01", "2026-10-30").strftime("%Y-%m-%d")
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
            if sym.startswith("1000"): k[["h", "c"]] /= 1000
            return nm, pazar, k
    return nm, None, None
with ThreadPoolExecutor(8) as ex: MUM = {nm: (p, k) for nm, p, k in ex.map(mum, sorted(set(X.nm) | set(C.nm)))}
print(f"[{time.time() - T0:.0f} sn] mum {sum(1 for p, k in MUM.values() if k is not None)} / {len(MUM)}", flush=True)
def ciftler(X, etiket):
    R = []
    for nm, g in X.groupby("nm"):
        p, k = MUM.get(nm, (None, None)); t, s = g.t.values, g.son.values
        for a in range(len(g)):
            m = np.where((t[:a] < t[a]) & (s[:a] > t[a]))[0]
            if not len(m): continue
            S1 = g.iloc[m[-1]]; t2 = g.t.iloc[a]; d = dict(t=t2, nm=nm, sinif=g.sinif.iloc[a], H=g.H.iloc[a], s1_t=S1.t, s1_H=S1.H, s1_sinif=S1.sinif, kaynak=p)
            if k is not None:
                w = k.loc[S1.t:t2 - pd.Timedelta(hours=1)]
                if len(w):
                    v = np.where(w.h.values >= S1.tp)[0]; d["olcek"] = float(w.c.iloc[0] / S1.G) if S1.G else np.nan
                    d["s1_zaten"] = float(len(v) > 0); d["s1_zaten_kati"] = float((v >= 1).any()); d["vurus_once_saat"] = float(len(w) - 1 - v[0]) if len(v) else np.nan
                    d["s1_getiri_t2"] = float(w.c.iloc[-1] / S1.P - 1)
            R.append(d)
    R = pd.DataFrame(R); R["veri"] = etiket; return R
A = ciftler(X, "arastirma"); B = ciftler(C[["t", "nm", "sinif", "H", "G", "P", "tp", "son"]], "canli")
pd.concat([A, B]).to_csv("ustuste3_veri.csv.gz", index=False, compression="gzip")
print(f"[{time.time() - T0:.0f} sn] araştırma çift {len(A)} · canlı çift {len(B)} · Z1 araştırma %{100 * A.s1_zaten.mean():.0f} katı %{100 * A.s1_zaten_kati.mean():.0f} · canlı Z1 %{100 * B.s1_zaten.mean() if len(B) else 0:.0f}")
