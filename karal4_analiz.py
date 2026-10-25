# karal4_analiz.py — PROTOKOL_karal4.md: yükselmiş / düşmüş fiyata göre 🎯 → karal4_sonuc.md
import glob, numpy as np, pandas as pd
L = []; yaz = lambda s="": (print(s), L.append(s))
S = pd.concat([pd.read_csv(p) for p in glob.glob("parca/**/karal4_p*.csv.gz", recursive=True)], ignore_index=True); S["t"] = pd.to_datetime(S.t, utc=True)
S = S.rename(columns={"D7": "n0", "D7h": "nh", "D7f": "nf"})
C = pd.concat([pd.read_csv(p) for p in glob.glob("parca/**/coinsec2_p*.csv.gz", recursive=True)], ignore_index=True); C["t"] = pd.to_datetime(C.t, utc=True); C = C[C.grp != "BTC"]
P0, YARI, A25, A26 = (pd.Timestamp(x, tz="UTC") for x in ("2022-06-01", "2023-07-01", "2025-01-01", "2026-01-01")); SON = pd.Timestamp("2027-01-01", tz="UTC")
def olc(d, c):
    x = d[c].dropna(); return dict(n=len(x), ii=100 * (x > 0).mean() if len(x) else np.nan, net=100 * x.mean() if len(x) else np.nan)
def iyi(o, b): return (o["net"] >= b["net"] + 0.03 and o["ii"] >= b["ii"] - 1) or (o["ii"] >= b["ii"] + 3 and o["net"] >= b["net"])
def satir(ad, d):
    o0, oh, of = olc(d, "n0"), olc(d, "nh"), olc(d, "nf")
    yaz(f"| {ad} | {o0['n']} | %{o0['ii']:.1f} · {o0['net']:+.3f} | %{oh['ii']:.1f} · {oh['net']:+.3f} {'✅' if iyi(oh, o0) else '❌'} | %{of['ii']:.1f} · {of['net']:+.3f} {'✅' if iyi(of, o0) else '❌'} |")
    return iyi(oh, o0), iyi(of, o0), oh["net"], of["net"]
YENI = {"A 2025+": C[(C.grp == "A") & (C.t >= A25)], "B 2022–24": C[(C.grp == "B") & (C.t >= P0) & (C.t < A25)], "B 2025+": C[(C.grp == "B") & (C.t >= A25)]}
SIN = ["✅ ana (+0,75σ)", "🔸 yedek (+0,50σ)", "📋 panelden (+0,45σ)"]
yaz("# 🎯 Mesaj anında fiyat yükselmiş / düşmüşse 🎯'yi ayarlamak — PROTOKOL_karal4.md")
yaz(f"_Yalnız etkilenen işlemler · piyasa girişi · hücre: işlem isabeti · işlem başı net % · ✅ = tabana (🎯 sabit) göre 'iyi' · yeni veri: {len(C):,} coin-olay (BTC güçlü ↑ saatleri, 5 dk), sinyal verisi: {len(S):,} sinyal (1 dk)_\n")
for yon, esik in (("YUKARI", 0.0025), ("AŞAĞI", -0.0025)):
    m = (lambda d: d[d.y > esik]) if yon == "YUKARI" else (lambda d: d[d.y < esik])
    yaz(f"## {yon} ({'y > +%0,25' if yon == 'YUKARI' else 'y < −%0,25'}) — 🎯 sabit | 🎯·(1+½y) | 🎯·(1+y)")
    yaz("### Yeni veri (karar)"); yaz("| Küme | n | 🎯 sabit | ½ | tam |"); yaz("|---|---|---|---|---|")
    R = {k: satir(k, m(v)) for k, v in YENI.items()}
    if yon == "YUKARI":
        gec = [(np.mean([R[k][2 + j] for k in R]), ad) for j, ad in enumerate(("U½", "U1")) if all(R[k][j] for k in R)]
        yaz(f"\n**YUKARI karar: {('✅ ' + max(gec)[1] + ' GEÇTİ') if gec else '❌ geçen yok'}**\n")
        yaz("### Bilgi: sinyal verisi (karal3'te görüldü)"); yaz("| Sınıf · dönem | n | 🎯 sabit | ½ | tam |"); yaz("|---|---|---|---|---|")
        for sn in SIN:
            for dn, a, b in (("2022–24", P0, A25), ("2025+", A25, SON), ("2026", A26, SON)): satir(f"{sn} {dn}", m(S[(S.sinif == sn) & (S.t >= a) & (S.t < b)]))
    else:
        yaz("### Sinyal verisi: keşif (iki yarı) → kontrol"); yaz("| Sınıf · dönem | n | 🎯 sabit | ½ | tam |"); yaz("|---|---|---|---|---|")
        for sn in SIN:
            d = m(S[S.sinif == sn]); r1 = satir(f"{sn} ½-1", d[(d.t >= P0) & (d.t < YARI)]); r2 = satir(f"{sn} ½-2", d[(d.t >= YARI) & (d.t < A25)]); rk = satir(f"{sn} KEŞİF", d[(d.t >= P0) & (d.t < A25)])
            ad = [(rk[2 + j], a_) for j, a_ in enumerate(("A½", "A1")) if r1[j] and r2[j]]
            if not ad: yaz(f"| **{sn} → keşif geçen yok** | | | | |"); continue
            sec = max(ad)[1]; j = 0 if sec == "A½" else 1
            k1 = satir(f"{sn} 2025+", d[d.t >= A25]); k2 = satir(f"{sn} 2026", d[d.t >= A26]); ok = k1[j] and k2[j] and all(R[k][j] for k in R)
            yaz(f"| **{sn} → keşif: {sec} → kontrol (2025+ · 2026 · yeni veri 3 küme): {'✅ GEÇTİ' if ok else '❌ geçmedi'}** | | | | |")
    yaz("")
yaz("## Bilgi: %0,5 eşiği (yeni veri)"); yaz("| Yön · küme | n | 🎯 sabit | ½ | tam |"); yaz("|---|---|---|---|---|")
for k, v in YENI.items(): satir(f"yukarı > %0,5 · {k}", v[v.y > 0.005]); satir(f"aşağı < −%0,5 · {k}", v[v.y < -0.005])
open("karal4_sonuc.md", "w").write("\n".join(L) + "\n")
