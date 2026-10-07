# para_coin.py — PARA TESTİ: "BTC 4s Çok güçlü ↑ anında coin al" vs "BTC al" (canlı sisteme dokunmaz)
# Olay: BTC 4s Çok güçlü ↑ (ilk ortaya çıktığı saat, 4 saat tekrar sayılmaz). O saatte kendi sinyali (⭐ / 4s ÇG↑ / A) olan coin'ler alınır, 4 saat tutulur.
# Stratejiler (önceden sabit): BTC · tüm coin'ler eşit · canlı 🤝 listesi eşit · geçmiş isabeti en iyi 1 coin · en iyi 3 coin (yalnız GEÇMİŞ olaylarla seçilir)
# Giriş/çıkış: saat kapanışı (0 dk) ve mesajın geldiği an (6 dk) — dakikalık Binance fiyatıyla. Komisyon: spot %0,10 · BNB %0,075 · vadeli %0,05 (her yön).
import os, io, glob, zipfile, time, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
f = lambda p: glob.glob(f"art/**/{p}", recursive=True)
EX = {os.path.basename(p)[5:-4]: pd.read_pickle(p) for p in f("disa_*USDT.pkl")}
EXB = EX.pop("BTCUSDT"); SYMS = sorted(EX)
OA = pd.read_csv("durum/ortak_acik.csv") if os.path.exists("durum/ortak_acik.csv") else pd.DataFrame(columns=["sym", "sinyal"])
LISTE = set(zip(OA.sym, OA.sinyal))
H = 4; A0, A24 = pd.Timestamp("2020-01-01", tz="UTC"), pd.Timestamp("2024-01-01", tz="UTC")
bm = EXB.u4.fillna(False).values.astype(bool) & EXB.y4.notna().values
EV = EXB.index[events(bm, H)]; EV = EV[EV >= A0]
yaz(f"# 💰 Coin para testi — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}")
yaz(f"BTC 4s Çok güçlü ↑ olayı: {len(EV)} ({EV[0]:%Y-%m} → {EV[-1]:%Y-%m-%d}) · coin evreni: {len(SYMS)} coin (taramadaki tümü)\n")
# ---- her olayda sinyal veren coin'ler ----
ATES = {}
for t in EV:
    a = []
    for s in SYMS:
        X = EX[s]
        if t in X.index and X.y4.notna().get(t, False):
            ks = [k for k in ("star", "u4", "acls") if bool(X.at[t, k])]
            if ks: a.append((s, ks))
    ATES[t] = a
yaz(f"En az bir coin'in de sinyal verdiği olay oranı: %{100*np.mean([len(v) > 0 for v in ATES.values()]):.0f} · olay başına ort. coin: {np.mean([len(v) for v in ATES.values()]):.1f}")
# ---- dakikalık fiyatlar (yalnız gereken dakikalar) ----
def gerekli(sym, times):
    out = set()
    for t in times:
        for d in (0, 6): out.add(t + pd.Timedelta(minutes=d)); out.add(t + pd.Timedelta(hours=H, minutes=d))
    return sorted(out)
NEED = {"BTCUSDT": gerekli("BTCUSDT", EV)}
for s in SYMS: NEED[s] = gerekli(s, [t for t, v in ATES.items() if any(x[0] == s for x in v)])
def ay_fiyat(sym, ym):
    for _ in range(3):
        try:
            r = requests.get(f"https://data.binance.vision/data/spot/monthly/klines/{sym}/1m/{sym}-1m-{ym}.zip", timeout=60)
            if r.status_code == 404: return None
            r.raise_for_status(); z = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=[0, 4])
            ot = d[0].astype("float64").values; ot = np.where(ot > 1e14, ot / 1000, ot)
            return pd.Series(d[4].astype(float).values, index=pd.to_datetime(ot, unit="ms", utc=True) + pd.Timedelta(minutes=1))
        except Exception: time.sleep(2)
    return None
cur_m = pd.Timestamp.now(tz="UTC").normalize().replace(day=1)
if os.environ.get("YEREL"):                                                                   # yerel duman testi (Bitstamp dakikası her coin yerine)
    _MM = pd.read_pickle("/home/claude/lab2/data/m_1m.pkl").close
    def ay_fiyat(sym, ym): p_ = pd.Period(ym, "M"); return _MM[(_MM.index >= p_.start_time.tz_localize("UTC")) & (_MM.index < p_.end_time.tz_localize("UTC"))]
    def fetch_1m(a, b, sym=None): return None
def coin_fiyat(sym):
    ts = NEED[sym]
    if not ts: return sym, pd.Series(dtype=float)
    yms = sorted({t.strftime("%Y-%m") for t in ts}); parts = []
    for ym in yms:
        if pd.Timestamp(ym + "-01", tz="UTC") >= cur_m:
            m = fetch_1m(pd.Timestamp(ym + "-01", tz="UTC").timestamp() * 1000, time.time() * 1000, sym=sym); s_ = m.close if m is not None else None
        else: s_ = ay_fiyat(sym, ym)
        if s_ is not None: parts.append(s_[s_.index.isin(pd.DatetimeIndex(ts))])
    P = pd.concat(parts) if parts else pd.Series(dtype=float); return sym, P[~P.index.duplicated()].sort_index()
