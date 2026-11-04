# kopya_veri.py — PROTOKOL_kopya.md: tüm Copy Trading liderlerinin 365 günlük ROI serisi (Neon /kopya) → kopya_veri.parquet
import json, time, requests, numpy as np, pandas as pd
U = "https://br-still-union-baibtf1k-derinlik.compute.c-8.eu-central-1.aws.neon.tech/kopya"; P = "/bapi/futures/v1/friendly/future/copy-trade/home-page/query-list"
def sayfa(n):
    b = {"pageNumber": n, "pageSize": 30, "timeRange": "365D", "dataType": "ROI", "favoriteOnly": False, "hideFull": False, "nickname": "", "order": "DESC", "userAsset": 0, "portfolioType": "PUBLIC"}
    for i in range(4):
        try:
            r = requests.get(U, params={"p": P, "b": json.dumps(b)}, timeout=90); d = r.json()["data"]; return d["total"], d["list"] or []
        except Exception as e: print("tekrar", n, e, flush=True); time.sleep(5)
    return None, []
T0 = time.time(); tot, L = sayfa(1); R = list(L); n_s = int(np.ceil(tot / 30)); print("toplam", tot, "sayfa", n_s, flush=True)
for n in range(2, n_s + 1):
    _, L = sayfa(n); R += L
    if n % 25 == 0: print(f"[{time.time() - T0:.0f} sn] sayfa {n} · {len(R)}", flush=True)
rows, ser = [], {}
for x in R:
    pid = x["leadPortfolioId"]
    if pid in ser: continue
    rows.append({k: x.get(k) for k in ("leadPortfolioId", "nickname", "roi", "pnl", "aum", "copyAum", "mdd", "winRate", "sharpRatio", "startTime", "currentCopyCount", "maxCopyCount", "copierPnl", "apiKeyTag")})
    ser[pid] = pd.Series({pd.Timestamp(c["dateTime"], unit="ms", tz="UTC"): c["value"] for c in x.get("chartItems") or []})
M = pd.DataFrame(rows); S = pd.DataFrame(ser).sort_index()
M.to_parquet("kopya_meta.parquet", index=False); S.astype("float32").to_parquet("kopya_roi.parquet")
print(f"bitti: {len(M)} portföy · {S.shape} · {S.index.min()} → {S.index.max()} · {time.time() - T0:.0f} sn")
