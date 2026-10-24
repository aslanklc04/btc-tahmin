# kesif.py — PROTOKOL_saat70.md (Ek 1 dahil) KEŞİF aşaması: yalnız 2022-06-01 → 2024-12-31. Doğrulama dönemi veriden SİLİNİR.
# Girdi: veri_seti.csv.gz · Çıktı: kesif_sonuc.md + kesif_adaylar.json (doğrulamaya gidecek ≤ 3 aday).
import json, itertools, numpy as np, pandas as pd
V = pd.read_csv("veri_seti.csv.gz", parse_dates=["t"])
V = V[V.t < pd.Timestamp("2025-01-01", tz="UTC")].copy()                                   # ← doğrulama dönemi burada atılır
assert V.t.max() < pd.Timestamp("2025-01-01", tz="UTC")
KG = [0.2, 0.3, 0.45, 0.5, 0.6, 0.75, 1.0, 1.25, 1.5, 2.0]
KS = {"✅ ana (+0,75σ)": 0.75, "🔸 yedek (+0,50σ)": 0.5, "📋 panelden (+0,45σ)": 0.45}
SIN = list(KS)
UC = {"vadeli": dict(Pg=0.0005, Lg=0.0002, Lc=0.0002, Pc=0.0005), "spot": dict(Pg=0.001, Lg=0.001, Lc=0.001, Pc=0.001)}
def net(df, k, gir="D", ucret="vadeli", yari=False):
    u = UC[ucret]; s = df.s.values; G = df.G.values; son = df.son.values
    if gir == "D": P = df.P.values; fg = np.full(len(df), u["Pg"]); dol = np.ones(len(df), bool)
    else: P = df.PB.values; fg = np.where(df.mB.values == 7, u["Pg"], u["Lg"]); dol = df.fB.values == 1
    sure = son / P - 1 - fg - u["Pc"]
    if k is None: r = sure
    else:
        tp = G * (1 + k * s); h = df[f"h{gir}{k}"].values.astype(bool)
        r = np.where(tp <= P, -fg - u["Pc"], np.where(h, tp / P - 1 - fg - u["Lc"], sure))
        if yari: r = 0.5 * r + 0.5 * sure
    return np.where(dol, r, np.nan)
def sepet(df, r):                                                                           # saat sepeti: aynı t'deki sinyallerin ortalaması
    x = pd.Series(r, index=df.index).groupby(df.t.values).mean().dropna(); return x
HAFTA = (pd.Timestamp("2025-01-01", tz="UTC") - pd.Timestamp("2022-06-01", tz="UTC")).days / 7
YARI = pd.Timestamp("2023-07-01", tz="UTC")
def ozet(x):
    if len(x) == 0: return dict(n=0, ist=np.nan, net=np.nan, hf=0, i1=np.nan, i2=np.nan, top=np.nan)
    i1 = (x[x.index < YARI] > 0).mean() if (x.index < YARI).any() else np.nan; i2 = (x[x.index >= YARI] > 0).mean() if (x.index >= YARI).any() else np.nan
    return dict(n=len(x), ist=100 * (x > 0).mean(), net=100 * x.mean(), hf=len(x) / HAFTA, i1=100 * i1, i2=100 * i2, top=100 * x.mean() * len(x) / HAFTA)
L = []; yaz = lambda s="": (print(s), L.append(s))
yaz("# 🔎 KEŞİF (2022-06 → 2024-12) — saat bazında isabet ve kâr · PROTOKOL_saat70.md")
yaz("_Saat isabeti = o saatte gelen sinyallerin ortalama neti > 0 · net = saat başı ortalama (%) · hf = haftada sinyalli saat · top = haftalık toplam net (%) · i1/i2 = keşifin iki yarısında saat isabeti · giriş t+7 dk piyasa (D) · vadeli ücret_\n")
# ---- taban (şimdiki kural) ----
def taban_r(df, gir="D", ucret="vadeli", kmap=None, yari=False):
    r = np.full(len(df), np.nan)
    for sn in SIN:
        m = (df.sinif == sn).values
        if m.any(): r[m] = net(df[m], (kmap or KS)[sn], gir, ucret, yari)
    return r
