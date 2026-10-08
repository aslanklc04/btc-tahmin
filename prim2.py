# prim2.py — prim_coin.py'de geçen kuralları CANLIYA hazırlar (veri: prim_coin çalışmasının kaydı, yeniden indirme yok):
# (1) Giriş saati: araştırma 1 saat sonra girdi; canlıda mesaj sinyal saatinin hemen ardından gelir (gecikme 0). İkisi de tutuyor mu?
# (2) Canlı listesi (önceden sabit seçim kuralı): prim_coin'de ✅ · gecikme 0 ile de doğrulama net > 0 · 2026'da (≥ 5 işlem) net > 0 → coin başına doğrulama alt sınırı en yüksek TEK kural.
#     SAT kuralları canlıda zaten var olan BTC 🔻 dışında alınmaz (havuzda SAT tutmadı).
# (3) Seçilen listenin haftalık sinyal sayısı ve toplam isabeti (dikkat: liste 2024+ sonuçlarına bakılarak seçildi → canlıda biraz daha düşük beklenmeli).
import numpy as np, pandas as pd
from ortak import *
L = []
def yaz(s=""): print(s, flush=True); L.append(s)
V = {k: v.astype("float64") for k, v in pd.read_pickle("prim_veri.pkl").items() if len(v) >= 3000}
R = pd.read_csv("prim_coin_tum.csv")
A24, A26, LMT = pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC"), 0.0002
DON = (("seçim 2022-06→2023", lambda i: i < A24), ("doğrulama 2024+", lambda i: i >= A24), ("2026", lambda i: i >= A26))
ESIK = {"AL2": (2, 1), "AL3": (3, 1), "SAT2": (-2, -1)}
def net_ser(D, m, yon, H, lag):
    y = D.c.shift(-(lag + H)) / D.c.shift(-lag) - 1; ev = D.index[events(m.values, H)]; return yon * y.reindex(ev).dropna() - 2 * LMT
def ozet(net):
    out = {}
    for pn, f in DON:
        x = net[f(net.index)]; out[pn] = (len(x), 100 * (x > 0).mean() if len(x) else np.nan, 100 * x.mean() if len(x) else np.nan, 100 * wboot(x.values, x.index.values)[0] if len(x) >= 8 else np.nan)
    return out
def fmt(o): return " · ".join(("—" if not np.isfinite(v) else (f"{v:.0f}" if i < 2 else f"{v:+.2f}")) for i, v in enumerate(o))
yaz(f"# 💵 Kendi primi → canlı hazırlık — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n## 1. Geçen kurallar: giriş 1 saat sonra (araştırma) vs hemen (canlı)\n_işlem · isabet % · net % · alt sınır %_\n")
rows, ADAY = [], []
for _, r in R[R.ok].iterrows():
    if r.coin not in V: continue
    D = V[r.coin]; e, yon = ESIK[r.kural]; m = ((D.z >= e) if yon > 0 else (D.z <= e)).fillna(False)
    o1, o0 = ozet(net_ser(D, m, yon, int(r.saat), 1)), ozet(net_ser(D, m, yon, int(r.saat), 0))
    rows.append(dict(coin=r.coin, kural=r.kural, saat=int(r.saat), **{f"1 sa sonra · {pn}": fmt(o1[pn]) for pn, _ in DON[1:]}, **{f"hemen · {pn}": fmt(o0[pn]) for pn, _ in DON[1:]}))
    d0, k26 = o0[DON[1][0]], o0["2026"]
    if yon > 0 and d0[2] > 0 and (k26[0] < 5 or k26[2] > 0):
        ADAY.append(dict(coin=r.coin, kural=r.kural, esik=e, saat=int(r.saat), n=d0[0], isabet=d0[1], net=d0[2], alt=d0[3], n26=k26[0], isabet26=k26[1], net26=k26[2],
                         haftada=d0[0] / ((D.index[-1] - A24).days / 7)))
yaz("```\n" + pd.DataFrame(rows).to_string(index=False) + "\n```")
A = pd.DataFrame(ADAY)
SEC = A.sort_values("alt", ascending=False).groupby("coin").head(1).sort_values("alt", ascending=False)
yaz(f"\n## 2. Canlı listesi (coin başına tek kural; gecikmesiz girişle doğrulama ve 2026 kontrolü) — {len(SEC)} coin\n```\n" + SEC.round(2).to_string(index=False) + "\n```")
SEC.to_csv("prim_acik.csv", index=False)
# toplam: seçilen listenin hep birlikte sonucu (gecikmesiz)
parts = []
for _, r in SEC.iterrows():
    D = V[r.coin]; m = (D.z >= r.esik).fillna(False); parts.append(net_ser(D, m, 1, int(r.saat), 0))
net = pd.concat(parts).sort_index(); o = ozet(net); hf = lambda pn, f: len(net[f(net.index)])
yaz(f"\n## 3. Seçilen liste hep birlikte (hemen giriş)\n- doğrulama 2024+: {fmt(o[DON[1][0]])} · haftada ~{o[DON[1][0]][0] / ((net.index[-1] - A24).days / 7):.1f} sinyal\n"
    f"- 2026: {fmt(o['2026'])} · haftada ~{o['2026'][0] / ((net.index[-1] - A26).days / 7):.1f} sinyal\n- seçim dönemi (2022-06→2023): {fmt(o[DON[0][0]])}")
yaz("\n## Şu an\n" + " · ".join(f"{r.coin} z {V[r.coin].z.dropna().iloc[-1]:+.1f} (eşik {r.esik:+.0f})" for _, r in SEC.iterrows()))
open("prim2_sonuc.md", "w").write("\n".join(L) + "\n")
