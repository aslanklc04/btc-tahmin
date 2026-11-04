# ou.py — PROTOKOL_ou.md → ou_sonuc.md
import glob, hashlib, time, numpy as np, pandas as pd
T0 = time.time(); out = []
def yaz(s=""): out.append(s); print(s, flush=True)
A = pd.concat([pd.read_parquet(f, columns=["t", "coin", "o", "c"]) for f in sorted(glob.glob("teknik3_mum_*.parquet"))]); A["t"] = pd.to_datetime(A.t, utc=True)
A = A.drop_duplicates(["coin", "t"]); O = A.pivot(index="t", columns="coin", values="o").sort_index().astype(float); C = A.pivot(index="t", columns="coin", values="c").sort_index().astype(float)
x = np.log(C["BTC"]); bo, bc = O["BTC"].values, C["BTC"].values
yari = lambda s: int(hashlib.md5(s.encode()).hexdigest(), 16) % 2; W = 720
def don(t): return "2022–23" if t.year <= 2023 else ("2024" if t.year == 2024 else "2025–26")
R = []; rng = np.random.default_rng(11); PL = {k: [] for k in range(20)}
idx = C.index
for nm in C.columns:
    if nm == "BTC": continue
    y = np.log(C[nm]); ok = y.notna() & x.notna()
    if ok.sum() < 3000: continue
    mx, my = x.rolling(W).mean(), y.rolling(W).mean(); cov = (x * y).rolling(W).mean() - mx * my; var = (x * x).rolling(W).mean() - mx * mx
    beta = cov / var; e = y - (my - beta * mx) - beta * x
    b = e.rolling(W).corr(e.shift(1)); hl = -np.log(2) / np.log(b.where((b > 0) & (b < 1)))
    z = (e - e.rolling(W).mean()) / e.rolling(W).std()
    zv, hv, bv_, ov, cv = z.values, hl.values, beta.values, O[nm].values, C[nm].values; n = len(zv)
    sig = np.where((zv <= -2.5) & (hv <= 48))[0]; serbest = -1; Ln = []
    for i in sig:
        if i <= serbest or i + 2 >= n or not np.isfinite(ov[i + 1]): continue
        e_ = i + 1; mx_ = int(min(72, np.ceil(2 * hv[i]))); j = e_
        while j < min(n - 1, e_ + mx_ - 1) and not (np.isfinite(zv[j]) and zv[j] >= 0): j += 1
        if not np.isfinite(cv[j]): continue
        Pe = ov[e_] * 1.001; rL = cv[j] / Pe - 1 - 0.001 - 0.0001 * (j - e_ + 1) / 8; rb = bc[j] / bo[e_] - 1
        rH = rL - bv_[i] * rb - 0.001
        R.append(dict(coin=nm, t=idx[i], yari=yari(nm), don=don(idx[i]), L=rL, H=rH, sure=j - e_ + 1)); Ln.append(j - e_ + 1); serbest = j
    # plasebo: aynı sayıda rastgele giriş, aynı süre dağılımı
    if Ln:
        gecerli = np.where(np.isfinite(ov[:-80]) & np.isfinite(cv[:-80]) & np.isfinite(zv[:-80]))[0]
        for k in range(20):
            for i, L in zip(rng.choice(gecerli, len(Ln), replace=False), Ln):
                e_ = i + 1; j = min(n - 1, e_ + L - 1)
                if not (np.isfinite(ov[e_]) and np.isfinite(cv[j])): continue
                Pe = ov[e_] * 1.001; rL = cv[j] / Pe - 1 - 0.001 - 0.0001 * L / 8; rb = bc[j] / bo[e_] - 1; rH = rL - (bv_[i] if np.isfinite(bv_[i]) else 1) * rb - 0.001
                PL[k].append(dict(yari=yari(nm), don=don(idx[i]), L=rL, H=rH))
D = pd.DataFrame(R); P = {k: pd.DataFrame(v) for k, v in PL.items()}
print(f"[{time.time() - T0:.0f} sn] {len(D)} işlem", flush=True)
yaz("# 📐 Ornstein–Uhlenbeck geri dönüş sinyali — PROTOKOL_ou.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {D.coin.nunique()} coin · {len(D)} işlem · günde ≈ {len(D) / ((D.t.max() - D.t.min()).days):.1f} · ort. süre {D.sure.mean():.0f} s · hücre: işlem · isabet · işlem başı net % · [plasebo en iyi net]_\n")
CELL = [(h, d) for h in (0, 1) for d in ("2022–23", "2024", "2025–26")]
for sur, ad in (("L", "L — yalnız coin AL"), ("H", "H — coin AL + β×BTC SAT (piyasadan bağımsız)")):
    hc = []; aday = umut = True
    for h, d in CELL:
        y = D[(D.yari == h) & (D.don == d)][sur]; pb = max(p[(p.yari == h) & (p.don == d)][sur].mean() for p in P.values())
        hc.append(f"{'keşif' if h == 0 else 'doğr.'} {d}: {len(y)} · %{100 * (y > 0).mean():.0f} · {100 * y.mean():+.2f} [{100 * pb:+.2f}]")
        aday &= len(y) >= 30 and (y > 0).mean() >= 0.65 and y.mean() >= 0.003 and y.mean() > pb; umut &= len(y) >= 30 and (y > 0).mean() >= 0.60 and y.mean() > 0 and y.mean() > pb
    yaz(f"## {ad}"); [yaz(f"- {c}") for c in hc]; yaz(f"**→ sinyal adayı {'✅' if aday else '✘'} · umut verici {'✅' if umut else '✘'}** · en kötü işlem {100 * D[sur].min():.1f}%\n")
open("ou_sonuc.md", "w").write("\n".join(out) + "\n")
