# zit2.py — HER COİNİN ZITTI: hedef coin için (a) aynı gün ters hareket eden coin/varlık, (b) YÜKSELMEYE başlayınca hedefi sonradan DÜŞÜREN (ya da düşünce yükselten) coin/varlık.
# Hedefler: sistemdeki coin'ler + 2026'da en çok işlem gören coin'ler. Adaylar: Binance'teki tüm USDT coin'leri (stabil/itibari/kaldıraçlı hariç) + 22 dış varlık (varlik.py).
# (b) Önceden sabit: aday ani yükseliş (1 g z ≥ 2) / yükselişe başladı (5 g z ≥ 1,5) → hedefi SAT; aday ani düşüş / düşüşe başladı → hedefi AL; 1 / 3 / 7 gün tut.
#     Giriş: adayın gün kapanışında (coin'ler 00:00 UTC; ABD varlıkları ~3 saat önce kapanır; FRED verisi 1 gün gecikmeli). Vadeli komisyon %0,05 × 2.
#     Seçim ≤2024: her hedef × sinyal × gün için ≤2024'te en iyi (t değeri en yüksek, ≥ 15 işlem) aday. Doğrulama 2025+: ≥ 8 işlem, net > 0 ve %90 alt sınır > 0 → ✅.
#     Şans karşılaştırması: aynı doğrulama TÜM adaylara uygulanır → "rastgele bir aday seçseydik geçme oranı". Seçilenler bundan belirgin iyi değilse zıt yok demektir.
import time, io, requests, numpy as np, pandas as pd
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
v = open("varlik.py").read(); exec(v[v.index("VG = {"):v.index("def gunluk(sym):")])               # SER: dış varlıklar (Yahoo + FRED)
SER.pop("Fed net likidite", None)
S = requests.Session()
def get(url, **p):
    for k in range(4):
        try:
            r = S.get(url, params=p, timeout=30)
            if r.status_code == 200: return r.json()
            if r.status_code in (400, 404): return None
        except Exception: pass
        time.sleep(1 + 2 * k)
    return None
INFO = get("https://data-api.binance.vision/api/v3/exchangeInfo") or get("https://api.binance.com/api/v3/exchangeInfo")
SY = [s for s in INFO["symbols"] if s["quoteAsset"] == "USDT"]; BASE = {s["symbol"]: s["baseAsset"] for s in SY}; DURUM = {s["symbol"]: s["status"] for s in SY}
def gunluk(sym):
    rows, cur = [], int(pd.Timestamp("2017-08-01", tz="UTC").timestamp() * 1000)
    while True:
        r = get(EP[0], symbol=sym, interval="1d", startTime=cur, limit=1000)
        if not r: break
        rows += r; cur = r[-1][0] + 86_400_000
        if len(r) < 1000: break
    if len(rows) < 60: return sym, None
    d = pd.DataFrame([[x[0], x[4], x[7]] for x in rows], columns=["t", "c", "q"]).astype(float); d.index = pd.to_datetime(d.t, unit="ms", utc=True); return sym, d[["c", "q"]]
with ThreadPoolExecutor(10) as ex: PX = {k: v for k, v in ex.map(gunluk, [s["symbol"] for s in SY]) if v is not None}
ITIBARI = set("EUR GBP AUD TRY BRL RUB UAH NGN ZAR BIDR IDRT BVND USDC BUSD TUSD USDP FDUSD DAI PAX UST USDS USDSB SUSD AEUR EURI XUSD USD1 RLUSD BFUSD U USDE".split())
BUYUK = "BTC ETH BNB XRP ADA LINK DOT EOS TRX XTZ LTC BCH FIL SXP YFI SUSHI UNI AAVE 1INCH XLM".split()
ix = pd.date_range("2017-08-17", pd.Timestamp.now(tz="UTC").floor("D") - pd.Timedelta(days=1), freq="D", tz="UTC")
LP, KAT = {}, {}
for sym, d in PX.items():
    b = BASE[sym]
    if b in ITIBARI or any(b == p + s for p in BUYUK for s in ("UP", "DOWN", "BULL", "BEAR")): continue
    lp = np.log(d.c).iloc[15:]; r = lp.diff()
    if len(r) < 200 or r.std() < 0.005: continue
    lp[r.abs() > 1.5] = np.nan; LP[b] = lp.reindex(ix); KAT[b] = "coin"
for ad, (x, dn, kay) in SER.items():
    x = x[x.index >= ix[0] - pd.Timedelta(days=200)]; LP[ad] = (np.log(x) if dn in ("log", "ters") else x); KAT[ad] = "fred" if kay == "fred" else "dış"
