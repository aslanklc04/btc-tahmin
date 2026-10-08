# tahmin_coin.py — HER SAAT (tahmin.py'den SONRA): altcoin sinyalleri (durum/model_*.pkl.gz). BTC sistemine dokunmaz; bir coin'de hata olursa yalnız o coin atlanır.
# v3: 🤝 BTC + coin ORTAK SİNYAL (coin sinyali, BTC'nin 4s Çok güçlü ↑ sinyaliyle aynı saatte; liste: durum/ortak_acik.csv, aylık denetlenir)
# v4: 🔇 BTC SESSİZKEN coin sinyali (BTC'de ⭐ / 4s Çok güçlü ↑ / A sınıfı yokken; liste: durum/tek_acik.csv, aylık denetlenir)
#     her ufuk için beklenen fiyat + %80 aralık · küçük fiyat biçimi (SHIB, PEPE) · yalnız bildirimi açık coin'ler hesaplanır · altcoin mesaj günlüğü
import os, glob, gzip, pickle, traceback
from concurrent.futures import ThreadPoolExecutor
from ortak import *
import ortak as _ortak
COIN_BILDIRIM = True             # altcoin Telegram mesajları; istemezseniz False
STATE_F = "durum/gecmis_coin.pkl"; AD = {"star": "⭐ en güçlü", "u4": "4s Çok güçlü ↑", "acls": "🟢 A sınıfı"}
GC = {}
if os.path.exists(STATE_F):
    try:
        with open(STATE_F, "rb") as f: GC = pickle.load(f)
    except Exception: GC = {}
JOINT, TEK = {}, {}                                                                          # {sembol: {sinyal: satır}} — 🤝 ortak / 🔇 BTC sessizken listeleri
for _f, _d in [("durum/ortak_acik.csv", JOINT), ("durum/tek_acik.csv", TEK)]:
    try:
        for _, r in pd.read_csv(_f).iterrows(): _d.setdefault(r.sym, {})[r.sinyal] = r
    except Exception: pass
BTC_T, BTC_STRONG, BTC_QUIET, BTC_LAST = None, False, False, None                            # BTC'nin bu saatteki durumu (tahmin.py az önce kaydetti)
try:
    with open("durum/gecmis.pkl", "rb") as f: GB = pickle.load(f)
    _e = pd.Series(dtype=float); sf4 = signal_frame(GB["PG"][4], GB["PL"][4], _e, False).iloc[-1]
    BTC_T = GB["PG"][4].index[-1]; BTC_STRONG = bool(sf4.S > 0 and sf4.C >= sf4.T10)          # BTC 4s Çok güçlü ↑ (⭐ bunu da içerir)
    _fr = {1: frame_from_S(cz(GB["ST"])).S, 4: signal_frame(GB["PG"][4], GB["PL"][4], _e, False).S, 8: signal_frame(GB["PG"][8], GB["PL"][8], _e, False).S}
    BTC_ACLS = float(np.mean([rpct(_fr[H].iloc[-800:]).iloc[-1] for H in CFG])) >= 0.85
    BTC_QUIET = (not BTC_STRONG) and (not BTC_ACLS)                                           # BTC'de ⭐ / 4s Çok güçlü ↑ / A sınıfı yok
    lt = [v for v in GB.get("last_sent", {}).values() if v is not None] + [GB.get("last_star"), GB.get("last_acls")]
    lt = [v for v in lt if v is not None]; BTC_LAST = max(lt) if lt else None
except Exception: traceback.print_exc()
def fmt(p):
    if not np.isfinite(p) or p <= 0: return "$?"
    if p >= 1000: return f"${p:,.0f}"
    if p >= 1: return f"${p:,.2f}"
    return f"${p:.{min(12, 3 - int(np.floor(np.log10(p))))}f}"                               # 4 anlamlı basamak: 0,09021 · 0,00001234
