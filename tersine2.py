# tersine2.py — PROTOKOL_tersine.md Ek 1: S (+%50 · H 1 · stop yok) sağlamlık testleri → tersine2_sonuc.md
import hashlib, numpy as np, pandas as pd
src = open("tersine.py").read(); exec(src.split("def calistir(")[0])
KAY, FM = 0.001, 1.0
def islem(j, g, yon, H, stop):
    i0, i1 = g + 1, g + H
    if i1 >= n or not np.isfinite(Ov[i0, j]): return None
    pe = Ov[i0, j] * (1 + KAY * yon); cc = Cv[i0:i1 + 1, j]; ok = np.where(np.isfinite(cc))[0]
    if not len(ok): return None
    ex = i0 + ok[-1]; net = yon * (cc[ok[-1]] * (1 - KAY * yon) / pe - 1)
    fon = Fv[i0:ex + 1, j].sum() * (-yon); fon = fon * FM if fon < 0 else fon
    return max(max(net, -1.0) - 0.001 + fon, -1.0), ex, fon
exec("def calistir(" + src.split("def calistir(")[1].split("hf = lambda")[0])
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
yari = lambda s: int(hashlib.md5(s[:-4].encode()).hexdigest(), 16) % 2
def ozet(D, ad):
    hc, ok = [], True
    for y in (2024, 2025, 2026):
        d = D[D.y == y]; g = len(d) > 0 and d.net.mean() > 0 and (d.net > 0).mean() >= 0.55; ok &= g
        hc.append(f"{len(d)} · {100 * d.net.mean():+.1f}% · kaz %{100 * (d.net > 0).mean():.0f}" if len(d) else "—")
    yaz(f"| {ad} | " + " | ".join(hc) + f" | {'✔' if ok else '✘'} |"); return ok
yaz("# 🔄 Yükselişten sonra short — sağlamlık testleri (PROTOKOL_tersine.md Ek 1)"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · temel: günlük değişim ≥ +%50 → ertesi gün açılışta short, aynı gün kapanışta çıkış, stop yok · hücre: n · ort. net · kazanma_\n")
yaz("| test | 2024 | 2025 | 2026 | sonuç |"); yaz("|---|---|---|---|---|")
D0 = calistir(-1, 0.50, 1, None); HEP = ozet(D0, "temel")
HEP &= ozet(D0[D0.s.map(yari) == 0], "R1 coin yarısı 0"); HEP &= ozet(D0[D0.s.map(yari) == 1], "R2 coin yarısı 1")
HEP &= ozet(D0.drop(D0.net.nlargest(5).index), "R3 en iyi 5 işlem çıkarılmış")
KAY = 0.003; HEP &= ozet(calistir(-1, 0.50, 1, None), "R4 kayma %0,30/taraf"); KAY = 0.001
FM = 1.5; HEP &= ozet(calistir(-1, 0.50, 1, None), "R5 ödenen fonlama ×1,5"); FM = 1.0
HEP &= ozet(calistir(-1, 0.40, 1, None), "R6a eşik +%40"); HEP &= ozet(calistir(-1, 0.60, 1, None), "R6b eşik +%60"); HEP &= ozet(calistir(-1, 0.50, 2, None), "R6c H 2 gün")
D = D0.copy(); D = D.sort_values("net").groupby("g").head(10)                                     # aynı gün en çok 10
m = D.groupby(D.g.dt.tz_convert(None).dt.to_period("M")).net.sum() * 0.02; m = m.reindex(pd.period_range(m.index.min(), m.index.max(), freq="M"), fill_value=0)
r7 = []
for y in (2024, 2025, 2026):
    a = m[m.index.year == y]; g = a.sum() > 0 and a.min() >= -0.10 and (a > 0).mean() >= 0.55; HEP &= g
    r7.append(f"{100 * a.sum():+.1f}% · en kötü ay {100 * a.min():+.1f}% · pozitif ay %{100 * (a > 0).mean():.0f} {'✔' if g else '✘'}")
yaz(f"| R7 portföy (%2, günde ≤ 10) | " + " | ".join(r7) + " | |")
yaz(f"\n**Sonuç → {'✅ HEPSİ GEÇTİ → gölge kurulabilir (onayla)' if HEP else '❌ geçmedi'}**")
yaz(f"\n_Bilgi: 2026'da ayda ortalama {len(D0[D0.y == 2026]) / 10:.0f} işlem · en kötü işlem {100 * D0.net.min():.0f}% · −%50'den kötü işlem oranı 2025 %{100 * (D0[D0.y == 2025].net <= -0.5).mean():.0f}, 2026 %{100 * (D0[D0.y == 2026].net <= -0.5).mean():.0f}_")
open("tersine2_sonuc.md", "w").write("\n".join(out) + "\n")
