# dogrulama.py — PROTOKOL_saat70.md DOĞRULAMA: kesif_adaylar.json'daki ≤ 3 aday, 2025-01-01 → bugün, BİR KEZ.
# Eşikler keşiften gelir (spec). Başarı: saat isabeti ≥ %70 · saat başı net (vadeli) > 0 · işlem başı net ≥ şimdiki kural · haftada ≥ 3 saat.
import json, numpy as np, pandas as pd
exec(open("kesif.py").read().split("L = []; yaz")[0].replace('V = V[V.t < pd.Timestamp("2025-01-01", tz="UTC")].copy()', "").replace('assert V.t.max() < pd.Timestamp("2025-01-01", tz="UTC")', ""))
A0 = pd.Timestamp("2025-01-01", tz="UTC"); V = V[V.t >= A0].copy(); HAFTA = (V.t.max() - A0).days / 7
J = json.load(open("kesif_adaylar.json")); KMAP, YMAP = J["KMAP"], J["YMAP"]
H_ = V.groupby("t").agg(n=("nm", "size"), b_r4=("b_r4", "first"), b_r24=("b_r24", "first"), zB=("zB", "first"), fon=("fon", "first"), gen24=("gen24", "first"), b_vr=("b_vr", "first"), hod=("hod", "first"), dow=("dow", "first"))
H_["dilim"] = H_.hod // 6; H_["hs"] = (H_.dow >= 5).astype(int); H_["dilim_g"] = (H_.dilim + 1) % 4
def r_k(d, km, ym, gir="D", uc="vadeli"):
    r = np.full(len(d), np.nan)
    for sn in SIN:
        m = (d.sinif == sn).values
        if m.any(): r[m] = net(d[m], km[sn], gir, uc, ym[sn])
    return r
def uygula(sp, km, ym, gir="D", uc="vadeli", donem=None):
    d = V if donem is None else V[V.t >= donem]
    r = pd.Series(r_k(d, km, ym, gir, uc), index=d.index)
    if sp["top"]: sk, N = sp["top"]; d = d.assign(_r=r.values, _so=d.sinif.map({sn: i for i, sn in enumerate(SIN)})).sort_values([sk, "_so", "H", "nm"], ascending=[False, True, True, True], kind="mergesort").groupby("t").head(N); r = d._r   # Ek 2.1
    x = sepet(d, r.values)
    for c, a, b in sp["f"]: m = (H_[c] > a) & (H_[c] <= b); x = x[x.index.isin(H_.index[m.values])]
    hf = len(x) / ((V.t.max() - (donem or A0)).days / 7)
    rr = r[r.index.isin(d.index[d.t.isin(x.index)])].dropna() if len(x) else pd.Series(dtype=float)
    return dict(n=len(x), ist=100 * (x > 0).mean() if len(x) else np.nan, net=100 * x.mean() if len(x) else np.nan, hf=hf, iist=100 * (rr > 0).mean() if len(rr) else np.nan, inet=100 * rr.mean() if len(rr) else np.nan)
L = []; yaz = lambda s="": (print(s), L.append(s))
yaz(f"# ✅ DOĞRULAMA (2025-01 → {V.t.max():%d.%m.%Y}) — tek sefer · PROTOKOL_saat70.md")
yaz("_Eşikler ve k'lar keşiften. Saat isabeti = saat sepeti neti > 0. Giriş t+7 dk piyasa (D) ana; B = kapanışa limit._\n")
TAB = dict(f=[], top=None); KS0 = {sn: KS[sn] for sn in SIN}; Y0 = {sn: False for sn in SIN}
yaz("| Kural | k | Giriş · ücret | Dönem | saat | hf | saat isabeti | saat başı net | işlem isabeti | işlem başı net | BAŞARI |"); yaz("|---|---|---|---|---|---|---|---|---|---|---|")
for ad, sp, km, ym in [("ŞİMDİKİ KURAL (taban)", TAB, KS0, Y0)] + [(a["ad"], a["spec"], KMAP[a["k"]], YMAP[a["k"]]) for a in J["adaylar"]]:
    t0 = uygula(TAB, KS0, Y0)
    for gir, uc in (("D", "vadeli"), ("B", "vadeli"), ("D", "spot")):
        for dn, dd in (("2025+", None), ("2026", pd.Timestamp("2026-01-01", tz="UTC"))):
            o = uygula(sp, km, ym, gir, uc, dd)
            ok = (o["ist"] >= 70 and o["net"] > 0 and o["inet"] >= t0["inet"] and o["hf"] >= 3) if (gir, uc, dn) == ("D", "vadeli", "2025+") and ad != "ŞİMDİKİ KURAL (taban)" else None
            yaz(f"| {ad} | {'—' if km is KS0 else [k for k in KMAP if KMAP[k] == km][0]} | {gir} · {uc} | {dn} | {o['n']} | {o['hf']:.1f} | %{o['ist']:.1f} | {o['net']:+.3f} | %{o['iist']:.1f} | {o['inet']:+.3f} | {'' if ok is None else ('✅' if ok else '❌')} |")
if not J["adaylar"]: yaz("\n_Keşiften aday çıkmadı; yalnız taban ölçüldü._")
open("dogrulama_sonuc.md", "w").write("\n".join(L) + "\n")
