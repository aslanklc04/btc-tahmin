# duyuru_veri.py — PROTOKOL_duyuru.md: Binance duyuru başlıkları (Neon /duyuru) → duyuru_liste.json
import json, time, requests
U = "https://br-still-union-baibtf1k-derinlik.compute.c-8.eu-central-1.aws.neon.tech/duyuru"; R = []
for cat in (161, 48, 49):
    say = 0
    for pg in range(1, 400):
        d = None
        for i in range(4):
            try:
                r = requests.get(U, params={"c": cat, "p": pg, "n": 50}, timeout=90); d = r.json(); break
            except Exception as e: err = str(e); time.sleep(3 * (i + 1))
        if d is None: print("hata", cat, pg, err); break
        if pg == 1: print(cat, "ilk yanıt:", json.dumps(d)[:600], flush=True)
        try: arts = d["data"]["catalogs"][0]["articles"]
        except Exception: arts = []
        if not arts: break
        R += [{"cat": cat, "title": a.get("title"), "t": a.get("releaseDate"), "code": a.get("code")} for a in arts]; say += len(arts)
        time.sleep(0.3)
    print("katalog", cat, "makale", say, flush=True)
json.dump(R, open("duyuru_liste.json", "w"), ensure_ascii=False)
ts = [x["t"] for x in R if x["t"]]; print("toplam", len(R), min(ts) if ts else None, max(ts) if ts else None)
