# tahmin.py — HER SAAT: kayıtlı v34 modelleriyle son saatin tahminini yapar, gerekirse Telegram'a yazar, son_durum.md'yi günceller
import os, gzip, pickle
from ortak import *
A_SINIFI_BILDIRIM = True       # 🟢 A sınıfı (haftada ~10) için de Telegram mesajı; istemezseniz False
HAFTALIK_RAPOR = True          # her pazar 20:00'de geçen haftanın sinyal sonuçları
GUNLUK_OZET_SAATI = 9          # her gün bu saatte (İstanbul) kısa bir "sistem çalışıyor" özeti gönderilir; istemezseniz None yapın
if not os.path.exists("durum/model.pkl.gz"): print("⚠️ Model yok: önce 'Aylık eğitim' iş akışını elle çalıştırın."); raise SystemExit(0)
with gzip.open("durum/model.pkl.gz", "rb") as f: M = pickle.load(f)
G = None
if os.path.exists("durum/gecmis.pkl"):
    with open("durum/gecmis.pkl", "rb") as f: G = pickle.load(f)
    if G.get("created") != M["created"]: G = None                                     # yeni eğitim yapılmış: geçmişi modelden başlat
if G is None:
    G = dict(created=M["created"], PG={H: M["R"][H]["PG"] for H in CFG}, PL={H: M["R"][H]["PL"] for H in CFG}, ST=M["ST"],
             BPG={B: M["BAR"][B]["PG"] for B in M["BHS"]}, BPL={B: M["BAR"][B]["PL"] for B in M["BHS"]}, last_sent={}, last_star=None, last_daily=None, last_acls=None)
import ortak as _ortak
_tg_raw = tg_send
def tg_send(text):                                                                       # her gönderimi kaydet (teşhis)
    ok = _tg_raw(text); G.setdefault("tglog", []).append(dict(t=pd.Timestamp.now(tz="UTC"), tip=text.split("\n")[0][:60], ok=ok, info=_ortak.TG_LAST["info"]))
    G["tglog"] = G["tglog"][-20:]; return ok
if not G.get("tg_tested_v341"):
    tg_send("📡 Bağlantı testi: saatlik tahmin Telegram'a ulaşabiliyor (v34.1). Bundan sonra sinyaller bu sohbete gelecek."); G["tg_tested_v341"] = True
FEATS, FEATS1, FEATS4, BK, BHS = M["FEATS"], M["FEATS1"], M["FEATS4"], M["BK"], M["BHS"]
now_ms = time.time() * 1000
full = fetch_1h(now_ms - 4000 * 3_600_000, now_ms)                                     # son ~5,5 ay saatlik
gap_h = int((full.index[-1] - min(G["PG"][H].index[-1] for H in CFG)) / pd.Timedelta(hours=1))
mins = fetch_1m(now_ms - min(max(80, gap_h + 80), 40 * 24) * 3_600_000, now_ms)         # eksik saatleri de kapsayan dakika verisi
if mins is None or len(mins) < 120: time.sleep(5); mins = fetch_1m(now_ms - 5 * 24 * 3_600_000, now_ms)   # bir kez daha, daha geniş pencereyle dene
if mins is not None and len(mins) >= 120:
    MIC = micro_features(mins).iloc[1:]; HHM = hourly_cv(mins).iloc[1:]                 # ilk (eksik) saat atlanır
else:
    print("⚠️ Dakika verisi alınamadı: bu saat saat içi özellikler olmadan tahmin yapılıyor.")
    MIC = pd.DataFrame(columns=[f for f in FEATS1 if f.startswith("m_")], dtype="float32"); HHM = pd.DataFrame(columns=["cv", "v"], dtype="float64")
Fl = features(full).iloc[-2000:]; t = Fl.index[-1]; price = float(full.close.loc[t])
Fl1 = Fl.join(MIC.reindex(Fl.index)); Fl4 = Fl.join(path2_features(full.close, HHM, MIC).reindex(Fl.index))
FR = {1: Fl1, 4: Fl4, 8: Fl}
for H in CFG:                                                                            # yeni saatlerin tahminleri
    X = M["R"][H]; new = Fl.index[Fl.index > G["PG"][H].index[-1]]
    if len(new):
        pg, pl = X["model"](FR[H].loc[new]); G["PG"][H] = pd.concat([G["PG"][H], pd.Series(pg, index=new)]); G["PL"][H] = pd.concat([G["PL"][H], pd.Series(pl, index=new)])
for B in BHS:
    new = Fl.index[Fl.index > G["BPG"][B].index[-1]]
    if len(new):
        pg, pl = M["BAR"][B]["model"](Fl.loc[new]); G["BPG"][B] = pd.concat([G["BPG"][B], pd.Series(pg, index=new)]); G["BPL"][B] = pd.concat([G["BPL"][B], pd.Series(pl, index=new)])
