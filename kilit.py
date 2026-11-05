# kilit.py — PROTOKOL_kilit.md: büyük token kilit açılımlarından önce short → kilit_sonuc.md
import json, re, itertools, numpy as np, pandas as pd
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
T = [x for x in json.load(open("kilit_takvim.json")) if x.get("type")]; CG = json.load(open("kilit_cg.json"))
adr = {}; cid = {c["id"]: c for c in CG}
for c in CG:
    for _, a in (c.get("platforms") or {}).items():
        if a: adr.setdefault(a.lower(), c)
def sembol(tok, p):
    if not tok: return None
    if tok.startswith("coingecko:"): c = cid.get(tok.split(":", 1)[1])
    else: c = adr.get(tok.split(":")[-1].lower())
    return c["symbol"].upper() if c else None
K = pd.read_parquet("yeniliste_mum.parquet"); F = pd.read_parquet("yeniliste_fon.parquet")
K["t"] = pd.to_datetime(K.t, utc=True).dt.floor("D"); K = K.drop_duplicates(["s", "t"])
taban = lambda s: re.sub(r"^(1000000|100000|10000|1000|1M)", "", s[:-4])
BIN = {}
for s in sorted(K.s.unique(), key=lambda s: K[K.s == s].t.min() if False else 0):
    if s.endswith("USDT"): BIN.setdefault(taban(s), s)
O = K.pivot(index="t", columns="s", values="o"); C = K.pivot(index="t", columns="s", values="c"); gun = O.index
ilk = K.groupby("s").t.min()
F["t"] = pd.to_datetime(F.t, utc=True); FP = F.pivot_table(index=F.t.dt.floor("D"), columns="s", values="fr", aggfunc="sum").reindex(index=gun, columns=O.columns).fillna(0)
yas = (gun.tz_convert(None).values[:, None] - ilk.reindex(O.columns).dt.tz_convert(None).values[None, :]) / np.timedelta64(1, "D"); ESKI = pd.DataFrame(yas >= 365, index=gun, columns=O.columns) & O.notna()
TUR = {"insiders": "ekip", "team": "ekip", "privateSale": "yatırımcı"}
# ---- takvim → günlük açılım (ayrık) + birikimli (hepsi)
E = []
for x in T:
    s_ = sembol(x["token"], x["p"]); b = BIN.get(s_) if s_ else None
    if not b: continue
    tur = TUR.get(x["kat"], "diğer")
    try: a = float(x.get("amount") or 0); x["start"] = float(x["start"]); x["end"] = float(x.get("end") or 0); x["stepDuration"] = float(x.get("stepDuration") or 0)
    except Exception: continue
    if not (1.2e9 < x["start"] < 2.2e9): continue
    if not np.isfinite(a) or a <= 0: continue
    if x["type"] == "cliff": E.append((b, x["p"], x["start"], a, tur, 1, None))
    elif x["type"] == "step":
        for i in range(int(x["steps"])): E.append((b, x["p"], x["start"] + i * x["stepDuration"], a, tur, 1, None))
    else:
        if x["end"] > x["start"]: E.append((b, x["p"], x["start"], a, tur, 0, x["end"]))
E = pd.DataFrame(E, columns=["s", "p", "ts", "a", "tur", "ayrik", "en"]); E["d"] = pd.to_datetime(E.ts, unit="s", utc=True).dt.floor("D")
P1 = E.groupby("s").p.agg(lambda v: v.value_counts().index[0]); E = E[E.p == E.s.map(P1)]          # coin başına tek proje
OLAY = []
for s, g in E.groupby("s"):
    di, li = g[g.ayrik == 1], g[g.ayrik == 0]; top = g.a.sum()
    if di.empty: continue
    dg = di.groupby("d").a.sum().sort_index(); dcum = dg.cumsum().shift(1).fillna(0)
    ay = di.groupby(["d", "tur"]).a.sum().unstack(fill_value=0)
    for d, row in ay.iterrows():
        t_ = d.timestamp(); lin = (li.a * ((t_ - li.ts) / (li.en - li.ts)).clip(0, 1)).sum() if len(li) else 0.0
        dol = dcum.get(d, 0.0) + lin; oran = row.sum() / (dol if dol > 0 else top)
        if oran >= 0.01 and dol > 0: OLAY.append((s, d, oran, row.idxmax(), row.sum()))
OL = pd.DataFrame(OLAY, columns=["s", "d", "oran", "tur", "a"]).sort_values(["s", "d"])
OL = OL[(OL.d >= OL.s.map(ilk) + pd.Timedelta(days=45)) & (OL.d <= gun.max() - pd.Timedelta(days=2))]
keep, son = [], {}
for r in OL.itertuples():
    if r.s in son and (r.d - son[r.s]).days < 30: continue
    keep.append(r.Index); son[r.s] = r.d
