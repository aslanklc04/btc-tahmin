# d10_canli.py — 📆 D10 BTC GÜNLÜK (yalnız PANEL — izleme, Telegram'a gitmez; kullanıcı kararı 20.10.2026)
# Kural (gunluk.py, 20.10.2026): BTC günlük kapanışı 200 günlük ortalamanın ÜSTÜNDE (trend yukarı) VE Coinbase BTC primi günlük ortalamasının z'si (son 90 gün) ≥ 1
#   (ABD güçlü alıyor) → 7 gün tut. Test: 2022–25 %68 · +%3,7 (37 sinyal) · 2026 %57 (7 sinyal) → %65 şartını 2026'da geçmedi; canlıda izlenir, karne ölçer.
# Günde bir kez (UTC 00:00 kapanışından sonraki ilk saatlik çalışma), 7 gün içinde tekrar sayılmaz. Durum: durum/d10_durum.json
import os, json, time, requests, numpy as np, pandas as pd
from ortak import EP, fetch_1h, tg_send
F = "durum/d10_durum.json"; now = pd.Timestamp.now(tz="UTC"); gun = now.floor("D")
try: D = json.load(open(F))
except Exception: D = {}
if D.get("son_kontrol") == str(gun) and not os.environ.get("D10_KURU"): print("📆 D10: bugün kontrol edildi"); raise SystemExit(0)
k = None
for url in EP:
    try:
        r = requests.get(url, params=dict(symbol="BTCUSDT", interval="1d", limit=400), timeout=20)
        if r.status_code == 200: k = r.json(); break
    except Exception: pass
if not k: raise RuntimeError("Binance günlük veri alınamadı")
c = pd.Series([float(x[4]) for x in k], index=pd.to_datetime([x[0] for x in k], unit="ms", utc=True) + pd.Timedelta(days=1)); c = c[c.index <= gun]
ma200 = c.rolling(200, min_periods=150).mean()
out, s = [], requests.Session()
for j in range(10, 0, -1):
    a, b = gun - pd.Timedelta(hours=300 * j), gun - pd.Timedelta(hours=300 * (j - 1))
    for _ in range(3):
        r = s.get("https://api.exchange.coinbase.com/products/BTC-USD/candles", params=dict(granularity=3600, start=a.isoformat(), end=b.isoformat()), timeout=20)
        if r.status_code == 200: out += r.json(); break
        time.sleep(1.5)
cb = pd.DataFrame(out, columns=["t", "low", "high", "open", "close", "volume"]).drop_duplicates("t")
cb = pd.Series(cb.close.values.astype(float), index=pd.to_datetime(cb.t, unit="s", utc=True) + pd.Timedelta(hours=1)).sort_index()
bn = fetch_1h((gun - pd.Timedelta(hours=3020)).timestamp() * 1000, gun.timestamp() * 1000 + 1).close
p = np.log(cb / bn.reindex(cb.index)).dropna(); p = p[p.index <= gun]
pd_ = p.resample("1D", label="right", closed="right").mean(); z = (pd_ - pd_.rolling(90, min_periods=30).mean()) / (pd_.rolling(90, min_periods=30).std() + 1e-12)
cs, ms, zs = float(c.iloc[-1]), float(ma200.iloc[-1]), float(z.get(gun, np.nan))
kosul = bool(cs > ms and np.isfinite(zs) and zs >= 1)
son = pd.Timestamp(D["son_sinyal"]) if D.get("son_sinyal") else None; yeni = son is None or gun - son >= pd.Timedelta(days=7)
print(f"📆 D10 {gun:%d.%m.%Y}: BTC {cs:,.0f} · 200 g ort. {ms:,.0f} ({'üstünde' if cs > ms else 'altında'}) · günlük prim z {zs:+.2f} → {'SİNYAL' if kosul and yeni else ('koşul var, 7 gün dolmadı' if kosul else 'yok')}")
if kosul and yeni:
    txt = (f"📆 D10 BTC GÜNLÜK (yalnız panel — izleme) — {gun.tz_convert('Europe/Istanbul'):%d.%m.%Y}\nBTC trendde (200 günlük ortalamanın üstünde) VE ABD güçlü alıyor (günlük Coinbase primi z {zs:+.1f}) → 7 gün tut\n"
           f"Test: 2022–25 %68 · işlem başı +%3,7 (37 sinyal) · 2026 %57 (7 sinyal) — %65 şartını geçmedi, canlıda izleniyor.")
    if not os.environ.get("D10_KURU"): tg_send(txt, etiket=f"📆 D10 BTC 7 gün (168 saat) · trend + ABD alıyor · prim z {zs:+.1f}", sinif="panel"); D["son_sinyal"] = str(gun)
    else: print(txt)
if not os.environ.get("D10_KURU"): D.update(son_kontrol=str(gun), son=dict(btc=cs, ma200=ms, z=zs)); json.dump(D, open(F, "w"))
