# coin_gercek_tablo.py — 26.10.2026 kullanıcı onayı: mesajda "eski test" yerine coin'in kendi GERÇEKÇİ geçmişi (aynı sınıf + tür, 🎯 ile, limit giriş, vadeli ücret)
# Kaynak: karal2_veri.csv.gz (B_T0) ⋈ veri_seti.csv.gz (tur) → durum/coin_gercek.json: {sınıf: {tür: {coin: [[n, isabet%, net%] × (2022–24, 2025+, 2026)]}}}
import json, numpy as np, pandas as pd
V = pd.read_csv("veri_seti.csv.gz", usecols=["t", "nm", "sinif", "H", "tur"]); D = pd.read_csv("karal2_veri.csv.gz", usecols=["t", "nm", "sinif", "H", "B_T0"])
for x in (V, D): x["t"] = pd.to_datetime(x.t, utc=True)
M = D.drop_duplicates(["t", "nm", "sinif", "H"]).merge(V.drop_duplicates(["t", "nm", "sinif", "H"]), on=["t", "nm", "sinif", "H"]).dropna(subset=["B_T0"])   # 29.10: karal2_veri tekrarları da ayıklanır
M["sn"] = M.sinif.map(lambda s: "ana" if s.startswith("✅") else ("yedek" if s.startswith("🔸") else "panelden"))
DON = (("2022-06-01", "2025-01-01"), ("2025-01-01", "2030-01-01"), ("2026-01-01", "2030-01-01")); T = {}
for (sn, tur, nm), g in M.groupby(["sn", "tur", "nm"]):
    r = []
    for a, b in DON:
        x = g[(g.t >= a) & (g.t < b)].B_T0.values; r.append([int(len(x)), round(100 * float((x > 0).mean()), 1) if len(x) else None, round(100 * float(x.mean()), 3) if len(x) else None])
    T.setdefault(sn, {}).setdefault(tur, {})[nm] = r
json.dump(dict(kaynak="karal2_veri B_T0 (gerçekçi: mesaj fiyatına limit 60 dk, 🎯 sınıf kuralı, vadeli ücret + fonlama) · veri sonu " + f"{M.t.max():%d.%m.%Y}", tablo=T), open("coin_gercek.json", "w"), ensure_ascii=False)
print({sn: {t: len(v) for t, v in d.items()} for sn, d in T.items()})
