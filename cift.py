# cift.py — PROTOKOL_cift.md: işlem çifti kaldırma (short) / ekleme (long) duyuruları → cift_sonuc.md
import json, re, numpy as np, pandas as pd
exec(open("duyuru.py").read().split("ayir = lambda")[0].replace('DU = pd.DataFrame(json.load(open("duyuru_liste.json")))', 'DU = pd.DataFrame(json.load(open("duyuru_liste.json")))'))
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
G = json.load(open("cift_govde.json"))
MAJ = set("BTC ETH BNB SOL XRP DOGE ADA TRX LINK AVAX LTC DOT".split()); STB = set("USDT USDC FDUSD TUSD BUSD DAI USDP EUR EURI AEUR XUSD USD1 USDE PAX USDS UST BFUSD RLUSD".split())
KOT = set("BUSD TUSD USDP PAX USDS AEUR UST DAI BIDR IDRT UAH RUB NGN GBP AUD VAI BKRW ZAR PLN RON ARS JPY MXN CZK COP".split())
rows, say = [], {"PR": 0, "PA": 0}
for kod, v in G.items():
    T = v["title"]; tur = "PR" if re.search(r"Removal|Remove", T) else ("PA" if re.search(r"\bAdd(s)?\b", T) else None)
    if tur is None or not v["cift"]: continue
    say[tur] += 1; g = pd.Timestamp(v["t"]).floor("D")
    for c in v["cift"]:
        b, q = c.split("/")
        if b in MAJ or b in STB or q in KOT or (tur == "PR" and q == "USDT"): continue
        rows.append((tur, g, b))
E = pd.DataFrame(rows, columns=["tur", "g", "coin"]).drop_duplicates().sort_values("g"); ev, sonolay = [], {}
for r in E.itertuples():
    for s in BIN.get(r.coin, []):
        if not (ilk[s] <= r.g and son[s] >= r.g + pd.Timedelta(days=1)) or r.g > gun.max() - pd.Timedelta(days=2): continue
        if (r.tur, s) in sonolay and (r.g - sonolay[(r.tur, s)]).days < 30: continue
        sonolay[(r.tur, s)] = r.g; ev.append((r.tur, r.g, s)); break
EV = pd.DataFrame(ev, columns=["tur", "g", "s"]); EV["y"] = EV.g.dt.year
def islem(j, i, yon, H):
    i0, i1 = i + 1, min(i + H, n - 1)
    if i0 >= n or not np.isfinite(Ov[i0, j]): return None
    cc = Cv[i0:i1 + 1, j]; ok = np.where(np.isfinite(cc))[0]
    if not len(ok): return None
    ex = i0 + ok[-1]; pe = Ov[i0, j] * (1 + 0.001 * yon); net = yon * (cc[ok[-1]] * (1 - 0.001 * yon) / pe - 1)
    fon = Fv[i0:ex + 1, j].sum() * (-yon); em = ESKI[i0] & np.isfinite(Cv[ex]); mk = np.nanmean(Cv[ex][em] / Ov[i0][em] - 1) if em.any() else 0.0
    return max(max(net, -1.0) - 0.001 + fon, -1.0), max(net, -1.0) - yon * mk, fon
def calistir(e, yon, H):
    R = []
    for r in e.itertuples():
        i = gun.searchsorted(r.g)
        if i >= n or gun[i] != r.g: continue
        v = islem(CI[r.s], i, yon, H)
        if v: R.append((r.s, r.g, r.y, *v, Cv[i, CI[r.s]] / Cv[i - 1, CI[r.s]] - 1 if i > 0 else np.nan))
    return pd.DataFrame(R, columns=["s", "g", "y", "net", "pnet", "fon", "r0"])
