# ayrim.py — PROTOKOL_ayrim.md: sinyal ayrımı (tür × koşul × coin) → ayrim_sonuc.md
import numpy as np, pandas as pd
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
K_ = ["t", "nm", "sinif", "H"]
V = pd.read_csv("veri_seti.csv.gz", usecols=K_ + ["tur", "z", "rz", "fon", "zB", "b_r24", "b_vr", "c_r4", "c_r24", "hod", "dow"]).drop_duplicates(K_)
KR = pd.read_csv("karal2_veri.csv.gz", usecols=K_ + ["D_T0", "B_T0"]).drop_duplicates(K_)
X = V.merge(KR, on=K_); X["t"] = pd.to_datetime(X.t, utc=True); X = X[X.D_T0.notna()].reset_index(drop=True)
X["don"] = np.select([X.t < pd.Timestamp("2025-01-01", tz="UTC"), X.t < pd.Timestamp("2026-01-01", tz="UTC")], ["A", "B"], "C"); X = X[X.t >= pd.Timestamp("2022-06-01", tz="UTC")]
X["sn"] = X.sinif.str.split(" \\(").str[0]; X["tur"] = X.tur.fillna("?").replace("G", "🌐🤝 (G)"); X["grup"] = X.sn + " " + X.tur
X["ok"] = X.D_T0 > 0; DON = ["A", "B", "C"]; DAD = {"A": "2022-06→24", "B": "2025", "C": "2026"}
KOS = {"K1 📉🔥 dip (rz ≤ −2)": X.rz <= -2, "K2 🚀 momentum (rz ≥ 2)": X.rz >= 2, "K3 🔥 fonlama (fon ≥ 2)": X.fon >= 2, "K4 coin primi z ≥ 1": X.z >= 1, "K5 coin primi z < 0": X.z < 0,
       "K6 ABD BTC satıyor (zB < 0)": X.zB < 0, "K7 BTC 24 s ≤ −%2": X.b_r24 <= -0.02, "K8 BTC 24 s ≥ +%2": X.b_r24 >= 0.02, "K9 BTC oynaklık yüksek (b_vr ≥ 1,25)": X.b_vr >= 1.25,
       "K10 coin 4 s düşüşte": X.c_r4 < 0, "K11 coin 24 s ≤ −%5": X.c_r24 <= -0.05, "K12 ABD seansı 12–16 UTC": X.hod.between(12, 16), "K13 Asya gecesi 0–5 UTC": X.hod.between(0, 5),
       "K14 hafta sonu": X.dow >= 5, "K15 süre 4 s": X.H == 4, "K16 süre ≥ 24 s": X.H >= 24}
