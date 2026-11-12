# duyuru_veri.py — PROTOKOL_duyuru.md: Binance duyuru başlıkları (Neon /duyuru) → duyuru_liste.json
import json, time, requests
U = "https://br-still-union-baibtf1k-derinlik.compute.c-8.eu-central-1.aws.neon.tech/duyuru"; R = []
for cat in (161, 48, 49):
    say = 0
    for pg in range(1, 400):
        arts = None
        for i in range(5):
            try:
                r = requests.get(U, params={"c": cat, "p": pg, "n": 20}, timeout=90); d = r.json(); arts = d["data"]["catalogs"][0]["articles"]
                if arts: break
                if pg * 20 >= (d["data"]["catalogs"][0].get("total") or 0): break
                print("boş", cat, pg, r.status_code, r.text[:200], flush=True)
            except Exception as e: print("hata", cat, pg, str(e)[:150], (r.text[:200] if "r" in dir() else ""), flush=True)
            time.sleep(4 * (i + 1))
        if pg == 1 and arts: print(cat, "toplam:", d["data"]["catalogs"][0].get("total"), flush=True)
        if not arts: break
        R += [{"cat": cat, "title": a.get("title"), "t": a.get("releaseDate"), "code": a.get("code")} for a in arts]; say += len(arts)
        time.sleep(0.25)
    print("katalog", cat, "makale", say, flush=True)
json.dump(R, open("duyuru_liste.json", "w"), ensure_ascii=False)
ts = [x["t"] for x in R if x["t"]]; print("toplam", len(R), min(ts) if ts else None, max(ts) if ts else None)
