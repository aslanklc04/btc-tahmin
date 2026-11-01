# denetim_yokla.py — 01.11.2026 denetim (3): 💧 Neon dönüşü sonrası 27 coin z ≤ −2 — ölçüm kayması mı? Neon (01.11) ↔ Binance arşivi bookDepth (25.10 Pazar · 31.10 Cumartesi) ±%1 derinlik
import io, zipfile, requests, numpy as np, pandas as pd
U = "https://br-still-union-baibtf1k-derinlik.compute.c-8.eu-central-1.aws.neon.tech"; S = requests.Session()
SEMB = pd.read_csv("m/durum/likidite_semboller.csv").set_index("coin").sym.to_dict()
def neon(H): return S.get(f"{U}/saat", params={"h": H.strftime("%Y%m%d%H")}, timeout=90).json().get("coins", {})
def arsiv(sym, g):
    r = S.get(f"https://data.binance.vision/data/futures/um/daily/bookDepth/{sym}/{sym}-bookDepth-{g}.zip", timeout=60)
    if r.status_code != 200: return None
    z = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z.open(z.namelist()[0])); d.columns = [c.strip().lower() for c in d.columns]
    d = d[pd.to_numeric(d.percentage, errors="coerce").isin([1, -1])].copy(); d["t"] = pd.to_datetime(d.timestamp, utc=True).dt.ceil("h")
    return d.groupby(["t", "percentage"]).notional.mean().unstack().sum(axis=1)
now = pd.Timestamp.now(tz="UTC").floor("h"); N = {}
for k in range(1, 7):
    H = now - pd.Timedelta(hours=k)
    for nm, x in neon(H).items():
        if x.get("n", 0) >= 6: N.setdefault(nm, []).append((H + pd.Timedelta(hours=1), x["bid1"] + x["ask1"], x.get("n")))
coins = sorted(N)[:40]; R = []
for nm in coins:
    sym = SEMB.get(nm)
    if not sym: continue
    a25, a31 = arsiv(sym, "2026-10-25"), arsiv(sym, "2026-10-31")
    nv = np.mean([v for _, v, _ in N[nm]])
    R.append(dict(coin=nm, neon_0111=nv, n=N[nm][0][2], ars_2510=None if a25 is None else a25.mean(), ars_3110=None if a31 is None else a31.mean()))
X = pd.DataFrame(R); X["oran_25"] = X.neon_0111 / X.ars_2510; X["oran_31"] = X.neon_0111 / X.ars_3110
print(X.round(3).to_string()); print("\nmedyan oran Neon(01.11)/arşiv(25.10):", round(X.oran_25.median(), 3), "· /arşiv(31.10):", round(X.oran_31.median(), 3))
