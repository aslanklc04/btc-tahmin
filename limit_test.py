# limit_test.py — EMİR TÜRÜ TESTİ: aynı sinyaller, piyasa emri mi limit emir mi? (canlı sisteme dokunmaz)
# Sinyaller (önceden sabit): BTC ⭐ (8 s) · BTC 4s Çok güçlü ↑ (4 s) · coin ⭐ (8 s) · coin 4s ÇG↑ (4 s) · 🤝 BTC güçlüyken coin (4 s) — canlı listedeki coin'ler.
# Mesaj :06'da gelir. Piyasa emri: o dakikanın kapanışından al, süre bitince :06'da sat (vadeli taker %0,05 her yön).
# Limit emir: alış limiti o anki fiyattan (ya da %0,1 aşağıdan) verilir; sonraki W dakikada fiyat limitin ALTINA inerse dolar (yalnız dokunmak yetmez — temkinli).
#   Dolmazsa işlem yok. Çıkışta limit satış o anki fiyattan, W dakikada fiyat ÜSTÜNE çıkarsa dolar; çıkmazsa W sonunda piyasa emriyle kapanır.
#   Limit komisyonu (maker) %0,02, piyasa %0,05. Fonlama hesaba katılmadı (8 saatte ~%0,01).
# Asıl soru: komisyondan kazanılan, kaçan (dolmayan) işlemlerin kaybından büyük mü? → "sinyal başına net" (dolmayan = 0) karşılaştırılır.
import os, io, glob, zipfile, time, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
YEREL = bool(os.environ.get("YEREL"))
EX = {os.path.basename(p)[5:-4]: pd.read_pickle(p) for p in glob.glob("art/**/disa_*USDT.pkl", recursive=True)}
LISTE = open("durum/coin_listesi.txt").read().split() if os.path.exists("durum/coin_listesi.txt") else []
COINS = [s for s in LISTE if s in EX] or [s for s in EX if s != "BTCUSDT"]
A0, A24 = pd.Timestamp("2020-01-01", tz="UTC"), pd.Timestamp("2024-01-01", tz="UTC")
def ev(X, col, H):
    m = X[col].fillna(False).astype(bool).values & X[f"y{H}"].notna().values; idx = X.index[events(m, H)]; return idx[idx >= A0]
B = EX["BTCUSDT"]; SIG = {}
SIG["BTC ⭐ (8 saat)"] = [("BTCUSDT", t, 8) for t in ev(B, "star", 8)]
SIG["BTC 4s Çok güçlü ↑ (4 saat)"] = [("BTCUSDT", t, 4) for t in ev(B, "u4", 4)]
SIG["Coin ⭐ (8 saat)"] = [(s, t, 8) for s in COINS for t in ev(EX[s], "star", 8)]
SIG["Coin 4s Çok güçlü ↑ (4 saat)"] = [(s, t, 4) for s in COINS for t in ev(EX[s], "u4", 4)]
ojt = []
for t in ev(B, "u4", 4):
    for s in COINS:
        X = EX[s]
        if t in X.index and pd.notna(X.at[t, "y4"]) and bool(X.loc[t, ["star", "u4", "acls"]].fillna(False).astype(bool).any()): ojt.append((s, t, 4))
SIG["🤝 BTC güçlüyken coin (4 saat)"] = ojt
yaz(f"# 🧾 Limit emir mi, piyasa emri mi? — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}")
yaz("Sinyaller: " + " · ".join(f"{k}: {len(v)}" for k, v in SIG.items()) + f" · coin'ler: {' '.join(c[:-4] for c in COINS)}\n")
# ---- dakikalık yüksek/düşük/kapanış (yalnız gereken pencereler) ----
W = 60; MK = lambda ts: int(ts.timestamp() // 60)                                     # dakika anahtarı = kapanış dakikası
NEED = {}
for v in SIG.values():
    for s, t, H in v:
        k0, k1 = MK(t) + 6, MK(t) + 60 * H + 6; NEED.setdefault(s, []).extend([np.arange(k0, k0 + W + 1), np.arange(k1, k1 + W + 1)])
NEED = {s: np.unique(np.concatenate(v)) for s, v in NEED.items()}
cur_m = pd.Timestamp.now(tz="UTC").normalize().replace(day=1)
def api_1m(sym, a, b):
    rows, cur, end = [], int(a.timestamp() * 1000), int(b.timestamp() * 1000)
    while cur < end:
        dt = None
        for url in EP:
            try:
                r = requests.get(url, params=dict(symbol=sym, interval="1m", startTime=cur, endTime=end, limit=1000), timeout=20)
                if r.status_code == 200: dt = r.json(); break
            except Exception: pass
        if not dt: break
        rows += dt; cur = dt[-1][0] + 60_000
        if len(dt) < 1000: break
    return pd.DataFrame([[x[0], x[2], x[3], x[4]] for x in rows]) if rows else None
def zip_1m(sym, ym):
    for _ in range(3):
        try:
            r = requests.get(f"https://data.binance.vision/data/spot/monthly/klines/{sym}/1m/{sym}-1m-{ym}.zip", timeout=90)
            if r.status_code == 404: return None
            r.raise_for_status(); z = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=[0, 2, 3, 4]); d.columns = [0, 1, 2, 3]; return d
        except Exception: time.sleep(3)
    return None
