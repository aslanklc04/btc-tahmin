# ayrim2.py — PROTOKOL_ayrim.md Ek 1: H1 / H3 sağlamlık testleri T1–T5 → ayrim2_sonuc.md (T6/T7 ayrim2_canli.py, Actions)
import hashlib, numpy as np, pandas as pd
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
k = ["t", "nm", "sinif", "H"]
V = pd.read_csv("veri_seti.csv.gz", usecols=k + ["tur", "b_vr", "c_r24"]).drop_duplicates(k); KR = pd.read_csv("karal2_veri.csv.gz", usecols=k + ["D_T0", "B_T0"]).drop_duplicates(k)
X = V.merge(KR, on=k); X["t"] = pd.to_datetime(X.t, utc=True); X = X[X.D_T0.notna() & (X.t >= pd.Timestamp("2022-06-01", tz="UTC"))].copy()
X["don"] = np.select([X.t < pd.Timestamp("2025-01-01", tz="UTC"), X.t < pd.Timestamp("2026-01-01", tz="UTC")], ["A", "B"], "C"); X["ay"] = X.t.dt.strftime("%Y-%m")
X["yari"] = X.nm.map(lambda s: int(hashlib.md5(s.encode()).hexdigest(), 16) % 2); X["ok"] = X.D_T0 > 0
G1 = X.sinif.str.startswith("✅") & (X.tur == "🌐🧪"); G3 = X.sinif.str.startswith("📋") & (X.tur == "💵")
AD = {"A": "2022-06→24", "B": "2025", "C": "2026"}
f = lambda y: f"{len(y)} · %{100 * y.ok.mean():.0f} · {100 * y.D_T0.mean():+.2f}" if len(y) else "—"
def per(y, esik=0.70, net0=True):
    return all(len(y[y.don == d]) >= 20 and y[y.don == d].ok.mean() >= esik and (not net0 or y[y.don == d].D_T0.mean() > 0) for d in "ABC")
yaz("# 🔍 Ayrım Ek 1 — H1 / H3 sağlamlık testleri (T1–T5)"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · D_T0 · hücre: sinyal · isabet · net %_\n")
SONUC = {}
for ad, grp, kos, alt in (("H1 ✅ ana 🌐🧪 + BTC oynak (b_vr ≥ 1,25)", G1, lambda e: X.b_vr >= e, [1.15, 1.35]), ("H3 📋 panelden 💵 + coin 24 s ≤ −%5", G3, lambda e: X.c_r24 <= e, [-0.04, -0.06])):
    e0 = 1.25 if ad.startswith("H1") else -0.05; m = grp & kos(e0); Y = X[m]; R = X[grp & ~kos(e0)]
    yaz(f"## {ad}"); yaz("taban (hücre): " + " · ".join(f"{AD[d]} {f(Y[Y.don == d])}" for d in "ABC") + f" · grubun geri kalanı: " + " · ".join(f"{AD[d]} {f(R[R.don == d])}" for d in "ABC"))
    T = {}
    # T1
    s = []
    for h in (0, 1):
        y = Y[Y.yari == h]; ok_ = len(y) and y.ok.mean() >= 0.70 and y.D_T0.mean() > 0 and all(len(y[y.don == d]) and y[y.don == d].ok.mean() >= 0.65 for d in "ABC")
        s.append(ok_); yaz(f"- T1 yarı {h}: tümü {f(y)} · " + " · ".join(f"{AD[d]} {f(y[y.don == d])}" for d in "ABC") + f" → {'✔' if ok_ else '✘'}")
    T["T1"] = all(s)
    # T2
    b = {d: Y[Y.don == d].B_T0.dropna() for d in "ABC"}; T["T2"] = all(len(b[d]) >= 20 and (b[d] > 0).mean() >= 0.70 for d in "ABC")
    yaz("- T2 limit giriş (B_T0): " + " · ".join(f"{AD[d]} {len(b[d])} · %{100 * (b[d] > 0).mean():.0f} · {100 * b[d].mean():+.2f}" for d in "ABC") + f" → {'✔' if T['T2'] else '✘'}")
    # T3
    ay = Y.groupby("ay").ok.agg(["size", "mean"]); ra = R.groupby("ay").ok.mean(); ay = ay[ay["size"] >= 5]; ay["r"] = ra.reindex(ay.index)
    oran = (ay["mean"] >= ay["r"]).mean(); T["T3"] = bool(len(ay) and oran >= 0.60)
    yaz(f"- T3 aylık istikrar: ≥ 5 sinyalli {len(ay)} ay · hücre ≥ geri kalan olan ay oranı %{100 * oran:.0f} · en kötü ay %{100 * ay['mean'].min():.0f} ({ay['mean'].idxmin()}) → {'✔' if T['T3'] else '✘'}")
    # T4
    top = Y.nm.value_counts().head(5).index.tolist(); y = Y[~Y.nm.isin(top)]
    T["T4"] = bool(y.ok.mean() >= 0.70 and y.D_T0.mean() > 0 and all(y[y.don == d].ok.mean() >= 0.65 for d in "ABC"))
    yaz(f"- T4 en çok 5 coin ({', '.join(top)}) çıkınca: tümü {f(y)} · " + " · ".join(f"{AD[d]} {f(y[y.don == d])}" for d in "ABC") + f" → {'✔' if T['T4'] else '✘'}")
    # T5
    s = []
    for e in alt:
        y = X[grp & kos(e)]; ok_ = per(y); s.append(ok_); yaz(f"- T5 eşik {e:+.2f}: " + " · ".join(f"{AD[d]} {f(y[y.don == d])}" for d in "ABC") + f" → {'✔' if ok_ else '✘'}")
    T["T5"] = all(s)
    SONUC[ad] = T; yaz(f"**{ad.split()[0]}: " + " · ".join(f"{k_} {'✔' if v else '✘'}" for k_, v in T.items()) + f" → T1–T5 {'GEÇTİ' if all(T.values()) else 'GEÇMEDİ'}**\n")
open("ayrim2_sonuc.md", "w").write("\n".join(out) + "\n")
