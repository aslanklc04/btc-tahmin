# zit.py — BTC'nin ZITTI coin var mı? (BTC yükselirken düşen, BTC düşerken yükselen)
# Evren: Binance'teki TÜM USDT çiftleri (listeden çıkarılmış / işlem durdurulmuş olanlar dahil — yalnız bugün yaşayanlara bakmak yanıltır).
# Kategoriler: normal coin · sabit değerli (stabil coin / itibari para: günlük oynaklık < %0,5) · altın (PAXG, XAUT) · kaldıraçlı token (BTCDOWN vb., 2024'te kaldırıldı).
# Ölçüler (dönem başına): günlük getiri korelasyonu ve beta · BTC +%3 üstü günlerde coin'in DÜŞME oranı · BTC −%3 altı günlerde coin'in YÜKSELME oranı
#   · kayan 90 g korelasyonun negatif olduğu günlerin oranı (“hep” zıt mı) · ertesi gün (BTC bugün → coin yarın) korelasyonu.
# Önceden sabit: adaylar ≤2023 verisiyle seçilir (en negatif 15 korelasyon, ≥365 gün), 2024+ ve 2026'da hâlâ zıt mı bakılır.
# Para testi (önceden sabit): ≤2023'te ERTESİ GÜN korelasyonu en negatif 10 coin → BTC günü ≥ +%3 ise ertesi gün coin'i SAT, ≤ −%3 ise AL (1 gün, vadeli komisyon %0,05×2).
# Adayların saatlik verisi: 1 s / 4 s korelasyon, BTC'nin %1'den büyük oynadığı saatlerde zıt yön oranı.
import time, re, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
S = requests.Session()
def get(url, **p):
    for k in range(4):
        try:
            r = S.get(url, params=p, timeout=30)
            if r.status_code == 200: return r.json()
            if r.status_code in (400, 404): return None
        except Exception: pass
        time.sleep(1 + 2 * k)
    return None
INFO = None
for base in ("https://data-api.binance.vision", "https://api.binance.com"):
    INFO = get(base + "/api/v3/exchangeInfo")
    if INFO: break
SY = [s for s in INFO["symbols"] if s["quoteAsset"] == "USDT"]
yaz(f"# 🔄 BTC'nin zıttı coin var mı? — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nBinance USDT çiftleri: {len(SY)} (durum: " + ", ".join(f"{k} {v}" for k, v in pd.Series([s['status'] for s in SY]).value_counts().items()) + ")")
def gunluk(sym):
    rows, cur = [], int(pd.Timestamp("2017-08-01", tz="UTC").timestamp() * 1000)
    while True:
        r = get(EP[0], symbol=sym, interval="1d", startTime=cur, limit=1000)
        if not r: break
        rows += r; cur = r[-1][0] + 86_400_000
        if len(r) < 1000: break
    if len(rows) < 60: return sym, None
    d = pd.DataFrame([x[:6] for x in rows], columns=["t", "o", "h", "l", "c", "v"]).astype(float)
    return sym, pd.Series(d.c.values, index=pd.to_datetime(d.t, unit="ms", utc=True))
with ThreadPoolExecutor(10) as ex: PX = {k: v for k, v in ex.map(gunluk, [s["symbol"] for s in SY]) if v is not None}
yaz(f"Günlük veri alınan: {len(PX)} çift · {time.time()-T0:.0f} sn\n")
BASE = {s["symbol"]: s["baseAsset"] for s in SY}; DURUM = {s["symbol"]: s["status"] for s in SY}
BUYUK = "BTC ETH BNB XRP ADA LINK DOT EOS TRX XTZ LTC BCH FIL SXP YFI SUSHI UNI AAVE 1INCH XLM".split()
def kategori(sym, r):
    b = BASE[sym]
    if any(b == p + s for p in BUYUK for s in ("UP", "DOWN", "BULL", "BEAR")): return "kaldıraçlı token"
    if b in ("PAXG", "XAUT"): return "altın"
    if r.std() < 0.005: return "sabit değerli"
    return "normal"
