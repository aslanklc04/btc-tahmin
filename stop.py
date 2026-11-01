# stop.py — PROTOKOL_stop.md: riski azaltan stop seçimi (sınıf başına) → stop_sonuc.md
import hashlib, numpy as np, pandas as pd
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
D = pd.read_csv("stop_veri.csv.gz"); D["t"] = pd.to_datetime(D.t, utc=True); D = D[D.t >= pd.Timestamp("2022-06-01", tz="UTC")]
D["don"] = np.select([D.t < pd.Timestamp("2025-01-01", tz="UTC"), D.t < pd.Timestamp("2026-01-01", tz="UTC")], ["A", "B"], "C"); D["sn"] = D.sinif.str.split(" \\(").str[0]
D["yari"] = D.nm.map(lambda s: int(hashlib.md5(s.encode()).hexdigest(), 16) % 2); D["gun"] = D.t.dt.floor("D")
VAR = ["S0"] + [f"SS{m:g}" for m in (1, 1.5, 2, 3, 4)] + [f"SY{p}" for p in (5, 8, 12, 15, 20)] + [f"SA{m}" for m in (2, 3, 4)] + [f"BE{m}" for m in (2, 3)]
VAD = {"S0": "stop yok (bugün)", **{f"SS{m:g}": f"−{m:g}σ" for m in (1, 1.5, 2, 3, 4)}, **{f"SY{p}": f"−%{p} sabit" for p in (5, 8, 12, 15, 20)}, **{f"SA{m}": f"−{m} ATR" for m in (2, 3, 4)},
       **{f"BE{m}": f"başa baş + −{m}σ" for m in (2, 3)}}
AD = {"A": "2022-06→24", "B": "2025", "C": "2026"}
def olc(y, v, g="D"):
    x = y[[f"{g}_{v}", f"{g}_S0"]].dropna(); a, b = x.iloc[:, 0].values, x.iloc[:, 1].values
    if len(a) < 30: return None
    q = max(1, int(round(0.05 * len(a)))); ca, cb = np.sort(a)[:q].mean(), np.sort(b)[:q].mean()
    st = y.loc[x.index, f"st_{v}"].mean() if f"st_{v}" in y and g == "D" else np.nan
    gd = y.loc[x.index].assign(_a=a).groupby("gun")._a.mean().cumsum().values; mdd = float((gd - np.maximum.accumulate(gd)).min()) if len(gd) else np.nan
    return dict(n=len(a), isa=(a > 0).mean(), net=a.mean(), en_kotu=a.min(), cvar=ca, st=st, mdd=mdd, isa0=(b > 0).mean(), net0=b.mean(), en_kotu0=b.min(), cvar0=cb)
def sart(m, cvar=True):
    if m is None: return False
    ok = m["isa"] >= m["isa0"] - 0.03 and m["net"] >= m["net0"] - 0.0005
    if cvar: ok = ok and (m["cvar"] - m["cvar0"]) / abs(m["cvar0"]) >= 0.20 and m["en_kotu"] > m["en_kotu0"]
    return ok
fm = lambda m: "—" if m is None else f"%{100 * m['isa']:.0f} · {100 * m['net']:+.2f} · en kötü {100 * m['en_kotu']:.1f} · CVaR5 {100 * m['cvar']:.2f} · stop %{100 * m['st']:.0f}" if np.isfinite(m["st"]) else f"%{100 * m['isa']:.0f} · {100 * m['net']:+.2f} · en kötü {100 * m['en_kotu']:.1f} · CVaR5 {100 * m['cvar']:.2f}"
yaz("# 🛑 Riski azaltan stop — PROTOKOL_stop.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {len(D)} sinyal · D = piyasadan giriş (ana ölçü), B = limit · hücre: isabet · işlem başı net % · en kötü işlem % · CVaR5 (en kötü %5'in ort.) % · stop olan oran_\n")
KARAR = {}
for sn in ["✅ ana", "🔸 yedek", "📋 panelden"]:
    Y = D[D.sn == sn]; yaz(f"## {sn} — {len(Y)} sinyal")
    yaz("| stop | " + " | ".join(AD[d] for d in "ABC") + " | MDD (A · B · C) |"); yaz("|---|---|---|---|---|")
    MA = {}
    for v in VAR:
        M = {d: olc(Y[Y.don == d], v) for d in "ABC"}; MA[v] = M
        yaz(f"| {VAD[v]} | " + " | ".join(fm(M[d]) for d in "ABC") + " | " + " · ".join("—" if M[d] is None else f"{100 * M[d]['mdd']:.0f}" for d in "ABC") + " |")
    aday = [v for v in VAR[1:] if MA[v]["A"] is not None and sart(MA[v]["A"], cvar=False)]
    sec = max(aday, key=lambda v: MA[v]["A"]["cvar"]) if aday else None
    if sec is None: yaz(f"\n**Seçim (A): isabet ≥ S0 − 3 puan ve net ≥ S0 − %0,05 şartını geçen stop YOK → stop eklenmez.**\n"); KARAR[sn] = None; continue
    T = {"seçim A": True}
    for d in "BC": T[f"test {AD[d]}"] = sart(MA[sec][d])
    for h in (0, 1): T[f"T1 yarı {h}"] = sart(olc(Y[Y.yari == h], sec))
    tb = {d: olc(Y[Y.don == d], sec, "B") for d in "ABC"}
    T["T2 limit"] = all(m is not None and m["net"] >= m["net0"] - 0.0005 and (m["cvar"] - m["cvar0"]) / abs(m["cvar0"]) >= 0.20 for m in tb.values())
    gec = all(T.values()); KARAR[sn] = sec if gec else None
    yaz(f"\n**Seçim (A'da şartı geçenler içinde CVaR5'i en iyi): {VAD[sec]}** · aday sayısı {len(aday)}")
    yaz("- " + " · ".join(f"{k} {'✔' if v else '✘'}" for k, v in T.items()))
    for d in "BC":
        m = MA[sec][d]; yaz(f"- {AD[d]}: isabet %{100 * m['isa0']:.0f} → %{100 * m['isa']:.0f} · net {100 * m['net0']:+.2f} → {100 * m['net']:+.2f} · en kötü {100 * m['en_kotu0']:.1f} → {100 * m['en_kotu']:.1f} · CVaR5 {100 * m['cvar0']:.2f} → {100 * m['cvar']:.2f} ({100 * (m['cvar'] - m['cvar0']) / abs(m['cvar0']):+.0f}%)")
    yaz("- limit (B): " + " · ".join("—" if tb[d] is None else f"{AD[d]} net {100 * tb[d]['net0']:+.2f} → {100 * tb[d]['net']:+.2f}, CVaR5 {100 * tb[d]['cvar0']:.2f} → {100 * tb[d]['cvar']:.2f}" for d in "ABC"))
    yaz(f"**→ {'GEÇTİ: mesaja 🛑 ' + VAD[sec] + ' stopu eklenecek' if gec else 'GEÇMEDİ: stop eklenmez'}**\n")
yaz("## Özet"); [yaz(f"- {sn}: {('🛑 ' + VAD[v]) if v else 'stop yok (bugünkü kalır)'}") for sn, v in KARAR.items()]
open("stop_sonuc.md", "w").write("\n".join(out) + "\n")
