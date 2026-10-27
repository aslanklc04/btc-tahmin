# igne3_analiz.py — PROTOKOL_igne3.md kararı → igne3_sonuc.md
import glob, numpy as np, pandas as pd
out = []; yaz = lambda s="": (out.append(s), print(s))
L_ = []
for f in sorted(glob.glob("parca/igne3-p-*/igne3_p*.csv.gz")):
    try: L_.append(pd.read_csv(f))
    except pd.errors.EmptyDataError: pass
R = pd.concat(L_, ignore_index=True); R["t"] = pd.to_datetime(R.t, utc=True); R = R.sort_values("t").reset_index(drop=True)
eksik = sorted(set(sum([open(f).read().split() for f in glob.glob("parca/igne3-p-*/igne3_eksik_p*.txt")], [])))
U = lambda s: pd.Timestamp(s, tz="UTC")
DON = {"½-1": (U("2022-06-01"), U("2023-07-01")), "½-2": (U("2023-07-01"), U("2025-01-01")), "2025+": (U("2025-01-01"), U("2027-01-01")), "2026": (U("2026-01-01"), U("2027-01-01"))}
def sec(k, filt):
    x = R[(R.kr >= k) & ((R.rb >= -0.015) if filt else True)]
    keep, son = [], {}
    for i, t, nm in zip(x.index, x.t, x.nm):                                   # aynı coin'de 24 saat bekleme
        if nm in son and t - son[nm] < pd.Timedelta(hours=24): continue
        son[nm] = t; keep.append(i)
    return x.loc[keep]
def ol(x, H, a, z):
    x = x[(x.t >= a) & (x.t < z)].dropna(subset=[f"n{H}"]); n = len(x)
    if not n: return dict(n=0)
    s = x.groupby("t")[f"n{H}"].mean(); hf = n / max((min(z, R.t.max()) - a).days / 7, 1)
    return dict(n=n, i=100 * (x[f"n{H}"] > 0).mean(), net=100 * x[f"n{H}"].mean(), si=100 * (s > 0).mean(), kotu=100 * x[f"n{H}"].min(), liq=int((x[f"mae{H}"] <= -0.45).sum()), hf=hf)
f_ = lambda o: (f"{o['n']} · %{o['i']:.1f} · {o['net']:+.2f} · saat %{o['si']:.0f} · {o['kotu']:+.1f} · liq {o['liq']} · haftada {o['hf']:.1f}" if o["n"] else "0")
sart = lambda o, m: o["n"] >= m and o["i"] >= 70 and o["net"] >= 0.20 and o["si"] >= 65 and o["liq"] == 0
yaz("# 🪡 İğne SONRASI alım — PROTOKOL_igne3.md · Binance vadeli 1 dk")
yaz(f"{R.nm.nunique()} coin · k ≥ 4 aday {len(R):,} · veri bulunamayan: {len(eksik)} ({', '.join(eksik)}) · son {R.t.max()}")
yaz("_hücre: işlem · işlem isabeti · işlem başı net % · saat isabeti · en kötü % · 2x likidasyon · haftada işlem_\n")
for baslik, alt in (("KARAR — tüm evren (126 + 15)", None), ("Bilgi — yalnız 126 yeni coin", "yeni"), ("Bilgi — yalnız 15 ana coin", "eski")):
    yaz(f"## {baslik}"); yaz("| Kural | " + " | ".join(DON) + " | keşif |"); yaz("|---|" + "---|" * (len(DON) + 1))
    gec, RS = [], {}
    for k in (4, 6):
        for filt in (False, True):
            x0 = sec(k, filt); x0 = x0 if alt is None else x0[x0.grup == alt]
            for H in (4, 24):
                oo = {dn: ol(x0, H, a, z) for dn, (a, z) in DON.items()}; RS[(k, filt, H)] = oo
                ok = sart(oo["½-1"], 50) and sart(oo["½-2"], 50)
                if ok: gec.append(((oo["½-1"]["net"] * oo["½-1"]["n"] + oo["½-2"]["net"] * oo["½-2"]["n"]) / (oo["½-1"]["n"] + oo["½-2"]["n"]), (k, filt, H)))
                yaz(f"| k{k} · BTC filtresi {'var' if filt else 'yok'} · {H} s | " + " | ".join(f_(o) for o in oo.values()) + f" | {'✅' if ok else '❌'} |")
    if alt is None:
        if gec:
            kk = max(gec)[1]; oo = RS[kk]; kon = sart(oo["2025+"], 30) and sart(oo["2026"], 30)
            yaz(f"\n**Keşiften seçilen: k{kk[0]} · BTC filtresi {'var' if kk[1] else 'yok'} · {kk[2]} s → KONTROL: {'✅ GEÇTİ' if kon else '❌ geçmedi'}**\n")
        else: yaz("\n**❌ Keşif şartını geçen kural yok.**\n")
    else: yaz()
yaz("## Bilgi — 10.10.2025 günü (k4)")
for filt in (False, True):
    x = sec(4, filt); x = x[(x.t >= U("2025-10-10")) & (x.t < U("2025-10-12"))]
    yaz(f"- BTC filtresi {'var' if filt else 'yok'}: {len(x)} sinyal · 24 s ort. {100 * x.n24.mean():+.2f} · isabet %{100 * (x.n24 > 0).mean():.0f}" if len(x) else f"- BTC filtresi {'var' if filt else 'yok'}: sinyal yok")
open("igne3_sonuc.md", "w").write("\n".join(out) + "\n")