with ThreadPoolExecutor(12) as ex: PX = dict(ex.map(coin_fiyat, ["BTCUSDT"] + SYMS))
yaz(f"Dakikalık fiyatlar alındı ({time.time()-T0:.0f} sn) · eksik dakika oranı: %{100*(1 - sum(len(PX[s]) for s in PX) / max(1, sum(len(NEED[s]) for s in NEED))):.1f}")
def getiri(sym, t, d):
    P = PX[sym]; a, b = t + pd.Timedelta(minutes=d), t + pd.Timedelta(hours=H, minutes=d)
    return P[b] / P[a] - 1 if (a in P.index and b in P.index) else np.nan
# ---- stratejiler ----
def gecmis_isabet(sym, t, hist):                                           # yalnız SONUCU t'den önce belli olmuş olaylar
    h = [ok for (tt, ok) in hist.get(sym, []) if tt + pd.Timedelta(hours=H) <= t]
    return (np.mean(h), len(h)) if len(h) >= 10 else (np.nan, len(h))
FEES = {"spot %0,10": 0.0010, "spot BNB %0,075": 0.00075, "vadeli %0,05": 0.0005}
sonuc = []
for d in (0, 6):
    hist = {}; R = {k: [] for k in ["BTC al", "Tüm coin'ler (eşit)", "Canlı 🤝 listesi (eşit)", "Geçmişi en iyi 1 coin", "Geçmişi en iyi 3 coin (eşit)"]}
    for t in EV:
        rb = getiri("BTCUSDT", t, d)
        if np.isnan(rb): continue
        R["BTC al"].append((t, rb))
        cs = [(s, ks, getiri(s, t, d)) for s, ks in ATES[t]]; cs = [c for c in cs if not np.isnan(c[2])]
        if cs:
            R["Tüm coin'ler (eşit)"].append((t, np.mean([c[2] for c in cs])))
            cl = [c for c in cs if any((c[0], k) in LISTE for k in c[1])]
            if cl: R["Canlı 🤝 listesi (eşit)"].append((t, np.mean([c[2] for c in cl])))
            sc = sorted([(gecmis_isabet(c[0], t, hist), c) for c in cs], key=lambda x: (-(x[0][0] if not np.isnan(x[0][0]) else -1), -x[0][1]))
            sc = [x for x in sc if not np.isnan(x[0][0])]
            if sc: R["Geçmişi en iyi 1 coin"].append((t, sc[0][1][2])); R["Geçmişi en iyi 3 coin (eşit)"].append((t, np.mean([x[1][2] for x in sc[:3]])))
        for s, ks, r in cs: hist.setdefault(s, []).append((t, r > 0))
    for k, v in R.items():
        if len(v) < 10: continue
        T = pd.DataFrame(v, columns=["t", "g"])
        for per, (a, b) in {"2020–23": (A0, A24), "2024+": (A24, pd.Timestamp("2030-01-01", tz="UTC"))}.items():
            x = T[(T.t >= a) & (T.t < b)]
            if len(x) < 10: continue
            wk = (min(b, EV[-1]) - max(a, EV[0])).days / 7; yrs = wk / 52.18
            for fn, fee in FEES.items():
                net = x.g.values - 2 * fee; eq = np.cumprod(1 + net); lo, hi = wboot(net, x.t.values)
                sonuc.append(dict(gecikme=f"{d} dk", strateji=k, donem=per, komisyon=fn, islem=len(x), haftada=len(x) / wk, isabet=100 * (x.g > 0).mean(), brut=100 * x.g.mean(),
                                  net=100 * net.mean(), alt=100 * lo, ust=100 * hi, yillik=100 * (eq[-1] ** (1 / yrs) - 1), maxdd=100 * (eq / np.maximum.accumulate(eq) - 1).min()))
S = pd.DataFrame(sonuc)
for d in ("6 dk", "0 dk"):
    yaz(f"\n## {'Gerçekçi: mesaj :06’da gelir, giriş-çıkış o dakika' if d == '6 dk' else 'İyimser: saat kapanışında giriş-çıkış'} ({d})")
    for per in ("2020–23", "2024+"):
        x = S[(S.gecikme == d) & (S.donem == per)]
        b = x[x.komisyon == "spot %0,10"].set_index("strateji")[["islem", "haftada", "isabet", "brut", "maxdd"]].rename(columns={"maxdd": "maxDD % (spot)"})
        n = x.pivot_table(index="strateji", columns="komisyon", values="net"); y = x.pivot_table(index="strateji", columns="komisyon", values="yillik"); a = x[x.komisyon == "vadeli %0,05"].set_index("strateji")[["alt", "ust"]]
        tb = b.join(n.add_prefix("net% · ")).join(y.add_prefix("yıllık% · ")).join(a.rename(columns={"alt": "vadeli net alt", "ust": "vadeli net üst"}))
        yaz(f"\n### {per}\n```\n" + tb.round(3).to_string() + "\n```")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn · brüt/net = işlem başı ortalama % (4 saat) · alt/üst = haftalık blok bootstrap %90 aralığı_")
open("arastirma3_sonuc.md", "w").write("\n".join(L) + "\n")
