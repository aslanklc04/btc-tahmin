# ab_prim2.py — "İKİSİ DE GÜÇLÜ ALIYOR" (ABD primi z ≥ 2 VE Avrupa primi z ≥ 2 → AL) SAĞLAMLIK TESTİ. ab_prim.py'de kullanıcının fikri olarak önceden listelenmişti;
# resmi K kararlarına girmediği için burada ÖNCEDEN YAZILI ek ölçütlerle sınanır (24 s ve 8 s tutma, 46 coin havuz, giriş sinyalden 1 saat sonra, limit komisyon %0,02 × 2):
#   R1 haftalık blok bootstrap %5 alt sınırı > 0 — HEM 22-06→23 HEM 2024+ · R2 en iyi 5 hafta çıkarılınca 2024+ net hâlâ > 0 ·
#   R3 aynı sayıda işlem veren "yalnız ABD z ≥ k" kuralından (k seçim döneminde sayı eşitlenerek) 2024+ ve 2026'da daha iyi ·
#   R4 2024+ döneminde ≥ 10 işlemli coin'lerin ≥ %60'ında net > 0 · R5 plasebo: Avrupa primi zamanda kaydırılınca (≥ 30 gün, 500 kez) gözlenen 2024+ net'e ulaşma oranı < %5.
#   Hepsi geçerse (24 s için) "canlıya aday".
import glob, time, numpy as np, pandas as pd
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
f = lambda p: glob.glob(p, recursive=True)
RAW = {k: v.astype("float64") for k, v in pd.read_pickle(f("art3/**/prim_veri.pkl")[0]).items()}
for k, v in RAW.items(): v.index = pd.DatetimeIndex(v.index).tz_convert("UTC").as_unit("ns")
AB = pd.read_pickle(f("art4/**/ab_veri.pkl")[0]); AB = {k: v for k, v in AB.items() if k in RAW}
LMT = 0.0002; P0, A24, A26 = pd.Timestamp("2022-06-01", tz="UTC"), pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")
DON = (("22-06→23", lambda i: (i >= P0) & (i < A24)), ("2024+", lambda i: i >= A24), ("2026", lambda i: i >= A26))
rng = np.random.default_rng(0)
YC = {}
def olay(mask_f, H, kaydir=None):
    out = []
    for nm, d in AB.items():
        D = RAW[nm]
        if (nm, H) not in YC: YC[(nm, H)] = (D.c.shift(-(1 + H)) / D.c.shift(-1) - 1, d.z_ab.reindex(D.index))
        y, a = YC[(nm, H)]
        if kaydir is not None: a = pd.Series(np.roll(a.values, kaydir), index=a.index)
        m = mask_f(D.z, a).fillna(False).values; ev = D.index[events(m, H)]; x = (y.reindex(ev) - 2 * LMT).dropna()
        out.append(pd.DataFrame({"coin": nm, "net": x.values}, index=x.index))
    E = pd.concat(out).sort_index(); E = E[E.index >= P0]; return E
def ozet(E):
    return {dn: (len(x), 100 * (x.net > 0).mean() if len(x) else np.nan, 100 * x.net.mean() if len(x) else np.nan, 100 * wboot(x.net.values, x.index.values, 1000)[0] if len(x) >= 8 else np.nan)
            for dn, fd in DON for x in [E[fd(E.index)]]}
