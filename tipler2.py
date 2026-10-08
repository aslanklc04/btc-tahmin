# tipler2.py — BTC YATIRIMCI TİPLERİ (zincir üstü, bitcoin-data.com / BGeometrics ücretsiz API: son 4 yıl, saatte 8 / günde 15 istek, anahtar yok).
# Ham veri veri_bgeo/*.json olarak depoya kaydedilir; 20 saatten yeniyse tekrar çekilmez (istek sınırı için).
# Ölçüler: balina (≥1000 BTC) cüzdanlarındaki BTC · küçük (<1 BTC) cüzdanlardaki BTC ve küçük cüzdan sayısı · arza göre düzeltilmiş CDD (eski coin hareketi)
#          · uzun / kısa vadeli yatırımcı SOPR (sattıkları coin'de kârda mı zararda mı) · HODL dalgaları (1 yıldan eski arz payı).
# Zamanlama: gün d verisi → gün d+1 kapanışında gir, 3 / 7 gün tut, limit komisyon %0,02 × 2. z: son 90 güne göre.
# Veri yalnız 4 yıl → SEÇİM: 2024-10 öncesi · DOĞRULAMA: 2024-10 ve sonrası (≥ 8 işlem, net > 0, %90 alt sınır > 0). 2026 ayrıca.
# A) Önceden sabit hipotezler (yön sabit, 7 gün):
#   H1 balinalar topluyor (balina BTC'si 30 g z ≥ 1) → AL · H1b dağıtıyor (z ≤ −1) → SAT
#   H2 küçük yatırımcı akını (küçük cüzdan BTC'si 30 g z ≥ 1,5) → SAT · H2c küçük cüzdan SAYISI 30 g z ≥ 1,5 → SAT
#   H3 balina topluyor + küçük satıyor (balina z ≥ 1 VE küçük z ≤ 0) → AL
#   H4 eski coin'ler uyanıyor (düzeltilmiş CDD 7 g toplamı z ≥ 1,5) → SAT · H4b 1 yıldan eski arz payı 30 g z ≤ −1,5 → SAT
#   H5 kısa vadeli yatırımcı zararına satıyor (STH-SOPR 7 g ort. z ≤ −1,5, teslimiyet) → AL · H5b büyük kârla satıyor (z ≥ 1,5) → SAT
#   H6 uzun vadeli yatırımcı büyük kârla satıyor (LTH-SOPR 7 g ort. z ≥ 1,5) → SAT
# B) Geniş tarama + plasebo (sinyal rastgele kaydırılmış) ile şans payı.
import os, json, time, requests, numpy as np, pandas as pd
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
EPS = ["coins-addr-10K-BTC", "coins-addr-10K-1K-BTC", "coins-addr-1-BTC", "balance-addr-1-BTC", "supply-adjusted-cdd", "sth-sopr", "lth-sopr", "hodl-waves-supply"]
os.makedirs("veri_bgeo", exist_ok=True); DURUM = {}
for ep in EPS:
    f = f"veri_bgeo/{ep}.json"
    if os.path.exists(f) and time.time() - os.path.getmtime(f) < 20 * 3600 and os.path.getsize(f) > 1000: DURUM[ep] = "önbellek"; continue
    try:
        r = requests.get(f"https://bitcoin-data.com/v1/{ep}", timeout=60, headers={"User-Agent": "btc-tahmin-arastirma"})
        DURUM[ep] = f"HTTP {r.status_code}"
        if r.status_code == 200 and len(r.text) > 1000: open(f, "w").write(r.text)
        else: print(ep, r.status_code, r.text[:300])
    except Exception as e: DURUM[ep] = f"hata {type(e).__name__}"
    time.sleep(2)
def oku(ep):
    f = f"veri_bgeo/{ep}.json"
    if not os.path.exists(f): return None
    j = json.load(open(f))
    if isinstance(j, dict): j = next((v for v in j.values() if isinstance(v, list)), [j])
    rows = []
    for x in j:
        if not isinstance(x, dict): continue
        dk = next((k for k in ("d", "theDay", "date", "day", "time") if k in x), None)
        if dk is None: continue
        rows.append({"_d": x[dk], **{k: v for k, v in x.items() if k != dk and "ts" not in k.lower() and "unix" not in k.lower()}})
    d = pd.DataFrame(rows)
    if d.empty: return None
    d.index = pd.to_datetime(d.pop("_d"), utc=True, errors="coerce").dt.floor("D"); d = d[d.index.notna()]
    d = d.apply(pd.to_numeric, errors="coerce").dropna(axis=1, how="all"); return d[~d.index.duplicated()].sort_index()
V = {ep: oku(ep) for ep in EPS}
yaz(f"# 🐋🧑 BTC yatırımcı tipleri (bitcoin-data.com) — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}")
for ep in EPS:
    d = V[ep]; yaz(f"- `{ep}` ({DURUM.get(ep)}): " + ("yok" if d is None else f"{d.index[0]:%Y-%m-%d} → {d.index[-1]:%Y-%m-%d}, {len(d)} gün, sütunlar: {', '.join(map(str, d.columns[:12]))}{' …' if d.shape[1] > 12 else ''}"))
