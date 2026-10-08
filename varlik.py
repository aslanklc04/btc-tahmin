# varlik.py — ÖNCÜ VARLIK: hangi varlık YÜKSELMEYE BAŞLAYINCA BTC sonradan DÜŞÜYOR? (kripto dışı: dolar, faiz, korku endeksi, emtia, borsalar, tahvil, likidite)
# Günlük (Yahoo 2017+, FRED): varlığın 1 günlük ani yükselişi (z ≥ 2) ve 5 günlük yükselişe başlaması (z ≥ 1,5) → BTC sonraki 1 / 3 / 7 gün. Düşüşler de ayrıca.
#   Zamanlama: varlığın gün d kapanışı → BTC gün d+1 kapanışında işlem (temkinli, 1 gün gecikme; FRED verisi de ertesi gün yayımlanır). Ek: 'hemen' (BTC gün d kapanışı, ABD kapanışından ~3 saat sonra).
#   Önceden sabit karar: yön ≤2023'ten seçilir (BTC sonra düştüyse SAT, çıktıysa AL); 2024+'da net > 0 ve %90 alt sınır > 0 → ✅ (vadeli komisyon %0,05×2).
#   Şans payı: aynı test, sinyal günleri rastgele kaydırılarak (plasebo) 10 kez → "tesadüfen kaç tane geçerdi" sayısı.
# Saatlik (Yahoo 730 gün): vadeli/döviz 1 saatlik ani hareket (z ≥ 2,5) → BTC sonraki 1 / 4 / 24 saat (giriş 1 saat sonra). İlk yıl seçim, sonrası doğrulama.
import time, io, requests, numpy as np, pandas as pd
import yfinance as yf
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
# ad: (kaynak, sembol, dönüşüm)  dönüşüm: log = % değişim · fark = seviye farkı (faiz/spread) · ters = 1/x (yen güçlenmesi)
VG = {"DXY dolar endeksi": ("yf", "DX-Y.NYB", "log"), "ABD 10 yıl faizi": ("yf", "^TNX", "fark"), "VIX korku endeksi": ("yf", "^VIX", "log"), "MOVE tahvil oynaklığı": ("yf", "^MOVE", "log"),
      "Altın": ("yf", "GC=F", "log"), "Gümüş": ("yf", "SI=F", "log"), "Petrol": ("yf", "CL=F", "log"), "Bakır": ("yf", "HG=F", "log"), "Doğalgaz": ("yf", "NG=F", "log"),
      "Japon yeni güçleniyor": ("yf", "JPY=X", "ters"), "Euro/dolar": ("yf", "EURUSD=X", "log"), "Dolar/yuan": ("yf", "CNY=X", "log"),
      "Nasdaq": ("yf", "^IXIC", "log"), "S&P 500": ("yf", "^GSPC", "log"), "Nikkei 225": ("yf", "^N225", "log"), "Yüksek getirili tahvil (HYG)": ("yf", "HYG", "log"),
      "Uzun vadeli ABD tahvili (TLT)": ("yf", "TLT", "log"), "Coinbase hissesi": ("yf", "COIN", "log"), "MicroStrategy hissesi": ("yf", "MSTR", "log"),
      "Reel faiz (10 y)": ("fred", "DFII10", "fark"), "Kredi riski spreadi": ("fred", "BAMLH0A0HYM2", "fark"), "Faiz eğrisi 10y−2y": ("fred", "T10Y2Y", "fark"),
      "Fed net likidite": ("likidite", None, "fark")}
def yfd(t, **k):
    for i in range(3):
        try:
            h = yf.Ticker(t).history(auto_adjust=True, **k)
            if len(h): return h
        except Exception as e: print(t, e)
        time.sleep(2 + 3 * i)
    return None
def fred(sid):
    for i in range(3):
        try:
            r = requests.get("https://fred.stlouisfed.org/graph/fredgraph.csv", params=dict(id=sid), timeout=60)
            if r.status_code == 200:
                d = pd.read_csv(io.StringIO(r.text), na_values="."); d.index = pd.to_datetime(d.iloc[:, 0]).dt.tz_localize("UTC"); return d.iloc[:, 1].astype(float).dropna()
        except Exception as e: print(sid, e)
        time.sleep(3)
    return None
