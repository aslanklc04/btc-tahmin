# capraz.py — COİN'LER ARASI PRİM (kullanıcı fikri: "SHIB'e DOGE'ye göre normalden fazla prim veriliyorsa ne olur?")
# (1) ÇAPRAZ PRİM (Coinbase primine en yakın): Binance'te coin'in doğrudan BTC (ve ETH) çifti ile USDT üzerinden ima edilen fiyatı karşılaştırılır.
#     prim = log( VWAP(XXX/BTC) × VWAP(BTC/USDT) / VWAP(XXX/USDT) )  — aynı saatin hacim ağırlıklı fiyatları (son işlem fiyatı gürültülü olduğu için).
#     Artı = BTC sahipleri bu coin için USDT alıcılarından fazla ödüyor (BTC'den bu coin'e akış). z: son 720 saate göre.
#     Önceden sabit: z ≥ 2 → coin'i AL · z ≤ −2 → coin'i SAT · giriş 1 saat sonra · 4 / 8 / 24 saat tut · limit komisyon %0,02 × 2.
# (2) GÖRELİ FİYAT: canlı coin'lerin her ikilisi için oran = log(A / B) (günlük). 7 günlük oran değişimi z (90 gün) ≥ 2 → A, B'ye göre olağandışı değerlenmiş.
#     Soru: sonraki 1 / 3 / 7 günde fark kapanıyor mu (geri dönüş) yoksa sürüyor mu? İşlem: "A kısa + B uzun" (geri dönüş) — yön seçim döneminden.
# Seçim ≤2023 · doğrulama 2024+ · 2026 ayrıca · ✅: seçimde net > 0, doğrulamada net > 0 ve %90 alt sınır > 0. Plasebo (sinyal kaydırılmış) ile şans payı.
import time, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
S = requests.Session()
def kl(sym, interval, start):
    rows, cur, end = [], int(pd.Timestamp(start, tz="UTC").timestamp() * 1000), int(time.time() * 1000)
    while cur < end:
        for k in range(4):
            try:
                r = S.get(EP[0], params=dict(symbol=sym, interval=interval, startTime=cur, limit=1000), timeout=30)
                if r.status_code == 200: dt = r.json(); break
                if r.status_code in (400, 404): return sym, None
            except Exception: pass
            time.sleep(1 + k)
        else: return sym, None
        if not dt: break
        rows += dt; cur = dt[-1][0] + (3_600_000 if interval == "1h" else 86_400_000)
        if len(dt) < 1000: break
    if not rows: return sym, None
    d = pd.DataFrame([x[:8] for x in rows], columns=["t", "o", "h", "l", "c", "v", "ct", "q"]).astype(float)
    d.index = pd.to_datetime(d.t, unit="ms", utc=True) + (pd.Timedelta(hours=1) if interval == "1h" else pd.Timedelta(0))
    d["vwap"] = np.where(d.v > 0, d.q / d.v, np.nan); return sym, d[["c", "v", "q", "vwap"]]
INFO = S.get("https://data-api.binance.vision/api/v3/exchangeInfo", timeout=60).json()
TR = {s["symbol"]: s for s in INFO["symbols"] if s["status"] == "TRADING"}
CANLI = [l.strip().replace("USDT", "") for l in open("durum/coin_listesi.txt") if l.strip()]
ADAY = list(dict.fromkeys(CANLI + "BTC ETH SOL XRP BNB ADA DOGE LINK DOT LTC AVAX NEAR TRX ATOM BCH UNI FIL".split()))
CAP = [(b, q) for b in ADAY for q in ("BTC", "ETH") if b != q and f"{b}{q}" in TR and f"{b}USDT" in TR]
yaz(f"# 🔀 Coin'ler arası prim — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nÇapraz çiftler ({len(CAP)}): " + ", ".join(f"{b}/{q}" for b, q in CAP))
semb = sorted({f"{b}{q}" for b, q in CAP} | {f"{b}USDT" for b, q in CAP} | {"BTCUSDT", "ETHUSDT"})
with ThreadPoolExecutor(8) as ex: HV = {k: v for k, v in ex.map(lambda s: kl(s, "1h", "2019-06-01"), semb) if v is not None}
yaz(f"Saatlik veri: {len(HV)} sembol · {time.time()-T0:.0f} sn\n")
A24, A26, LMT = pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC"), 0.0002
DON = (("≤2023", lambda i: i < A24), ("2024+", lambda i: i >= A24), ("2026", lambda i: i >= A26))
def ozet(net, reps=800):
    out = {}
    for pn, f in DON:
        x = net[f(net.index)]; out[pn] = (len(x), 100 * (x > 0).mean() if len(x) else np.nan, 100 * x.mean() if len(x) else np.nan, 100 * wboot(x.values, x.index.values, reps)[0] if len(x) >= 8 else np.nan)
    return out
