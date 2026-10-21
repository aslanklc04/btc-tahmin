# cokus_test.py — 🕳️ ÇÖKÜŞ DİBİ kuralının sağlamlık testi (21.10.2026; karanlik.py'de tek geçen kural; yalnız test)
# Kural (eşikler karanlik.py seçim döneminden, DONDURULDU): BTC son 24 s z ≤ −1  VE  coin 30 g zirveye uzaklık (log) ≤ −0,644  VE  coin son 24 s getiri z ≤ −2,46
#   → coin'i AL, 24 saat tut; aynı coin'de 24 s tekrar yok. Giriş = sinyal saati kapanışı, maliyet %0,04.
# Şüpheler: (1) hayatta kalan yanılgısı — karanlik.py yalnız bugün listede olan coin'leri kullandı; çöküp listeden çıkan coin'ler yoktu.
#           (2) birkaç büyük çöküş gününe yığılma · (3) çöküş anında gerçek alım fiyatı / makas.
# Evren: Binance'teki TÜM USDT çiftleri (listeden çıkarılmış BREAK dahil; kaldıraçlı token ve sabit değerli hariç).
#   Listeden çıkan coin'de 24 s dolmadan veri biterse: son fiyattan çıkılmış sayılır ve isabetsiz (kayıp) yazılır.
# ÖNCEDEN YAZILI KARAR (sonuç görülmeden) — KARAR evreni "likit": sinyal anında son 30 g ortalama günlük hacim ≥ 1 milyon $.
#   T1 tüm USDT (çıkanlar dahil) likit: doğrulama 2024–25 VE 2026 isabet ≥ %65, saat bazında ≥ %65, net > 0.
#   T2 gün bazında (aynı UTC günündeki sinyaller tek olay): 2024+ gün isabeti ≥ %65 (≥ 20 gün) VE en çok sinyalli 3 gün çıkarılınca 2024+ isabet ≥ %65.
#   T3 1 saat geç giriş (bir sonraki saat kapanışı, çıkış +25 s): 2024–25 ve 2026 isabet ≥ %65.
#   T4 yüksek maliyet %0,5 (makas + kayma): 2024–25 ve 2026 net > 0 ve isabet ≥ %60.
#   Dördü de geçerse "sağlam" → kullanıcıya canlı öneri (onaysız eklenmez). Biri bile geçmezse kural canlıya önerilmez.
import time, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import EP
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(str(s))
def kaydet(): open("cokus_test_sonuc.md", "w").write("\n".join(L) + "\n")
def dk(): return f"{(time.time() - T0) / 60:.0f} dk"
S = requests.Session(); BAS = pd.Timestamp("2021-01-01", tz="UTC")
import os
KURU = os.environ.get("KURU") == "1"
def get(url, **p):
    if KURU: return kuru_get(url, **p)
    for k in range(7):
        try:
            r = S.get(url, params=p, timeout=30)
            if r.status_code == 200: return r.json()
            if r.status_code in (400, 404): return None
            if r.status_code in (418, 429): time.sleep(15 * (k + 1)); continue
        except Exception: pass
        time.sleep(1 + 2 * k)
    raise RuntimeError(f"istek başarısız: {p.get('symbol')}")
def kuru_get(url, **p):
    if url.endswith("exchangeInfo"):
        return {"symbols": [{"symbol": f"C{i}USDT", "baseAsset": f"C{i}", "quoteAsset": "USDT", "status": "TRADING" if i < 15 else "BREAK"} for i in range(20)] + [{"symbol": "BTCUPUSDT", "baseAsset": "BTCUP", "quoteAsset": "USDT", "status": "BREAK"}]}
    sym = p["symbol"]; rg = np.random.default_rng(abs(hash(sym)) % 2**32); n0 = 50000; t0 = int(BAS.timestamp() * 1000)
    bl = np.random.default_rng(0).normal(0, .006, n0); lr = bl * (1 if sym == "BTCUSDT" else 1.2) + (0 if sym == "BTCUSDT" else rg.normal(0, .015, n0))
    if sym == "C16USDT": lr[30000:] -= 0.002
    c = 100 * np.exp(np.cumsum(lr)); end = n0 if sym not in ("C16USDT", "C17USDT") else 40000
    i0 = (p["startTime"] - t0) // 3_600_000; i1 = min(i0 + 1000, end)
    return [[t0 + i * 3_600_000, 0, 0, 0, c[i], 0, 0, 2e5 * (1 + (sym == "C3USDT") * 0), 0, 0, 0, 0] for i in range(int(i0), int(i1))]
INFO = None
for base in ("https://data-api.binance.vision", "https://api.binance.com"):
    INFO = get(base + "/api/v3/exchangeInfo")
    if INFO: break