btc = np.log(PX["BTCUSDT"]).diff()
A24, A26 = pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")
DON = (("≤2023", lambda i: i < A24), ("2024+", lambda i: i >= A24), ("2026", lambda i: i >= A26))
rows = []
for sym, px in PX.items():
    if sym == "BTCUSDT": continue
    r = np.log(px).diff().iloc[15:]                                                         # ilk 2 hafta (listeleme dalgası) hariç
    r = r[r.abs() < 1.5]
    if len(r) < 60: continue
    kat = kategori(sym, r); x = pd.DataFrame({"c": r, "b": btc.reindex(r.index)}).dropna()
    rc = x.c.rolling(90, min_periods=60).corr(x.b)
    for pn, f in DON:
        xx = x[f(x.index)]
        if len(xx) < 60: continue
        up, dn = xx[xx.b >= 0.03], xx[xx.b <= -0.03]; nx = xx.c.shift(-1)
        rows.append(dict(sym=sym, coin=BASE[sym], kat=kat, durum=DURUM[sym], donem=pn, gun=len(xx), kor=xx.c.corr(xx.b), beta=np.cov(xx.c, xx.b)[0, 1] / xx.b.var(),
                         btc_up_dus=100 * (up.c < 0).mean() if len(up) >= 5 else np.nan, btc_dn_yuk=100 * (dn.c > 0).mean() if len(dn) >= 5 else np.nan, n_up=len(up), n_dn=len(dn),
                         kayan_neg=100 * (rc[f(rc.index)] < 0).mean(), ertesi_kor=nx.corr(xx.b)))
R = pd.DataFrame(rows)
def tab(d, cols=("coin", "kat", "durum", "gun", "kor", "beta", "btc_up_dus", "btc_dn_yuk", "kayan_neg", "ertesi_kor")): return "```\n" + d[list(cols)].round(2).to_string(index=False) + "\n```"
yaz("## 1. Genel tablo: coin'ler BTC ile ne kadar birlikte hareket ediyor? (günlük, normal coin'ler)")
g = R[R.kat == "normal"].groupby("donem").agg(coin=("kor", "size"), medyan_kor=("kor", "median"), negatif_kor_coin=("kor", lambda s: int((s < 0).sum())),
                                                 medyan_btc_up_dus=("btc_up_dus", "median"), medyan_kayan_neg=("kayan_neg", "median"))
yaz("```\n" + g.round(2).to_string() + "\n```\n_kor: 1 = BTC ile tam aynı, 0 = ilgisiz, −1 = tam zıt · btc_up_dus: BTC +%3 üstü günlerde coin'in düştüğü günlerin %'si · kayan_neg: 90 günlük korelasyonun negatif olduğu günlerin %'si_\n")
yaz("## 2. Kategorilere göre (2024+)\n```\n" + R[R.donem == "2024+"].groupby("kat").agg(coin=("kor", "size"), medyan_kor=("kor", "median"), en_dusuk_kor=("kor", "min"),
                                                medyan_btc_up_dus=("btc_up_dus", "median")).round(2).to_string() + "\n```")
yaz("En negatif kaldıraçlı/altın/sabit örnekler (tüm dönemler):\n" + tab(R[R.kat != "normal"].sort_values("kor").groupby("kat").head(4), ("coin", "kat", "durum", "donem", "gun", "kor", "beta", "btc_up_dus", "btc_dn_yuk")))
yaz("\n## 3. Önceden sabit seçim: ≤2023'te BTC ile EN ZIT 15 normal coin (≥365 gün) → 2024+ ve 2026'da hâlâ zıt mı?")
p23 = R[(R.donem == "≤2023") & (R.kat == "normal") & (R.gun >= 365)].sort_values("kor").head(15)
sec = p23.sym.tolist()
yaz("≤2023:\n" + tab(p23))
p24 = R[(R.donem == "2024+") & R.sym.isin(sec)].set_index("sym").reindex(sec).dropna(subset=["kor"]).reset_index()
yaz("Aynı coin'ler 2024+:\n" + tab(p24))
p26 = R[(R.donem == "2026") & R.sym.isin(sec)].set_index("sym").reindex(sec).dropna(subset=["kor"]).reset_index()
yaz("Aynı coin'ler 2026:\n" + tab(p26))
yaz(f"→ ≤2023'te korelasyonu negatif olan normal coin: {int(((R.donem=='≤2023')&(R.kat=='normal')&(R.gun>=365)&(R.kor<0)).sum())} · bunlardan 2024+'da da negatif kalan: "
    + str(int(R[(R.donem == '2024+') & R.sym.isin(R[(R.donem=='≤2023')&(R.kat=='normal')&(R.gun>=365)&(R.kor<0)].sym)].kor.lt(0).sum())))
