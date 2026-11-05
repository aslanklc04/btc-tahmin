# Neon /bilgi yoklaması: vadeli sembol türleri
import json, requests, collections
r = requests.get("https://br-still-union-baibtf1k-derinlik.compute.c-8.eu-central-1.aws.neon.tech/bilgi", timeout=120); print(r.status_code)
d = r.json(); print(len(d)); print(collections.Counter(x["ut"] for x in d)); print(collections.Counter(x["ct"] for x in d))
print([x for x in d if x["ut"] != "COIN"][:15])
json.dump(d, open("vadeli_bilgi.json", "w"))