KAL = ("UP", "DOWN", "BULL", "BEAR")
SY = [s for s in INFO["symbols"] if s["quoteAsset"] == "USDT" and not any(s["baseAsset"].endswith(k) and len(s["baseAsset"]) > len(k) for k in KAL)]
DUR = {s["symbol"]: s["status"] for s in SY}
CANLI = set(l.strip() for l in open("canli/durum/genis_liste.txt") if l.strip()) | set(l.strip() for l in open("canli/durum/coin_listesi.txt") if l.strip())
yaz(f"# 🕳️ Çöküş dibi — sağlamlık testi — {pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M}\nBinance USDT çiftleri (kaldıraçlı hariç): {len(SY)} · durum: "
    + ", ".join(f"{k} {v}" for k, v in pd.Series(list(DUR.values())).value_counts().items()))
def kl(sym):
    rows, cur, end = [], int(BAS.timestamp() * 1000), int(time.time() * 1000)
    while cur < end:
        dt = get(EP[0], symbol=sym, interval="1h", startTime=cur, limit=1000)
        if not dt: break
        rows += dt; cur = dt[-1][0] + 3_600_000
        if len(dt) < 1000: break
    if len(rows) < 900: return sym, None
    d = pd.DataFrame([[x[0], x[4], x[7]] for x in rows], columns=["t", "c", "qv"]).astype(float)
    d.index = pd.DatetimeIndex(pd.to_datetime(d.t, unit="ms", utc=True) + pd.Timedelta(hours=1)).as_unit("ns"); d = d[~d.index.duplicated()].sort_index()
    return sym, d[["c", "qv"]]
with ThreadPoolExecutor(1 if KURU else 6) as ex: O = {k: v for k, v in ex.map(kl, [s["symbol"] for s in SY] + ["BTCUSDT"]) if v is not None}
B = O.pop("BTCUSDT"); IX = pd.date_range(BAS, B.index[-1], freq="1h", tz="UTC").as_unit("ns")
yaz(f"2021+ en az 900 saat verisi olan: {len(O)} çift (listeden çıkmış: {sum(DUR[k] != 'TRADING' for k in O)}) · {dk()}")
bc = np.log(B.c.reindex(IX).ffill(limit=3)); bsig = bc.diff().rolling(720, min_periods=168).std(); KB = ((bc - bc.shift(24)) / (bsig * np.sqrt(24)) <= -1).values
EV = []
for sym, d in O.items():
    d = d.reindex(IX); cl = d.c.ffill(limit=3); c = np.log(cl); lr = c.diff(); sig = lr.rolling(720, min_periods=168).std()
    if np.nanmedian(sig) < 0.001: continue                                                          # sabit değerli (stabil / itibari)
    zr24 = (c - c.shift(24)) / (sig * np.sqrt(24)); dh30 = c - c.rolling(720, min_periods=700).max()
    liq = (d.qv.fillna(0).rolling(720, min_periods=168).sum() / 30).values
    m = (KB & (dh30 <= -0.644).values & (zr24 <= -2.46).values & cl.notna().values)
    son = cl.last_valid_index(); cv = cl.values; last = -10**9
    for i in np.flatnonzero(m):
        if i - last < 24: continue
        last = i; r = {}
        for ad, gi, H, mal in (("n", 0, 24, .0004), ("gec", 1, 24, .0004), ("pah", 0, 24, .005)):
            a, b = i + gi, i + gi + H
            if a >= len(IX) or not np.isfinite(cv[a]): r[ad] = np.nan; continue
            if b < len(IX) and np.isfinite(cv[b]): r[ad] = cv[b] / cv[a] - 1 - mal
            elif IX[b if b < len(IX) else -1] > son and DUR.get(sym) != "TRADING":            # listeden çıktı, veri bitti → son fiyattan çıkış, kayıp sayılır
                r[ad] = min(cl.loc[:son].iloc[-1] / cv[a] - 1 - mal, -1e-9); r["cikti"] = True
            else: r[ad] = np.nan
        EV.append(dict(t=IX[i], sym=sym, likit=liq[i] >= 1e6, durum=DUR.get(sym), canli=sym in CANLI, cikti=r.get("cikti", False), n=r["n"], gec=r["gec"], pah=r["pah"],
                       dd=float(np.exp(dh30.iloc[i]) - 1), z=float(zr24.iloc[i])))
E = pd.DataFrame(EV); E["yil"] = E.t.dt.year; E["gun"] = E.t.dt.floor("D")
E["per"] = np.where(E.t < pd.Timestamp("2024-01-01", tz="UTC"), "2021–23", np.where(E.t < pd.Timestamp("2026-01-01", tz="UTC"), "2024–25", "2026"))
yaz(f"sinyal: {len(E):,} (likit {E.likit.sum():,} · listeden çıkmış coin'de {(E.durum != 'TRADING').sum():,} · veri bittiği için kayıp yazılan {E.cikti.sum()}) · {dk()}")
def ozet(x, k="n"):
    x = x[x[k].notna()]
    if len(x) == 0: return dict(n=0, hit=np.nan, net=np.nan, saat=np.nan, gun=np.nan, ng=0)
    s = x.groupby("t")[k].mean(); g = x.groupby("gun")[k].mean()
    return dict(n=len(x), hit=(x[k] > 0).mean() * 100, net=x[k].mean() * 100, saat=(s > 0).mean() * 100, gun=(g > 0).mean() * 100, ng=len(g))
