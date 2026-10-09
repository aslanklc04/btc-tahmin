# desen2.py — desen.py'de geçen işaretler YENİ BİLGİ mi, yoksa canlıdaki Coinbase primini (💵) mi tekrar ediyor? (yalnız test)
# Not: Coinbase primi = log(Coinbase BTC-USD / Binance BTC-USDT) içinde USDT'nin dolardan sapması da var → USDT primi onunla örtüşebilir.
# ÖNCEDEN KARAR: işaret "yeni bilgi" sayılır ancak — Coinbase primi z < 2 iken (💵 sinyali yokken) gelen olaylarda 2024+ net > 0 ve haftalık blok %5 alt sınır > 0 · 2026 net ≥ 0.
import glob, pickle, numpy as np, pandas as pd
from ortak import *
L = []
def yaz(s=""): print(s, flush=True); L.append(s)
f = lambda p: glob.glob(p, recursive=True)
RAW = {k: v.astype("float64") for k, v in pd.read_pickle(f("art3/**/prim_veri.pkl")[0]).items()}
for v in RAW.values(): v.index = pd.DatetimeIndex(v.index).tz_convert("UTC").as_unit("ns")
UP, BT, U, VP = pickle.load(open(f("art5/**/desen_veri.pkl")[0], "rb"))
zf = lambda p: (p - p.rolling(720, min_periods=168).mean()) / (p.rolling(720, min_periods=168).std() + 1e-12)
B = RAW["BTC"]; ix = B.index
zU = zf(np.log(U).where(lambda x: x.abs() < 0.05)).reindex(ix)
pK = np.log(UP["BTC"].reindex(ix) / (UP["USDT"].reindex(ix) * B.c)); zK = zf(pK.where(pK.abs() < 0.3))
yaz(f"# 🔁 Yeni bilgi mi? USDT primi ve Kore primi vs canlı Coinbase primi — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}")
yaz(f"Aynı saatte birlikte hareket (korelasyon): USDT primi z ↔ BTC Coinbase primi z: {zU.corr(B.z):+.2f} · Kore primi z ↔ Coinbase primi z: {zK.corr(B.z):+.2f} · USDT ↔ Kore: {zU.corr(zK):+.2f}")
LMT = 0.0002; A24, A26 = pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")
def ol(D, isaret, H, maske=None):
    m = (isaret.reindex(D.index) >= 2).fillna(False)
    if maske is not None: m = m & maske.reindex(D.index).fillna(False)
    ev = D.index[events(m.values, H)]; y = D.c.shift(-H) / D.c - 1; return (y.reindex(ev) - 2 * LMT).dropna()
def oz(x):
    out = []
    for dn, a in (("2024+", A24), ("2026", A26)):
        v = x[x.index >= a]; out.append(f"{dn}: {len(v)} · %{100*(v>0).mean():.0f} · {100*v.mean():+.2f} · alt {100*wboot(v.values, v.index.values, 600)[0]:+.2f}" if len(v) >= 8 else f"{dn}: {len(v)}")
    return " | ".join(out)
yaz("\n_olay · isabet · işlem başı net % · haftalık blok %5 alt sınır_\n```")
SON = []
for ad, isaret, H, coins in (("USDT primi z ≥ 2 → BTC", zU, 8, ["BTC"]), ("USDT primi z ≥ 2 → BTC", zU, 24, ["BTC"]), ("USDT primi z ≥ 2 → coin'ler", zU, 8, None), ("USDT primi z ≥ 2 → coin'ler", zU, 24, None),
                             ("Kore primi z ≥ 2 → BTC", zK, 4, ["BTC"])):
    cs = coins or [c for c in RAW if len(RAW[c]) > 3000]
    for alt_ad, kos in (("hepsi", None), ("💵 yokken (kendi Coinbase primi z < 2)", "yok"), ("💵 varken (z ≥ 2)", "var")):
        parca = []
        for c in cs:
            D = RAW[c]; mk = None if kos is None else ((D.z < 2) if kos == "yok" else (D.z >= 2)); parca.append(ol(D, isaret, H, mk))
        x = pd.concat(parca).sort_index(); yaz(f"{ad:28s} {H:>2} s · {alt_ad:38s} {oz(x)}")
        if kos == "yok":
            v = x[x.index >= A24]; v26 = x[x.index >= A26]; ok = len(v) >= 30 and v.mean() > 0 and wboot(v.values, v.index.values, 600)[0] > 0 and (len(v26) < 10 or v26.mean() >= 0)
            SON.append((f"{ad} · {H} s", ok))
yaz("```\n**Önceden yazılı karar (💵 yokken de çalışıyor mu?):** " + " · ".join(f"{a}: {'✅ yeni bilgi' if o else '❌'}" for a, o in SON))
open("desen2_sonuc.md", "w").write("\n".join(L) + "\n")
