# trader_tipleri.py — ALICI/SATICI TİPLERİ (kullanıcının fikri): işlemleri yapan kim? insan mı, bot mu, balina mı?
# Veri: Binance BTCUSDT aggTrades (HER işlem: fiyat, miktar, zaman, alıcı mı satıcı mı saldırgan). Son 6 ay (2026-04 → 2026-09).
# Sınıflar (önceden sabit):
#   🧑 insan-benzeri: tutar tam yuvarlak dolar (10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 2500, 5000, 10000 $) VEYA miktar ≤ 3 ondalık (0,01 BTC gibi)
#   🤖 bot-benzeri: geri kalan (garip, çok ondalıklı miktarlar)
#   küçük (< 1.000 $) · orta (1.000–100.000 $) · 🐋 balina (≥ 100.000 $) · ⚡ aynı milisaniyede ≥ 3 işlem (algoritmik süpürme)
# Her sınıf için saatlik NET AKIŞ = (saldırgan alım − saldırgan satım) / saatin toplam hacmi; ve 7 günlük z-skoru.
# Test: 1 saat ve 4 saat sonraki BTC yönüyle AUC; 6 ay iki yarıya bölünür, iki yarıda da aynı yönde ve |AUC − 0,5| ≥ 0,03 ise "umut verici".
import io, zipfile, time, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from sklearn.metrics import roc_auc_score
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
GUN = pd.date_range("2026-04-01", "2026-09-30", freq="D")
R_USD = np.array([10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 2500, 5000, 10000], float)
def gun(d):
    url = f"https://data.binance.vision/data/spot/daily/aggTrades/BTCUSDT/BTCUSDT-aggTrades-{d:%Y-%m-%d}.zip"
    for _ in range(3):
        try:
            r = requests.get(url, timeout=120); r.raise_for_status(); z = zipfile.ZipFile(io.BytesIO(r.content))
            x = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=[1, 2, 5, 6], names=["p", "q", "ts", "m"], dtype={"p": "float64", "q": "float64", "ts": "int64"})
            break
        except Exception: time.sleep(3); x = None
    if x is None: return None
    ts = x.ts.values.astype("float64"); ts = np.where(ts > 1e14, ts / 1000, ts)               # mikro → mili saniye
    p, q = x.p.values, x.q.values; v = p * q; m = x.m.astype(str).str.lower().isin(["true", "1"]).values; s = np.where(m, -1.0, 1.0)
    step = p * 1e-5; yuv = (np.abs(v[:, None] - R_USD[None, :]) <= step[:, None]).any(axis=1) | (np.abs(q * 1000 - np.round(q * 1000)) < 1e-6)
    msk = pd.Series(ts).map(pd.Series(ts).value_counts()).values >= 3
    h = (pd.to_datetime(ts, unit="ms", utc=True).floor("h") + pd.Timedelta(hours=1))           # saat KAPANIŞI
    D = pd.DataFrame({"h": h, "v": v, "sv": s * v, "Y": yuv, "K": v < 1e3, "O": (v >= 1e3) & (v < 1e5), "B": v >= 1e5, "M": msk})
    out = D.groupby("h").agg(v=("v", "sum"), n=("v", "size"))
    for c in ["Y", "K", "O", "B", "M"]:
        g = D[D[c]].groupby("h"); out[f"pay_{c}"] = g.v.sum().reindex(out.index).fillna(0) / out.v; out[f"net_{c}"] = g.sv.sum().reindex(out.index).fillna(0) / out.v
    g = D[~D.Y].groupby("h"); out["net_N"] = g.sv.sum().reindex(out.index).fillna(0) / out.v
    out["net_hepsi"] = D.groupby("h").sv.sum() / out.v; out["insan_eksi_bot"] = out.net_Y - out.net_N; out["balina_eksi_kucuk"] = out.net_B - out.net_K
    return out
with ThreadPoolExecutor(4) as ex: P = [x for x in ex.map(gun, GUN) if x is not None]
F = pd.concat(P).sort_index(); F = F[~F.index.duplicated()]
yaz(f"# 🧑🤖🐋 Alıcı/satıcı tipleri — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}")
yaz(f"Veri: {len(P)}/{len(GUN)} gün · {int(F.n.sum()):,} işlem · {len(F):,} saat · {time.time()-T0:.0f} sn")
yaz(f"Ortalama pay: 🧑 insan-benzeri %{100*F.pay_Y.mean():.1f} · küçük %{100*F.pay_K.mean():.1f} · 🐋 balina %{100*F.pay_B.mean():.1f} · ⚡ süpürme %{100*F.pay_M.mean():.1f} (hacmin)\n")
o = fetch_1h(pd.Timestamp("2026-03-20", tz="UTC").timestamp() * 1000, time.time() * 1000)
cols = [c for c in F.columns if c.startswith("net_") or c.startswith("pay_") or c in ("insan_eksi_bot", "balina_eksi_kucuk")]
for c in cols: F[c + "_z"] = (F[c] - F[c].rolling(168, min_periods=48).mean().shift(1)) / (F[c].rolling(168, min_periods=48).std().shift(1) + 1e-12)
rows = []; mid = F.index[len(F) // 2]
for H in (1, 4):
    y = np.log(o.close.shift(-H) / o.close).reindex(F.index)
    for c in [c for c in F.columns if c.startswith(("net_", "pay_", "insan_", "balina_"))]:
        x = pd.DataFrame({"f": F[c], "y": y}).dropna(); x = x[x.index.hour % H == 0]
        a1 = x[x.index < mid]; a2 = x[x.index >= mid]
        if len(a1) < 50 or len(a2) < 50: continue
        A1, A2 = roc_auc_score(a1.y > 0, a1.f), roc_auc_score(a2.y > 0, a2.f)
        rows.append(dict(ufuk=f"{H}s", ozellik=c, AUC_1yari=A1, AUC_2yari=A2, umut=bool((A1 - .5) * (A2 - .5) > 0 and min(abs(A1 - .5), abs(A2 - .5)) >= .03)))
R = pd.DataFrame(rows); R["guc"] = (R[["AUC_1yari", "AUC_2yari"]] - .5).abs().min(axis=1)
yaz("## Her tip için: alım/satım baskısı sonraki BTC yönünü gösteriyor mu? (AUC 0,50 = bilgi yok · >0,53 aynı yön · <0,47 ters yön)")
yaz("```\n" + R.sort_values("guc", ascending=False).round(4).to_string(index=False) + "\n```")
U = R[R.umut]; yaz(f"\nUmut verici (iki yarıda da aynı yönde ve |AUC − 0,5| ≥ 0,03): {len(U)} → " + (", ".join(f"{u.ozellik} ({u.ufuk}, {u.AUC_1yari:.3f}/{u.AUC_2yari:.3f})" for u in U.itertuples()) or "yok"))
yaz(f"\nKarşılaştırma: mevcut modelin AUC'si 1s ~0,55 · 4s ~0,555. Rastgele beklenen yanlış pozitif: ~1–2 (çok sayıda özellik denendi).")
open("trader_tipleri_sonuc.md", "w").write("\n".join(L) + "\n")
