# hl_yokla.py — Hyperliquid API yoklaması (salt okuma)
import json, requests
try:
    r = requests.get("https://stats-data.hyperliquid.xyz/Mainnet/leaderboard", timeout=180); print("leaderboard", r.status_code, len(r.content))
    d = r.json(); rows = d.get("leaderboardRows", d if isinstance(d, list) else []); print("satır", len(rows)); print(json.dumps(rows[0])[:900])
    av = sorted(float(x["accountValue"]) for x in rows); print("hesap değeri: min", av[0], "medyan", av[len(av) // 2], "≥50k", sum(a >= 50000 for a in av), "≥1M", sum(a >= 1e6 for a in av), "<100$", sum(a < 100 for a in av))
    def w(x, k): return {a: b for a, b in x["windowPerformances"]}[k]
    vl = sorted(rows, key=lambda x: -float(w(x, "allTime")["vlm"])); print("hacim 1.:", w(vl[0], "allTime"), "3000.:", w(vl[2999], "allTime") if len(vl) > 2999 else None)
    print("allTime pnl < 0 oranı:", sum(float(w(x, "allTime")["pnl"]) < 0 for x in rows) / len(rows))
    adr = vl[10]["ethAddress"]
except Exception as e: print("leaderboard hata", str(e)[:300]); adr = "0x0000000000000000000000000000000000000000"
try:
    r = requests.post("https://api.hyperliquid.xyz/info", json={"type": "portfolio", "user": adr}, timeout=60); print("portfolio", r.status_code, len(r.content), dict(r.headers).get("content-type"))
    p = r.json()
    for k, v in p:
        ph, ah = v.get("pnlHistory", []), v.get("accountValueHistory", []); print(k, "pnl n", len(ph), ph[:2], ph[-1:] if ph else "", "| av n", len(ah), ah[:1], "| vlm", v.get("vlm"))
    r = requests.post("https://api.hyperliquid.xyz/info", json={"type": "clearinghouseState", "user": adr}, timeout=60); print("state", r.status_code, r.text[:500])
except Exception as e: print("portfolio hata", str(e)[:300])
