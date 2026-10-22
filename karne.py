# karne.py — CANLI KARNE (15.10.2026, kullanıcı isteği): gönderilen / gönderilmeyen her sinyalin GERÇEK sonucu ve testle karşılaştırma.
# Kayıt: durum/karne_kayit.csv (gonder.py her saat yazar; 12–15.10 geçmişi git kayıtlarından). Sonuç: durum/karne.md + son_durum.md özeti.
# Ölçüm testlerle aynı: giriş = sinyal saatinin kapanışı (Binance spot 1 s), çıkış = giriş + süre kapanışı, maliyet %0,04. Süresi dolmayan = açık (hesaba girmez).
# Telegram: her PAZAR TR 20:00 sonrası tek haftalık karne — TÜM sinyaller (ana · yedek · panel) tür tür not (15.10: eski 5 haftalık model raporunun yerine; onlar panele yazılır).
# ÖNCEDEN YAZILI KARAR (15.10.2026, sonuçlar görülmeden): 12.11.2026'dan itibaren ✅ ana olarak gönderilmiş bir türde ≥ 20 kapanan sinyal varsa
#   canlı isabet testteki isabetin belirgin altında (tek yönlü binom p < 0,05) VE canlı işlem başı net < 0 → "❌ ana'dan çıkarma önerisi" (kullanıcıya sorulur).
import os, re, json, math, numpy as np, pandas as pd
from ortak import fetch_1h, tg_send, DISPLAY_TZ, TUT_TEST, KARAL_K, KARAL_K_YEDEK, KARAL_K_PANEL
KAYIT_F, MD_F, DUR_F = "durum/karne_kayit.csv", "durum/karne.md", "durum/karne_durum.json"
KOM, KARAR_T = 0.04, pd.Timestamp("2026-11-12", tz=DISPLAY_TZ)
GEN = {l.strip()[:-4] for l in open("durum/genis_liste.txt") if l.strip()} if os.path.exists("durum/genis_liste.txt") else set()
PA = pd.read_csv("durum/prim_acik.csv") if os.path.exists("durum/prim_acik.csv") else pd.DataFrame(columns=["coin", "esik", "saat"])
TEST = {k: (v[0][0], v[0][2]) for k, v in TUT_TEST.items()} | {"🔇/🪙": (56.9, 53.7)} | {k + " 🔥": (74.0, 80.0) for k in ("🤝", "🧪", "🔇/🪙", "💵", "🔀")} | {"🌐🤝 🔥": (75.0, 81.0)}   # 🔥 yükselenler: ekle_ara.py / kombin.py       # (isabet tüm test, 2026) — tutma3.py · kombin.py Y3
SINIF_TEST = {"ana": (61.9, 67.1), "yedek": (59.6, 64.8)}                                   # fon_ana.py 14.10 ana seti · 16.10: yedek = 🌐🤝 eşik altı (ekle_ara.py G1)
TEST_Y = {"🌐🤝": (59.6, 64.8)}                                                                # yedekteki 🌐🤝 eşik altının kendi testi
TEST_P = {"📆": (68.0, 57.0), "🌐🤝": (59.6, 64.8), "🤝": (55.4, 52.7), "🔇/🪙": (55.4, 52.7), "🧪": (55.4, 52.7)}   # 17.10: panel türleri kendi testleriyle (🌐 eşik altı G1 · coin primi < 0 P1, filtre_kontrol.py) — ana testiyle değil
COIN_RE = re.compile(r"([A-Z0-9]{2,12}) \((?:z ([+-]?[\d.]+)[^)]*|prim yok[^)]*)\)")
def prim_saat(nm, z, sure):
    r = PA[PA.coin == nm]
    if r.empty: return sure or 24
    if z is not None: r2 = r[r.esik <= z]; r = r2 if len(r2) else r
    return int(r.sort_values("esik").saat.iloc[-1])
