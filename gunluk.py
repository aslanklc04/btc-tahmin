# gunluk.py — GÜNLÜK / ÇOK GÜNLÜK SİNYAL TARAMASI (20.10.2026, kullanıcı: "aramaya devam", isabet ≥ %65 şartı; yalnız test)
# BTC, ETH ve büyük 8 coin · günlük kapanış (UTC 00:00) · giriş = sinyal günü kapanışı · H gün sonra çıkış · maliyet %0,04 · yalnız AL.
# ÖNCEDEN YAZILI ŞART: doğrulama 2022–25 isabet ≥ %65 VE 2026 isabet ≥ %65 · doğrulama ≥ 20 sinyal · doğrulama net > 0 ve blok alt sınır > 0 · 2026 net > 0 ·
#   seçim (2018–21, verisi olanlarda) net > 0 · plasebo (sinyal günleri rastgele 20–200 gün kaydırılmış, 20 kez) %95'lik < gerçek geçen sayısı.
import glob, time, requests, numpy as np, pandas as pd
from ortak import fetch_1h, events, wboot
L = []
def yaz(s=""): print(s, flush=True); L.append(str(s))
T0 = time.time(); BAS = pd.Timestamp("2017-09-01", tz="UTC")
COINS = ["BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOGE", "LINK", "AVAX", "DOT"]
G = {}
for nm in COINS:
    try:
        o = fetch_1h(BAS.timestamp() * 1000, time.time() * 1000, sym=f"{nm}USDT"); o.index = pd.DatetimeIndex(o.index).tz_convert("UTC")
        d = pd.DataFrame({"c": o.close.resample("1D", label="right", closed="right").last(), "v": (o.volume * o.close).resample("1D", label="right", closed="right").sum()}).dropna()
        G[nm] = d[d.index < pd.Timestamp.now(tz="UTC").floor("D") + pd.Timedelta(days=1)]
    except Exception as e: print(nm, e)
RAW = {k: v.astype("float64") for k, v in pd.read_pickle(glob.glob("art3/**/prim_veri.pkl", recursive=True)[0]).items()}
PZD = {}
for nm in COINS:
    if nm in RAW:
        x = RAW[nm]; x.index = pd.DatetimeIndex(x.index).tz_convert("UTC"); p = (x.bp / 1e4).resample("1D", label="right", closed="right").mean()
        PZD[nm] = (p - p.rolling(90, min_periods=30).mean()) / (p.rolling(90, min_periods=30).std() + 1e-12)
out, a = [], pd.Timestamp("2022-03-01", tz="UTC")
while a < pd.Timestamp.now(tz="UTC"):
    b = a + pd.Timedelta(days=30)
    try: j = requests.get("https://api-futures.kucoin.com/api/v1/contract/funding-rates", params={"symbol": "XBTUSDTM", "from": int(a.timestamp() * 1000), "to": int(b.timestamp() * 1000)}, timeout=30).json(); out += j.get("data", [])
    except Exception: pass
    a = b
K_ = pd.DataFrame(out).drop_duplicates("timepoint"); FK = pd.Series(K_.fundingRate.astype(float).values, index=pd.to_datetime(K_.timepoint.astype("int64"), unit="ms", utc=True)).sort_index()
FKD = FK.resample("1D", label="right", closed="right").mean(); FZD = (FKD - FKD.rolling(90, min_periods=30).mean()) / (FKD.rolling(90, min_periods=30).std() + 1e-12)
B = G["BTC"]; E_ = G["ETH"]; ethbtc = np.log(E_.c / B.c.reindex(E_.index))
yaz(f"# 📆 Günlük sinyal taraması — {pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M}\n{len(G)} coin · günlük veri {B.index[0]:%Y-%m} → {B.index[-1]:%d.%m.%Y} · prim {len(PZD)} coin · {(time.time() - T0) / 60:.0f} dk\n")
def F(nm):
    d = G[nm]; c = np.log(d.c); r = c.diff(); s = r.rolling(90, min_periods=60).std()
    f = pd.DataFrame(index=d.index)
    f["z3"] = (c - c.shift(3)) / (s * np.sqrt(3)); f["z7"] = (c - c.shift(7)) / (s * np.sqrt(7)); f["g"] = r > 0
    f["ma200"] = d.c > d.c.rolling(200, min_periods=150).mean(); f["ma20"] = d.c > d.c.rolling(20).mean()
    f["dd30"] = d.c / d.c.rolling(30).max() - 1
    bw = d.c.rolling(20).std() / d.c.rolling(20).mean(); f["sik"] = bw <= bw.rolling(180, min_periods=120).quantile(0.1)
    f["pz"] = PZD[nm].reindex(d.index) if nm in PZD else np.nan; f["pz3"] = f.pz.rolling(3).min()
    f["fz"] = FZD.reindex(d.index); f["eb7"] = (ethbtc - ethbtc.shift(7)).reindex(d.index)
    f["eb7z"] = (f.eb7 - f.eb7.rolling(180, min_periods=90).mean()) / (f.eb7.rolling(180, min_periods=90).std() + 1e-12)
    return f
