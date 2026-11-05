# yeniliste_veri.py — PROTOKOL_yeniliste.md: tüm USDT-M vadeli sembollerinin 1 g mumları + fonlaması (data.binance.vision, kapatılanlar dahil)
import io, re, time, zipfile, requests, xml.etree.ElementTree as ET, pandas as pd
from concurrent.futures import ThreadPoolExecutor
S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"; D = "https://data.binance.vision/"; T0 = time.time(); ses = requests.Session()
def liste(prefix, dizin=True):
    out, mark = [], ""
    while True:
        p = {"prefix": prefix, "marker": mark}
        if dizin: p["delimiter"] = "/"
        for i in range(6):
            try: x = ET.fromstring(requests.get(S3, params=p, timeout=60).content); break
            except Exception: time.sleep(3 * (i + 1))
        else: return out
        ns = {"s": x.tag.split("}")[0][1:]}
        ks = [e.text for e in x.findall("s:CommonPrefixes/s:Prefix", ns)] if dizin else [e.text for e in x.findall("s:Contents/s:Key", ns)]
        out += ks; tr = x.find("s:IsTruncated", ns)
        if tr is None or tr.text != "true" or not ks: return out
        mark = ks[-1]
SYM = [p.rstrip("/").split("/")[-1] for p in liste("data/futures/um/monthly/klines/")]
SYM = [s for s in SYM if s.endswith("USDT") and "_" not in s]; print("sembol", len(SYM), flush=True)
def zipcsv(url):
    for i in range(5):
        try:
            r = requests.get(url, timeout=60)
            if r.status_code == 404: return None
            z = zipfile.ZipFile(io.BytesIO(r.content)); return pd.read_csv(z.open(z.namelist()[0]), header=None)
        except Exception: time.sleep(2 * (i + 1))
    return None
def sembol(s):
    ks = [k for k in liste(f"data/futures/um/monthly/klines/{s}/1d/", False) if k.endswith(".zip")]
    fs = [k for k in liste(f"data/futures/um/monthly/fundingRate/{s}/", False) if k.endswith(".zip")]
    K = [d for d in (zipcsv(D + k) for k in ks) if d is not None]; F = [d for d in (zipcsv(D + k) for k in fs) if d is not None]
    k = pd.concat(K) if K else pd.DataFrame(); f = pd.concat(F) if F else pd.DataFrame()
    if len(k):
        k = k[pd.to_numeric(k[0], errors="coerce").notna()].iloc[:, :6]; k.columns = ["t", "o", "h", "l", "c", "v"]; k = k.astype(float); k["s"] = s
    if len(f):
        f = f[pd.to_numeric(f[0], errors="coerce").notna()].iloc[:, [0, 2]]; f.columns = ["t", "fr"]; f = f.astype(float); f["s"] = s
    return k, f
with ThreadPoolExecutor(12) as ex: R = list(ex.map(sembol, SYM))
K = pd.concat([r[0] for r in R if len(r[0])]); F = pd.concat([r[1] for r in R if len(r[1])])
K["t"] = pd.to_datetime(K.t, unit="ms", utc=True); F["t"] = pd.to_datetime(F.t, unit="ms", utc=True)
K.to_parquet("yeniliste_mum.parquet", index=False); F.to_parquet("yeniliste_fon.parquet", index=False)
print(f"bitti {K.s.nunique()} sembol mum · {F.s.nunique()} fonlama · {len(K)} gün · {K.t.min()} → {K.t.max()} · {time.time() - T0:.0f} sn")