SER, YOK = {}, []
for ad, (kay, s, dn) in VG.items():
    if kay == "yf":
        h = yfd(s, period="max", interval="1d")
        x = None if h is None else pd.Series(h.Close.values, index=pd.DatetimeIndex(h.index.tz_localize(None).normalize()).tz_localize("UTC"))
    elif kay == "fred": x = fred(s)
    else:
        w, t, r = fred("WALCL"), fred("WTREGEN"), fred("RRPONTSYD")
        x = None if w is None or t is None or r is None else (w / 1e3).resample("D").last().ffill().sub(t.resample("D").last().ffill()).sub(r.resample("D").last().ffill(), fill_value=0).dropna()
        if x is not None: x = x[x.index.isin(w.index)]                                        # haftalık (çarşamba) nokta: yalnız yeni veri günleri
    if x is None or len(x) < 300: YOK.append(ad); continue
    x = x[~x.index.duplicated()].sort_index(); x = x[x > 0] if dn != "fark" else x
    SER[ad] = (1 / x if dn == "ters" else x, dn, kay)
    time.sleep(0.5)
def gunluk(sym):
    rows, cur = [], int(pd.Timestamp("2017-08-17", tz="UTC").timestamp() * 1000)
    while True:
        r = requests.get(EP[0], params=dict(symbol=sym, interval="1d", startTime=cur, limit=1000), timeout=20).json()
        if not r: break
        rows += r; cur = r[-1][0] + 86_400_000
        if len(r) < 1000: break
    d = pd.DataFrame([x[:5] for x in rows], columns=["t", "o", "h", "l", "c"]).astype(float); return pd.Series(d.c.values, index=pd.to_datetime(d.t, unit="ms", utc=True))
PX = gunluk("BTCUSDT"); lp = np.log(PX)
yaz(f"# 🔭 Öncü varlık: hangisi yükselince BTC sonra düşüyor? — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nVeri alınan: {len(SER)} varlık"
    + (f" · alınamayan: {', '.join(YOK)}" if YOK else "") + f" · BTC {PX.index[0]:%Y-%m} → {PX.index[-1]:%Y-%m-%d} · {time.time()-T0:.0f} sn\n")
A24, A26, FEE = pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC"), 0.0005
DON = (("≤2023", lambda i: i < A24), ("2024+", lambda i: i >= A24), ("2026", lambda i: i >= A26))
ix = PX.index
def yb(H, lag): return (lp.shift(-(lag + H)) - lp.shift(-lag))                               # BTC: gün d+lag kapanışında gir, H gün tut
Y = {(H, lag): yb(H, lag) for H in (1, 3, 7) for lag in (0, 1)}
btc1 = lp.diff()
SIG, kor_rows = {}, []
for ad, (x, dn, kay) in SER.items():
    x = x[x.index >= ix[0] - pd.Timedelta(days=200)]
    r1 = (np.log(x).diff() if dn in ("log", "ters") else x.diff())
    sd = r1.rolling(90, min_periods=40).std()
    z1, z5 = r1 / sd, (np.log(x).diff(5) if dn in ("log", "ters") else x.diff(5)) / (sd * np.sqrt(5))
    if kay == "likidite": z1, z5 = z1 * np.nan, (x.diff(4) / (x.diff().rolling(52, min_periods=20).std() * 2))   # haftalık: 4 haftalık değişim
    SIG[ad] = {k: m.reindex(ix).fillna(False).astype(bool) for k, m in (("ani yükseliş (1 g z≥2)", z1 >= 2), ("yükselişe başladı (5 g z≥1,5)", z5 >= 1.5),
                                                                            ("ani düşüş (1 g z≤−2)", z1 <= -2), ("düşüşe başladı (5 g z≤−1,5)", z5 <= -1.5))}
    zz5 = z5.reindex(ix); c0 = pd.DataFrame({"a": r1.reindex(ix), "b": btc1}).dropna()
    for pn, f in DON:
        row = dict(varlik=ad, donem=pn, ayni_gun_kor=c0[f(c0.index)].a.corr(c0[f(c0.index)].b))
        for H in (1, 3, 7):
            d = pd.DataFrame({"z": zz5, "y": Y[(H, 1)]}).dropna(); d = d[f(d.index)]; row[f"sonraki_{H}g_kor"] = d.z.corr(d.y)
        kor_rows.append(row)
