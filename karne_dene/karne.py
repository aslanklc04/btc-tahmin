# karne.py — CANLI KARNE (15.10.2026, kullanıcı isteği): gönderilen / gönderilmeyen her sinyalin GERÇEK sonucu ve testle karşılaştırma.
# Kayıt: durum/karne_kayit.csv (gonder.py her saat yazar; 12–15.10 geçmişi git kayıtlarından). Sonuç: durum/karne.md + son_durum.md özeti.
# Ölçüm testlerle aynı: giriş = sinyal saatinin kapanışı (Binance spot 1 s), çıkış = giriş + süre kapanışı, maliyet %0,04. Süresi dolmayan = açık (hesaba girmez).
# Telegram: ilk karne bir kez + her PAZARTESİ TR 09:00 sonrası haftalık karne (bilgi mesajı).
# ÖNCEDEN YAZILI KARAR (15.10.2026, sonuçlar görülmeden): 12.11.2026'dan itibaren ✅ ana olarak gönderilmiş bir türde ≥ 20 kapanan sinyal varsa
#   canlı isabet testteki isabetin belirgin altında (tek yönlü binom p < 0,05) VE canlı işlem başı net < 0 → "❌ ana'dan çıkarma önerisi" (kullanıcıya sorulur).
import os, re, json, math, numpy as np, pandas as pd
from ortak import fetch_1h, tg_send, DISPLAY_TZ, TUT_TEST
KAYIT_F, MD_F, DUR_F = "durum/karne_kayit.csv", "durum/karne.md", "durum/karne_durum.json"
KOM, KARAR_T = 0.04, pd.Timestamp("2026-11-12", tz=DISPLAY_TZ)
GEN = {l.strip()[:-4] for l in open("durum/genis_liste.txt") if l.strip()} if os.path.exists("durum/genis_liste.txt") else set()
PA = pd.read_csv("durum/prim_acik.csv") if os.path.exists("durum/prim_acik.csv") else pd.DataFrame(columns=["coin", "esik", "saat"])
TEST = {k: (v[0][0], v[0][2]) for k, v in TUT_TEST.items()} | {"🔇/🪙": (56.9, 53.7)}       # (isabet tüm test, 2026) — tutma3.py · kombin.py Y3
SINIF_TEST = {"ana": (61.9, 67.1), "yedek": (55.5, 53.3)}                                   # fon_ana.py 14.10 ana seti · kombin.py Y1–Y3 ağırlıklı
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
        for nm, H, yon, tur, isr in coz(r.e, su):
            rows.append(dict(t0=t0, sinif=sinif(r.s, r.k), terfi="🔥" in r.s, coin=nm, H=H, yon=yon, tur=tur, isr=isr,
                             fz=float(r.fz) if r.fz else np.nan, prim_ret="⛔" in r.e))
    X = pd.DataFrame(rows)
    if X.empty: print("karne: çözülen sinyal yok"); return
    X = X.drop_duplicates(["t0", "coin", "H", "yon", "tur"]).reset_index(drop=True)          # aynı saatte aynı sinyal iki kez (yeniden çalışma) → tek
    now = pd.Timestamp.now(tz="UTC"); bas = X.t0.min() - pd.Timedelta(hours=2); P = {}
    for nm in X.coin.unique():
        try: P[nm] = fetch_1h(bas.value // 10**6, now.value // 10**6, sym=nm + "USDT").close
        except Exception as e: print("karne fiyat yok:", nm, e)
    net, kap = [], []
    for r in X.itertuples():
        c = P.get(r.coin); t1 = r.t0 + pd.Timedelta(hours=int(r.H))
        if c is None or r.t0 not in c.index: net.append(np.nan); kap.append(False); continue
        k_ = t1 in c.index; p1 = c[t1] if k_ else c.iloc[-1]
        net.append(r.yon * 100 * (p1 / c[r.t0] - 1) - KOM); kap.append(k_)
    X["net"], X["kap"] = net, kap
    X = X[np.isfinite(X.net)]; Kp = X[X.kap]
    yerel = now.tz_convert(DISPLAY_TZ)
    def ozet(m):
        k = Kp[m]; a = X[m & ~X.kap]
        return len(k), (100 * (k.net > 0).mean() if len(k) else np.nan), (k.net.mean() if len(k) else np.nan), k.net.sum(), len(a)
    f = lambda v, d=1: "—" if not np.isfinite(v) else f"{v:.{d}f}"
    L = [f"# 📒 Canlı karne — {yerel:%d.%m.%Y %H:%M}",
         f"_Kayıt: {X.t0.min().tz_convert(DISPLAY_TZ):%d.%m %H:%M} → bugün · ölçüm testlerle aynı (sinyal saati kapanışı → süre sonu kapanışı, maliyet %0,04) · açık = süresi dolmamış, hesaba girmez_\n",
         "| Sınıf | Kapanan | İsabet | İşlem başı net | Toplam | Açık | Testte isabet (tüm · 2026) |", "|---|---|---|---|---|---|---|"]
    for sn, ad in (("ana", "✅ ana (gönderildi)"), ("yedek", "🔸 yedek (gönderildi)"), ("panel", "panel (gönderilmedi)")):
        n, h, a, s, o = ozet(X.sinif == sn); ts = SINIF_TEST.get(sn)
        L.append(f"| {ad} | {n} | %{f(h, 0)} | {f(a, 2)}% | {f(s, 1)}% | {o} | {'%' + f(ts[0], 0) + ' · %' + f(ts[1], 0) if ts else '—'} |")
    n, h, a, s, o = ozet((X.sinif == "panel") & X.prim_ret); L.append(f"| ↳ panel · prim ⛔ (filtre) | {n} | %{f(h, 0)} | {f(a, 2)}% | {f(s, 1)}% | {o} | — |")
    L += ["", "## Tür bazında (gönderilen ✅ ana + 🔸 yedek)", "| Tür | Sınıf | Kapanan | İsabet | İşlem başı net | Testte isabet (tüm · 2026) | Durum |", "|---|---|---|---|---|---|---|"]
    karar = []
    for (tur, sn), g in X[X.sinif != "panel"].groupby(["tur", "sinif"]):
        k = g[g.kap]; n = len(k); h = 100 * (k.net > 0).mean() if n else np.nan; ts = TEST.get(tur)
        if n < 20: dur = f"⏳ veri az ({n}/20)"
        elif ts is None: dur = "— test yok"
        else:
            p = binom_alt(int((k.net > 0).sum()), n, ts[0] / 100)
            if p < 0.05 and k.net.mean() < 0: dur = f"❌ testin belirgin altında (p {p:.3f})"; karar.append((tur, sn, n, h, k.net.mean(), ts[0]))
            elif h >= ts[0] - 5: dur = "✅ testle uyumlu"
            else: dur = f"⚠️ testin altında, belirgin değil (p {p:.2f})"
        L.append(f"| {tur} | {sn} | {n} | %{f(h, 0)} | {f(k.net.mean() if n else np.nan, 2)}% | {'%' + f(ts[0], 0) + ' · %' + f(ts[1], 0) if ts else '—'} | {dur} |")
    L += ["", f"**Önceden yazılı karar (15.10.2026):** {KARAR_T:%d.%m.%Y}'den itibaren ✅ ana türünde ≥ 20 kapanan sinyal varken canlı isabet testin belirgin altında (binom p < 0,05) VE işlem başı net < 0 ise → ana'dan çıkarma önerisi (kullanıcıya sorulur)."]
    ana_karar = [x for x in karar if x[1] == "ana"]
    if yerel >= KARAR_T and ana_karar: L.append("- ❌ **ÖNERİ:** " + " · ".join(f"{t} ({n} sinyal, %{h:.0f} vs test %{ts:.0f}, net {a:+.2f}%)" for t, _, n, h, a, ts in ana_karar))
    L += ["", "## Son 25 kapanan (gönderilen)", "| Saat | Sınıf | Tür | Coin | Süre | Net | |", "|---|---|---|---|---|---|---|"]
    for r in Kp[Kp.sinif != "panel"].sort_values("t0").tail(25).itertuples():
        L.append(f"| {r.t0.tz_convert(DISPLAY_TZ):%d.%m %H:%M} | {r.sinif}{' 🔥' if r.terfi else ''} | {r.tur}{(' ' + r.isr) if r.isr else ''} | {r.coin} | {r.H} s | {r.net:+.2f}% | {'✅' if r.net > 0 else '❌'} |")
    open(MD_F, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("\n".join(L[:12]))
    if os.path.exists("son_durum.md"):
        open("son_durum.md", "a", encoding="utf-8").write("\n\n## 📒 Canlı karne (ayrıntı: durum/karne.md)\n" + "\n".join(L[2:9]) + "\n")
    try: D = json.load(open(DUR_F, encoding="utf-8"))
    except Exception: D = {}
    hafta = f"{yerel:%G-%V}"
    if not D.get("ilk") or (yerel.weekday() == 0 and yerel.hour >= 9 and D.get("hafta") != hafta):
        def sat(sn, ad):
            n, h, a, s, o = ozet(X.sinif == sn); ts = SINIF_TEST.get(sn)
            return f"{ad}: {n} kapandı · isabet %{f(h, 0)} · işlem başı {f(a, 2)}% · toplam {f(s, 1)}%" + (f" (testte %{ts[0]:.0f} · 2026 %{ts[1]:.0f})" if ts else "") + (f" · {o} açık" if o else "")
        n_, h_, a_, s_, o_ = ozet((X.sinif == "panel") & X.prim_ret)
        tl = [f"📒 CANLI KARNE — {yerel:%d.%m.%Y} (kayıt {X.t0.min().tz_convert(DISPLAY_TZ):%d.%m}'den beri)", "Ölçüm testlerle aynı: sinyal saati kapanışı → süre sonu kapanışı, maliyet %0,04.",
              sat("ana", "✅ Ana"), sat("yedek", "🔸 Yedek"), sat("panel", "Panel (gönderilmedi)"),
              f"↳ ⛔ prim filtresinin engelledikleri: {n_} kapandı · isabet %{f(h_, 0)} · toplam {f(s_, 1)}%"]
        tt = [f"{tur} {sn}: {len(g[g.kap])} · %{f(100 * (g[g.kap].net > 0).mean() if g.kap.any() else np.nan, 0)} · {f(g[g.kap].net.mean() if g.kap.any() else np.nan, 2)}%"
              for (tur, sn), g in X[X.sinif != "panel"].groupby(["tur", "sinif"])]
        if tt: tl.append("Tür bazında (kapanan · isabet · işlem başı): " + " | ".join(tt))
        tl.append(f"Karar günü {KARAR_T:%d.%m}: ana türünde ≥ 20 kapanan sinyal ve canlı isabet testin belirgin altında + zarar → çıkarma önerisi." + (" Az sinyal varken tek gün/hafta sonucu yanıltıcıdır." if len(Kp[Kp.sinif == "ana"]) < 40 else ""))
        if yerel >= KARAR_T and ana_karar: tl.append("❌ ÖNERİ — ana'dan çıkarılması önerilen: " + ", ".join(t for t, *_ in ana_karar))
        tg_send("\n".join(tl))
        D.update(ilk=True, hafta=hafta if yerel.weekday() == 0 and yerel.hour >= 9 else D.get("hafta")); json.dump(D, open(DUR_F, "w", encoding="utf-8"))
if __name__ == "__main__": main()
