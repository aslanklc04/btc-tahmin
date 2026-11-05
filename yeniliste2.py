# yeniliste2.py — PROTOKOL_yeniliste.md Ek 1: portföy düzeyi sağlamlık testleri → yeniliste2_sonuc.md
import hashlib, numpy as np, pandas as pd
src = open("yeniliste.py").read().split("AY = list(")[0]; exec(src)
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
def olay2(s, L, k, H, uc, fm):
    i0 = gun.searchsorted(L + pd.Timedelta(days=k)); i1 = i0 + H - 1
    if i0 >= len(gun): return None
    o = O[s].iloc[i0]
    if not np.isfinite(o): return None
    cc = C[s].iloc[i0:i1 + 1].dropna()
    if not len(cc): return None
    ce, te = cc.iloc[-1], cc.index[-1]; fr = FG.get(s)
    if fr is not None:
        f = fr[(fr.index >= gun[i0]) & (fr.index < te + pd.Timedelta(days=1))]; fon = f[f > 0].sum() + fm * f[f < 0].sum()
    else: fon = 0.0
    return max(max(-(ce / o - 1), -1.0) - uc + fon, -1.0), gun[i0], te
def portfoy(k=1, H=30, uc=UC, fm=1.0, filtre=None, cikar_top=0):
    rows = []
    for s, x in EV.iterrows():
        if filtre is not None and not filtre(s): continue
        v = olay2(s, x.ilk, k, H, uc, fm)
        if v: rows.append((s, x.ilk, *v))
    D = pd.DataFrame(rows, columns=["s", "L", "net", "gir", "cik"]).sort_values("gir")
    if cikar_top: D = D.drop(D.net.nlargest(cikar_top).index)
    acik, tut = [], []                                                                             # en çok 40 açık pozisyon
    for r in D.itertuples():
        acik = [c for c in acik if c >= r.gir]
        if len(acik) >= 40: tut.append(False); continue
        acik.append(r.cik); tut.append(True)
    D = D[tut]; m = (D.groupby(D.cik.dt.tz_convert(None).dt.to_period("M")).net.sum() * 0.02)
    m = m.reindex(pd.period_range(m.index.min(), m.index.max(), freq="M"), fill_value=0.0)
    S = {}
    for y in (2024, 2025, 2026):
        a = m[m.index.year == y]; c = a.cumsum(); dd = (c - c.cummax()).min() if len(a) else np.nan
        S[y] = (a.sum(), a.min(), dd, (a > 0).mean(), len(D[D.cik.dt.year == y]))
    return S
yari = lambda h: (lambda s: int(hashlib.md5(taban(s).encode()).hexdigest(), 16) % 2 == h)
TEST = {"P0 temel": {}, "P1 kayma %0,30/taraf": {"uc": 2 * (0.0005 + 0.003)}, "P2 negatif fonlama ×1,5": {"fm": 1.5}, "P3 coin yarısı 0": {"filtre": yari(0)},
        "P4 coin yarısı 1": {"filtre": yari(1)}, "P5 en iyi 5 olay çıkarılmış": {"cikar_top": 5}, "P6a k 3 · H 30": {"k": 3}, "P6b k 1 · H 14": {"H": 14},
        "P6c k 3 · H 14": {"k": 3, "H": 14}, "P7 kayma %0,30 + fonlama ×1,5": {"uc": 2 * (0.0005 + 0.003), "fm": 1.5}}
yaz("# 🆕 Yeni listeleme short — portföy sağlamlık testleri (PROTOKOL_yeniliste.md Ek 1)"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · her olaya %2 · 1× · en çok 40 açık · hücre: yıllık toplam · en kötü ay · yıl içi en büyük düşüş · pozitif ay · kapanan işlem_\n")
yaz("| test | 2024 | 2025 | 2026 (Eki'ye kadar) | sonuç |"); yaz("|---|---|---|---|---|")
HEP = True
for ad, kw in TEST.items():
    S = portfoy(**kw); g = all(v[0] > 0 and v[1] >= -0.10 and v[2] >= -0.20 and v[3] >= 0.55 for v in S.values()); HEP &= g
    yaz(f"| {ad} | " + " | ".join(f"{100 * v[0]:+.1f}% · {100 * v[1]:+.1f}% · {100 * v[2]:.1f}% · %{100 * v[3]:.0f} · {v[4]}" for v in S.values()) + f" | {'✔' if g else '✘'} |")
yaz(f"\n**Sonuç → {'✅ HEPSİ GEÇTİ → 🆕 gölge kurulur' if HEP else '❌ geçmedi → gölge kurulmaz'}**")
open(__import__("os").environ.get("YL2_CIKTI", "yeniliste2_sonuc.md"), "w").write("\n".join(out) + "\n")
