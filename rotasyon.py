# rotasyon.py — PARA NE ZAMAN KRİPTOYA, NE ZAMAN HİSSEYE, NE ZAMAN DEVLET TAHVİLİNE GEÇİYOR? (betimleyici; yalnız bilgi, canlıya dokunmaz)
# Veri (Yahoo): BTC, S&P 500 (SPY), Nasdaq 100 (QQQ), uzun vadeli ABD devlet tahvili (TLT), altın (GLD), dolar endeksi (DXY), ABD 10 yıllık faiz (^TNX), korku endeksi (^VIX).
# 1) Yıl yıl: BTC'nin hisse / tahvil / altınla aynı ay hareketi (korelasyon).
# 2) Ortam: aylık 10 yıllık faiz ↑/↓ × dolar ↑/↓ → o ay ve SONRAKİ ay ortalama getiri (hangi ortamda para nereye gidiyor).
# 3) Korku haftaları (VIX ≥ 30): o hafta ve sonraki 4 hafta.
import numpy as np, pandas as pd, yfinance as yf
L = []
def yaz(s=""): print(s, flush=True); L.append(s)
TK = {"BTC": "BTC-USD", "Hisse (S&P 500)": "SPY", "Teknoloji (Nasdaq)": "QQQ", "Devlet tahvili (TLT)": "TLT", "Altın": "GLD", "Dolar (DXY)": "DX-Y.NYB", "10y faiz": "^TNX", "VIX": "^VIX"}
D = {}
for ad, t in TK.items():
    h = yf.Ticker(t).history(start="2017-01-01", auto_adjust=True)["Close"]; D[ad] = pd.Series(h.values, index=pd.DatetimeIndex([x.date() for x in h.index]))
P = pd.DataFrame(D).sort_index(); P = P[P.index >= "2017-06-01"]
M = P.resample("ME").last(); R = M.pct_change(); R["10y faiz"] = M["10y faiz"].diff()          # faiz: puan değişimi
VAR = ["Hisse (S&P 500)", "Teknoloji (Nasdaq)", "Devlet tahvili (TLT)", "Altın", "Dolar (DXY)"]
yaz(f"# 🔄 Para nereye gidiyor: kripto · hisse · devlet tahvili — {pd.Timestamp.now():%d.%m.%Y}\nAylık veri {R.index[1]:%Y-%m} → {R.index[-1]:%Y-%m} ({len(R)-1} ay)\n")
K = {}
for y in range(2018, R.index[-1].year + 1):
    x = R[R.index.year == y]
    if len(x) >= 6: K[y] = {v: round(x["BTC"].corr(x[v]), 2) for v in VAR}
yaz("## 1) BTC ile aynı ay hareketi (korelasyon: +1 hep birlikte, 0 ilgisiz, −1 ters)\n```\n" + pd.DataFrame(K).T.to_string() + "\n```")
# 2) ortamlar
R["faiz"] = np.where(R["10y faiz"] > 0, "faiz ↑", "faiz ↓"); R["dolar"] = np.where(R["Dolar (DXY)"] > 0, "dolar ↑", "dolar ↓"); R["ortam"] = R.faiz + " · " + R.dolar
S = ["BTC", "Teknoloji (Nasdaq)", "Hisse (S&P 500)", "Devlet tahvili (TLT)", "Altın"]
def tablo(df, kaydir, baslik):
    X = df.copy()
    if kaydir: X[S] = X[S].shift(-1)
    T = X.dropna(subset=S).groupby("ortam").agg(**{"ay": ("BTC", "size")}, **{s: (s, lambda v: f"{100*v.mean():+.1f} (%{100*(v>0).mean():.0f})") for s in S})
    yaz(f"\n### {baslik}\n_ortalama aylık getiri % (yükselen ay oranı)_\n```\n" + T.to_string() + "\n```")
tablo(R, False, "2a) O ay: faiz ve dolar hareketine göre")
tablo(R, True, "2b) SONRAKİ ay (bu ayın faiz/dolar hareketi biliniyorken) — öncü mü?")
# 3) korku haftaları
W = P.resample("W-FRI").last(); WR = W.pct_change()
kh = W.index[(W["VIX"] >= 30) & (W["VIX"].shift(1) < 30)]
rows = []
for t in kh:
    i = W.index.get_loc(t); r = {"hafta": f"{t:%Y-%m-%d}", "VIX": round(W["VIX"].iloc[i], 0)}
    for s in ["BTC", "Teknoloji (Nasdaq)", "Devlet tahvili (TLT)", "Altın"]:
        r[f"{s.split(' (')[0]} o hafta"] = f"{100*WR[s].iloc[i]:+.1f}"; r[f"{s.split(' (')[0]} +4 hafta"] = f"{100*(W[s].iloc[min(i+4, len(W)-1)]/W[s].iloc[i]-1):+.1f}" if i + 4 < len(W) else "—"
    rows.append(r)
yaz("\n## 3) Korku haftaları (VIX 30'u aştığı ilk hafta): o hafta ve sonraki 4 hafta getirisi %\n```\n" + pd.DataFrame(rows).to_string(index=False) + "\n```")
yaz(f"\n_Son değerler: 10y faiz %{M['10y faiz'].iloc[-1]:.2f} (bu ay {R['10y faiz'].iloc[-1]:+.2f} puan) · dolar bu ay {100*R['Dolar (DXY)'].iloc[-1]:+.1f}% · VIX {P['VIX'].dropna().iloc[-1]:.0f}_")
open("rotasyon_sonuc.md", "w").write("\n".join(L) + "\n")
