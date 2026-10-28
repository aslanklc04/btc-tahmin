# kesif5b_analiz.py — PROTOKOL_kesif5 Ek: F5 geride kalan, bakılmamış coin'lerde (BİLGİ)
src = open("kesif5_analiz.py").read().split("hucre = lambda")[0]
exec(src)
hucre = lambda r, j: (f"{r['n']} · %{r['i'][j]:.0f} · {r['net'][j]:+.2f} · gün %{r['gi'][j]:.0f} · en kötü {r['kotu'][j]:+.1f} · liq {int(r['liq'][j])} · ayda {r['ay']:.1f}" if r else "0")
out.clear()
yaz("# 🧲 kesif5b — geride kalan coin, BAKILMAMIŞ coin'lerde (bilgi, karar değil)")
yaz("_hücre: işlem · işlem isabeti · işlem başı net % · gün isabeti · en kötü işlem % · 2x likidasyon · ayda işlem_\n")
f = lambda m: (m.btc24 >= 0.05) & (m.r24 - m.btc24 <= -0.02)
for ad in ("T0.03_yok_H72", "T0.05_yok_H72", "T0.03_S_H72"):
    j = ADLAR.index(ad)
    for g, gad in (("gor", "görülmüş"), ("yeni", "BAKILMAMIŞ")):
        idx = sec(g, f); R = olc(idx)
        yaz(f"- {ad} · **{gad}:** " + " | ".join(f"{d} {hucre(R[d], j)}" for d in DON))
        if g == "yeni":
            n = X[idx, 2 * j]; gun = M.gun.values[idx]; G = pd.Series(n).groupby(gun).agg(["mean", "size"])
            yaz(f"  - tümü {len(n)} işlem · isabet %{100 * (n > 0).mean():.1f} · ort. {100 * n.mean():+.2f} · {len(G)} farklı gün · gün isabeti %{100 * (G['mean'] > 0).mean():.0f} · en kalabalık gün {int(G['size'].max())} işlem")
    yaz()
open("kesif5b_sonuc.md", "w").write("\n".join(out) + "\n")
