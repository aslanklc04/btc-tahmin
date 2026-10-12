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
def tg_send(text, **kw):
    ok = _tg_raw(text, **kw) if BILDIRIM else False; GS["tglog"].append(dict(t=pd.Timestamp.now(tz="UTC"), tip=text.split("\n")[0][:70], ok=ok, info=_ortak.TG_LAST["info"]))
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
_Y24 = sorted(glob.glob("durum/model24_*.pkl.gz")); _V24 = {os.path.basename(x) for x in _Y24}
# 🌐 GENİŞ LİSTE (modeller dalı, ~125 coin): yalnız coin'in KENDİ primi z ≥ 1,5 iken ✅ ana (genis_esik.py: isabet ve kârda ana seti 3 dönemde de geçti —
#    %58,7 / %59,6 / %59,8 · +%0,72 / +%1,23 / +%1,20); altındakiler GÖNDERİLMEZ (yalnız panel) — kullanıcı şartı: isabeti/kârı düşüren coin eklenmez
GENIS24 = [x for x in sorted(glob.glob("modeller/model24_*.pkl.gz")) if os.path.basename(x) not in _V24]; GENIS24_SET = {os.path.basename(x)[8:-7] for x in GENIS24}; GENIS_ESIK = 1.5
for mf in _Y24 + GENIS24:
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
        t = o.index[-1]; price = float(o.close.iloc[-1]); RZ = r24z(o.close)                   # 🚀 / 📉🔥 (teknik_tara C3)
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
        if os.environ.get("TEST_ZORLA") and not fire: yeni = True                               # yalnız test: ilk iki coin'i zorla
        if os.environ.get("TEST_ZORLA") and len(fire) == 1: yeni = True
        if yeni:
            p_now = anlik(sym, price); CBO = CBD if NM == "BTC" else cb_prim(NM); ZC = cb_coin_z(NM, CBO, CBD)        # 💵 coin'in kendi Coinbase primi
            GS["last"][sym] = t
            if sym in GENIS24_SET and not (CBO and np.isfinite(ZC) and ZC >= GENIS_ESIK): yeni = False   # 🌐 eşik altı: gönderilmez, kayda da girmez (yalnız panelde 🧪 işareti yok)
        if yeni:
            GS["log"].append(dict(t=t, sym=sym, p=p_now, cb=ZC)); T_FIRE = t
            gr24_ = st24.get("gross", st24.get("net", np.nan) + 200 * FEE); hz_ = hiz_notu(ZC if CBO else float("nan"))
            fire.append((ZC if CBO else float("nan"), NM, f"• {NM}{' 🌐' if sym in GENIS24_SET else ''} {fmt(p_now)} — limit alış {fmt(p_now)} · çıkış {(t + pd.Timedelta(hours=H, minutes=6)).tz_convert(DISPLAY_TZ):%d.%m %H:%M}"
                        + f" ({CIKIS_NOT})" + (f" · geçmiş ort. sonuç {'+' if gr24_ >= 0 else '−'}%{abs(gr24_):.2f}" if np.isfinite(gr24_) else "")
                        + f" · geçmiş 2024+ isabet %{st24['acc']:.0f}" + (f", {now.year} %{s26['acc']:.0f}" if s26 else "")
                        + (f"\n   💵 {NM} kendi Coinbase primi z {ZC:+.1f}" if CBO else (f"\n   💵 {NM} için prim yok · BTC geneli z {ZC:+.1f}" if np.isfinite(ZC) else f"\n   💵 prim alınamadı"))
                        + ("" if not np.isfinite(ZC) else (" (yalnız bilgi)" if NM in CB_BILGI else (" ⛔ ALMA — ABD satıyor" if ZC <= -1 else (" ✅ onaylı" if ZC > 0 else " ⚠️ onaysız"))))
                        + (f"\n   {hz_}" if hz_ else ""), RZ))
        acik = [e for e in GS["log"] if e["sym"] == sym and "ok" not in e]
        rows_md.append(f"| {NM} | {fmt(price)} | {'⬆️' if sg == 1 else '⬇️'} {LEV[li].split(' (')[0]}{' · 🧪 SİNYAL' if yeni else ''} | "
                       + (f"giriş {fmt(acik[-1]['p'])} → çıkış {(acik[-1]['t'] + pd.Timedelta(hours=H)).tz_convert(DISPLAY_TZ):%d.%m %H:%M}" if acik else "—")
                       + f" | %{st24['acc']:.0f} · {st24['net']:+.2f} | " + (f"%{s26['acc']:.0f} · {s26['net']:+.2f} ({s26['n']})" if s26 else "—") + " |")
    except Exception: traceback.print_exc(); rows_md.append(f"| {NM} | ⚠️ hata | | | |"); hata_kaydet("24 saat", f"{NM} ({traceback.format_exc().strip().splitlines()[-1][:120]})")