def tek(ep):
    d = V.get(ep)
    if d is None or d.empty: return None
    return d.iloc[:, 0] if d.shape[1] == 1 else d[d.var().idxmax()]
def gunluk(sym):
    rows, cur = [], int(pd.Timestamp("2021-01-01", tz="UTC").timestamp() * 1000)
    while True:
        r = requests.get(EP[0], params=dict(symbol=sym, interval="1d", startTime=cur, limit=1000), timeout=20).json()
        if not r: break
        rows += r; cur = r[-1][0] + 86_400_000
        if len(r) < 1000: break
    d = pd.DataFrame([x[:5] for x in rows], columns=["t", "o", "h", "l", "c"]).astype(float); return pd.Series(d.c.values, index=pd.to_datetime(d.t, unit="ms", utc=True))
px = gunluk("BTCUSDT")
def zs(s, n=90): return (s - s.rolling(n, min_periods=30).mean()) / (s.rolling(n, min_periods=30).std() + 1e-12)
F = {}
w1, w2, sm, sc = tek("coins-addr-10K-BTC"), tek("coins-addr-10K-1K-BTC"), tek("coins-addr-1-BTC"), tek("balance-addr-1-BTC")
if w1 is not None and w2 is not None: F["balina BTC 30g"] = np.log(w1.add(w2, fill_value=np.nan)).diff(30)
if sm is not None: F["küçük cüzdan BTC 30g"] = np.log(sm).diff(30)
if sc is not None: F["küçük cüzdan sayısı 30g"] = np.log(sc.where(sc > 0)).diff(30)
cdd = tek("supply-adjusted-cdd")
if cdd is not None: F["eski coin hareketi (CDD 7g)"] = cdd.rolling(7).sum()
for ep, ad in (("sth-sopr", "STH-SOPR 7g"), ("lth-sopr", "LTH-SOPR 7g")):
    s = tek(ep)
    if s is not None: F[ad] = s.rolling(7).mean()
hw = V.get("hodl-waves-supply")
if hw is not None and hw.shape[1] > 3:
    yaz(f"\nHODL dalgası sütunları: {', '.join(map(str, hw.columns))}")
    import re
    def yas_gun(c):                                                                                     # sütun adından alt yaş sınırı (gün)
        m = re.findall(r"(\d+)\s*([dwmy])", str(c).lower())
        if not m: return None
        n, u = m[0]; return int(n) * {"d": 1, "w": 7, "m": 30, "y": 365}[u]
    yg = {c: yas_gun(c) for c in hw.columns}; eski = [c for c, g in yg.items() if g is not None and g >= 365]
    if eski:
        tot = hw[[c for c in yg if yg[c] is not None]].sum(1); top = hw[eski].sum(1)
        pay = top / tot if tot.median() > 1.5 else top                                                    # yüzde ya da oran
        F["1 yıldan eski arz payı 30g"] = pay.diff(30); yaz(f"1 yıldan eski sayılan: {', '.join(map(str, eski))}")
ix = px.index
Z = {k: zs(v.reindex(ix)) for k, v in F.items()}
SEC_END, A26, LMT = pd.Timestamp("2024-10-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC"), 0.0002
DON = (("seçim (→2024-09)", lambda i: i < SEC_END), ("doğrulama (2024-10→)", lambda i: i >= SEC_END), ("2026", lambda i: i >= A26))
def sonuc(m, yon, HD, reps=800):
    y = np.log(px.shift(-(1 + HD)) / px.shift(-1)); ev = ix[events(m.reindex(ix).fillna(False).values, HD)]; y = y.reindex(ev).dropna()
    net = yon * (np.exp(y) - 1) - 2 * LMT; out = {}
    for pn, f in DON:
        e = net[f(net.index)]; out[pn] = (len(e), 100 * (e > 0).mean() if len(e) else np.nan, 100 * e.mean() if len(e) else np.nan, 100 * wboot(e.values, e.index.values, reps)[0] if len(e) >= 8 else np.nan)
    return out