def coz(e, sure):
    """etiket → [(coin, süre saat, yön, tür, işaret)]"""
    isr = "".join(k for k in ("📉🔥", "💧", "💸") if k in e.split(":")[0].split("·")[0])
    if e.startswith("🔻"): return [("BTC", 24, -1, "🔻", "")]
    if e.startswith("📆"): return [("BTC", 168, 1, "📆", "")]                                    # 20.10: D10 BTC günlük (panel, izleme)
    if e.startswith("🧑"): return [(c, sure or 168, 1, "🧑", "") for c in ("BTC", "ETH")]
    if e.startswith("⛓️"):
        if "çelişkili" in e: return []
        return [("ETH", sure or 120, -1 if "SAT" in e else 1, "⛓️", "")]
    if "💵 ABD" in e:
        out = []
        for g in re.finditer(r"([A-Z0-9]{2,12}) \(z ([+-]?[\d.]+)(?:, (\d+) saat)?\)", e.split(":", 1)[1]):
            out.append((g.group(1), int(g.group(3)) if g.group(3) else prim_saat(g.group(1), float(g.group(2)), sure), 1, "💵", isr))
        return out
    if e.startswith("🧪"): return [(g.group(1), 24, 1, "🌐🧪" if g.group(1) in GEN else "🧪", isr) for g in COIN_RE.finditer(e.split(":", 1)[1])]
    if e.startswith("🤝"): return [(g.group(1), 4, 1, "🌐🤝" if g.group(1) in GEN else "🤝", isr) for g in COIN_RE.finditer(e.split(":", 1)[1])]
    if e.startswith("₿"):
        hs = [int(x) for x in re.findall(r"(\d+) saat", e)] + [int(x) for x in re.findall(r"\((\d+) s\)", e)]
        return [("BTC", max(hs) if hs else (sure or 4), -1 if ("(bilgi)" in e or "↓" in e) else 1, "🚀" if "🚀" in e else "₿", "")]
    g = re.match(r"^(\S+) ([A-Z0-9]{2,12}) .*?· (\d+) saat", e)
    if g:
        on = g.group(1); tur = "🔀" if "🔀" in on else ("🚀" if "🚀" in on else "🔇/🪙")
        return [(g.group(2), int(g.group(3)), 1, tur, "".join(k for k in ("📉🔥", "💧", "💸") if k in on))]
    g = re.match(r"^(\S+) ([A-Z0-9]{2,12}) (.*?) ·", e)                                       # 12.10 eski biçim (süre yazmıyor): ⭐ 8 s · A / 4s 4 s
    if g:
        on = g.group(1); H = 8 if ("⭐" in g.group(3) or g.group(3).startswith("8s")) else 4; tur = "🔀" if "🔀" in on else ("🚀" if "🚀" in on else "🔇/🪙")
        return [(g.group(2), H, 1, tur, "")]
    return []
def sinif(s, k):
    if s.startswith("✅"): return "ana"
    if s.startswith("🔸") and k.startswith("gönderildi"): return "yedek"
    return "panel"
