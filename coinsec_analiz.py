# coinsec_analiz.py — PROTOKOL_coinsec.md: kurallar · plasebo · keşif seçimi → tek seferlik doğrulama → coinsec_sonuc.md
import glob, json, time, numpy as np, pandas as pd
T0 = time.time(); L_ = []; yaz = lambda s="": (print(s, flush=True), L_.append(s))
D = pd.concat([pd.read_csv(p) for p in glob.glob("parca/**/coinsec_p*.csv.gz", recursive=True)], ignore_index=True)
D["t"] = pd.to_datetime(D.t, utc=True); D["fB"] = D.fB.astype(str).str.lower().eq("true")
BT = D[D.grp == "BTC"].copy(); D = D[D.grp != "BTC"].copy()
P0, YARI, A25, A26 = (pd.Timestamp(x, tz="UTC") for x in ("2022-06-01", "2023-07-01", "2025-01-01", "2026-01-01")); SON = D.t.max() + pd.Timedelta(hours=1)
KUR = {"R0": None, "R1": ("beta", False), "R2": ("s", False), "R3": ("rho", False), "R4": ("rel", True), "R5": ("rel", False), "R6": ("rz", True)}
AD = {"R0": "tüm coin'ler", "R1": "en yüksek beta", "R2": "en yüksek σ", "R3": "en yüksek korelasyon", "R4": "en geride kalan (rel düşük)", "R5": "en önde giden (rel yüksek)", "R6": "son 24 s en çok düşen"}
def lfil(d): return d[d.liq >= d.groupby("t").liq.transform("median")]
def sec(d, k, L):
    if L: d = lfil(d)
    if k == "R0": return d
    c, asc = KUR[k]; d = d.dropna(subset=[c])
    return d.sort_values(["t", c, "coin"], ascending=[True, asc, True], kind="mergesort").groupby("t").head(5)
def olc(sel, a, b, kol="nB"):
    b = min(b, SON); x = sel[(sel.t >= a) & (sel.t < b)]
    x = x[x.fB] if kol == "nB" else x
    w = max((b - a).days / 7, 1e-9)
    if not len(x): return dict(n=0, ist=np.nan, net=np.nan, iist=np.nan, inet=np.nan, hf=0.0)
    sp = x.groupby("t")[kol].mean()
    return dict(n=len(sp), ist=100 * (sp > 0).mean(), net=100 * sp.mean(), iist=100 * (x[kol] > 0).mean(), inet=100 * x[kol].mean(), hf=len(sp) / w)
UA, UB = D[D.grp == "A"], D[D.grp == "B"]
DON = {"K½-1": (UA, P0, YARI), "K½-2": (UA, YARI, A25), "KEŞİF": (UA, P0, A25), "A 2025+": (UA, A25, SON), "B 2022–24": (UB, P0, A25), "B 2025+": (UB, A25, SON), "A 2026": (UA, A26, SON), "B 2026": (UB, A26, SON)}
rng = np.random.default_rng(20261025); PL = {}
for L in (False, True):
    for dn, (U, a, b) in DON.items():
        u = lfil(U) if L else U; u = u[(u.t >= a) & (u.t < min(b, SON))]; res = []
        for _ in range(200):
            s = u.assign(_r=rng.random(len(u))).sort_values(["t", "_r"]).groupby("t").head(5); res.append(olc(s, a, b))
        PL[(L, dn)] = dict(ist=np.nanmean([r["ist"] for r in res]), net=np.nanmean([r["net"] for r in res]), ist95=np.nanpercentile([r["ist"] for r in res], 95), net95=np.nanpercentile([r["net"] for r in res], 95))
yaz(f"# 🪙 BTC güçlü ↑ saatinde hangi coin? — PROTOKOL_coinsec.md · {pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M}")
yaz(f"_{D.t.nunique():,} olay saati · A evreni {UA.coin.nunique()} coin · B (dokunulmamış) {UB.coin.nunique()} coin · {len(D):,} coin-olay satırı · veri sonu {SON - pd.Timedelta(hours=1):%d.%m.%Y}_")
yaz("_Giriş B: kapanışa limit 60 dk (5 dk mum) · 🎯 +0,75σ · 4 saat · vadeli ücret + fonlama · saat = olay sepeti (seçilen 5 coin'den dolanlar, eşit pay) · 14 kural denendi_\n")
yaz("## Taban ve plasebo (saat isabeti · saat başı net %)")
yaz("| Küme | olay | yalnız BTC | tüm coin'ler (R0) | plasebo rastgele 5 (ort · %95) | plasebo + L |"); yaz("|---|---|---|---|---|---|")
for dn, (U, a, b) in DON.items():
    o_b, o_0 = olc(BT, a, b), olc(sec(U, "R0", False), a, b); p, pl = PL[(False, dn)], PL[(True, dn)]
    yaz(f"| {dn} | {o_0['n']} | %{o_b['ist']:.1f} · {o_b['net']:+.3f} | %{o_0['ist']:.1f} · {o_0['net']:+.3f} | %{p['ist']:.1f} · {p['net']:+.3f} (%{p['ist95']:.1f} · {p['net95']:+.3f}) | %{pl['ist']:.1f} · {pl['net']:+.3f} |")
