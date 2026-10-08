# zincir_canli.py — HER SAAT (tahmin24.py'den sonra): ⛓️ GÜNLÜK ARZ / TALEP kontrolü (araştırma: zincir.py, zincir2.py, zincir3.py · dal arastirma3).
# Arz: Coin Metrics (ücretsiz) borsaya giriş/çıkış ve borsalardaki ETH miktarı. Talep: DefiLlama toplam stabil coin arzı. z: son 90 güne göre.
# TR 09:00'dan sonra, DÜNÜN verisi yayımlanmışsa günde BİR kez değerlendirir (veri gelmediyse sonraki saatlerde tekrar bakar).
# Yalnız testi geçen ETH kuralları mesaj gönderir (≤2023'te seçildi, 2024+'da net > 0 ve %90 alt sınır > 0). BTC'de aynı kurallar anlamlı çıkmadı → yalnız bilgi.
# Her sinyal kaydedilir (giriş = mesaj anındaki fiyat, çıkış = tutma süresi sonundaki saat kapanışı, limit komisyon %0,02 × 2); pazar 20:00'de haftalık özet.
import os, pickle, time, traceback, requests, numpy as np, pandas as pd
from ortak import *
import ortak as _ortak
STATE_F, FEE = "durum/zincir.pkl", 0.0002
CM = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
KURAL = [   # (ad, açıklama, yön, tutma günü, koşul, geçmiş — zincir3_sonuc.md: canlı giriş = veri günü + 1, TR 09:00)
    ("AL-2", "Borsalardaki ETH 30 günde azalıyor + stabil coin arzı 30 günde büyüyor", 1, 7, lambda z: (z.ms30 >= 1) & (z.t30 >= 1),
     "2024+: 15 işlem, isabet %67, işlem başı net +%4,62 (alt sınır +%1,45) · ≤2023: 24 işlem +%5,26 · 2026: 4 işlem +%4,45 · en kötü ara düşüş %15"),
    ("AL-1", "ETH borsalardan soğuk cüzdana çıkıyor (7 g) + stabil coin arzı 7 günde büyüyor", 1, 7, lambda z: (z.cik7 >= 1) & (z.t7 >= 1),
     "2024+: 13 işlem, isabet %69, net +%2,76 (alt +%0,28) · ≤2023: 20 işlem +%0,24 (zayıf) · 2026: 4 işlem +%0,76 · en kötü ara düşüş %11"),
    ("AL-3", "Talep çok güçlü: stabil coin arzı 7 günde olağandışı büyüyor (z ≥ 1,5)", 1, 3, lambda z: z.t7 >= 1.5,
     "2024+: 47 işlem, isabet %53, net +%1,84 (alt +%0,37 — kazançlar kayıplardan büyük) · ≤2023: 76 işlem +%1,81 · 2026: 13 işlem +%2,00 · en kötü ara düşüş %12"),
    ("SAT-1", "ETH borsalara akıyor (7 g net giriş z ≤ −1,5) + talep zayıf (stabil coin 7 g büyüme z ≤ 0)", -1, 7, lambda z: (z.cik7 <= -1.5) & (z.t7 <= 0),
     "2024+: 10 işlem, 10/10 tuttu, net +%7,33 (alt +%4,48) · ≤2023: 29 işlem +%0,39 (zayıf) · en kötü ara yükseliş %13"),
]
ADLAR = {"cik7": "borsadan çıkış 7g", "ms30": "borsadaki miktar azalışı 30g", "t7": "stabil coin 7g", "t30": "stabil coin 30g"}
def zs(s, n=90): return (s - s.rolling(n, min_periods=30).mean()) / (s.rolling(n, min_periods=30).std() + 1e-12)
def cm(asset, gun=400):
    rows, url = [], CM
    params = dict(assets=asset, metrics="FlowInExNtv,FlowOutExNtv,SplyExNtv", frequency="1d", page_size=10000,
                  start_time=(pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=gun)).strftime("%Y-%m-%d"))
    for _ in range(10):
        for k in range(5):
            r = requests.get(url, params=params, timeout=60)
            if r.status_code == 429: time.sleep(3 * (k + 1)); continue
            break
        r.raise_for_status(); j = r.json(); rows += j.get("data", []); url = j.get("next_page_url"); params = None
        if not url: break
    d = pd.DataFrame(rows); d.index = pd.to_datetime(d.time, utc=True).dt.floor("D")
    return d.drop(columns=["asset", "time"]).apply(pd.to_numeric, errors="coerce").sort_index()