yaz("## Taban: şimdiki kural (sınıf k'ları, filtre yok)")
yaz("| Kapsam | Giriş · ücret | saat | saat isabeti | saat başı net | işlem isabeti | işlem başı net | hf |"); yaz("|---|---|---|---|---|---|---|---|")
for kap in ["tümü"] + SIN:
    d = V if kap == "tümü" else V[V.sinif == kap]
    for gir, uc in (("D", "vadeli"), ("B", "vadeli"), ("D", "spot")):
        r = taban_r(d, gir, uc); o = ozet(sepet(d, r)); rr = r[np.isfinite(r)]
        yaz(f"| {kap} | {gir} · {uc} | {o['n']} | %{o['ist']:.1f} | {o['net']:+.3f} | %{100 * (rr > 0).mean():.1f} | {100 * rr.mean():+.3f} | {o['hf']:.1f} |")
R0 = taban_r(V); T0 = ozet(sepet(V, R0)); NT = 0
# ---- Aşama 1: K-C (k ızgarası, sınıf başına; yarı 🎯) ----
yaz("\n## Aşama 1 — K-C çıkış: sınıf başına k (filtre yok, D, vadeli; sınıfın kendi saat sepeti)")
yaz("| Sınıf | k | saat isabeti | saat başı net | yarı🎯: isabet · net |"); yaz("|---|---|---|---|---|")
EN_K = {}
for sn in SIN:
    d = V[V.sinif == sn]; best = None
    for k in KG + [None]:
        o = ozet(sepet(d, net(d, k))); NT += 1; oy = ozet(sepet(d, net(d, k, yari=True))) if k is not None else None; NT += k is not None
        yaz(f"| {sn} | {k if k is not None else 'hedefsiz'} | %{o['ist']:.1f} | {o['net']:+.3f} | " + (f"%{oy['ist']:.1f} · {oy['net']:+.3f}" if oy else "—") + " |")
        for yr, oo in ((False, o), (True, oy)):
            if oo and oo["ist"] >= 72 and (best is None or oo["net"] > best[2]): best = (k, yr, oo["net"])
    EN_K[sn] = best
yaz("\nSınıf başına saat isabeti ≥ %72 olan en kârlı k: " + " · ".join(f"{sn.split(' (')[0]}: " + (f"k {b[0]}{' yarı' if b[1] else ''} ({b[2]:+.3f})" if b else "yok") for sn, b in EN_K.items()))
# ---- Aşama 2: K-A filtreler, K-B saat içi seçim ----
H_ = V.groupby("t").agg(n=("nm", "size"), b_r4=("b_r4", "first"), b_r24=("b_r24", "first"), zB=("zB", "first"), fon=("fon", "first"), gen24=("gen24", "first"), b_vr=("b_vr", "first"), hod=("hod", "first"), dow=("dow", "first"))
H_["dilim"] = H_.hod // 6; H_["hs"] = (H_.dow >= 5).astype(int)
SUR = ["n", "b_r4", "b_r24", "zB", "fon", "gen24", "b_vr"]
def secenek(c):                                                                              # (ad, spec) · spec = (sütun, alt, üst): alt < x ≤ üst
    if c == "dilim": return [(f"dilim∈{{{a}}}" if a == b else f"dilim∈{{{a},{b}}}", (c, a - 1, b)) for a in range(4) for b in range(a, min(a + 2, 4))]
    if c == "hs": return [("hafta sonu", (c, 0, 1)), ("hafta içi", (c, -1, 0))]
    q1, q2 = H_[c].quantile([1 / 3, 2 / 3]).values; I = np.inf
    return [(f"{c} alt⅓ (≤{q1:.3g})", (c, -I, q1)), (f"{c} orta⅓ ({q1:.3g}…{q2:.3g})", (c, q1, q2)), (f"{c} üst⅓ (>{q2:.3g})", (c, q2, I)), (f"{c} ≤ {q2:.3g}", (c, -I, q2)), (f"{c} > {q1:.3g}", (c, q1, I))]
def maske(sp): c, a, b = sp; return (H_[c] > a) & (H_[c] <= b)
SEC = {c: [(a, sp, maske(sp)) for a, sp in secenek(c)] for c in SUR + ["dilim", "hs"]}
KMAP = {"şimdiki k": dict(KS), "Aşama1 k": {sn: (EN_K[sn][0] if EN_K[sn] else KS[sn]) for sn in SIN}}
YMAP = {"şimdiki k": {sn: False for sn in SIN}, "Aşama1 k": {sn: (EN_K[sn][1] if EN_K[sn] else False) for sn in SIN}}
def r_k(d, km, ym):
    r = np.full(len(d), np.nan)
    for sn in SIN:
        m = (d.sinif == sn).values
        if m.any(): r[m] = net(d[m], km[sn], yari=ym[sn])
    return r
