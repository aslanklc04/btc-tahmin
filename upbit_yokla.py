# upbit_yokla.py — "ABD satıyor ama Asya alıyor" fikri için veri yoklaması (15.10.2026): Upbit API runner'dan açık mı, hangi coin'ler var, geçmiş ne kadar geriye gidiyor
import requests, time, pandas as pd, glob
L = []
def yaz(s): print(s, flush=True); L.append(str(s))
try:
    m = requests.get("https://api.upbit.com/v1/market/all", timeout=20); yaz(f"market/all HTTP {m.status_code}")
    M = [x["market"] for x in m.json() if x["market"].startswith("KRW-")]; yaz(f"KRW pazar sayısı: {len(M)}")
    biz = set(l.strip()[:-4] for l in open("canli_liste.txt") if l.strip()) if glob.glob("canli_liste.txt") else set()
    ort = sorted(set(x[4:] for x in M) & biz); yaz(f"bizim coin'lerle ortak: {len(ort)} → {', '.join(ort)}")
    yaz(f"KRW-USDT var mı: {'KRW-USDT' in M}")
    for mk in ("KRW-BTC", "KRW-ETH", "KRW-XRP", "KRW-USDT"):
        for to in ("2022-06-01T00:00:00", "2023-06-01T00:00:00"):
            r = requests.get("https://api.upbit.com/v1/candles/minutes/60", params=dict(market=mk, to=to, count=200), timeout=20)
            j = r.json() if r.status_code == 200 else []
            yaz(f"{mk} to={to}: HTTP {r.status_code} · {len(j)} mum · " + (f"{j[-1]['candle_date_time_utc']} → {j[0]['candle_date_time_utc']}" if j else str(r.text[:120])))
            time.sleep(0.15)
    t0 = time.time(); n = 0
    for i in range(20):
        r = requests.get("https://api.upbit.com/v1/candles/minutes/60", params=dict(market="KRW-BTC", count=200), timeout=20); n += r.status_code == 200; time.sleep(0.11)
    yaz(f"hız: 20 istek {time.time()-t0:.1f} sn · başarılı {n} · kalan limit başlığı: {r.headers.get('Remaining-Req')}")
except Exception as e: yaz(f"HATA {type(e).__name__}: {e}")
open("upbit_yokla_sonuc.md", "w").write("\n".join(L) + "\n")
