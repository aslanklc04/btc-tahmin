# tahmin_coin.py — HER SAAT (tahmin.py'den SONRA): ETH / BNB / DOGE sinyalleri. BTC sistemine dokunmaz; bir coin'de hata olursa yalnız o coin atlanır.
import os, glob, gzip, pickle, traceback
from ortak import *
import ortak as _ortak
COIN_BILDIRIM = True             # altcoin Telegram mesajları; istemezseniz False
STATE_F = "durum/gecmis_coin.pkl"
GC = {}
if os.path.exists(STATE_F):
    try:
        with open(STATE_F, "rb") as f: GC = pickle.load(f)
    except Exception: GC = {}
BTC_T, BTC_SIG = None, False                                                                 # BTC bu saatte sinyal verdi mi? (bilgi satırı için)
try:
    with open("durum/gecmis.pkl", "rb") as f: GB = pickle.load(f)
    lt = [v for v in GB.get("last_sent", {}).values() if v is not None] + [GB.get("last_star"), GB.get("last_acls")]
    lt = [v for v in lt if v is not None]; BTC_T = max(lt) if lt else None
except Exception: GB = None
def fmt(p): return f"${p:,.4f}" if p < 1 else (f"${p:,.2f}" if p < 1000 else f"${p:,.0f}")
def lvname(li): return LEV[li].split(" (")[0]
now_ms = time.time() * 1000; rows_md, logs_all = [], []
for mf in sorted(glob.glob("durum/model_*.pkl.gz")):
    NM = os.path.basename(mf)[6:-7].replace("USDT", "")
    try:
        with gzip.open(mf, "rb") as f: M = pickle.load(f)
        SYM = M["sym"]; SIG = M["SIG"]; G = GC.get(SYM)
        if G is None or G.get("created") != M["created"]:                                    # yeni eğitim: tahmin geçmişi modelden, KAYITLAR korunur
            KEEP = {k: G[k] for k in ("log", "MIC_TAIL", "HHM_TAIL") if G and k in G}
            G = dict(created=M["created"], PG={H: M["R"][H]["PG"] for H in CFG}, PL={H: M["R"][H]["PL"] for H in CFG}, ST=M["ST"], last={}, **KEEP)
        full = fetch_1h(now_ms - 4000 * 3_600_000, now_ms, sym=SYM)
        gap_h = int((full.index[-1] - min(G["PG"][H].index[-1] for H in CFG)) / pd.Timedelta(hours=1))
        mins = fetch_1m(now_ms - min(max(80, gap_h + 80), 40 * 24) * 3_600_000, now_ms, sym=SYM)
        if mins is not None and len(mins) >= 120: MIC = micro_features(mins).iloc[1:]; HHM = hourly_cv(mins).iloc[1:]
        else: MIC = M["MIC_TAIL"].iloc[:0]; HHM = M["HHM_TAIL"].iloc[:0]; print(f"⚠️ {NM}: dakika verisi alınamadı")
        def _merge(old, new_):
            x = pd.concat([old, new_]) if len(new_) else old; x = x[~x.index.duplicated(keep="last")].sort_index(); return x.iloc[-1500:]
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
        now = {"star": cur[4] == (1, 2) and cur[8] == (1, 2), "u4": cur[4] == (1, 2), "acls": am >= 0.85}
        # ---- sonuç takibi (coin'in kendi fiyatıyla) ----
        LOG = G.setdefault("log", [])
        for e_ in LOG:
            tt = e_["t"] + pd.Timedelta(hours=e_["H"])
            if "ok" not in e_ and tt in full.index:
                p2 = float(full.close.loc[tt]); e_["ok"] = bool(p2 > e_["p"]); e_["ret"] = (p2 / e_["p"] - 1) * 100
        G["log"] = [e_ for e_ in LOG if t - e_["t"] <= pd.Timedelta(days=60)]
        # ---- bildirim: aynı saatte birden fazla sinyal tek mesajda; öncelik ⭐ > 4s Çok güçlü ↑ > A sınıfı ----
        fire = [k for k in ("star", "u4", "acls") if now[k] and SIG[k]["on"] and (G["last"].get(k) is None or t - G["last"][k] >= pd.Timedelta(hours=SIG[k]["H"]))]
        tloc = t.tz_convert(DISPLAY_TZ); head = f"🧭 {NM} {tloc:%d.%m %H:%M} · {fmt(price)}"
        ufuk = " · ".join(f"{CFG[H]['ad']}: {'⬆️' if cur[H][0] == 1 else '⬇️'} {lvname(cur[H][1])}" for H in CFG)
        if fire:
            k0 = fire[0]; s0 = SIG[k0]
            baslik = {"star": f"🪙 {NM} ⭐ EN GÜÇLÜ SİNYAL — {head}\n4 ve 8 saat birlikte 'Çok güçlü YUKARI' · geçmiş (2024+, canlı ölçüm): 4s isabet %{s0['acc_h4']:.0f} · 8s %{s0['acc_h']:.0f} · haftada ~{s0['wk']:.1f}",
                      "u4": f"🪙 {NM} 4 SAAT ÇOK GÜÇLÜ ↑ — {head}\nGeçmiş (2024+, canlı ölçüm): 4 saat sonra isabet %{s0['acc_h']:.0f} · haftada ~{s0['wk']:.1f}",
                      "acls": f"🪙 {NM} 🟢 A SINIFI — {head}\n1s+4s+8s birlikte güçlü yukarı (ortalama yüzdelik {am:.2f}) · geçmiş (2024+): 4 saat sonra isabet %{s0['acc_h']:.0f} · haftada ~{s0['wk']:.1f}"}[k0]
            ek = [SIG[k]["ad"] for k in fire[1:]]
            btc_ = "BTC bu saatte de sinyal verdi" if (BTC_T is not None and BTC_T == t) else "BTC bu saatte sinyal vermedi"
            txt = (baslik + ("\nBu saatte ayrıca: " + " · ".join(ek) if ek else "") + f"\n{ufuk}\n{btc_}\n"
                   "⏱️ Gecikmeden hareket edin. ℹ️ İsabet testinden geçti; komisyon sonrası kâr kanıtlanmadı.")
            if COIN_BILDIRIM: tg_send(txt)
            for k in fire:
                G["last"][k] = t; G["log"].append(dict(t=t, tip=f"{NM} {SIG[k]['ad']}", H=SIG[k]["H"], sg=1, p=price))
        wk7 = [e_ for e_ in G["log"] if "ok" in e_ and t - e_["t"] <= pd.Timedelta(days=7)]; logs_all += G["log"]
        acik = " · ".join(f"{v['ad']} %{v['olcu']:.0f}" for v in SIG.values() if v["on"]) or "yok"
        son7 = (str(sum(x["ok"] for x in wk7)) + "/" + str(len(wk7))) if wk7 else "—"
        rows_md.append(f"| {NM} | {fmt(price)} | " + " | ".join(f"{'⬆️' if cur[H][0] == 1 else '⬇️'} {lvname(cur[H][1])}" for H in CFG)
                       + f" | {'**VAR**' if now['star'] else '✘'} | {am:.2f}{' **VAR**' if now['acls'] else ''} | {acik} | {son7} |")
        GC[SYM] = G
        for d_ in ("PG", "PL"):
            for H in CFG: G[d_][H] = G[d_][H][G[d_][H].index >= G[d_][H].index[-1] - pd.Timedelta(days=70)]
        G["ST"] = G["ST"][G["ST"].index >= G["ST"].index[-1] - pd.Timedelta(days=70)]
        print(f"✅ {NM}: {ufuk} · ⭐ {now['star']} · A {am:.2f} · bildirim: {fire or '-'}")
    except Exception:
        traceback.print_exc(); rows_md.append(f"| {NM} | ⚠️ bu saat hesaplanamadı | | | | | | | |")