K = pd.DataFrame(kor_rows)
yaz("## 1. İlişki tablosu (günlük)\n_ayni_gun_kor: aynı gün birlikte mi hareket ediyor (− = ters) · sonraki_Hg_kor: varlığın son 5 günlük hareketi ile BTC'nin SONRAKİ H günü (1 gün gecikmeli) — "
    "negatif = varlık yükselince BTC sonra düşüyor. ±0,05 altı pratikte ilişki yok._")
for pn in ("≤2023", "2024+", "2026"):
    yaz(f"### {pn}\n```\n" + K[K.donem == pn].drop(columns="donem").set_index("varlik").sort_values("sonraki_3g_kor").round(3).to_string() + "\n```")
def test(m, H, lag, reps=800):
    ev = ix[events(m.values, H)]; y = Y[(H, lag)].reindex(ev).dropna()
    e1 = y[y.index < A24]
    if len(e1) < 15: return None
    yon = -1 if e1.mean() < 0 else 1; net = yon * (np.exp(y) - 1) - 2 * FEE
    out = dict(yon="SAT" if yon < 0 else "AL")
    for pn, f in DON:
        e = net[f(net.index)]; out[pn] = (len(e), 100 * (e > 0).mean() if len(e) else np.nan, 100 * e.mean() if len(e) else np.nan, 100 * wboot(e.values, e.index.values, reps)[0] if len(e) >= 8 else np.nan)
    o23, o24 = out["≤2023"], out["2024+"]; out["ok"] = o23[2] > 0 and o24[0] >= 8 and o24[2] > 0 and o24[3] > 0; return out
yaz("\n## 2. Para testi (önceden sabit: yön ≤2023'ten · 2024+ net > 0 ve alt > 0 → ✅) — giriş 1 gün gecikmeli")
res, rng = [], np.random.default_rng(0); plasebo_ok = plasebo_n = 0
for ad in SIG:
    for sk, m in SIG[ad].items():
        if not m.any(): continue
        for H in (1, 3, 7):
            o = test(m, H, 1)
            if o is None: continue
            oh = test(m, H, 0) if SER[ad][2] == "yf" else None
            res.append(dict(varlik=ad, sinyal=sk, gun=H, yon=o["yon"], **{f"{pn} işlem·isabet·net·alt": " · ".join(("—" if not np.isfinite(v) else f"{v:.0f}" if i < 2 else f"{v:+.2f}") for i, v in enumerate(o[pn])) for pn, _ in DON},
                            hemen_2024_net=np.nan if oh is None else oh["2024+"][2], ok=o["ok"]))
            for _ in range(10):                                                             # plasebo: sinyali rastgele kaydır (otokorelasyon korunur)
                sh = int(rng.integers(90, len(m) - 90)); pm = pd.Series(np.roll(m.values, sh), index=m.index); po = test(pm, H, 1, reps=200)
                if po is not None: plasebo_n += 1; plasebo_ok += po["ok"]
R = pd.DataFrame(res)
gec = R[R.ok]
yaz(f"Toplam {len(R)} deneme · ✅ geçen: **{len(gec)}** · plasebo (rastgele kaydırılmış sinyal) geçme oranı %{100*plasebo_ok/max(1,plasebo_n):.1f} → tesadüfen beklenen ≈ **{plasebo_ok/max(1,plasebo_n)*len(R):.1f}**\n")
yaz("### ✅ Geçenler\n```\n" + (gec.drop(columns="ok").to_string(index=False) if len(gec) else "(yok)") + "\n```")
yaz("### 'Yükselince BTC SAT' sonuçları (kullanıcının sorusu): yükseliş sinyalleri, ≤2023'te BTC sonra düşmüş olanlar\n```\n"
    + R[(R.sinyal.str.contains("yüksel")) & (R.yon == "SAT")].drop(columns="ok").to_string(index=False) + "\n```")
yaz("### Tüm denemeler (2024+ sırasıyla)\n```\n" + R.assign(_s=R["2024+ işlem·isabet·net·alt"].str.split(" · ").str[2].str.replace("—", "nan").astype(float)).sort_values("_s", ascending=False).drop(columns=["_s"]).to_string(index=False) + "\n```")
# ---- 3. saatlik ----
yaz("\n## 3. Saatlik (son 730 gün, Yahoo vadeli/döviz): varlık 1 saatte ani hareket → BTC sonraki saatler (giriş 1 saat sonra)")
HT = {"DXY vadeli": "DX=F", "Altın vadeli": "GC=F", "Petrol vadeli": "CL=F", "Nasdaq vadeli": "NQ=F", "S&P vadeli": "ES=F", "Yen güçleniyor (USD/JPY ters)": "JPY=X",
      "Euro/dolar": "EURUSD=X", "10 y tahvil vadeli (fiyat; yükseliş = faiz düşüyor)": "ZN=F", "Gümüş vadeli": "SI=F", "VIX": "^VIX"}
