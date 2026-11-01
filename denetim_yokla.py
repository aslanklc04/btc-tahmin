# denetim_yokla.py — 01.11.2026 sistem denetimi (2): 💧 Neon derinlik servisi yanıt veriyor mu
import requests, pandas as pd
U = "https://br-still-union-baibtf1k-derinlik.compute.c-8.eu-central-1.aws.neon.tech"
now = pd.Timestamp.now(tz="UTC").floor("h")
for k in (1, 2, 6, 24, 72, 150):
    H = now - pd.Timedelta(hours=k)
    try:
        r = requests.get(f"{U}/saat", params={"h": H.strftime("%Y%m%d%H")}, timeout=90); j = r.json() if r.status_code == 200 else None
        c = (j or {}).get("coins", {}); print(H, "HTTP", r.status_code, "coin", len(c), "örnek n", [x.get("n") for x in list(c.values())[:3]], r.text[:150] if not c else "")
    except Exception as e: print(H, "HATA", repr(e)[:200])
for p in ("", "/saglik", "/health", "/durum"):
    try: r = requests.get(U + p, timeout=60); print("GET", p or "/", r.status_code, r.text[:200])
    except Exception as e: print("GET", p, "HATA", repr(e)[:150])
