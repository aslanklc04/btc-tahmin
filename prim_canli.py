# prim_canli.py — HER SAAT (kucuk_canli.py'den sonra): 💵 ABD GÜÇLÜ ALIYOR → COİN AL (coin'in KENDİ Coinbase primi; araştırma: prim_coin.py, prim2.py · dal arastirma3).
# Prim = log(Coinbase COIN-USD / Binance COINUSDT), saatlik, son 720 saate göre z (ortak.cb_prim). Liste ve eşikler: durum/prim_acik.csv (coin başına tek kural).
# Kural: z ≥ eşik (2 ya da 3) → o coin'i AL, listedeki süre kadar (4 / 8 / 24 saat) tut. Aynı coin'de tutma süresi dolmadan yeni sinyal yok.
# Araştırma (gecikmesiz giriş, limit komisyon %0,02 × 2): 15 coin birlikte 2024+ 2628 işlem, isabet %54, işlem başı +%0,71 (alt +%0,50) · 2026 %54, +%0,62 · haftada ~18–20 sinyal.
# Her sinyal kaydedilir (giriş = mesaj anındaki fiyat, çıkış = süre sonundaki saat kapanışı); pazar 20:00'de haftalık özet.
import os, pickle, traceback, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import *
import ortak as _ortak
STATE_F, LISTE_F, FEE = "durum/prim.pkl", "durum/prim_acik.csv", 0.0002
def fmt(p):
    if not np.isfinite(p) or p <= 0: return "$?"
    if p >= 1000: return f"${p:,.0f}"
    if p >= 1: return f"${p:,.3f}"
    return f"${p:.{min(12, 3 - int(np.floor(np.log10(p))))}f}"
def anlik(sym, yedek=np.nan):
    for url in EP:
        try:
            r = requests.get(url.replace("klines", "ticker/price"), params=dict(symbol=sym), timeout=10)
            if r.status_code == 200: return float(r.json()["price"])
        except Exception: pass
    return yedek