hf = lambda d: f"{len(d)} · {100 * d.net.mean():+.1f}% · med {100 * d.net.median():+.1f}% · kaz %{100 * (d.net > 0).mean():.0f} · piy {100 * d.pnet.mean():+.1f}% · ≤−50 %{100 * (d.net <= -0.5).mean():.0f}" if len(d) else "—"
yaz("# 🔇 İşlem çifti kaldırma / ekleme duyuruları — PROTOKOL_cift.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · gövdesi okunan duyuru {len(G)} (çift içeren kaldırma {say['PR']} · ekleme {say['PA']}) · giriş duyurudan sonraki gün açılışı · ücret+kayma %0,40 + gerçek fonlama · 1× · hücre: n · ort. net · medyan · kazanma · piyasaya göre · ≤ −%50_\n")
yaz("**Vadelisi olan olay (tür × yıl):** " + " · ".join(f"{t}: {EV[EV.tur == t].y.value_counts().sort_index().to_dict()}" for t in ("PR", "PA")) + "\n")
rng = np.random.default_rng(1213); HS = (7, 14, 30)
for t, ad, yon in (("PR", "PR — çift kaldırıldı → SHORT", -1), ("PA", "PA — çift eklendi → LONG", +1)):
    e = EV[EV.tur == t]; yaz(f"## {ad}")
    if not len(e): yaz("olay yok\n"); continue
    T = {H: calistir(e, yon, H) for H in HS}
    yaz(f"_Duyuru günü coin getirisi: medyan {100 * T[7].r0.median():+.1f}% · ort. {100 * T[7].r0.mean():+.1f}%_")
    yaz("| H (gün) | keşif ≤ 2024 | 2025 | 2026 |"); yaz("|---|---|---|---|")
    for H in HS: D = T[H]; yaz(f"| {H} | {hf(D[D.y <= 2024])} | {hf(D[D.y == 2025])} | {hf(D[D.y == 2026])} |")
    uy = {H: D for H, D in T.items() if len(D[D.y <= 2024]) >= 40}
    if not uy: yaz("**Keşifte ≥ 40 olaylı ayar yok → VERİ YETERSİZ**\n"); continue
    H = max(uy, key=lambda h: uy[h][uy[h].y <= 2024].net.mean()); D = T[H]; yaz(f"\n**Keşif seçimi: H {H}** ({hf(D[D.y <= 2024])})"); ok, yeter = True, True
    for y in (2025, 2026):
        d = D[D.y == y]
        if len(d) < 30: yaz(f"- {y}: {hf(d)} → olay < 30, veri yetersiz"); yeter = False; continue
        pl = []; i_lo, i_hi = gun.searchsorted(pd.Timestamp(f"{y}-01-01", tz="UTC")), min(n - 32, gun.searchsorted(pd.Timestamp(f"{y + 1}-01-01", tz="UTC")) - 1)
        olg = {s: set(gun.searchsorted(g_) for g_ in EV[EV.s == s].g) for s in d.s.unique()}
        for _ in range(200):
            v = []
            for s in d.s:
                for _t in range(8):
                    i = int(rng.integers(i_lo, i_hi))
                    if all(abs(i - o_) > 30 for o_ in olg[s]) and (x := islem(CI[s], i, yon, H)): v.append(x[0]); break
            pl.append(np.mean(v) if v else np.nan)
        q = np.nanquantile(pl, 0.95); g_ = d.net.mean() >= 0.02 and d.net.median() > 0 and (d.net > 0).mean() >= 0.55 and d.pnet.mean() > 0 and (d.net <= -0.5).mean() <= 0.10 and d.net.mean() > q; ok &= bool(g_)
        yaz(f"- {y}: {hf(d)} · en kötü {100 * d.net.min():.0f}% · fonlama ort. {100 * d.fon.mean():+.2f}% · rastgele gün ort. {100 * np.nanmean(pl):+.1f}% / %95 {100 * q:+.1f}% {'✔' if g_ else '✘'}")
    yaz(f"\n**{t} → {'veri yetersiz' if not yeter else ('✅ BULUNDU' if ok else '❌ bulunamadı')}**\n")
open("cift_sonuc.md", "w").write("\n".join(out) + "\n")
