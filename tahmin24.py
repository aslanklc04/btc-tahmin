# tahmin24.py — HER SAAT (tahmin_coin.py'den sonra): 🧪 24 SAAT DENEME sinyalleri (durum/model24_*.pkl.gz · egit24.py). Diğer sistemlere dokunmaz.
# Sinyal: 24 saatlik model 'Çok güçlü ↑' (son 30 günün en güçlü %10'u, yukarı). Araştırmayla aynı sayım: ilk saat sayılır, 24 saat tekrar sayılmaz.
# GERÇEK PARA İÇİN DEĞİL: 2024–25'te iyiydi, 2026'da zayıf. Her sinyal kaydedilir (giriş = mesaj anındaki fiyat, çıkış = 24 saat sonraki saat kapanışı,
# limit komisyon %0,02 × 2); pazar 20:00'de haftalık deneme raporu. 4–6 hafta tutarsa gerçek kullanım konuşulur.
import os, glob, gzip, pickle, traceback, requests
from concurrent.futures import ThreadPoolExecutor
from ortak import *
import ortak as _ortak
BILDIRIM = True; STATE_F = "durum/gecmis24.pkl"; H = 24; FEE = 0.0002
GS = {}
if os.path.exists(STATE_F):
    try:
        with open(STATE_F, "rb") as f: GS = pickle.load(f)
    except Exception: GS = {}
for k, v in (("last", {}), ("log", []), ("tglog", [])): GS.setdefault(k, v)
GS.setdefault("start", pd.Timestamp.now(tz="UTC"))
def fmt(p):
    if not np.isfinite(p) or p <= 0: return "$?"
    if p >= 1000: return f"${p:,.0f}"
    if p >= 1: return f"${p:,.3f}"
    return f"${p:.{min(12, 3 - int(np.floor(np.log10(p))))}f}"
_tg_raw = tg_send
def tg_send(text):
    ok = _tg_raw(text) if BILDIRIM else False; GS["tglog"].append(dict(t=pd.Timestamp.now(tz="UTC"), tip=text.split("\n")[0][:70], ok=ok, info=_ortak.TG_LAST["info"]))
    GS["tglog"] = GS["tglog"][-10:]; return ok
def anlik(sym, yedek):                                                                       # mesaj anındaki fiyat (limit emir için)
    for url in EP:
        try:
            r = requests.get(url.replace("klines", "ticker/price"), params=dict(symbol=sym), timeout=10)
            if r.status_code == 200: return float(r.json()["price"])
        except Exception: pass
    return yedek
CBD = cb_prim(); CBZ, CBL = cb_z(CBD), cb_satir(CBD)                                         # 💵 ABD alıyor mu? (birlesim.py: 24 s sinyalde 2026 kaybını kâra çeviren filtre)
MODELS = {}
for mf in sorted(glob.glob("durum/model24_*.pkl.gz")):
    try:
        with gzip.open(mf, "rb") as f: M = pickle.load(f)
        MODELS[M["sym"]] = M
    except Exception: traceback.print_exc()
now = pd.Timestamp.now(tz="UTC"); now_ms = now.timestamp() * 1000
def _fetch(sym):
    try: return sym, fetch_1h(now_ms - 4000 * 3_600_000, now_ms, sym=sym)
    except Exception: traceback.print_exc(); return sym, None
