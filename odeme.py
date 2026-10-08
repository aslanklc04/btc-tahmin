# odeme.py — BTC "PARA OLARAK" KULLANILINCA NE OLUYOR? Ödeme kabulü / yasal para haberleri etrafında BTC fiyatı (olay çalışması; yalnız bilgi).
# Fiyat: Yahoo BTC-USD günlük kapanış (UTC). Pencereler: önce (E−8 → E−1) · tepki (E−1 → E+1) · sonra 7 gün (E+1 → E+8) · sonra 30 gün (E+1 → E+31).
# Karşılaştırma: olayın ±1 yılındaki aynı uzunluktaki tüm pencereler → olayın getirisi bunların yüzde kaçından iyi (yüzdelik) ve medyanın ne kadar üstünde (fazla).
# Tarihler kaynaklardan (haberin çıktığı gün, UTC): Microsoft 11.12.2014 · PayPal kripto 21.10.2020 · Tesla 10-K 08.02.2021 · Mastercard 10.02.2021 · Tesla kabul 24.03.2021 ·
#   PayPal Checkout with Crypto 30.03.2021 · Tesla askıya aldı 12.05.2021 (ABD akşamı) · El Salvador duyuru 06.06.2021 · yasa 09.06.2021 · yürürlük 07.09.2021 · Twitter Lightning bahşiş 23.09.2021 ·
#   Strike–Shopify/NCR 07.04.2022 · Orta Afrika Cumh. yasal para 27.04.2022 · Steak 'n Shake duyuru 09.05.2025 · başlangıç 16.05.2025 · Square ilk satıcılar 22.07.2025 · Square geniş açılış 10.11.2025 ·
#   El Salvador yasal para statüsünü kaldırdı 29.01.2025.
import numpy as np, pandas as pd, yfinance as yf
L = []
def yaz(s=""): print(s, flush=True); L.append(s)
h = yf.Ticker("BTC-USD").history(start="2014-09-01", auto_adjust=True)["Close"]; P = pd.Series(h.values, index=pd.DatetimeIndex([d.date() for d in h.index]))
OL = [("2014-12-11", "Microsoft BTC ile ödeme kabul", 1), ("2020-10-21", "PayPal kripto al-sat + ödeme planı", 1), ("2021-02-08", "Tesla 1,5 milyar $ BTC + ödeme kabul edecek", 1),
      ("2021-02-10", "Mastercard kripto desteği duyurusu", 1), ("2021-03-24", "Tesla BTC ile araç satışı başladı", 1), ("2021-03-30", "PayPal Checkout with Crypto", 1),
      ("2021-05-12", "Tesla BTC ödemesini askıya aldı (ABD akşamı)", -1), ("2021-06-06", "El Salvador: BTC yasal para olacak (duyuru)", 1), ("2021-06-09", "El Salvador BTC yasası kabul", 1),
      ("2021-09-07", "El Salvador BTC yasası yürürlükte", 1), ("2021-09-23", "Twitter Lightning ile BTC bahşiş", 1), ("2022-04-07", "Strike: Shopify, NCR ile BTC ödeme", 1),
      ("2022-04-27", "Orta Afrika Cumh. BTC yasal para", 1), ("2025-01-29", "El Salvador BTC yasal para statüsünü kaldırdı", -1), ("2025-05-09", "Steak 'n Shake BTC kabul edecek (duyuru)", 1),
      ("2025-05-16", "Steak 'n Shake BTC kabulü başladı", 1), ("2025-07-22", "Square ilk satıcılarda BTC ödeme", 1), ("2025-11-10", "Square BTC ödeme geniş açılış", 1)]
W = {"önce 7 g": (-8, -1), "tepki 2 g": (-1, 1), "sonra 7 g": (1, 8), "sonra 30 g": (1, 31)}
def ret(t0, t1):
    a, b = P.asof(t0), P.asof(t1); return b / a - 1 if np.isfinite(a) and np.isfinite(b) else np.nan
rows = []
for d, ad, yon in OL:
    E = pd.Timestamp(d); r = dict(tarih=d, olay=ad, tür="olumlu" if yon > 0 else "OLUMSUZ")
    for wn, (a, b) in W.items():
        x = ret(E + pd.Timedelta(days=a), E + pd.Timedelta(days=b)); n = b - a
        idx = P.index[(P.index >= E - pd.Timedelta(days=365)) & (P.index <= E + pd.Timedelta(days=365))]
        base = np.array([ret(t, t + pd.Timedelta(days=n)) for t in idx if abs((t - (E + pd.Timedelta(days=a))).days) > 3]); base = base[np.isfinite(base)]
        r[wn] = f"{100*x:+.1f}% (y{100*(base < x).mean():.0f})" if np.isfinite(x) else "—"
        r[f"_f_{wn}"] = 100 * (x - np.median(base)) if np.isfinite(x) and len(base) else np.nan; r[f"_p_{wn}"] = 100 * (base < x).mean() if len(base) else np.nan
    rows.append(r)
R = pd.DataFrame(rows)
yaz("# 💳 BTC para olarak kullanılınca: ödeme kabulü haberleri ve fiyat\n_hücre: BTC getirisi (y = o yılın aynı uzunluktaki pencerelerinin yüzde kaçından iyi; 50 = sıradan)_\n```\n"
    + R[["tarih", "olay", "tür"] + list(W)].to_string(index=False) + "\n```")
for tur in ("olumlu", "OLUMSUZ"):
    G = R[R.tür == tur]
    yaz(f"\n**{tur} haberler ({len(G)}):** " + " · ".join(f"{wn}: ort. fazla {G[f'_f_{wn}'].mean():+.1f} puan, ort. yüzdelik {G[f'_p_{wn}'].mean():.0f}, sıradan üstü {int((G[f'_p_{wn}'] > 50).sum())}/{G[f'_p_{wn}'].notna().sum()}" for wn in W))
open("odeme_sonuc.md", "w").write("\n".join(L) + "\n")
