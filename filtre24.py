# filtre24.py — 24 SAAT DENEME SİNYALİNE FİLTRE: isabeti artıran bir "ne zaman güvenilir" kuralı var mı? (canlı sisteme dokunmaz)
# Temel sinyal: canlı denemedeki 10 coin'de 24 saat 'Çok güçlü ↑' (ilk saat sayılır, 24 saat tekrar sayılmaz; giriş 1 saat sonra, limit komisyon %0,02×2).
# Filtreler ÖNCEDEN sabit; sinyal saatinde koşul sağlanmazsa o sinyal alınmaz:
#   F1: 8 saatlik model de 'Güçlü ve üstü ↑' · F2: 72 saatlik model yönü ↑ · F3: BTC'nin 24 saatlik model yönü ↑ · F4: F1 ve F2 birlikte
#   F5: coin'in KENDİ son 20 sonuçlanmış sinyalinin isabeti ≥ %50 · F6: 10 coin'in TOPLAM son 50 sonuçlanmış sinyalinin isabeti ≥ %52 (yalnız sinyalden önce sonucu belli olanlar)
# Karar: 2020–23 VE 2024+ dönemlerinin ikisinde de isabet ve net temel sinyalden yüksek, ve sinyallerin ≥ %40'ı kalıyorsa ✅. 2026 ayrıca gösterilir.
import os, glob, numpy as np, pandas as pd
from ortak import *
L = []
def yaz(s=""): print(s, flush=True); L.append(s)
EX = {os.path.basename(p)[7:-4][:-4]: pd.read_pickle(p) for p in glob.glob("art/**/disa24_*USDT.pkl", recursive=True)}
SEC = [s for s in ["ADA", "BNB", "BTC", "DOGE", "DOT", "ETH", "LINK", "NEAR", "OP", "SHIB"] if s in EX]; FEE, D1, H = 0.0002, 1, 24
A0, A24, A26 = (pd.Timestamp(x, tz="UTC") for x in ("2020-01-01", "2024-01-01", "2026-01-01"))
def hz(X): return X.reindex(pd.date_range(X.index[0], X.index[-1], freq="1h", tz="UTC"))
B = hz(EX["BTC"]); rows = []
for s in SEC:
    X = hz(EX[s]); n = len(X); c = X.close.ffill(limit=3).values
    m0 = np.nan_to_num(((X.S24 > 0) & (X.C24 >= X.T10_24)).values).astype(bool) & X.T10_24.notna().values & (np.arange(n) + H + D1 < n)
    for i in events(m0, H):
        t = X.index[i]
        if t < A0 or not (np.isfinite(c[i + D1]) and np.isfinite(c[i + H + D1])): continue
        r = X.iloc[i]; b = B.loc[t] if t in B.index else None
        rows.append(dict(coin=s, t=t, g=c[i + H + D1] / c[i + D1] - 1,
                         f1=bool(r.S8 > 0 and r.C8 >= r.T30_8), f2=bool(r.S72 > 0), f3=bool(b is not None and b.S24 > 0)))
E = pd.DataFrame(rows).sort_values("t").reset_index(drop=True); E["net"] = E.g - 2 * FEE; E["ok"] = E.g > 0; E["bitis"] = E.t + pd.Timedelta(hours=H + D1)
E["f4"] = E.f1 & E.f2
def gecmis_isabet(sub, N, esik, minn):
    out = np.zeros(len(sub), bool); bt, ok = sub.bitis.values, sub.ok.values
    for k, t in enumerate(sub.t.values):
        past = ok[:k][bt[:k] <= t][-N:]
        out[k] = len(past) >= minn and past.mean() >= esik
    return out
E["f5"] = False
for s, g in E.groupby("coin"): E.loc[g.index, "f5"] = gecmis_isabet(g, 20, 0.50, 10)
E["f6"] = gecmis_isabet(E, 50, 0.52, 30)
AD = {"temel": "Temel (filtresiz)", "f1": "F1 · 8 saat de güçlü ↑", "f2": "F2 · 72 saat yönü ↑", "f3": "F3 · BTC 24 saat yönü ↑", "f4": "F4 · 8 s güçlü ↑ ve 72 s ↑",
      "f5": "F5 · coin'in son 20 sinyali ≥ %50", "f6": "F6 · toplam son 50 sinyal ≥ %52"}
DON = {"2020–23": (A0, A24), "2024+": (A24, E.t.max() + pd.Timedelta(hours=1)), "2024–25": (A24, A26), "2026": (A26, E.t.max() + pd.Timedelta(hours=1))}
res = []
for k, ad in AD.items():
    for pn, (a, b) in DON.items():
        x = E[(E.t >= a) & (E.t < b)]; base = len(x); x = x if k == "temel" else x[x[k]]
        if not len(x): continue
        lo, hi = wboot(x.net.values, x.t.values) if len(x) >= 10 else (np.nan, np.nan); wk = (b - a).days / 7
        res.append(dict(filtre=ad, donem=pn, sinyal=len(x), kalan=100 * len(x) / base, haftada=len(x) / wk, isabet=100 * x.ok.mean(), net=100 * x.net.mean(), alt=100 * lo))
R = pd.DataFrame(res)
yaz(f"# 🧹 24 saat sinyaline filtre — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nTemel: 10 coin ({' '.join(SEC)}) · 24 saat 'Çok güçlü ↑' · giriş 1 saat sonra · limit komisyon · net = işlem başı %\n")
for pn in DON: yaz(f"## {pn}\n```\n" + R[R.donem == pn].drop(columns="donem").set_index("filtre").round(2).to_string() + "\n```")
yaz("\n## Karar (önceden sabit: 2020–23 ve 2024+'da isabet VE net temelden yüksek, sinyallerin ≥ %40'ı kalıyor)")
for k, ad in list(AD.items())[1:]:
    p = R.set_index(["filtre", "donem"]); ok = True; parts = []
    for pn in ("2020–23", "2024+"):
        if (ad, pn) not in p.index: ok = False; continue
        f, t_ = p.loc[(ad, pn)], p.loc[(AD["temel"], pn)]; ok &= f.isabet > t_.isabet and f.net > t_.net and f.kalan >= 40
        parts.append(f"{pn}: isabet %{t_.isabet:.1f}→%{f.isabet:.1f}, net {t_.net:+.2f}→{f.net:+.2f}, kalan %{f.kalan:.0f}")
    z = p.loc[(ad, "2026")] if (ad, "2026") in p.index else None; z0 = p.loc[(AD["temel"], "2026")]
    yaz(f"- {'✅' if ok else '❌'} {ad} · " + " · ".join(parts) + (f" · 2026: isabet %{z0.isabet:.1f}→%{z.isabet:.1f}, net {z0.net:+.2f}→{z.net:+.2f}" if z is not None else ""))
open("filtre24_sonuc.md", "w").write("\n".join(L) + "\n")
