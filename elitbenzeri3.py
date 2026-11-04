# elitbenzeri3.py — PROTOKOL_elitbenzeri.md Ek 2: 💎🌪️ (E1 / E2) T1–T5 + T9 → elitbenzeri3_sonuc.md
import os, numpy as np, pandas as pd
src = open("elitbenzeri2.py").read().split('yaz("# 🌪️+')[0]; exec(src)
GF = next(p for p in ("canli/durum/genis_liste.txt", "../main-wt/durum/genis_liste.txt") if os.path.exists(p)); GEN = {l.strip()[:-4] for l in open(GF) if l.strip()}
dipC = lambda e: (X.rz <= e).values & ~X.nm.isin(GEN).values
C12 = lambda e: KOS["C12 BTC oynak"][0](e)
ELIT_v = lambda e_rz=-2.0: (X.rz <= e_rz).values | var("C3 🔥fon") | (X.tur == "🔀").values
AD_ = {"E1 💎 ELİT ∧ BTC oynak": (lambda e12=1.25, erz=-2.0: ELIT_v(erz) & C12(e12)), "E2 📉🔥 dip (canlı tanım) ∧ BTC oynak": (lambda e12=1.25, erz=-2.0: dipC(erz) & C12(e12))}
yaz("# 💎🌪️ ELİT + BTC oynak çift işareti — PROTOKOL_elitbenzeri.md Ek 2"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · ✅ ana (🤝/💵 hariç) · D_T0 · hücre: işlem · isabet · net % · geniş liste {len(GEN)} coin_\n")
SEC = None; hf = (X.t.max() - pd.Timestamp("2025-01-01", tz="UTC")).days / 7
for ad, fn in AD_.items():
    m = fn(); t5 = [(f"C12 {e:+.2f}", fn(e12=e)) for e in (1.15, 1.35)] + ([(f"rz {e:+.2f}", fn(erz=e)) for e in (-1.75, -2.25)] if ad.startswith("E2") else [])
    T, L = testler(m, t5); T.pop("T8"); L = [x for x in L if "T8" not in x]
    R = X[ELIT_v() & ~m]; Y = X[m]; t9 = []
    for d in "ABC":
        y, r = Y[Y.don == d], R[R.don == d]; t9.append(len(y) >= 20 and y.ok.mean() >= r.ok.mean() + 0.05 and y.D_T0.mean() >= r.D_T0.mean() + 0.003)
    T["T9"] = all(t9); L.append("- T9 ELİT'in geri kalanına göre: " + " · ".join(f"{AD[d]} aday {f(Y[Y.don == d])} / geri kalan {f(R[R.don == d])}" for d in "ABC") + f" → {'✔' if T['T9'] else '✘'}")
    y2 = Y[Y.don != "A"]; L.append(f"- bilgi: 2025+ haftada {len(y2) / hf:.1f} sinyal · farklı gün/hafta {y2.t.dt.floor('D').nunique() / hf:.1f}")
    yaz(f"## {ad}"); [yaz(x) for x in L]; ok_ = all(T.values())
    yaz(f"**{ad.split()[0]}: " + " · ".join(f"{k} {'✔' if v else '✘'}" for k, v in T.items()) + f" → {'GEÇTİ' if ok_ else 'GEÇMEDİ'}**\n")
    if ok_ and SEC is None: SEC = ad
yaz(f"## Seçim: {SEC or 'ikisi de geçmedi → eklenmez'}"); open("elitbenzeri3_sonuc.md", "w").write("\n".join(out) + "\n")
