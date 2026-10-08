# zincir3.py — canlı sürümün kontrolü (zincir_canli.py):
# (1) GİRİŞ SAATİ: araştırma gün d verisiyle d+1 KAPANIŞINDA (TR 03:00) girdi. Canlıda d+1 TR 09:00'da (06:00 UTC) giriliyor; veri geç gelirse TR 15:00. Kurallar bu saatlerde de tutuyor mu?
# (2) Coin Metrics'in son günü (yayın gecikmesi) · (3) 400 günlük kısa veriyle canlı hesap = tam geçmiş hesabı mı · (4) işlem sırasında en kötü ara zarar (kaldıraç için)
import time, requests, numpy as np, pandas as pd
from ortak import *
import zincir_canli as ZC
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
z1 = open("zincir.py").read(); exec(z1[z1.index('CM = "https'):z1.index('M = ["FlowInExNtv"')])         # cm() tam geçmiş
now = pd.Timestamp.now(tz="UTC"); SC = ZC.stabil(); D = {a: cm(a, ["FlowInExNtv", "FlowOutExNtv", "SplyExNtv"]) for a in ("btc", "eth")}
yaz(f"# ⛓️ Arz/talep — canlı sürüm kontrolü ({pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M})\n## Veri ne zaman geliyor\nŞu an {now:%d.%m %H:%M} UTC · Coin Metrics son gün: ETH {D['eth'].index[-1]:%d.%m}, BTC {D['btc'].index[-1]:%d.%m} · DefiLlama son nokta {SC.index[-1]:%d.%m}")
yaz("```\n" + D["eth"].tail(3).to_string() + "\n```")
yaz("## Kısa veri (400 gün) = tam geçmiş mi")
ZF = {}
for a in ("eth", "btc"):
    ZF[a] = ZC.olcu(D[a], SC); zs_ = ZC.olcu(ZC.cm(a), SC); ix = zs_.dropna().index[-200:]
    dif = (ZF[a].reindex(ix) - zs_.reindex(ix)).abs().max()
    of, os_ = ZC.kural_olaylari(ZF[a]), ZC.kural_olaylari(zs_)
    ayni = {k: list(of[k][of[k] >= ix[60]]) == list(os_[k][os_[k] >= ix[60]]) for k in of}
    yaz(f"- {a.upper()}: son 200 günde en büyük z farkı " + ", ".join(f"{k} {v:.4f}" for k, v in dif.items()) + " · son 140 günün olayları aynı: " + ", ".join(f"{k} {'✅' if v else '❌'}" for k, v in ayni.items()))
    yaz(f"  Son gün {ZF[a].dropna().index[-1]:%d.%m}: " + ZC.zsatir(ZF[a].dropna().iloc[-1]))
HP = {a: fetch_1h(pd.Timestamp("2017-09-01", tz="UTC").timestamp() * 1000, now.timestamp() * 1000, sym=f"{a.upper()}USDT") for a in ("eth", "btc")}
yaz(f"\nSaatlik fiyat: ETH {len(HP['eth']):,} · BTC {len(HP['btc']):,} saat · {time.time()-T0:.0f} sn")
A24, A26, LMT = pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC"), 0.0002
GIRIS = {"araştırma: d+1 kapanışı (TR 03:00)": pd.Timedelta(days=2), "CANLI: d+1 TR 09:00": pd.Timedelta(days=1, hours=6), "geç veri: d+1 TR 15:00": pd.Timedelta(days=1, hours=12)}
out, KAR = [], []
for a in ("eth", "btc"):
    o = HP[a]; Z = ZF[a]
    for ad, acik, yon, gun0, kos, _ in ZC.KURAL:
        for HD in sorted({3, 7}):
            ev = Z.index[events(kos(Z).fillna(False).values, HD)]
            for gn, dt in GIRIS.items():
                R = []
                for d in ev:
                    t1 = d + dt; t2 = t1 + pd.Timedelta(days=HD)
                    if t2 > o.index[-1] or t1 not in o.index: continue
                    p1 = o.close.loc[t1]; w = o.loc[(o.index > t1) & (o.index <= t2)]
                    r = yon * (w.close.iloc[-1] / p1 - 1); mae = (w.low.min() / p1 - 1) if yon > 0 else -(w.high.max() / p1 - 1)
                    R.append(dict(t=d, net=r - 2 * LMT, mae=mae))
                E = pd.DataFrame(R)
                if E.empty: continue
                E = E.set_index("t")
                for pn, m in (("≤2023", E.index < A24), ("2024+", E.index >= A24), ("2026", E.index >= A26)):
                    e = E[m]
                    if len(e) < 3: continue
                    lo, _ = wboot(e.net.values, e.index.values) if len(e) >= 8 else (np.nan, np.nan)
                    out.append(dict(coin=a.upper(), kural=ad, gun=HD, giris=gn, donem=pn, olay=len(e), isabet=100 * (e.net > 0).mean(), net=100 * e.net.mean(), alt=100 * lo,
                                    ara_zarar_med=100 * e.mae.median(), ara_zarar_kotu=100 * e.mae.min()))
O = pd.DataFrame(out)
for a in ("ETH", "BTC"):
    yaz(f"\n## {a} — giriş saatine göre (net = işlem başı %, limit komisyon dahil · ara zarar = işlem sürerken gördüğü en kötü an, % — kaldıraç için)\n```\n"
        + O[O.coin == a].drop(columns="coin").set_index(["kural", "gun", "giris", "donem"]).round(2).to_string() + "\n```")
yaz("\n## Karar: canlı ayar (ETH, CANLI giriş, kuralın kendi tutma günü) — 2024+ net > 0 ve alt > 0 → ✅")
for ad, acik, yon, gun0, kos, _ in ZC.KURAL:
    p = O[(O.coin == "ETH") & (O.kural == ad) & (O.gun == gun0) & (O.giris.str.startswith("CANLI"))].set_index("donem")
    if "2024+" not in p.index: yaz(f"- ❓ {ad}: 2024+ olay yok"); continue
    q = p.loc["2024+"]; ok = q.net > 0 and q.alt > 0
    yaz(f"- {'✅' if ok else '❌'} ETH {ad} · {gun0} gün · 2024+ {int(q.olay)} işlem, isabet %{q.isabet:.0f}, net %{q.net:+.2f} (alt %{q.alt:+.2f}) · en kötü ara zarar %{q.ara_zarar_kotu:.1f} (medyan %{q.ara_zarar_med:.1f})"
        + (f" · ≤2023 {int(p.loc['≤2023','olay'])} işlem net %{p.loc['≤2023','net']:+.2f}" if "≤2023" in p.index else "") + (f" · 2026 {int(p.loc['2026','olay'])} işlem net %{p.loc['2026','net']:+.2f}" if "2026" in p.index else ""))
yaz("\n## Kuru çalıştırma (zincir_canli.py, Telegram'sız)")
import os, io, contextlib
os.environ["ZINCIR_KURU"] = "1"; buf = io.StringIO()
with contextlib.redirect_stdout(buf): ZC.calis()
yaz("```\n" + buf.getvalue()[-3500:] + "\n```")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("zincir3_sonuc.md", "w").write("\n".join(L) + "\n")
