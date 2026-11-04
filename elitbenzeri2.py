# elitbenzeri2.py — PROTOKOL_elitbenzeri.md Ek 1: 10 aday + 🌪️+ birleşimi için T1–T5, T8 → elitbenzeri2_sonuc.md (T6/T7 Actions'ta)
import hashlib, json, numpy as np, pandas as pd
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
K_ = ["t", "nm", "sinif", "H"]
V = pd.read_csv("veri_seti.csv.gz", usecols=K_ + ["tur", "z", "rz", "fon", "b_vr", "c_r4", "c_r24", "s"]).drop_duplicates(K_)
KR = pd.read_csv("karal2_veri.csv.gz", usecols=K_ + ["D_T0", "B_T0"]).drop_duplicates(K_); G = pd.read_csv("garch_rho.csv.gz", usecols=K_ + ["rho"])
X = V.merge(KR, on=K_).merge(G, on=K_, how="left"); X["t"] = pd.to_datetime(X.t, utc=True); X = X[X.D_T0.notna() & (X.t >= pd.Timestamp("2022-06-01", tz="UTC"))]
X["sn"] = X.sinif.str.split(" \\(").str[0]; X = X[(X.sn == "✅ ana") & ~X.tur.isin(["🤝", "💵"])].reset_index(drop=True)
X["don"] = np.where(X.t.dt.year <= 2024, "A", np.where(X.t.dt.year == 2025, "B", "C")); X["ay"] = X.t.dt.strftime("%Y-%m")
X["yari"] = X.nm.map(lambda s: int(hashlib.md5(s.encode()).hexdigest(), 16) % 2); X["ok"] = X.D_T0 > 0
AD = {"A": "2022-06→24", "B": "2025", "C": "2026"}
def s_ust(q): return X.groupby("don").s.transform(lambda v: v >= v.quantile(q)).values
KOS = {  # ad: (fonksiyon(eşik), varsayılan, komşular)
    "C1 dip": (lambda e: (X.rz <= e).values, -2.0, [-1.75, -2.25]), "C3 🔥fon": (lambda e: (X.fon >= e).values, 2.0, [1.75, 2.25]),
    "C5 prim z≥2": (lambda e: (X.z >= e).values, 2.0, [1.75, 2.25]), "C6 prim z≥1": (lambda e: (X.z >= e).values, 1.0, [0.75, 1.25]),
    "C12 BTC oynak": (lambda e: (X.b_vr >= e).values, 1.25, [1.15, 1.35]), "C14 coin4s≤−1%": (lambda e: (X.c_r4 <= e).values, -0.01, [-0.0075, -0.0125]),
    "C15 coin24≤−5%": (lambda e: (X.c_r24 <= e).values, -0.05, [-0.04, -0.06]), "C20 GARCH↑": (lambda e: (X.rho >= e).values, 1.2, [1.1, 1.3]),
    "C22 coin oynak": (lambda q: s_ust(q), 2 / 3, [0.60, 1 - 0.8 / 3]), "C23 süre≥24s": (lambda e: (X.H >= e).values, 24, [])}
ADAY = {"K1": ("C1 dip", "C12 BTC oynak"), "K2": ("C3 🔥fon", "C14 coin4s≤−1%"), "K3": ("C3 🔥fon", "C15 coin24≤−5%"), "K4": ("C5 prim z≥2", "C12 BTC oynak"),
        "K5": ("C6 prim z≥1", "C12 BTC oynak"), "K6": ("C12 BTC oynak", "C14 coin4s≤−1%"), "K7": ("C12 BTC oynak", "C15 coin24≤−5%"), "K8": ("C12 BTC oynak", "C20 GARCH↑"),
        "K9": ("C12 BTC oynak", "C22 coin oynak"), "K10": ("C12 BTC oynak", "C23 süre≥24s")}