rhs = {H: Fl[f"r{H}"] for H in CFG}
Sb = {H: signal_frame(G["PG"][H], G["PL"][H], rhs[H], CFG[H]["don"]).S for H in CFG}
newi = Sb[1].index[Sb[1].index > G["ST"].index[-1]]
if len(newi):
    Xn = pd.DataFrame({"S1": Sb[1], "S4": Sb[4], "S8": Sb[8]}).reindex(newi).ffill().fillna(0).clip(-5, 5)
    G["ST"] = pd.concat([G["ST"], pd.Series(M["STACK"].decision_function(Xn[["S1", "S4", "S8"]]), index=newi)])
# ---- sinyaller ----
lines, md_rows, strong_up, fire = [], [], {}, False; iyi_now = False; new_sig = []
IYI_ON, GOOD_BLK, IYI = M.get("IYI_ON", False), M.get("GOOD_BLK", []), M.get("IYI", {})
for H, cf in CFG.items():
    X = M["R"][H]; sf = (frame_from_S(cz(G["ST"])) if H == 1 else signal_frame(G["PG"][H], G["PL"][H], rhs[H], cf["don"])).iloc[-1]
    sg = 1 if sf.S > 0 else -1; li = 2 if sf.C >= sf.T10 else (1 if sf.C >= sf.T30 else 0); st = X["STATS"][(li, sg)]
    q = np.sort([X["QM"][qq].predict(Fl.loc[[t], FEATS])[0] for qq in (0.1, 0.5, 0.9)]); lo, mid, hi = price * np.exp([q[0] - X["QC"], q[1], q[2] + X["QC"]])
    act, cls = action(H, sg, li, st); strong_up[H] = (sg == 1 and li == 2); tgt = (t + pd.Timedelta(hours=H)).tz_convert(DISPLAY_TZ)
    if H == 4 and IYI_ON and sg == 1 and li == 1 and (t.hour // 4) in GOOD_BLK:
        iyi_now = True; act = f"🟢 ⏰ İyi saat diliminde güçlü yukarı — planlı alım için iyi an (bu durumda geçmiş isabet %{IYI['acc']:.1f})"
    lines.append(f"{cf['ad']}: {'⬆️' if sg == 1 else '⬇️'} {LEV[li].split(' (')[0]} — {act}\n   beklenen ${mid:,.0f} · %80 aralık ${lo:,.0f}–${hi:,.0f}")
    md_rows.append(f"| {cf['ad']} | {tgt:%d.%m %H:%M} | {'⬆️' if sg == 1 else '⬇️'} {LEV[li].split(' (')[0]} | {act} | ${mid:,.0f} | ${lo:,.0f} – ${hi:,.0f} | %{st['acc']:.1f} (2024+ %{st['acc_h']:.1f}) · en güçlü ↑ %{X['STATS'][(2, 1)]['acc']:.1f} |")
    key = f"{H}_{sg}_{li}"
    if act[:1] in ("✅", "🟢", "🔴") and (G["last_sent"].get(key) is None or t - G["last_sent"][key] >= pd.Timedelta(hours=H)): fire = True; G["last_sent"][key] = t; new_sig.append((H, sg, f"{cf['ad']} {LEV[li].split(' (')[0]} {'↑' if sg == 1 else '↓'}" + (" ⏰" if (H == 4 and iyi_now) else "")))
bar_md, bar_tg = [], []
for B in BHS:
    X_ = M["BAR"][B]; bsf = signal_frame(G["BPG"][B], G["BPL"][B], rhs[B], False).iloc[-1]; bsg = 1 if bsf.S > 0 else -1; bli = 2 if bsf.C >= bsf.T10 else (1 if bsf.C >= bsf.T30 else 0)
    bst = X_["STATS"][(bli, bsg)]; sgn = float(np.log(full.close).diff().iloc[-168:].std() * np.sqrt(B)); tp, sl = price * (1 + BK * sgn), price * (1 - BK * sgn)
    bar_tg.append(f"🎯 {B}s: hedef ${tp:,.0f} / stop ${sl:,.0f} → {'önce HEDEF' if bsg == 1 else 'önce STOP'} ({LEV[bli].split(' (')[0]}, geçmiş %{bst['first']:.0f})")
    bar_md.append(f"| {B} saat | ${tp:,.0f} (+%{BK*sgn*100:.2f}) | ${sl:,.0f} (−%{BK*sgn*100:.2f}) | {'⬆️ önce HEDEF' if bsg == 1 else '⬇️ önce STOP'} · {LEV[bli].split(' (')[0]} | %{bst['first']:.1f} (2024+ %{bst['first_h']:.1f}) |")
agree = strong_up.get(4) and strong_up.get(8); a4_, a8_ = M["AGR"][("ikisi birden", 4)], M["AGR"][("ikisi birden", 8)]; AC_ = M["ACLS"]
fr_ = {1: frame_from_S(cz(G["ST"])).S, 4: signal_frame(G["PG"][4], G["PL"][4], rhs[4], False).S, 8: signal_frame(G["PG"][8], G["PL"][8], rhs[8], False).S}
pct_now = {H: float(rpct(fr_[H].iloc[-800:]).iloc[-1]) for H in CFG}; acls_m = float(np.mean(list(pct_now.values()))); acls_on = acls_m >= 0.85
tloc = t.tz_convert(DISPLAY_TZ); head = f"🧭 BTC {tloc:%d.%m %H:%M} · ${price:,.0f}"; GECIK = "⏱️ Sinyal gelince gecikmeden hareket edin (testte beklemek sonucu kötüleştirdi)."
# ---- sinyal sonuç takibi (haftalık rapor için) ----
LOG = G.setdefault("log", [])
for e_ in LOG:
    tt = e_["t"] + pd.Timedelta(hours=e_["H"])
    if "ok" not in e_ and tt in full.index:
        p2 = float(full.close.loc[tt]); e_["ok"] = bool((p2 > e_["p"]) == (e_["sg"] == 1)); e_["ret"] = (p2 / e_["p"] - 1) * e_["sg"] * 100
G["log"] = [e_ for e_ in LOG if t - e_["t"] <= pd.Timedelta(days=60)]
def logsig(tip, H, sg): G["log"].append(dict(t=t, tip=tip, H=H, sg=sg, p=price))
if agree and (G["last_star"] is None or t - G["last_star"] >= pd.Timedelta(hours=8)):
    tg_send(f"⭐ EN GÜÇLÜ SİNYAL — {head}\n4 ve 8 saat birlikte 'Çok güçlü YUKARI'\nGeçmiş (canlı ölçüm): 4s isabet %{a4_['acc']:.1f} · 8s isabet %{a8_['acc']:.1f} · haftada ~{a4_['wk']:.1f}\n"
            + (M.get("ALT_LINE", "") + "\n" if M.get("ALT_LINE") else "") + GECIK + "\n" + "\n".join(lines + bar_tg)); G["last_star"] = t; fire = False; logsig("⭐ en güçlü (8s)", 8, 1)
if acls_on and A_SINIFI_BILDIRIM and not agree and (G.get("last_acls") is None or t - G["last_acls"] >= pd.Timedelta(hours=4)):
    tg_send(f"🟢 A SINIFI SİNYAL — {head}\n1s+4s+8s birlikte güçlü yukarı (ortalama yüzdelik {acls_m:.2f})\nGeçmiş (canlı ölçüm): 4 saat sonra isabet %{AC_['acc']:.1f} · haftada ~{AC_['wk']:.0f}\n" + GECIK + "\n"
            + "\n".join(lines + bar_tg)); G["last_acls"] = t; fire = False; logsig("🟢 A sınıfı (4s)", 4, 1)
if fire:
    hdr = (f"🟢 4 SAAT GÜÇLÜ (⏰ iyi saat dilimi) — {head}\nGeçmiş (canlı ölçüm): isabet %{IYI.get('acc', float('nan')):.1f} · haftada ~{IYI.get('wk', 0):.0f}" if iyi_now else head)
    tg_send(hdr + "\n" + (GECIK + "\n" if any(x[1] == 1 for x in new_sig) else "") + "\n".join(lines + bar_tg))
    for H_, sg_, lab_ in new_sig: logsig(lab_, H_, sg_)
if HAFTALIK_RAPOR and tloc.weekday() == 6 and tloc.hour == 20 and (G.get("last_weekly") is None or t - G["last_weekly"] >= pd.Timedelta(days=6)):
    wk_ = [e_ for e_ in G["log"] if "ok" in e_ and t - e_["t"] <= pd.Timedelta(days=7)]
    if wk_:
        by = {}
        for e_ in wk_: by.setdefault(e_["tip"], []).append(e_)
        body = "\n".join(f"• {k}: {sum(x['ok'] for x in v)}/{len(v)} tuttu (%{100*sum(x['ok'] for x in v)/len(v):.0f}) · ort. %{np.mean([x['ret'] for x in v]):+.2f}" for k, v in by.items())
        tot = sum(x["ok"] for x in wk_)
        tg_send(f"📊 HAFTALIK SONUÇ — son 7 gün\n{body}\nToplam: {tot}/{len(wk_)} tuttu (%{100*tot/len(wk_):.0f})\n(Yön sinyalin ufku sonundaki fiyata göre; ort. = sinyal yönünde getiri)")
    else: tg_send("📊 HAFTALIK SONUÇ — son 7 günde sonuçlanan sinyal yok.")
    G["last_weekly"] = t
if GUNLUK_OZET_SAATI is not None and tloc.hour == GUNLUK_OZET_SAATI and (G["last_daily"] is None or t - G["last_daily"] >= pd.Timedelta(hours=20)):
    tg_send(f"☀️ Günlük özet — {head}\n⭐ en güçlü sinyal: {'VAR' if agree else 'yok'} · 🟢 A sınıfı: {'VAR' if acls_on else 'yok'}\n" + "\n".join(lines)); G["last_daily"] = t
# ---- son_durum.md (GitHub'da okunabilir panel) ----
star = (f"## ⭐ EN GÜÇLÜ SİNYAL VAR — 4 ve 8 saat birlikte 'Çok güçlü YUKARI'\nGeçmiş: 4 saat sonra isabet **%{a4_['acc']:.1f}**, 8 saat sonra **%{a8_['acc']:.1f}** ({a4_['n']} olay)" + ("\n\n" + M.get("ALT_LINE", "") if M.get("ALT_LINE") else "")
        if agree else f"⭐ En güçlü sinyal şu an **yok** (4s: {'✔' if strong_up.get(4) else '✘'} · 8s: {'✔' if strong_up.get(8) else '✘'}). Geldiğinde geçmiş isabet 4s %{a4_['acc']:.1f}, 8s %{a8_['acc']:.1f}.")
wk7 = [e_ for e_ in G["log"] if "ok" in e_ and t - e_["t"] <= pd.Timedelta(days=7)]
son7 = (f"📊 Son 7 günde sonuçlanan sinyaller: {sum(x['ok'] for x in wk7)}/{len(wk7)} tuttu" if wk7 else "📊 Son 7 günde sonuçlanan sinyal yok.")
iyi_md = f"⏰ İyi saat dilimi (4s güçlü ↑): {'**AÇIK**' if IYI_ON else 'kapalı'} · geçmiş isabet %{IYI.get('acc', float('nan')):.1f} · haftada ~{IYI.get('wk', 0):.1f}" + (" · **şu an sinyal VAR**" if iyi_now else "")
acl_md = f"🟢 A sınıfı: **{'VAR' if acls_on else 'yok'}** (üç ufkun ortalama yüzdeliği {acls_m:.2f}, eşik 0,85) · geçmiş (canlı ölçüm): haftada ~{AC_['wk']:.1f}, 4s isabet %{AC_['acc']:.1f}"
md = (f"# 🧭 BTC çok ufuklu tahmin (v34) — {tloc:%d.%m.%Y %H:%M} kapanışı · ${price:,.2f}\n\n{star}\n\n{acl_md}\n\n{iyi_md}\n\n{son7}\n\n## 📊 Yön ve fiyat aralıkları (%80)\n"
      "| Ufuk | Hedef | Yön | Karar | Beklenen | %80 aralık | Bu seviyenin geçmiş isabeti (canlı ölçüm) |\n|---|---|---|---|---|---|---|\n" + "\n".join(md_rows) +
      "\n\n## 🎯 Hedef / stop yarışı (±1σ)\n| Ufuk | Hedef | Stop | Model | Geçmişte sinyal yönünde önce bariyer |\n|---|---|---|---|---|\n" + "\n".join(bar_md) +
      f"\n\n_Model eğitimi: {M['created'].tz_convert(DISPLAY_TZ):%d.%m.%Y} · güncelleme: {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M} · ⚠️ Yatırım tavsiyesi değildir._\n")
tl = G.get("tglog", [])[-10:]
md += "\n## 📨 Telegram günlüğü (son 10 gönderim)\n" + ("\n".join(f"- {x['t'].tz_convert(DISPLAY_TZ):%d.%m %H:%M} · {'✅' if x['ok'] else '❌'} · {x['tip']} · {x['info']}" for x in reversed(tl)) if tl else "- (henüz gönderim yok)") + "\n"
md += f"\n_Çalıştırma: {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m %H:%M} · token {'VAR' if _ortak.TELEGRAM_TOKEN else 'YOK'} · sohbet kimliği {'VAR' if _ortak.TELEGRAM_CHAT_ID else 'YOK'}_\n"
open("son_durum.md", "w").write(md)
for d_ in ("PG", "PL", "BPG", "BPL"):
    for k in G[d_]: G[d_][k] = G[d_][k][G[d_][k].index >= G[d_][k].index[-1] - pd.Timedelta(days=70)]
G["ST"] = G["ST"][G["ST"].index >= G["ST"].index[-1] - pd.Timedelta(days=70)]
with open("durum/gecmis.pkl", "wb") as f: pickle.dump(G, f)
print(md)
