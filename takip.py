# takip.py — BÜYÜK COİN YÜKSELİNCE BAŞKA BİR COİN SONRADAN (1–24 SAAT) YÜKSELİYOR / DÜŞÜYOR MU? (kullanıcı fikri, yalnız test, 12.10.2026)
# Daha önce: zit.py / zit2.py GÜNLÜK veride "zıt coin" aradı → normal coin'ler arasında zıt yok, gecikmeli zıtlar rastgeleden iyi değil (%4,9 vs %5,2).
# Bu test SAATLİK ve hem "takipçi" (sonradan yükselen) hem "zıt" (sonradan düşen) coin'i arar.
# Liderler: BTC · ETH · SOL · BNB ve "büyükler birlikte" (4'ünden en az 3'ü aynı anda z ≥ 1,5). Lider olayı: son k saatlik getiri z ≥ 2 (k = 1 ve 4; z = getiri / (saatlik oynaklık × √k)).
# Evren: Binance USDT spot, 24 saatlik hacme göre en büyük ~160 coin (stabil, altın, sarılı hariç), saatlik mum 2022-01'den. Maliyet %0,04 (limit, iki bacak).
# Tutma: 1 · 2 · 4 · 8 · 24 saat (24 = ertesi gün). Dönemler: SEÇİM 2022-06→2023 · DOĞRULAMA 2024+ · 2026.
# ÖNCEDEN YAZILI KARAR (12.10.2026, sonuçlar görülmeden):
#   A) GERİDE KALANLAR SEPETİ (coin seçimi yok): lider olayında son k saatte henüz hareket etmemiş (kendi z ≤ 0,5) lider dışı coin'lerin eşit ağırlıklı sepeti AL.
#      En iyi (lider, k, süre) yalnız SEÇİM döneminden (işlem başı net) seçilir. Kabul: seçimde isabet ≥ %55,9 ve net ≥ +0,30; 2024+ isabet ≥ %58,6 ve net ≥ +0,647
#      ve haftalık blok bootstrap %5 alt sınırı > 0; 2026 isabet ≥ %59,1 ve net ≥ +0,589 (en az 30 / 30 / 10 olay). (= canlı ✅ ana sinyal ölçütü)
#   B) COİN'E ÖZEL TAKİPÇİ / ZIT: her (lider, k, süre, yön AL/SAT) için SEÇİM döneminde en iyi 3 coin (≥ 20 olay, t ≥ 2) seçilir.
#      Kabul: (i) seçilenlerin 2024+'da "geçme" oranı (net > 0 ve bootstrap alt sınırı > 0) rastgele coin'lerin geçme oranının ≥ 2 katı ve ≥ %20,
#             (ii) seçilenlerin toplu 2024+ ve 2026 sonucu ana sinyal ölçütünü geçer. İkisi de yoksa "takipçi / zıt coin yok" denir.
import time, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import events, wboot, DISPLAY_TZ
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
STAB = set("USDC USDT DAI TUSD USDP PYUSD FDUSD EUR GBP EURI AEUR USDS USDE USD1 RLUSD PAX BUSD WBTC WBETH BETH CBETH PAXG XAUT BFUSD XUSD TRY BRL".split())
TK = requests.get("https://data-api.binance.vision/api/v3/ticker/24hr", timeout=60).json()
HAC = pd.Series({t["symbol"][:-4]: float(t["quoteVolume"]) for t in TK if t["symbol"].endswith("USDT") and t["symbol"][:-4] not in STAB
                 and not t["symbol"][:-4].endswith(("UP", "DOWN", "BULL", "BEAR"))}).sort_values(ascending=False)
LID = ["BTC", "ETH", "SOL", "BNB"]; EVREN = list(dict.fromkeys(LID + list(HAC.index[:160])))
def kline(nm):
    rows, cur, end = [], int(pd.Timestamp("2022-01-01", tz="UTC").timestamp() * 1000), time.time() * 1000
    while cur < end:
        dt = None
        for k in range(6):
            try: r = requests.get("https://data-api.binance.vision/api/v3/klines", params=dict(symbol=nm + "USDT", interval="1h", startTime=cur, limit=1000), timeout=20); r.raise_for_status(); dt = r.json(); break
            except Exception: time.sleep(2 + 2 * k)
        if not dt: break
        rows += dt; cur = dt[-1][0] + 3_600_000
        if len(dt) < 1000: break
    if not rows: return nm, None
    d = pd.DataFrame([x[:5] for x in rows], columns=["t", "o", "h", "l", "c"]).astype(float)
    return nm, pd.Series(d.c.values, index=pd.DatetimeIndex(pd.to_datetime(d.t, unit="ms", utc=True) + pd.Timedelta(hours=1)).as_unit("ns"))
