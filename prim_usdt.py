# prim_usdt.py — DENETİM (19.10.2026, kullanıcı: "Coinbase primini doğru hesapladığımızdan emin miyiz?"; yalnız test)
# Prim = log(Coinbase COIN-USD / Binance COIN-USDT). Binance fiyatı USDT cinsinden → USDT'nin dolardan sapması (USDT-USD ≠ 1) primin İÇİNE giriyor:
# USDT 1,001 $ olursa bütün coin'lerin primi aynı anda düşer ("ABD satıyor" gibi görünür). Düzeltilmiş prim = ham prim − log(Coinbase USDT-USD).
# Ölçülen: (1) ham ↔ düzeltilmiş z ne kadar farklı, ✅/⛔ ne sıklıkla değişiyor (2) coin 4s Çok güçlü ↑ sinyallerinde prim filtresinin ayırma gücü hangisinde iyi.
# ÖNCEDEN YAZILI KARAR: düzeltilmiş prim ancak ÜÇ dönemin (2022-06→2023 · 2024–25 · 2026) ÜÇÜNDE de (a) "z ≥ 0" grubunun isabeti hamdan düşük değil
#   VE (b) "z ≥ 0" ile "z ≤ −1" arasındaki isabet farkı hamdan büyükse önerilir (canlıya ayrıca sorulur). Aksi halde ham prim doğru kabul edilir.
import glob, os, time, requests, numpy as np, pandas as pd
L = []
def yaz(s=""): print(s, flush=True); L.append(str(s))
f = lambda p: glob.glob(p, recursive=True)
RAW = {k: v.astype("float64") for k, v in pd.read_pickle(f("art3/**/prim_veri.pkl")[0]).items()}
for k, v in RAW.items(): v.index = pd.DatetimeIndex(v.index).tz_convert("UTC").as_unit("ns")
EX = {os.path.basename(p)[5:-8]: p for p in f("art1/**/disa_*USDT.pkl")}
def cb(nm, a, b):
    out, cur = [], a
    while cur < b:
        nx = min(cur + pd.Timedelta(hours=300), b)
        for k in range(4):
            try:
                r = requests.get(f"https://api.exchange.coinbase.com/products/{nm}/candles", params=dict(granularity=3600, start=cur.isoformat(), end=nx.isoformat()), timeout=20)
                if r.status_code == 200: out += r.json(); break
            except Exception: pass
            time.sleep(1 + k)
        cur = nx; time.sleep(0.15)
    d = pd.DataFrame(out, columns=["t", "low", "high", "open", "close", "volume"]).drop_duplicates("t")
    return pd.Series(d.close.values.astype(float), index=pd.to_datetime(d.t, unit="s", utc=True) + pd.Timedelta(hours=1)).sort_index()
U = cb("USDT-USD", pd.Timestamp("2022-04-01", tz="UTC"), pd.Timestamp.now(tz="UTC").floor("h")); U.index = U.index.as_unit("ns")
lu = np.log(U).reindex(pd.date_range(U.index[0], U.index[-1], freq="1h", tz="UTC")).ffill(limit=3)
yaz(f"# 💵 Coinbase primi doğru mu? USDT etkisi — {pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M}\nUSDT-USD (Coinbase) {len(U):,} saat · ortalama {U.mean():.5f} $ · en düşük {U.min():.4f} · en yüksek {U.max():.4f}\n")
zf = lambda p: (p - p.rolling(720, min_periods=168).mean()) / (p.rolling(720, min_periods=168).std() + 1e-12)
Z = {}
for nm, d in RAW.items():
    p = d.bp / 1e4; padj = p - lu.reindex(p.index).values
    Z[nm] = pd.DataFrame({"z": d.z, "za": zf(padj)})
B = Z.get("BTC")
yaz("## 1) Ham ↔ USDT-düzeltilmiş z (2024+)\n```")
rows = []
for nm, d in Z.items():
    x = d[d.index >= pd.Timestamp("2024-01-01", tz="UTC")].dropna()
    if len(x) < 2000: continue
    rows.append(dict(coin=nm, kor=round(x.z.corr(x.za), 3), ort_fark=round((x.z - x.za).abs().mean(), 2), isaret_degisir=round(100 * ((x.z >= 0) != (x.za >= 0)).mean(), 1),
                     dur_degisir=round(100 * ((x.z <= -1) != (x.za <= -1)).mean(), 1)))
