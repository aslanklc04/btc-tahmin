# kopya_yokla.py — Neon /kopya: liste parametreleri (sayfa boyu, süre) yoklaması (salt okuma)
import json, requests
U = "https://br-still-union-baibtf1k-derinlik.compute.c-8.eu-central-1.aws.neon.tech/kopya"
P = "/bapi/futures/v1/friendly/future/copy-trade/home-page/query-list"
def liste(**k):
    b = {"pageNumber": 1, "pageSize": 18, "timeRange": "90D", "dataType": "ROI", "favoriteOnly": False, "hideFull": False, "nickname": "", "order": "DESC", "userAsset": 0, "portfolioType": "PUBLIC"} | k
    r = requests.get(U, params={"p": P, "b": json.dumps(b)}, timeout=90)
    try: d = r.json()
    except Exception: return r.status_code, r.text[:300]
    dd = d.get("data") or {}; L = dd.get("list") or []
    return r.status_code, {"code": d.get("code"), "total": dd.get("total"), "n": len(L), "chart_n": len(L[0]["chartItems"]) if L else None, "ilk": (L[0]["nickname"], L[0]["roi"], L[0].get("startTime")) if L else None, "son": (L[-1]["nickname"], L[-1]["roi"]) if L else None}
for k in [dict(pageSize=50), dict(pageSize=100), dict(timeRange="180D"), dict(timeRange="30D"), dict(timeRange="7D"), dict(timeRange="365D"), dict(dataType="AUM"), dict(dataType="SHARP_RATIO"), dict(dataType="COPIER_PNL"), dict(order="ASC"), dict(pageNumber=500)]:
    print(k, liste(**k))