def binom_alt(k, n, p):                                                                     # P(X ≤ k), X ~ Bin(n, p)
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))
def main():
    if not os.path.exists(KAYIT_F): print("karne: kayıt yok"); return
    K = pd.read_csv(KAYIT_F, dtype=str).fillna("")
    rows = []
    for r in K.itertuples():
        su = int(float(r.sure)) if r.sure else None; t0 = pd.Timestamp(r.t, tz=DISPLAY_TZ).floor("h").tz_convert("UTC")
        IM = dict(x.split(":", 1) for x in str(getattr(r, "isr", "") or "").split("|") if ":" in x)   # 19.10: mesajdaki coin işaretleri
        for nm, H, yon, tur, isr in coz(r.e, su):
            isr = "".join(m for m in ("📉🔥", "💧", "💸", "🚀") if m in isr + IM.get(nm, ""))
            rows.append(dict(t0=t0, sinif=sinif(r.s, r.k), terfi="🔥" in r.s, pden="📋" in r.s, coin=nm, H=H, yon=yon, tur=tur + (" 🔥" if "🔥" in r.s else ""), isr=isr,   # 🔥 ile yükselenler ayrı satır
                             fz=float(r.fz) if r.fz else np.nan, prim_ret="⛔" in r.e))
    X = pd.DataFrame(rows)
    if X.empty: print("karne: çözülen sinyal yok"); return
    X = X.drop_duplicates(["t0", "coin", "H", "yon", "tur"]).reset_index(drop=True)          # aynı saatte aynı sinyal iki kez (yeniden çalışma) → tek
    now = pd.Timestamp.now(tz="UTC"); bas = X.t0.min() - pd.Timedelta(days=32); P, PH = {}, {}   # 21.10: 32 gün önceden (🎯 kâr-al σ için 720 saat)
    for nm in X.coin.unique():
        try: _o = fetch_1h(bas.value // 10**6, now.value // 10**6, sym=nm + "USDT"); P[nm], PH[nm] = _o.close, _o.high
        except Exception as e: print("karne fiyat yok:", nm, e)
    net, kap, ntp, ktp = [], [], [], []
    for r in X.itertuples():
        c = P.get(r.coin); t1 = r.t0 + pd.Timedelta(hours=int(r.H))
        if c is None or r.t0 not in c.index: net.append(np.nan); kap.append(False); ntp.append(np.nan); ktp.append(False); continue
        k_ = t1 in c.index; p1 = c[t1] if k_ else c.iloc[-1]
        net.append(r.yon * 100 * (p1 / c[r.t0] - 1) - KOM); kap.append(k_)
        # 🎯 kâr-al +0,75σ (karal.py ile aynı): süre içinde saatlik YÜKSEK hedefe değerse hedeften çık · yalnız AL sinyalleri
        sg = np.log(c[c.index <= r.t0]).diff().dropna().iloc[-720:]
        kk_ = KARAL_K_PANEL if r.pden else (KARAL_K_YEDEK if r.sinif == "yedek" else KARAL_K)   # 22.10: 🔸 yedek 0,50σ · 📋 panelden 0,45σ · ✅ ana ve panel 0,75σ
        hd = c[r.t0] * (1 + kk_ * sg.std() * np.sqrt(int(r.H))) if r.yon > 0 and len(sg) >= 168 and r.tur not in ("⛓️", "🧑") else np.nan   # 21.10: ⛓️ / 🧑 mesajında 🎯 yok
        w = PH[r.coin][(PH[r.coin].index > r.t0) & (PH[r.coin].index <= t1)]
        if np.isfinite(hd) and (w >= hd).any(): ntp.append(100 * (hd / c[r.t0] - 1) - KOM); ktp.append(True)
        else: ntp.append(net[-1]); ktp.append(k_)
    X["net"], X["kap"], X["net_tp"], X["kap_tp"] = net, kap, ntp, ktp
    X = X[np.isfinite(X.net)]; Kp = X[X.kap]
    try:                                                                                   # 22.10.2026 önceden yazılı durdurma: 📋 panelden yedek 30 kapanışta (🎯 kâr-al ile) isabet < %55 ya da net < 0 → durur
        _p = X[(X.sinif == "yedek") & X.pden & X.kap_tp]
        if len(_p) >= 30 and not os.path.exists("durum/panelden_dur.json") and ((_p.net_tp > 0).mean() < 0.55 or _p.net_tp.mean() < 0):
            json.dump(dict(tarih=f"{now:%Y-%m-%d %H:%M}", n=int(len(_p)), isabet=round(100 * float((_p.net_tp > 0).mean()), 1), net=round(float(_p.net_tp.mean()), 3)), open("durum/panelden_dur.json", "w"))
            tg_send(f"📋 PANELDEN YEDEKLER DURDURULDU (önceden yazılı kural): {len(_p)} sinyal kapandı · isabet %{100 * (_p.net_tp > 0).mean():.0f} · işlem başı {_p.net_tp.mean():+.2f}% → 💵 / 🧪 ana coin / 🔇🪙 yeniden yalnız panelde.")
    except Exception as e: print("panelden kuralı:", e)
    yerel = now.tz_convert(DISPLAY_TZ)
    def ozet(m):
        k = Kp[m]; a = X[m & ~X.kap]
        return len(k), (100 * (k.net > 0).mean() if len(k) else np.nan), (k.net.mean() if len(k) else np.nan), k.net.sum(), len(a)
    f = lambda v, d=1: "—" if not np.isfinite(v) else f"{v:.{d}f}"
    L = [f"# 📒 Canlı karne — {yerel:%d.%m.%Y %H:%M}",
         f"_Kayıt: {X.t0.min().tz_convert(DISPLAY_TZ):%d.%m %H:%M} → bugün · ölçüm testlerle aynı (sinyal saati kapanışı → süre sonu kapanışı, maliyet %0,04) · açık = süresi dolmamış, hesaba girmez_\n",
         "| Sınıf | Kapanan | İsabet | İşlem başı net | Toplam | Açık | 🎯 kâr-al ile: kapanan · isabet · net | Testte isabet (tüm · 2026) |", "|---|---|---|---|---|---|---|---|"]
    def ozet_tp(m):
        k = X[m & X.kap_tp]; return len(k), (100 * (k.net_tp > 0).mean() if len(k) else np.nan), (k.net_tp.mean() if len(k) else np.nan)
    for sn, ad in (("ana", "✅ ana (gönderildi)"), ("yedek", "🔸 yedek (gönderildi)"), ("panel", "panel (gönderilmedi)")):
        n, h, a, s, o = ozet(X.sinif == sn); ts = SINIF_TEST.get(sn); nt_, ht_, at_ = ozet_tp(X.sinif == sn)
        L.append(f"| {ad} | {n} | %{f(h, 0)} | {f(a, 2)}% | {f(s, 1)}% | {o} | {nt_} · %{f(ht_, 0)} · {f(at_, 2)}% | {'%' + f(ts[0], 0) + ' · %' + f(ts[1], 0) if ts else '—'} |")
    n, h, a, s, o = ozet((X.sinif == "yedek") & X.pden); nt_, ht_, at_ = ozet_tp((X.sinif == "yedek") & X.pden)
    L.append(f"| ↳ 🔸 yedek · 📋 panelden (22.10'dan beri) | {n} | %{f(h, 0)} | {f(a, 2)}% | {f(s, 1)}% | {o} | {nt_} · %{f(ht_, 0)} · {f(at_, 2)}% | %72 (🎯 +0,45σ ile) |")
    n, h, a, s, o = ozet((X.sinif == "panel") & X.prim_ret); L.append(f"| ↳ panel · prim ⛔ (filtre) | {n} | %{f(h, 0)} | {f(a, 2)}% | {f(s, 1)}% | {o} | — | — |")
    L.append("_🎯 kâr-al ile = 21.10'dan beri mesajda yazan hedef (+0,75σ): süre içinde fiyat hedefe değdiyse oradan çıkılmış sayılır (testte ✅ ana %69–74), değmediyse süre sonu. Geçmiş sinyallere de aynı kuralla uygulanır. Hedef: ✅ ana +0,75σ · 🔸 yedek +0,50σ · 📋 panelden +0,45σ (22.10'dan beri; geçmiş sinyaller de aynı kuralla ölçülür) · ⛓️ ETH ve 🧑 küçük yatırımcıda hedef yok (süre sonunda sat)._")
    hafta_m = (X.t0 + pd.to_timedelta(X.H, unit="h")) > now - pd.Timedelta(days=7)            # son 7 günde KAPANAN
    def notu(k, ts):                                                                        # tür notu: ≥ 20 sinyal ve test varsa testle (binom), yoksa basit not
        n = len(k)
        if n < 5: return "⏳ veri az", None
        h, a = 100 * (k.net > 0).mean(), k.net.mean()
        if n >= 20 and ts is not None:
            p = binom_alt(int((k.net > 0).sum()), n, ts[0] / 100)
            if p < 0.05 and a < 0: return f"❌ testin belirgin altında (p {p:.3f})", p
            if h >= ts[0] - 5: return ("✅ iyi · testle uyumlu" if a > 0 else "⚠️ isabet testle uyumlu ama zararda"), p
            return f"⚠️ testin altında, belirgin değil (p {p:.2f})", p
        if h >= 55 and a > 0: return "✅ iyi", None
        if h < 50 and a < 0: return "❌ kötü", None
        return "⚠️ orta", None
    SN_AD = {"ana": "✅ ana", "yedek": "🔸 yedek", "panel": "panel"}
    TUR_AD = {"₿": "₿ BTC saatlik / ⭐ / A", "🚀": "🚀 BTC momentum", "🔻": "🔻 BTC kısa", "🔇/🪙": "🔇/🪙 coin tek", "🧪": "🧪 24 s ana coin", "🌐🧪": "🌐🧪 24 s geniş liste",
              "🤝": "🤝 BTC ile ortak", "🌐🤝": "🌐🤝 ortak geniş liste", "💵": "💵 ABD alıyor", "🔀": "🔀 zıt yön", "🧑": "🧑 küçük yatırımcı", "⛓️": "⛓️ arz/talep", "📆": "📆 D10 BTC günlük (trend + ABD alıyor, izleme)"}
    def tad(t_): return TUR_AD.get(t_.replace(" 🔥", ""), t_) + (" · 🔥 yükseldi" if "🔥" in t_ else "")
    L += ["", "## Tür notları — TÜM sinyaller (ana · yedek · panel)", "| Sınıf | Tür | Bu hafta kapanan | Başlangıçtan beri kapanan | İsabet | İşlem başı net | Toplam | Testte isabet (tüm · 2026) | Not |", "|---|---|---|---|---|---|---|---|---|"]
    karar, TN = [], []
    for sn in ("ana", "yedek", "panel"):
        for tur, g in X[X.sinif == sn].groupby("tur"):
            k = g[g.kap]; kw = k[hafta_m[k.index]]; n = len(k); h = 100 * (k.net > 0).mean() if n else np.nan; a = k.net.mean() if n else np.nan; ts = TEST_Y.get(tur) if sn == "yedek" else (TEST_P.get(tur) if sn == "panel" else TEST.get(tur))
            nt, p = notu(k, ts)
            if nt.startswith("❌ testin"): karar.append((tur, sn, n, h, a, ts[0]))
            hw = f"{len(kw)} · %{f(100 * (kw.net > 0).mean(), 0)}" if len(kw) else "0"
            L.append(f"| {SN_AD[sn]} | {tad(tur)} | {hw} | {n} | %{f(h, 0)} | {f(a, 2)}% | {f(k.net.sum(), 1)}% | {'%' + f(ts[0], 0) + ' · %' + f(ts[1], 0) if ts else '—'} | {nt} |")
            TN.append((sn, tur, n, h, a, len(kw), (100 * (kw.net > 0).mean() if len(kw) else np.nan), (kw.net.mean() if len(kw) else np.nan), ts, nt))
    L += ["", f"**Önceden yazılı karar (15.10.2026):** {KARAR_T:%d.%m.%Y} tarihinden itibaren ✅ ana türünde ≥ 20 kapanan sinyal varken canlı isabet testin belirgin altında (binom p < 0,05) VE işlem başı net < 0 ise → ana'dan çıkarma önerisi (kullanıcıya sorulur).",
          "_Not: ✅ iyi = isabet ≥ %55 ve kârda · ⚠️ orta · ❌ kötü = isabet < %50 ve zararda · ≥ 20 sinyal + test varsa testle karşılaştırılır · ⏳ = 5'ten az kapanan_"]
    ana_karar = [x for x in karar if x[1] == "ana"]
    ISR_TEST = {"📉🔥": (66.9, 71.4), "💧": (68.5, 69.0), "💸": (65.0, 64.0), "🚀": (64.6, 69.0)}   # ana içinde (2024+ · 2026): ozet_tablo · ld_genis · teknik_tara C4b · ozet_tablo
    ISR_SAT = []
    for mk, ts in ISR_TEST.items():
        m = (X.sinif == "ana") & X.isr.str.contains(mk, regex=False); k = Kp[m[Kp.index]]; a_ = X[m & ~X.kap]
        if len(k) or len(a_): ISR_SAT.append((mk, len(k), 100 * (k.net > 0).mean() if len(k) else np.nan, k.net.mean() if len(k) else np.nan, len(a_), ts))
    L += ["", "## İşaretli ✅ ana sinyaller (19.10'dan beri ayrı kayıt; 13.10 SHIB 📉🔥 elle eklendi)", "| İşaret | Kapanan | İsabet | İşlem başı net | Açık | Testte (2024+ · 2026) |", "|---|---|---|---|---|---|"]
    L += [f"| {mk} | {n} | %{f(h, 0)} | {f(a, 2)}% | {o} | %{ts[0]:.0f} · %{ts[1]:.0f} |" for mk, n, h, a, o, ts in ISR_SAT] or ["| — | henüz işaretli ana sinyal yok | | | | |"]
    if yerel >= KARAR_T and ana_karar: L.append("- ❌ **ÖNERİ:** " + " · ".join(f"{t} ({n} sinyal, %{h:.0f} vs test %{ts:.0f}, net {a:+.2f}%)" for t, _, n, h, a, ts in ana_karar))
    L += ["", "## Son 25 kapanan (gönderilen)", "| Saat | Sınıf | Tür | Coin | Süre | Net | |", "|---|---|---|---|---|---|---|"]
    for r in Kp[Kp.sinif != "panel"].sort_values("t0").tail(25).itertuples():
        L.append(f"| {r.t0.tz_convert(DISPLAY_TZ):%d.%m %H:%M} | {r.sinif}{' 🔥' if r.terfi else ''} | {r.tur}{(' ' + r.isr) if r.isr else ''} | {r.coin} | {r.H} s | {r.net:+.2f}% | {'✅' if r.net > 0 else '❌'} |")
    open(MD_F, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("\n".join(L))
    if os.path.exists("son_durum.md"):
        open("son_durum.md", "a", encoding="utf-8").write("\n\n## 📒 Canlı karne (ayrıntı: durum/karne.md)\n" + "\n".join(L[2:9]) + "\n")
    try: D = json.load(open(DUR_F, encoding="utf-8"))
    except Exception: D = {}
    hafta = f"{yerel:%G-%V}"
    if os.environ.get("KARNE_ZORLA") == "1" or (yerel.weekday() == 6 and yerel.hour >= 20 and D.get("hafta") != hafta):   # 15.10: PAZAR 20:00 — eski 5 haftalık rapor yerine tek mesaj
        def sat(m, ad, ts=None):
            n, h, a, s_, o = ozet(m); w = Kp[m & hafta_m]
            nt_, ht_, at_ = ozet_tp(m)
            return (f"{ad}: bu hafta {len(w)} kapandı" + (f" · %{100 * (w.net > 0).mean():.0f} · {w.net.mean():+.2f}%" if len(w) else "") +
                    f" | başlangıçtan {n} · isabet %{f(h, 0)} · işlem başı {f(a, 2)}% · toplam {f(s_, 1)}%" + (f" (testte %{ts[0]:.0f})" if ts else "")
                    + (f" · 🎯 kâr-al ile %{f(ht_, 0)} · {f(at_, 2)}%" if nt_ else ""))
        tl = [f"📒 HAFTALIK KARNE — {yerel:%d.%m.%Y} · TÜM sinyaller ({X.t0.min().tz_convert(DISPLAY_TZ):%d.%m} tarihinden beri)",
              "Ölçüm testlerle aynı: sinyal saati kapanışı → süre sonu kapanışı, maliyet %0,04. Süresi dolmayanlar sayılmaz.", "",
              sat(X.sinif == "ana", "✅ Ana", SINIF_TEST["ana"]), sat(X.sinif == "yedek", "🔸 Yedek", SINIF_TEST["yedek"]), sat(X.sinif == "panel", "Panel (gönderilmedi)"),
              sat((X.sinif == "panel") & X.prim_ret, "↳ ⛔ prim filtresinin engelledikleri"), "", "TÜR NOTLARI (başlangıçtan beri kapanan · isabet · işlem başı · bu hafta):"]
        son_sn = None
        for sn, tur, n, h, a, nw, hw, aw, ts, nt in TN:
            if sn != son_sn: tl.append(f"{SN_AD[sn]}:"); son_sn = sn
            tl.append(f"• {tad(tur)}: {n} · %{f(h, 0)} · {f(a, 2)}% · hafta {nw}" + (f" (%{hw:.0f})" if nw else "") + (f" · test %{ts[0]:.0f}" if ts else "") + f" → {nt}")
        if ISR_SAT: tl += ["", "İŞARETLİ ANA SİNYALLER:"] + [f"• {mk}: {n} kapandı · %{f(h, 0)} · {f(a, 2)}%" + (f" · açık {o}" if o else "") + f" · test %{ts[1]:.0f}" for mk, n, h, a, o, ts in ISR_SAT]
        tl += ["", f"Karar günü {KARAR_T:%d.%m}: ana türünde ≥ 20 kapanan sinyal ve canlı isabet testin belirgin altında + zarar → çıkarma önerisi (sana sorulur)."]
        if len(Kp[Kp.sinif == "ana"]) < 40: tl.append("Az sinyal varken tek hafta sonucu yanıltıcıdır.")
        if yerel >= KARAR_T and ana_karar: tl.append("❌ ÖNERİ — ana'dan çıkarılması önerilen: " + ", ".join(t for t, *_ in ana_karar))
        tl.append("(Eski model raporları artık Telegram'a gitmiyor; panelde: durum/haftalik_rapor.md)")
        tg_send("\n".join(tl))
        if os.environ.get("KARNE_ZORLA") != "1": D.update(ilk=True, hafta=hafta); json.dump(D, open(DUR_F, "w", encoding="utf-8"))
if __name__ == "__main__": main()