var = lambda k: KOS[k][0](KOS[k][1])
ELIT = var("C1 dip") | var("C3 🔥fon") | (X.tur == "🔀").values; OYN0 = (X.tur == "🌐🧪").values & var("C12 BTC oynak")
f = lambda y: f"{len(y)} · %{100 * y.ok.mean():.0f} · {100 * y.D_T0.mean():+.2f}" if len(y) else "—"
per = lambda y: all(len(y[y.don == d]) >= 20 and y[y.don == d].ok.mean() >= 0.70 and y[y.don == d].D_T0.mean() > 0 for d in "ABC")
def testler(m, t5):
    """m: aday maskesi · t5: [(etiket, maske)] eşik komşuları → {T: bool}, satırlar"""
    Y, R = X[m], X[~m]; T, L = {}, ["taban: " + " · ".join(f"{AD[d]} {f(Y[Y.don == d])}" for d in "ABC") + " · geri kalan ✅ ana: " + " · ".join(f"{AD[d]} {f(R[R.don == d])}" for d in "ABC")]
    s = []
    for h in (0, 1):
        y = Y[Y.yari == h]; ok_ = bool(len(y) and y.ok.mean() >= 0.70 and y.D_T0.mean() > 0 and all(len(y[y.don == d]) and y[y.don == d].ok.mean() >= 0.65 for d in "ABC"))
        s.append(ok_); L.append(f"- T1 yarı {h}: tümü {f(y)} · " + " · ".join(f"{AD[d]} {f(y[y.don == d])}" for d in "ABC") + f" → {'✔' if ok_ else '✘'}")
    T["T1"] = all(s)
    b = {d: Y[Y.don == d].B_T0.dropna() for d in "ABC"}; T["T2"] = all(len(b[d]) >= 20 and (b[d] > 0).mean() >= 0.70 for d in "ABC")
    L.append("- T2 limit giriş (B_T0): " + " · ".join(f"{AD[d]} {len(b[d])} · %{100 * (b[d] > 0).mean():.0f} · {100 * b[d].mean():+.2f}" for d in "ABC") + f" → {'✔' if T['T2'] else '✘'}")
    ay = Y.groupby("ay").ok.agg(["size", "mean"]); ra = R.groupby("ay").ok.mean(); ay = ay[ay["size"] >= 5]; ay["r"] = ra.reindex(ay.index); oran = (ay["mean"] >= ay["r"]).mean() if len(ay) else 0
    T["T3"] = bool(len(ay) and oran >= 0.60); L.append(f"- T3 aylık: ≥ 5 sinyalli {len(ay)} ay · geri kalandan iyi ay %{100 * oran:.0f} · en kötü ay %{100 * ay['mean'].min():.0f}" + (f" ({ay['mean'].idxmin()})" if len(ay) else "") + f" → {'✔' if T['T3'] else '✘'}")
    top = Y.nm.value_counts().head(5).index.tolist(); y = Y[~Y.nm.isin(top)]
    T["T4"] = bool(len(y) and y.ok.mean() >= 0.70 and y.D_T0.mean() > 0 and all(len(y[y.don == d]) and y[y.don == d].ok.mean() >= 0.65 for d in "ABC"))
    L.append(f"- T4 en çok 5 coin ({', '.join(top)}) çıkınca: tümü {f(y)} · " + " · ".join(f"{AD[d]} {f(y[y.don == d])}" for d in "ABC") + f" → {'✔' if T['T4'] else '✘'}")
    s = []
    for et, mm in t5:
        y = X[mm]; ok_ = per(y); s.append(ok_); L.append(f"- T5 {et}: " + " · ".join(f"{AD[d]} {f(y[y.don == d])}" for d in "ABC") + f" → {'✔' if ok_ else '✘'}")
    T["T5"] = all(s)
    y = X[m & ~ELIT & ~OYN0]; T["T8"] = per(y); L.append(f"- T8 YENİ KISIM (ELİT/🌪️ olmayan): " + " · ".join(f"{AD[d]} {f(y[y.don == d])}" for d in "ABC") + f" · 2025+ haftada {len(y[y.don != 'A']) / ((X.t.max() - pd.Timestamp('2025-01-01', tz='UTC')).days / 7):.1f} · farklı gün/hafta {y[y.don != 'A'].t.dt.floor('D').nunique() / ((X.t.max() - pd.Timestamp('2025-01-01', tz='UTC')).days / 7):.1f} → {'✔' if T['T8'] else '✘'}")
    return T, L
