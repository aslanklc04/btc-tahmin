# hl_veri.py — PROTOKOL_hl.md: hacme göre ilk 3.000 Hyperliquid hesabının kâr/zarar ve hesap değeri geçmişi → hl_seri.parquet, hl_meta.parquet
import json, time, requests, pandas as pd
T0 = time.time()
rows = requests.get("https://stats-data.hyperliquid.xyz/Mainnet/leaderboard", timeout=300).json()["leaderboardRows"]
def w(x, k): return {a: b for a, b in x["windowPerformances"]}[k]
M = pd.DataFrame([{"adr": x["ethAddress"], "av": float(x["accountValue"]), "pnl_all": float(w(x, "allTime")["pnl"]), "vlm_all": float(w(x, "allTime")["vlm"]),
                   "pnl_ay": float(w(x, "month")["pnl"]), "vlm_ay": float(w(x, "month")["vlm"]), "ad": x.get("displayName")} for x in rows])
M = M.sort_values("vlm_all", ascending=False).reset_index(drop=True); M.to_parquet("hl_meta.parquet", index=False); U = M.adr.head(3000).tolist()
S, hata = [], 0
for k, a in enumerate(U):
    for i in range(6):
        try:
            r = requests.post("https://api.hyperliquid.xyz/info", json={"type": "portfolio", "user": a}, timeout=60)
            if r.status_code == 429: time.sleep(10 * (i + 1)); continue
            v = dict(r.json()).get("allTime", {}); ph, ah = v.get("pnlHistory", []), dict((t, x) for t, x in v.get("accountValueHistory", []))
            S += [(a, t, float(p), float(ah.get(t, "nan"))) for t, p in ph]; break
        except Exception as e:
            if i == 5: hata += 1; print("hata", a, str(e)[:80], flush=True)
            time.sleep(3 * (i + 1))
    time.sleep(1.02)
    if k % 200 == 0: print(f"[{time.time() - T0:.0f} sn] {k} · {len(S)} nokta · hata {hata}", flush=True)
D = pd.DataFrame(S, columns=["adr", "t", "pnl", "av"]); D["t"] = pd.to_datetime(D.t, unit="ms", utc=True); D.to_parquet("hl_seri.parquet", index=False)
print(f"bitti: {D.adr.nunique()} hesap · {len(D)} nokta · {D.t.min()} → {D.t.max()} · hata {hata} · {time.time() - T0:.0f} sn")
