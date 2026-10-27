# igne4b_analiz.py — PROTOKOL_igne4 Ek: en yakın 2 formül bakılmamış coin'lerde (BİLGİ)
src = open("igne4_analiz.py").read().split("# ---- TARAMA")[0].replace('open("igne4_sonuc.md"', 'open("_x"')
exec(src)
out.clear()
FORM = [((8, 0.75, np.inf, -0.01, -np.inf), "f1.25_S2_H48"), ((6, 0.75, np.inf, -np.inf, -np.inf), "f1.25_yok_H48")]
yaz("# 🪡 igne4 Ek — en yakın 2 formül, bakılmamış coin'lerde (BİLGİ, karar değil)")
yaz("_hücre: işlem · işlem isabeti · işlem başı net % · saat isabeti · en kötü işlem % · 2x likidasyon · haftada işlem_\n")
for F, ad in FORM:
    j = ADLAR.index(ad); yaz(f"## {fad(F)} · {ad}")
    for g, gad in (("gor", "görülmüş 141"), ("yeni", "bakılmamış")):
        idx = sec(g, F); R = olc(idx); yaz(f"- **{gad}:** " + " | ".join(f"{d} {hucre(R[d], j)}" for d in DON))
        x = M.loc[idx]; ii = idx[((x.t >= U("2025-10-10")) & (x.t < U("2025-10-12"))).values]
        yaz(f"  - 10–11.10.2025: " + (f"{len(ii)} işlem · ort. {100 * X[ii, 2 * j].mean():+.2f} · isabet %{100 * (X[ii, 2 * j] > 0).mean():.0f}" if len(ii) else "işlem yok"))
        if g == "yeni":
            n = X[idx, 2 * j]; yaz(f"  - tümü: {len(n)} işlem · isabet %{100 * (n > 0).mean():.1f} · ort. {100 * n.mean():+.2f} · medyan {100 * np.median(n):+.2f} · en kötü %5 dilim {100 * np.percentile(n, 5):+.1f}")
    yaz()
open("igne4b_sonuc.md", "w").write("\n".join(out) + "\n")
