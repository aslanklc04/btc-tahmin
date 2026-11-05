# yas.py — PROTOKOL_yas.md: coin yaşı etkisi (aylık nötr sepet) → yas_sonuc.md
import re, numpy as np, pandas as pd
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
K = pd.read_parquet("yeniliste_mum.parquet"); F = pd.read_parquet("yeniliste_fon.parquet")
K["t"] = pd.to_datetime(K.t, utc=True).dt.floor("D"); K = K.drop_duplicates(["s", "t"])
HARIC = re.compile(r"^(USDC|FDUSD|TUSD|BUSD|USDP|DAI|BTCDOM|DEFI|FOOTBALL|BLUEBIRD|XAU|XAG|XPT|XPD|PAXG|AAPL|TSLA|NVDA|MSTR|COIN|AMZN|GOOGL|META|MSFT|HOOD|CRCL|SPY|QQQ|AMD|PLTR|INTC|NFLX|BABA)USDT$")
K = K[~K.s.str.match(HARIC)]
O = K.pivot(index="t", columns="s", values="o"); C = K.pivot(index="t", columns="s", values="c")
ilk = K.groupby("s").t.min()
F["t"] = pd.to_datetime(F.t, utc=True); FP = F.pivot_table(index=F.t.dt.floor("D"), columns="s", values="fr", aggfunc="sum").reindex(index=O.index, columns=O.columns).fillna(0)
AYLAR = pd.date_range("2022-01-01", "2026-10-01", freq="MS", tz="UTC")
def ay_getiri(a):
    b = a + pd.offsets.MonthBegin(1); i0 = O.index.searchsorted(a); i1 = O.index.searchsorted(b) - 1
    if i0 >= len(O.index) or i1 <= i0: return None
    o = O.iloc[i0]; c = C.iloc[i0:i1 + 1].ffill().iloc[-1]; ok = o.notna() & c.notna()
    r = (c / o - 1)[ok]; f = FP.iloc[i0:i1 + 1].sum()[ok]; yas = ((O.index[i0] - ilk[r.index]).dt.days)
    return r, f, yas
D = {a: ay_getiri(a) for a in AYLAR}; D = {a: v for a, v in D.items() if v is not None}
DIL = {"Y1 31–90 g": (31, 90), "Y2 91–180 g": (91, 180), "Y3 181–365 g": (181, 365)}
UC = 0.006
def strateji(lo, hi, karistir=None):
    R = {}
    for a, (r, f, yas) in D.items():
        y = yas.values.copy()
        if karistir is not None: y = karistir.permutation(y)
        g = (y >= lo) & (y <= hi); e = y > 365
        if g.sum() < 3 or e.sum() < 10: continue
        R[a] = -r[g].mean() + r[e].mean() - UC + f[g].mean() - f[e].mean()
    return pd.Series(R)
yaz("# 👶 Coin yaşı etkisi — genç kontratları short, yaşlıları long (PROTOKOL_yas.md)"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {K.s.nunique()} kontrat · aylık · maliyet %0,60/ay + gerçek fonlama · hücre: ay · ort. aylık · pozitif ay · en kötü ay_\n")
yaz("| strateji | 2022 | 2023 | 2024 | 2025 | 2026 | tüm dönem: t · en büyük düşüş · plasebo %95 | sonuç |"); yaz("|---|---|---|---|---|---|---|---|")
rng = np.random.default_rng(88)
for ad, (lo, hi) in DIL.items():
    s = strateji(lo, hi); ok = True; hc = []
    for y in range(2022, 2027):
        a = s[s.index.year == y]; hc.append(f"{len(a)} · {100 * a.mean():+.1f}% · %{100 * (a > 0).mean():.0f} · {100 * a.min():.1f}%" if len(a) else "—")
        ok &= len(a) > 0 and a.mean() > 0 and (a > 0).mean() >= 0.55 and a.min() >= -0.15
    t = s.mean() / (s.std() / np.sqrt(len(s))); c = s.cumsum(); dd = (c - c.cummax()).min()
    pl = np.quantile([strateji(lo, hi, rng).mean() for _ in range(200)], 0.95); ok &= t >= 2 and s.mean() > pl
    sb = [len(D[a][2][(D[a][2] >= lo) & (D[a][2] <= hi)]) for a in s.index]
    yaz(f"| S {ad} (sepette ort. {np.mean(sb):.0f} coin) | " + " | ".join(hc) + f" | t {t:.1f} · {100 * dd:.1f}% · {100 * pl:+.1f}% | {'✅' if ok else '❌'} |")
open("yas_sonuc.md", "w").write("\n".join(out) + "\n")