def ozet(x): return f"{sum(e['ok'] for e in x)}/{len(x)} tuttu (%{100*sum(e['ok'] for e in x)/len(x):.0f}) · ort. net %{np.mean([e['net'] for e in x]):+.2f} · toplam %{np.sum([e['net'] for e in x]):+.1f}" if x else "sonuçlanan işlem yok"
def calis():
    kuru = os.environ.get("PRIM_KURU") == "1"
    if not os.path.exists(LISTE_F): print("prim_acik.csv yok"); return
    LS = pd.read_csv(LISTE_F)
    GP = {}
    if os.path.exists(STATE_F):
        try:
            with open(STATE_F, "rb") as f: GP = pickle.load(f)
        except Exception: GP = {}
    for k, v in (("log", []), ("tglog", []), ("last", {}), ("son", {})): GP.setdefault(k, v)
    GP.setdefault("start", pd.Timestamp.now(tz="UTC"))
    def tg(text, **kw):
        if kuru: print("---- (kuru) Telegram ----\n" + (f"[öncelik {kw.get('oncelik')} · {kw.get('etiket')}]\n" if kw else "") + text + "\n-------------------------"); return False
        ok = tg_send(text, **kw); GP["tglog"] = (GP["tglog"] + [dict(t=pd.Timestamp.now(tz="UTC"), tip=text.split("\n")[0][:70], ok=ok, info=_ortak.TG_LAST["info"])])[-10:]; return ok
    now = pd.Timestamp.now(tz="UTC"); tl = now.tz_convert(DISPLAY_TZ)
    with ThreadPoolExecutor(4) as ex: CB = dict(zip(LS.coin, ex.map(lambda c: cb_prim(c), LS.coin)))
    fire = []
    for _, r in LS.iterrows():
        d = CB.get(r.coin); z = cb_z(d)
        if not np.isfinite(z): GP["son"][r.coin] = dict(z=np.nan, bp=np.nan, hesap=now); continue
        t = pd.Timestamp(d["t"]).tz_convert("UTC") if pd.Timestamp(d["t"]).tzinfo else pd.Timestamp(d["t"], tz="UTC")
        GP["son"][r.coin] = dict(z=z, bp=d["bp"], hesap=now, t=t)
        if now - t > pd.Timedelta(hours=3): continue                                            # veri eski
        son = GP["last"].get(r.coin)
        if z >= r.esik and (son is None or t - son >= pd.Timedelta(hours=int(r.saat))):
            p = anlik(f"{r.coin}USDT"); GP["last"][r.coin] = t
            if np.isfinite(p): GP["log"].append(dict(t=t, coin=r.coin, p=p, H=int(r.saat), z=z))
            cikis = (t + pd.Timedelta(hours=int(r.saat), minutes=6)).tz_convert(DISPLAY_TZ)
            gr_ = float(r.net) + 200 * FEE; hz_ = hiz_notu(z)
            fire.append((z, r.coin, f"• {r.coin}: kendi primi z {z:+.1f} ({d['bp']:+.1f} baz puan) · limit ALIŞ {fmt(p)} · çıkış {cikis:%d.%m %H:%M} ({int(r.saat)} saat)"
                        + f" · {CIKIS_NOT} · geçmiş ort. sonuç +%{gr_:.2f}\n"
                        f"   Geçmiş 2024+: {int(r.n)} işlem, isabet %{r.isabet:.0f}, işlem başı +%{r.net:.2f} · 2026: {int(r.n26)} işlem, %{r.isabet26:.0f}, +%{r.net26:.2f}" + (f"\n   {hz_}" if hz_ else "")))
    if fire:
        fire.sort(key=lambda x: -x[0])                                                         # primi en yüksek olan üstte
        tg(f"💵🟢 ABD GÜÇLÜ ALIYOR → AL — {tl:%d.%m %H:%M}\nCoinbase'de bu coin(ler) için normalin çok üstünde prim ödeniyor (son 30 güne göre z ≥ eşik) · sıra: primi en yüksek olan üstte.\n" + "\n".join(x[2] for x in fire)
           + "\n⚠️ İsabet ~%55: kâr, kazançların kayıplardan büyük olmasından geliyor; tek işleme büyük para koyma, kaldıraçsız ya da düşük kaldıraç. Yatırım tavsiyesi değildir.",
           oncelik=sira_puani("💵", fire[0][0]), etiket="💵 ABD güçlü alıyor: " + ", ".join(f"{x[1]} (z {x[0]:+.1f})" for x in fire))
    # ---- sonuçlanan işlemler ----
    acik = [e for e in GP["log"] if "ok" not in e and now >= e["t"] + pd.Timedelta(hours=e["H"])]
    OO = {}
    for e in acik:
        try:
            if e["coin"] not in OO: OO[e["coin"]] = fetch_1h((now - pd.Timedelta(days=4)).timestamp() * 1000, now.timestamp() * 1000, sym=f"{e['coin']}USDT").close
            o = OO[e["coin"]]; te = e["t"] + pd.Timedelta(hours=e["H"])
            if te not in o.index and now - te < pd.Timedelta(hours=3): continue
            p2 = float(o.loc[te]) if te in o.index else float(o[o.index <= te].iloc[-1])
            e["ret"] = 100 * (p2 / e["p"] - 1); e["net"] = e["ret"] - 200 * FEE; e["ok"] = bool(e["ret"] > 0); e["p2"] = p2
        except Exception: traceback.print_exc()
    kap = [e for e in GP["log"] if "ok" in e]
    # ---- haftalık özet ----
    try:
        tlh = tl.floor("h")
        if GP["log"] and tlh.weekday() == 6 and tlh.hour >= 20 and (GP.get("last_weekly") is None or tlh - GP["last_weekly"] >= pd.Timedelta(days=6)):
            wk = [e for e in kap if now - e["t"] <= pd.Timedelta(days=8)]
            per = pd.DataFrame(wk).groupby("coin").agg(n=("ok", "size"), ok=("ok", "sum"), net=("net", "mean")) if wk else None
            tg(f"💵📊 ABD ALIYOR (kendi primi) — HAFTALIK\nSon 7 gün: {ozet(wk)}\nBaşlangıçtan ({GP['start'].tz_convert(DISPLAY_TZ):%d.%m}) beri: {ozet(kap)}"
               + ("\n" + " · ".join(f"{c} {int(r_.ok)}/{int(r_.n)} ({r_.net:+.2f})" for c, r_ in per.iterrows()) if per is not None else "") + "\n(giriş: mesaj anındaki fiyat · çıkış: süre sonu · limit komisyon dahil)")
            GP["last_weekly"] = tlh
    except Exception: traceback.print_exc()
    # ---- panel ----
    md = ("\n## 💵 ABD güçlü alıyor → coin AL (kendi Coinbase primi, saatlik)\n"
          f"Başlangıçtan ({GP['start'].tz_convert(DISPLAY_TZ):%d.%m.%Y}) beri sonuçlanan: **{ozet(kap)}**\n\n| Coin | Kendi primi z | Eşik | Tut | Durum | Geçmiş 2024+ (isabet · işlem başı net) |\n|---|---|---|---|---|---|\n")
    for _, r in LS.iterrows():
        s = GP["son"].get(r.coin, {}); z = s.get("z", np.nan); ac = [e for e in GP["log"] if e["coin"] == r.coin and "ok" not in e]
        dur = (f"🟢 açık: {fmt(ac[-1]['p'])} → {(ac[-1]['t'] + pd.Timedelta(hours=ac[-1]['H'])).tz_convert(DISPLAY_TZ):%d.%m %H:%M}" if ac else ("—" if np.isfinite(z) else "⚠️ prim alınamadı"))
        md += f"| {r.coin} | {z:+.2f} | ≥ {r.esik:.0f} | {int(r.saat)} s | {dur} | %{r.isabet:.0f} · +%{r.net:.2f} ({int(r.n)}) |\n"
    md += "\n_prim_coin.py: 50 coin'de 441 denemenin 37'si geçti (tesadüfen ~7) · prim2.py: coin başına tek kural, gecikmesiz girişle ve 2026'da da tuttu. İsabet ~%54; kâr ortalamadan._\n"
    if GP["tglog"]: md += "\n### 📨 Prim mesajları (son 10)\n" + "\n".join(f"- {x['t'].tz_convert(DISPLAY_TZ):%d.%m %H:%M} · {'✅' if x['ok'] else '❌'} · {x['tip']} · {x['info']}" for x in reversed(GP["tglog"])) + "\n"
    if os.path.exists("son_durum.md") and not kuru: open("son_durum.md", "a").write(md)
    print(md)
    GP["log"] = [e for e in GP["log"] if now - e["t"] <= pd.Timedelta(days=120)]
    if not kuru:
        with open(STATE_F, "wb") as f: pickle.dump(GP, f)
if __name__ == "__main__": calis()