KA = list(KOS); KM = np.column_stack([KOS[k].fillna(False).values for k in KA])
def st(y): return (len(y), y.ok.mean() if len(y) else np.nan, y.D_T0.mean() if len(y) else np.nan)
fs = lambda s: f"{s[0]} · %{100 * s[1]:.0f} · {100 * s[2]:+.2f}" if s[0] else "—"
yaz("# 🔍 Sinyal ayrımı — tür × koşul × coin (PROTOKOL_ayrim.md)")
yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {len(X)} sinyal · {X.nm.nunique()} coin · ölçü D_T0 (piyasadan giriş, sınıf 🎯'si, vadeli ücret + fonlama) · hücre: sinyal · isabet · işlem başı net %_\n")
yaz("## Sınıf tabanı"); yaz("| sınıf | " + " | ".join(DAD[d] for d in DON) + " |"); yaz("|---|---|---|---|")
for sn, g in X.groupby("sn"): yaz(f"| {sn} | " + " | ".join(fs(st(g[g.don == d])) for d in DON) + " |")
GR = [g for g, x in X.groupby("grup") if all((x.don == d).sum() >= 30 for d in DON)]
yaz(f"\n_Üç dönemde de ≥ 30 sinyali olan grup: {len(GR)} — " + ", ".join(GR) + "_")
# ---------- Bölüm 1 ----------
def hucre_tara(X, KM):
    R = []
    for g in GR:
        ix = np.where(X.grup.values == g)[0]
        for j, k in enumerate(KA):
            on = KM[ix, j]; rec = dict(grup=g, kos=k); kotu = iyi = mut = True; bsgn = []
            for d in DON:
                m = X.don.values[ix] == d; a, b = ix[m & on], ix[m & ~on]
                if len(a) < 30 or len(b) < 30: kotu = iyi = mut = False; rec[d] = None; continue
                ha, hb = X.ok.values[a].mean(), X.ok.values[b].mean(); na, nb = X.D_T0.values[a].mean(), X.D_T0.values[b].mean()
                Ba, Bb = X.B_T0.values[a], X.B_T0.values[b]; Ba, Bb = Ba[~np.isnan(Ba)], Bb[~np.isnan(Bb)]
                bd = (np.mean(Ba > 0) - np.mean(Bb > 0)) if len(Ba) and len(Bb) else np.nan; bsgn.append(bd)
                rec[d] = (len(a), ha, na, 100 * (ha - hb), 100 * (na - nb), bd)
                kotu &= (100 * (ha - hb) <= -5) and (100 * (na - nb) <= -0.10); iyi &= (100 * (ha - hb) >= 5) and (100 * (na - nb) >= 0.10); mut &= (ha < 0.55) and (na < 0)
            rec.update(kotu=kotu, iyi=iyi, mut=mut, b_kotu=kotu and all(np.isfinite(b) and b < 0 for b in bsgn), b_iyi=iyi and all(np.isfinite(b) and b > 0 for b in bsgn)); R.append(rec)
    return pd.DataFrame(R)
H1 = hucre_tara(X, KM)
rng = np.random.default_rng(111); PL = []
for it in range(50):
    KP = KM.copy()
    for (g, d), ix in X.groupby(["grup", "don"]).indices.items(): KP[ix] = KM[rng.permutation(ix)]
    h = hucre_tara(X, KP); PL.append((int(h.kotu.sum()), int(h.iyi.sum()), int(h.mut.sum())))
PL = np.array(PL)
def hc(r, d):
    x = r[d]; return "—" if x is None else f"{x[0]} · %{100 * x[1]:.0f} · {100 * x[2]:+.2f} ({x[3]:+.0f} / {x[4]:+.2f})"
yaz("\n## Bölüm 1 — tür × koşul hücreleri")
yaz(f"**Kötü hücre (ele adayı, 3 dönemde ≤ −5 puan ve ≤ −%0,10): {int(H1.kotu.sum())}** (B_T0 ile de aynı yönde: {int(H1.b_kotu.sum())}) · plasebo ort. {PL[:, 0].mean():.1f} (en çok {PL[:, 0].max()})")
yaz(f"**İyi hücre (öne çıkar adayı): {int(H1.iyi.sum())}** (B_T0 ile de: {int(H1.b_iyi.sum())}) · plasebo ort. {PL[:, 1].mean():.1f} (en çok {PL[:, 1].max()})")
yaz(f"**Mutlak kötü (3 dönemde isabet < %55 ve net < 0): {int(H1.mut.sum())}** · plasebo ort. {PL[:, 2].mean():.1f} (en çok {PL[:, 2].max()})\n")
yaz("_hücre: sinyal · isabet · net (isabet farkı puan / net farkı %; fark = koşul var − yok, aynı grupta)_\n")
for bas, m in (("❌ Kötü hücreler", H1.kotu | H1.mut), ("✅ İyi hücreler", H1.iyi)):
    yaz(f"### {bas}"); yaz("| grup | koşul | " + " | ".join(DAD[d] for d in DON) + " | B_T0 aynı yön | tür |"); yaz("|---|---|---|---|---|---|---|")
    for r in H1[m].itertuples(): yaz(f"| {r.grup} | {r.kos} | " + " | ".join(hc(r._asdict(), d) for d in DON) + f" | {'✔' if (r.b_kotu or r.b_iyi) else '✘'} | {'mutlak kötü' if r.mut else ('kötü' if r.kotu else 'iyi')} |")
    if not m.any(): yaz("| — | | | | | | |")
# ---------- Bölüm 2 ----------
yaz("\n## Bölüm 2 — grubun kendisi (3 dönemde isabet < %55 ve net < 0 → ele adayı)")
yaz("| grup | " + " | ".join(DAD[d] for d in DON) + " | |"); yaz("|---|---|---|---|---|"); GELE = []
for g, x in X.groupby("grup"):
    S = [st(x[x.don == d]) for d in DON]; ele = all(s[0] >= 30 and s[1] < 0.55 and s[2] < 0 for s in S)
    if sum(s[0] for s in S) >= 60: yaz(f"| {g} | " + " | ".join(fs(s) for s in S) + f" | {'❌ ele adayı' if ele else ''} |")
    if ele: GELE.append(g)
# ---------- Bölüm 3 ----------
def coin_tara(X, nmv):
    kotu, iyi = [], []
    for g in GR:
        ix = np.where(X.grup.values == g)[0]; dn = X.don.values[ix]; nm = nmv[ix]; ok = X.ok.values[ix]; net = X.D_T0.values[ix]
        A, T = dn == "A", dn != "A"; hA, nA, hT, nT = ok[A].mean(), net[A].mean(), ok[T].mean(), net[T].mean()
        for c in np.unique(nm):
            a, t = A & (nm == c), T & (nm == c)
            if a.sum() < 20 or t.sum() < 20: continue
            ra, rt = ok[a].mean(), ok[t].mean(); qa, qt = net[a].mean(), net[t].mean()
            ta, tt = (ok[A & (nm != c)].mean(), ok[T & (nm != c)].mean())
            if ra <= hA - 0.10 and qa < 0 and 100 * (rt - tt) <= -5 and qt < 0: kotu.append((g, c, a.sum(), ra, qa, t.sum(), rt, qt))
            if ra >= hA + 0.10 and qa > 0 and 100 * (rt - tt) >= 5 and qt > 0: iyi.append((g, c, a.sum(), ra, qa, t.sum(), rt, qt))
    return kotu, iyi
CK, CI = coin_tara(X, X.nm.values); PC = []
for it in range(50):
    nmv = X.nm.values.copy()
    for (g, d), ix in X.groupby(["grup", "don"]).indices.items(): nmv[ix] = nmv[rng.permutation(ix)]
    k_, i_ = coin_tara(X, nmv); PC.append((len(k_), len(i_)))
PC = np.array(PC)
yaz("\n## Bölüm 3 — coin düzeyi (seçim 2022-06→24, test 2025+2026; her birinde ≥ 20)")
yaz(f"**Kötü coin × grup: {len(CK)}** · plasebo ort. {PC[:, 0].mean():.1f} (en çok {PC[:, 0].max()}) · **iyi coin × grup: {len(CI)}** · plasebo ort. {PC[:, 1].mean():.1f} (en çok {PC[:, 1].max()})")
for bas, L in (("❌ kötü", CK), ("✅ iyi", CI)):
    if L:
        yaz(f"\n| {bas} | coin | seçim (sinyal · isabet · net) | test 2025+26 |"); yaz("|---|---|---|---|")
        for g, c, na_, ra, qa, nt_, rt, qt in L: yaz(f"| {g} | {c} | {na_} · %{100 * ra:.0f} · {100 * qa:+.2f} | {nt_} · %{100 * rt:.0f} · {100 * qt:+.2f} |")
# ---------- Bölüm 4 ----------
ELE = np.zeros(len(X), bool)
for r in H1[H1.kotu | H1.mut].itertuples(): ELE |= (X.grup.values == r.grup) & KM[:, KA.index(r.kos)]
for g in GELE: ELE |= X.grup.values == g
if len(CK) and len(CK) > PC[:, 0].mean() + 2 * PC[:, 0].std():
    for g, c, *_ in CK: ELE |= (X.grup.values == g) & (X.nm.values == c)
yaz(f"\n## Bölüm 4 — eleme etkisi (Bölüm 1–3'te geçenler çıkarılınca; elenen {int(ELE.sum())} sinyal)")
yaz("| sınıf | " + " | ".join(f"{DAD[d]} önce → sonra" for d in DON) + " |"); yaz("|---|---|---|---|")
for sn in sorted(X.sn.unique()):
    m = X.sn.values == sn; yaz(f"| {sn} | " + " | ".join(f"{fs(st(X[m & (X.don.values == d)]))} → {fs(st(X[m & (X.don.values == d) & ~ELE]))}" for d in DON) + " |")
# ---------- bilgi: SHIB ----------
yaz("\n## Bilgi — kullanıcının örneği: SHIB (coin × grup × 📉🔥/🔥; küçük örnek, karar için değil)")
S = X[X.nm == "SHIB"]; yaz("| grup | koşul | " + " | ".join(DAD[d] for d in DON) + " | toplam |"); yaz("|---|---|---|---|---|---|")
for g, x in S.groupby("grup"):
    for ad, m in (("hepsi", np.ones(len(x), bool)), ("📉🔥 dip", (x.rz <= -2).values), ("🔥 fonlama", (x.fon >= 2).values), ("dip ya da 🔥", ((x.rz <= -2) | (x.fon >= 2)).values)):
        y = x[m]
        if len(y): yaz(f"| {g} | {ad} | " + " | ".join(fs(st(y[y.don == d])) for d in DON) + f" | {fs(st(y))} |")
open("ayrim_sonuc.md", "w").write("\n".join(out) + "\n")
