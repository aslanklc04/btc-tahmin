# genis_analiz.py — GENİŞ COİN TARAMASI (~200 coin): hangi coin'ler canlıdaki ✅ İŞLEM SİNYALİ setine (R5) eklenmeli? (yalnız test)
# Sinyaller (canlıdaki R5 ile aynı aileler, coin başına saat başına tek işlem):
#   🤝 coin'de ⭐/4s ÇG↑/A varken BTC 4s Çok güçlü ↑ · 🔇 coin'de ⭐/4s ÇG↑/A varken BTC'de ⭐/4s/A yok (ikisi 4 saat tut) · 🧪 24 saat Çok güçlü ↑ (24 saat tut)
#   Yalnız coin'in KENDİ Coinbase primi z ≥ 0 iken. Net = getiri − %0,04. Canlıdaki aylık coin içi açma/kapama (öz-denetim) burada UYGULANMAZ (o da tüm dönemi gördüğü için).
# ÖNCEDEN YAZILI SEÇİM (sonuçları görmeden, 11.10.2026):
#   Kohort A: 2022-06 → 2023 arasında ≥ 15 sinyali olan coin'ler — seçim bu dönemde, doğrulama 2024+.
#   Kohort B: kalanlardan 2024'te ≥ 15 sinyali olanlar — seçim 2024, doğrulama 2025+.
#   Seçim koşulu (coin başına, seçim döneminde): ≥ 15 sinyal · isabet ≥ %55 · işlem başı net ≥ +%0,20.
#   KARAR: seçilen YENİ coin'ler (canlıda olmayanlar) birlikte, kendi doğrulama dönemlerinde: ≥ 100 sinyal · isabet ≥ %55 · net > 0 · haftalık blok %5 alt sınır > 0 · 2026'da net ≥ 0
#   → geçerse seçilen yeni coin'ler canlıya aday (coin modeli + 24 saat listesi). Karşılaştırma: seçilmeyenler ve canlıdaki coin'ler.
import glob, os, numpy as np, pandas as pd
from ortak import events, wboot, DISPLAY_TZ
L = []
def yaz(s=""): print(s, flush=True); L.append(s)
def bul(p):
    x = glob.glob(p, recursive=True); return x[0] if x else None
SY = sorted({os.path.basename(p)[5:-4] for p in glob.glob("ga/**/disa_*USDT.pkl", recursive=True)})
CANLI = set()
for f in ("canli/durum/coin_listesi.txt", "canli/durum/deneme24_liste.txt"):
    if os.path.exists(f): CANLI |= {l.strip().replace("USDT", "") for l in open(f) if l.strip()}
EVR = pd.read_csv(bul("**/genis_evren.csv") or "genis_evren.csv") if (bul("**/genis_evren.csv") or os.path.exists("genis_evren.csv")) else None
B = pd.read_pickle(bul("ga/**/disa_BTCUSDT.pkl")); B.index = pd.DatetimeIndex(B.index).tz_convert("UTC")
KOM = 0.0004; P0, A24, A25, A26 = (pd.Timestamp(x, tz="UTC") for x in ("2022-06-01", "2024-01-01", "2025-01-01", "2026-01-01"))
EV, yok = [], []
for sym in SY:
    nm = sym[:-4]
    pz, d24 = bul(f"ga/**/prim_{sym}.pkl"), bul(f"ga/**/disa24_{sym}.pkl")
    if pz is None: yok.append(f"{nm} (prim yok)"); continue
    Z = pd.read_pickle(pz).astype("float64"); Z.index = pd.DatetimeIndex(Z.index).tz_convert("UTC")
    X = pd.read_pickle(bul(f"ga/**/disa_{sym}.pkl")); X.index = pd.DatetimeIndex(X.index).tz_convert("UTC")
    if nm != "BTC":
        Bx = B.reindex(X.index); bu4 = Bx.u4.fillna(False).astype(bool).values; bany = (Bx.star.fillna(False).astype(bool) | Bx.u4.fillna(False).astype(bool) | Bx.acls.fillna(False).astype(bool)).values
        any_ = (X.star.fillna(False).astype(bool) | X.u4.fillna(False).astype(bool) | X.acls.fillna(False).astype(bool)).values & X.y4.notna().values
        for aile, kos in (("🤝", bu4), ("🔇", ~bany)):
            ev = events(any_ & kos, 4); t = X.index[ev]
            EV.append(pd.DataFrame({"nm": nm, "aile": aile, "t": t, "r": np.exp(X.y4.values[ev]) - 1, "z": Z.z.reindex(t).values}))
    if d24:
        D = pd.read_pickle(d24).astype("float64"); D.index = pd.DatetimeIndex(D.index).tz_convert("UTC")
        D = D.reindex(pd.date_range(D.index[0], D.index[-1], freq="1h", tz="UTC")); c = D.close.ffill(limit=3).values; n = len(D)
        m = np.nan_to_num(((D.S24 > 0) & (D.C24 >= D.T10_24)).values).astype(bool) & D.T10_24.notna().values & (np.arange(n) + 25 < n)
        ev = events(m, 24); t = D.index[ev]
        EV.append(pd.DataFrame({"nm": nm, "aile": "🧪", "t": t, "r": c[ev + 24] / c[ev] - 1, "z": Z.z.reindex(t).values}))
