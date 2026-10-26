# turev_analiz.py — PROTOKOL_turev.md: 18 filtre · keşif (iki yarı + plasebo) → ≤ 3 → kontrol (bir kez) → turev_sonuc.md
import glob, numpy as np, pandas as pd
F = pd.concat([pd.read_csv(p) for p in glob.glob("parca/**/turev_p*.csv.gz", recursive=True)], ignore_index=True); F["t"] = pd.to_datetime(F.t, utc=True)
P = pd.read_csv(glob.glob("parca/**/turev_piyasa.csv.gz", recursive=True)[0], index_col=0); P.index = pd.to_datetime(P.index, utc=True)
for c in ("dvol", "dvol24", "fg"):
    i = P.index.searchsorted(F.t.values, side="right") - 1; ok = i >= 0; v = np.full(len(F), np.nan); v[ok] = P[c].values[i[ok]]; F[c] = v
V = pd.read_csv("veri_seti.csv.gz", usecols=["t", "nm", "sinif", "H", "tur", "rz", "fon"]).rename(columns={"fon": "kfon"}); K = pd.read_csv("karal2_veri.csv.gz", usecols=["t", "nm", "sinif", "H", "B_T0", "D_T0"])
for x in (V, K): x["t"] = pd.to_datetime(x.t, utc=True)
M = K.merge(V.drop_duplicates(["t", "nm", "sinif", "H"]), on=["t", "nm", "sinif", "H"]).merge(F.drop_duplicates(["t", "nm", "sinif", "H"]), on=["t", "nm", "sinif", "H"], how="left")
OZ = ["oi24", "oi4", "ls_top", "ls_all", "taker", "fon", "baz", "dvol", "dvol24", "fg"]
P0, YARI, A25, A26 = (pd.Timestamp(x, tz="UTC") for x in ("2022-06-01", "2023-07-01", "2025-01-01", "2026-01-01")); SON = M.t.max() + pd.Timedelta(hours=1)
L = []; yaz = lambda s="": (print(s, flush=True), L.append(s))
A = M[M.sinif.str.startswith("✅")]
def don(d, a, b): return d[(d.t >= a) & (d.t < b)]
def olc(d, c="B_T0"):
    x = d[["t", c]].dropna()
    if not len(x): return dict(n=0, ii=np.nan, inet=np.nan, si=np.nan, hf=0)
    sp = x.groupby("t")[c].mean(); return dict(n=len(x), ii=100 * (x[c] > 0).mean(), inet=100 * x[c].mean(), si=100 * (sp > 0).mean(), hf=len(sp))
KS = don(A, P0, A25); KUT = {}
yaz("# 🧭 Fiyat dışı veri (türev · opsiyon · duygu) ile sinyal seçimi — PROTOKOL_turev.md")
yaz(f"_{len(M):,} sinyal · özellik doluluğu (✅ ana keşif): " + " · ".join(f"{o} %{100 * KS[o].notna().mean():.0f}" for o in OZ) + "_\n")
FIL = []
for o in OZ:
    q30, q70 = np.nanquantile(KS[o], 0.3), np.nanquantile(KS[o], 0.7); KUT[o] = (q30, q70)
    FIL += [(f"{o} düşük (≤ {q30:.3g})", lambda d, o=o, q=q30: d[d[o] <= q]), (f"{o} yüksek (≥ {q70:.3g})", lambda d, o=o, q=q70: d[d[o] >= q])]
rng = np.random.default_rng(20261026)
def plasebo95(d, n):
    x = d.B_T0.dropna().values
    if n == 0 or len(x) == 0: return np.nan
    return np.nanpercentile([100 * (rng.choice(x, size=min(n, len(x)), replace=False) > 0).mean() for _ in range(200)], 95)