now = pd.Timestamp.now(tz="UTC")
BH = fetch_1h((now - pd.Timedelta(days=735)).timestamp() * 1000, now.timestamp() * 1000, sym="BTCUSDT").close; lb = np.log(BH)
hrows, hres = [], []
for ad, t in HT.items():
    h = yfd(t, period="730d", interval="1h")
    if h is None or len(h) < 2000: yaz(f"- {ad}: saatlik veri alınamadı"); continue
    a = pd.Series(h.Close.values, index=pd.DatetimeIndex(h.index).tz_convert("UTC") + pd.Timedelta(hours=1))   # çubuk başı → kapanış zamanı
    if "ters" in ad: a = 1 / a
    a = a[~a.index.duplicated()].sort_index()
    g = pd.merge_asof(pd.DataFrame({"T": BH.index}), pd.DataFrame({"T": a.index, "ta": a.index, "a": a.values}), on="T", direction="backward").set_index("T")
    taze = pd.Series(np.asarray((g.index - pd.DatetimeIndex(g.ta)) <= pd.Timedelta(minutes=60)), index=g.index); la = np.log(g.a)
    r1 = la.diff().where(taze & taze.shift(1, fill_value=False)); z = r1 / r1.rolling(24 * 30, min_periods=200).std()
    yarisi = BH.index[0] + (BH.index[-1] - BH.index[0]) / 2
    for hh in (1, 4, 24):
        y = (lb.shift(-(1 + hh)) - lb.shift(-1))
        d = pd.DataFrame({"r": r1, "y": y, "b0": lb.diff()}).dropna()
        for pn, f in (("1. yıl", d.index < yarisi), ("2. yıl", d.index >= yarisi)):
            dd = d[f]; hrows.append(dict(varlik=ad, saat=hh, donem=pn, saat_say=len(dd), ayni_saat_kor=dd.r.corr(dd.b0), sonraki_kor=dd.r.corr(dd.y)))
        for sk, m in (("ani yükseliş (z≥2,5)", z >= 2.5), ("ani düşüş (z≤−2,5)", z <= -2.5)):
            ev = BH.index[events(m.fillna(False).values, hh)]; e = y.reindex(ev).dropna()
            e1, e2 = e[e.index < yarisi], e[e.index >= yarisi]
            if len(e1) < 15 or len(e2) < 8: continue
            yon = -1 if e1.mean() < 0 else 1; n1, n2 = yon * (np.exp(e1) - 1) - 2 * FEE, yon * (np.exp(e2) - 1) - 2 * FEE
            lo = wboot(n2.values, n2.index.values)[0]
            hres.append(dict(varlik=ad, sinyal=sk, saat=hh, yon="SAT" if yon < 0 else "AL", yil1=f"{len(n1)} · %{100*(n1>0).mean():.0f} · {100*n1.mean():+.2f}",
                             yil2=f"{len(n2)} · %{100*(n2>0).mean():.0f} · {100*n2.mean():+.2f} (alt {100*lo:+.2f})", ok=n1.mean() > 0 and n2.mean() > 0 and lo > 0))
    time.sleep(1)
if hrows:
    HK = pd.DataFrame(hrows)
    yaz("_ayni_saat_kor: aynı saatte birlikte mi · sonraki_kor: varlığın son 1 saati ile BTC'nin sonraki H saati (negatif = varlık yükselince BTC sonra düşüyor)_\n```\n"
        + HK.pivot_table(index=["varlik", "saat"], columns="donem", values=["ayni_saat_kor", "sonraki_kor"]).round(3).to_string() + "\n```")
if hres:
    HR = pd.DataFrame(hres)
    yaz(f"Saatlik para testi ({len(HR)} deneme; yön 1. yıldan, 2. yıl net > 0 ve alt > 0 → ✅; işlem · isabet · işlem başı net %): ✅ geçen **{int(HR.ok.sum())}**\n```\n" + HR.to_string(index=False) + "\n```")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("varlik_sonuc.md", "w").write("\n".join(L) + "\n")