yaz("# 🌪️+ ELİT-benzeri türler — sağlamlık testleri (PROTOKOL_elitbenzeri.md Ek 1)"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · ✅ ana (🤝/💵 hariç) {len(X)} sinyal · D_T0 · hücre: işlem · isabet · net %_\n")
GEC = {}
for k, (a, b) in ADAY.items():
    m = var(a) & var(b); t5 = []
    for c_ in (a, b):
        for e in KOS[c_][2]: t5.append((f"{c_.split()[0]} {e:+.4g}", KOS[c_][0](e) & var(b if c_ == a else a)))
    T, L = testler(m, t5); yaz(f"## {k}: {a} + {b}"); [yaz(x) for x in L]
    t15 = all(T[x] for x in ("T1", "T2", "T3", "T4", "T5")); GEC[k] = (t15, T["T8"])
    yaz(f"**{k}: " + " · ".join(f"{x} {'✔' if v else '✘'}" for x, v in T.items()) + f" → T1–T5 {'GEÇTİ' if t15 else 'GEÇMEDİ'} · yeni kısım {'var ✔' if T['T8'] else 'yok/zayıf ✘'}**\n")
# 🌪️+ birleşimi: C12 ∧ (geçen adayların C12 dışındaki koşulları; C20 hariç, C5 ⊂ C6; C3 adayları C12 içermez → birleşime girmez)
KAT = []
for k, (a, b) in ADAY.items():
    if not all(GEC[k]) or "C12 BTC oynak" not in (a, b): continue
    o = a if b == "C12 BTC oynak" else b
    if o == "C20 GARCH↑": continue
    KAT.append(o)
KAT = sorted(set(KAT)); KAT = [c_ for c_ in KAT if not (c_ == "C5 prim z≥2" and "C6 prim z≥1" in KAT)]
yaz(f"## 🌪️+ birleşimi: ✅ ana ∧ C12 BTC oynak ∧ ({' ∨ '.join(KAT) or '—'}) · 🌐🧪 hariç (onlarda 🌪️ zaten var)")
SONUC = {"kat": KAT, "gecti": False}
if KAT:
    nt = (X.tur != "🌐🧪").values; birl = lambda e12: KOS["C12 BTC oynak"][0](e12) & np.logical_or.reduce([var(c_) for c_ in KAT]) & nt
    T, L = testler(birl(1.25), [(f"C12 {e:+.2f}", birl(e)) for e in (1.15, 1.35)]); [yaz(x) for x in L]
    ok_ = all(T.values()); SONUC.update(gecti=ok_, T={k_: bool(v) for k_, v in T.items()})
    yaz(f"**🌪️+: " + " · ".join(f"{x} {'✔' if v else '✘'}" for x, v in T.items()) + f" → {'T1–T5 + T8 GEÇTİ (T6 canlı hesap eşitliği Actions’ta)' if ok_ else 'GEÇMEDİ → canlıya eklenmez'}**")
    Y = X[birl(1.25)]; SONUC["oran"] = {d: [int(len(Y[Y.don == d])), round(100 * Y[Y.don == d].ok.mean()), round(100 * Y[Y.don == d].D_T0.mean(), 2)] for d in "ABC"}
    R_ = X[(X.tur != "🌐🧪").values & ~birl(1.25)]; SONUC["diger"] = {d: [round(100 * R_[R_.don == d].ok.mean()), round(100 * R_[R_.don == d].D_T0.mean(), 2)] for d in "ABC"}
    SONUC["s_esik"] = float(X[X.don == "C"].s.quantile(2 / 3))
    yaz(f"\n_canlı C22 eşiği (2026 ✅ ana s üst üçte bir): {SONUC['s_esik']:.4f}_")
json.dump(SONUC, open("elitbenzeri2_sonuc.json", "w"), ensure_ascii=False, indent=1); open("elitbenzeri2_sonuc.md", "w").write("\n".join(out) + "\n")
