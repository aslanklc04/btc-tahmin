# turev_yokla.py — Binance vadeli (USDⓈ-M) arşivinde hangi veriler var? fonlama · prim endeksi · metrikler (açık pozisyon, uzun/kısa oranı)
import re, io, time, zipfile, requests, pandas as pd
S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"; BV = "https://data.binance.vision/"
def s3_list(prefix):
    out, marker = [], ""
    while True:
        r = requests.get(S3, params=dict(delimiter="/", prefix=prefix, marker=marker), timeout=60); x = r.text
        pre = re.findall(r"<Prefix>([^<]+)</Prefix>", x)[1:]; keys = re.findall(r"<Key>([^<]+)</Key>", x); out += pre + keys
        if "<IsTruncated>true</IsTruncated>" not in x or not (pre or keys): return out
        marker = (pre + keys)[-1]
L = []
def yaz(s): print(s, flush=True); L.append(s)
yaz("# Vadeli arşiv yoklaması\n")
for kind in ["data/futures/um/monthly/", "data/futures/um/daily/"]: yaz(f"{kind}: " + " ".join(p.split("/")[-2] for p in s3_list(kind)))
SY = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "DOGEUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT", "NEARUSDT", "OPUSDT", "1000SHIBUSDT"]
for nm, pref, sub in [("fonlama", "data/futures/um/monthly/fundingRate/{s}/", ""), ("prim 1s", "data/futures/um/monthly/premiumIndexKlines/{s}/1h/", ""),
                      ("metrik (günlük)", "data/futures/um/daily/metrics/{s}/", ""), ("vadeli kline 1s", "data/futures/um/monthly/klines/{s}/1h/", "")]:
    yaz(f"\n## {nm}")
    for s in SY:
        ks = [k for k in s3_list(pref.format(s=s)) if k.endswith(".zip")]
        yaz(f"- {s}: {len(ks)} dosya · ilk {ks[0].split('/')[-1] if ks else '-'} · son {ks[-1].split('/')[-1] if ks else '-'}")
        if s == "BTCUSDT" and ks:
            for k in (ks[0], ks[-1]):
                z = zipfile.ZipFile(io.BytesIO(requests.get(BV + k, timeout=60).content)); txt = z.open(z.namelist()[0]).read().decode()[:400]
                yaz("```\n" + "\n".join(txt.splitlines()[:4]) + "\n```")
open("turev_yokla.md", "w").write("\n".join(L) + "\n")