def fmt(o): return " · ".join(("—" if not np.isfinite(v) else (f"{v:.0f}" if i < 2 else f"{v:+.2f}")) for i, v in enumerate(o))
def gecti(o): s, d = o[DON[0][0]], o[DON[1][0]]; return bool(np.isfinite(s[2]) and s[2] > 0 and d[0] >= 8 and d[2] > 0 and d[3] > 0)
yaz(f"\nÖzellikler: {', '.join(Z)} · {time.time()-T0:.0f} sn\n")
H = {}
g = lambda k: Z.get(k)
if g("balina BTC 30g") is not None: H["H1 balinalar topluyor → AL"] = (g("balina BTC 30g") >= 1, 1); H["H1b balinalar dağıtıyor → SAT"] = (g("balina BTC 30g") <= -1, -1)
if g("küçük cüzdan BTC 30g") is not None: H["H2 küçük yatırımcı akını → SAT"] = (g("küçük cüzdan BTC 30g") >= 1.5, -1)
if g("küçük cüzdan sayısı 30g") is not None: H["H2c küçük cüzdan sayısı fırlıyor → SAT"] = (g("küçük cüzdan sayısı 30g") >= 1.5, -1)
if g("balina BTC 30g") is not None and g("küçük cüzdan BTC 30g") is not None: H["H3 balina topluyor + küçük satıyor → AL"] = ((g("balina BTC 30g") >= 1) & (g("küçük cüzdan BTC 30g") <= 0), 1)
if g("eski coin hareketi (CDD 7g)") is not None: H["H4 eski coin'ler uyanıyor → SAT"] = (g("eski coin hareketi (CDD 7g)") >= 1.5, -1)
if g("1 yıldan eski arz payı 30g") is not None: H["H4b eski arz payı düşüyor → SAT"] = (g("1 yıldan eski arz payı 30g") <= -1.5, -1)
if g("STH-SOPR 7g") is not None: H["H5 kısa vadeli zararına satıyor (teslimiyet) → AL"] = (g("STH-SOPR 7g") <= -1.5, 1); H["H5b kısa vadeli büyük kârla satıyor → SAT"] = (g("STH-SOPR 7g") >= 1.5, -1)
if g("LTH-SOPR 7g") is not None: H["H6 uzun vadeli büyük kârla satıyor → SAT"] = (g("LTH-SOPR 7g") >= 1.5, -1)
yaz("## A) Önceden sabit hipotezler (yön sabit) — işlem · isabet % · işlem başı net % · alt sınır %")
rows, KAR = [], []
for k, (m, yon) in H.items():
    for HD in (3, 7):
        o = sonuc(m, yon, HD); rows.append(dict(hipotez=k, gun=HD, **{pn: fmt(o[pn]) for pn, _ in DON}))
        if HD == 7: KAR.append(f"- {'✅' if gecti(o) else '❌'} {k} · 7 gün: seçim {fmt(o[DON[0][0]])} · doğrulama {fmt(o[DON[1][0]])} · 2026 {fmt(o['2026'])}")
if rows: yaz("```\n" + pd.DataFrame(rows).set_index(["hipotez", "gun"]).to_string() + "\n```")
yaz("### Karar (A)\n" + ("\n".join(KAR) if KAR else "(veri yok)"))
son = {k: v.dropna().iloc[-1] for k, v in Z.items() if v.notna().any()}
if son: yaz("\nŞu an: " + " · ".join(f"{k} z {v:+.2f}" for k, v in son.items()))
yaz("\n## B) Geniş tarama (yön seçim döneminden; doğrulamada net > 0 ve alt > 0 → ✅)")
res, rng, pl_ok, pl_n = [], np.random.default_rng(0), 0, 0
for k, z in Z.items():
    for sk, m in (("z ≥ 1,5", z >= 1.5), ("z ≤ −1,5", z <= -1.5), ("z ≥ 1", z >= 1), ("z ≤ −1", z <= -1)):
        for HD in (3, 7):
            y = np.log(px.shift(-(1 + HD)) / px.shift(-1)); ev = ix[events(m.fillna(False).values, HD)]; e1 = y.reindex(ev).dropna(); e1 = e1[e1.index < SEC_END]
            if len(e1) < 8: continue
            yon = 1 if e1.mean() > 0 else -1; o = sonuc(m, yon, HD)
            res.append(dict(olcu=k, sinyal=sk, gun=HD, yon="AL" if yon > 0 else "SAT", **{pn: fmt(o[pn]) for pn, _ in DON}, ok=gecti(o)))
            mv = m.fillna(False).values; ok_i = np.where(~np.isnan(z.values))[0]
            for _ in range(20):
                sh = int(rng.integers(60, max(61, len(ok_i) - 60))); pv = np.zeros(len(mv), bool); pv[ok_i] = np.roll(mv[ok_i], sh); pm = pd.Series(pv, index=m.index)
                ev = ix[events(pv, HD)]; p1 = y.reindex(ev).dropna(); p1 = p1[p1.index < SEC_END]
                if len(p1) < 8: continue
                po = sonuc(pm, 1 if p1.mean() > 0 else -1, HD, reps=200); pl_n += 1; pl_ok += gecti(po)
R = pd.DataFrame(res)
if len(R):
    yaz(f"Toplam {len(R)} deneme · ✅ geçen **{int(R.ok.sum())}** · plasebo geçme oranı %{100*pl_ok/max(1,pl_n):.1f} → tesadüfen beklenen ≈ **{pl_ok/max(1,pl_n)*len(R):.1f}**")
    yaz("```\n" + R.to_string(index=False) + "\n```")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("tipler2_sonuc.md", "w").write("\n".join(L) + "\n")