yaz("\n## 4. Bilgi: 2024+'da BTC ile en zıt 15 normal coin (≥180 gün; seçim sonradan yapıldığı için şans payı yüksek)")
yaz(tab(R[(R.donem == "2024+") & (R.kat == "normal") & (R.gun >= 180)].sort_values("kor").head(15)))
yaz("2026'da en zıt 10 normal coin (≥120 gün):\n" + tab(R[(R.donem == "2026") & (R.kat == "normal") & (R.gun >= 120)].sort_values("kor").head(10)))
yaz("\n## 5. 'BTC yükselirken düşen' en sık coin'ler (2024+, BTC +%3 üstü günler ≥ 15, normal)")
yaz(tab(R[(R.donem == "2024+") & (R.kat == "normal") & (R.n_up >= 15)].sort_values("btc_up_dus", ascending=False).head(12), ("coin", "durum", "gun", "n_up", "btc_up_dus", "n_dn", "btc_dn_yuk", "kor")))
# ---- sistemdeki coin'ler ----
try:
    CL = [l.strip() for l in open("durum/coin_listesi.txt") if l.strip()]
    yaz("\n## 6. Bizim sistemdeki coin'ler (günlük korelasyon)\n```\n" + R[R.sym.isin(CL)].pivot_table(index="coin", columns="donem", values="kor").round(2).to_string() + "\n```")
except Exception as e: yaz(f"_coin listesi okunamadı: {e}_")
# ---- 7. para testi: ertesi gün zıt hareket ----
yaz("\n## 7. Para testi (önceden sabit): BTC büyük günden sonra ERTESİ GÜN zıt hareket eden coin'ler")
q23 = R[(R.donem == "≤2023") & (R.kat == "normal") & (R.gun >= 365)].sort_values("ertesi_kor").head(10); sec2 = q23.sym.tolist()
yaz("≤2023'te ertesi gün korelasyonu en negatif 10 coin: " + ", ".join(f"{BASE[s]} {k:+.2f}" for s, k in zip(sec2, q23.ertesi_kor)))
FEE = 0.0005; out = []
for sym in sec2:
    r = np.log(PX[sym]).diff(); x = pd.DataFrame({"b": btc, "n": r.shift(-1)}).dropna()               # gün d kapanışında BTC'nin günü belli → hemen gir, d+1 kapanışında çık
    ev = x[(x.b >= 0.03) | (x.b <= -0.03)]; net = -np.sign(ev.b) * (np.exp(ev.n) - 1) - 2 * FEE
    for pn, f in DON:
        e = net[f(net.index)]
        if len(e) < 5: continue
        lo, _ = wboot(e.values, e.index.values) if len(e) >= 8 else (np.nan, np.nan)
        out.append(dict(coin=BASE[sym], donem=pn, islem=len(e), isabet=100 * (e > 0).mean(), net=100 * e.mean(), alt=100 * lo))
O = pd.DataFrame(out)
if len(O):
    yaz("```\n" + O.set_index(["coin", "donem"]).round(2).to_string() + "\n```")
    a = O[O.donem == "2024+"]; yaz(f"Toplam 2024+: {int(a.islem.sum())} işlem, ortalama net %{(a.net * a.islem).sum() / max(1, a.islem.sum()):+.2f}")
# ---- 8. saatlik: adaylar ----
cand = list(dict.fromkeys(sec[:8] + R[(R.donem == "2024+") & (R.kat == "normal") & (R.gun >= 180)].sort_values("kor").sym.head(6).tolist() + [s for s in ("PAXGUSDT",) if s in PX]))
yaz(f"\n## 8. Saatlik bakış (adaylar: {', '.join(BASE[s] for s in cand)})")
now_ms = time.time() * 1000; st = pd.Timestamp("2019-01-01", tz="UTC").timestamp() * 1000
def saatlik(sym):
    try: return sym, fetch_1h(st, now_ms, sym=sym).close
    except Exception: return sym, None
with ThreadPoolExecutor(6) as ex: HP = dict(ex.map(saatlik, ["BTCUSDT"] + cand))
hb = np.log(HP["BTCUSDT"]); hr = []
for sym in cand:
    if HP.get(sym) is None: continue
    hc = np.log(HP[sym])
    for H in (1, 4):
        x = pd.DataFrame({"b": hb.diff(H), "c": hc.diff(H)}).iloc[::H].dropna(); x = x[x.c.abs() < 1]
        for pn, f in DON:
            xx = x[f(x.index)]
            if len(xx) < 200: continue
            big = xx[xx.b.abs() >= 0.01 * np.sqrt(H)]
            hr.append(dict(coin=BASE[sym], saat=H, donem=pn, n=len(xx), kor=xx.c.corr(xx.b), btc_buyuk_hareket=len(big), zit_yon=100 * (np.sign(big.c) == -np.sign(big.b)).mean() if len(big) else np.nan))
yaz("```\n" + pd.DataFrame(hr).set_index(["coin", "saat", "donem"]).round(2).to_string() + "\n```\n_zit_yon: BTC'nin büyük oynadığı saatlerde (1 s: ≥%1, 4 s: ≥%2) coin'in ters yöne gittiği saatlerin %'si (50 = yazı tura)_")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("zit_sonuc.md", "w").write("\n".join(L) + "\n")
