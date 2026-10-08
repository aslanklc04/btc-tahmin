# kucuk_canli.py — HER SAAT (zincir_canli.py'den sonra): 🧑 KÜÇÜK YATIRIMCI KAÇIYOR → BTC / ETH AL (araştırma: tipler2.py, tipler3.py, kucuk_coin.py · dal arastirma3).
# kucuk_coin.py: aynı sinyal 307 coin'in %88'inde kazandırdı; testi geçen en güvenilir ikinci seçenek ETH. Diğer büyük coin'ler mesajda yalnız bilgi (çok sert ara düşüşler).
# Ölçü: 1 BTC'den küçük cüzdanlardaki toplam BTC (bitcoin-data.com ücretsiz API, günlük) → 30 günlük log değişimi → son 90 güne göre z.
# Kural: z ≤ −1,5 (küçük yatırımcı olağandışı BTC elden çıkarıyor) → BTC AL, 7 gün tut. Sayım araştırmayla aynı: koşulun ilk günü olay, 7 gün tekrar yok.
# TR 15:00–23:59 arasında, DÜNÜN verisi gelince günde BİR kez bakar (API sınırı: saatte 8 / günde 15 istek; bu betik en fazla 9 istek/gün).
# Her sinyal kaydedilir (giriş = mesaj anındaki fiyat, çıkış = 7 gün sonraki saat kapanışı, limit komisyon %0,02 × 2); pazar 20:00'de haftalık özet.
import os, pickle, traceback, requests, numpy as np, pandas as pd
from ortak import *
import ortak as _ortak
STATE_F, FEE, GUN, ESIK = "durum/kucuk.pkl", 0.0002, 7, -1.5
KOIN = (("BTC", "BTCUSDT", "2x", "2022-10→2024-09 17 işlem, isabet %76, işlem başı +%4,65 · 2024-10→ bugün 22 işlem, %68, +%2,98 (alt sınır +%0,65) · 2026: 8 işlem, %75, +%3,09 · en kötü ara düşüş %17"),
        ("ETH", "ETHUSDT", "1,5x", "2022-10→2024-09 17 işlem, isabet %76, +%3,24 · 2024-10→ bugün 22 işlem, %68, +%3,86 (alt sınır +%0,64) · 2026: 8 işlem, %62, +%3,18 · en kötü ara düşüş %24"))
NET_2024 = {"BTC": 2.98, "ETH": 3.86}                                                        # KOIN'daki 2024-10→ işlem başı net % (mesajdaki geçmiş ortalama sonuç; brüt = net + %0,04)
BILGI = ("ℹ️ Aynı sinyalde diğer büyük coin'ler de yükselmiş ama çok daha sert dalgalanarak (2024-10→, 7 gün, işlem başı net · en kötü ara düşüş): XRP +%11,0 · %56 · ADA +%7,0 · %67 · "
         "LINK +%6,5 · %65 · BNB +%2,6 · %34. Alacaksan KALDIRAÇSIZ ve küçük miktar: 10.10.2025 çöküşünde altcoin'ler birkaç saatte %50–95 düştü.")
def zs(s, n=90): return (s - s.rolling(n, min_periods=30).mean()) / (s.rolling(n, min_periods=30).std() + 1e-12)
def veri():
    r = requests.get("https://bitcoin-data.com/v1/coins-addr-1-BTC", timeout=60, headers={"User-Agent": "btc-tahmin"})
    if r.status_code != 200: raise RuntimeError(f"bitcoin-data.com HTTP {r.status_code}: {r.text[:120]}")
    d = pd.DataFrame(r.json()); d.index = pd.to_datetime(d.pop("d"), utc=True).dt.floor("D")
    d = d.drop(columns=[c for c in d.columns if "ts" in c.lower() or "unix" in c.lower()]).apply(pd.to_numeric, errors="coerce")
    s = d.iloc[:, 0].dropna(); return s[~s.index.duplicated()].sort_index()
def olcu(s):
    s = s.asfreq("D"); return zs(np.log(s).diff(30))
def fmt(p): return f"${p:,.0f}"
def anlik(sym, yedek=np.nan):
    for url in EP:
        try:
            r = requests.get(url.replace("klines", "ticker/price"), params=dict(symbol=sym), timeout=10)
            if r.status_code == 200: return float(r.json()["price"])
        except Exception: pass
    return yedek
