# kesif6d_analiz.py — PROTOKOL_kesif6c Ek: en yakın S2′ formülleri bakılmamış coin'lerde (BİLGİ)
src = open("kesif6c_analiz.py").read().split("hucre = lambda")[0]
exec(src)
hucre = lambda r, j: (f"{r['n']} · %{r['i'][j]:.0f} · {r['net'][j]:+.2f} · gün %{r['gi'][j]:.0f} · en kötü {r['kotu'][j]:+.1f} · liq {int(r['liq'][j])} · ayda {r['ay']:.1f}" if r else "0")
out.clear()
yaz("# 🔭 kesif6d — en yakın S2′ short formülleri, BAKILMAMIŞ coin'lerde (bilgi, karar değil)")
yaz("_hücre: işlem · işlem isabeti · işlem başı net % · gün isabeti · en kötü işlem % · 2x likidasyon · ayda işlem_\n")
for q in (2e6, 2e7):
    f = lambda m, q=q: (m.fr >= 0.0003) & (m.fp >= 0.98) & (m.liq >= q)
    for ad in ("T0.05_F20_H120", "T0.05_F20_H72"):
        j = ADLAR.index(ad)
        for g, gad in (("gor", "görülmüş"), ("yeni", "BAKILMAMIŞ")):
            idx = sec(g, f); R = olc(idx)
            yaz(f"- likidite≥{q / 1e6:.0f} M$ · {ad} · **{gad}:** " + " | ".join(f"{d} {hucre(R[d], j)}" for d in DON))
            if g == "yeni":
                n = X[idx, 2 * j]; t = M.t.values[idx]
                yaz(f"  - tümü {len(n)} işlem · isabet %{100 * (n > 0).mean():.1f} · ort. {100 * n.mean():+.2f} · medyan {100 * np.median(n):+.2f} · yıllara göre: " +
                    " · ".join(f"{y}: {int(((t >= np.datetime64(f'{y}-01-01')) & (t < np.datetime64(f'{y + 1}-01-01'))).sum())} işlem ort. {100 * n[(t >= np.datetime64(f'{y}-01-01')) & (t < np.datetime64(f'{y + 1}-01-01'))].mean():+.2f}" for y in range(2022, 2027)))
    yaz()
open("kesif6d_sonuc.md", "w").write("\n".join(out) + "\n")
