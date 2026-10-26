# igne_analiz.py — PROTOKOL_igne.md kararları (parçaları birleştirir → igne_sonuc.md)
import glob, numpy as np, pandas as pd
out = []; yaz = lambda s="": (out.append(s), print(s))
def oku(desen):
    L = []
    for f in sorted(glob.glob(desen, recursive=True)):
        try: d = pd.read_csv(f)
        except pd.errors.EmptyDataError: d = pd.DataFrame()
        print(f, len(d)); L.append(d)
    return pd.concat(L, ignore_index=True)
A = oku("parca/**/igneA_p*.csv.gz"); A["t"] = pd.to_datetime(A.t, utc=True)
B = oku("parca/**/igneB_p*.csv.gz"); B["gun"] = pd.to_datetime(B.gun, utc=True)
eksik = sorted(set(sum([open(f).read().split() for f in glob.glob("parca/**/igne_eksik_p*.txt", recursive=True)], [])))
U = lambda s: pd.Timestamp(s, tz="UTC")
DON = {"½-1": (U("2022-06-01"), U("2023-07-01")), "½-2": (U("2023-07-01"), U("2025-01-01")), "2025+": (U("2025-01-01"), U("2027-01-01")), "2026": (U("2026-01-01"), U("2027-01-01"))}
yaz("# 🪡 Likidasyon iğnesi — PROTOKOL_igne.md · Binance vadeli 1 dk")
yaz(f"A: {len(A):,} sinyal ölçüldü (veri_seti 28,280) · B: {len(B):,} gün×coin×d satırı · vadeli sembolü bulunamayan coin: {len(eksik)} ({', '.join(eksik[:30])})")
yaz(f"Son sinyal: {A.t.max()} · son B günü: {B.gun.max().date()}\n")
def ol(x):
    x = x.dropna(); n = len(x)
    return dict(n=n, i=100 * (x > 0).mean() if n else np.nan, net=100 * x.mean() if n else np.nan, kotu=100 * x.min() if n else np.nan)
f_ = lambda o: f"{o['n']} · %{o['i']:.1f} · {o['net']:+.3f}" if o["n"] else "0"
# ---------------- A
yaz("## A — sinyallere ikinci kademe (L = Gf·(1 − d·s), 7. dk → t + H)")
yaz("_hücre: dolan işlem · işlem isabeti · işlem başı net % · Taban = kademe 1 (giriş B)_\n")
kurA = [f"d{d}_{e}" for d in (0.5, 1.0, 1.5, 2.0) for e in ("E1", "E2")]
secA = {}
for sn in ("✅ ana (+0,75σ)", "🔸 yedek (+0,50σ)", "📋 panelden (+0,45σ)"):
    a = A[A.sinif == sn]; yaz(f"### {sn} · {len(a):,} sinyal")
    yaz("| Kural | " + " | ".join(DON) + " | keşif |"); yaz("|---|" + "---|" * (len(DON) + 1))
    tab = {dn: ol(a[(a.t >= x) & (a.t < y)].B) for dn, (x, y) in DON.items()}
    yaz("| Taban (kademe 1) | " + " | ".join(f_(o) for o in tab.values()) + " | — |")
    gec = []
    for k in kurA:
        oo = {dn: ol(a[(a.t >= x) & (a.t < y)][k]) for dn, (x, y) in DON.items()}
        ok = all(oo[h]["n"] >= 30 and oo[h]["i"] >= 70 and oo[h]["net"] >= 0.10 for h in ("½-1", "½-2"))
        if ok: gec.append(((oo["½-1"]["net"] * oo["½-1"]["n"] + oo["½-2"]["net"] * oo["½-2"]["n"]) / (oo["½-1"]["n"] + oo["½-2"]["n"]), k))
        yaz(f"| {k} | " + " | ".join(f_(o) for o in oo.values()) + f" | {'✅' if ok else '❌'} |")
    sn0 = sn.split(" ")[1]
    if gec:
        k = max(gec)[1]; secA[sn0] = k
        oo = {dn: ol(a[(a.t >= x) & (a.t < y)][k]) for dn, (x, y) in DON.items()}
        kk = all(oo[h]["n"] >= 20 and oo[h]["i"] >= 70 and oo[h]["net"] >= 0.10 and oo[h]["net"] >= tab[h]["net"] for h in ("2025+", "2026"))
        yaz(f"\n**Keşiften seçilen: {k} → KONTROL: {'✅ GEÇTİ' if kk else '❌ geçmedi'}**" + ("" if sn0 == "ana" else " _(bu sınıf yalnız bilgi)_"))
    else: yaz("\n**Keşif şartını geçen kural yok.**" + ("" if sn0 == "ana" else " _(bilgi)_"))
    for k in kurA[::2]:
        d = k.split("_")[0]; m = a[f"{d}_mae"].dropna()
        hf = {dn: a[(a.t >= x) & (a.t < y)][f"{d}_E1"].notna().sum() / max((min(y, A.t.max()) - x).days / 7, 1) for dn, (x, y) in DON.items()}
        yaz(f"- {d}: dolum oranı %{100 * a[f'{d}_E1'].notna().mean():.1f} · haftada dolum " + " · ".join(f"{v:.1f}" for v in hf.values()) + f" · dolumdan sonra ek düşüş ort. %{100 * m.mean():.1f}, en kötü %{100 * m.min():.1f}")
    yaz()