# ---- haftalık altcoin raporu (pazar 20:00, BTC raporuyla aynı saatte) ----
try:
    tl_ = pd.Timestamp.now(tz=DISPLAY_TZ).floor("h")
    if rows_md and tl_.weekday() == 6 and tl_.hour == 20 and (GC.get("_last_weekly") is None or tl_ - GC["_last_weekly"] >= pd.Timedelta(days=6)):
        wk_ = [e_ for e_ in logs_all if "ok" in e_ and pd.Timestamp.now(tz="UTC") - e_["t"] <= pd.Timedelta(days=7)]
        if wk_:
            by = {}
            for e_ in wk_: by.setdefault(e_["tip"], []).append(e_)
            body = "\n".join(f"• {k}: {sum(x['ok'] for x in v)}/{len(v)} tuttu (%{100*sum(x['ok'] for x in v)/len(v):.0f}) · ort. %{np.mean([x['ret'] for x in v]):+.2f}" for k, v in by.items())
            tot = sum(x["ok"] for x in wk_); tg_send(f"🪙📊 ALTCOİN HAFTALIK SONUÇ — son 7 gün\n{body}\nToplam: {tot}/{len(wk_)} tuttu (%{100*tot/len(wk_):.0f})")
        else: tg_send("🪙📊 ALTCOİN HAFTALIK SONUÇ — son 7 günde sonuçlanan altcoin sinyali yok.")
        GC["_last_weekly"] = tl_
except Exception: traceback.print_exc()
# ---- panel: son_durum.md'ye altcoin bölümü ----
if rows_md:
    md = ("\n## 🪙 Altcoinler (kendi modelleriyle)\n| Coin | Fiyat | 1 saat | 4 saat | 8 saat | ⭐ | A sınıfı (eşik 0,85) | Açık bildirimler (2024+ isabet) | Son 7 gün |\n|---|---|---|---|---|---|---|---|---|\n"
          + "\n".join(rows_md) + "\n\n_Altcoin sinyalleri isabet testinden geçti; komisyon sonrası kâr kanıtlanmadı. Bir sinyalin 2024+ isabeti %58'in altına düşerse aylık eğitimde bildirimi kendiliğinden kapanır._\n")
    if os.path.exists("son_durum.md"): open("son_durum.md", "a").write(md)
    print(md)
with open(STATE_F, "wb") as f: pickle.dump(GC, f)
