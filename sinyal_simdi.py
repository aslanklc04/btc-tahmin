# sinyal_simdi.py — 23.10.2026: kullanıcının yapıştırdığı mesajlardaki sinyaller şu an ne durumda? (yalnız bilgi, canlıya dokunmaz)
# 1 dakikalık Binance mumlarıyla: limit alış doldu mu (60 dk), 🎯 kâr-al'a değdi mi (ilk değme anı), değmeden önceki en derin düşüş,
# süre bittiyse çıkış fiyatı, bitmediyse şu anki fiyat. Saatler TR (UTC+3).
import requests, pandas as pd
TR = "Europe/Istanbul"; U = "https://data-api.binance.vision/api/v3/klines"
def t(s): return pd.Timestamp(s, tz=TR)
S = [  # (sınıf, coin, gönderim, çıkış, giriş, 🎯)
    *[("🔸 yedek 🌐🤝", c, "2026-10-23 00:08", "2026-10-23 04:06", g, k) for c, g, k in [
        ("YFI", 2138, 2154), ("ARPA", 0.01001, 0.01012), ("SUSHI", 0.2121, 0.2141), ("KSM", 3.940, 3.978), ("API3", 0.2612, 0.2644),
        ("JASMY", 0.004510, 0.004559), ("RLC", 0.6496, 0.6684), ("PUNDIX", 0.09580, 0.09653), ("ACH", 0.005220, 0.005270), ("LDO", 0.3799, 0.3843),
        ("ENS", 5.470, 5.519), ("METIS", 3.840, 3.891), ("ALT", 0.008350, 0.008532)]],
    ("📋 panelden 💵", "INJ", "2026-10-23 01:07", "2026-10-24 01:06", 7.921, 8.143),
    ("✅ ana 🌐🧪", "CAKE", "2026-10-23 05:07", "2026-10-24 05:06", 2.116, 2.170),
    ("📋 panelden 🧪", "SHIB", "2026-10-23 12:06", "2026-10-24 12:06", 0.0000051, 0.000005175)]
def mum(sym, a, b):
    rows, cur = [], int(a.timestamp() * 1000); son = int(b.timestamp() * 1000)
    while cur < son:
        x = requests.get(U, params=dict(symbol=sym, interval="1m", startTime=cur, endTime=son, limit=1000), timeout=20).json()
        if not isinstance(x, list) or not x: break
        rows += x; cur = x[-1][0] + 60_000
        if len(x) < 1000: break
    d = pd.DataFrame([r[:5] for r in rows], columns=["t", "a", "y", "d", "k"]).astype(float)
    d.index = pd.DatetimeIndex(pd.to_datetime(d.t, unit="ms", utc=True)).tz_convert(TR); return d
NOW = pd.Timestamp.now(tz=TR); o = [f"# Sinyaller şu an — {NOW:%d.%m %H:%M} TR (Binance 1 dk mum)\n",
    "| Sınıf | Coin | Giriş | 🎯 | Doldu mu | 🎯 değdi mi (saat) | 🎯 öncesi en derin düşüş | En yüksek | Durum | Sonuç |", "|---|---|---|---|---|---|---|---|---|---|"]
for sn, c, g0, c0, g, k in S:
    gt, ct = t(g0), t(c0); bitis = min(ct, NOW)
    try: d = mum(c + "USDT", gt, bitis)
    except Exception as e: o.append(f"| {sn} | {c} | {g:g} | {k:g} | veri yok ({type(e).__name__}) |||||| "); continue
    if d.empty: o.append(f"| {sn} | {c} | {g:g} | {k:g} | veri yok |||||| "); continue
    ilk = d[d.index < gt + pd.Timedelta(minutes=60)]; dol = ilk[ilk.d <= g]
    if dol.empty:
        pg = d.a.iloc[0]; h2 = d[d.y >= k]; r = 100 * (d.k.iloc[-1] / pg - 1)
        o.append(f"| {sn} | {c} | {g:g} | {k:g} | ❌ limit dolmadı (60 dk en düşük {ilk.d.min():g}) · piyasadan {pg:g} ({100 * (pg / g - 1):+.2f}%) alınsaydı → | "
                 + (f"✅ {h2.index[0]:%d.%m %H:%M}" if not h2.empty else "hayır") + f" | {100 * ((d[d.index <= h2.index[0]] if not h2.empty else d).d.min() / pg - 1):+.2f}% | {100 * (d.y.max() / pg - 1):+.2f}% | {'kapandı' if NOW >= ct else 'açık'} | "
                 + (f"✅ 🎯 +%{100 * (k / pg - 1):.2f}" if not h2.empty else f"{'✅' if r > 0.04 else '❌'} süre sonu {r:+.2f}%") + " |"); continue
    d2 = d[d.index >= dol.index[0]]; hit = d2[d2.y >= k]; ht = hit.index[0] if not hit.empty else None
    once = d2[d2.index <= ht] if ht is not None else d2; dd = 100 * (once.d.min() / g - 1); mx = 100 * (d2.y.max() / g - 1)
    son = d2.k.iloc[-1]; kap = NOW >= ct
    if ht is not None: sonuc = f"✅ 🎯 +%{100 * (k / g - 1):.2f}"; dur = "kapandı (🎯)"
    elif kap: r = 100 * (son / g - 1); sonuc = f"{'✅' if r > 0.04 else '❌'} süre sonu {r:+.2f}%"; dur = "kapandı (süre)"
    else: sonuc = f"⏳ şu an {100 * (son / g - 1):+.2f}% ({son:g})"; dur = f"açık → {ct:%d.%m %H:%M}"
    o.append(f"| {sn} | {c} | {g:g} | {k:g} | ✅ {dol.index[0]:%H:%M} | {f'✅ {ht:%d.%m %H:%M}' if ht is not None else 'hayır'} | {dd:+.2f}% | {mx:+.2f}% | {dur} | {sonuc} |")
print("\n".join(o)); open("sinyal_simdi_sonuc.md", "w").write("\n".join(o) + "\n")