ADAY = []
for kad in KMAP:
    R = pd.Series(r_k(V, KMAP[kad], YMAP[kad]), index=V.index); S_ = sepet(V, R.values)
    def dene(ad, maske_saat=None, d=None, r=None, spec=None):
        global NT; NT += 1
        x = sepet(d, r.values) if d is not None else S_
        if maske_saat is not None: x = x[x.index.isin(H_.index[maske_saat.reindex(H_.index).fillna(False).values])]
        o = ozet(x); o.update(ad=ad, k=kad, spec=json.dumps(spec)); ADAY.append(o)
    dene("filtre yok", spec=dict(f=[], top=None))
    tek = [(c, a, sp, m) for c in SEC for a, sp, m in SEC[c]]
    for c, a, sp, m in tek: dene(a, m, spec=dict(f=[sp], top=None))
    for (c1, a1, s1, m1), (c2, a2, s2, m2) in itertools.combinations(tek, 2):
        if c1 != c2: dene(f"{a1} & {a2}", m1 & m2, spec=dict(f=[s1, s2], top=None))
    for sk in ["z", "rz", "c_r24"]:
        for N in (1, 3, 5):
            sel = V.assign(_r=R.values).sort_values(sk, ascending=False).groupby("t").head(N); rr = sel._r
            dene(f"saat içi en iyi {N} ({sk})", None, sel, rr, spec=dict(f=[], top=[sk, N]))
            for c, a, sp, m in tek: dene(f"saat içi en iyi {N} ({sk}) & {a}", m, sel, rr, spec=dict(f=[sp], top=[sk, N]))
A = pd.DataFrame(ADAY)
taban_net = T0["net"]
gec = A[(A.ist >= 72) & (A.net > taban_net) & (A.hf >= 4) & (A.i1 >= 68) & (A.i2 >= 68)].copy()
yaz(f"\n## Aşama 2 — {len(A):,} kural denendi (toplam deneme {NT:,}) · taban saat başı net {taban_net:+.3f} · şartları geçen: {len(gec)}")
yaz("Şartlar: saat isabeti ≥ %72 · saat başı net > taban · haftada ≥ 4 saat · iki yarıda da ≥ %68\n")
yaz("### Saat isabetine göre en yüksek 15 (haftada ≥ 4 saat olanlar; şart geçmese de bilgi)")
yaz("| Kural | k | saat | hf | saat isabeti | i1 · i2 | saat başı net | haftalık top |"); yaz("|---|---|---|---|---|---|---|---|")
for _, r in A[A.hf >= 4].sort_values("ist", ascending=False).head(15).iterrows():
    yaz(f"| {r.ad} | {r.k} | {r.n} | {r.hf:.1f} | %{r.ist:.1f} | %{r.i1:.0f} · %{r.i2:.0f} | {r.net:+.3f} | {r.top:+.2f} |")
yaz("\n### Şartları geçenler (haftalık toplam nete göre)")
if len(gec):
    yaz("| Kural | k | saat | hf | saat isabeti | i1 · i2 | saat başı net | haftalık top |"); yaz("|---|---|---|---|---|---|---|---|")
    for _, r in gec.sort_values("top", ascending=False).head(25).iterrows():
        yaz(f"| {r.ad} | {r.k} | {r.n} | {r.hf:.1f} | %{r.ist:.1f} | %{r.i1:.0f} · %{r.i2:.0f} | {r.net:+.3f} | {r.top:+.2f} |")
sec = []
for _, r in gec.sort_values("top", ascending=False).iterrows():
    if r.ad not in [s["ad"] for s in sec]: sec.append(dict(ad=r.ad, k=r.k, spec=json.loads(r.spec)))
    if len(sec) == 3: break
yaz("\n## Doğrulamaya gidecek adaylar (Ek 1: haftalık toplam nete göre ilk 3, aynı filtre tek)")
yaz("\n".join(f"- {s['ad']} · {s['k']}" for s in sec) if sec else "- **Yok** — hiçbir kural keşif şartlarını sağlamadı.")
json.dump(dict(adaylar=sec, KMAP=KMAP, YMAP=YMAP), open("kesif_adaylar.json", "w"), ensure_ascii=False, indent=1)
open("kesif_sonuc.md", "w").write("\n".join(L) + "\n")
