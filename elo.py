# elo.py — PROTOKOL_elo.md → elo_sonuc.md
import glob, numpy as np, pandas as pd
out = []
def yaz(s=""): out.append(s); print(s, flush=True)
A = pd.concat([pd.read_parquet(f, columns=["t", "coin", "c"]) for f in sorted(glob.glob("teknik3_mum_*.parquet"))]); A["t"] = pd.to_datetime(A.t, utc=True)
A = A[A.t.dt.hour == 0].drop_duplicates(["coin", "t"]); C = A.pivot(index="t", columns="coin", values="c").sort_index().astype(float)
R = C.pct_change(); yas = C.notna().cumsum(); R = R.where(yas >= 60)
piy = R.mean(axis=1); med = R.median(axis=1); gun = R.index; coins = R.columns; n = len(coins)
def elo1():
    Rt = pd.Series(1500.0, index=coins); P = []
    for t in gun:
        P.append(Rt.copy()); r = R.loc[t]; ok = r.notna()
        if ok.sum() < 10: continue
        s = (r[ok] > med[t]).astype(float); e = 1 / (1 + 10 ** (-(Rt[ok] - 1500) / 400)); Rt[ok] += 20 * (s - e)
    return pd.DataFrame(P, index=gun)                                                             # t'deki puan = t'den ÖNCEKİ maçlar
def elo2():
    rng = np.random.default_rng(7); Rt = pd.Series(1500.0, index=coins); P = []
    for t in gun:
        P.append(Rt.copy()); r = R.loc[t].dropna()
        if len(r) < 10: continue
        cs = rng.permutation(r.index.values)
        for a, b in zip(cs[0::2], cs[1::2]):
            ea = 1 / (1 + 10 ** ((Rt[b] - Rt[a]) / 400)); sa = float(r[a] > r[b]); Rt[a] += 20 * (sa - ea); Rt[b] -= 20 * (sa - ea)
    return pd.DataFrame(P, index=gun)
rel7 = (C / C.shift(7) - 1).sub((C / C.shift(7) - 1).mean(axis=1), axis=0).where(yas >= 60)
PUAN = {"E1 Elo (piyasaya karşı)": elo1(), "E2 Elo (eşleşmeli)": elo2(), "E3 7 g göreli güç": rel7.shift(0), "E4 ters (7 g en zayıf)": -rel7}
def sim(P, tut, rastgele=None):
    """P: t günü 00 UTC'de bilinen puan (t'ye kadar kapanışlar) → t..t+1 getirisi. Dönüş: günlük net getiri dizisi."""
    rng = np.random.default_rng(rastgele) if rastgele is not None else None
    sec_ = None; g = []
    for k, t in enumerate(gun[:-1]):
        t1 = gun[k + 1]; uygun = R.loc[t1].notna() & P.loc[t].notna() & (yas.loc[t] >= 60)
        if uygun.sum() < 10: g.append(np.nan); continue
        yenile = (tut == 1) or (t.dayofweek == 0) or sec_ is None
        if yenile:
            yeni = (list(rng.choice(uygun[uygun].index, 4, replace=False)) if rng is not None else list(P.loc[t][uygun].nlargest(4).index))
            deg = 4 if sec_ is None else len(set(yeni) - set(sec_)); sec_ = yeni; ucret = deg / 4 * (0.001 + 0.001 + 0.0005)
        else: ucret = 0.0
        sec_ok = [c for c in sec_ if pd.notna(R.loc[t1, c])]
        g.append((R.loc[t1, sec_ok].mean() if sec_ok else 0.0) - ucret)
    return pd.Series(g, index=gun[1:])
yaz("# 🏆 Maç tarzı güç sıralaması (Elo) — PROTOKOL_elo.md"); yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · {n} coin · her gün en güçlü 4 coin · ücret %0,10+%0,10+%0,05 (değişen pozisyon) · fazla = seçilen − piyasa (eşit ağırlık)_\n")
PZ = piy.shift(-1).reindex(gun[1:]).values * 0 + piy.reindex(gun[1:]).values
for tut in (1, 7):
    PL = [sim(PUAN["E1 Elo (piyasaya karşı)"], tut, rastgele=s) for s in range(50)]
    yaz(f"## Tutma {tut} gün"); yaz("| puan | " + " | ".join(str(y) for y in range(2022, 2027)) + " | sonuç |"); yaz("|---|---|---|---|---|---|---|")
    for ad, P in PUAN.items():
        g = sim(P, tut); f = g - piy.reindex(g.index); h = []; ok = True
        for y in range(2022, 2027):
            m = g.index.year == y; fy = f[m].dropna(); yil = fy.mean() * 365; yen = (fy > 0).mean()
            ply = max((p - piy.reindex(p.index))[p.index.year == y].mean() for p in PL) * 365
            h.append(f"{100 * yil:+.0f}% · yen %{100 * yen:.0f}"); ok &= yil > 0 and yen >= 0.52 and yil > ply
        yaz(f"| {ad} | " + " | ".join(h) + f" | {'✅' if ok else '❌'} |")
    yaz("")
open("elo_sonuc.md", "w").write("\n".join(out) + "\n")