def fmt(o): return " · ".join(("—" if not np.isfinite(v) else (f"{v:.0f}" if i < 2 else f"{v:+.2f}")) for i, v in enumerate(o))
def gecti(o): s, d = o["≤2023"], o["2024+"]; return bool(s[0] >= 10 and s[2] > 0 and d[0] >= 10 and d[2] > 0 and d[3] > 0)
# ---- (1) çapraz prim ----
rows, rng, pl_ok, pl_n, havuz = [], np.random.default_rng(0), 0, 0, {}
for b, q in CAP:
    X, U, Q = HV.get(f"{b}{q}"), HV.get(f"{b}USDT"), HV.get(f"{q}USDT")
    if X is None or U is None or Q is None: continue
    ix = U.index.intersection(X.index).intersection(Q.index)
    if len(ix) < 5000: continue
    pr = np.log(X.vwap.reindex(ix) * Q.vwap.reindex(ix) / U.vwap.reindex(ix)); pr = pr[(X.v.reindex(ix) > 0)]
    z = ((pr - pr.rolling(720, min_periods=168).mean()) / (pr.rolling(720, min_periods=168).std() + 1e-12)).reindex(U.index)
    c = U.c
    for sk, m, yon in (("z ≥ 2 → AL", z >= 2, 1), ("z ≤ −2 → SAT", z <= -2, -1)):
        mv = m.fillna(False).values
        for H in (4, 8, 24):
            y = c.shift(-(1 + H)) / c.shift(-1) - 1; ev = c.index[events(mv, H)]; net = (yon * y.reindex(ev) - 2 * LMT).dropna(); o = ozet(net)
            havuz.setdefault((sk, H), []).append(net)
            rows.append(dict(cift=f"{b}/{q}", sinyal=sk, saat=H, **{pn: fmt(o[pn]) for pn, _ in DON}, ok=gecti(o)))
            for _ in range(5):
                sh = int(rng.integers(500, len(mv) - 500)); ev2 = c.index[events(np.roll(mv, sh), H)]; po = ozet((yon * y.reindex(ev2) - 2 * LMT).dropna(), reps=200)
                if po["≤2023"][0] >= 10: pl_n += 1; pl_ok += gecti(po)
