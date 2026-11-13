# btcalt.py — PROTOKOL_btcalt.md: BTC long + alt sepeti short (aylık) → btcalt_sonuc.md
import json, re, numpy as np, pandas as pd
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
K = pd.read_parquet("yeniliste_mum.parquet"); F = pd.read_parquet("yeniliste_fon.parquet")
K["t"] = pd.to_datetime(K.t, utc=True).dt.floor("D"); K = K.drop_duplicates(["s", "t"])
VB = {x["s"]: x for x in json.load(open("vadeli_bilgi.json"))}
HARIC = re.compile(r"^(USDC|FDUSD|TUSD|BUSD|USDP|DAI|BTCDOM|DEFI|FOOTBALL|BLUEBIRD|USDE|USD1|XUSD|EURI|AEUR)USDT$")
K = K[[s.endswith("USDT") and "_" not in s and not HARIC.match(s) and ((s not in VB) or (VB[s]["ut"] == "COIN" and VB[s]["ct"] == "PERPETUAL")) for s in K.s]]
O, Hh, C, V = (K.pivot(index="t", columns="s", values=k) for k in ("o", "h", "c", "v")); gun = O.index; COL = list(O.columns); jB = COL.index("BTCUSDT")
F["t"] = pd.to_datetime(F.t, utc=True); FP = F.pivot_table(index=F.t.dt.floor("D"), columns="s", values="fr", aggfunc="sum").reindex(index=gun, columns=COL).fillna(0)
Ov, Hv, Cv, Fv = O.values, Hh.values, C.values, FP.values; DV = (V * C).rolling(30, min_periods=15).sum().values
ilk = K.groupby("s").t.min().reindex(COL); ilk_i = gun.searchsorted(pd.DatetimeIndex(ilk))
lc = np.log(C); R90 = (lc - lc.shift(90)).values; R30 = (lc - lc.shift(30)).values
AYLAR = pd.period_range("2021-01", "2026-10", freq="M"); UC = 0.0035
def ay_sonuc(a):
    """→ dict: btc (long net), kisa[j] (short net, coin başına), özellikler"""
    i0 = gun.searchsorted(a.to_timestamp().tz_localize("UTC")); i1 = gun.searchsorted((a + 1).to_timestamp().tz_localize("UTC")) - 1
    if i0 >= len(gun) or i1 <= i0: return None
    btc = Cv[i1, jB] / Ov[i0, jB] - 1 - Fv[i0:i1 + 1, jB].sum()
    yas = i0 - ilk_i; ev = (yas >= 90) & np.isfinite(Ov[i0]) & (np.arange(len(COL)) != jB); kisa = np.full(len(COL), np.nan)
    for j in np.where(ev)[0]:
        pe = Ov[i0, j]; hh = Hv[i0:i1 + 1, j]; cc = Cv[i0:i1 + 1, j]; ok = np.where(np.isfinite(cc))[0]
        if not len(ok): continue
        w = np.where(hh >= 2 * pe)[0]
        if len(w): kisa[j] = -1.0 + Fv[i0:i0 + w[0] + 1, j].sum()
        else: kisa[j] = -(cc[ok[-1]] / pe - 1) + Fv[i0:i0 + ok[-1] + 1, j].sum()
    p = i0 - 1                                                                                     # ay başında bilinen son gün
    return dict(btc=btc, kisa=kisa, ev=ev & np.isfinite(kisa), r90=R90[p], r30=R30[p], dv=DV[p], yas=yas, btc30=R30[p, jB])
D = {a: ay_sonuc(a) for a in AYLAR}; D = {a: v for a, v in D.items() if v is not None}
def uc(x, m, ust):
    v = x[m]; v = v[np.isfinite(v)]
    if len(v) < 9: return np.zeros(len(x), bool)
    q = np.quantile(v, 2 / 3 if ust else 1 / 3); return m & np.isfinite(x) & ((x >= q) if ust else (x <= q))
SEP = {"V0 tüm altcoin'ler": lambda d: d["ev"], "V1 zayıflar (90 g en çok düşen ⅓)": lambda d: uc(d["r90"], d["ev"], False), "V2 güçlüler (90 g en çok yükselen ⅓)": lambda d: uc(d["r90"], d["ev"], True),
       "V3 küçük hacimliler (⅓)": lambda d: uc(d["dv"], d["ev"], False), "V4 büyük hacimliler (⅓)": lambda d: uc(d["dv"], d["ev"], True), "V5 gençler (90–365 gün)": lambda d: d["ev"] & (d["yas"] <= 365)}
