# karal2_analiz.py — PROTOKOL_karal2.md: keşifte seçim (2022-06→2024), sonra kontrol (2025+ · 2026; ikinci kullanım, destekleyici kanıt).
import json, numpy as np, pandas as pd
D = pd.read_csv("karal2_veri.csv.gz"); D["t"] = pd.to_datetime(D.t, utc=True)
A25, A26, YARI, P0 = (pd.Timestamp(x, tz="UTC") for x in ("2025-01-01", "2026-01-01", "2023-07-01", "2022-06-01"))
SIN = ["✅ ana (+0,75σ)", "🔸 yedek (+0,50σ)", "📋 panelden (+0,45σ)"]
KG = [0.3, 0.45, 0.6, 0.75, 0.9, 1.1]; TAU = [0.25, 0.5, 1.0]
L = []; yaz = lambda s="": (print(s), L.append(s))
def olc(d, col):
    x = d[["t", col]].dropna()
    if len(x) == 0: return dict(n=0, ii=np.nan, si=np.nan, net=np.nan)
    sp = x.groupby("t")[col].mean()
    return dict(n=len(x), ii=100 * (x[col] > 0).mean(), si=100 * (sp > 0).mean(), net=100 * x[col].mean())
def donem(d, a, b): return d[(d.t >= a) & (d.t < b)]
SON = D.t.max() + pd.Timedelta(hours=1)
KES = [("keşif", P0, A25), ("keşif ½-1", P0, YARI), ("keşif ½-2", YARI, A25)]; KON = [("2025+", A25, SON), ("2026", A26, SON)]
def sart(o, b): return o["ii"] >= b["ii"] - 0.5 and o["si"] >= b["si"] - 0.5 and o["net"] >= b["net"] + 0.03
yaz("# 🎯 Kâr-al formülleri — PROTOKOL_karal2.md")
yaz("_Giriş B (mesajdaki fiyata limit) ana · vadeli ücret + fonlama yaklaşığı · ii = işlem isabeti · si = saat isabeti (sınıfın saat sepeti) · net = işlem başı % · kontrol dönemi ikinci kullanım (destekleyici kanıt)_\n")
SEC = {}
for sn in SIN:
    d = D[D.sinif == sn]; g = "B"
    b_k = olc(donem(d, P0, A25), f"{g}_T0")
    aday = [f"{g}_T1_{tau}" for tau in TAU]
    for sx in ("s168", "s24", "atr"):                                                       # eşit isabet: T0'ın keşif işlem isabetine en yakın k
        cs = [f"{g}_T2_{sx}_{k}" for k in KG if f"{g}_T2_{sx}_{k}" in d]
        if cs: aday.append(min(cs, key=lambda c: abs(olc(donem(d, P0, A25), c)["ii"] - b_k["ii"])))
    bilgi = [f"{g}_T3", f"{g}_T13"]
    yaz(f"## {sn}")
    yaz("| Formül | " + " | ".join(f"{a}: n · ii · si · net" for a, _, _ in KES) + " | keşif şartı |"); yaz("|---|" + "---|" * (len(KES) + 1))
    gec = []
    for c in [f"{g}_T0"] + aday + bilgi:
        os_ = [olc(donem(d, a, b), c) for _, a, b in KES]; bs = [olc(donem(d, a, b), f"{g}_T0") for _, a, b in KES]
        ok = (c in aday) and all(sart(o, b) for o, b in zip(os_, bs))
        if ok: gec.append((os_[0]["net"], c))
        yaz(f"| {c[2:]} | " + " | ".join(f"{o['n']} · %{o['ii']:.1f} · %{o['si']:.1f} · {o['net']:+.3f}" for o in os_) + f" | {'—' if c == f'{g}_T0' else ('bilgi' if c in bilgi else ('✅' if ok else '❌'))} |")
    SEC[sn] = max(gec)[1] if gec else None
    yaz(f"\n**Kontrole giden:** {SEC[sn][2:] if SEC[sn] else 'yok (keşif şartını geçen formül yok)'}\n")
json.dump(SEC, open("karal2_secim.json", "w"), ensure_ascii=False)
yaz("## Kontrol (2025+ · 2026) — ikinci kullanım")
yaz("| Sınıf | Formül | Dönem | n | ii | si | net | T0: ii · si · net | şart |"); yaz("|---|---|---|---|---|---|---|---|---|")
for sn in SIN:
    d = D[D.sinif == sn]
    for c in ([SEC[sn]] if SEC[sn] else []) + ["B_T0"]:
        for a_, a, b in KON:
            o = olc(donem(d, a, b), c); bb = olc(donem(d, a, b), "B_T0")
            yaz(f"| {sn} | {c[2:]} | {a_} | {o['n']} | %{o['ii']:.1f} | %{o['si']:.1f} | {o['net']:+.3f} | %{bb['ii']:.1f} · %{bb['si']:.1f} · {bb['net']:+.3f} | {'' if c == 'B_T0' else ('✅' if sart(o, bb) else '❌')} |")
yaz("\n## Bilgi: piyasa girişi (D) ile aynı formüller, kontrol dönemi")
yaz("| Sınıf | Formül | 2025+: ii · net | 2026: ii · net |"); yaz("|---|---|---|---|")
for sn in SIN:
    d = D[D.sinif == sn]
    for c in ["D_T0"] + ([("D" + SEC[sn][1:])] if SEC[sn] else []):
        if c not in d: continue
        o1, o2 = olc(donem(d, A25, SON), c), olc(donem(d, A26, SON), c)
        yaz(f"| {sn} | {c[2:]} | %{o1['ii']:.1f} · {o1['net']:+.3f} | %{o2['ii']:.1f} · {o2['net']:+.3f} |")
yaz("\n_Not: T1'de stop dolumu 1 dk mum içinde stop seviyesinden varsayıldı (kayma yok); gerçekte biraz daha kötü olabilir. Fonlama sabit %0,01/8 saat yaklaşığı._")
open("karal2_sonuc.md", "w").write("\n".join(L) + "\n")
