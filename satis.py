# satis.py — DÜŞÜŞTE SATIŞ (vadeli kısa pozisyon) SİNYALİ: "satıcılar sabırsız" fikri + ABD satışı, para testi (canlı sisteme dokunmaz)
# Kısa pozisyon: olaydan 1 saat sonra aç, 24 saat tut, limit komisyon %0,02×2; fonlama dahil (fonlama > 0 iken kısa pozisyon fonlama ALIR).
# BTC kuralları (önceden sabit):
#   B1 akış/defter z ≤ −2 (sabırsız satıcı + sabırlı alıcı; vadeli emir defteri — canlıda hesaplanabilirliği ayrıca yoklanır)
#   B2 Coinbase primi z ≤ −2 (ABD güçlü satıyor) · B3 spot satıcı baskısı 24 s z ≤ −2 · B4 B3 ve Coinbase primi z ≤ 0
#   B5 spot satıcı baskısı 4 s z ≤ −2 ve Coinbase primi z ≤ −1 · B6 B2 veya B3
# Coin kuralları (11 coin birlikte): C1 coin spot satıcı baskısı 24 s z ≤ −2 · C2 C1 ve BTC Coinbase primi z ≤ 0 · C3 BTC Coinbase primi z ≤ −2 → coin'leri sat
#   C4 coin'in KENDİ Coinbase primi z ≤ −2 (yalnız 2024+, seçim dönemi yok → keşif)
# Karar: ≤2023'te (B1 için 2023) net > 0 ve 2024+'da net > 0 ve %90 alt sınır > 0 → ✅. 2026 ayrıca.
import io, re, time, zipfile, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
def log(*a): print(f"[{time.time()-T0:5.0f} sn]", *a, flush=True)
ea = open("emir_akisi.py").read(); exec(ea[ea.index("SYMS = ["):ea.index("with ThreadPoolExecutor(6) as ex:\n    fs")])      # SYMS, kl, s3_list, zraw, csv_, vadeli, defter_gun
bo = open("bosluklar2.py").read(); exec(bo[bo.index("UA = "):bo.index("def kl(sym):")]); exec(bo[bo.index("def coinbase_1h"):bo.index("def upbit_1h")])
# ---- canlı erişim yoklaması (GitHub sunucusu ABD'de) ----
yok = {}
for ad, url in (("vadeli emir defteri (fapi depth)", "https://fapi.binance.com/fapi/v1/depth?symbol=BTCUSDT&limit=5"), ("vadeli mum (fapi klines)", "https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=1h&limit=2"),
                ("spot emir defteri (data-api depth)", "https://data-api.binance.vision/api/v3/depth?symbol=BTCUSDT&limit=5"), ("spot mum (data-api klines)", "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=2")):
    try: yok[ad] = requests.get(url, timeout=15).status_code
    except Exception as e: yok[ad] = type(e).__name__
def cb_coin(prod, bas=pd.Timestamp("2023-10-01", tz="UTC")):
    out, cur, end = [], bas, pd.Timestamp.now(tz="UTC"); s = requests.Session(); s.headers.update(UA); fails = 0
    try:
        if s.get(f"https://api.exchange.coinbase.com/products/{prod}", timeout=15).status_code != 200: return None
    except Exception: return None
    while cur < end and fails < 30:
        nx = min(cur + pd.Timedelta(hours=300), end)
        try:
            r = s.get(f"https://api.exchange.coinbase.com/products/{prod}/candles", params=dict(granularity=3600, start=cur.isoformat(), end=nx.isoformat()), timeout=20)
            if r.status_code == 429: time.sleep(1); continue
            r.raise_for_status(); out += r.json(); cur = nx; time.sleep(0.12)
        except Exception: fails += 1; time.sleep(2)
    if not out: return None
    d = pd.DataFrame(out, columns=["t", "low", "high", "open", "close", "volume"]).drop_duplicates("t"); return pd.Series(d.close.values.astype(float), index=pd.to_datetime(d.t, unit="s", utc=True) + pd.Timedelta(hours=1)).sort_index()
