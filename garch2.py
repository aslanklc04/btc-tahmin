# garch2.py — PROTOKOL_garch.md Ek 2 değerlendirme → garch2_sonuc.md
import hashlib, numpy as np, pandas as pd
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
D = pd.read_csv("garch2_veri.csv.gz"); D["t"] = pd.to_datetime(D.t, utc=True); D = D[D.t >= pd.Timestamp("2022-06-01", tz="UTC")]
D["don"] = np.select([D.t < pd.Timestamp("2025-01-01", tz="UTC"), D.t < pd.Timestamp("2026-01-01", tz="UTC")], ["A", "B"], "C"); D["sn"] = D.sinif.str.split(" \\(").str[0]
D["yari"] = D.nm.map(lambda s: int(hashlib.md5(s.encode()).hexdigest(), 16) % 2); AD = {"A": "2022-06→24", "B": "2025", "C": "2026"}
st = lambda v: (len(v.dropna()), (v.dropna() > 0).mean(), v.dropna().mean())
yaz("# 📈 GARCH'a göre 🎯 (TG) — PROTOKOL_garch.md Ek 2"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {len(D)} sinyal · hücre: sinyal · isabet · işlem başı net % (D piyasa) — T0 → TG_\n")
GR = [("✅ ana (tümü)", D.sn == "✅ ana", 30), ("🔸 yedek", D.sn == "🔸 yedek", 30), ("📋 panelden", D.sn == "📋 panelden", 30),
      ("⬇️ ana 🤝 BTC ile ortak", (D.sn == "✅ ana") & (D.tur == "🤝"), 30), ("⬇️ ana 💵 ABD alıyor", (D.sn == "✅ ana") & (D.tur == "💵"), 15)]
yaz("| grup | " + " | ".join(AD.values()) + " | yarılar (T0 → TG net) | limit B net farkı (3 dönem) | TG daha iyi | ana'ya çıkar |"); yaz("|---|---|---|---|---|---|---|---|")
for ad, m, nmin in GR:
    hc = []; iyi = True; ana = True
    for d in "ABC":
        y = D[m & (D.don == d)]; a, b = st(y.D_T0), st(y.D_TG)
        hc.append(f"%{100 * a[1]:.0f} · {100 * a[2]:+.2f} → %{100 * b[1]:.0f} · {100 * b[2]:+.2f} ({a[0]})")
        iyi &= a[0] >= nmin and b[1] >= a[1] - 0.01 and b[2] >= a[2] + 0.0005; ana &= b[0] >= nmin and b[1] >= 0.65 and b[2] > 0
    yr = []
    for h in (0, 1):
        y = D[m & (D.yari == h)]; a, b = st(y.D_T0), st(y.D_TG); yr.append(f"{100 * a[2]:+.2f}→{100 * b[2]:+.2f}"); iyi &= b[1] >= a[1] - 0.01 and b[2] >= a[2] + 0.0005
    bb = []
    for d in "ABC":
        y = D[m & (D.don == d)]; f = y.B_TG.mean() - y.B_T0.mean(); bb.append(f"{100 * f:+.2f}"); iyi &= f >= 0
    yaz(f"| {ad} | " + " | ".join(hc) + f" | {' · '.join(yr)} | {' · '.join(bb)} | {'✅' if iyi else '✘'} | {('✅' if (ana and iyi) else '✘') if ad.startswith('⬇️') else '—'} |")
yaz(f"\n_ρ̃ (kırpılmış) dağılımı: medyan {D.rho_k.median():.2f} · %10 {D.rho_k.quantile(.1):.2f} · %90 {D.rho_k.quantile(.9):.2f}_")
open("garch2_sonuc.md", "w").write("\n".join(out) + "\n")