FT = {nm: F(nm) for nm in G}
KURAL = {
 "D1a 3 günde sert düşüş (z ≤ −2) + bugün yeşil → 3 gün": (lambda f, nm: (f.z3 <= -2) & f.g, 3), "D1b aynı → 7 gün": (lambda f, nm: (f.z3 <= -2) & f.g, 7),
 "D2 ABD 3 gün üst üste alıyor (prim z ≥ 1) → 7 gün": (lambda f, nm: f.pz3 >= 1, 7),
 "D3a fonlama çok düşük (KuCoin z ≤ −2, açığa satan çok) → 3 gün": (lambda f, nm: f.fz <= -2, 3), "D3b aynı → 7 gün": (lambda f, nm: f.fz <= -2, 7),
 "D5 sıkışma (bant genişliği en dar %10) + 20 gün ortalama üstü → 7 gün": (lambda f, nm: f.sik & f.ma20, 7),
 "D7a yükseliş trendinde (200 g ort. üstü) %10+ düşüş + ilk yeşil gün → 7 gün": (lambda f, nm: f.ma200 & (f.dd30 <= -0.10) & f.g, 7),
 "D7b aynı → 14 gün": (lambda f, nm: f.ma200 & (f.dd30 <= -0.10) & f.g, 14),
 "D8 7 günde sert düşüş (z ≤ −2) + ABD alıyor (prim ≥ 0) → 7 gün": (lambda f, nm: (f.z7 <= -2) & (f.pz >= 0), 7),
 "D9 ETH/BTC 7 günde sert ↑ (z ≥ 2) → bu coin 7 gün (alt sezonu)": (lambda f, nm: f.eb7z >= 2, 7),
 "D10 trendde (200 g üstü) + ABD alıyor (prim z ≥ 1) → 7 gün": (lambda f, nm: f.ma200 & (f.pz >= 1), 7)}
SEL, VAL, Y26 = (pd.Timestamp("2018-01-01", tz="UTC"), pd.Timestamp("2022-01-01", tz="UTC")), (pd.Timestamp("2022-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")), (pd.Timestamp("2026-01-01", tz="UTC"), pd.Timestamp("2100-01-01", tz="UTC"))
def deg(kaydir=False, rg=None):
    R = {}
    for k, (fn, H) in KURAL.items():
        for grp, coins in (("BTC", ["BTC"]), ("ETH", ["ETH"]), ("10 coin", list(G))):
            T, N = [], []
            for nm in coins:
                f = FT[nm]; m = np.nan_to_num(fn(f, nm).values.astype(float), nan=0).astype(bool)
                if kaydir: m = np.roll(m, int(rg.integers(20, 200)))
                c = G[nm].c.values; n = len(c); ok = np.arange(n) + H < n; ev = events(m & ok, H)
                if len(ev): T.append(f.index[ev]); N.append(c[ev + H] / c[ev] - 1 - 0.0004)
            if not T: continue
            t = pd.DatetimeIndex(np.concatenate(T)); r = np.concatenate(N); res = {}
            for dn, (a, b) in (("sel", SEL), ("val", VAL), ("y26", Y26)):
                s = (t >= a) & (t < b); res[dn] = (int(s.sum()), 100 * (r[s] > 0).mean() if s.any() else np.nan, 100 * r[s].mean() if s.any() else np.nan)
            s = (t >= VAL[0]) & (t < VAL[1]); res["lo"] = wboot(r[s] * 100, t[s])[0] if s.sum() >= 5 else np.nan
            res["gec"] = bool(res["val"][0] >= 20 and res["val"][1] >= 65 and res["y26"][1] >= 65 and res["val"][2] > 0 and res["lo"] > 0 and res["y26"][2] > 0 and not (res["sel"][0] >= 5 and res["sel"][2] <= 0))
            R[(k, grp)] = res
    return R
R = deg(); ng = sum(v["gec"] for v in R.values())
yaz("```"); yaz(f"{'kural':62s} {'grup':8s} | seçim 2018–21 n·isabet·net | doğrulama 2022–25 n·isabet·net (alt) | 2026 n·isabet·net | sonuç")
for (k, grp), v in R.items():
    yaz(f"{k[:62]:62s} {grp:8s} | {v['sel'][0]:4d} %{v['sel'][1]:4.0f} {v['sel'][2]:+6.2f} | {v['val'][0]:4d} %{v['val'][1]:4.0f} {v['val'][2]:+6.2f} ({v['lo']:+.2f}) | {v['y26'][0]:3d} %{v['y26'][1]:4.0f} {v['y26'][2]:+6.2f} | {'✅' if v['gec'] else '—'}")
yaz("```")
rg = np.random.default_rng(17); PL = [sum(v["gec"] for v in deg(True, rg).values()) for _ in range(20)]; p95 = np.percentile(PL, 95)
yaz(f"\n## Plasebo (20 kaydırma): geçen ortalama {np.mean(PL):.1f} · %95'lik {p95:.1f} · en çok {max(PL)}")
yaz(f"\n**Karar (önceden yazılı, %65):** " + (f"✅ {ng} geçti (plasebo %95 {p95:.1f}): " + ", ".join(f"{k} [{g}]" for (k, g), v in R.items() if v["gec"]) if ng > p95 and ng > 0 else f"❌ şartı geçen yok ya da şanstan ayırt edilemiyor (gerçek {ng}, plasebo %95 {p95:.1f})"))
open("gunluk_sonuc.md", "w").write("\n".join(L) + "\n")