def lvname(li): return LEV[li].split(" (")[0]
CBD = cb_prim(); CBZ, CBL = cb_z(CBD), cb_satir(CBD)                                         # 💵 ABD alıyor mu? (tahmin.py bu saat hesapladı; dosyadan)
_tg_raw = tg_send
def tg_send(text):                                                                           # altcoin gönderimlerini kaydet (panelde görünür)
    ok = _tg_raw(text); GC.setdefault("_tglog", []).append(dict(t=pd.Timestamp.now(tz="UTC"), tip=text.split("\n")[0][:70], ok=ok, info=_ortak.TG_LAST["info"]))
    GC["_tglog"] = GC["_tglog"][-20:]; return ok
now_ms = time.time() * 1000; rows_md, logs_all, kapali, ortak_msg = [], [], [], []
JOBS = []                                                                                    # 1) modeller ve geçmiş (hızlı)
for mf in sorted(glob.glob("durum/model_*.pkl.gz")):
    NM = os.path.basename(mf)[6:-7].replace("USDT", "")
    try:
        with gzip.open(mf, "rb") as f: M = pickle.load(f)
        SYM = M["sym"]
        if not any(v["on"] for v in M["SIG"].values()) and SYM not in JOINT and SYM not in TEK: kapali.append(NM); continue   # açık sinyali yok: bu ay izlenmez
        G = GC.get(SYM)
        if G is None or G.get("created") != M["created"]:                                    # yeni eğitim: tahmin geçmişi modelden, KAYITLAR korunur
            KEEP = {k: G[k] for k in ("log", "MIC_TAIL", "HHM_TAIL", "last") if G and k in G}
            G = dict(created=M["created"], PG={H: M["R"][H]["PG"] for H in CFG}, PL={H: M["R"][H]["PL"] for H in CFG}, ST=M["ST"], last={}); G.update(KEEP)
        gap_h = int((pd.Timestamp(now_ms, unit="ms", tz="UTC") - min(G["PG"][H].index[-1] for H in CFG)) / pd.Timedelta(hours=1))
        JOBS.append((NM, SYM, M, G, min(max(80, gap_h + 80), 40 * 24)))
    except Exception: traceback.print_exc(); rows_md.append(f"| {NM} | ⚠️ model okunamadı | | | | | | | | |")
def _fetch(j):                                                                               # 2) veri: coin'ler paralel
    try: return fetch_1h(now_ms - 3200 * 3_600_000, now_ms, sym=j[1]), fetch_1m(now_ms - j[4] * 3_600_000, now_ms, sym=j[1])
    except Exception: traceback.print_exc(); return None, None
with ThreadPoolExecutor(max(1, min(16, len(JOBS)))) as ex: DATA = list(ex.map(_fetch, JOBS))
def _merge(old, new_):
    x = pd.concat([old, new_]) if len(new_) else old; x = x[~x.index.duplicated(keep="last")].sort_index(); return x.iloc[-1500:]