def seri(fn, zaman):
    R, N = {}, {}
    for a, d in D.items():
        m = fn(d); N[a] = int(m.sum())
        if m.sum() < 5: R[a] = 0.0; continue
        if zaman:
            med = np.nanmedian(d["r30"][d["ev"]])
            if not (np.isfinite(d["btc30"]) and d["btc30"] > med): R[a] = 0.0; N[a] = 0; continue
        R[a] = d["btc"] + np.nanmean(d["kisa"][m]) - UC
    return pd.Series(R), pd.Series(N)
ys = lambda s, y: s[s.index.year == y]
def dd(s): c = s.cumsum(); return (c - c.cummax()).min()
yaz("# ⚖️ BTC al + altcoin sepeti sat (aylık, piyasa-nötr) — PROTOKOL_btcalt.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {len(COL)} coin vadelisi (kapatılanlar dahil) · 2021-01 → 2026-10 · aylık getiri = BTC − sepet + gerçek fonlama − %0,35 · 2 katına çıkan coin diliminde −%100 · hücre: yıllık toplam (en kötü ay · pozitif ay)_\n")
yaz("| sepet | zamanlama | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 (10 ay) | keşif ort/std | tüm dönem t · en büyük düşüş | sepette ort. coin |"); yaz("|---|---|---|---|---|---|---|---|---|---|---|")
T = {}
for ad, fn in SEP.items():
    for z in (False, True):
        s, nn = seri(fn, z); T[(ad, z)] = s; k = s[s.index.year <= 2023]; ks = k.mean() / k.std() if k.std() > 0 else 0
        yaz(f"| {ad} | {'evet' if z else 'sürekli'} | " + " | ".join(f"{100 * ys(s, y).sum():+.0f}% ({100 * ys(s, y).min():+.0f} · %{100 * (ys(s, y) > 0).mean():.0f})" for y in range(2021, 2027)) + f" | {ks:+.2f} | {s.mean() / (s.std() / np.sqrt(len(s))):.1f} · {100 * dd(s):.0f}% | {nn[nn > 0].mean():.0f} |")
sec = max(T, key=lambda k_: (lambda k: k.mean() / k.std() if k.std() > 0 else -9)(T[k_][T[k_].index.year <= 2023])); s = T[sec]
yaz(f"\n**Keşif seçimi (2021–23 ort/std en yüksek): {sec[0]} · {'zamanlamalı' if sec[1] else 'sürekli'}**"); ok = True
for y in (2024, 2025, 2026):
    a = ys(s, y); g = a.sum() > 0 and a.min() >= -0.15 and (a > 0).mean() >= 0.55; ok &= bool(g)
    yaz(f"- {y}: toplam {100 * a.sum():+.1f}% · en kötü ay {100 * a.min():+.1f}% · pozitif ay %{100 * (a > 0).mean():.0f} · pozisyonda ay %{100 * (a != 0).mean():.0f} {'✔' if g else '✘'}")
d3 = dd(s[s.index.year >= 2024]); ok &= d3 >= -0.30; yaz(f"- 2024–26 en büyük birikimli düşüş {100 * d3:.1f}% {'✔' if d3 >= -0.30 else '✘'}")
yaz(f"\n**Sonuç → {'✅ BULUNDU' if ok else '❌ bulunamadı'}**")
s0 = T[("V0 tüm altcoin'ler", False)]; yaz("\n**En kötü 3 ay (V0 sürekli):** " + " · ".join(f"{a}: {100 * v:+.0f}%" for a, v in s0.nsmallest(3).items()) + " · **en iyi 3 ay:** " + " · ".join(f"{a}: {100 * v:+.0f}%" for a, v in s0.nlargest(3).items()))
yaz("**Seçilenin en kötü 3 ayı:** " + " · ".join(f"{a}: {100 * v:+.0f}%" for a, v in s.nsmallest(3).items()))
b = pd.Series({a: d["btc"] for a, d in D.items()}); al = pd.Series({a: -np.nanmean(d["kisa"][d["ev"]]) for a, d in D.items()})
yaz("\n_Bilgi — yıllık: BTC long bacağı / altcoin sepeti (alış yönünde, fonlama dahil):_ " + " · ".join(f"{y}: {100 * ys(b, y).sum():+.0f}% / {100 * ys(al, y).sum():+.0f}%" for y in range(2021, 2027)))
open("btcalt_sonuc.md", "w").write("\n".join(out) + "\n")
