# makas.py — PROTOKOL_makas.md: USDT/TL makası (Binance USDTTRY ↔ bankalar arası TRY=X) → makas_sonuc.md
import numpy as np, pandas as pd
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
B = pd.read_parquet("makas_binance.parquet"); U = B[B.sym == "USDTTRY"].set_index("t").sort_index(); U = U[~U.index.duplicated()]
Y = pd.read_parquet("makas_yahoo_saat.parquet").set_index("t").sort_index().close; Y = Y[~Y.index.duplicated()]
Y.index = Y.index.floor("h") + pd.Timedelta(hours=1)                                                # saat başı etiket → kapanış zamanı (Binance ile aynı)
X = U[["o", "c"]].join(Y.rename("fx"), how="left"); X = X[X.index >= Y.index.min()]
X["fx"] = X.fx.ffill(limit=72)                                                                   # hafta sonu: Cuma kapanışı taşınır
X["p"] = X.c / X.fx - 1; X = X.dropna(subset=["p"]); X["hs"] = (X.index.dayofweek >= 5) | ((X.index.dayofweek == 4) & (X.index.hour >= 22)) | ((X.index.dayofweek == 6))
orta = X.index[len(X) // 2]; X["don"] = np.where(X.index < orta, "S", "T")
UC = 0.001 + 0.001 + 0.0002                                                                       # %0,10 + %0,10 + kayma
yaz("# 💱 USDT/TL makası — PROTOKOL_makas.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {len(X)} saat · {X.index.min():%d.%m.%Y} → {X.index.max():%d.%m.%Y} · S: → {orta:%d.%m.%Y} · T: sonrası · makas p = Binance USDTTRY / bankalar arası USD/TL − 1 · ücret %0,10 + %0,10 + kayma %0,02_\n")
yaz("## Makasın kendisi"); yaz("| dönem | ort. | medyan | %10 | %90 | hafta içi ort. | hafta sonu ort. |"); yaz("|---|---|---|---|---|---|---|")
for d in ("S", "T"):
    x = X[X.don == d]; yaz(f"| {d} | {100 * x.p.mean():+.2f}% | {100 * x.p.median():+.2f}% | {100 * x.p.quantile(.1):+.2f}% | {100 * x.p.quantile(.9):+.2f}% | {100 * x.p[~x.hs].mean():+.2f}% | {100 * x.p[x.hs].mean():+.2f}% |")
s = X[X.don == "S"]; Q10, Q90 = s.p.quantile(0.10), s.p.quantile(0.90)
c, o, p, idx = X.c.values, X.o.values, X.p.values, X.index
def kural(gir, cik_kosul, yon, ix_list=None):
    """yon +1: USDT al (getiri = USDT/TL değişimi − USDT tutma tabanı değil; ham) · −1: USDT sat (getiri = USDT/TL düşüşü). Giriş sonraki saat açılışı."""
    R, i, n = [], 0, len(c)
    cand = ix_list if ix_list is not None else np.where(gir)[0]
    serbest = -1
    for i in cand:
        if i <= serbest or i + 1 >= n: continue
        e = i + 1; Pe = o[e]; j = e
        while j < min(n - 1, e + 72) and not cik_kosul(j): j += 1
        r = yon * (c[j] / Pe - 1) - UC; dur = j - e + 1
        base = (c[j] / Pe - 1)                                                                     # USDT tutsaydın bu sürede (taban)
        R.append((idx[i], r, base, dur)); serbest = j
    return pd.DataFrame(R, columns=["t", "net", "taban", "saat"])
M1 = kural(p <= Q10, lambda j: p[j] >= 0, +1)
M2 = kural(p >= Q90, lambda j: p[j] <= 0, -1)
dw, hr = idx.dayofweek, idx.hour
cuma = np.where((dw == 4) & (hr == 20))[0]; pzt = {i: None for i in np.where((dw == 0) & (hr == 8))[0]}
def hafta(yon):
    R = []
    for i in cuma:
        js = [j for j in range(i + 1, min(len(c), i + 80)) if j in pzt]
        if not js or i + 1 >= len(c): continue
        j = js[0]; Pe = o[i + 1]; R.append((idx[i], yon * (c[j] / Pe - 1) - UC, c[j] / Pe - 1, j - i))
    return pd.DataFrame(R, columns=["t", "net", "taban", "saat"])
M3a, M3b = hafta(+1), hafta(-1)
rng = np.random.default_rng(3)
def plasebo(K, yon, cikk):
    res = []
    for _ in range(50):
        r = []
        for d in ("S", "T"):
            k = int((K.t < orta).sum()) if d == "S" else int((K.t >= orta).sum()); pool = np.where(X.don.values == d)[0][:-80]
            r.append(kural(None, cikk, yon, np.sort(rng.choice(pool, size=max(k, 1), replace=False))))
        res.append(pd.concat(r))
    return res
def ozet(K, ad, PL=None, M2mi=False):
    yaz(f"\n### {ad}"); yaz("| dönem | işlem · ayda | isabet | işlem başı net | USDT tutmaya göre fazla | ort. süre | en kötü | plasebo en iyi net |"); yaz("|---|---|---|---|---|---|---|---|")
    gec = True
    for d in ("S", "T"):
        k = K[(K.t < orta) if d == "S" else (K.t >= orta)]; ay = max((X[X.don == d].index.max() - X[X.don == d].index.min()).days / 30.4, 1)
        if not len(k): yaz(f"| {d} | 0 | | | | | | |"); gec = False; continue
        fazla = (k.net - (-(k.taban) if M2mi else k.taban)).mean() if M2mi else (k.net - k.taban + UC).mean() * 0 + k.net.mean() - 0
        pl = max((pp[(pp.t < orta) if d == "S" else (pp.t >= orta)].net.mean() for pp in PL), default=np.nan) if PL else np.nan
        yaz(f"| {d} | {len(k)} · {len(k) / ay:.1f} | %{100 * (k.net > 0).mean():.0f} | {100 * k.net.mean():+.3f}% | {100 * (k.net - k.taban).mean():+.3f}% | {k.saat.mean():.0f} s | {100 * k.net.min():.2f}% | {100 * pl:+.3f}% |")
        gec &= k.net.mean() > 0 and (k.net > 0).mean() >= 0.65 and len(k) / ay >= 2 and (np.isnan(pl) or k.net.mean() > pl) and k.net.min() >= -0.02
    yaz(f"**→ {'✅ GEÇTİ' if gec else '❌ geçmedi'}**"); return gec
G = {}
G["M1"] = ozet(M1, "M1 iskonto → USDT al, makas kapanınca sat", plasebo(M1, +1, lambda j: p[j] >= 0))
G["M2"] = ozet(M2, "M2 prim → USDT sat, makas kapanınca geri al (USDT tutan için)", plasebo(M2, -1, lambda j: p[j] <= 0), True)
G["M3a"] = ozet(M3a, "M3a hafta sonu USDT al (Cuma 20:00 → Pazartesi 08:00 UTC)")
G["M3b"] = ozet(M3b, "M3b hafta sonu USDT sat")
yaz("\n## Bilgi — taban: USDT'yi hep tutmak"); yaz(" · ".join(f"{d}: {100 * (X[X.don == d].c.iloc[-1] / X[X.don == d].c.iloc[0] - 1):+.1f}% ({(X[X.don == d].index.max() - X[X.don == d].index.min()).days} gün)" for d in ("S", "T")))
yaz("\n## Özet"); yaz(" · ".join(f"{k}: {'✅' if v else '❌'}" for k, v in G.items()))
open("makas_sonuc.md", "w").write("\n".join(out) + "\n")
