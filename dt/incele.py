import os, glob, sys, gzip, pickle
import pandas as pd, numpy as np
sys.path.insert(0, "canli")
for d in ("art1", "art2", "art3", "art4", "ga"):
    fs = sorted(glob.glob(f"{d}/**/*", recursive=True)); fs = [f for f in fs if os.path.isfile(f)]
    print(f"== {d}: {len(fs)} dosya"); print("  örnek:", fs[:6])
    ex = {}
    for f in fs: ex.setdefault(os.path.basename(f).split("_")[0], []).append(f)
    print("  önekler:", {k: len(v) for k, v in ex.items()})
def show(f):
    try:
        x = pd.read_pickle(f)
        if isinstance(x, dict):
            print(f"  {f}: dict {len(x)} anahtar, ilk: {list(x)[:8]}"); k = list(x)[0]; v = x[k]
            if hasattr(v, "columns"): print(f"    [{k}] cols {list(v.columns)} idx {v.index[0]} → {v.index[-1]} n={len(v)}"); print(v.tail(3))
        elif hasattr(x, "columns"):
            print(f"  {f}: cols {list(x.columns)} idx {x.index[0]} → {x.index[-1]} n={len(x)} dtypes {dict(x.dtypes.astype(str))}"); print(x.tail(3))
    except Exception as e: print("  hata", f, e)
for pat in ("art1/**/disa_BTCUSDT.pkl", "art1/**/disa_ETHUSDT.pkl", "art2/**/disa24_ETHUSDT.pkl", "art3/**/*.pkl", "art4/**/*.pkl", "ga/**/disa_AAVEUSDT.pkl", "ga/**/disa24_AAVEUSDT.pkl"):
    for f in glob.glob(pat, recursive=True)[:1]: show(f)
print("ga disa:", len(glob.glob("ga/**/disa_*.pkl", recursive=True)), "ga disa24:", len(glob.glob("ga/**/disa24_*.pkl", recursive=True)))
print("ga dosya türleri:", sorted({os.path.basename(f).split("_")[0] for f in glob.glob("ga/**/*", recursive=True) if os.path.isfile(f)}))
print("ga bir klasör:", sorted(glob.glob("ga/g-AAVEUSDT/**/*", recursive=True)))
# canlı model dosyası yapısı
with gzip.open("canli/durum/model_ETHUSDT.pkl.gz", "rb") as g: M = pickle.load(g)
print("model_ETH:", M["created"], {k: (v["on"], v.get("H")) for k, v in M["SIG"].items()}, "PG4", M["R"][4]["PG"].index[0], M["R"][4]["PG"].index[-1])
with gzip.open("canli/durum/model.pkl.gz", "rb") as g: MB = pickle.load(g)
print("model BTC:", MB["created"], "PG4", MB["R"][4]["PG"].index[0], MB["R"][4]["PG"].index[-1])
for f in sorted(glob.glob("canli/durum/model24_*.pkl.gz"))[:1]:
    with gzip.open(f, "rb") as g: M2 = pickle.load(g)
    print("model24:", f, list(M2.keys())[:20], M2.get("created"))
