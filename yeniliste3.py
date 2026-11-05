# yeniliste3.py — PROTOKOL_yeniliste2.md: listeleme short süzgeçleri → yeniliste3_sonuc.md
import numpy as np, pandas as pd
exec(open("yeniliste2.py").read().split("yari = lambda")[0].replace('out = []', 'out = []', 1))
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
V = K.pivot(index="t", columns="s", values="v"); BTC = C["BTCUSDT"]
rows = []
for s, x in EV.iterrows():
    v = olay2(s, x.ilk, 1, 30, UC, 1.0)
    if not v: continue
    iL = gun.searchsorted(x.ilk); o, h, l, c = O[s].iloc[iL], Hh[s].iloc[iL], (K[(K.s == s)].set_index("t").l).get(x.ilk, np.nan), C[s].iloc[iL]
    fr = FG.get(s); f1 = fr[(fr.index >= x.ilk) & (fr.index < x.ilk + pd.Timedelta(days=1))].sum() if fr is not None else np.nan
    b30 = BTC.iloc[iL] / BTC.iloc[max(0, iL - 30)] - 1
    rows.append((s, x.ilk, v[0], v[1], v[2], c / o - 1, h / l - 1 if l else np.nan, b30, f1, V[s].iloc[iL] * c))
D = pd.DataFrame(rows, columns=["s", "L", "net", "gir", "cik", "r1", "ar1", "b30", "f1", "hac"]).sort_values("L").reset_index(drop=True)
D["hac_p"] = [((D.L < r.L) & (D.L >= r.L - pd.Timedelta(days=180))).pipe(lambda m: (D.hac[m] < r.hac).mean() if m.sum() >= 10 else np.nan) for r in D.itertuples()]
D["n30"] = [((D.L < r.L) & (D.L >= r.L - pd.Timedelta(days=30))).sum() for r in D.itertuples()]
D["y"] = D.L.dt.year; D["don"] = np.where(D.y <= 2023, "K", D.y.astype(str))
KOS = {"C1 ilk gün ≥ +%20": D.r1 >= 0.20, "C2 ilk gün ≤ 0": D.r1 <= 0, "C3 ilk gün aralığı ≥ %50": D.ar1 >= 0.5, "C4 BTC 30 g > 0": D.b30 > 0, "C5 BTC 30 g ≤ 0": D.b30 <= 0,
       "C6 ilk gün fonlama < 0": D.f1 < 0, "C7 ilk gün fonlama > 0": D.f1 > 0, "C8 hacim üst üçte bir": D.hac_p >= 2 / 3, "C9 hacim alt üçte bir": D.hac_p <= 1 / 3,
       "C10 sıcak dönem (≥ 15/30 g)": D.n30 >= 15, "C11 sakin dönem (< 15/30 g)": D.n30 < 15}
hf = lambda d: f"{len(d)} · {100 * d.net.mean():+.1f}% · med {100 * d.net.median():+.1f}% · ≤−50 %{100 * (d.net <= -0.5).mean():.0f}" if len(d) else "—"
yaz("# 🆕 Listeleme short süzgeçleri — PROTOKOL_yeniliste2.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · k 1 · H 30 · {len(D)} olay · hücre: n · ort. net · medyan · ≤ −%50 oranı_\n")
yaz("| koşul | keşif 2021–23 | 2024 | 2025 | 2026 | keşif | doğrulama |"); yaz("|---|---|---|---|---|---|---|")
taban_ = {p: D[D.don == p] for p in ("K", "2024", "2025", "2026")}
yaz("| (tümü) | " + " | ".join(hf(taban_[p]) for p in ("K", "2024", "2025", "2026")) + " | | |")
rng = np.random.default_rng(77); GEC = []
for ad, m in KOS.items():
    m = m.fillna(False).values; c = {p: D[m & (D.don == p).values] for p in ("K", "2024", "2025", "2026")}; t = taban_["K"]
    kes = len(c["K"]) >= 30 and c["K"].net.mean() >= t.net.mean() + 0.03 and c["K"].net.median() >= t.net.median(); dog = kes
    if kes:
        for p in ("2024", "2025", "2026"):
            d, b = c[p], taban_[p]
            pl = np.quantile([b.net.sample(len(d), random_state=int(rng.integers(1e9))).mean() for _ in range(200)], 0.95) if 0 < len(d) <= len(b) else np.inf
            dog &= len(d) >= 15 and d.net.mean() >= b.net.mean() + 0.02 and d.net.median() > 0 and (d.net <= -0.5).mean() <= (b.net <= -0.5).mean() and d.net.mean() > pl
    if kes and dog: GEC.append((ad, m))
    yaz(f"| {ad} | " + " | ".join(hf(c[p]) for p in ("K", "2024", "2025", "2026")) + f" | {'✔' if kes else '✘'} | {'✔' if (kes and dog) else ('✘' if kes else '')} |")
for ad, m in GEC:
    sel = set(D.s[m]); S = portfoy(filtre=lambda s: s in sel); g = all(v[0] > 0 and v[1] >= -0.10 and v[2] >= -0.20 and v[3] >= 0.55 for v in S.values())
    yaz(f"\n**Portföy — {ad}:** " + " · ".join(f"{y}: {100 * v[0]:+.1f}% · en kötü ay {100 * v[1]:+.1f}% · düşüş {100 * v[2]:.1f}% · pozitif ay %{100 * v[3]:.0f}" for y, v in S.items()) + f" → {'✅' if g else '❌'}")
yaz(f"\n**Sonuç → {'süzgeç bulundu: ' + ', '.join(a for a, _ in GEC) if GEC else '❌ süzgeç yok (hiçbir koşul keşif + doğrulamayı birlikte geçmedi)'}**")
open("yeniliste3_sonuc.md", "w").write("\n".join(out) + "\n"); D.to_csv("yeniliste3_olaylar.csv", index=False)
