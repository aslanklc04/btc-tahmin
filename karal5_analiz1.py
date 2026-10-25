# karal5_analiz1.py — PROTOKOL_karal5.md: tarama (keşif) → en iyi 5 (✅ ana) → karal5_secim.json + karal5_tarama.md
import glob, json, re, numpy as np, pandas as pd
P = sorted(glob.glob("parca/**/karal5s_meta_p*.csv.gz", recursive=True)); AD = json.load(open(glob.glob("parca/**/karal5_adlar.json", recursive=True)[0]))
MT, XS = [], []
for p in P:
    k = re.search(r"_p(\d+)\.csv", p).group(1); MT.append(pd.read_csv(p)); XS.append(np.load(glob.glob(f"parca/**/karal5s_X_p{k}.npy", recursive=True)[0]))
D = pd.concat(MT, ignore_index=True); X = np.vstack(XS).astype(float); D["t"] = pd.to_datetime(D.t, utc=True)
P0, YARI, A25, A26 = (pd.Timestamp(x, tz="UTC") for x in ("2022-06-01", "2023-07-01", "2025-01-01", "2026-01-01")); SON = pd.Timestamp("2027-01-01", tz="UTC")
DON = {"½-1": (P0, YARI), "½-2": (YARI, A25), "KEŞİF": (P0, A25), "2025+": (A25, SON), "2026": (A26, SON)}
TAB = {"✅ ana (+0,75σ)": "S 0.75", "🔸 yedek (+0,50σ)": "S 0.5", "📋 panelden (+0,45σ)": "S 0.45"}
def olc(m):
    x = X[m]; t = D.t.values[m]; dol = ~np.isnan(x[:, 0]); n = len(x)
    if n == 0: return None
    xf = x[dol]; snet = 100 * np.nansum(x, 0) / n; ii = 100 * (xf > 0).mean(0)
    df = pd.DataFrame(xf); df["t"] = t[dol]; sp = df.groupby("t").mean(); si = 100 * (sp.values > 0).mean(0)
    return dict(n=n, snet=snet, ii=ii, si=si, inet=100 * np.nanmean(xf, 0))
def iyi(o, b, j, bj):
    return ((o["snet"][j] >= b["snet"][bj] + 0.03 and o["ii"][j] >= b["ii"][bj] - 1 and o["si"][j] >= b["si"][bj] - 1)
            or (o["ii"][j] >= b["ii"][bj] + 3 and o["si"][j] >= b["si"][bj] + 1 and o["snet"][j] >= b["snet"][bj]))
L = []; yaz = lambda s="": (print(s), L.append(s)); SEC = {}
yaz(f"# 🎯 Büyük kâr-al taraması (karal5) — {len(AD)} kural · {len(D):,} sinyal\n_Hücre: işlem isabeti · saat isabeti · **sinyal başı net** %_\n")
for sn, tb in TAB.items():
    bj = AD.index(tb); O = {dn: olc(((D.sinif == sn) & (D.t >= a) & (D.t < b)).values) for dn, (a, b) in DON.items()}
    gec = [j for j in range(len(AD)) if j != bj and iyi(O["½-1"], O["½-1"], j, bj) and iyi(O["½-2"], O["½-2"], j, bj)]
    sec = sorted(gec, key=lambda j: -O["KEŞİF"]["snet"][j])[:5]
    if sn.startswith("✅"): SEC = {"secim": [AD[j] for j in sec], "taban": tb}
    yaz(f"## {sn} — taban {tb} · keşifte iki yarıda da iyi: {len(gec)} kural")
    yaz("| Kural | " + " | ".join(DON) + " |"); yaz("|---|" + "---|" * len(DON))
    f = lambda j: "| " + AD[j] + (" (taban)" if j == bj else (" ⭐ seçildi" if j in sec else "")) + " | " + " | ".join(f"%{o['ii'][j]:.1f} · %{o['si'][j]:.1f} · **{o['snet'][j]:+.3f}**" for o in O.values()) + " |"
    yaz(f(bj)); [yaz(f(j)) for j in sec]
    yaz("\n_Bilgi: keşif sinyal başı netine göre ilk 15 (şarttan bağımsız)_"); [yaz(f(j)) for j in np.argsort(-O["KEŞİF"]["snet"])[:15]]
    yaz("\n_Bilgi: keşif işlem isabetine göre ilk 10_"); [yaz(f(j)) for j in np.argsort(-O["KEŞİF"]["ii"])[:10]]; yaz("")
json.dump(SEC, open("karal5_secim.json", "w"), ensure_ascii=False); open("karal5_tarama.md", "w").write("\n".join(L) + "\n")
O25 = {sn: {dn: olc(((D.sinif == sn) & (D.t >= a) & (D.t < b)).values) for dn, (a, b) in DON.items()} for sn in ["✅ ana (+0,75σ)"]}
json.dump({dn: {k: (v.tolist() if hasattr(v, "tolist") else v) for k, v in o.items()} for dn, o in O25["✅ ana (+0,75σ)"].items()}, open("karal5_ana_olcu.json", "w"))