yaz("\n## KEŞİF (A evreni, 2022-06 → 2024) — iki yarıda da: saat isabeti ≥ plasebo + 3 · saat net ≥ plasebo + 0,10 · net > 0")
yaz("| Kural | L | ½-1: saat · ist · net · işlem ist · işlem net | ½-2: saat · ist · net · işlem ist · işlem net | KEŞİF: ist · net · hf | geçti |"); yaz("|---|---|---|---|---|---|")
GEC = []
for k in KUR:
    for L in (False, True):
        s = sec(UA, k, L); oo = {dn: olc(s, a, b) for dn, (U, a, b) in DON.items() if U is UA and dn.startswith("K")}
        ok = k != "R0" and all(oo[dn]["ist"] >= PL[(L, dn)]["ist"] + 3 and oo[dn]["net"] >= PL[(L, dn)]["net"] + 0.10 and oo[dn]["net"] > 0 for dn in ("K½-1", "K½-2"))
        if ok: GEC.append((oo["KEŞİF"]["net"], k, L))
        f = lambda o: f"{o['n']} · %{o['ist']:.1f} · {o['net']:+.3f} · %{o['iist']:.1f} · {o['inet']:+.3f}"
        yaz(f"| {k} {AD[k]} | {'✓' if L else ''} | {f(oo['K½-1'])} | {f(oo['K½-2'])} | %{oo['KEŞİF']['ist']:.1f} · {oo['KEŞİF']['net']:+.3f} · {oo['KEŞİF']['hf']:.1f} | {'—' if k == 'R0' else ('✅' if ok else '❌')} |")
SEC = [(k, L) for _, k, L in sorted(GEC, reverse=True)[:2]]
_ad = ", ".join(k + (" + L" if L else "") for k, L in SEC) if SEC else "yok — keşif şartını geçen kural yok (doğrulama yalnız bilgi için)"
yaz(f"\n**Doğrulamaya giden:** {_ad}\n")
json.dump([[k, L] for k, L in SEC], open("coinsec_secim.json", "w"))
yaz("## DOĞRULAMA (bir kez) — üç kümede de: saat isabeti ≥ %65 · saat net ≥ +0,15 · plasebodan ≥ 3 puan ve ≥ +0,10 · haftada ≥ 3 olay")
yaz("| Kural | Küme | olay | saat isabeti | saat net | işlem isabeti | işlem net | hf | plasebo ist · net | şart |"); yaz("|---|---|---|---|---|---|---|---|---|---|")
for k, L in (SEC or [(k, False) for k in KUR if k != "R0"]):
    s_a, s_b = sec(UA, k, L), sec(UB, k, L); hep = True
    for dn in ("A 2025+", "B 2022–24", "B 2025+", "A 2026", "B 2026"):
        U, a, b = DON[dn]; o = olc(s_a if U is UA else s_b, a, b); p = PL[(L, dn)]
        ok = o["ist"] >= 65 and o["net"] >= 0.15 and o["ist"] >= p["ist"] + 3 and o["net"] >= p["net"] + 0.10 and o["hf"] >= 3
        if dn in ("A 2025+", "B 2022–24", "B 2025+"): hep &= ok
        yaz(f"| {k}{' + L' if L else ''} | {dn} | {o['n']} | %{o['ist']:.1f} | {o['net']:+.3f} | %{o['iist']:.1f} | {o['inet']:+.3f} | {o['hf']:.1f} | %{p['ist']:.1f} · {p['net']:+.3f} | {('✅' if ok else '❌') if not dn.endswith('2026') else 'bilgi'} |")
    yaz(f"| **{k}{' + L' if L else ''} sonuç** | | | | | | | | | **{'BAŞARILI' if hep and SEC else ('başarısız' if SEC else 'bilgi (keşif yok)')}** |")
yaz("\n## Bilgi: aynı olay saatlerinde canlıdaki 🤝 (coin modeliyle) — veri_seti + karal2_veri, giriş B")
try:
    V = pd.read_csv("veri_seti.csv.gz"); K2 = pd.read_csv("karal2_veri.csv.gz")
    for x in (V, K2): x["t"] = pd.to_datetime(x.t, utc=True)
    M = K2.merge(V[["t", "nm", "sinif", "H", "tur"]].drop_duplicates(["t", "nm", "sinif", "H"]), on=["t", "nm", "sinif", "H"], how="left")
    M = M[M.sinif.str.startswith("✅") & M.tur.isin(["🤝", "🌐🤝"]) & M.t.isin(set(D.t))].rename(columns={"B_T0": "nB"}); M["fB"] = M.nB.notna()
    for dn in ("KEŞİF", "A 2025+", "A 2026"):
        _, a, b = DON[dn]; o = olc(M, a, b); yaz(f"- {dn}: {o['n']} saat · saat isabeti %{o['ist']:.1f} · saat net {o['net']:+.3f} · işlem net {o['inet']:+.3f}")
except Exception as e: yaz(f"_karşılaştırma yapılamadı: {e!r}_")
yaz("\n## Bilgi: özelliklerin 5'li dilimlerine göre işlem neti (A keşifte belirlenen sınırlar; dolan işlemler)")
K_ = UA[(UA.t >= P0) & (UA.t < A25) & UA.fB]
yaz("| Özellik | Küme | dilim 1 (düşük) | 2 | 3 | 4 | 5 (yüksek) |"); yaz("|---|---|---|---|---|---|---|")
for c in ("beta", "s", "rho", "rel", "rz", "liq"):
    q = np.nanquantile(K_[c], [0.2, 0.4, 0.6, 0.8])
    for dn in ("KEŞİF", "A 2025+", "B 2022–24", "B 2025+"):
        U, a, b = DON[dn]; x = U[(U.t >= a) & (U.t < min(b, SON)) & U.fB]; bi = np.digitize(x[c], q)
        yaz(f"| {c} | {dn} | " + " | ".join(f"{100 * x.nB[bi == j].mean():+.3f} (%{100 * (x.nB[bi == j] > 0).mean():.0f})" for j in range(5)) + " |")
yaz(f"\n_Süre {time.time() - T0:.0f} sn · plasebo 200 tekrar · tohum 20261025_")
open("coinsec_sonuc.md", "w").write("\n".join(L_) + "\n")
