# canli_degerlendir.py — 07.10.2026'da Telegram'a gelen canlı sinyallerin sonucu (Binance dakikalık fiyatlarıyla). Saatler UTC (TR = UTC+3).
import time, requests, numpy as np, pandas as pd
from ortak import *
L = []
def yaz(s=""): print(s, flush=True); L.append(s)
U = lambda s: pd.Timestamp(f"2026-10-07 {s}", tz="UTC")
# (coin, sinyal, saat UTC, mesaj fiyatı, {ufuk: (yön, seviye, alt, üst)}, {ufuk: (hedef, stop)}, ana ufuk)
SIG = [
    ("BTC", "🟢 A sınıfı", "02:00", 84392, {1: (1, "Çok güçlü", 83903, 84750), 4: (1, "Zayıf", 83922, 84914), 8: (1, "Zayıf", 83685, 85289)}, {1: (84688, 84095), 4: (84984, 83799), 8: (85229, 83554)}, 4),
    ("DOGE", "⭐ en güçlü", "03:00", 0.0901, {4: (1, "Çok güçlü", None, None), 8: (1, "Çok güçlü", None, None)}, {}, 8),
    ("BTC", "1s Güçlü ↑", "05:00", 84103, {1: (1, "Güçlü", 83836, 84310), 4: (1, "Zayıf", 83694, 84523), 8: (1, "Zayıf", 83462, 84624)}, {1: (84402, 83805), 4: (84700, 83506), 8: (84947, 83259)}, 1),
    ("BTC", "☀️ günlük özet", "06:00", 84333, {1: (-1, "Zayıf", 84099, 84522), 4: (-1, "Zayıf", 83929, 84683), 8: (-1, "Zayıf", 83604, 84893)}, {}, None),
    ("DOGE", "⭐ en güçlü", "12:00", 0.08889, {1: (1, "Çok güçlü", 0.08817, 0.08953), 4: (1, "Çok güçlü", 0.08797, 0.09068), 8: (1, "Çok güçlü", 0.08749, 0.09117)}, {}, 8),
    ("BTC", "🟢 A sınıfı", "13:00", 83492, {1: (1, "Zayıf", 83089, 83865), 4: (1, "Güçlü", 82793, 84249), 8: (1, "Zayıf", 82344, 84473)}, {1: (83764, 83220), 4: (84035, 82949), 8: (84260, 82724)}, 4),
    ("BTC", "1s+4s Güçlü ↑", "14:00", 83192, {1: (1, "Güçlü", 82685, 83814), 4: (1, "Güçlü", 82593, 84040), 8: (1, "Zayıf", 82082, 84148)}, {1: (83459, 82925), 4: (83726, 82658), 8: (83948, 82436)}, 4),
    ("SHIB", "🧪 24s deneme", "14:00", 0.000005390, {24: (1, "Çok güçlü", None, None)}, {}, 24),
    ("BTC", "1s+4s+8s Güçlü ↑", "15:00", 83010, {1: (1, "Güçlü", 82664, 83483), 4: (1, "Güçlü", 82387, 83767), 8: (1, "Güçlü", 81986, 83828)}, {1: (83270, 82751), 4: (83529, 82492), 8: (83744, 82277)}, 4),
    ("ADA", "⭐ en güçlü", "15:00", 0.2532, {1: (1, "Güçlü", 0.2507, 0.2559), 4: (1, "Çok güçlü", 0.2491, 0.2585), 8: (1, "Çok güçlü", 0.2469, 0.2612)}, {}, 8),
]
now = pd.Timestamp.now(tz="UTC"); a = U("01:00").timestamp() * 1000
MN = {}
for c in sorted({s[0] for s in SIG}):
    rows, cur = [], int(a)
    while cur < now.timestamp() * 1000:
        r = requests.get(EP[0], params=dict(symbol=c + "USDT", interval="1m", startTime=cur, limit=1000), timeout=20).json()
        if not r: break
        rows += r; cur = r[-1][0] + 60_000
        if len(r) < 1000: break
    d = pd.DataFrame([x[:5] for x in rows], columns=["t", "o", "h", "l", "c"]).astype(float); d.index = pd.to_datetime(d.t, unit="ms", utc=True) + pd.Timedelta(minutes=1); MN[c] = d