# ---------------- B
yaz("## B — bağımsız günlük iğne emri (BTC + 14 ana coin · 00:00 UTC'de L = P·(1 − d·σgün), gün boyu geçerli)")
yaz("_hücre: işlem · işlem isabeti · işlem başı net % · gün isabeti · en kötü işlem % · 2x/3x likidasyon_\n")
yaz("| Kural | " + " | ".join(DON) + " | keşif |"); yaz("|---|" + "---|" * (len(DON) + 1))
def olB(b, X):
    x = b.dropna(subset=[X]); n = len(x)
    if not n: return dict(n=0)
    g = x.groupby("gun")[X].mean()
    return dict(n=n, i=100 * (x[X] > 0).mean(), net=100 * x[X].mean(), gi=100 * (g > 0).mean(), kotu=100 * x[X].min(), l2=int((x[X + "_mae"] <= -0.45).sum()), l3=int((x[X + "_mae"] <= -0.30).sum()), ay=n / max(len(b.gun.unique()) / 30.4, 1))
fB = lambda o: (f"{o['n']} · %{o['i']:.1f} · {o['net']:+.2f} · gün %{o['gi']:.0f} · {o['kotu']:+.1f} · {o['l2']}/{o['l3']}" if o["n"] else "0")
gecB = []; RB = {}
for d in (2, 3, 4):
    for X in ("X1", "X2"):
        b = B[B.d == d]; oo = {dn: olB(b[(b.gun >= x) & (b.gun < y)], X) for dn, (x, y) in DON.items()}; RB[(d, X)] = oo
        ok = all(oo[h]["n"] >= 30 and oo[h]["i"] >= 70 and oo[h]["net"] >= 0.20 and oo[h]["gi"] >= 65 for h in ("½-1", "½-2"))
        if ok: gecB.append(((oo["½-1"]["net"] * oo["½-1"]["n"] + oo["½-2"]["net"] * oo["½-2"]["n"]) / (oo["½-1"]["n"] + oo["½-2"]["n"]), (d, X)))
        yaz(f"| d{d} {X} | " + " | ".join(fB(o) for o in oo.values()) + f" | {'✅' if ok else '❌'} |")
if gecB:
    k = max(gecB)[1]; oo = RB[k]
    kk = all(oo[h]["n"] >= 15 and oo[h]["i"] >= 70 and oo[h]["net"] >= 0.20 and oo[h]["gi"] >= 65 and oo[h]["l2"] == 0 for h in ("2025+", "2026"))
    yaz(f"\n**Keşiften seçilen: d{k[0]} {k[1]} → KONTROL: {'✅ GEÇTİ' if kk else '❌ geçmedi'}**")
else: yaz("\n**Keşif şartını geçen kural yok.**")
yaz("\n### B bilgi: coin başına (d3 X1, tüm dönem) · ayda işlem")
for nm, b in B[B.d == 3].groupby("nm"):
    o = olB(b, "X1"); yaz(f"- {nm}: " + (fB(o) + f" · ayda {o['ay']:.1f}" if o["n"] else "dolum yok"))
open("igne_sonuc.md", "w").write("\n".join(out) + "\n")