with ThreadPoolExecutor(10) as ex: KL = {k: v for k, v in ex.map(kline, EVREN) if v is not None and len(v) >= 3000}
C = pd.DataFrame(KL).sort_index(); C = C[~C.index.duplicated()]; C = C.reindex(pd.date_range(C.index[0], C.index[-1], freq="1h")).ffill(limit=3)
yaz(f"# 🔗 Büyük coin yükselince sonradan yükselen / düşen coin var mı? — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n"
    f"Evren: {C.shape[1]} coin (Binance USDT, hacme göre) · {C.index[0]:%Y-%m} → {C.index[-1]:%Y-%m-%d} · {time.time()-T0:.0f} sn\n")
LR = np.log(C); SG = LR.diff().rolling(720, min_periods=168).std()
def zk(k): return (LR - LR.shift(k)) / (SG * np.sqrt(k))
Z = {1: zk(1), 4: zk(4)}
P0, A24, A26 = (pd.Timestamp(x, tz="UTC") for x in ("2022-06-01", "2024-01-01", "2026-01-01")); KOM = 0.0004
IX = C.index; DON = (("seçim 2022-06→2023", (IX >= P0) & (IX < A24)), ("2024+", IX >= A24), ("2026", IX >= A26))
HAF = {"seçim 2022-06→2023": (A24 - P0).days / 7, "2024+": (IX[-1] - A24).days / 7, "2026": (IX[-1] - A26).days / 7}
BEN = {"seçim 2022-06→2023": (55.9, 0.30), "2024+": (58.6, 0.647), "2026": (59.1, 0.589)}; MIN = {"seçim 2022-06→2023": 30, "2024+": 30, "2026": 10}
DIGER = [c for c in C.columns if c not in LID]
def lider(ad, k):
    if ad == "büyükler birlikte": return ((Z[k][LID] >= 1.5).sum(axis=1) >= 3).values
    return (Z[k][ad] >= 2).fillna(False).values
LIDERLER = LID + ["büyükler birlikte"]; HS = (1, 2, 4, 8, 24)
FWD = {h: (C.shift(-h) / C - 1) for h in HS}
def ozet(v, t):
    o = {}
    for dn, md in DON:
        m = md[t] & np.isfinite(v); x = v[m]
        o[dn] = (len(x), 100 * (x > 0).mean() if len(x) else np.nan, 100 * x.mean() if len(x) else np.nan, len(x) / HAF[dn])
    return o
def sat(o): return " | ".join(f"{o[dn][3]:4.1f}/hf · %{o[dn][1]:4.1f} · {o[dn][2]:+.2f}" if o[dn][0] >= 5 else f"{o[dn][0]:4d} az            " for dn, _ in DON)
# ---------------- A) geride kalanlar sepeti ----------------
yaz("## A) Lider fırlayınca henüz hareket etmemiş coin'lerin sepeti (coin seçimi yok)\n_haftada olay · isabet · olay başı net % — seçim 2022-06→2023 | 2024+ | 2026_\n```")
RA = {}
for ad in LIDERLER:
    for k in (1, 4):
        e = lider(ad, k)
        for h in HS:
            ev = events(e & (np.arange(len(IX)) + h < len(IX)), h)
            if len(ev) < 10: continue
            F = FWD[h][DIGER].values[ev]; geri = (Z[k][DIGER].values[ev] <= 0.5)
            sep = np.where(geri.sum(1) >= 5, np.nanmean(np.where(geri, F, np.nan), axis=1), np.nan) - KOM
            hep = np.nanmean(F, axis=1) - KOM
            RA[(ad, k, h)] = (ozet(sep, ev), ozet(hep, ev), sep, ev)
            yaz(f"{ad:18s} {k} s z≥2 → {h:>2} s tut  geride kalan {sat(RA[(ad, k, h)][0])}")
            yaz(f"{'':38s}hepsi        {sat(RA[(ad, k, h)][1])}")