son = {c: (d.index[-1], d.c.iloc[-1]) for c, d in MN.items()}
fm = lambda p: f"{p:,.0f}" if p >= 1000 else (f"{p:.4f}" if p >= 0.01 else f"{p:.9f}")
yaz(f"# 📋 07.10.2026 canlı sinyal değerlendirmesi — {now.tz_convert(DISPLAY_TZ):%d.%m %H:%M} TR\nSon fiyatlar: " + " · ".join(f"{c} {fm(p)}" for c, (t, p) in son.items()) + "\n")
yaz("| Saat (TR) | Coin | Sinyal | Ufuk | Yön · seviye | Mesaj fiyatı | Ufuk sonu fiyatı | Getiri (yön) | Sonuç | %80 aralıkta | Hedef/stop: model → gerçek |\n|---|---|---|---|---|---|---|---|---|---|---|")
OZ = []
for c, ad, sa, p0, U_, B_, ana in SIG:
    t = U(sa); d = MN[c]
    for H, (yon, sev, lo, hi) in U_.items():
        te = t + pd.Timedelta(hours=H)
        if te <= son[c][0]: p1 = float(d.c.loc[:te].iloc[-1]); bitti = True
        else: p1 = son[c][1]; bitti = False
        r = 100 * (p1 / p0 - 1) * yon; ok = r > 0
        ar = ("✅" if lo <= p1 <= hi else "❌") if (lo and bitti) else "—"
        bar = "—"
        if H in B_:
            tp, sl = B_[H]; w = d[(d.index > t) & (d.index <= min(te, son[c][0]))]
            ht = w.index[w.h >= tp]; st_ = w.index[w.l <= sl]
            ilk = ("HEDEF" if (len(ht) and (not len(st_) or ht[0] < st_[0])) else "STOP") if (len(ht) or len(st_)) else ("ikisi de değmedi" if bitti else "bekleniyor")
            bar = f"önce STOP → {ilk}" + (" ✅" if ilk == "STOP" else (" ❌" if ilk == "HEDEF" else ""))
        yaz(f"| {t.tz_convert(DISPLAY_TZ):%H:%M} | {c} | {ad}{' (ana)' if H == ana else ''} | {H}s | {'⬆️' if yon == 1 else '⬇️'} {sev} | {fm(p0)} | {fm(p1)}{'' if bitti else ' (şimdi)'} | {r:+.2f}% | {('✅' if ok else '❌') if bitti else ('devam · ' + ('önde' if ok else 'geride'))} | {ar} | {bar} |")
        OZ.append(dict(coin=c, sinyal=ad, H=H, ana=H == ana, yon=yon, sev=sev, bitti=bitti, ok=ok, r=r))
O = pd.DataFrame(OZ); B = O[O.bitti & (O.yon == 1)]
yaz("\n## Özet (sonuçlanan, yukarı yönlü)")
for lab, x in (("Ana ufuk (her sinyalin kendi süresi)", B[B.ana]), ("Tüm ufuklar", B), ("Çok güçlü", B[B.sev == "Çok güçlü"]), ("Güçlü", B[B.sev == "Güçlü"]), ("Zayıf", B[B.sev == "Zayıf"])):
    if len(x): yaz(f"- {lab}: {int(x.ok.sum())}/{len(x)} tuttu · ortalama getiri %{x.r.mean():+.2f}")
yaz(f"\n_BTC hareketi bugün: {fm(MN['BTC'].c.loc[:U('02:00')].iloc[-1])} (05:00 TR) → {fm(son['BTC'][1])} (şimdi), %{100*(son['BTC'][1]/MN['BTC'].c.loc[:U('02:00')].iloc[-1]-1):+.2f}_")
open("canli_degerlendirme.md", "w").write("\n".join(L) + "\n")
