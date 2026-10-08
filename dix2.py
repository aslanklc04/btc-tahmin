# dix2.py — KARANLIK HAVUZ SAĞLAMLIK TESTİ (etf.py'de geçen 2 kural için, karar kuralları ÖNCEDEN yazıldı):
#  Pay = IBIT'in borsa dışı (FINRA TRF: dark pool + iç eşleştirme) hacmi / toplam hacim (Yahoo). z: son 60 işlem günü. T günü verisi T+1 14:00 UTC'den sonra kullanılır.
#  A) Tek başına "pay z ≥ k → BTC AL, H gün": k ∈ {1,0 · 1,5 · 2,0}, H ∈ {3, 5, 7, 10} · yıl yıl (2024 / 2025 / 2026) · plasebo (dairesel kaydırma, 2000 kez).
#     Canlıya önerilir ancak: ana kural (k 1,5 · H 7) plasebo p < 0,05 · her yıl net > 0 · 2025+ döneminde 12 komşudan ≥ 9'u net > 0.
#     Ek bakış (karar dışı): tüm büyük BTC ETF'leri toplamı (IBIT+FBTC+GBTC+ARKB+BITB) ile aynı kural · ETH (ETHA) ile aynı kural.
#  B) Filtre "pay z ≤ −k → sinyal kötü" (k ∈ {0,5 · 1,0 · 1,5}), aile aile, yıl yıl · plasebo (pay serisi dairesel kaydırılır, 500 kez; 2025+ fark).
#     Bir aile için canlıya önerilir ancak: k 1,0'da plasebo p < 0,05 · her yıl (2024, 2025, 2026) iyi > kötü · 3 eşikten ≥ 2'sinde 2025+ fark ≥ 3 puan.
import os, io, re, glob, time, gzip, pickle, requests, numpy as np, pandas as pd
import yfinance as yf
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
rng = np.random.default_rng(1); LMT = 0.0002; TS = lambda s: pd.Timestamp(s, tz="UTC")
YIL = (("2024", TS("2024-01-01"), TS("2025-01-01")), ("2025", TS("2025-01-01"), TS("2026-01-01")), ("2026", TS("2026-01-01"), TS("2030-01-01")))
FR = pd.read_csv("veri_finra.csv.gz", dtype={"Date": str}); FR["t"] = pd.to_datetime(FR.Date, format="%Y%m%d").dt.tz_localize("UTC")
def yv(t):
    h = yf.Ticker(t).history(start="2024-01-01", auto_adjust=False)["Volume"]; return pd.Series(h.values, index=[pd.Timestamp(i.date(), tz="UTC") for i in h.index])
def pay(semboller):
    off = FR[FR.Symbol.isin(semboller)].groupby("t").TotalVolume.sum(); top = sum(yv(s).reindex(off.index) for s in semboller); return (off / top).replace([np.inf, -np.inf], np.nan).dropna()
Z = lambda v: (v - v.rolling(60, min_periods=20).mean()) / (v.rolling(60, min_periods=20).std() + 1e-9)
P = {"IBIT": pay(["IBIT"]), "BTC ETF'leri (5)": pay(["IBIT", "FBTC", "GBTC", "ARKB", "BITB"]), "ETHA": pay(["ETHA"])}
def gunluk(sym):
    rows, cur = [], int(pd.Timestamp("2023-06-01", tz="UTC").timestamp() * 1000)
    while True:
        r = requests.get(EP[0], params=dict(symbol=sym, interval="1d", startTime=cur, limit=1000), timeout=20).json()
        if not r: break
        rows += r; cur = r[-1][0] + 86_400_000
        if len(r) < 1000: break
    d = pd.DataFrame([x[:5] for x in rows], columns=["t", "o", "h", "l", "c"]).astype(float); return pd.Series(d.c.values, index=pd.to_datetime(d.t, unit="ms", utc=True))
PX = {"BTC": gunluk("BTCUSDT"), "ETH": gunluk("ETHUSDT")}
yaz(f"# 🕶️ Karanlık havuz sağlamlık testi — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n" + " · ".join(f"{k}: {v.index[0]:%Y-%m-%d}→{v.index[-1]:%Y-%m-%d}, ort pay %{100*v.mean():.0f}, son %{100*v.iloc[-1]:.0f}" for k, v in P.items()))
# ---------------- A) tek başına ----------------
def kural(pz, coin, k, H):
    px = PX[coin]; ix = px.index; y = px.shift(-(1 + H)) / px.shift(-1) - 1                                # giriş: T+1 kapanışı (T+2 00:00 UTC)
    mv = (pz >= k).reindex(ix).fillna(False).values; return mv, y, ix