with ThreadPoolExecutor(max(1, min(12, len(MODELS)))) as ex: DATA = dict(ex.map(_fetch, list(MODELS)))
rows_md, fire, T_FIRE = [], [], None
for sym, M in MODELS.items():
    NM = sym.replace("USDT", ""); st24 = M["STATS"]["2024+"]; s26 = M["STATS"]["yil"].get(now.year, {})
    try:
        o = DATA.get(sym)
        if o is None or len(o) < 2500: rows_md.append(f"| {NM} | ⚠️ veri alınamadı | | | |"); continue
        t = o.index[-1]; price = float(o.close.iloc[-1])
        if now - t > pd.Timedelta(hours=3): rows_md.append(f"| {NM} | ⚠️ veri eski ({t:%d.%m %H:%M}) | | | |"); continue
        FA = features(o); new = FA.index[FA.index > M["PG"].index[-1]]
        if len(new): pg, pl = M["model"](FA.loc[new]); PG = pd.concat([M["PG"], pd.Series(pg, index=new)]); PL = pd.concat([M["PL"], pd.Series(pl, index=new)])
        else: PG, PL = M["PG"], M["PL"]
        SF = signal_frame(PG, PL, FA.r24, False)
        if SF.index[-1] != t: rows_md.append(f"| {NM} | ⚠️ tahmin saati uyuşmadı | | | |"); continue
        sf = SF.iloc[-1]; sg = 1 if sf.S > 0 else -1; li = 2 if sf.C >= sf.T10 else (1 if sf.C >= sf.T30 else 0)
        W_ = SF.iloc[-720:]; mk = np.nan_to_num(((W_.S > 0) & (W_.C >= W_.T10)).values).astype(bool) & W_.T10.notna().values
        for e in GS["log"]:                                                                 # sonuçlanan deneme işlemleri (24 saat sonraki saat kapanışı)
            if e["sym"] == sym and "ok" not in e:
                te = e["t"] + pd.Timedelta(hours=H)
                if te in o.index: p2 = float(o.close.loc[te])
                elif t - te > pd.Timedelta(hours=6): p2 = float(o.close[o.index <= te].iloc[-1]) if (o.index <= te).any() else price
                else: continue
                e["ret"] = 100 * (p2 / e["p"] - 1); e["net"] = e["ret"] - 200 * FEE; e["ok"] = bool(p2 > e["p"])
        ev = events(mk, H); yeni = len(ev) > 0 and ev[-1] == len(W_) - 1 and GS["last"].get(sym) != t   # araştırmadaki sayımın aynısı (son 30 gün zinciri)
        if yeni:
            p_now = anlik(sym, price); CBO = CBD if NM == "BTC" else cb_prim(NM); ZC = cb_coin_z(NM, CBO, CBD)        # 💵 coin'in kendi Coinbase primi
            GS["last"][sym] = t; GS["log"].append(dict(t=t, sym=sym, p=p_now, cb=ZC)); T_FIRE = t
            fire.append(f"• {NM} {fmt(p_now)} — limit alış {fmt(p_now)} · çıkış {(t + pd.Timedelta(hours=H, minutes=6)).tz_convert(DISPLAY_TZ):%d.%m %H:%M}"
                        f" · geçmiş 2024+ isabet %{st24['acc']:.0f}" + (f", {now.year} %{s26['acc']:.0f}" if s26 else "")
                        + (f"\n   💵 {NM} kendi Coinbase primi z {ZC:+.1f}" if CBO else (f"\n   💵 {NM} için prim yok · BTC geneli z {ZC:+.1f}" if np.isfinite(ZC) else f"\n   💵 prim alınamadı"))
                        + ("" if not np.isfinite(ZC) else (" (yalnız bilgi)" if NM in CB_BILGI else (" ⛔ ALMA — ABD satıyor" if ZC <= -1 else (" ✅ onaylı" if ZC > 0 else " ⚠️ onaysız")))))
        acik = [e for e in GS["log"] if e["sym"] == sym and "ok" not in e]
        rows_md.append(f"| {NM} | {fmt(price)} | {'⬆️' if sg == 1 else '⬇️'} {LEV[li].split(' (')[0]}{' · 🧪 SİNYAL' if yeni else ''} | "
                       + (f"giriş {fmt(acik[-1]['p'])} → çıkış {(acik[-1]['t'] + pd.Timedelta(hours=H)).tz_convert(DISPLAY_TZ):%d.%m %H:%M}" if acik else "—")
                       + f" | %{st24['acc']:.0f} · {st24['net']:+.2f} | " + (f"%{s26['acc']:.0f} · {s26['net']:+.2f} ({s26['n']})" if s26 else "—") + " |")
    except Exception: traceback.print_exc(); rows_md.append(f"| {NM} | ⚠️ hata | | | |")
