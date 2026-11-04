# garch4.py — PROTOKOL_garch.md Ek 4 → garch4_sonuc.md
import numpy as np, pandas as pd
exec(open("garch3.py").read().split("st = lambda")[0])
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
ms = (D.sn == "✅ ana").values; v0, v1 = mcol(0, 0), mcol(0.25, 1.5); b0, b1 = mcol(0, 0, "B"), mcol(0.25, 1.5, "B")
def risk(v, m):
    x = v[m]; x = x[np.isfinite(x)]; q = max(1, int(round(0.05 * len(x)))); g = pd.Series(v[m], index=D.t[m].dt.floor("D")).groupby(level=0).sum().cumsum().values
    return dict(n=len(x), isa=(x > 0).mean(), net=x.mean(), cvar=np.sort(x)[:q].mean(), std=x.std(), mdd=(g - np.maximum.accumulate(g)).min(), worst=x.min())
f = lambda r: f"%{100 * r['isa']:.1f} · {100 * r['net']:+.3f} · CVaR5 {100 * r['cvar']:.2f} · std {100 * r['std']:.2f} · MDD {100 * r['mdd']:.0f} · en kötü {100 * r['worst']:.1f}"
yaz("# 📈 Kısmi GARCH hedefi (γ↑ 0,25 · γ↓ 1,5) — risk ve tam test (PROTOKOL_garch.md Ek 4, ✅ ana)"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M}_\n")
R1 = True; belirgin = 0; T1 = True
yaz("| dönem | bugünkü (T0) | kısmi GARCH |"); yaz("|---|---|---|")
for d in "ABC":
    m = ms & (D.don == d).values; a, b = risk(v0, m), risk(v1, m); yaz(f"| {AD[d]} | {f(a)} | {f(b)} |")
    R1 &= b["cvar"] >= a["cvar"] and b["std"] <= a["std"] and b["mdd"] >= a["mdd"] - 0.01; belirgin += (b["cvar"] - a["cvar"] >= 0.0005) or (a["std"] - b["std"] >= 0.0002)
    T1 &= b["isa"] >= a["isa"] - 0.005 and b["net"] >= a["net"]
RA = R1 and belirgin >= 2; T = {"T1 dönemler": T1}
ok = True
for h in (0, 1):
    m = ms & (D.yari == h).values; a, b = risk(v0, m), risk(v1, m); ok &= b["isa"] >= a["isa"] - 0.005 and b["net"] >= a["net"] and b["cvar"] >= a["cvar"]; yaz(f"- yarı {h}: {f(a)} → {f(b)}")
T["T2 coin yarıları"] = ok; ok = True
for d in "ABC":
    m = ms & (D.don == d).values; a, b = risk(b0, m), risk(b1, m); ok &= b["net"] >= a["net"] and b["cvar"] >= a["cvar"] - 0.0005; yaz(f"- limit {AD[d]}: {f(a)} → {f(b)}")
T["T3 limit"] = ok
ay = D.t.dt.strftime("%Y-%m"); G = pd.DataFrame({"ay": ay[ms], "a": v0[ms], "b": v1[ms]}).groupby("ay").agg(n=("a", "size"), a=("a", "mean"), b=("b", "mean")); G = G[G.n >= 20]
T["T4 aylık"] = (G.b >= G.a).mean() >= 0.55; yaz(f"- aylık: {len(G)} ay · kısmi ≥ bugünkü olan ay oranı %{100 * (G.b >= G.a).mean():.0f}")
top = D[ms].nm.value_counts().head(5).index; m = ms & ~D.nm.isin(top).values; a, b = risk(v0, m), risk(v1, m)
T["T5 ilk 5 coin hariç"] = b["isa"] >= a["isa"] - 0.005 and b["net"] >= a["net"]; yaz(f"- ilk 5 coin ({', '.join(top)}) hariç: {f(a)} → {f(b)}")
ok = True
for gu in (0, 0.5):
    for gd in (1.0, 1.5):
        vv = mcol(gu, gd); r = []
        for d in "ABC":
            m = ms & (D.don == d).values; r.append(np.nanmean(vv[m]) - np.nanmean(v0[m])); ok &= r[-1] >= -0.0002
        yaz(f"- komşu γ↑ {gu} · γ↓ {gd}: net farkı " + " · ".join(f"{100 * x:+.3f}" for x in r))
T["T6 komşular"] = ok
yaz(f"\n**Risk azaldı mı: {'✅ EVET' if RA else '❌ HAYIR'}** (R1 üç dönemde {'✔' if R1 else '✘'}, belirgin iyileşme {belirgin}/3 dönem)")
yaz("**Tam test:** " + " · ".join(f"{k} {'✔' if x else '✘'}" for k, x in T.items()))
yaz(f"**→ {'✅ GEÇTİ: canlıya eklenir' if RA and all(T.values()) else '❌ GEÇMEDİ: eklenmez'}**")
open("garch4_sonuc.md", "w").write("\n".join(out) + "\n")
