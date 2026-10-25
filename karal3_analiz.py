# karal3_analiz.py — PROTOKOL_karal3.md: keşif → kontrol (bir kez) → karal3_sonuc.md
import glob, numpy as np, pandas as pd
D = pd.concat([pd.read_csv(p) for p in glob.glob("parca/**/karal3_p*.csv.gz", recursive=True)], ignore_index=True); D["t"] = pd.to_datetime(D.t, utc=True)
P0, YARI, A25, A26 = (pd.Timestamp(x, tz="UTC") for x in ("2022-06-01", "2023-07-01", "2025-01-01", "2026-01-01")); SON = D.t.max() + pd.Timedelta(hours=1)
SIN = ["✅ ana (+0,75σ)", "🔸 yedek (+0,50σ)", "📋 panelden (+0,45σ)"]; DON = {"½-1": (P0, YARI), "½-2": (YARI, A25), "KEŞİF": (P0, A25), "2025+": (A25, SON), "2026": (A26, SON)}
for x in (0.0025, 0.005):
    u = D.y > x; tag = f"{x * 100:g}"
    D[f"K{tag}"] = np.where(u, D.D7, D.B); D[f"K{tag}h"] = np.where(u, D.D7h, D.B); D[f"K{tag}f"] = np.where(u, D.D7f, D.B); D[f"u{tag}"] = u
L = []; yaz = lambda s="": (print(s), L.append(s))
def olc(d, c):
    y = d[["t", c]].dropna()
    if not len(y): return dict(n=len(d), ii=np.nan, snet=np.nan, si=np.nan, inet=np.nan)
    sp = y.groupby("t")[c].mean()
    return dict(n=len(d), ii=100 * (y[c] > 0).mean(), inet=100 * y[c].mean(), snet=100 * y[c].sum() / len(d), si=100 * (sp > 0).mean())
def sart(o, b): return o["snet"] >= b["snet"] + 0.03 and o["ii"] >= b["ii"] - 1 and o["si"] >= b["si"] - 1
yaz("# 🎯 Yükselmişken piyasadan alınca 🎯'yi kaydırmak — PROTOKOL_karal3.md")
yaz(f"_{len(D):,} sinyal · 1 dk mum · vadeli ücret + fonlama · taban Kx: yükselme > x ise piyasadan (🎯 sabit), değilse 60 dk limit · sütun: işlem isabeti · işlem başı net · **sinyal başı net** · saat isabeti_\n")
for sn in SIN:
    d = D[D.sinif == sn]; yaz(f"## {sn}"); yaz("| Kural | " + " | ".join(DON) + " | keşif |"); yaz("|---|" + "---|" * (len(DON) + 1)); gec = []
    for c in ["B", "K0.25", "K0.25h", "K0.25f", "K0.5", "K0.5h", "K0.5f"]:
        oo = {dn: olc(d[(d.t >= a) & (d.t < b)], c) for dn, (a, b) in DON.items()}; ok = None
        if c[-1] in "hf":
            bb = {dn: olc(d[(d.t >= a) & (d.t < b)], c[:-1]) for dn, (a, b) in DON.items()}
            ok = sart(oo["½-1"], bb["½-1"]) and sart(oo["½-2"], bb["½-2"])
            if ok: gec.append((oo["KEŞİF"]["snet"], c))
        yaz(f"| {c} | " + " | ".join(f"%{o['ii']:.1f} · {o['inet']:+.3f} · **{o['snet']:+.3f}** · %{o['si']:.1f}" for o in oo.values()) + f" | {'' if ok is None else ('✅' if ok else '❌')} |")
    if gec:
        c = max(gec)[1]; oo = {dn: olc(d[(d.t >= a) & (d.t < b)], c) for dn, (a, b) in DON.items()}; bb = {dn: olc(d[(d.t >= a) & (d.t < b)], c[:-1]) for dn, (a, b) in DON.items()}
        k = all(sart(oo[x], bb[x]) for x in ("2025+", "2026")); yaz(f"\n**Keşiften seçilen: {c} → KONTROL: {'✅ GEÇTİ — önerilir' if k else '❌ geçmedi'}**")
    else: yaz("\n**Keşif şartını geçen kural yok.**")
    for tag in ("0.25", "0.5"):
        yaz(f"- bilgi, yalnız yükselme > %{tag} olan işlemler: " + " · ".join(f"{dn}: n {int(d[(d.t >= a) & (d.t < b)][f'u{tag}'].sum())} · sabit {olc(d[(d.t >= a) & (d.t < b) & d[f'u{tag}']], 'D7')['inet']:+.3f} (%{olc(d[(d.t >= a) & (d.t < b) & d[f'u{tag}']], 'D7')['ii']:.0f}) → ½ {olc(d[(d.t >= a) & (d.t < b) & d[f'u{tag}']], 'D7h')['inet']:+.3f} (%{olc(d[(d.t >= a) & (d.t < b) & d[f'u{tag}']], 'D7h')['ii']:.0f}) → tam {olc(d[(d.t >= a) & (d.t < b) & d[f'u{tag}']], 'D7f')['inet']:+.3f} (%{olc(d[(d.t >= a) & (d.t < b) & d[f'u{tag}']], 'D7f')['ii']:.0f})" for dn, (a, b) in DON.items() if dn in ("KEŞİF", "2025+", "2026")))
    yaz("")
try:
    G2 = pd.read_csv("giris2_veri.csv.gz"); G2["t"] = pd.to_datetime(G2.t, utc=True); m = D.merge(G2[["t", "nm", "sinif", "H", "B", "D7"]], on=["t", "nm", "sinif", "H"], suffixes=("", "_g"))
    yaz(f"_Tutarlılık (giris2 ile): {len(m):,} · |B fark| {100 * (m.B - m.B_g).abs().mean():.4f} · |D7 fark| {100 * (m.D7 - m.D7_g).abs().mean():.4f}_")
except Exception as e: yaz(f"_tutarlılık: {e!r}_")
open("karal3_sonuc.md", "w").write("\n".join(L) + "\n")
