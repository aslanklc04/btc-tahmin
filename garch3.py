# garch3.py — PROTOKOL_garch.md Ek 3 → garch3_sonuc.md
import hashlib, numpy as np, pandas as pd
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
D = pd.read_csv("garch3_veri.csv.gz"); D["t"] = pd.to_datetime(D.t, utc=True); D = D[D.t >= pd.Timestamp("2022-06-01", tz="UTC")].reset_index(drop=True)
D["don"] = np.select([D.t < pd.Timestamp("2025-01-01", tz="UTC"), D.t < pd.Timestamp("2026-01-01", tz="UTC")], ["A", "B"], "C"); D["sn"] = D.sinif.str.split(" \\(").str[0]
D["yari"] = D.nm.map(lambda s: int(hashlib.md5(s.encode()).hexdigest(), 16) % 2); AD = {"A": "2022-06→24", "B": "2025", "C": "2026"}
GU, GD = [0, 0.25, 0.5, 0.75, 1.0], [0, 0.25, 0.5, 0.75, 1.0, 1.5]
def mcol(gu, gd, g="D"):
    m = np.where(D.rho >= 1, D.rho ** gu, D.rho ** gd); m = np.clip(np.round(m / 0.05) * 0.05, 0.5, 2.0)
    cols = {f"{x:.2f}": D[f"{g}_{x:.2f}"].values for x in np.round(np.arange(0.5, 2.0001, 0.05), 2)}
    return np.array([cols[f"{v:.2f}"][i] for i, v in enumerate(m)])
st = lambda v: (np.isfinite(v).sum(), np.nanmean(v > 0) if np.isfinite(v).any() else np.nan, np.nanmean(v))
yaz("# 📈 Kısmi GARCH hedefi — 30 kombinasyon (PROTOKOL_garch.md Ek 3)"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {len(D)} sinyal · γ↑: oynaklık artacakken hedefi uzaklaştırma derecesi · γ↓: azalacakken yakınlaştırma derecesi · hücre: isabet · işlem başı net % (D)_\n")
for sn in ["✅ ana", "🔸 yedek", "📋 panelden"]:
    ms = (D.sn == sn).values; R = {}
    for gu in GU:
        for gd in GD:
            v = mcol(gu, gd); R[(gu, gd)] = {d: st(v[ms & (D.don == d).values]) for d in "ABC"}; R[(gu, gd)]["v"] = v
    t0 = R[(0, 0)]
    yaz(f"## {sn}"); yaz("| γ↑ \\ γ↓ (2022–24 isabet · net) | " + " | ".join(str(g) for g in GD) + " |"); yaz("|---|" + "---|" * len(GD))
    for gu in GU: yaz(f"| **{gu}** | " + " | ".join(f"%{100 * R[(gu, gd)]['A'][1]:.1f} · {100 * R[(gu, gd)]['A'][2]:+.2f}" for gd in GD) + " |")
    aday = [k for k in R if k != (0, 0) and R[k]["A"][1] >= t0["A"][1]]
    if not aday: yaz("\n**Seçim: isabeti düşürmeyen kombinasyon yok → bugünkü kalır.**\n"); continue
    sec = max(aday, key=lambda k: R[k]["A"][2]); v = R[sec]["v"]; v0 = t0["v"]; T = {}
    for d in "BC":
        m_ = ms & (D.don == d).values; T[f"test {AD[d]}"] = st(v[m_])[1] >= st(v0[m_])[1] - 0.005 and st(v[m_])[2] >= st(v0[m_])[2] + 0.0005
    for h in (0, 1):
        m_ = ms & (D.yari == h).values; T[f"yarı {h}"] = st(v[m_])[1] >= st(v0[m_])[1] - 0.005 and st(v[m_])[2] >= st(v0[m_])[2] + 0.0005
    vb, vb0 = mcol(*sec, "B"), mcol(0, 0, "B")
    for d in "ABC":
        m_ = ms & (D.don == d).values; T[f"limit {AD[d]}"] = np.nanmean(vb[m_]) - np.nanmean(vb0[m_]) >= 0
    yaz(f"\n**Seçim (2022–24'te isabeti düşürmeyenler içinde en kârlı): γ↑ {sec[0]} · γ↓ {sec[1]}**")
    for d in "ABC":
        m_ = ms & (D.don == d).values; a, b = st(v0[m_]), st(v[m_]); yaz(f"- {AD[d]}: %{100 * a[1]:.1f} · {100 * a[2]:+.2f} → %{100 * b[1]:.1f} · {100 * b[2]:+.2f} ({a[0]} sinyal)")
    yaz("- " + " · ".join(f"{k} {'✔' if x else '✘'}" for k, x in T.items())); yaz(f"**→ {'✅ GEÇTİ' if all(T.values()) else '❌ geçmedi'}**\n")
open("garch3_sonuc.md", "w").write("\n".join(out) + "\n")