def stabil():
    j = requests.get("https://stablecoins.llama.fi/stablecoincharts/all", timeout=60).json()
    s = pd.Series({pd.Timestamp(int(x["date"]), unit="s", tz="UTC").floor("D"): float((x.get("totalCirculatingUSD") or x.get("totalCirculating") or {}).get("peggedUSD", np.nan)) for x in j})
    return s.sort_index()
def olcu(d, sc):
    """zincir2.py ile birebir: gün d'nin ölçüleri (z, son 90 güne göre)."""
    sc = sc.reindex(d.index).ffill(limit=3)
    return pd.DataFrame({"cik7": zs(-(d.FlowInExNtv - d.FlowOutExNtv).rolling(7).sum() / d.SplyExNtv), "ms30": zs(-np.log(d.SplyExNtv / d.SplyExNtv.shift(30))),
                         "t7": zs(np.log(sc / sc.shift(7))), "t30": zs(np.log(sc / sc.shift(30)))}, index=d.index)
def kural_olaylari(Z):
    """Her kural için araştırmadaki sayım: koşulun ilk günü olay, tutma süresi boyunca tekrar sayılmaz."""
    return {ad: Z.index[events(kos(Z).fillna(False).values, gun)] for ad, _, _, gun, kos, _ in KURAL}
def fmt(p): return f"${p:,.0f}" if p >= 1000 else f"${p:,.2f}"
def anlik(sym, yedek=np.nan):
    for url in EP:
        try:
            r = requests.get(url.replace("klines", "ticker/price"), params=dict(symbol=sym), timeout=10)
            if r.status_code == 200: return float(r.json()["price"])
        except Exception: pass
    return yedek
