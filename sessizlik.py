# sessizlik.py — TEŞHİS (21.10.2026, kullanıcı: "dünden beri sinyal gelmiyor, modelde hata var mı?"; yalnız bilgi, canlıya dokunmaz)
# 22.10.2026 gece: tam denetim
# Canlının kendi önbelleğinden (durum/gecmis.pkl + gecmis_coin.pkl, actions cache) son 72 saat, saat saat:
#   BTC 1/4/8 s yön + güç (Çok güçlü = son 30 günün en güçlü %10'u) · ⭐ · A sınıfı · coin'lerde 4 s Çok güçlü ↑ sayısı (BTC ile aynı saatte = 🤝 adayı)
#   + her coin'in önbelleği bu saate kadar güncel mi (güncel değilse o coin sessizce düşmüş demektir).
# Main kökünden çalışır (main'in ortak.py'si).
import os, pickle, numpy as np, pandas as pd
from ortak import signal_frame, frame_from_S, cz, rpct, DISPLAY_TZ
L = []
def yaz(s=""): print(s, flush=True); L.append(str(s))
NOW = pd.Timestamp.now(tz="UTC"); _e = pd.Series(dtype=float)
yaz(f"# 🩺 Sessizlik teşhisi — {NOW.tz_convert(DISPLAY_TZ):%d.%m.%Y %H:%M}\n")
def cerceve(G):
    return {1: frame_from_S(cz(G["ST"])), 4: signal_frame(G["PG"][4], G["PL"][4], _e, False), 8: signal_frame(G["PG"][8], G["PL"][8], _e, False)}
def durum(F, t):
    o = []
    for H in (1, 4, 8):
        if t not in F[H].index: o.append("?"); continue
        r = F[H].loc[t]; o.append(("↑" if r.S > 0 else "↓") + ("ÇG" if r.C >= r.T10 else ("G" if r.C >= r.T30 else "")))
    return o
GB = pickle.load(open("durum/gecmis.pkl", "rb")); FB = cerceve(GB)
son = FB[4].index[-1]; SA = FB[4].index[FB[4].index > son - pd.Timedelta(hours=72)]
yaz(f"BTC önbelleği son saat: {son.tz_convert(DISPLAY_TZ):%d.%m %H:%M} (şimdi {NOW.tz_convert(DISPLAY_TZ):%d.%m %H:%M}) · model eğitimi {GB.get('created')}")
pct = {H: rpct(FB[H].S.iloc[-900:]) for H in (1, 4, 8)}
GC = pickle.load(open("durum/gecmis_coin.pkl", "rb")); CO = {k: v for k, v in GC.items() if not k.startswith("_") and isinstance(v, dict) and "PG" in v}
yaz(f"coin önbelleği: {len(CO)} coin")
eski = []; U4 = {}
for sym, G in CO.items():
    try:
        F = cerceve(G); ls = F[4].index[-1]
        if ls < son: eski.append(f"{sym} ({ls.tz_convert(DISPLAY_TZ):%d.%m %H:%M})")
        f4 = F[4]; U4[sym] = ((f4.S > 0) & (f4.C >= f4.T10)).reindex(SA).fillna(False)
    except Exception as e: eski.append(f"{sym} (okunamadı: {type(e).__name__})")
yaz(f"BTC'den geride kalan coin önbelleği: {len(eski)}" + (" → " + ", ".join(eski[:40]) if eski else " (hepsi güncel ✅)"))
U = pd.DataFrame(U4)
yaz("\n## Saat saat (Türkiye saati) — BTC 1 s · 4 s · 8 s · A yüzdeliği · 4 s Çok güçlü ↑ coin sayısı\n```")
yaz("saat         BTC 1s  4s    8s    ⭐  A(≥0,85)  coin 4sÇG↑  🤝 adayı (BTC 4sÇG↑ aynı saat)")
n_bu4 = 0
for t in SA:
    d = durum(FB, t); bu4 = d[1] == "↑ÇG"; n_bu4 += bu4; star = bu4 and d[2] == "↑ÇG"
    a = float(np.mean([pct[H].get(t, np.nan) for H in (1, 4, 8)])); nc = int(U.loc[t].sum()) if t in U.index else 0
    ad = ", ".join(sorted(U.columns[U.loc[t].values].str.replace("USDT", "")))[:90] if bu4 and nc else ""
    yaz(f"{t.tz_convert(DISPLAY_TZ):%d.%m %H:%M}  {d[0]:<6} {d[1]:<5} {d[2]:<5} {'⭐' if star else '  '}  {a:5.2f}{' 🟢' if a >= 0.85 else '   '}   {nc:>4}        {ad}")
yaz("```")
yaz(f"\nSon 72 saatte BTC 4 s Çok güçlü ↑: {n_bu4} saat · coin 4 s Çok güçlü ↑ toplam: {int(U.values.sum())} coin-saat")
# karşılaştırma: önceki 30 günde BTC 4 s ÇG↑ sıklığı
f4 = FB[4]; m30 = f4.index > son - pd.Timedelta(days=30); b30 = ((f4.S > 0) & (f4.C >= f4.T10))[m30]
yaz(f"Son 30 günde BTC 4 s Çok güçlü ↑: {int(b30.sum())} saat (günde ~{b30.sum() / 30:.1f}) · en uzun ara: "
    + f"{int(pd.Series(b30.index[b30.values]).diff().max() / pd.Timedelta(hours=1)) if b30.sum() > 1 else 0} saat")
open("sessizlik_sonuc.md", "w").write("\n".join(L) + "\n")