DON = {"½-1": (P0, YARI), "½-2": (YARI, A25), "KEŞİF": (P0, A25), "2025+": (A25, SON), "2026": (A26, SON)}
B = {dn: olc(don(A, a, b)) for dn, (a, b) in DON.items()}
yaz("## Taban (✅ ana, tüm sinyaller)"); yaz(" · ".join(f"{dn}: {o['n']} işlem · ist %{o['ii']:.1f} · net {o['inet']:+.3f} · saat %{o['si']:.1f}" for dn, o in B.items()))
yaz("\n## KEŞİF — iki yarıda da: isabet ≥ taban + 4 · net ≥ taban + 0,10 · isabet > plasebo %95 · ≥ 100 işlem")
yaz("| Filtre | ½-1 (n · ist · net · pl95) | ½-2 (n · ist · net · pl95) | KEŞİF ist · net | geçti |"); yaz("|---|---|---|---|---|")
GEC = []
for ad, f in FIL:
    r = {}; ok = True
    for dn in ("½-1", "½-2"):
        a, b = DON[dn]; d = don(A, a, b); s = f(d); o = olc(s); p95 = plasebo95(d, o["n"]); r[dn] = (o, p95)
        ok &= o["n"] >= 100 and o["ii"] >= B[dn]["ii"] + 4 and o["inet"] >= B[dn]["inet"] + 0.10 and o["ii"] > p95
    k = olc(f(don(A, P0, A25)))
    if ok: GEC.append((k["ii"], ad, f))
    yaz(f"| {ad} | " + " | ".join(f"{o['n']} · %{o['ii']:.1f} · {o['inet']:+.3f} · %{p:.1f}" for o, p in r.values()) + f" | %{k['ii']:.1f} · {k['inet']:+.3f} | {'✅' if ok else '❌'} |")
SEC = sorted(GEC, key=lambda x: -x[0])[:3]
yaz(f"\n**Kontrole giden:** {', '.join(a for _, a, _ in SEC) if SEC else 'yok'}\n")
yaz("## KONTROL (bir kez) — 2025+ ve 2026: isabet ≥ %70 · net ≥ taban + 0,10 · saat isabeti ≥ %65 · haftada ≥ 1 saat")
yaz("| Filtre | Dönem | n | işlem isabeti | işlem başı net | saat isabeti | haftada saat | şart |"); yaz("|---|---|---|---|---|---|---|---|")
for _, ad, f in SEC:
    hep = True
    for dn in ("2025+", "2026"):
        a, b = DON[dn]; o = olc(f(don(A, a, b))); hf = o["hf"] / max((min(b, SON) - a).days / 7, 1)
        ok = o["ii"] >= 70 and o["inet"] >= B[dn]["inet"] + 0.10 and o["si"] >= 65 and hf >= 1; hep &= ok
        yaz(f"| {ad} | {dn} | {o['n']} | %{o['ii']:.1f} | {o['inet']:+.3f} | %{o['si']:.1f} | {hf:.1f} | {'✅' if ok else '❌'} |")
    yaz(f"| **{ad} → {'BAŞARILI' if hep else 'başarısız'}** | | | | | | | |")
if len(SEC) >= 2:
    yaz("\n_Bilgi: ikili kesişimler (karar değil)_")
    for i in range(len(SEC)):
        for j in range(i + 1, len(SEC)):
            for dn in ("KEŞİF", "2025+", "2026"):
                a, b = DON[dn]; s = SEC[j][2](SEC[i][2](don(A, a, b))); o = olc(s); yaz(f"- {SEC[i][1]} ∩ {SEC[j][1]} · {dn}: {o['n']} · %{o['ii']:.1f} · {o['inet']:+.3f}")
yaz("\n## Bilgi: aynı filtreler 🔸 yedek / 📋 panelden ve piyasadan giriş (D) — seçilenler için")
for _, ad, f in SEC:
    for sn in ("🔸", "📋"):
        d = M[M.sinif.str.startswith(sn)]
        yaz(f"- {ad} · {sn}: " + " · ".join(f"{dn} {olc(f(don(d, *DON[dn])))['n']} · %{olc(f(don(d, *DON[dn])))['ii']:.1f} · {olc(f(don(d, *DON[dn])))['inet']:+.3f}" for dn in ("KEŞİF", "2025+", "2026")))
    yaz(f"- {ad} · ✅ ana piyasadan (D): " + " · ".join(f"{dn} %{olc(f(don(A, *DON[dn])), 'D_T0')['ii']:.1f} · {olc(f(don(A, *DON[dn])), 'D_T0')['inet']:+.3f}" for dn in ("KEŞİF", "2025+", "2026")))
yaz("\n## Bilgi: tüm filtrelerin 2025+ ve 2026 sonuçları (seçimden bağımsız, karar değil)")
for ad, f in FIL:
    yaz(f"- {ad}: " + " · ".join(f"{dn} {olc(f(don(A, *DON[dn])))['n']} · %{olc(f(don(A, *DON[dn])))['ii']:.1f} · {olc(f(don(A, *DON[dn])))['inet']:+.3f}" for dn in ("2025+", "2026")))
open("turev_sonuc.md", "w").write("\n".join(L) + "\n"); M.to_csv("turev_veri.csv.gz", index=False, compression="gzip")