def ozet(x): return f"{sum(e['ok'] for e in x)}/{len(x)} tuttu (%{100*sum(e['ok'] for e in x)/len(x):.0f}) · ort. net %{np.mean([e['net'] for e in x]):+.2f} · toplam %{np.sum([e['net'] for e in x]):+.1f}" if x else "sonuçlanan işlem yok"
def zsatir(r): return " · ".join(f"{ADLAR[k]} z {r[k]:+.1f}" for k in ADLAR if np.isfinite(r[k]))
def calis():
    kuru = os.environ.get("ZINCIR_KURU") == "1"                                              # test: Telegram'a göndermez, saati beklemez, durumu kaydetmez
    GZ = {}
    if os.path.exists(STATE_F):
        try:
            with open(STATE_F, "rb") as f: GZ = pickle.load(f)
        except Exception: GZ = {}
    for k, v in (("log", []), ("tglog", []), ("son", None), ("gun", None)): GZ.setdefault(k, v)
    GZ.setdefault("start", pd.Timestamp.now(tz="UTC"))
    def tg(text):
        if kuru: print("---- (kuru) Telegram ----\n" + text + "\n-------------------------"); return False
        ok = tg_send(text); GZ["tglog"] = (GZ["tglog"] + [dict(t=pd.Timestamp.now(tz="UTC"), tip=text.split("\n")[0][:70], ok=ok, info=_ortak.TG_LAST["info"])])[-10:]; return ok
    now = pd.Timestamp.now(tz="UTC"); tl = now.tz_convert(DISPLAY_TZ); dun = now.floor("D") - pd.Timedelta(days=1)
    # ---- günlük değerlendirme (TR 09:00'dan sonra, dünün verisi gelince, günde bir kez) ----
    if kuru or (tl.hour >= 9 and GZ["gun"] != dun):
        try:
            SC = stabil(); D = {a: cm(a) for a in ("eth", "btc")}
            ZZ = {a: olcu(D[a], SC) for a in D}; Z = ZZ["eth"]; son_gun = Z.dropna().index[-1]
            print(f"Coin Metrics son gün: ETH {D['eth'].index[-1]:%d.%m} · BTC {D['btc'].index[-1]:%d.%m} · ölçülerin son tam günü {son_gun:%d.%m} · stabil coin son {SC.index[-1]:%d.%m} ({SC.iloc[-1]/1e9:,.0f} milyar $)")
            if son_gun >= dun or kuru:
                OL = kural_olaylari(Z); r = Z.loc[son_gun]; rb = ZZ["btc"].dropna().iloc[-1]
                yeni = [k for k in KURAL if len(OL[k[0]]) and OL[k[0]][-1] == son_gun and not any(e["kural"] == k[0] and e["veri"] == son_gun for e in GZ["log"])]   # aynı veri günü iki kez gönderilmez
                durum = ", ".join(f"{ad} ({'bugün sinyal' if ad in [k[0] for k in yeni] else 'koşul sürüyor, sinyal daha önce verildi'})" for ad, _, _, _, kos, _ in KURAL if bool(kos(Z.loc[[son_gun]]).iloc[0]))
                btc_k = [ad for ad, _, _, _, kos, _ in KURAL if bool(kos(ZZ["btc"].dropna().iloc[[-1]]).iloc[0])]
                btc_satir = f"₿ BTC (yalnız bilgi — bu kurallar BTC'de testte anlamlı çıkmadı): {zsatir(rb)}" + (f" · koşul: {', '.join(btc_k)}" if btc_k else "")
                GZ["son"] = dict(gun=son_gun, eth=r.to_dict(), btc=rb.to_dict(), durum=durum, btc_k=btc_k, hesap=now)
                if yeni:
                    p_now = anlik("ETHUSDT"); t0 = now.floor("h")
                    yon = {k[2] for k in yeni}
                    bas = "⛓️🟢 ETH ARZ/TALEP — AL SİNYALİ" if yon == {1} else ("⛓️🔻 ETH ARZ/TALEP — SAT (KISA) SİNYALİ" if yon == {-1} else "⛓️⚖️ ETH ARZ/TALEP — ÇELİŞKİLİ (AL ve SAT birlikte → işlem açma)")
                    sat = []
                    for ad, acik, y, gun, kos, gec in yeni:
                        cikis = (t0 + pd.Timedelta(days=gun, minutes=6)).tz_convert(DISPLAY_TZ)
                        sat.append(f"• {ad}: {acik}\n   {'Limit ALIŞ' if y > 0 else 'Limit SATIŞ (kısa)'} {fmt(p_now)} · çıkış {cikis:%d.%m %H:%M} ({gun} gün tut)\n   Geçmiş: {gec}")
                        if np.isfinite(p_now) and len(yon) == 1: GZ["log"].append(dict(t=t0, kural=ad, yon=y, gun=gun, p=p_now, veri=son_gun))
                    tg(f"{bas} — {tl:%d.%m %H:%M}\nVeri: {son_gun:%d.%m} günü (Coin Metrics + DefiLlama · test bu giriş saatiyle yapıldı: zincir3.py)\n"
                       f"ETH ölçüleri: {zsatir(r)}\n\n" + "\n".join(sat) + f"\n\n{btc_satir}\n"
                       "⚠️ Seyrek, 3–7 gün süren işlemler; geçmiş örnek az (10–47). İşlem sürerken geçmişte en kötü ters hareket 2024+ %11–15, eski yıllarda %30'a kadar → kaldıraç en fazla 2x. Yatırım tavsiyesi değildir.")
                if not kuru: GZ["gun"] = dun
            else: print(f"Dünün ({dun:%d.%m}) verisi henüz yok → sonraki saat yeniden bakılacak")
        except Exception: traceback.print_exc()
    # ---- sonuçlanan işlemler (tutma süresi sonundaki saat kapanışı) ----
    acik = [e for e in GZ["log"] if "ok" not in e]
    if any(now >= e["t"] + pd.Timedelta(days=e["gun"]) for e in acik):
        try:
            bas = min(e["t"] for e in acik) - pd.Timedelta(days=2)
            o = fetch_1h(bas.timestamp() * 1000, now.timestamp() * 1000, sym="ETHUSDT").close
            for e in acik:
                te = e["t"] + pd.Timedelta(days=e["gun"])
                if now < te or not (o.index <= te).any(): continue
                p2 = float(o.loc[te]) if te in o.index else float(o[o.index <= te].iloc[-1])
                e["ret"] = 100 * e["yon"] * (p2 / e["p"] - 1); e["net"] = e["ret"] - 200 * FEE; e["ok"] = bool(e["ret"] > 0); e["p2"] = p2
                tg(f"⛓️ ETH {e['kural']} işlemi kapandı — {'✅ tuttu' if e['ok'] else '❌ tutmadı'}\n{fmt(e['p'])} → {fmt(p2)} · {'AL' if e['yon'] > 0 else 'SAT'} · net %{e['net']:+.2f} (komisyon dahil)")
        except Exception: traceback.print_exc()
    kap = [e for e in GZ["log"] if "ok" in e]
    # ---- haftalık özet (pazar 20:00; yalnız en az bir sinyal geldiyse) ----
    try:
        tlh = tl.floor("h")
        if GZ["log"] and tlh.weekday() == 6 and tlh.hour >= 20 and (GZ.get("last_weekly") is None or tlh - GZ["last_weekly"] >= pd.Timedelta(days=6)):
            wk = [e for e in kap if now - e["t"] - pd.Timedelta(days=e["gun"]) <= pd.Timedelta(days=8)]
            tg(f"⛓️📊 ARZ/TALEP (ETH) — HAFTALIK\nBu hafta kapanan: {ozet(wk)}\nBaşlangıçtan ({GZ['start'].tz_convert(DISPLAY_TZ):%d.%m}) beri: {ozet(kap)}\nAçık işlem: {len([e for e in GZ['log'] if 'ok' not in e])}")
            GZ["last_weekly"] = tlh
    except Exception: traceback.print_exc()
    # ---- panel ----
    s = GZ["son"]
    md = "\n## ⛓️ Arz/Talep (günlük, ETH) — borsadan çıkan coin + stabil coin talebi\n"
    if s:
        md += (f"Son değerlendirme: **{s['hesap'].tz_convert(DISPLAY_TZ):%d.%m %H:%M}** (veri günü {s['gun']:%d.%m})\n\n"
               f"- ETH: {zsatir(pd.Series(s['eth']))} → {('koşulu sağlanan kural: ' + s['durum']) if s['durum'] else 'hiçbir kuralın koşulu yok'}\n"
               f"- BTC (yalnız bilgi): {zsatir(pd.Series(s['btc']))}" + (f" · koşul: {', '.join(s['btc_k'])}" if s["btc_k"] else "") + "\n")
    else: md += "Henüz değerlendirme yok (her gün TR 09:00'dan sonra, dünün verisi gelince).\n"
    ac = [e for e in GZ["log"] if "ok" not in e]
    if ac: md += "\n" + "\n".join(f"- Açık: {e['kural']} {'AL' if e['yon'] > 0 else 'SAT'} {fmt(e['p'])} → çıkış {(e['t'] + pd.Timedelta(days=e['gun'])).tz_convert(DISPLAY_TZ):%d.%m %H:%M}" for e in ac) + "\n"
    md += (f"\nBaşlangıçtan ({GZ['start'].tz_convert(DISPLAY_TZ):%d.%m.%Y}) beri sonuçlanan: **{ozet(kap)}**\n\n"
           "_Kurallar: AL-2 (7 g), AL-1 (7 g), AL-3 (3 g), SAT-1 (7 g) — zincir2.py'de ≤2023'te seçildi, 2024+'da doğrulandı; zincir3.py: TR 09:00 girişle de tuttu. Yılda ~25–30 sinyal beklenir._\n")
    if GZ["tglog"]: md += "\n### 📨 Arz/Talep mesajları (son 10)\n" + "\n".join(f"- {x['t'].tz_convert(DISPLAY_TZ):%d.%m %H:%M} · {'✅' if x['ok'] else '❌'} · {x['tip']} · {x['info']}" for x in reversed(GZ["tglog"])) + "\n"
    if os.path.exists("son_durum.md") and not kuru: open("son_durum.md", "a").write(md)
    print(md)
    GZ["log"] = [e for e in GZ["log"] if now - e["t"] <= pd.Timedelta(days=400)]
    if not kuru:
        os.makedirs("durum", exist_ok=True)
        with open(STATE_F, "wb") as f: pickle.dump(GZ, f)
if __name__ == "__main__": calis()