R1 = pd.DataFrame(rows)
yaz(f"## 1. Çapraz prim (BTC / ETH ile doğrudan çift vs USDT üzerinden)\nToplam {len(R1)} deneme · ✅ geçen **{int(R1.ok.sum()) if len(R1) else 0}** · plasebo geçme oranı %{100*pl_ok/max(1,pl_n):.1f} → tesadüfen ≈ {pl_ok/max(1,pl_n)*len(R1):.1f}")
yaz("### Havuz (tüm çiftler birlikte) · işlem · isabet % · işlem başı net % · alt sınır %\n```\n" + pd.DataFrame([dict(sinyal=k[0], saat=k[1], **{pn: fmt(o[pn]) for pn, _ in DON}) for k, v in havuz.items() for o in [ozet(pd.concat(v).sort_index())]]).to_string(index=False) + "\n```")
yaz("### ✅ Geçenler\n```\n" + (R1[R1.ok].drop(columns="ok").to_string(index=False) if len(R1) and R1.ok.any() else "(yok)") + "\n```")
yaz("### Tümü\n```\n" + (R1.drop(columns="ok").to_string(index=False) if len(R1) else "") + "\n```")
# ---- (2) göreli fiyat (günlük) ----
with ThreadPoolExecutor(8) as ex: DV = {k[:-4]: v.c for k, v in ex.map(lambda s: kl(s, "1d", "2019-06-01"), [f"{c}USDT" for c in dict.fromkeys(["BTC"] + CANLI)]) if v is not None}
yaz(f"\n## 2. Göreli fiyat: bir coin diğerine göre 7 günde olağandışı değerlendiğinde (z ≥ 2) sonra ne oluyor? · {len(DV)} coin, {len(DV)*(len(DV)-1)//2} ikili")
rows2, havuz2, pl2_ok, pl2_n = [], {}, 0, 0
nm = sorted(DV)
for i in range(len(nm)):
    for j in range(i + 1, len(nm)):
        a, b = nm[i], nm[j]; ix = DV[a].index.intersection(DV[b].index)
        if len(ix) < 500: continue
        lr = np.log(DV[a].reindex(ix) / DV[b].reindex(ix)); d7 = lr.diff(7); zz = (d7 - d7.rolling(90, min_periods=40).mean()) / (d7.rolling(90, min_periods=40).std() + 1e-12)
        for HD in (1, 3, 7):
            fwd = lr.shift(-HD) - lr                                                                        # A'nın B'ye göre sonraki HD gün getirisi (log)
            for sk, m, isaret in ((f"{a} > {b} (z ≥ 2)", zz >= 2, 1), (f"{b} > {a} (z ≤ −2)", zz <= -2, -1)):
                mv = m.fillna(False).values; ev = ix[events(mv, HD)]
                g = (-isaret * fwd.reindex(ev)).dropna()                                                     # geri dönüş işlemi: değerlenen kısa, diğeri uzun
                e1 = g[g.index < A24]
                if len(e1) < 10: continue
                yon = 1 if e1.mean() > 0 else -1; net = yon * g - 4 * LMT; o = ozet(net)                      # iki bacak → 4 komisyon
                havuz2.setdefault((("geri dönüş" if yon > 0 else "devam"), HD), []).append(net)
                rows2.append(dict(ikili=sk, gun=HD, yon="geri dönüş" if yon > 0 else "devam", **{pn: fmt(o[pn]) for pn, _ in DON}, ok=gecti(o)))
                for _ in range(3):
                    sh = int(rng.integers(60, len(mv) - 60)); ev2 = ix[events(np.roll(mv, sh), HD)]; g2 = (-isaret * fwd.reindex(ev2)).dropna()
                    e2 = g2[g2.index < A24]
                    if len(e2) < 10: continue
                    po = ozet((1 if e2.mean() > 0 else -1) * g2 - 4 * LMT, reps=200); pl2_n += 1; pl2_ok += gecti(po)
R2 = pd.DataFrame(rows2)
yaz(f"Toplam {len(R2)} deneme · ✅ geçen **{int(R2.ok.sum()) if len(R2) else 0}** · plasebo geçme oranı %{100*pl2_ok/max(1,pl2_n):.1f} → tesadüfen ≈ {pl2_ok/max(1,pl2_n)*len(R2):.1f}")
yaz("### Yön dağılımı (≤2023'te hangisi çıktı) ve havuz\n```\n" + pd.DataFrame([dict(yon=k[0], gun=k[1], cift_sayisi=len(v), **{pn: fmt(o[pn]) for pn, _ in DON}) for k, v in sorted(havuz2.items()) for o in [ozet(pd.concat(v).sort_index())]]).to_string(index=False) + "\n```")
yaz("### ✅ Geçenler\n```\n" + (R2[R2.ok].drop(columns="ok").to_string(index=False) if len(R2) and R2.ok.any() else "(yok)") + "\n```")
if "SHIB" in DV and "DOGE" in DV:
    yaz("### Örnek: SHIB ↔ DOGE\n```\n" + R2[R2.ikili.str.contains("SHIB") & R2.ikili.str.contains("DOGE")].drop(columns="ok").to_string(index=False) + "\n```")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("capraz_sonuc.md", "w").write("\n".join(L) + "\n")