for (NM, SYM, M, G, _), (full, mins) in zip(JOBS, DATA):                                    # 3) sinyaller
    try:
        SIG = M["SIG"]; JO = JOINT.get(SYM, {}); TK = TEK.get(SYM, {})
        if full is None or len(full) < 2900: raise RuntimeError("saatlik veri alınamadı")
        if mins is not None and len(mins) >= 120: MIC = micro_features(mins).iloc[1:]; HHM = hourly_cv(mins).iloc[1:]
        else: MIC = M["MIC_TAIL"].iloc[:0]; HHM = M["HHM_TAIL"].iloc[:0]; print(f"⚠️ {NM}: dakika verisi alınamadı")
        MICX = _merge(G.get("MIC_TAIL", M["MIC_TAIL"]), MIC); HHMX = _merge(G.get("HHM_TAIL", M["HHM_TAIL"]), HHM); G["MIC_TAIL"], G["HHM_TAIL"] = MICX, HHMX
        Fl = features(full).iloc[-2000:]; t = Fl.index[-1]; price = float(full.close.loc[t])
        FR = {1: Fl.join(MICX.reindex(Fl.index)), 4: Fl.join(path2_features(full.close, HHMX, MICX).reindex(Fl.index)), 8: Fl}
        for H in CFG:
            new = Fl.index[Fl.index > G["PG"][H].index[-1]]
            if len(new):
                pg, pl = M["R"][H]["model"](FR[H].loc[new]); G["PG"][H] = pd.concat([G["PG"][H], pd.Series(pg, index=new)]); G["PL"][H] = pd.concat([G["PL"][H], pd.Series(pl, index=new)])
        rhs = {H: Fl[f"r{H}"] for H in CFG}; Sb = {H: signal_frame(G["PG"][H], G["PL"][H], rhs[H], False).S for H in CFG}
        newi = Sb[1].index[Sb[1].index > G["ST"].index[-1]]
        if len(newi):
            Xn = pd.DataFrame({"S1": Sb[1], "S4": Sb[4], "S8": Sb[8]}).reindex(newi).ffill().fillna(0).clip(-5, 5)
            G["ST"] = pd.concat([G["ST"], pd.Series(M["STACK"].decision_function(Xn[["S1", "S4", "S8"]]), index=newi)])
        FRM = {1: frame_from_S(cz(G["ST"])), 4: signal_frame(G["PG"][4], G["PL"][4], rhs[4], False), 8: signal_frame(G["PG"][8], G["PL"][8], rhs[8], False)}
        cur = {}
        for H in CFG:
            sf = FRM[H].iloc[-1]; sg = 1 if sf.S > 0 else -1; li = 2 if sf.C >= sf.T10 else (1 if sf.C >= sf.T30 else 0); cur[H] = (sg, li)
        pct = {H: float(rpct(FRM[H].S.iloc[-800:]).iloc[-1]) for H in CFG}; am = float(np.mean(list(pct.values())))
        RNG = {}                                                                             # fiyat aralığı (BTC ile aynı yöntem)
        for H in CFG:
            X_ = M["R"][H]
            if "QM" in X_:
                q = np.sort([X_["QM"][qq].predict(Fl.loc[[t], M["FEATS"]])[0] for qq in (0.1, 0.5, 0.9)]); RNG[H] = price * np.exp([q[0] - X_["QC"], q[1], q[2] + X_["QC"]])
        DON = f"{M.get('EVAL0', pd.Timestamp(HOLD_START, tz='UTC')):%Y}+"
        now = {"star": cur[4] == (1, 2) and cur[8] == (1, 2), "u4": cur[4] == (1, 2), "acls": am >= 0.85}
        btc_ok = BTC_STRONG and BTC_T == t; btc_sessiz = BTC_QUIET and BTC_T == t
        # ---- sonuç takibi (coin'in kendi fiyatıyla) ----
        LOG = G.setdefault("log", [])
        for e_ in LOG:
            tt = e_["t"] + pd.Timedelta(hours=e_["H"])
            if "ok" not in e_ and tt in full.index:
                p2 = float(full.close.loc[tt]); e_["ok"] = bool(p2 > e_["p"]); e_["ret"] = (p2 / e_["p"] - 1) * 100
        G["log"] = [e_ for e_ in LOG if t - e_["t"] <= pd.Timedelta(days=60)]
        G.setdefault("last", {})
        yeni = lambda k: G["last"].get(k) is None or t - G["last"][k] >= pd.Timedelta(hours=SIG[k]["H"])
        f_ortak = [k for k in ("star", "u4", "acls") if now[k] and btc_ok and k in JO and yeni(k)]
        f_tek = [k for k in ("star", "u4", "acls") if now[k] and (SIG[k]["on"] or (k in TK and btc_sessiz)) and k not in f_ortak and yeni(k)]
        CBO = cb_prim(NM) if (f_ortak or f_tek) else None; ZC = cb_coin_z(NM, CBO, CBD)              # 💵 coin'in KENDİ Coinbase primi (yalnız sinyal varsa)
        tloc = t.tz_convert(DISPLAY_TZ); head = f"🧭 {NM} {tloc:%d.%m %H:%M} · {fmt(price)}"
        ufuk = " · ".join(f"{CFG[H]['ad']}: {'⬆️' if cur[H][0] == 1 else '⬇️'} {lvname(cur[H][1])}" for H in CFG)
        ufuk_tg = "\n".join(f"{CFG[H]['ad']}: {'⬆️' if cur[H][0] == 1 else '⬇️'} {lvname(cur[H][1])}" + (f"\n   beklenen {fmt(RNG[H][1])} · %80 aralık {fmt(RNG[H][0])}–{fmt(RNG[H][2])}" if H in RNG else "") for H in CFG)
        if f_ortak:                                                                          # 🤝 bu saatin ortak mesajında toplanır
            r4 = (f" → 4s beklenen {fmt(RNG[4][1])} (%80: {fmt(RNG[4][0])}–{fmt(RNG[4][2])})" if 4 in RNG else "")
            ortak_msg.append(f"• {NM} {fmt(price)} — " + " · ".join(f"{AD[k]} %{JO[k]['isabet']:.0f}" for k in f_ortak) + r4
                             + f" · 💵 {NM}: {cb_kisa(CBO) if CBO else 'prim yok'}" + (" (yalnız bilgi)" if NM in CB_BILGI else (" ⛔ ALMA" if np.isfinite(cb_z(CBO)) and cb_z(CBO) <= -1 else "")))
            for k in f_ortak: G["last"][k] = t; G["log"].append(dict(t=t, tip=f"🤝 {NM} {AD[k]}", H=SIG[k]["H"], sg=1, p=price, cb=ZC))
        if f_tek:
            k0 = f_tek[0]; s0 = SIG[k0]
            if not SIG[k0]["on"]:                                                            # yalnız 🔇 listesinden: BTC'de fırsat yokken coin'de fırsat
                baslik = (f"🪙🔇 {NM} {dict(star='⭐ EN GÜÇLÜ', u4='4 SAAT ÇOK GÜÇLÜ ↑', acls='🟢 A SINIFI')[k0]} — BTC SESSİZKEN — {head}\nBTC'de güçlü sinyal yokken bu coin'de {AD[k0]} · geçmiş (2024+, BTC sessizken): "
                          f"4 saat sonra isabet %{TK[k0]['isabet']:.0f} · haftada ~{TK[k0]['haftada']:.1f}")
            elif k0 == "star": baslik = f"🪙 {NM} ⭐ EN GÜÇLÜ SİNYAL — {head}\n4 ve 8 saat birlikte 'Çok güçlü YUKARI' · geçmiş ({DON}, canlı ölçüm): 4s isabet %{s0['acc_h4']:.0f} · 8s %{s0['acc_h']:.0f} · haftada ~{s0['wk']:.1f}"
            elif k0 == "u4": baslik = f"🪙 {NM} 4 SAAT ÇOK GÜÇLÜ ↑ — {head}\nGeçmiş ({DON}, canlı ölçüm): 4 saat sonra isabet %{s0['acc_h']:.0f} · haftada ~{s0['wk']:.1f}"
            else: baslik = f"🪙 {NM} 🟢 A SINIFI — {head}\n1s+4s+8s birlikte güçlü yukarı (ortalama yüzdelik {am:.2f}) · geçmiş ({DON}): 4 saat sonra isabet %{s0['acc_h']:.0f} · haftada ~{s0['wk']:.1f}"
            if SIG[k0]["on"] and k0 in TK and btc_sessiz: baslik += f"\n🔇 BTC sessizken bu sinyalin geçmişi: %{TK[k0]['isabet']:.0f}"
            ek = [AD[k] for k in f_tek[1:]]
            btc_ = "BTC bu saatte de sinyal verdi" if (BTC_LAST is not None and BTC_LAST == t) else "BTC bu saatte sinyal vermedi"
            txt = (baslik + ("\nBu saatte ayrıca: " + " · ".join(ek) if ek else "") + f"\n{ufuk_tg}\n{btc_}\n{cb_satir_coin(NM, CBO, CBD)}\n"
                   "⏱️ Gecikmeden hareket edin. ℹ️ İsabet testinden geçti; komisyon sonrası kâr kanıtlanmadı.")
            if COIN_BILDIRIM: tg_send(txt)
            for k in f_tek: G["last"][k] = t; G["log"].append(dict(t=t, tip=f"{NM} {AD[k]}" + (" 🔇" if btc_sessiz and k in TK else ""), H=SIG[k]["H"], sg=1, p=price, cb=ZC))
        wk7 = [e_ for e_ in G["log"] if "ok" in e_ and t - e_["t"] <= pd.Timedelta(days=7)]; logs_all += G["log"]
        acik = " · ".join([f"{AD[k]} %{v['olcu']:.0f}" for k, v in SIG.items() if v["on"]] + [f"🔇 {AD[k]} %{TK[k]['isabet']:.0f}" for k in ("star", "u4", "acls") if k in TK]) or "—"
        ort_ = " · ".join(f"{AD[k]} %{JO[k]['isabet']:.0f}" for k in ("star", "u4", "acls") if k in JO) or "—"
        son7 = (str(sum(x["ok"] for x in wk7)) + "/" + str(len(wk7))) if wk7 else "—"
        rows_md.append(f"| {NM} | {fmt(price)} | " + " | ".join(f"{'⬆️' if cur[H][0] == 1 else '⬇️'} {lvname(cur[H][1])}" + (f"<br>{fmt(RNG[H][1])} ({fmt(RNG[H][0])}–{fmt(RNG[H][2])})" if H in RNG else "") for H in CFG)
                       + f" | {'**VAR**' if now['star'] else '✘'} | {am:.2f}{' **VAR**' if now['acls'] else ''} | {acik} | {ort_} | {son7} |")
        GC[SYM] = G
        for d_ in ("PG", "PL"):
            for H in CFG: G[d_][H] = G[d_][H][G[d_][H].index >= G[d_][H].index[-1] - pd.Timedelta(days=70)]
        G["ST"] = G["ST"][G["ST"].index >= G["ST"].index[-1] - pd.Timedelta(days=70)]
        print(f"✅ {NM}: {ufuk} · ⭐ {now['star']} · A {am:.2f} · ortak {f_ortak or '-'} · tek {f_tek or '-'}")
    except Exception:
        traceback.print_exc(); rows_md.append(f"| {NM} | ⚠️ bu saat hesaplanamadı | | | | | | | | |")
