# yeniliste.py — PROTOKOL_yeniliste.md: yeni listelenen vadeli kontratları short → yeniliste_sonuc.md
import re, itertools, numpy as np, pandas as pd
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
K = pd.read_parquet("yeniliste_mum.parquet"); F = pd.read_parquet("yeniliste_fon.parquet")
K["t"] = pd.to_datetime(K.t, utc=True).dt.floor("D"); K = K.drop_duplicates(["s", "t"]).sort_values(["s", "t"])
HARIC = re.compile(r"^(USDC|FDUSD|TUSD|BUSD|USDP|DAI|BTCDOM|DEFI|FOOTBALL|BLUEBIRD|XAU|XAG|XPT|XPD|PAXG|AAPL|TSLA|NVDA|MSTR|COIN|AMZN|GOOGL|META|MSFT|HOOD|CRCL|SPY|QQQ|AMD|PLTR|INTC|NFLX|BABA)USDT$")
taban = lambda s: re.sub(r"^(1000000|100000|10000|1000|1M)", "", s[:-4])
ilk = K.groupby("s").t.min(); son = K.groupby("s").t.max()
S = pd.DataFrame({"ilk": ilk, "son": son}); S = S[~S.index.str.match(HARIC)]; S["b"] = [taban(s) for s in S.index]
S = S.sort_values("ilk").groupby("b").head(1)                                                    # aynı coin'in ilk kontratı
EV = S[S.ilk >= pd.Timestamp("2021-01-01", tz="UTC")]
O = K.pivot(index="t", columns="s", values="o"); C = K.pivot(index="t", columns="s", values="c"); Hh = K.pivot(index="t", columns="s", values="h")
gun = O.index; yas = (gun.tz_convert(None).values[:, None] - ilk.reindex(O.columns).dt.tz_convert(None).values[None, :]) / np.timedelta64(1, "D")
ESKI = pd.DataFrame(yas >= 365, index=gun, columns=O.columns) & O.notna()
F["t"] = pd.to_datetime(F.t, utc=True); FG = {s: g.set_index("t").fr.sort_index() for s, g in F.groupby("s")}
UC = 2 * (0.0005 + 0.001)
def olay(s, L, k, H, stop=None):
    i0 = gun.searchsorted(L + pd.Timedelta(days=k)); i1 = i0 + H - 1
    if i0 >= len(gun): return None
    o = O[s].iloc[i0]
    if not np.isfinite(o): return None
    cc = C[s].iloc[i0:i1 + 1].dropna()
    if not len(cc): return None
    ce, te = cc.iloc[-1], cc.index[-1]
    fr = FG.get(s); fon = fr[(fr.index >= gun[i0]) & (fr.index < te + pd.Timedelta(days=1))].sum() if fr is not None else 0.0
    r = -(ce / o - 1)
    if stop is not None and (Hh[s].iloc[i0:i1 + 1].dropna() >= o * (1 + stop)).any(): r = -stop - 0.002
    net = max(max(r, -1.0) - UC + fon, -1.0)                                                    # 1× short: fonlama dahil kayıp en çok −%100 (tasfiye)
    em = ESKI.iloc[i0] & C.iloc[min(i1, len(gun) - 1)].notna(); mk = (C.iloc[min(i1, len(gun) - 1)][em] / O.iloc[i0][em] - 1).mean()
    return net, net + mk, fon
AY = list(itertools.product((1, 3, 7), (7, 14, 30)))
def tablo(stop=None):
    R = {}
    for k, H in AY:
        rows = []
        for s, x in EV.iterrows():
            v = olay(s, x.ilk, k, H, stop)
            if v: rows.append((s, x.ilk, *v))
        D = pd.DataFrame(rows, columns=["s", "L", "net", "pnet", "fon"]); D["y"] = D.L.dt.year; R[(k, H)] = D
    return R
R = tablo(); yil = lambda D: {"K": D[D.y <= 2023], "2024": D[D.y == 2024], "2025": D[D.y == 2025], "2026": D[D.y == 2026]}
hf = lambda d: f"{len(d)} · ort. {100 * d.net.mean():+.1f}% · medyan {100 * d.net.median():+.1f}% · kazanma %{100 * (d.net > 0).mean():.0f} · piyasaya göre {100 * d.pnet.mean():+.1f}% · ≤ −%50 %{100 * (d.net <= -0.5).mean():.0f}" if len(d) else "—"
yaz("# 🆕 Binance'te yeni listelenen vadeli kontratları short — PROTOKOL_yeniliste.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {K.s.nunique()} sembol (kapatılanlar dahil) · 2021+ yeni listeleme {len(EV)} · ücret+kayma %0,30 + gerçek fonlama · 1× · hücre: olay · ort. net · medyan · kazanma · piyasaya göre · −%50'den kötü_\n")
yaz(f"_Yıllara göre listeleme: {EV.ilk.dt.year.value_counts().sort_index().to_dict()}_\n")
yaz("| k (gün sonra) | H (gün tut) | keşif 2021–23 | 2024 | 2025 | 2026 |"); yaz("|---|---|---|---|---|---|")
for (k, H), D in R.items(): Y = yil(D); yaz(f"| {k} | {H} | " + " | ".join(hf(Y[p]) for p in ("K", "2024", "2025", "2026")) + " |")
uy = {a: D for a, D in R.items() if len(yil(D)["K"]) >= 40}; sec = max(uy, key=lambda a: yil(uy[a])["K"].net.mean())
Y = yil(R[sec]); ok = True; yaz(f"\n**Keşif seçimi: k {sec[0]} · H {sec[1]}** ({hf(Y['K'])})")
for p in ("2024", "2025", "2026"):
    d = Y[p]; g = len(d) >= 20 and d.net.mean() >= 0.02 and d.net.median() > 0 and (d.net > 0).mean() >= 0.55 and d.pnet.mean() > 0 and (d.net <= -0.5).mean() <= 0.10; ok &= g
    yaz(f"- {p}: {hf(d)} · en kötü {100 * d.net.min():.0f}% · fonlama ort. {100 * d.fon.mean():+.2f}% {'✔' if g else '✘'}")
yaz(f"\n**Sonuç → {'✅ BULUNDU' if ok else '❌ bulunamadı'}**")
R30 = tablo(0.30); Y3 = yil(R30[sec]); yaz("\n_Bilgi — −%30 stoplu (aynı ayar):_ " + " · ".join(f"{p}: {hf(Y3[p])}" for p in ("K", "2024", "2025", "2026")))
open("yeniliste_sonuc.md", "w").write("\n".join(out) + "\n"); R[sec].to_csv("yeniliste_olaylar.csv", index=False)
