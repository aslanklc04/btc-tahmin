# giris2_analiz.py — PROTOKOL_giris2.md: keşifte seçim → kontrol (bir kez) → giris2_sonuc.md
import glob, numpy as np, pandas as pd
D = pd.concat([pd.read_csv(p) for p in glob.glob("parca/**/giris2_p*.csv.gz", recursive=True)], ignore_index=True); D["t"] = pd.to_datetime(D.t, utc=True)
P0, YARI, A25, A26 = (pd.Timestamp(x, tz="UTC") for x in ("2022-06-01", "2023-07-01", "2025-01-01", "2026-01-01")); SON = D.t.max() + pd.Timedelta(hours=1)
ALT = ["D7", "E15", "E30", "E60", "P10", "P25", "P50", "P25E60"]; SIN = ["✅ ana (+0,75σ)", "🔸 yedek (+0,50σ)", "📋 panelden (+0,45σ)"]
DON = {"½-1": (P0, YARI), "½-2": (YARI, A25), "KEŞİF": (P0, A25), "2025+": (A25, SON), "2026": (A26, SON)}
L = []; yaz = lambda s="": (print(s), L.append(s))
def olc(d, c):
    x = d[["t", c]]; f = x[c].notna(); y = x[f]
    if not len(y): return dict(n=len(x), dol=0, ii=np.nan, inet=np.nan, snet=np.nan, si=np.nan, snt=np.nan)
    sp = y.groupby("t")[c].mean()
    return dict(n=len(x), dol=100 * f.mean(), ii=100 * (y[c] > 0).mean(), inet=100 * y[c].mean(), snet=100 * y[c].sum() / len(x), si=100 * (sp > 0).mean(), snt=100 * sp.mean())
def sart(o, b): return o["snet"] >= b["snet"] + 0.03 and o["si"] >= b["si"] - 1 and o["ii"] >= b["ii"] - 2
yaz("# 🚪 Giriş kuralı: limit dolmazsa ne yapmalı? — PROTOKOL_giris2.md")
yaz(f"_{len(D):,} sinyal · 1 dk mum · vadeli ücret + fonlama · 🎯 mesajdaki sabit fiyat · sinyal başı net = dolan işlemlerin toplamı / TÜM sinyaller (dolmayan = 0)_\n")
yaz("_Sütun: dolum % · işlem isabeti · işlem başı net · **sinyal başı net** · saat isabeti · saat başı net_\n")
for sn in SIN:
    d = D[D.sinif == sn]; yaz(f"## {sn}")
    yaz("| Giriş | " + " | ".join(DON) + " | keşif şartı |"); yaz("|---|" + "---|" * (len(DON) + 1))
    ob = {dn: olc(d[(d.t >= a) & (d.t < b)], "B") for dn, (a, b) in DON.items()}; gec = []
    for c in ["B"] + ALT:
        oo = {dn: olc(d[(d.t >= a) & (d.t < b)], c) for dn, (a, b) in DON.items()}
        ok = c != "B" and sart(oo["½-1"], ob["½-1"]) and sart(oo["½-2"], ob["½-2"])
        if ok: gec.append((oo["KEŞİF"]["snet"], c))
        yaz(f"| {c} | " + " | ".join(f"%{o['dol']:.0f} · %{o['ii']:.1f} · {o['inet']:+.3f} · **{o['snet']:+.3f}** · %{o['si']:.1f} · {o['snt']:+.3f}" for o in oo.values()) + f" | {'—' if c == 'B' else ('✅' if ok else '❌')} |")
    sec = max(gec)[1] if gec else None
    if sec:
        oo = {dn: olc(d[(d.t >= a) & (d.t < b)], sec) for dn, (a, b) in DON.items()}; k = all(sart(oo[x], ob[x]) for x in ("2025+", "2026"))
        yaz(f"\n**Keşiften seçilen: {sec} → KONTROL (2025+ ve 2026): {'✅ GEÇTİ — B yerine önerilir' if k else '❌ geçmedi — B kalır'}**\n")
    else: yaz("\n**Keşif şartını geçen alternatif yok → B kalır.**\n")
try:                                                                                           # tutarlılık: B, karal2_veri B_T0 ile aynı mı
    K2 = pd.read_csv("karal2_veri.csv.gz"); K2["t"] = pd.to_datetime(K2.t, utc=True); m = D.merge(K2[["t", "nm", "sinif", "H", "B_T0"]], on=["t", "nm", "sinif", "H"])
    yaz(f"_Tutarlılık: {len(m):,} eşleşen sinyal · B dolumu aynı %{100 * (m.B.notna() == m.B_T0.notna()).mean():.1f} · |B − karal2 B_T0| ort. {100 * (m.B - m.B_T0).abs().mean():.4f} puan_\n")
except Exception as e: yaz(f"_tutarlılık kontrolü yapılamadı: {e!r}_")
yaz("## Bilgi: canlı karne (12.10 →, karne_gercek.csv) — yalnız B ve D7 var")
try:
    K = pd.read_csv("canli/durum/karne_gercek.csv")
    for sn in ("ana", "yedek", "panelden"):
        k = K[K.sinif == sn]
        for c in ("B_T0", "D_T0"):
            x = k[c]; f = x.notna(); yaz(f"- {sn} {c[0]}: {len(k)} sinyal · dolum %{100 * f.mean():.0f} · işlem isabeti %{100 * (x[f] > 0).mean():.0f} · işlem başı {100 * x[f].mean():+.2f} · sinyal başı {100 * x[f].sum() / max(len(k), 1):+.2f}")
except Exception as e: yaz(f"_okunamadı: {e!r}_")
open("giris2_sonuc.md", "w").write("\n".join(L) + "\n")
