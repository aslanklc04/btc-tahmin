# denetim_yokla.py — 01.11.2026 sistem denetimi: (1) Binance arşivinde 28–31.10 günleri var mı · (2) gonder.onceki_vurdu geçmiş mesajlarda hatasız mı (main kopyası m/)
import sys, requests, pandas as pd
V = "https://data.binance.vision/data"
for pz, sym in (("futures/um", "BTCUSDT"), ("spot", "BTCUSDT"), ("futures/um", "ETHUSDT"), ("futures/um", "SOLUSDT")):
    print(pz, sym, " ".join(f"{g}:{requests.head(f'{V}/{pz}/daily/klines/{sym}/1h/{sym}-1h-{g}.zip', timeout=30).status_code}" for g in ("2026-10-27", "2026-10-28", "2026-10-29", "2026-10-30", "2026-10-31")))
for pz, sym in (("futures/um", "BTCUSDT"),):
    print("metrics", " ".join(f"{g}:{requests.head(f'{V}/{pz}/daily/metrics/{sym}/{sym}-metrics-{g}.zip', timeout=30).status_code}" for g in ("2026-10-27", "2026-10-28", "2026-10-29", "2026-10-30", "2026-10-31")))
import os; sys.path.insert(0, os.path.abspath("m")); os.chdir("m")
import gonder
K = pd.read_csv("durum/karne_kayit.csv", dtype=str).fillna(""); G = K[K.k.str.startswith("gönderildi") & (K.s != "panel")]
n = h = 0
for r in G.itertuples():
    t2 = pd.Timestamp(r.t, tz="Europe/Istanbul").tz_convert("UTC").floor("h")
    try: v = gonder.onceki_vurdu(r.e, t2); n += 1
    except Exception as e: print("HATA", r.t, repr(e)); h += 1; continue
    if v: print(r.t, r.s, r.e[:60], "→ ♻️", v)
print("onceki_vurdu çalıştı:", n, "· hata:", h)