if fire:
    tl0 = T_FIRE.tz_convert(DISPLAY_TZ)
    tg_send(f"🧪 DENEME · 24 SAAT ÇOK GÜÇLÜ ↑ — {tl0:%d.%m %H:%M}\nGerçek para için değil, canlı takip (4–6 hafta). Geçmiş 2024+: isabet %55, işlem başı net +%0,46 — ama 2026'da zayıf.\n"
            + "\n".join(fire) + "\n💵 BTC geneli: " + cb_kisa(CBD) + " · 24 saatte onaylı (z > 0) sinyaller 2024+ %58 / 2026 %54 tuttu, ⛔ olanlar %48\n💡 Limit alış 60 dk geçerli; çıkış saatinde o anki fiyattan limit sat, 60 dk'da dolmazsa piyasa emriyle. Aynı anda gelen sinyaller birbirine bağlıdır.")
# ---- haftalık deneme raporu (pazar 20:00) ----
kap = [e for e in GS["log"] if "ok" in e]
def ozet_onay(x):
    a = [e for e in x if np.isfinite(e.get("cb", np.nan)) and e["cb"] > 0]; b = [e for e in x if np.isfinite(e.get("cb", np.nan)) and e["cb"] <= 0]
    return f"💵 ABD onaylı: {ozet(a)} | onaysız: {ozet(b)}" if (a or b) else ""
def ozet(x): return f"{sum(e['ok'] for e in x)}/{len(x)} tuttu (%{100*sum(e['ok'] for e in x)/len(x):.0f}) · ort. net %{np.mean([e['net'] for e in x]):+.2f} · toplam %{np.sum([e['net'] for e in x]):+.1f}" if x else "sonuçlanan işlem yok"
try:
    tl_ = now.tz_convert(DISPLAY_TZ).floor("h")
    if MODELS and tl_.weekday() == 6 and tl_.hour == 20 and (GS.get("last_weekly") is None or tl_ - GS["last_weekly"] >= pd.Timedelta(days=6)):
        wk = [e for e in kap if now - e["t"] <= pd.Timedelta(days=8)]
        tg_send(f"🧪📊 24 SAAT DENEME — HAFTALIK\nSon 7 gün: {ozet(wk)}\nBaşlangıçtan ({GS['start'].tz_convert(DISPLAY_TZ):%d.%m}) beri: {ozet(kap)}\n{ozet_onay(kap)}\n(Giriş: mesaj anındaki fiyat · çıkış: 24 saat sonra · limit komisyon dahil)")
        GS["last_weekly"] = tl_
except Exception: traceback.print_exc()
# ---- panel ----
if MODELS:
    md = (f"\n## 🧪 24 saat DENEME ({len(MODELS)} coin) — gerçek para için değil\nBaşlangıçtan ({GS['start'].tz_convert(DISPLAY_TZ):%d.%m.%Y}) beri sonuçlanan deneme işlemleri: **{ozet(kap)}**\n\n" + (ozet_onay(kap) + "\n\n" if ozet_onay(kap) else "") + f"Şu an: {CBL}\n\n"
          "| Coin | Fiyat | 24 saat | Açık deneme işlemi | 2024+ isabet · net % | " + f"{now.year} isabet · net % (sinyal)" + " |\n|---|---|---|---|---|---|\n" + "\n".join(rows_md)
          + "\n\n_Araştırma (ufuk24): 10 coin, 2024+ isabet %55, işlem başı net +%0,46 (limit emir); 2024 %58, 2025 %55, 2026 %52 (net −%0,14). Canlıda 4–6 hafta izlenir._\n"
          + "\n### 📨 Deneme mesajları (son 10)\n" + ("\n".join(f"- {x['t'].tz_convert(DISPLAY_TZ):%d.%m %H:%M} · {'✅' if x['ok'] else '❌'} · {x['tip']} · {x['info']}" for x in reversed(GS['tglog'])) if GS["tglog"] else "- (henüz gönderim yok)") + "\n")
    if os.path.exists("son_durum.md"): open("son_durum.md", "a").write(md)
    print(md)
GS["log"] = [e for e in GS["log"] if now - e["t"] <= pd.Timedelta(days=120)]
with open(STATE_F, "wb") as f: pickle.dump(GS, f)