def net_of(mv, y, ix, H): ev = ix[events(mv, H)]; return (y.reindex(ev) - 2 * LMT).dropna()
def yillik(n): return " | ".join(f"{pn}: {len(x)} · %{100*(x>0).mean():.0f} · {100*x.mean():+.2f}" if len(x) else f"{pn}: —" for pn, a, b in YIL for x in [n[(n.index >= a) & (n.index < b)]])
yaz("\n## A) Tek başına: borsa dışı pay z ≥ k → AL (H gün) — _işlem · isabet · işlem başı net %_")
for ad, coin in (("IBIT", "BTC"), ("BTC ETF'leri (5)", "BTC"), ("ETHA", "ETH")):
    pz = Z(P[ad]); kom = 0
    yaz(f"\n**{ad} → {coin}**\n```")
    for k in (1.0, 1.5, 2.0):
        for H in (3, 5, 7, 10):
            mv, y, ix = kural(pz, coin, k, H); n = net_of(mv, y, ix, H); n25 = n[n.index >= TS("2025-01-01")]
            kom += bool(len(n25) and n25.mean() > 0); yaz(f"k {k:.1f} · H {H:>2} → {yillik(n)}")
    mv, y, ix = kural(pz, coin, 1.5, 7); n0 = net_of(mv, y, ix, 7); n0 = n0[n0.index >= TS("2024-01-01")]; ob = n0.mean()
    ok_ix = np.where(ix >= TS("2024-03-01"))[0]; i0, i1 = ok_ix[0], len(ix) - 10; seg = mv[i0:i1]; sh = []
    for _ in range(2000):
        s_ = int(rng.integers(30, len(seg) - 30)); m2 = mv.copy(); m2[i0:i1] = np.roll(seg, s_); x = net_of(m2, y, ix, 7); x = x[x.index >= TS("2024-01-01")]
        if len(x): sh.append(x.mean())
    p = float(np.mean(np.array(sh) >= ob)); yil_ok = all(len(x) and x.mean() > 0 for pn, a, b in YIL for x in [n0[(n0.index >= a) & (n0.index < b)]])
    yaz(f"```\nAna kural (k 1,5 · H 7): ort net {100*ob:+.2f}% · plasebo p = {p:.3f} · her yıl net > 0: {'evet' if yil_ok else 'hayır'} · 2025+ komşu pozitif: {kom}/12"
        + (f" → {'✅ GEÇTİ' if (p < 0.05 and yil_ok and kom >= 9) else '❌ GEÇMEDİ'}" if ad == "IBIT" else " (ek bakış)"))
# ---------------- B) filtre ----------------
fh = open("filtre_hepsi.py").read(); _k = fh[fh.index("f = lambda p"):fh.index("# ---------- durum değişkenleri ----------")]; _k = re.sub(r"\nyaz\(f\"# 🔎.*?\n", "\n", _k, flags=re.S); exec(_k)
E["ok"] = E.r > 0; tt = pd.DatetimeIndex(E.t); E["hafta"] = tt.floor("7D"); E = E[tt >= TS("2024-03-01")].copy(); tt = pd.DatetimeIndex(E.t)
gun_once = (tt - pd.Timedelta(hours=14)).floor("D") - pd.Timedelta(days=1)
def asof(s, t):
    s = s.dropna(); s.index = pd.DatetimeIndex(s.index).as_unit("ns")
    L_ = pd.DataFrame({"t": pd.DatetimeIndex(t).as_unit("ns"), "i": np.arange(len(t))}).sort_values("t")
    return pd.merge_asof(L_, pd.DataFrame({"t": s.index, "v": s.values.astype(float)}), on="t", direction="backward").sort_values("i").v.values
pz = Z(P["IBIT"]).dropna(); E["pz"] = asof(pz, gun_once)
yaz("\n## B) Filtre: dünkü IBIT borsa dışı pay z ≤ −k → kötü — _iyi % / kötü % (kötü işlem)_\n```")
SON = []
for aile, G in E.groupby("aile"):
    gt = pd.DatetimeIndex(G.t); satir = []; fk = 0; yil_ok = None
    for k in (0.5, 1.0, 1.5):
        kk = (G.pz <= -k).values; parca = []
        for pn, a, b in YIL:
            m = (gt >= a) & (gt < b); iyi, kot = G.ok.values[m & ~kk].mean() * 100 if (m & ~kk).any() else np.nan, G.ok.values[m & kk].mean() * 100 if (m & kk).any() else np.nan
            parca.append(f"{pn} {iyi:.0f}/{kot:.0f} ({int((m & kk).sum())})")
            if k == 1.0: yil_ok = (yil_ok is not False) and bool(np.isfinite(kot) and iyi > kot)
        m25 = gt >= TS("2025-01-01"); f25 = 100 * (G.ok.values[m25 & ~kk].mean() - G.ok.values[m25 & kk].mean()) if (m25 & kk).any() else np.nan; fk += bool(f25 >= 3)
        satir.append(f"  k {k:.1f}: " + " · ".join(parca) + f" · 2025+ fark {f25:+.1f}")
    kk = (G.pz <= -1.0).values; m25 = gt >= TS("2025-01-01"); ob = 100 * (G.ok.values[m25 & ~kk].mean() - G.ok.values[m25 & kk].mean()); sh = []
    v = pz.values
    for _ in range(500):
        s_ = int(rng.integers(20, len(v) - 20)); kz = asof(pd.Series(np.roll(v, s_), index=pz.index), gun_once[E.index.get_indexer(G.index)]) <= -1.0
        if (m25 & kz).any() and (m25 & ~kz).any(): sh.append(100 * (G.ok.values[m25 & ~kz].mean() - G.ok.values[m25 & kz].mean()))
    p = float(np.mean(np.array(sh) >= ob)); gecti = bool(p < 0.05 and yil_ok and fk >= 2); SON.append((aile, gecti))
    yaz(f"{aile}: plasebo p = {p:.3f} · her yıl iyi > kötü: {'evet' if yil_ok else 'hayır'} · ≥3 puan eşik: {fk}/3 → {'✅ GEÇTİ' if gecti else '❌'}"); [yaz(s) for s in satir]
yaz("```")
yaz(f"\nFiltre geçen aileler: {', '.join(a for a, g in SON if g) or 'yok'}\n\n_Süre: {time.time()-T0:.0f} sn_")
open("dix2_sonuc.md", "w").write("\n".join(L) + "\n")