yaz(f"# 🔄 Her coinin zıttı — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nAday: {sum(v == 'coin' for v in KAT.values())} coin (çıkarılanlar dahil; stabil/itibari/kaldıraçlı hariç) + {sum(v != 'coin' for v in KAT.values())} dış varlık · {time.time()-T0:.0f} sn\n")
# ---- hedefler ----
SIS = [l.strip().replace("USDT", "") for l in open("durum/coin_listesi.txt") if l.strip()] if __import__("os").path.exists("durum/coin_listesi.txt") else []
A25, A26 = pd.Timestamp("2025-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")
hacim = pd.Series({BASE[s]: d.q[d.index >= A26].mean() for s, d in PX.items() if DURUM[s] == "TRADING" and BASE[s] in LP and LP[BASE[s]][ix < A25].notna().sum() >= 400})
HEDEF = list(dict.fromkeys([c for c in SIS if c in LP] + [c for c in hacim.sort_values(ascending=False).index if c != "BTC"][:16]))
yaz(f"Hedef coin'ler ({len(HEDEF)}): {', '.join(HEDEF)}\n")
# ---- getiri matrisleri ----
RET = pd.DataFrame({k: (LP[k].reindex(ix).diff() if KAT[k] == "coin" else LP[k].diff().reindex(ix)) for k in LP})       # dış varlık: işlem günü değişimi, hafta sonu boş
SEC, DOG = ix < A25, ix >= A25
btc = RET["BTC"]
yaz("## 1. Aynı gün en ters hareket eden (günlük getiri korelasyonu; ≤2024 ≥ 365 ortak gün, 2025+ ≥ 200)")
yaz("_ham: düz korelasyon (1 = aynı, −1 = tam zıt) · BTC'siz: iki tarafın da BTC'ye bağlı kısmı çıkarıldıktan sonra kalan kendi hareketlerinin korelasyonu_")
beta = {k: (RET.loc[SEC, k].cov(btc[SEC]) / btc[SEC].var()) if RET.loc[SEC, k].notna().sum() >= 200 else RET[k].cov(btc) / btc.var() for k in RET}
RES = pd.DataFrame({k: RET[k] - beta[k] * btc for k in RET})
rows = []
for t in HEDEF:
    out = dict(hedef=t)
    for nm, M in (("ham", RET), ("BTC'siz", RES)):
        for pn, m, mn in (("≤2024", SEC, 365), ("2025+", DOG, 200)):
            X = M[m]; c = X.corrwith(X[t]).drop(t, errors="ignore"); n = (X.notna() & X[t].notna().values[:, None]).sum().drop(t, errors="ignore"); c = c[n >= mn]
            if nm == "ham" and pn == "≤2024": sec_min = c.idxmin() if len(c) else None
            out[f"{nm} {pn} en ters"] = f"{c.idxmin()} {c.min():+.2f}" if len(c) else "—"
            if nm == "ham": out[f"ham {pn} medyan"] = round(c.median(), 2) if len(c) else np.nan
        if nm == "ham" and sec_min:
            X = RET[DOG]; out["≤2024'ün en tersi 2025+'da"] = f"{X[sec_min].corr(X[t]):+.2f}"
    rows.append(out)
yaz("```\n" + pd.DataFrame(rows).set_index("hedef").to_string() + "\n```")
# ---- 2. öncü zıt ----
yaz("\n## 2. Öncü zıt: aday yükselmeye başlayınca hedef sonra düşüyor mu (ya da aday düşünce hedef yükseliyor mu)?")
FEE = 0.0005; HS = (1, 3, 7)
TL = np.column_stack([LP[t].reindex(ix).values for t in HEDEF])                                         # hedef log fiyat (gün kapanışı)
FWD = {H: np.vstack([TL[H:] - TL[:-H], np.full((H, len(HEDEF)), np.nan)]) for H in HS}
SIGS = (("ani yükseliş (1 g z≥2)", -1), ("yükselişe başladı (5 g z≥1,5)", -1), ("ani düşüş (1 g z≤−2)", 1), ("düşüşe başladı (5 g z≤−1,5)", 1))
sec_i, dog_i, y26 = SEC, DOG, ix >= A26
ST = {}                                                                                                 # (aday, sinyal, H) → istatistik dizileri (hedef başına)
for c in LP:
    x = LP[c]; r1 = x.diff(); sd = r1.rolling(90, min_periods=40).std(); z1, z5 = r1 / sd, x.diff(5) / (sd * np.sqrt(5))
    if KAT[c] == "coin": z1, z5 = z1.reindex(ix), z5.reindex(ix)
    else:
        z1, z5 = z1.reindex(ix), z5.reindex(ix)
        if KAT[c] == "fred": z1, z5 = z1.shift(1), z5.shift(1)                                         # FRED: ertesi gün yayımlanır
    MS = (z1 >= 2, z5 >= 1.5, z1 <= -2, z5 <= -1.5)
    for (sn, yon), m in zip(SIGS, MS):
        mv = m.fillna(False).values
        if mv.sum() < 15: continue
        for H in HS:
            ev = events(mv, H); Y = yon * (np.exp(FWD[H][ev]) - 1) - 2 * FEE; ps = ix[ev]
            def stat(pm):
                Z = Y[pm]; n = np.isfinite(Z).sum(0); mu = np.nanmean(np.where(np.isfinite(Z), Z, np.nan), 0) if len(Z) else np.full(len(HEDEF), np.nan)
                s = np.nanstd(Z, 0, ddof=1) if len(Z) > 1 else np.full(len(HEDEF), np.nan); return n, mu, s
            with np.errstate(all="ignore"):
                n1, m1, s1 = stat(ps < A25); n2, m2, s2 = stat(ps >= A25); n3, m3, _ = stat(ps >= A26)
            ST[(c, sn, H)] = dict(n1=n1, t1=m1 / (s1 / np.sqrt(np.maximum(n1, 1))), m1=m1, n2=n2, m2=m2, lo2=m2 - 1.645 * s2 / np.sqrt(np.maximum(n2, 1)), n3=n3, m3=m3, ev=ps)