R = pd.DataFrame(rows).sort_values("kor"); yaz(R.to_string(index=False)); yaz("```")
yaz(f"- medyan korelasyon {R.kor.median():.3f} · ✅/⛔ (z ≥ 0) değişen saat medyanı %{R.isaret_degisir.median():.1f} · ⛔ (z ≤ −1) değişen %{R.dur_degisir.median():.1f}")
# ortak hareket: aynı saatte coin'lerin çoğu birlikte ⛔ mi (USDT etkisinin izi)
W = pd.DataFrame({nm: d.z for nm, d in Z.items()}); Wa = pd.DataFrame({nm: d.za for nm, d in Z.items()})
W, Wa = W[W.index >= pd.Timestamp("2024-01-01", tz="UTC")], Wa[Wa.index >= pd.Timestamp("2024-01-01", tz="UTC")]
yaz(f"- coin'lerin %70'inden fazlası AYNI ANDA ⛔ olan saat: ham %{100 * ((W <= -1).mean(axis=1) > 0.7).mean():.1f} · düzeltilmiş %{100 * ((Wa <= -1).mean(axis=1) > 0.7).mean():.1f}")
yaz(f"- son 7 gün ortalama z (tüm coin'ler): ham {W.iloc[-168:].mean().mean():+.2f} · düzeltilmiş {Wa.iloc[-168:].mean().mean():+.2f} · BTC ham {W.BTC.iloc[-168:].mean():+.2f} / düzeltilmiş {Wa.BTC.iloc[-168:].mean():+.2f} · ETH ham {W.ETH.iloc[-168:].mean():+.2f} / düzeltilmiş {Wa.ETH.iloc[-168:].mean():+.2f}")
# 2) filtrenin ayırma gücü: coin 4s Çok güçlü ↑ (u4) + ⭐ + A, 4 saat sonra
from ortak import events
EV = []
for nm, p in EX.items():
    if nm not in Z: continue
    X = pd.read_pickle(p); X.index = pd.DatetimeIndex(X.index).tz_convert("UTC").as_unit("ns")
    m = (X.u4.fillna(False) | X.star.fillna(False) | X.acls.fillna(False)).values.astype(bool) & X.y4.notna().values; ev = events(m, 4); t = X.index[ev]
    EV.append(pd.DataFrame({"nm": nm, "t": t, "ok": X.y4.values[ev] > 0, "z": Z[nm].z.reindex(t).values, "za": Z[nm].za.reindex(t).values}))
E = pd.concat(EV).dropna(subset=["z", "za"]); tt = pd.DatetimeIndex(E.t)
DON = (("2022-06→2023", (tt >= pd.Timestamp("2022-06-01", tz="UTC")) & (tt < pd.Timestamp("2024-01-01", tz="UTC"))), ("2024–25", (tt >= pd.Timestamp("2024-01-01", tz="UTC")) & (tt < pd.Timestamp("2026-01-01", tz="UTC"))), ("2026", tt >= pd.Timestamp("2026-01-01", tz="UTC")))
yaz(f"\n## 2) Prim filtresi ne kadar iyi ayırıyor? ({E.nm.nunique()} coin, coin 4s ÇG ↑ / ⭐ / A sinyalleri, 4 saat sonra isabet)\n```")
ok = {"ham": [], "düz": []}
for dn, dm in DON:
    x = E[dm]; s = []
    for ad, c in (("ham", "z"), ("düz", "za")):
        a, b_ = x[x[c] >= 0], x[x[c] <= -1]; ha, hb = 100 * a.ok.mean(), 100 * b_.ok.mean(); s.append(f"{ad}: ✅ %{ha:.1f} (n{len(a)}) · ⛔ %{hb:.1f} (n{len(b_)}) · fark {ha - hb:+.1f}"); ok[ad].append((ha, ha - hb))
    yaz(f"{dn:13s} " + "  ||  ".join(s))
yaz("```")
gec = all(ok["düz"][i][0] >= ok["ham"][i][0] and ok["düz"][i][1] > ok["ham"][i][1] for i in range(3))
yaz(f"\n**Karar (önceden yazılı):** {'✅ USDT-düzeltilmiş prim üç dönemde de daha iyi → canlıya önerilir (sorulacak)' if gec else '❌ düzeltme üç dönemde de daha iyi değil → ham prim kalır'}")
open("prim_usdt_sonuc.md", "w").write("\n".join(L) + "\n")
