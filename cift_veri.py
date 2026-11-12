# cift_veri.py — PROTOKOL_cift.md: "Trading Pairs" duyurularının gövdeleri (Neon /duyuru_detay) → cift_govde.json
import json, os, re, time, requests, pandas as pd
U = "https://br-still-union-baibtf1k-derinlik.compute.c-8.eu-central-1.aws.neon.tech/duyuru_detay"
D = pd.DataFrame(json.load(open("duyuru_liste.json"))).dropna(subset=["title", "t"]).drop_duplicates("code"); D["t"] = pd.to_datetime(D.t, unit="ms", utc=True)
D = D[(D.t >= "2022-01-01") & D.title.str.contains("Trading Pair") & ~D.title.str.contains("Margin|Futures|Options|Loan|Leveraged")]
print("çekilecek", len(D), flush=True)
R = json.load(open("cift_govde.json")) if os.path.exists("cift_govde.json") else {}
for k, r in enumerate(D.itertuples()):
    if r.code in R: continue
    for i in range(5):
        try:
            x = requests.get(U, params={"kod": r.code}, timeout=90)
            if x.status_code == 429 or not x.text.strip(): time.sleep(8 * (i + 1)); continue
            d = x.json().get("data") or {}; govde = d.get("body") or d.get("content") or ""
            if k < 2: print("örnek alanlar:", list(d.keys())[:20], "·", str(govde)[:300], flush=True)
            metin = re.sub(r"\\s+", " ", re.sub(r"<[^>]+>", " ", " ".join(re.findall(r'"text":"(.*?)"', govde)) if '"text"' in govde else govde))
            R[r.code] = {"title": r.title, "t": r.t.isoformat(), "metin": metin[:6000], "cift": sorted(set(re.findall(r"\\b[A-Z0-9]{2,12}/[A-Z0-9]{2,6}\\b", metin)))}
            break
        except Exception as e: print("hata", r.code, str(e)[:100], flush=True); time.sleep(5 * (i + 1))
    time.sleep(0.5)
    if k % 50 == 0: print(k, len(R), flush=True); json.dump(R, open("cift_govde.json", "w"), ensure_ascii=False)
json.dump(R, open("cift_govde.json", "w"), ensure_ascii=False); print("bitti", len(R), "çiftli", sum(1 for v in R.values() if v["cift"]))
