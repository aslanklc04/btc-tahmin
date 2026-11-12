# duyuru.py — PROTOKOL_duyuru.md: Binance duyurularından sonraki günlerde sürüklenme → duyuru_sonuc.md
import json, re, numpy as np, pandas as pd
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
DU = pd.DataFrame(json.load(open("duyuru_liste.json"))).dropna(subset=["title", "t"]); DU["t"] = pd.to_datetime(DU.t, unit="ms", utc=True); DU = DU.drop_duplicates("code")
K = pd.read_parquet("yeniliste_mum.parquet"); F = pd.read_parquet("yeniliste_fon.parquet")
K["t"] = pd.to_datetime(K.t, utc=True).dt.floor("D"); K = K.drop_duplicates(["s", "t"])
VB = {x["s"]: x for x in json.load(open("vadeli_bilgi.json"))}
K = K[[s.endswith("USDT") and "_" not in s and ((s not in VB) or (VB[s]["ut"] == "COIN" and VB[s]["ct"] == "PERPETUAL")) for s in K.s]]
O, C = (K.pivot(index="t", columns="s", values=k) for k in ("o", "c")); gun = O.index; n = len(gun); COL = list(O.columns); CI = {s: j for j, s in enumerate(COL)}
F["t"] = pd.to_datetime(F.t, utc=True); FP = F.pivot_table(index=F.t.dt.floor("D"), columns="s", values="fr", aggfunc="sum").reindex(index=gun, columns=COL).fillna(0)
Ov, Cv, Fv = O.values, C.values, FP.values; ilk = K.groupby("s").t.min(); son = K.groupby("s").t.max()
yas = (gun.tz_convert(None).values[:, None] - ilk.reindex(COL).dt.tz_convert(None).values[None, :]) / np.timedelta64(1, "D"); ESKI = (yas >= 365) & np.isfinite(Ov)
taban = lambda s: re.sub(r"^(1000000|100000|10000|1000|1M)", "", s[:-4]); BIN = {}
for s in COL: BIN.setdefault(taban(s), []).append(s)
ayir = lambda x: [t.strip().upper() for t in re.split(r",|&| and ", x) if re.fullmatch(r"[A-Za-z0-9]{2,12}", t.strip())]
EV = []
for r in DU.itertuples():
    T = r.title; g = r.t.floor("D")
    m = re.match(r"Binance Will Delist (.+?) on \d{4}-\d{2}-\d{2}", T)
    if m and not re.search(r"Futures|Margin|Pair|Options|Leveraged|Loan|Earn|Contract", T): EV += [("D", g, c) for c in ayir(m.group(1))]
    m = re.search(r"Monitoring Tag to Include (.+?)(?:,? and Remove|, Remove| on \d{4}-\d{2}-\d{2}|$)", T)
    if m: EV += [("M", g, c) for c in ayir(m.group(1))]
    if T.startswith("Binance Will List "): EV += [("S", g, c.upper()) for c in re.findall(r"\(([A-Za-z0-9]{2,12})\)", T)]
E = pd.DataFrame(EV, columns=["tur", "g", "coin"]).drop_duplicates().sort_values("g"); rows = []; sonolay = {}
for r in E.itertuples():
    for s in BIN.get(r.coin, []):
        if not (ilk[s] <= r.g - pd.Timedelta(days=7 if r.tur == "S" else 0) and son[s] >= r.g + pd.Timedelta(days=1)) or r.g > gun.max() - pd.Timedelta(days=2): continue
        if (r.tur, s) in sonolay and (r.g - sonolay[(r.tur, s)]).days < 30: continue
        sonolay[(r.tur, s)] = r.g; rows.append((r.tur, r.g, s)); break
EV = pd.DataFrame(rows, columns=["tur", "g", "s"]); EV["y"] = EV.g.dt.year
def islem(j, i, yon, H):
    """i: duyuru günü satırı → giriş i+1 açılış, çıkış i+H kapanış"""
    i0, i1 = i + 1, min(i + H, n - 1)
    if i0 >= n or not np.isfinite(Ov[i0, j]): return None
    cc = Cv[i0:i1 + 1, j]; ok = np.where(np.isfinite(cc))[0]
    if not len(ok): return None
    ex = i0 + ok[-1]; pe = Ov[i0, j] * (1 + 0.001 * yon); net = yon * (cc[ok[-1]] * (1 - 0.001 * yon) / pe - 1)
    fon = Fv[i0:ex + 1, j].sum() * (-yon); em = ESKI[i0] & np.isfinite(Cv[ex]); mk = np.nanmean(Cv[ex][em] / Ov[i0][em] - 1) if em.any() else 0.0
    return max(max(net, -1.0) - 0.001 + fon, -1.0), max(net, -1.0) - yon * mk, fon
def calistir(ev, yon, H):
    R = []
    for r in ev.itertuples():
        i = gun.searchsorted(r.g)
        if i >= n or gun[i] != r.g: continue
        v = islem(CI[r.s], i, yon, H)
        if v: R.append((r.s, r.g, r.y, *v, Cv[i, CI[r.s]] / Cv[i - 1, CI[r.s]] - 1 if i > 0 else np.nan))
    return pd.DataFrame(R, columns=["s", "g", "y", "net", "pnet", "fon", "r0"])
