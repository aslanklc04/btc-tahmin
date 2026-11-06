# tersine.py — PROTOKOL_tersine.md: sert yükselişten sonra short / çöküşten sonra long → tersine_sonuc.md
import json, re, itertools, numpy as np, pandas as pd
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
K = pd.read_parquet("yeniliste_mum.parquet"); F = pd.read_parquet("yeniliste_fon.parquet")
K["t"] = pd.to_datetime(K.t, utc=True).dt.floor("D"); K = K.drop_duplicates(["s", "t"])
VB = {x["s"]: x for x in json.load(open("vadeli_bilgi.json"))}
HARIC = re.compile(r"^(USDC|FDUSD|TUSD|BUSD|USDP|DAI|BTCDOM|DEFI|FOOTBALL|BLUEBIRD)USDT$")
K = K[[s.endswith("USDT") and not HARIC.match(s) and ((s not in VB) or (VB[s]["ut"] == "COIN" and VB[s]["ct"] == "PERPETUAL")) for s in K.s]]
O, Hh, L, C = (K.pivot(index="t", columns="s", values=k) for k in ("o", "h", "l", "c"))
F["t"] = pd.to_datetime(F.t, utc=True); FP = F.pivot_table(index=F.t.dt.floor("D"), columns="s", values="fr", aggfunc="sum").reindex(index=O.index, columns=O.columns).fillna(0)
Ov, Hv, Lv, Cv, Fv = O.values, Hh.values, L.values, C.values, FP.values; gun = O.index; n = len(gun); COL = list(O.columns)
R1 = (C / C.shift(1) - 1).values
def islem(j, g, yon, H, stop):
    """g: olay günü satırı · yon −1 short, +1 long → (net, çıkış satırı) | None"""
    i0, i1 = g + 1, g + H
    if i1 >= n or not np.isfinite(Ov[i0, j]): return None
    pe = Ov[i0, j] * (1 - 0.001 * yon)                                                             # kayma aleyhe
    net = None
    for i in range(i0, i1 + 1):
        if stop is not None:
            if yon < 0 and np.isfinite(Hv[i, j]) and Hv[i, j] >= pe * stop: net = -(stop * 1.001 - 1); ex = i; break
            if yon > 0 and np.isfinite(Lv[i, j]) and Lv[i, j] <= pe * stop: net = stop * 0.999 - 1; ex = i; break
    if net is None:
        cc = Cv[i0:i1 + 1, j]; ok = np.where(np.isfinite(cc))[0]
        if not len(ok): return None
        ex = i0 + ok[-1]; net = yon * (cc[ok[-1]] / pe - 1)
    fon = Fv[i0:ex + 1, j].sum() * (-yon)                                                          # short pozitif fonlamada alır
    return max(max(net, -1.0) - 0.001 + fon, -1.0), ex, fon
def calistir(yon, esik, H, stop, rng=None, gunler=None):
    rows = []
    for j, s in enumerate(COL):
        r = R1[:, j]; ev = np.where((r >= esik) if yon < 0 else (r <= esik))[0] if gunler is None else gunler.get(j, [])
        mes = -1
        for g in ev:
            if g <= mes: continue
            v = islem(j, g, yon, H, stop)
            if v: rows.append((s, gun[g], v[0], v[2])); mes = v[1]
    D = pd.DataFrame(rows, columns=["s", "g", "net", "fon"]); D["y"] = D.g.dt.year if len(D) else []
    return D
hf = lambda d: f"{len(d)} · {100 * d.net.mean():+.1f}% · med {100 * d.net.median():+.1f}% · kaz %{100 * (d.net > 0).mean():.0f} · ≤−50 %{100 * (d.net <= -0.5).mean():.0f}" if len(d) else "—"
DON = {"K": lambda y: y <= 2023, "2024": lambda y: y == 2024, "2025": lambda y: y == 2025, "2026": lambda y: y == 2026}
yaz("# 🔄 Sert yükselişten sonra short · çöküşten sonra long — PROTOKOL_tersine.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {len(COL)} coin · giriş olaydan sonraki gün açılışı · ücret+kayma %0,30 + gerçek fonlama · 1× · hücre: n · ort. net · medyan · kazanma · ≤ −%50_\n")
rng = np.random.default_rng(31)
for ad, yon, AY in (("S — yükselişten sonra SHORT", -1, list(itertools.product((0.30, 0.50), (1, 3, 7), (None, 1.40)))), ("L — çöküşten sonra LONG", +1, list(itertools.product((-0.30,), (1, 3, 7), (None, 0.70))))):
    yaz(f"## {ad}"); yaz("| eşik | H | stop | keşif 2021–23 | 2024 | 2025 | 2026 |"); yaz("|---|---|---|---|---|---|---|")
    T = {}
    for esik, H, stop in AY:
        D = calistir(yon, esik, H, stop); T[(esik, H, stop)] = D
        yaz(f"| {100 * esik:+.0f}% | {H} | {'yok' if stop is None else f'{100 * (stop - 1):+.0f}%'} | " + " | ".join(hf(D[D.y.map(f)]) for f in DON.values()) + " |")
    uy = {a: D for a, D in T.items() if len(D[D.y <= 2023]) >= 40}
    if not uy: yaz("\n**Keşifte ≥ 40 olaylı ayar yok**\n"); continue
    sec = max(uy, key=lambda a: uy[a][uy[a].y <= 2023].net.mean()); D = T[sec]; esik, H, stop = sec
    yaz(f"\n**Keşif seçimi: eşik {100 * esik:+.0f}% · H {H} · stop {'yok' if stop is None else f'{100 * (stop - 1):+.0f}%'}** ({hf(D[D.y <= 2023])})"); ok = True
    for p in ("2024", "2025", "2026"):
        d = D[D.y == int(p)]; pl = []
        olay_g = {COL.index(s): set(d[d.s == s].g) for s in d.s.unique()}
        for _ in range(200):
            gg = {}
            for j, ev in olay_g.items():
                i0 = gun.searchsorted(pd.Timestamp(f"{p}-01-01", tz="UTC")); i1 = min(n - 8, gun.searchsorted(pd.Timestamp(f"{int(p) + 1}-01-01", tz="UTC")) - 1)
                if i1 <= i0: continue
                c_ = rng.integers(i0, i1, size=3 * len(ev)); rr = R1[c_, j]; c_ = c_[~((rr >= esik) if yon < 0 else (rr <= esik))]   # olay olmayan günler
                gg[j] = sorted(c_[:len(ev)])
            P = calistir(yon, esik, H, stop, gunler=gg); pl.append(P.net.mean() if len(P) else np.nan)
        q = np.nanquantile(pl, 0.95)
        g_ = len(d) >= 30 and d.net.mean() >= 0.01 and d.net.median() > 0 and (d.net > 0).mean() >= 0.55 and (d.net <= -0.5).mean() <= 0.10 and d.net.mean() > q; ok &= g_
        m = d.groupby(d.g.dt.to_period("M")).net.sum() * 0.02
        yaz(f"- {p}: {hf(d)} · en kötü {100 * d.net.min():.0f}% · fonlama ort. {100 * d.fon.mean():+.2f}% · rastgele gün %95 {100 * q:+.1f}% · %2'lik payla yıllık {100 * m.sum():+.1f}% / en kötü ay {100 * m.min():+.1f}% {'✔' if g_ else '✘'}")
    yaz(f"\n**{ad.split(' —')[0]} → {'✅ BULUNDU' if ok else '❌ bulunamadı'}**\n")
open("tersine_sonuc.md", "w").write("\n".join(out) + "\n")