def ozet(x): return f"{sum(e['ok'] for e in x)}/{len(x)} tuttu (%{100*sum(e['ok'] for e in x)/len(x):.0f}) · ort. net %{np.mean([e['net'] for e in x]):+.2f} · toplam %{np.sum([e['net'] for e in x]):+.1f}" if x else "sonuçlanan işlem yok"
def calis():
    kuru = os.environ.get("KUCUK_KURU") == "1"                                               # test: Telegram yok, saat beklenmez, durum kaydedilmez
    GK = {}
    if os.path.exists(STATE_F):
        try:
            with open(STATE_F, "rb") as f: GK = pickle.load(f)
        except Exception: GK = {}
    for k, v in (("log", []), ("tglog", []), ("son", None), ("gun", None)): GK.setdefault(k, v)
    GK.setdefault("start", pd.Timestamp.now(tz="UTC"))
    def tg(text, **kw):
        if kuru: print("---- (kuru) Telegram ----\n" + (f"[öncelik {kw.get('oncelik')} · {kw.get('etiket')}]\n" if kw else "") + text + "\n-------------------------"); return False
        ok = tg_send(text, **kw); GK["tglog"] = (GK["tglog"] + [dict(t=pd.Timestamp.now(tz="UTC"), tip=text.split("\n")[0][:70], ok=ok, info=_ortak.TG_LAST["info"])])[-10:]; return ok
    now = pd.Timestamp.now(tz="UTC"); tl = now.tz_convert(DISPLAY_TZ); dun = now.floor("D") - pd.Timedelta(days=1)
    # ---- günlük değerlendirme ----
    if kuru or (tl.hour >= 15 and GK["gun"] != dun):
        try:
            s = veri(); z = olcu(s); son_gun = z.dropna().index[-1]
            print(f"bitcoin-data.com son gün {s.index[-1]:%d.%m} · küçük cüzdan BTC {s.iloc[-1]:,.0f} · z {z.dropna().iloc[-1]:+.2f}")
            if son_gun >= dun or kuru:
                ev = z.index[events((z <= ESIK).fillna(False).values, GUN)]; zn = float(z.loc[son_gun])
                d30 = 100 * (s.loc[son_gun] / s[s.index <= son_gun - pd.Timedelta(days=30)].iloc[-1] - 1)
                yeni = len(ev) > 0 and ev[-1] == son_gun and not any(e["veri"] == son_gun for e in GK["log"])
                GK["son"] = dict(gun=son_gun, z=zn, d30=d30, btc=float(s.loc[son_gun]), kosul=bool(zn <= ESIK), yeni=yeni, hesap=now)
                if yeni:
                    t0 = now.floor("h"); cikis = (t0 + pd.Timedelta(days=GUN, minutes=6)).tz_convert(DISPLAY_TZ); sat = []; ZK = {}
                    for nm, sym, kal, gec in KOIN:
                        p_now = anlik(sym); CBK = cb_prim(nm); ZK[nm] = cb_z(CBK); gr_ = NET_2024.get(nm, np.nan) + 200 * FEE; hz_ = hiz_notu(ZK[nm])
                        if np.isfinite(p_now): GK["log"].append(dict(t=t0, sym=nm, p=p_now, veri=son_gun, z=zn))
                        bek_ = f" · {CIKIS_NOT} · geçmiş ort. sonuç +%{gr_:.2f}" if np.isfinite(gr_) else f" · {CIKIS_NOT}"
                        sat.append(f"• {nm}: limit ALIŞ {fmt(p_now) if np.isfinite(p_now) else '?'} · kaldıraç en fazla {kal}{bek_}\n   💵 {nm} Coinbase primi: {cb_kisa(CBK)} (bilgi)" + (f" · {hz_}" if hz_ else "") + f"\n   Geçmiş: {gec}")
                    tg(f"🧑🟢 BTC / ETH AL — KÜÇÜK YATIRIMCI KAÇIYOR — {tl:%d.%m %H:%M}\n"
                       f"1 BTC'den küçük cüzdanlardaki BTC 30 günde %{d30:+.2f} değişti (olağandışı düşüş, z {zn:+.1f}) · veri günü {son_gun:%d.%m}\n"
                       + "\n".join(sat) + f"\nÇıkış (ikisi için): {cikis:%d.%m %H:%M} ({GUN} gün tut)\n{BILGI}\n"
                       "⚠️ BTC ve ETH aynı bahis (birlikte hareket eder): ikisini birden alırsan toplam risk büyür. Ayda ~1 sinyal, bazen art arda haftalar. Veri yalnız 4 yıllık; canlıda izleniyor. Yatırım tavsiyesi değildir.",
                       oncelik=sira_puani("🧑", ZK.get("BTC", float("nan"))), etiket=f"🧑 BTC / ETH AL — küçük yatırımcı kaçıyor (7 gün)")
                if not kuru: GK["gun"] = dun
            else: print(f"Dünün ({dun:%d.%m}) verisi henüz yok → sonraki saat yeniden bakılacak")
        except Exception: traceback.print_exc()
    # ---- sonuçlanan işlemler ----
    acik = [e for e in GK["log"] if "ok" not in e]
    if any(now >= e["t"] + pd.Timedelta(days=GUN) for e in acik):
        try:
            OO = {}
            for e in acik:
                te = e["t"] + pd.Timedelta(days=GUN)
                if now < te: continue
                nm = e.get("sym", "BTC")
                if nm not in OO: OO[nm] = fetch_1h((min(x["t"] for x in acik) - pd.Timedelta(days=2)).timestamp() * 1000, now.timestamp() * 1000, sym=f"{nm}USDT").close
                o = OO[nm]
                if not (o.index <= te).any(): continue
                p2 = float(o.loc[te]) if te in o.index else float(o[o.index <= te].iloc[-1])
                e["ret"] = 100 * (p2 / e["p"] - 1); e["net"] = e["ret"] - 200 * FEE; e["ok"] = bool(e["ret"] > 0); e["p2"] = p2
                tg(f"🧑 {nm} küçük yatırımcı işlemi kapandı — {'✅ tuttu' if e['ok'] else '❌ tutmadı'}\n{fmt(e['p'])} → {fmt(p2)} · AL · net %{e['net']:+.2f} (komisyon dahil)")
        except Exception: traceback.print_exc()
    kap = [e for e in GK["log"] if "ok" in e]
    # ---- haftalık özet (pazar 20:00; en az bir sinyal geldiyse) ----
    try:
        tlh = tl.floor("h")
        if GK["log"] and tlh.weekday() == 6 and tlh.hour >= 20 and (GK.get("last_weekly") is None or tlh - GK["last_weekly"] >= pd.Timedelta(days=6)):
            wk = [e for e in kap if now - e["t"] - pd.Timedelta(days=GUN) <= pd.Timedelta(days=8)]
            tg(f"🧑📊 KÜÇÜK YATIRIMCI (BTC / ETH) — HAFTALIK\nBu hafta kapanan: {ozet(wk)}\nBaşlangıçtan ({GK['start'].tz_convert(DISPLAY_TZ):%d.%m}) beri: "
               + " · ".join(f"{nm}: {ozet([e for e in kap if e.get('sym', 'BTC') == nm])}" for nm, *_ in KOIN) + f"\nAçık işlem: {len([e for e in GK['log'] if 'ok' not in e])}")
            GK["last_weekly"] = tlh
    except Exception: traceback.print_exc()
    # ---- panel ----
    s_ = GK["son"]
    md = "\n## 🧑 Küçük yatırımcı kaçıyor → BTC / ETH AL (günlük)\n"
    if s_:
        md += (f"Son değerlendirme: **{s_['hesap'].tz_convert(DISPLAY_TZ):%d.%m %H:%M}** (veri günü {s_['gun']:%d.%m}) · 1 BTC'den küçük cüzdanlarda {s_['btc']:,.0f} BTC, "
               f"30 günde %{s_['d30']:+.2f} · z **{s_['z']:+.2f}** (sinyal: z ≤ {ESIK}) → " + ("🟢 bugün sinyal" if s_["yeni"] else ("koşul sürüyor (sinyal daha önce verildi)" if s_["kosul"] else "sinyal yok")) + "\n")
    else: md += "Henüz değerlendirme yok (her gün TR 15:00'ten sonra, dünün verisi gelince).\n"
    ac = [e for e in GK["log"] if "ok" not in e]
    if ac: md += "\n" + "\n".join(f"- Açık: {e.get('sym', 'BTC')} AL {fmt(e['p'])} → çıkış {(e['t'] + pd.Timedelta(days=GUN)).tz_convert(DISPLAY_TZ):%d.%m %H:%M}" for e in ac) + "\n"
    md += (f"\nBaşlangıçtan ({GK['start'].tz_convert(DISPLAY_TZ):%d.%m.%Y}) beri sonuçlanan: " + " · ".join(f"{nm} **{ozet([e for e in kap if e.get('sym', 'BTC') == nm])}**" for nm, *_ in KOIN) + "\n\n"
           "_tipler2.py: 53 denemelik taramada öne çıktı · tipler3.py: iki dönemde de anlamlı, fiyat etkisinden bağımsız, TR 15:00 girişle tuttu. Ayda ~1 sinyal. kucuk_coin.py: ETH de geçti (en kötü ara düşüş %24); diğer coin'ler yalnız bilgi._\n")
    if GK["tglog"]: md += "\n### 📨 Küçük yatırımcı mesajları (son 10)\n" + "\n".join(f"- {x['t'].tz_convert(DISPLAY_TZ):%d.%m %H:%M} · {'✅' if x['ok'] else '❌'} · {x['tip']} · {x['info']}" for x in reversed(GK["tglog"])) + "\n"
    if os.path.exists("son_durum.md") and not kuru: open("son_durum.md", "a").write(md)
    print(md)
    GK["log"] = [e for e in GK["log"] if now - e["t"] <= pd.Timedelta(days=400)]
    if not kuru:
        os.makedirs("durum", exist_ok=True)
        with open(STATE_F, "wb") as f: pickle.dump(GK, f)
if __name__ == "__main__": calis()
