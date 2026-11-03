# chronos_test.py — PROTOKOL_chronos.md (Actions, CPU) → chronos_sonuc.md
import glob, time, numpy as np, pandas as pd, torch
from chronos import BaseChronosPipeline
T0 = time.time(); out = []
def yaz(s=""): out.append(s); print(s, flush=True)
A = pd.concat([pd.read_parquet(f, columns=["t", "coin", "c"]) for f in sorted(glob.glob("teknik3_mum_*.parquet"))]); A["t"] = pd.to_datetime(A.t, utc=True)
C = A.drop_duplicates(["coin", "t"]).pivot(index="t", columns="coin", values="c").sort_index().astype(float)
ilk = C.notna().idxmax(); coins = ["BTC", "ETH"] + [c for c in ilk.sort_values().index if c not in ("BTC", "ETH")][:18]
P = BaseChronosPipeline.from_pretrained("amazon/chronos-bolt-small", device_map="cpu", torch_dtype=torch.float32)
noktalar = C.index[(C.index >= pd.Timestamp("2025-07-01", tz="UTC")) & (C.index <= pd.Timestamp("2026-10-28", tz="UTC")) & (C.index.hour == 0)]
R = []
for nm in coins:
    s = C[nm]; ctx, meta = [], []
    for t in noktalar:
        i = s.index.get_loc(t); x = s.iloc[i - 511:i + 1]; y = s.iloc[i + 1:i + 25]
        if x.isna().any() or len(x) < 512 or y.isna().any() or len(y) < 24: continue
        ctx.append(torch.tensor(x.values, dtype=torch.float32)); meta.append((t, x.iloc[-1], y.values, x.iloc[-1] / x.iloc[-25] - 1))
    for b in range(0, len(ctx), 128):
        q, _ = P.predict_quantiles(context=ctx[b:b + 128], prediction_length=24, quantile_levels=[0.1, 0.5, 0.9])
        for k, (t, c0, y, m24) in enumerate(meta[b:b + 128]):
            qq = q[k].numpy(); R.append(dict(coin=nm, t=t, c0=c0, m1=qq[0, 1], m4=qq[3, 1], m24=qq[23, 1], q10=qq[23, 0], q90=qq[23, 2], y1=y[0], y4=y[3], y24=y[23], mom=m24))
    print(f"[{time.time() - T0:.0f} sn] {nm} {len(meta)}", flush=True)
D = pd.DataFrame(R); D["don"] = np.where(D.t < pd.Timestamp("2026-01-01", tz="UTC"), "2025-H2", "2026"); D.to_csv("chronos_tahmin.csv.gz", index=False, compression="gzip")
yaz("# 🌦️ Hava tahmini tarzı ön-eğitimli model (Chronos-Bolt, sıfır atış) — PROTOKOL_chronos.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {len(coins)} coin · {len(D)} tahmin (her gün 00 UTC) · ücret %0,25 gidiş-dönüş_\n")
rng = np.random.default_rng(5); OK = True
yaz("| dönem | yön isabeti 1 s · 4 s · 24 s | Chronos AL sinyali: işlem · isabet · işlem başı net | her gün AL | momentum AL | yazı-tura en iyi | %80 aralıkta kalma |"); yaz("|---|---|---|---|---|---|---|")
for d, x in D.groupby("don"):
    acc = [((x[f"m{h}"] > x.c0) == (x[f"y{h}"] > x.c0)).mean() for h in (1, 4, 24)]
    r24 = x.y24 / x.c0 - 1; al = x.m24 >= x.c0 * 1.0025; n_ = r24[al] - 0.0025
    her = (r24 - 0.0025).mean(); mom = (r24[x.mom > 0] - 0.0025).mean()
    yt = max((r24[rng.random(len(x)) < 0.5] - 0.0025).mean() for _ in range(50)); kal = ((x.y24 >= x.q10) & (x.y24 <= x.q90)).mean()
    yaz(f"| {d} | %{100 * acc[0]:.1f} · %{100 * acc[1]:.1f} · %{100 * acc[2]:.1f} | {al.sum()} · %{100 * (n_ > 0).mean():.0f} · {100 * n_.mean():+.2f}% | {100 * her:+.2f}% | {100 * mom:+.2f}% | {100 * yt:+.2f}% | %{100 * kal:.0f} |")
    OK &= acc[2] >= 0.53 and n_.mean() > 0 and n_.mean() > max(her, mom, yt)
yaz(f"\n**→ {'✅ İŞE YARIYOR' if OK else '❌ geçmedi'}**"); yaz(f"\n_süre {time.time() - T0:.0f} sn_"); open("chronos_sonuc.md", "w").write("\n".join(out) + "\n")