if ortak_msg and COIN_BILDIRIM and BTC_T is not None:                                        # 🤝 tek mesaj: bu saatte BTC güçlüyken gelen tüm coin sinyalleri
    tl0 = BTC_T.tz_convert(DISPLAY_TZ)
    tg_send(f"🤝 BTC GÜÇLÜYKEN COİN SİNYALLERİ — {tl0:%d.%m %H:%M}\nBTC 4s Çok güçlü ↑ ve aynı saatte bu coin'ler de güçlü (geçmiş 2024+, 4 saat sonra isabet):\n" + "\n".join(ortak_msg)
            + "\n💵 BTC geneli: " + cb_kisa(CBD) + " · her satırda coin'in kendi Coinbase primi (⛔ = ABD o coin'i satıyor, alma)\n⏱️ Gecikmeden hareket edin. ℹ️ Aynı anda gelen sinyaller birbirine bağlıdır: BTC dönerse çoğu birlikte döner. Komisyon sonrası kâr kanıtlanmadı.")
# ---- haftalık altcoin raporu (pazar 20:00, BTC raporuyla aynı saatte) ----
try:
    tl_ = pd.Timestamp.now(tz=DISPLAY_TZ).floor("h")
    if (rows_md or kapali) and tl_.weekday() == 6 and tl_.hour == 20 and (GC.get("_last_weekly") is None or tl_ - GC["_last_weekly"] >= pd.Timedelta(days=6)):
        wk_ = [e_ for e_ in logs_all if "ok" in e_ and pd.Timestamp.now(tz="UTC") - e_["t"] <= pd.Timedelta(days=7)]
        if wk_:
            by = {}
            for e_ in wk_: by.setdefault(e_["tip"], []).append(e_)
            body = "\n".join(f"• {k}: {sum(x['ok'] for x in v)}/{len(v)} tuttu (%{100*sum(x['ok'] for x in v)/len(v):.0f}) · ort. %{np.mean([x['ret'] for x in v]):+.2f}" for k, v in by.items())
            oo = [x for x in wk_ if x["tip"].startswith("🤝")]; tt_ = [x for x in wk_ if not x["tip"].startswith("🤝")]
            ozet = (f"\n🤝 ortak: {sum(x['ok'] for x in oo)}/{len(oo)}" if oo else "") + (f" · tek başına: {sum(x['ok'] for x in tt_)}/{len(tt_)}" if tt_ else "")
            cbo = cb_ozet(wk_); ozet += ("\n" + cbo if cbo else "")
            tot = sum(x["ok"] for x in wk_); tg_send(f"🪙📊 ALTCOİN HAFTALIK SONUÇ — son 7 gün\n{body}\nToplam: {tot}/{len(wk_)} tuttu (%{100*tot/len(wk_):.0f}){ozet}")
        else: tg_send("🪙📊 ALTCOİN HAFTALIK SONUÇ — son 7 günde sonuçlanan altcoin sinyali yok.")
        GC["_last_weekly"] = tl_