def fonlama(sym):
    fs = "1000SHIBUSDT" if sym == "SHIBUSDT" else sym
    keys = [k for k in s3_list(f"data/futures/um/monthly/fundingRate/{fs}/") if k.endswith(".zip")]
    with ThreadPoolExecutor(8) as ex: parts = [csv_(r) for r in ex.map(zraw, keys) if r]
    if not parts: return sym, None
    P = pd.concat(parts); ot = pd.to_numeric(P[0], errors="coerce").astype(float).values; ot = np.where(ot > 1e14, ot / 1000, ot)
    return sym, pd.Series(pd.to_numeric(P[2], errors="coerce").values, index=pd.to_datetime(ot, unit="ms", utc=True).floor("h")).groupby(level=0).last().sort_index()
with ThreadPoolExecutor(8) as ex:
    f_sp = ex.submit(lambda: dict(ThreadPoolExecutor(6).map(kl, SYMS))); f_cb = ex.submit(coinbase_1h); f_fu = ex.submit(vadeli, "BTCUSDT")
    f_fr = ex.submit(lambda: dict(ThreadPoolExecutor(4).map(fonlama, SYMS))); f_own = ex.submit(lambda: dict(ThreadPoolExecutor(4).map(lambda s: (s, cb_coin(s[:-4] + "-USD")), SYMS[1:])))
    bk = [k for k in s3_list("data/futures/um/daily/bookDepth/BTCUSDT/") if k.endswith(".zip")]
    SP = f_sp.result(); CB = f_cb.result(); FU = f_fu.result()[1]; FR = f_fr.result(); OWN = f_own.result(); log("veri tamam")