if YEREL:
    _MM = pd.read_pickle("/home/claude/lab2/data/m_1m.pkl").close; _rg = np.random.default_rng(1)
    _K = (_MM.index.as_unit("s").asi8 // 60).astype(np.int64)
def ay(arg):
    sym, ym, keys = arg; a = pd.Timestamp(ym + "-01", tz="UTC"); b = a + pd.offsets.MonthBegin(1)
    if YEREL:
        m = np.isin(_K, keys); c = _MM.values[m]; e = np.abs(_rg.normal(0, 0.0007, len(c))) * c
        return pd.DataFrame({"h": c + e, "l": c - e, "c": c}, index=_K[m])
    d = zip_1m(sym, ym) if a < cur_m else None
    if d is None: d = api_1m(sym, a, min(b, pd.Timestamp.now(tz="UTC")))
    if d is None: return None
    ot = pd.to_numeric(d[0], errors="coerce").values.astype("float64"); ot = np.where(ot > 1e14, ot / 1000, ot)
    k = (ot // 60_000).astype(np.int64) + 1; m = np.isin(k, keys)
    return pd.DataFrame({"h": pd.to_numeric(d[1]).values[m], "l": pd.to_numeric(d[2]).values[m], "c": pd.to_numeric(d[3]).values[m]}, index=k[m])
jobs = []
for s, keys in NEED.items():
    mon = pd.to_datetime(keys * 60, unit="s", utc=True).strftime("%Y-%m")
    for ym in sorted(set(mon)): jobs.append((s, ym, keys[mon == ym]))
with ThreadPoolExecutor(1 if YEREL else 16) as ex: res = list(ex.map(ay, jobs))
PX = {}
for (s, ym, _), d in zip(jobs, res):
    if d is not None and len(d): PX.setdefault(s, []).append(d)
PX = {s: (lambda D: D[~D.index.duplicated()].sort_index())(pd.concat(v)) for s, v in PX.items()}
bulunan = sum(len(PX.get(s, [])) for s in NEED); gerek = sum(len(v) for v in NEED.values())
yaz(f"Dakikalık veri: {len(jobs)} ay-dosyası · bulunan dakika %{100*bulunan/gerek:.1f} · {time.time()-T0:.0f} sn\n")
# ---- işlem benzetimi ----
TK, MKR = 0.0005, 0.0002
VAR = {"Piyasa emri (iki yön %0,05)": None, "Limit · anlık fiyat · 30 dk": (0.0, 30), "Limit · anlık fiyat · 60 dk": (0.0, 60), "Limit · %0,1 aşağıdan · 60 dk": (0.001, 60)}
def benzet(s, t, H):
    P = PX.get(s)
    if P is None: return None
    k0, k1 = MK(t) + 6, MK(t) + 60 * H + 6
    if k0 not in P.index or k1 not in P.index: return None
    pin, pout = P.c.at[k0], P.c.at[k1]; gm = pout / pin - 1; out = {"Piyasa emri (iki yön %0,05)": (True, gm, gm - 2 * TK)}
    for ad, (off, w) in [(k, v) for k, v in VAR.items() if v]:
        lim = pin * (1 - off); win = P.l.loc[k0 + 1:k0 + w]
        if not len(win) or not (win.min() < lim): out[ad] = (False, np.nan, np.nan); continue
        wo = P.h.loc[k1 + 1:k1 + w]
        if len(wo) and wo.max() > pout: px_out, fo = pout, MKR
        else:
            ke = P.c.loc[k1:k1 + w]; px_out, fo = (ke.iloc[-1] if len(ke) else pout), TK
        g = px_out / lim - 1; out[ad] = (True, g, g - MKR - fo)
    out["_kacan_piyasa"] = gm; return out
rows = []
for sn, v in SIG.items():
    for s, t, H in v:
        o = benzet(s, t, H)
        if o is None: continue
        for ad in VAR: dol, g, n = o[ad]; rows.append(dict(sinyal=sn, sym=s, t=t, yol=ad, dolu=dol, brut=g, net=n, piyasa_brut=o["_kacan_piyasa"]))
R = pd.DataFrame(rows); yaz(f"Benzetilen sinyal-yol: {len(R)} · {time.time()-T0:.0f} sn")
# ---- özet ----
LAST = R.t.max(); DON = {"2020–23": (A0, A24), "2024+": (A24, LAST + pd.Timedelta(seconds=1))}
out = []
for (sn, ad), g in R.groupby(["sinyal", "yol"], sort=False):
    for pn, (a, b) in DON.items():
        x = g[(g.t >= a) & (g.t < b)]
        if len(x) < 20: continue
        f = x[x.dolu]; wk = (b - a).days / 7; lo, hi = wboot(f.net.values, f.t.values) if len(f) >= 5 else (np.nan, np.nan)
        r = dict(sinyal=sn, yol=ad, donem=pn, sinyal_say=len(x), dolan=100 * x.dolu.mean(), islem=len(f), haftada=len(f) / wk, isabet=100 * (f.brut > 0).mean(), brut=100 * f.brut.mean(),
                 net_islem=100 * f.net.mean(), alt=100 * lo, ust=100 * hi, net_sinyal=100 * f.net.sum() / len(x), kacan_brut=100 * x[~x.dolu].piyasa_brut.mean() if (~x.dolu).any() else np.nan)
        if sn.startswith("BTC"):
            e = np.cumprod(1 + f.sort_values("t").net.values); yrs = (b - a).days / 365.25; r["yıllık"] = 100 * (e[-1] ** (1 / yrs) - 1); r["maxDD"] = 100 * (e / np.maximum.accumulate(np.r_[1, e])[1:] - 1).min()
        out.append(r)
S = pd.DataFrame(out)
for sn in SIG:
    yaz(f"\n## {sn}")
    for pn in DON:
        x = S[(S.sinyal == sn) & (S.donem == pn)].set_index("yol").drop(columns=["sinyal", "donem"])
        if len(x): yaz(f"### {pn}\n```\n" + x.round(3).to_string() + "\n```")
yaz("\n## Karar (sinyal başına net — dolmayan işlem 0 sayılır; limit, piyasa emrinden iki dönemde de iyiyse ✅)")
for sn in SIG:
    for ad in [k for k, v in VAR.items() if v]:
        z = S[(S.sinyal == sn)].pivot_table(index="donem", columns="yol", values="net_sinyal")
        if ad not in z or "Piyasa emri (iki yön %0,05)" not in z or len(z) < 2: continue
        d = z[ad] - z["Piyasa emri (iki yön %0,05)"]; ok = bool((d > 0).all())
        k24 = S[(S.sinyal == sn) & (S.yol == ad) & (S.donem == "2024+")]
        yaz(f"- {'✅' if ok else '❌'} {sn} · {ad}: fark (puan) 2020–23 {d.get('2020–23', np.nan):+.3f} · 2024+ {d.get('2024+', np.nan):+.3f}"
            + (f" · 2024+ dolan %{k24.dolan.iloc[0]:.0f}, net/işlem %{k24.net_islem.iloc[0]:.3f}, kaçanların piyasa brütü %{k24.kacan_brut.iloc[0]:.3f}" if len(k24) else ""))
yaz(f"\n_Süre: {time.time()-T0:.0f} sn · brüt/net % = işlem başı · net_sinyal = toplam net / sinyal sayısı · kacan_brut = dolmayan işlemlerin piyasa emriyle brüt getirisi (pozitifse kaçanlar iyi işlemlermiş) · alt/üst = haftalık blok bootstrap %90_")
open("limit_sonuc.md", "w").write("\n".join(L) + "\n")
