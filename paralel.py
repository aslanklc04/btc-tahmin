# paralel.py — BINANCE ve COINBASE'TE AYNI ANDA (ya da birkaç dk arayla) BENZER BÜYÜKLÜKTE ALIM / SATIŞ (kullanıcı fikri 12.10.2026; yalnız test).
# Fikir: büyük bir oyuncu emrini iki borsaya bölerse iki borsada aynı dakikalarda olağandışı hacim + aynı yönde fiyat hareketi görülür.
# Veri: paralel_veri.py (5 dk çubuk). Hacim z = log(5 dk $ hacmi) son 7 güne göre. Yön: iki borsada da 5 dk getiri aynı işaretli + Binance agresif alıcı payı ≥ %60 (satışta ≤ %40).
# "Birkaç dk arayla": son 10 dakikada (2 çubuk) iki borsada da z ≥ 3. "Benzer büyüklük": normalin ÜSTÜNDEKİ $ hacimleri arasındaki oran 0,5–2.
# Kurallar: P1 paralel ALIM (benzer büyüklük) → AL · P2 paralel SATIŞ (benzer büyüklük) → SAT · P3/P4 aynısı büyüklük şartı olmadan.
#   Karşılaştırma (bilgi): yalnız Binance'te sıçrama / yalnız Coinbase'te sıçrama.
# ÖNCEDEN YAZILI KARAR (sonuçlar görülmeden): tutma süresi (1 / 4 / 8 s) yalnız 2022-06→2023'ten seçilir; üç dönemde (2022-06→2023 · 2024+ · 2026) ana set ölçütü
#   (isabet ≥ %55,9 · %58,6 · %59,1 VE net ≥ +0,30 · +0,647 · +0,589; en az 30 / 30 / 10) → yeni sinyal adayı.
#   PLASEBO (eşzamanlılık gerçekten önemli mi?): Coinbase serisi 1 saat ve 1 gün kaydırılınca aynı kural geçmemeli; geçerse "paralel" bir şey katmıyor demektir.
import glob, os, time, numpy as np, pandas as pd
from ortak import events
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
D = {os.path.basename(p)[8:-4]: pd.read_pickle(p).astype("float64") for p in glob.glob("**/paralel_*.pkl", recursive=True)}
P0, A24, A26 = (pd.Timestamp(x, tz="UTC") for x in ("2022-06-01", "2024-01-01", "2026-01-01"))
DNS = (("2022-06→2023", P0, A24), ("2024+", A24, None), ("2026", A26, None)); MINS = {"2022-06→2023": 30, "2024+": 30, "2026": 10}
BEN = {"2022-06→2023": (55.9, 0.30), "2024+": (58.6, 0.647), "2026": (59.1, 0.589)}
W = 2016
def zv(q): l = np.log(q.where(q > 0)); return (l - l.rolling(W, min_periods=288).mean()) / (l.rolling(W, min_periods=288).std() + 1e-12)
def kosul(X, kay=0):
    cb = X[["cb_o", "cb_c", "cb_q"]].shift(kay) if kay else X[["cb_o", "cb_c", "cb_q"]]
    zb, zc = zv(X.bn_q), zv(cb.cb_q); rb, rc = X.bn_c / X.bn_o - 1, cb.cb_c / cb.cb_o - 1; tb = X.bn_tbq / X.bn_q
    exb = (X.bn_q - X.bn_q.rolling(W, min_periods=288).median()).rolling(2).sum(); exc = (cb.cb_q - cb.cb_q.rolling(W, min_periods=288).median()).rolling(2).sum()
    zb2, zc2 = zb.rolling(2).max(), zc.rolling(2).max(); rb2, rc2 = rb.rolling(2).sum(), rc.rolling(2).sum(); tb2 = X.bn_tbq.rolling(2).sum() / X.bn_q.rolling(2).sum()
    oran = exc / exb; ben = (oran >= 0.5) & (oran <= 2)
    al = (zb2 >= 3) & (zc2 >= 3) & (rb2 > 0) & (rc2 > 0) & (tb2 >= 0.6); sat = (zb2 >= 3) & (zc2 >= 3) & (rb2 < 0) & (rc2 < 0) & (tb2 <= 0.4)
    return {"P1 paralel ALIM, benzer büyüklük": (al & ben, 1), "P2 paralel SATIŞ, benzer büyüklük": (sat & ben, -1),
            "P3 paralel ALIM (büyüklük şartsız)": (al, 1), "P4 paralel SATIŞ (büyüklük şartsız)": (sat, -1),
            "K1 yalnız Binance'te alım sıçraması": ((zb2 >= 3) & (zc2 < 1.5) & (rb2 > 0) & (tb2 >= 0.6), 1), "K2 yalnız Coinbase'te alım sıçraması": ((zc2 >= 3) & (zb2 < 1.5) & (rc2 > 0), 1)}