def tab(x, k="n", bas=""):
    yaz(f"{bas:<34}" + " | ".join(f"{p}: {s['n']:>4} %{s['hit']:>3.0f} net {s['net']:+5.2f} saat%{s['saat']:>3.0f} gün%{s['gun']:>3.0f} ({s['ng']} g)" if s["n"] else f"{p}: —"
                                   for p, s in ((p, ozet(x[x.per == p], k)) for p in ("2021–23", "2024–25", "2026"))))
yaz("\n## Evrenlere göre (24 s tut, maliyet %0,04)\n```")
tab(E[E.canli], bas="yalnız canlı liste (karanlik.py gibi)"); tab(E, bas="TÜM USDT (çıkanlar dahil)"); tab(E[E.likit], bas="TÜM USDT, likit ≥ 1 M$/gün (KARAR)")
tab(E[E.likit & (E.durum != "TRADING")], bas="  ↳ yalnız listeden çıkmış, likit")
yaz("```\n\n## Yıl yıl (KARAR evreni)\n```")
K = E[E.likit]
for y_, x in K.groupby("yil"):
    s = ozet(x); yaz(f"{y_}: {s['n']:>4} sinyal · isabet %{s['hit']:.0f} · net {s['net']:+.2f}% · saat %{s['saat']:.0f} · gün %{s['gun']:.0f} ({s['ng']} gün)")
yaz("```\n\n## En çok sinyalli günler (KARAR evreni)\n```")
gg = K.groupby("gun").agg(n=("n", "size"), isabet=("n", lambda v: (v > 0).mean() * 100), net=("n", lambda v: v.mean() * 100)).sort_values("n", ascending=False)
for g, r in gg.head(15).iterrows(): yaz(f"{g:%d.%m.%Y}: {int(r.n):>3} sinyal · isabet %{r.isabet:.0f} · net {r.net:+.2f}%")
yaz("```")
K24 = K[K.t >= pd.Timestamp("2024-01-01", tz="UTC")]; top3 = K24.groupby("gun").size().sort_values(ascending=False).head(3).index
s3 = ozet(K24[~K24.gun.isin(top3)]); s24 = ozet(K24)
yaz(f"\n2024+ en kalabalık 3 gün ({', '.join(f'{g:%d.%m.%Y}' for g in top3)}) çıkarılınca: {s3['n']} sinyal · isabet %{s3['hit']:.0f} · net {s3['net']:+.2f}% · gün %{s3['gun']:.0f}")
yaz("\n## Gerçekçi alım\n```"); tab(K, "gec", "1 saat geç giriş"); tab(K, "pah", "maliyet %0,5"); yaz("```")
yaz("\n## 2026 sinyalleri (KARAR evreni)\n```")
for _, r in K[K.per == "2026"].sort_values("t").iterrows():
    yaz(f"{r.t.tz_convert('Europe/Istanbul'):%d.%m.%Y %H:%M} {r.sym[:-4]:<10} zirveden %{r.dd * 100:.0f} · 24 s z {r.z:.1f} · sonuç {r.n * 100:+.1f}%{' (listeden çıktı)' if r.durum != 'TRADING' else ''}")
yaz("```")
a, b = ozet(K[K.per == "2024–25"]), ozet(K[K.per == "2026"]); ga, gb = ozet(K[K.per == "2024–25"], "gec"), ozet(K[K.per == "2026"], "gec")
pa, pb = ozet(K[K.per == "2024–25"], "pah"), ozet(K[K.per == "2026"], "pah")
T1 = all(s["n"] >= 10 and s["hit"] >= 65 and s["saat"] >= 65 and s["net"] > 0 for s in (a, b))
T2 = s24["ng"] >= 20 and s24["gun"] >= 65 and s3["hit"] >= 65
T3 = all(s["n"] >= 10 and s["hit"] >= 65 for s in (ga, gb))
T4 = all(s["n"] >= 10 and s["net"] > 0 and s["hit"] >= 60 for s in (pa, pb))
yaz(f"\n## KARAR\nT1 tüm USDT likit {'✅' if T1 else '❌'} · T2 gün bazında / ilk 3 gün hariç {'✅' if T2 else '❌'} · T3 1 saat geç {'✅' if T3 else '❌'} · T4 maliyet %0,5 {'✅' if T4 else '❌'}")
yaz("→ " + ("✅ SAĞLAM — kullanıcıya canlı öneri (onaysız eklenmez)" if T1 and T2 and T3 and T4 else "❌ sağlam değil — canlıya önerilmez"))
yaz(f"\nBitti · {dk()}"); kaydet()
