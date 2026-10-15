# degerlendir_hepsi.py — canlı günlükteki TÜM sinyallerin (✅ ana · 🔸 yedek · panel) gerçek sonucu (yalnız bilgi, 15.10.2026).
# Giriş = sinyal saatinin kapanış fiyatı (Binance spot 1 s), çıkış = giriş + tahmin süresi kapanışı; süre dolmadıysa son kapanış (AÇIK). Maliyet %0,04.
# Yön: ↑ al · "↓" / "KISA" sat. Saatler TR (UTC+3).
import numpy as np, pandas as pd
from ortak import fetch_1h
S = [  # (saat TR, sınıf, coin, süre, yön, açıklama)
    ("14.10 10", "ana", "CRV", 8, 1, "💵 z +3.2"), ("14.10 11", "ana", "MAGIC", 24, 1, "🧪🌐 z +1.9"),
    ("14.10 14", "panel", "BTC", 8, -1, "₿ 8s Güçlü ↓ (bilgi)"),
    ("14.10 16", "panel", "ETH", 4, 1, "🪙 A · ⛔ z -1.5"), ("14.10 16", "panel", "ETH", 24, 1, "🧪 · ⛔ z -1.5"),
    ("14.10 17", "ana", "SHIB", 24, 1, "🧪 z +0.4"), ("14.10 17", "ana", "FIL", 8, 1, "💵 z +5.0"),
    ("14.10 17", "panel", "BTC", 1, 1, "₿ 1s Çok güçlü ↑ · z +0.3"), ("14.10 17", "panel", "ETH", 4, 1, "🔇 4s ÇG · ⛔ z -1.2"),
    ("14.10 18", "panel", "BTC", 4, 1, "₿ A · ⛔ z -2.8"), ("14.10 18", "panel", "BTC", 24, -1, "🔻 KISA · z -2.8"),
    ("14.10 19", "ana", "RPL", 24, 1, "🧪🌐 z +2.2"), ("14.10 19", "yedek", "BNB", 4, 1, "🪙 4s ÇG · z +0.4"),
    ("14.10 19", "panel", "BTC", 4, 1, "₿ 1s ÇG + 4s G ⏰ · ⛔ z -1.9"),
    ("14.10 21", "panel", "BTC", 1, 1, "₿ 1s ÇG · ⛔ z -2.0"), ("14.10 21", "panel", "ETH", 4, 1, "🪙 4s ÇG · ⛔ z -2.0"),
    ("15.10 00", "panel", "BTC", 4, 1, "₿ A · ⚠️ z -0.7"), ("15.10 00", "panel", "BNB", 4, 1, "🪙 A · ⛔ z -1.6"),
    ("15.10 00", "panel", "DOGE", 8, 1, "🪙 ⭐ · ⛔ z -1.3"), ("15.10 01", "panel", "ETH", 4, 1, "🪙 A · ⛔ z -2.2"),
    ("15.10 02", "panel", "BTC", 8, 1, "₿ 8s G · ⛔ z -2.0"), ("15.10 03", "panel", "DOGE", 24, 1, "🧪 · ⛔ z -1.6"),
    ("15.10 04", "panel", "BTC", 4, 1, "₿ A · ⛔ z -1.9"), ("15.10 05", "panel", "BTC", 1, 1, "₿ 1s G · ⛔ z -1.9"),
    ("15.10 05", "panel", "ETH", 4, 1, "🪙 4s ÇG · ⛔ z -2.0"),
    ("15.10 06", "yedek", "FIL", 8, 1, "💵 z +13.6"), ("15.10 06", "yedek", "DOT", 8, 1, "🔇 ⭐ · z +0.4"),
    ("15.10 06", "panel", "ADA", 8, 1, "🔇 ⭐ · ⛔ z -1.6"), ("15.10 06", "panel", "BNB", 4, 1, "🪙 4s ÇG · ⛔ z -2.6"),
    ("15.10 06", "panel", "SHIB", 8, 1, "🔇 ⭐ · ⛔ z -1.0"), ("15.10 06", "panel", "ADA", 24, 1, "🧪 · ⛔ z -1.6"),
    ("15.10 07", "panel", "BTC", 4, 1, "₿ 1s G + 4s G · ⛔ z -2.4"), ("15.10 07", "panel", "NEAR", 24, 1, "🧪 · ⛔ z -1.1"),
    ("15.10 09", "panel", "BTC", 4, 1, "₿ A · ⛔ z -2.0"), ("15.10 09", "panel", "DOGE", 8, 1, "🪙 ⭐ · ⚠️ z -0.8"),
    ("15.10 09", "panel", "BNB", 24, 1, "🧪 · ⛔ z -1.3"),
    ("15.10 10", "panel", "BTC", 1, 1, "₿ 1s G · ⛔ z -2.1"), ("15.10 10", "panel", "BNB", 4, 1, "🪙 4s ÇG · ⛔ z -1.1"),
    ("15.10 12", "yedek", "INJ", 24, 1, "💵 z +3.2"),
]
now = pd.Timestamp.now(tz="UTC"); bas = pd.Timestamp("2026-10-13 00:00", tz="UTC"); P = {}
def fiyat(nm):
    if nm not in P: P[nm] = fetch_1h(bas.value // 10**6, now.value // 10**6, sym=nm + "USDT").close
    return P[nm]
out = []
for saat, sn, nm, H, yon, ac in S:
    t0 = pd.Timestamp(f"2026-{saat[3:5]}-{saat[:2]} {saat[6:]}:00", tz="Europe/Istanbul").tz_convert("UTC"); t1 = t0 + pd.Timedelta(hours=H)
    c = fiyat(nm); b = fiyat("BTC")
    if t0 not in c.index: continue
    kap = t1 in c.index; p0 = c[t0]; p1 = c[t1] if kap else c.iloc[-1]; w = c[(c.index > t0) & (c.index <= t1)]
    net = yon * 100 * (p1 / p0 - 1) - 0.04; bt = 100 * ((b[t1] if kap else b.iloc[-1]) / b[t0] - 1)
    out.append(dict(saat=saat, sinif=sn, coin=nm, sure=H, yon="↑" if yon > 0 else "↓", tur=ac, durum="KAPANDI" if kap else "AÇIK",
                    net=round(net, 2), tuttu="✅" if net > 0 else "❌", en_iyi=round(yon * 100 * ((w.max() if yon > 0 else w.min()) / p0 - 1), 2) if len(w) else np.nan,
                    en_kotu=round(yon * 100 * ((w.min() if yon > 0 else w.max()) / p0 - 1), 2) if len(w) else np.nan, btc=round(bt, 2)))
X = pd.DataFrame(out); pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)
L = [f"{now.tz_convert('Europe/Istanbul'):%d.%m %H:%M} TR · giriş = sinyal saati kapanışı, çıkış = süre sonu kapanışı (AÇIK = şimdiki fiyat) · maliyet %0,04", X.to_string(index=False), ""]
def oz(m, ad):
    k = X[m & (X.durum == "KAPANDI")]; a = X[m & (X.durum == "AÇIK")]
    return f"{ad:38s} kapanan {len(k):2d}: {int((k.net > 0).sum())} tuttu (%{100 * (k.net > 0).mean() if len(k) else float('nan'):.0f}) · ort net {k.net.mean() if len(k) else float('nan'):+.2f}% · toplam {k.net.sum():+.2f}%  | açık {len(a)} (şu an ort {a.net.mean() if len(a) else float('nan'):+.2f}%)"
pz = X.tur.str.contains("⛔")
for m, ad in ((X.sinif == "ana", "✅ ana (gönderildi)"), (X.sinif == "yedek", "🔸 yedek (gönderildi)"), (X.sinif == "panel", "panel (gönderilmedi) hepsi"),
              ((X.sinif == "panel") & pz, "  panel · prim ⛔ (z ≤ −1)"), ((X.sinif == "panel") & ~pz, "  panel · ⛔ değil"),
              ((X.sinif == "panel") & pz & (X.coin == "BTC"), "  panel · BTC ⛔"), ((X.sinif == "panel") & pz & (X.coin != "BTC"), "  panel · coin ⛔")):
    L.append(oz(m, ad))
open("degerlendir_hepsi.txt", "w").write("\n".join(L) + "\n"); print("\n".join(L))