hf = lambda d: f"{len(d)} · {100 * d.net.mean():+.1f}% · med {100 * d.net.median():+.1f}% · kaz %{100 * (d.net > 0).mean():.0f} · piy {100 * d.pnet.mean():+.1f}% · ≤−50 %{100 * (d.net <= -0.5).mean():.0f}" if len(d) else "—"
AD = {"D": ("D — listeden çıkarma duyurusu → SHORT", (1, 3, 7)), "M": ("M — izleme etiketi eklendi → SHORT", (7, 14, 30)), "S": ("S — spot listeleme (vadelisi önceden var) → SHORT", (1, 3, 7))}
yaz("# 📢 Binance duyurularından sonraki günlerde sürüklenme — PROTOKOL_duyuru.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {len(DU)} duyuru başlığı ({DU.t.min():%Y-%m} → {DU.t.max():%Y-%m}; haberler kataloğunda 225 sayfanın 3'ü çekilemedi) · giriş duyurudan sonraki gün açılışı · ücret+kayma %0,40 + gerçek fonlama · 1× · hücre: n · ort. net · medyan · kazanma · piyasaya göre · ≤ −%50_\n")
yaz("**Vadelisi olan olay sayısı (tür × yıl):** " + " · ".join(f"{t}: {EV[EV.tur == t].y.value_counts().sort_index().to_dict()}" for t in "DMS") + "\n")
rng = np.random.default_rng(1212)
for t, (ad, HS) in AD.items():
    ev = EV[EV.tur == t]; yaz(f"## {ad}")
    if not len(ev): yaz("olay yok\n"); continue
    T = {H: calistir(ev, -1, H) for H in HS}; TL = {H: calistir(ev, +1, H) for H in HS}
    yaz(f"_Duyuru günü (g) coin getirisi: medyan {100 * T[HS[0]].r0.median():+.1f}% · ort. {100 * T[HS[0]].r0.mean():+.1f}%_")
    yaz("| H (gün) | keşif ≤ 2024 | 2025 | 2026 | ters yön (long) 2025 · 2026: ort. net |"); yaz("|---|---|---|---|---|")
    for H in HS:
        D = T[H]; yaz(f"| {H} | {hf(D[D.y <= 2024])} | {hf(D[D.y == 2025])} | {hf(D[D.y == 2026])} | {100 * TL[H][TL[H].y == 2025].net.mean():+.1f}% · {100 * TL[H][TL[H].y == 2026].net.mean():+.1f}% |")
    uy = {H: D for H, D in T.items() if len(D[D.y <= 2024]) >= 25}
    if not uy: yaz(f"**Keşifte ≥ 25 olaylı ayar yok → VERİ YETERSİZ (sonuç zorlanmaz)**\n"); continue
    H = max(uy, key=lambda h: uy[h][uy[h].y <= 2024].net.mean()); D = T[H]; yaz(f"\n**Keşif seçimi: H {H}** ({hf(D[D.y <= 2024])})"); ok = True; yeter = True
    for y in (2025, 2026):
        d = D[D.y == y]
        if len(d) < 15: yaz(f"- {y}: {hf(d)} → olay < 15, veri yetersiz"); yeter = False; continue
        pl = []; i_lo, i_hi = gun.searchsorted(pd.Timestamp(f"{y}-01-01", tz="UTC")), min(n - 32, gun.searchsorted(pd.Timestamp(f"{y + 1}-01-01", tz="UTC")) - 1)
        olg = {s: set(gun.searchsorted(g_) for g_ in EV[EV.s == s].g) for s in d.s.unique()}
        for _ in range(200):
            v = []
            for s in d.s:
                for _t in range(8):
                    i = int(rng.integers(i_lo, i_hi))
                    if all(abs(i - o_) > 30 for o_ in olg[s]) and (x := islem(CI[s], i, -1, H)): v.append(x[0]); break
            pl.append(np.mean(v) if v else np.nan)
        q = np.nanquantile(pl, 0.95); g_ = d.net.mean() >= 0.02 and d.net.median() > 0 and (d.net > 0).mean() >= 0.55 and d.pnet.mean() > 0 and (d.net <= -0.5).mean() <= 0.10 and d.net.mean() > q; ok &= g_
        yaz(f"- {y}: {hf(d)} · en kötü {100 * d.net.min():.0f}% · fonlama ort. {100 * d.fon.mean():+.2f}% · rastgele gün %95 {100 * q:+.1f}% {'✔' if g_ else '✘'}")
    yaz(f"\n**{t} → {'veri yetersiz' if not yeter else ('✅ BULUNDU' if ok else '❌ bulunamadı')}**\n")
    D.to_csv(f"duyuru_{t}.csv", index=False)
open("duyuru_sonuc.md", "w").write("\n".join(out) + "\n")