def olc(ad, H, kay=0):
    rows = []
    for nm, X in D.items():
        m, yon = kosul(X, kay)[ad]; m = m.fillna(False).values.astype(bool); c = X.bn_c.values; n = len(X); m &= (np.arange(n) + H < n) & np.isfinite(c)
        ev = events(m, H); r = yon * (c[np.minimum(ev + H, n - 1)] / c[ev] - 1) - 0.0004
        rows.append(pd.DataFrame({"t": X.index[ev], "net": r}))
    E = pd.concat(rows); E = E[np.isfinite(E.net)]; E["ok"] = E.net > 0; o = {}
    for dn, a, b in DNS:
        x = E[(E.t >= a) & ((E.t < b) if b is not None else True)]; hf = ((b or E.t.max()) - a).days / 7
        o[dn] = (len(x), len(x) / max(hf, 1), 100 * x.ok.mean() if len(x) else np.nan, 100 * x.net.mean() if len(x) else np.nan)
    return o
def yz(o): return " | ".join(f"{o[dn][1]:5.1f}/hf · %{o[dn][2]:4.1f} · {o[dn][3]:+.2f} ({o[dn][0]})" if o[dn][0] >= 5 else f"{o[dn][0]:4d} az" for dn, _, _ in DNS)
HS = {"1 s": 12, "4 s": 48, "8 s": 96}
yaz(f"# 🔀 Binance + Coinbase'te paralel büyük alım/satış — {pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M}\nCoin: {', '.join(sorted(D))} · {time.time()-T0:.0f} sn\n"
    "_haftada · isabet · işlem başı net % (sinyal) — 2022-06→2023 | 2024+ | 2026 · ← = 2022–23'te seçilen süre_\n```")
GEC = []
for ad in kosul(next(iter(D.values()))):
    R = {h: olc(ad, H) for h, H in HS.items()}; hs = max(R, key=lambda h: R[h]["2022-06→2023"][3] if np.isfinite(R[h]["2022-06→2023"][3]) else -9)
    for h in HS: yaz(f"{ad[:40]:40s} {h}{' ←' if h == hs else '  '} {yz(R[h])}")
    if ad[0] == "P" and all(R[hs][dn][0] >= MINS[dn] and R[hs][dn][2] >= BEN[dn][0] and R[hs][dn][3] >= BEN[dn][1] for dn in MINS):
        pl = [olc(ad, HS[hs], k) for k in (12, 288)]
        pg = any(all(p[dn][0] >= MINS[dn] and p[dn][2] >= BEN[dn][0] and p[dn][3] >= BEN[dn][1] for dn in MINS) for p in pl)
        yaz(f"{'':40s}   plasebo Coinbase +1 s: {yz(pl[0])}\n{'':40s}   plasebo Coinbase +1 g: {yz(pl[1])}"); GEC.append((ad, hs, not pg))
yaz("```\n## Önceden yazılı karar")
yaz("\n".join(f"- {'✅ KABUL' if ok else '❌ plasebo da geçti (eşzamanlılık bir şey katmıyor)'}: {ad} ({hs})" for ad, hs, ok in GEC) if GEC else "- Hiçbir paralel kural ana set ölçütünü geçmedi → eklenmez")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("paralel_sonuc.md", "w").write("\n".join(L) + "\n")