E = pd.concat(EV, ignore_index=True); E = E[np.isfinite(E.r) & np.isfinite(E.z) & (E.z >= 0)].copy(); E["net"] = E.r - KOM; E["ok"] = E.net > 0
SONT = E.t.max(); HF = lambda a, b: max((min(b, SONT) - a).days / 7, 1)
yaz(f"# 🌐 Geniş coin taraması — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nEğitilen coin: {len(SY)} · prim verisi olmayan: {', '.join(yok) or '—'} · ✅ sinyal (kendi primi ≥ 0): {len(E):,}\n"
    + (f"_Evren: Coinbase USD ∩ Binance USDT, 2024-10 öncesi listelenmiş, Binance hacmine göre ilk {len(SY)-1}_\n" if EVR is not None else ""))
def st(x):
    if len(x) == 0: return dict(n=0, isabet=np.nan, net=np.nan, alt=np.nan)
    return dict(n=len(x), isabet=100 * x.ok.mean(), net=100 * x.net.mean(), alt=100 * wboot(x.net.values, x.t.values, 400)[0] if len(x) >= 8 else np.nan)
R = []
for nm, g in E.groupby("nm"):
    if nm == "BTC": continue
    a = g[(g.t >= P0) & (g.t < A24)]
    if len(a) >= 15: koh, sec, dog = "A", a, g[g.t >= A24]
    else:
        b = g[(g.t >= A24) & (g.t < A25)]
        if len(b) < 15: R.append(dict(nm=nm, kohort="—", secildi=False, canli=nm in CANLI)); continue
        koh, sec, dog = "B", b, g[g.t >= A25]
    s, d, d26 = st(sec), st(dog), st(g[g.t >= A26])
    ok = s["n"] >= 15 and s["isabet"] >= 55 and s["net"] >= 0.20
    R.append(dict(nm=nm, kohort=koh, secildi=ok, canli=nm in CANLI, s_n=s["n"], s_is=s["isabet"], s_net=s["net"], d_n=d["n"], d_is=d["isabet"], d_net=d["net"], d_alt=d["alt"],
                  y26_n=d26["n"], y26_is=d26["isabet"], y26_net=d26["net"], hf26=d26["n"] / HF(A26, SONT)))
R = pd.DataFrame(R); R.to_csv("genis_coin.csv", index=False)
def dogrulama(nms):                                                                        # her coin kendi kohortunun doğrulama döneminde
    parca = []
    for nm in nms:
        k = R.loc[R.nm == nm, "kohort"].iloc[0]; g = E[E.nm == nm]; parca.append(g[g.t >= (A24 if k == "A" else A25)])
    return pd.concat(parca) if parca else E.iloc[:0]
def satir(ad, x, x26):
    s, s26 = st(x), st(x26)
    return f"{ad:38s} coin {x.nm.nunique():3d} · sinyal {s['n']:5d} · isabet %{s['isabet']:.1f} · net {s['net']:+.3f} (alt {s['alt']:+.2f}) | 2026: {s26['n']} · %{s26['isabet']:.1f} · {s26['net']:+.3f} · haftada {s26['n']/HF(A26, SONT):.1f}"
K = R[R.kohort != "—"]
SEC_AD = "✅ seçilen YENİ coin'ler"
gruplar = {SEC_AD: K[K.secildi & ~K.canli].nm, "seçilmeyen yeni coin'ler": K[~K.secildi & ~K.canli].nm,
           "canlıdaki coin'ler (karşılaştırma)": K[K.canli].nm, "  ↳ canlıdakilerden seçimi geçenler": K[K.secildi & K.canli].nm}
yaz("## 1) Gruplar — doğrulama döneminde (kohort A: 2024+, B: 2025+) · ayrıca 2026\n```")
for ad, nms in gruplar.items():
    x = dogrulama(list(nms)); yaz(satir(ad, x, x[x.t >= A26]))
yaz("```")
yeni = dogrulama(list(gruplar[SEC_AD])); s, s26 = st(yeni), st(yeni[yeni.t >= A26])
GECTI = bool(s["n"] >= 100 and s["isabet"] >= 55 and s["net"] > 0 and s["alt"] > 0 and (s26["n"] == 0 or s26["net"] >= 0))
yaz(f"\n**Önceden yazılı karar:** seçilen yeni coin'ler ({len(gruplar[SEC_AD])}: {', '.join(gruplar[SEC_AD]) or '—'}) doğrulamada: {s['n']} sinyal · isabet %{s['isabet']:.1f} · net {s['net']:+.3f} · alt {s['alt']:+.2f} · 2026 net {s26['net']:+.3f} → "
    + ("✅ CANLIYA ADAY" if GECTI else "❌ geçmedi"))
yaz("\n## 2) Seçilen yeni coin'lerde aile bazında (doğrulama)\n```")
for a, g in yeni.groupby("aile"): yaz(satir(f"{a}", g, g[g.t >= A26]))
yaz("```")
yaz("\n## 3) Coin tablosu (seçim dönemi netine göre) — _s: seçim · d: doğrulama · 26: 2026_\n```")
T = K.sort_values("s_net", ascending=False).copy()
for c in ("s_is", "s_net", "d_is", "d_net", "d_alt", "y26_is", "y26_net", "hf26"): T[c] = T[c].round(2)
T["durum"] = np.where(T.canli, "canlı", "") + np.where(T.secildi, " ✅", "")
yaz(T[["nm", "kohort", "durum", "s_n", "s_is", "s_net", "d_n", "d_is", "d_net", "d_alt", "y26_n", "y26_is", "y26_net", "hf26"]].to_string(index=False))
yaz("```")
yaz(f"\nKohortu olmayan (yeterli sinyal yok): {', '.join(R[R.kohort == '—'].nm) or '—'}")
open("genis_sonuc.md", "w").write("\n".join(L) + "\n")