OL = OL.loc[keep].reset_index(drop=True); OL["y"] = OL.d.dt.year
UC = 2 * (0.0005 + 0.001)
def islem(s, d, Eg):
    i0 = gun.searchsorted(d - pd.Timedelta(days=Eg)); i1 = gun.searchsorted(d + pd.Timedelta(days=1))
    if i0 < 0 or i1 >= len(gun) or i0 >= i1: return None
    o, c = O[s].iloc[i0], C[s].iloc[i0:i1 + 1].ffill().iloc[-1]
    if not (np.isfinite(o) and np.isfinite(c)): return None
    net = max(max(-(c / o - 1), -1.0) - UC + FP[s].iloc[i0:i1 + 1].sum(), -1.0)
    em = ESKI.iloc[i0] & C.iloc[i1].notna(); mk = (C.iloc[i1][em] / O.iloc[i0][em] - 1).mean()
    return net, net + mk
GRUP = {"tümü": lambda t: True, "ekip": lambda t: t == "ekip", "yatırımcı": lambda t: t == "yatırımcı", "ekip+yatırımcı": lambda t: t in ("ekip", "yatırımcı")}
R = {}
for Eg in (30, 14, 7):
    rows = [(r.s, r.d, r.y, r.tur, r.oran, *v) for r in OL.itertuples() if (v := islem(r.s, r.d, Eg))]
    R[Eg] = pd.DataFrame(rows, columns=["s", "d", "y", "tur", "oran", "net", "pnet"])
hf = lambda d: f"{len(d)} · {100 * d.net.mean():+.1f}% · med {100 * d.net.median():+.1f}% · kaz %{100 * (d.net > 0).mean():.0f} · piy {100 * d.pnet.mean():+.1f}% · ≤−50 %{100 * (d.net <= -0.5).mean():.0f}" if len(d) else "—"
DON = {"K": lambda y: y <= 2023, "2024": lambda y: y == 2024, "2025": lambda y: y == 2025, "2026": lambda y: y == 2026}
yaz("# 🔓 Token kilit açılımlarından önce short — PROTOKOL_kilit.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · takvim: emissions-adapters kopyası (304 proje, çalışmayan {96} kayıt dışarıda) · Binance'le eşleşen coin {OL.s.nunique()} · büyük açılım (≥ %1 dolaşım) {len(OL)} · hücre: n · ort. net · medyan · kazanma · piyasaya göre · ≤ −%50_\n")
yaz(f"_Yıllara göre olay: {OL.y.value_counts().sort_index().to_dict()} · türe göre: {OL.tur.value_counts().to_dict()}_\n")
yaz("| E (gün önce) | alıcı | keşif 2021–23 | 2024 | 2025 | 2026 |"); yaz("|---|---|---|---|---|---|")
for Eg, D in R.items():
    for g, f in GRUP.items():
        d = D[D.tur.map(f)]; yaz(f"| {Eg} | {g} | " + " | ".join(hf(d[d.y.map(fn)]) for fn in DON.values()) + " |")
cand = [(Eg, g) for Eg in R for g in GRUP if len((d := R[Eg][R[Eg].tur.map(GRUP[g])])[d.y <= 2023]) >= 30]
if not cand: yaz("\n**Keşifte ≥ 30 olaylı ayar yok → test yapılamadı**")
else:
    sec = max(cand, key=lambda a: (d := R[a[0]][R[a[0]].tur.map(GRUP[a[1]])])[d.y <= 2023].net.mean()); Eg, g = sec; D = R[Eg][R[Eg].tur.map(GRUP[g])]
    yaz(f"\n**Keşif seçimi: E {Eg} · {g}** ({hf(D[D.y <= 2023])})"); ok = True; rng = np.random.default_rng(99)
    unl = {s: set(OL[OL.s == s].d) for s in OL.s.unique()}
    for p in ("2024", "2025", "2026"):
        d = D[D.y == int(p)]; pl = []
        for _ in range(200):
            v = []
            for r in d.itertuples():
                for _t in range(10):
                    rd = pd.Timestamp(f"{p}-01-01", tz="UTC") + pd.Timedelta(days=int(rng.integers(0, 300)))
                    if all(abs((rd - u).days) > 30 for u in unl.get(r.s, ())) and (x := islem(r.s, rd, Eg)): v.append(x[0]); break
            pl.append(np.mean(v) if v else np.nan)
        q = np.nanquantile(pl, 0.95); g_ = len(d) >= 15 and d.net.mean() >= 0.02 and d.net.median() > 0 and (d.net > 0).mean() >= 0.55 and d.pnet.mean() > 0 and (d.net <= -0.5).mean() <= 0.10 and d.net.mean() > q
        ok &= g_; yaz(f"- {p}: {hf(d)} · rastgele tarih %95 {100 * q:+.1f}% {'✔' if g_ else '✘'}")
    yaz(f"\n**Sonuç → {'✅ BULUNDU' if ok else '❌ bulunamadı'}**")
yaz("\n_Bilinen yanlılık: takvimler bugünkü bilgiyle kodlanmış; bazı geçmiş açılımlar önceden bilinmiyor olabilir (sonuç iyimser olabilir)._")
for lo, hi in ((0.01, 0.05), (0.05, 0.10), (0.10, 9)):
    d = R[14][(R[14].oran >= lo) & (R[14].oran < hi)]; yaz(f"_Bilgi E 14 · büyüklük %{100 * lo:.0f}–{'' if hi > 1 else f'%{100 * hi:.0f}'}: {hf(d)}_")
open("kilit_sonuc.md", "w").write("\n".join(out) + "\n"); OL.to_csv("kilit_olaylar.csv", index=False)