fm = lambda o: f"{o[0]} · %{o[1]:.0f} · {o[2]:+.2f} (alt {o[3]:+.2f})"
IKI = lambda u, a: (u >= 2) & (a >= 2)
yaz(f"# 💪 İkisi de güçlü alıyor (ABD z ≥ 2 ve Avrupa z ≥ 2) → AL: sağlamlık — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n{len(AB)} coin · _işlem · isabet · işlem başı net % (haftalık blok %5 alt sınır)_\n")
SONUC = {}
for H in (24, 8):
    E = olay(IKI, H); o = ozet(E)
    yaz(f"## {H} saat tut\n- İkisi de z ≥ 2: " + " | ".join(f"{dn}: {fm(o[dn])}" for dn, _ in DON))
    r1 = o["22-06→23"][3] > 0 and o["2024+"][3] > 0
    e24 = E[E.index >= A24]; wk = e24.net.groupby(e24.index.floor("7D")).sum().sort_values(ascending=False); kalan = e24[~e24.index.floor("7D").isin(wk.index[:5])]
    r2 = kalan.net.mean() > 0
    yaz(f"- Gün sayısı (2024+): {e24.index.floor('D').nunique()} farklı gün · en iyi 5 hafta: {', '.join(f'{t:%Y-%m-%d}' for t in wk.index[:5])} · bunlar çıkınca net {100*kalan.net.mean():+.2f}% ({len(kalan)} işlem)")
    n_sec = o["22-06→23"][0]; best_k, best_d = None, 1e9
    for k in np.arange(2.0, 8.01, 0.25):
        n_ = len(olay(lambda u, a, k=k: u >= k, H).pipe(lambda x: x[(x.index >= P0) & (x.index < A24)]))
        if abs(n_ - n_sec) < best_d: best_k, best_d = k, abs(n_ - n_sec)
    oU = ozet(olay(lambda u, a: u >= best_k, H)); r3 = o["2024+"][2] > oU["2024+"][2] and o["2026"][2] > oU["2026"][2]
    yaz(f"- Aynı sayıda işlem veren yalnız ABD kuralı: z ≥ {best_k:.2f} → " + " | ".join(f"{dn}: {fm(oU[dn])}" for dn, _ in DON))
    pc = e24.groupby("coin").net.agg(["count", "mean"]); pc = pc[pc["count"] >= 10]; r4 = (pc["mean"] > 0).mean() >= 0.6
    yaz(f"- Coin coin (2024+, ≥ 10 işlem): {int((pc['mean']>0).sum())}/{len(pc)} coin'de net > 0 · en iyi: " + ", ".join(f"{c} {100*m:+.2f}" for c, m in pc["mean"].sort_values(ascending=False).head(6).items())
        + " · en kötü: " + ", ".join(f"{c} {100*m:+.2f}" for c, m in pc["mean"].sort_values().head(4).items()))
    ob = o["2024+"][2]; sh = []
    for _ in range(500 if H == 24 else 200):
        s_ = int(rng.integers(720, 20000)) * (1 if rng.random() < 0.5 else -1); x = olay(IKI, H, kaydir=s_); x = x[x.index >= A24]
        if len(x): sh.append(100 * x.net.mean())
    p = float(np.mean(np.array(sh) >= ob)); r5 = p < 0.05
    yaz(f"- Plasebo (Avrupa primi kaydırılmış): ortalama {np.mean(sh):+.2f}% · gözlenen {ob:+.2f}% · p = {p:.3f}")
    SONUC[H] = (r1, r2, r3, r4, r5)
    yaz(f"- Ölçütler: R1 {'✅' if r1 else '❌'} · R2 {'✅' if r2 else '❌'} · R3 {'✅' if r3 else '❌'} · R4 {'✅' if r4 else '❌'} · R5 {'✅' if r5 else '❌'}\n")
# canlıdaki 15 💵 coin'i için ayrıca (bilgi)
PA = ["DOGE", "XRP", "ADA", "ALGO", "NEAR", "ETH", "CRV", "AVAX", "LINK", "BTC", "UNI", "AAVE", "FIL", "SOL", "INJ"]
E = olay(IKI, 24); e = E[E.coin.isin(PA)]; o = ozet(e)
yaz("## Canlıdaki 15 💵 coin'inde (24 s, bilgi)\n" + " | ".join(f"{dn}: {fm(o[dn])}" for dn, _ in DON))
w = len(E[E.index >= A24]) / ((E.index[-1] - A24).days / 7); w2 = len(e[e.index >= A24]) / ((E.index[-1] - A24).days / 7)
yaz(f"Haftada sinyal (2024+): 46 coin {w:.1f} · canlıdaki 15 coin {w2:.1f}")
ok24 = all(SONUC[24]); yaz(f"\n**Karar (24 s):** {'✅ tüm ölçütleri geçti → canlıya aday' if ok24 else '❌ en az bir ölçüt geçmedi'} · 8 s: {'✅' if all(SONUC[8]) else '❌'}\n_Süre: {time.time()-T0:.0f} sn_")
open("ab_prim2_sonuc.md", "w").write("\n".join(L) + "\n")
