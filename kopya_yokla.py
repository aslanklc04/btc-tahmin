# kopya_yokla.py — Neon /kopya üzerinden Binance Copy Trading uçlarını yoklar (salt okuma) → kopya_yokla_log.txt
import json, requests
U = "https://br-still-union-baibtf1k-derinlik.compute.c-8.eu-central-1.aws.neon.tech/kopya"
def g(p, b=None, **q):
    prm = {"p": p, **q}
    if b is not None: prm["b"] = json.dumps(b)
    try:
        r = requests.get(U, params=prm, timeout=90); return r.status_code, r.text
    except Exception as e: return -1, str(e)
L = {"pageNumber": 1, "pageSize": 18, "timeRange": "90D", "dataType": "ROI", "favoriteOnly": False, "hideFull": False, "nickname": "", "order": "DESC", "userAsset": 0, "portfolioType": "PUBLIC"}
s, t = g("/bapi/futures/v1/friendly/future/copy-trade/home-page/query-list", L); print("== liste", s, t[:1500])
pid = None
try:
    d = json.loads(t)["data"]; print("toplam", d.get("total")); lst = d.get("list") or []
    if lst: print("alanlar:", sorted(lst[0].keys())); pid = lst[0].get("leadPortfolioId")
except Exception as e: print("ayrıştırma", e)
if pid:
    for ad, p, b, q in [("detay", "/bapi/futures/v1/friendly/future/copy-trade/lead-portfolio/detail", None, {"portfolioId": pid}),
                        ("performans", "/bapi/futures/v1/public/future/copy-trade/lead-portfolio/performance", None, {"portfolioId": pid, "timeRange": "90D"}),
                        ("grafik ROI", "/bapi/futures/v1/public/future/copy-trade/lead-portfolio/chart-data", None, {"dataType": "ROI", "portfolioId": pid, "timeRange": "90D"}),
                        ("pozisyon geçmişi", "/bapi/futures/v1/public/future/copy-trade/lead-portfolio/position-history", {"pageNumber": 1, "pageSize": 10, "portfolioId": pid}, {}),
                        ("açık pozisyon", "/bapi/futures/v1/friendly/future/copy-trade/lead-data/positions", None, {"portfolioId": pid})]:
        s, t = g(p, b, **q); print(f"== {ad}", s, t[:1200])