if fire:
    tl0 = T_FIRE.tz_convert(DISPLAY_TZ)
    fire.sort(key=lambda x: -(x[0] if np.isfinite(x[0]) else -9))                             # coin'in kendi primi yüksek olan üstte
    _g = lambda x: x[1] + "USDT" in GENIS24_SET
    _ana = [x for x in fire if (np.isfinite(x[0]) and x[0] >= GENIS_ESIK) if _g(x)] + [x for x in fire if not _g(x) and ana_mi(x[0])]   # ✅ (en fazla 10 satır/mesaj)
    _ana.sort(key=lambda x: -(x[0] if np.isfinite(x[0]) else -9))
    _mom = lambda x: (not _g(x)) and (not ana_mi(x[0])) and mom_mu(x[3])                       # 🚀 primsiz ama momentumlu → ✅ ana (teknik_tara C3a)
    _ana += [x for x in fire if _mom(x)]
    _yed = [x for x in fire if not _g(x) and not ana_mi(x[0]) and not _mom(x)]                # primsizler → panel · geniş listenin eşik altı sinyalleri gönderilmez
    _isr = lambda x, s_: (lambda t_: t_.replace("⛔ ALMA", "⛔ ama 🚀 momentum") if _mom(x) else t_)(x[2].replace("• ", "• " + ("🚀 " if _mom(x) else "") + ("📉🔥 " if s_ == "ana" and dip_mi(x[3]) and not _g(x) else "") + ("💸 " if s_ == "ana" and fon_mu(x[1]) else ""), 1))
    for sinif_, grup in [("ana", _ana[i:i + 10]) for i in range(0, len(_ana), 10)] + [("panel", [x]) for x in _yed]:   # 12.10.2026: primi < 0 / yok → gönderilmez (panel)
        if not grup: continue
        zmax_ = max((x[0] for x in grup if np.isfinite(x[0])), default=float("nan")); hepsi_alma = all(np.isfinite(x[0]) and x[0] <= -1 for x in grup)
        _gn = ("🌐 = geniş liste coin'i: yalnız ABD güçlü alıyorken (kendi primi z ≥ 1,5) gelir · testte isabet ~%60, işlem başı +%1,2\n" if any(_g(x) for x in grup) else "")
        bas_ = (f"🧪 24 SAAT ÇOK GÜÇLÜ ↑ — {tl0:%d.%m %H:%M}\n{ANA_NOT} Sıra: kendi primi yüksek olan üstte.\n" + _gn if sinif_ == "ana" else
                f"🧪 DENEME · 24 SAAT ÇOK GÜÇLÜ ↑ — {tl0:%d.%m %H:%M}\nGeçmiş 2024+: isabet %55, işlem başı net +%0,46 — ama 2026'da zayıf; coin'in kendi primi < 0 olanlar daha zayıf. Sıra: kendi primi yüksek olan üstte.\n")
        tg_send(bas_ + "\n".join(_isr(x, sinif_) for x in grup) + "".join("\n" + v for k_, v in MOM_DIP_ACK.items() if any(k_ in _isr(x, sinif_).split("—")[0] for x in grup)) + "\n💵 BTC geneli: " + cb_kisa(CBD) + " · 24 saatte onaylı (z > 0) sinyaller 2024+ %58 / 2026 %54 tuttu, ⛔ olanlar %48\n💡 Limit alış 60 dk geçerli; çıkış saatinde o anki fiyattan limit sat, 60 dk'da dolmazsa piyasa emriyle. Aynı anda gelen sinyaller birbirine bağlıdır.",
                oncelik=sira_puani("🧪", zmax_, hepsi_alma) + (ONCELIK_DIP if sinif_ == "ana" and any(dip_mi(x[3]) and not _g(x) for x in grup) else 0) + (ONCELIK_FON if sinif_ == "ana" and any(fon_mu(x[1]) for x in grup) else 0), etiket="🧪 24 saat: " + ", ".join(f"{x[1]} ({'z ' + format(x[0], '+.1f') if np.isfinite(x[0]) else 'prim yok'}{' ⛔' if np.isfinite(x[0]) and x[0] <= -1 else ''})" for x in grup), sinif=sinif_)
# ---- haftalık deneme raporu (pazar 20:00) ----
kap = [e for e in GS["log"] if "ok" in e]
def ozet_onay(x):
    a = [e for e in x if np.isfinite(e.get("cb", np.nan)) and e["cb"] > 0]; b = [e for e in x if np.isfinite(e.get("cb", np.nan)) and e["cb"] <= 0]
    return f"💵 ABD onaylı: {ozet(a)} | onaysız: {ozet(b)}" if (a or b) else ""
def ozet(x): return f"{sum(e['ok'] for e in x)}/{len(x)} tuttu (%{100*sum(e['ok'] for e in x)/len(x):.0f}) · ort. net %{np.mean([e['net'] for e in x]):+.2f} · toplam %{np.sum([e['net'] for e in x]):+.1f}" if x else "sonuçlanan işlem yok"
try:
    tl_ = now.tz_convert(DISPLAY_TZ).floor("h")
    if MODELS and tl_.weekday() == 6 and tl_.hour >= 20 and (GS.get("last_weekly") is None or tl_ - GS["last_weekly"] >= pd.Timedelta(days=6)):
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