yaz("```")
S1 = "seçim 2022-06→2023"
en = max(RA, key=lambda q: RA[q][0][S1][2] if RA[q][0][S1][0] >= MIN[S1] and np.isfinite(RA[q][0][S1][2]) else -9)
oA, sepA, evA = RA[en][0], RA[en][2], RA[en][3]; m24 = (IX[evA] >= A24) & np.isfinite(sepA); lo, hi = wboot(sepA[m24], IX[evA][m24])
KA = all(oA[dn][0] >= MIN[dn] and oA[dn][1] >= BEN[dn][0] and oA[dn][2] >= BEN[dn][1] for dn in MIN) and lo > 0
yaz(f"Seçimde en iyi: **{en[0]} {en[1]} s → {en[2]} s tut** · {sat(oA)} · 2024+ bootstrap %90: {100*lo:+.2f} … {100*hi:+.2f} → {'✅ GEÇTİ' if KA else '❌ geçmedi'}\n")
# ---------------- B) coin'e özel takipçi / zıt ----------------
yaz("## B) Coin'e özel takipçi (AL) ve zıt (SAT): seçim döneminin en iyi 3 coin'i doğrulamada tutuyor mu?\n```")
sec_rows, rast_g, rast_n = [], 0, 0; POOL = {1: [], -1: []}
for ad in LIDERLER:
    for k in (1, 4):
        e = lider(ad, k)
        for h in HS:
            ev = events(e & (np.arange(len(IX)) + h < len(IX)), h); t = IX[ev]
            if len(ev) < 20: continue
            F = FWD[h].values[ev]; ms = (t >= P0) & (t < A24); mv = t >= A24; m26 = t >= A26
            for yon in (1, -1):
                G = yon * F - KOM; kand = []
                for j, c in enumerate(C.columns):
                    if c == ad or (ad == "büyükler birlikte" and c in LID): continue
                    xs = G[ms, j]; xs = xs[np.isfinite(xs)]; xv = G[mv, j]; okv = np.isfinite(xv)
                    if okv.sum() >= 20:
                        lo_, _ = wboot(xv[okv], t[mv][okv], reps=300); gecti = np.nanmean(xv) > 0 and lo_ > 0; rast_n += 1; rast_g += gecti
                    else: gecti = None
                    if len(xs) >= 20:
                        tt = xs.mean() / (xs.std(ddof=1) / np.sqrt(len(xs)) + 1e-12)
                        if tt >= 2: kand.append((xs.mean(), c, j, tt, len(xs), gecti))
                for mn, c, j, tt, n, gecti in sorted(kand, reverse=True)[:3]:
                    xv = G[mv, j]; x26 = G[m26, j]
                    sec_rows.append((ad, k, h, "AL" if yon > 0 else "SAT", c, n, 100 * mn, tt, int(np.isfinite(xv).sum()), 100 * np.nanmean(xv), 100 * np.nanmean(xv > 0),
                                     int(np.isfinite(x26).sum()), 100 * np.nanmean(x26) if np.isfinite(x26).any() else np.nan, gecti))
                    POOL[yon].append(pd.DataFrame({"t": t, "r": G[:, j]}))
S = pd.DataFrame(sec_rows, columns=["lider", "k", "tut", "yön", "coin", "n_seç", "net_seç", "t_seç", "n_24+", "net_24+", "isabet_24+", "n_26", "net_26", "geçti_24+"])
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500)
if len(S): yaz(S.round(2).to_string(index=False))
yaz("```")
sg = S["geçti_24+"].dropna(); oran_s = 100 * sg.astype(bool).mean() if len(sg) else np.nan; oran_r = 100 * rast_g / max(rast_n, 1)
yaz(f"Seçilen {len(S)} takipçi/zıt · 2024+'da geçen: {int(sg.astype(bool).sum()) if len(sg) else 0}/{len(sg)} (%{oran_s:.1f}) · rastgele coin'lerde geçme oranı %{oran_r:.1f} ({rast_n:,} deneme)")
KB = []
for yon, ad_ in ((1, "AL (takipçi)"), (-1, "SAT (zıt)")):
    if not POOL[yon]: continue
    X = pd.concat(POOL[yon]); X = X[np.isfinite(X.r)]; tX = pd.DatetimeIndex(X.t); v = X.r.values
    o = {dn: (int(m.sum()), 100 * (v[m] > 0).mean() if m.any() else np.nan, 100 * v[m].mean() if m.any() else np.nan, m.sum() / HAF[dn])
         for dn, m in (("seçim 2022-06→2023", (tX >= P0) & (tX < A24)), ("2024+", tX >= A24), ("2026", tX >= A26))}
    ok_ = all(o[dn][0] >= MIN[dn] and o[dn][1] >= BEN[dn][0] and o[dn][2] >= BEN[dn][1] for dn in ("2024+", "2026"))
    yaz(f"Seçilenler toplu, {ad_}: {sat(o)} → ana ölçüt {'✅' if ok_ else '❌'}")
    if ok_: KB.append(ad_)
KBok = bool(KB) and np.isfinite(oran_s) and oran_s >= 20 and oran_s >= 2 * oran_r
yaz("\n## Önceden yazılı karar")
yaz(f"- A) Geride kalanlar sepeti: {'✅ GEÇTİ → yeni sinyal adayı' if KA else '❌ geçmedi'}")
yaz(f"- B) Coin'e özel takipçi / zıt: {'✅ GEÇTİ (' + ', '.join(KB) + ')' if KBok else '❌ geçmedi — seçilen coin rastgele seçilmişten iyi değil ya da ana ölçütü tutmuyor'}")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("takip_sonuc.md", "w").write("\n".join(L) + "\n")