with ThreadPoolExecutor(24) as ex: BK = [b for b in ex.map(defter_gun, bk) if b is not None and len(b)]
BOOK = pd.concat(BK).groupby(level=0).mean().sort_index(); BOOK.index = pd.DatetimeIndex(BOOK.index).as_unit("ns")
A23, A24, A26 = (pd.Timestamp(x, tz="UTC") for x in ("2023-01-01", "2024-01-01", "2026-01-01")); H, LMT = 24, 0.0002
def zs(s): return (s - s.rolling(720, min_periods=168).mean()) / (s.rolling(720, min_periods=168).std() + 1e-12)
def baski(d, k): q = d.qv.rolling(k, min_periods=k // 2 or 1).sum(); return (2 * d.tbq.rolling(k, min_periods=k // 2 or 1).sum() - q) / (q + 1e-12)
B = SP["BTCUSDT"]; ix = B.index; ZCB = zs(np.log(CB.reindex(ix) / B.close))
fu = FU.copy(); fu.index = pd.DatetimeIndex(fu.index).as_unit("ns"); fu = fu.reindex(BOOK.index)
tb4, ts4 = fu.tbq.rolling(4, min_periods=2).sum(), (fu.qv - fu.tbq).rolling(4, min_periods=2).sum(); bid, ask = BOOK.bid1.rolling(4, min_periods=2).mean(), BOOK.ask1.rolling(4, min_periods=2).mean()
ZAD = zs(np.log(tb4 / bid) + np.log(ask / ts4)).reindex(ix)
def islemler(sym, mask, kural):
    d = SP[sym]; c = d.close.values; n = len(d); fr = FR.get(sym); m = np.nan_to_num(mask.reindex(d.index).values.astype(float)).astype(bool) & (np.arange(n) + H + 1 < n)
    out = []
    for i in events(m, H):
        a, b = d.index[i + 1], d.index[i + H + 1]
        if not (np.isfinite(c[i + 1]) and np.isfinite(c[i + H + 1])): continue
        g = -(c[i + H + 1] / c[i + 1] - 1); fon = float(fr[(fr.index > a) & (fr.index <= b)].sum()) if fr is not None else 0.0
        out.append(dict(kural=kural, coin=sym[:-4], t=d.index[i], g=g, net=g - 2 * LMT + fon, fon=fon))
    return out
R = []
zsb24, zsb4 = zs(baski(B, 24)), zs(baski(B, 4))
KB = {"B1 akış/defter z ≤ −2 (vadeli defter)": ZAD <= -2, "B2 Coinbase primi z ≤ −2": ZCB <= -2, "B3 spot satıcı baskısı 24 s z ≤ −2": zsb24 <= -2,
      "B4 B3 + Coinbase primi z ≤ 0": (zsb24 <= -2) & (ZCB <= 0), "B5 spot satıcı baskısı 4 s z ≤ −2 + Coinbase z ≤ −1": (zsb4 <= -2) & (ZCB <= -1), "B6 B2 veya B3": (ZCB <= -2) | (zsb24 <= -2)}
for k, m in KB.items(): R += islemler("BTCUSDT", m, k)
for s in SYMS[1:]:
    d = SP[s]; z24 = zs(baski(d, 24)); zb = ZCB.reindex(d.index)
    R += islemler(s, z24 <= -2, "C1 coin spot satıcı baskısı 24 s z ≤ −2"); R += islemler(s, (z24 <= -2) & (zb <= 0), "C2 C1 + BTC Coinbase primi z ≤ 0")
    R += islemler(s, zb <= -2, "C3 BTC Coinbase primi z ≤ −2 → coin sat")
    if OWN.get(s) is not None: R += islemler(s, zs(np.log(OWN[s].reindex(d.index) / d.close)) <= -2, "C4 coin'in kendi Coinbase primi z ≤ −2 (keşif)")
R = pd.DataFrame(R); yaz(f"# 🔻 Düşüşte satış (kısa pozisyon) sinyali — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nCanlı erişim (GitHub sunucusundan, HTTP kodu): " + " · ".join(f"{k}: {v}" for k, v in yok.items()) + f"\n{len(R)} işlem · {time.time()-T0:.0f} sn\n")
out = []
for k, g in R.groupby("kural", sort=False):
    sel_a = A23 if k.startswith("B1") else pd.Timestamp("2017-01-01", tz="UTC")
    for pn, (a, b) in {"seçim (≤2023)": (sel_a, A24), "2024+": (A24, R.t.max() + pd.Timedelta(hours=1)), "2026": (A26, R.t.max() + pd.Timedelta(hours=1))}.items():
        x = g[(g.t >= a) & (g.t < b)]
        if len(x) < 5: continue
        wk = (b - max(a, g.t.min())).days / 7; lo, _ = wboot(x.net.values, x.t.values) if len(x) >= 10 else (np.nan, np.nan); r = dict(kural=k, donem=pn, islem=len(x), haftada=len(x) / max(wk, 1), isabet=100 * (x.g > 0).mean(), brut=100 * x.g.mean(), fonlama=100 * x.fon.mean(), net=100 * x.net.mean(), alt=100 * lo)
        if k.startswith("B"):
            e = np.cumprod(1 + x.sort_values("t").net.values); yrs = max((b - max(a, g.t.min())).days / 365.25, 0.1); r["yıllık"] = 100 * (e[-1] ** (1 / yrs) - 1); r["maxDD"] = 100 * (e / np.maximum.accumulate(np.r_[1, e])[1:] - 1).min()
        out.append(r)
S = pd.DataFrame(out); yaz("## Sonuçlar (işlem başı %, kısa pozisyon: fiyat düşerse kazanç · isabet = fiyatın düştüğü işlem oranı)\n```\n" + S.set_index(["kural", "donem"]).round(2).to_string() + "\n```")
yaz("\n## Karar (önceden sabit: seçimde net > 0, 2024+'da net > 0 ve alt sınır > 0)")
for k in S.kural.unique():
    p = S[S.kural == k].set_index("donem")
    if "2024+" not in p.index: continue
    c1 = ("seçim (≤2023)" in p.index and p.loc["seçim (≤2023)", "net"] > 0) or k.startswith("C4"); c2 = p.loc["2024+", "net"] > 0 and p.loc["2024+", "alt"] > 0
    z26 = f" · 2026: isabet %{p.loc['2026','isabet']:.0f}, net %{p.loc['2026','net']:+.2f} ({int(p.loc['2026','islem'])})" if "2026" in p.index else ""
    yaz(f"- {'✅' if c1 and c2 else '❌'} {k}: 2024+ haftada {p.loc['2024+','haftada']:.1f}, isabet %{p.loc['2024+','isabet']:.0f}, net %{p.loc['2024+','net']:+.2f} (alt {p.loc['2024+','alt']:+.2f}){z26}" + (" · seçim dönemi yok (keşif)" if k.startswith("C4") else ""))
z_now = {"Coinbase primi z": ZCB.dropna().iloc[-1], "spot satıcı baskısı 24 s z": zsb24.dropna().iloc[-1], "akış/defter z (arşiv, 1 gün gecikmeli)": ZAD.dropna().iloc[-1]}
yaz("\nŞu an (BTC): " + " · ".join(f"{k} {v:+.2f}" for k, v in z_now.items()) + f"\n_Süre: {time.time()-T0:.0f} sn_")
open("satis_sonuc.md", "w").write("\n".join(L) + "\n")
