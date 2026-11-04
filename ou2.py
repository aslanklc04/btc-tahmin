# ou2.py — PROTOKOL_ou2.md: OU ters sinyaller (I1 açığa sat · I1-H · I2 güçlüyü al), yalnız hiç bakılmamış coin'ler → ou2_sonuc.md
import hashlib, numpy as np, pandas as pd
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
A = pd.read_parquet("ou2_mum.parquet"); A["t"] = pd.to_datetime(A.t, utc=True); A = A.drop_duplicates(["coin", "t"]); A = A[~A.coin.isin(["AMDB", "CRCLB", "EWYB", "INTCB", "LITEB", "METAB", "MSFTB", "MSTRB", "NVDAB", "PLTRB", "QQQB", "SNDKB", "SPCXB", "TSLAB", "XAUT", "RWUSD", "SOXLB", "GOOGLB", "SKHYB", "MUB"])]   # 04.11: tokenleştirilmiş hisse / altın / stabil hariç (kripto değil)
O = A.pivot(index="t", columns="coin", values="o").sort_index().astype(float); C = A.pivot(index="t", columns="coin", values="c").sort_index().astype(float)
x = np.log(C["BTC"]); bo, bc = O["BTC"].values, C["BTC"].values; idx = C.index; W = 720
yari = lambda s: int(hashlib.md5(s.encode()).hexdigest(), 16) % 2
def don(t): return "2022–23" if t.year <= 2023 else ("2024" if t.year == 2024 else "2025–26")
rng = np.random.default_rng(12); R = {k: [] for k in ("I1", "I1H", "I2")}; PL = {k: {i: [] for i in range(20)} for k in R}
for nm in C.columns:
    if nm == "BTC": continue
    y = np.log(C[nm])
    if y.notna().sum() < 3000: continue
    mx, my = x.rolling(W).mean(), y.rolling(W).mean(); beta = ((x * y).rolling(W).mean() - mx * my) / ((x * x).rolling(W).mean() - mx * mx)
    e = y - (my - beta * mx) - beta * x; b = e.rolling(W).corr(e.shift(1)); hl = -np.log(2) / np.log(b.where((b > 0) & (b < 1)))
    z = (e - e.rolling(W).mean()) / e.rolling(W).std(); zv, hv, bv, ov, cv = z.values, hl.values, beta.values, O[nm].values, C[nm].values; n = len(zv)
    for kural, kos, bit, yon in (("I1", zv <= -2.5, lambda j: zv[j] >= 0, -1), ("I2", zv >= 2.5, lambda j: zv[j] <= 0, +1)):
        sig = np.where(kos & (hv <= 48))[0]; serbest = -1; Ls = []
        for i in sig:
            if i <= serbest or i + 2 >= n or not np.isfinite(ov[i + 1]): continue
            e_ = i + 1; mx_ = int(min(72, np.ceil(2 * hv[i]))); j = e_
            while j < min(n - 1, e_ + mx_ - 1) and not (np.isfinite(zv[j]) and bit(j)): j += 1
            if not np.isfinite(cv[j]): continue
            r = yon * (cv[j] / ov[e_] - 1) - 0.001 - 0.001; rb = bc[j] / bo[e_] - 1
            R[kural].append(dict(coin=nm, t=idx[i], yari=yari(nm), don=don(idx[i]), net=r))
            if kural == "I1": R["I1H"].append(dict(coin=nm, t=idx[i], yari=yari(nm), don=don(idx[i]), net=r + bv[i] * rb - 0.001))
            Ls.append((i, j - e_ + 1)); serbest = j
        if Ls:
            ok = np.where(np.isfinite(ov[:-80]) & np.isfinite(cv[:-80]) & np.isfinite(bv[:-80]))[0]
            for k in range(20):
                for i, L in zip(rng.choice(ok, len(Ls), replace=False), [l for _, l in Ls]):
                    e_ = i + 1; j = min(n - 1, e_ + L - 1)
                    if not (np.isfinite(ov[e_]) and np.isfinite(cv[j])): continue
                    r = yon * (cv[j] / ov[e_] - 1) - 0.002; rb = bc[j] / bo[e_] - 1
                    PL[kural][k].append(dict(yari=yari(nm), don=don(idx[i]), net=r))
                    if kural == "I1": PL["I1H"][k].append(dict(yari=yari(nm), don=don(idx[i]), net=r + bv[i] * rb - 0.001))
ncoin = sum(1 for c in C.columns if c != "BTC" and C[c].notna().sum() >= 3000)
yaz("# 📐 OU ters sinyal — hiç bakılmamış coin'ler (PROTOKOL_ou2.md)"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {ncoin} yeni coin · hücre: işlem · isabet · işlem başı net % [plasebo en iyi]_\n")
CELL = [(h, d) for h in (0, 1) for d in ("2022–23", "2024", "2025–26")]
for k, ad in (("I1", "I1 — BTC'ye göre aşırı ucuz → AÇIĞA SAT"), ("I1H", "I1-H — açığa sat + β×BTC al (piyasadan bağımsız)"), ("I2", "I2 — BTC'ye göre aşırı güçlü → AL")):
    D = pd.DataFrame(R[k]); P = [pd.DataFrame(v) for v in PL[k].values()]; aday = umut = True; hc = []
    for h, d in CELL:
        y = D[(D.yari == h) & (D.don == d)].net if len(D) else pd.Series(dtype=float); pb = max((p[(p.yari == h) & (p.don == d)].net.mean() for p in P if len(p)), default=np.nan)
        hc.append(f"yarı {h} {d}: {len(y)} · %{100 * (y > 0).mean():.0f} · {100 * y.mean():+.2f} [{100 * pb:+.2f}]")
        aday &= len(y) >= 30 and (y > 0).mean() >= 0.60 and y.mean() >= 0.003 and y.mean() > pb; umut &= len(y) >= 30 and y.mean() > 0 and y.mean() > pb
    yaz(f"## {ad}"); [yaz(f"- {c}") for c in hc]; yaz(f"**→ sinyal adayı {'✅' if aday else '✘'} · umut verici {'✅' if umut else '✘'}** · toplam {len(D)} işlem · en kötü {100 * D.net.min():.1f}%\n")
open("ou2_sonuc.md", "w").write("\n".join(out) + "\n")