except Exception: traceback.print_exc()
# ---- panel: son_durum.md'ye altcoin bölümü ----
if rows_md or kapali:
    tl = GC.get("_tglog", [])[-10:]
    md = ("\n## 🪙 Altcoinler (kendi modelleriyle)\n"
          f"BTC şu an: **{'4s Çok güçlü ↑ — 🤝 ortak sinyaller etkin' if BTC_STRONG else ('sessiz (⭐ / 4s Çok güçlü ↑ / A yok) — 🔇 BTC sessizken sinyalleri etkin' if BTC_QUIET else 'A sınıfı var — ortak/sessiz listeleri bu saat beklemede')}**\n\n"
          "| Coin | Fiyat | 1 saat | 4 saat | 8 saat | ⭐ | A sınıfı (eşik 0,85) | Tek başına açık · 🔇 BTC sessizken (isabet) | 🤝 BTC ile ortak açık (isabet) | Son 7 gün |\n|---|---|---|---|---|---|---|---|---|---|\n"
          + "\n".join(rows_md) + "\n\nHücrelerde: yön · beklenen fiyat (%80 aralık)."
          + (f" Bu ay açık sinyali olmayan (izlenmeyen): {', '.join(kapali)}." if kapali else "")
          + "\n\n_Altcoin sinyalleri isabet testinden geçti; komisyon sonrası kâr kanıtlanmadı. Her ay yeniden denetlenir. 🤝 ortak sinyal: coin sinyali BTC'nin 4s Çok güçlü ↑ sinyaliyle aynı saatte gelirse (19 coin taraması: 2020–23 %63–64, 2024+ %59–61; BTC sessizken %53–56)._\n"
          + "\n### 📨 Altcoin mesajları (son 10)\n" + ("\n".join(f"- {x['t'].tz_convert(DISPLAY_TZ):%d.%m %H:%M} · {'✅' if x['ok'] else '❌'} · {x['tip']} · {x['info']}" for x in reversed(tl)) if tl else "- (henüz gönderim yok)") + "\n")
    if os.path.exists("son_durum.md"): open("son_durum.md", "a").write(md)
    print(md)
with open(STATE_F, "wb") as f: pickle.dump(GC, f)
