# kilit_yokla.py — DefiLlama token kilit (emissions) API yoklaması
import json, requests
r = requests.get("https://api.llama.fi/emissions", timeout=120); print("emissions", r.status_code, len(r.content))
d = r.json(); print(type(d), len(d) if hasattr(d, "__len__") else "")
x = d[0] if isinstance(d, list) else d; print(json.dumps(x)[:2500])
if isinstance(d, list):
    print("alanlar", sorted(d[0].keys())); ev = [y for y in d if y.get("events")]; print("events olan", len(ev))
    if ev: print(json.dumps(ev[0]["events"][:5])[:1500])
    nm = d[0].get("token") or d[0].get("name"); print("örnek isim", nm)
    for k in ("name", "protocolId", "token"):
        v = d[0].get(k)
        if v:
            r2 = requests.get(f"https://api.llama.fi/emission/{v}", timeout=120); print("emission/", k, v, r2.status_code, r2.text[:1500])