yaz(f"Hesaplanan aday×sinyal×süre: {len(ST)} · {time.time()-T0:.0f} sn")
sel, base_ok, base_n, base_m = [], 0, 0, []
for j, t in enumerate(HEDEF):
    for sn, yon in SIGS:
        for H in HS:
            cand = [(c, st) for (c, s_, h), st in ST.items() if s_ == sn and h == H and c != t and st["n1"][j] >= 15 and st["n2"][j] >= 8]
            if not cand: continue
            for c, st in cand:                                                                          # şans: tüm adaylar
                base_n += 1; ok = st["m2"][j] > 0 and st["lo2"][j] > 0; base_ok += ok; base_m.append(st["m2"][j])
            c, st = max(cand, key=lambda z: z[1]["t1"][j])
            ok = st["m2"][j] > 0 and st["lo2"][j] > 0
            sel.append(dict(hedef=t, sinyal=sn, gun=H, yon="SAT" if yon < 0 else "AL", zit=c, sec=f"{int(st['n1'][j])} · {100*st['m1'][j]:+.2f} (t {st['t1'][j]:.1f})",
                            dog=f"{int(st['n2'][j])} · {100*st['m2'][j]:+.2f} (alt {100*st['lo2'][j]:+.2f})", y2026=f"{int(st['n3'][j])} · {100*st['m3'][j]:+.2f}" if st["n3"][j] else "—", ok=ok, m2=st["m2"][j]))
SL = pd.DataFrame(sel)
yaz(f"\n### Özet: seçilen zıtlar rastgele adaydan iyi mi?\n- Seçilen (≤2024'ün en iyisi) zıt: {len(SL)} · 2025+'da geçen: **{int(SL.ok.sum())}** (%{100*SL.ok.mean():.1f}) · 2025+ ortalama net %{100*SL.m2.mean():+.2f}\n"
    f"- Rastgele aday (tüm adaylar): {base_n:,} · 2025+'da geçen %{100*base_ok/max(1,base_n):.1f} · ortalama net %{100*np.nanmean(base_m):+.2f}\n"
    f"- Yalnız 'yükselince SAT' (senin sorduğun): seçilen {int((SL.yon=='SAT').sum())}, geçen {int(SL[SL.yon=='SAT'].ok.sum())} (%{100*SL[SL.yon=='SAT'].ok.mean():.1f}) · 2025+ ortalama net %{100*SL[SL.yon=='SAT'].m2.mean():+.2f}")
yaz("\n### ✅ Geçenler (seçim ≤2024 · doğrulama 2025+ · işlem · işlem başı net %)\n```\n" + (SL[SL.ok].drop(columns=["ok", "m2"]).to_string(index=False) if SL.ok.any() else "(yok)") + "\n```")
yaz("\n### Her hedefin ≤2024'te seçilen zıtları ve 2025+ sonucu (3 gün)\n```\n" + SL[SL.gun == 3].drop(columns=["ok", "m2"]).to_string(index=False) + "\n```")
yaz("\n### Tümü (1 ve 7 gün)\n```\n" + SL[SL.gun != 3].drop(columns=["m2"]).to_string(index=False) + "\n```")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("zit2_sonuc.md", "w").write("\n".join(L) + "\n")
