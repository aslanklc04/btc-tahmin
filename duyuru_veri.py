# duyuru_veri.py — PROTOKOL_duyuru.md: Binance duyuru başlıkları (Neon /duyuru) → duyuru_liste.json (eksik sayfaları tamamlar)
import json, os, time, requests
U = "https://br-still-union-baibtf1k-derinlik.compute.c-8.eu-central-1.aws.neon.tech/duyuru"
R = json.load(open("duyuru_liste.json")) if os.path.exists("duyuru_liste.json") else []; var = {x["code"] for x in R}
cat, bas = int(os.environ.get("D_CAT", "49")), int(os.environ.get("D_BAS", "49")); say = atla = 0
for pg in range(bas, 260):
    arts, d = None, None
    for i in range(4):
        try:
            r = requests.get(U, params={"c": cat, "p": pg, "n": 20}, timeout=90)
            try: d = r.json()
            except Exception: print("json değil", pg, r.status_code, repr(r.text[:160]), flush=True); time.sleep(5 * (i + 1)); continue
            cs = d.get("data", {}).get("catalogs") or []
            arts = cs[0]["articles"] if cs else []
            break
        except Exception as e: print("hata", pg, str(e)[:120], flush=True); time.sleep(5 * (i + 1))
    if arts is None: atla += 1; print("sayfa atlandı", pg, flush=True); 
    elif not arts: print("son sayfa", pg, flush=True); break
    else:
        yeni = [a for a in arts if a.get("code") not in var]; R += [{"cat": cat, "title": a.get("title"), "t": a.get("releaseDate"), "code": a.get("code")} for a in yeni]; var |= {a.get("code") for a in yeni}; say += len(yeni)
    if atla >= 8: print("çok sayfa atlandı, durdu"); break
    time.sleep(0.3)
json.dump(R, open("duyuru_liste.json", "w"), ensure_ascii=False); print("eklenen", say, "atlanan sayfa", atla, "toplam", len(R))
