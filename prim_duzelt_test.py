# prim_duzelt_test.py — TEST (18.10.2026, önceden yazılı): prim-duzelt dalındaki yeni ortak.cb_prim (son saat = son gerçek işlem, eski saat yok)
# canlıdaki gibi saat başından +3 dk'da okunur; eski cb_prim (main) ile birlikte. Kesin değer: +65 dk'da Coinbase mumlarıyla aynı saat (canlı yöntem).
# 2. deneme (18.10 19:00): 1. denemede işlem seçimi hatası (sayfa sırası varsayımı) düzeltildi, şart aynı.
# GEÇME ŞARTI (önceden): yeni yöntemde |z − kesin| ≤ 0,2 olan coin oranı ≥ %95 VE eski yöntemden kötü değil VE eski saatin z'si hiç kullanılmamış.
import importlib.util, os, sys, time, json, numpy as np, pandas as pd
def yukle(ad, yol):
    sys.path.insert(0, os.path.dirname(yol)); sp = importlib.util.spec_from_file_location(ad, yol); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); sys.path.pop(0); return m
YENI = yukle("ortak_yeni", "yeni/ortak.py"); ESKI = yukle("ortak_eski", "eski/ortak.py")
C = ["REQ", "ARPA", "PUNDIX", "BAND", "KNC", "C98", "GNO", "BNT", "MASK", "BLUR", "T", "CVC", "CELR", "AUDIO", "ALT", "KAVA", "UMA", "RPL", "ARKM", "GMT",
     "GTC", "POWR", "RLC", "AUCTION", "LQTY", "GLM", "ALICE", "RARE", "LPT", "AGLD", "1INCH", "CTSI", "FIDA", "MINA", "OGN", "API3", "G", "SUSHI", "VET", "ROSE",
     "BTC", "ETH", "SOL", "OP", "DOT", "LINK", "AVAX", "DOGE", "ARB", "LDO"]
os.makedirs("/tmp/pd", exist_ok=True)
h0 = pd.Timestamp.now(tz="UTC").ceil("h"); print("bekleniyor:", h0, flush=True)
while pd.Timestamp.now(tz="UTC") < h0 + pd.Timedelta(minutes=3): time.sleep(5)
from concurrent.futures import ThreadPoolExecutor
def oku(nm):
    t0 = time.time(); y = YENI.cb_prim(nm, path=f"/tmp/pd/y_{nm}.json"); ty = time.time() - t0; e = ESKI.cb_prim(nm, path=f"/tmp/pd/e_{nm}.json")
    return nm, dict(z_yeni=YENI.cb_z(y), t_yeni=(y or {}).get("t"), kaynak=(y or {}).get("kaynak"), islem=YENI.CB_SON_DEBUG.get(nm, {}).get("islem", "")[11:19], sayfa=f'{YENI.CB_SON_DEBUG.get(nm, {}).get("sayfa_ilk", "")[11:19]}→{YENI.CB_SON_DEBUG.get(nm, {}).get("sayfa_son", "")[11:19]}', sn_yeni=round(ty, 1), z_eski=ESKI.cb_z(e), t_eski=(e or {}).get("t"))
with ThreadPoolExecutor(4) as ex: R = dict(ex.map(oku, C))
print("+3 dk okundu", pd.Timestamp.now(tz="UTC"), flush=True)
while pd.Timestamp.now(tz="UTC") < h0 + pd.Timedelta(minutes=65): time.sleep(10)
def kesin(nm):
    import requests
    s = requests.Session(); out = []
    for k in (3, 2, 1):
        a, b = h0 - pd.Timedelta(hours=300 * k), h0 - pd.Timedelta(hours=300 * (k - 1))
        for _ in range(3):
            r = s.get(f"https://api.exchange.coinbase.com/products/{nm}-USD/candles", params=dict(granularity=3600, start=a.isoformat(), end=b.isoformat()), timeout=20)
            if r.status_code == 200: out += r.json(); break
            time.sleep(1.5)
    d = pd.DataFrame(out, columns=["t", "low", "high", "open", "close", "volume"]).drop_duplicates("t")
    cb = pd.Series(d.close.values.astype(float), index=pd.to_datetime(d.t, unit="s", utc=True) + pd.Timedelta(hours=1)).sort_index(); cb = cb[cb.index <= h0]
    bn = YENI.fetch_1h((h0 - pd.Timedelta(hours=920)).timestamp() * 1000, (h0 + pd.Timedelta(minutes=1)).timestamp() * 1000, sym=f"{nm}USDT").close
    p = np.log(cb / bn.reindex(cb.index)).dropna(); z = (p - p.rolling(720, min_periods=168).mean()) / (p.rolling(720, min_periods=168).std() + 1e-12)
    return nm, (float(z[h0]) if h0 in z.index else np.nan)
with ThreadPoolExecutor(4) as ex: KZ = dict(ex.map(kesin, C))
X = pd.DataFrame([dict(coin=nm, **R[nm], z_kesin=KZ[nm]) for nm in C])
X["hata_yeni"] = (X.z_yeni - X.z_kesin).abs(); X["hata_eski"] = (X.z_eski - X.z_kesin).abs()
hz = str(h0)
def iyi(col, tcol):                                                                             # doğru: (ikisi de NaN) ya da (aynı saat ve |fark| ≤ 0,2)
    nan_ok = X[col].isna() & X.z_kesin.isna(); val_ok = (X[tcol] == hz) & (X[col] - X.z_kesin).abs().le(0.2); return nan_ok | val_ok
X["dogru_yeni"], X["dogru_eski"] = iyi("z_yeni", "t_yeni"), iyi("z_eski", "t_eski")
eski_saat = int((X.t_yeni.notna() & (X.t_yeni != hz)).sum())
py, pe = X.dogru_yeni.mean() * 100, X.dogru_eski.mean() * 100
pd.set_option("display.width", 250)
L = [f"# 💵 Prim düzeltme testi — saat {h0.tz_convert('Europe/Istanbul'):%d.%m %H:00} (TR) · okuma +3 dk · kesin +65 dk", "```", X.round(2).to_string(index=False), "```",
     f"- doğru (|z − kesin| ≤ 0,2 ya da ikisi de yok): YENİ %{py:.0f} ({int(X.dogru_yeni.sum())}/{len(X)}) · ESKİ %{pe:.0f} ({int(X.dogru_eski.sum())}/{len(X)})",
     f"- yenide eski saatin z'si kullanılan: {eski_saat} · yeni yöntem süresi ort {X.sn_yeni.mean():.1f} sn, en çok {X.sn_yeni.max():.1f} sn",
     f"- yalnız az işlem gören 40 coin: YENİ %{X.dogru_yeni[:40].mean() * 100:.0f} · ESKİ %{X.dogru_eski[:40].mean() * 100:.0f} · likit 10 coin: YENİ %{X.dogru_yeni[40:].mean() * 100:.0f} · ESKİ %{X.dogru_eski[40:].mean() * 100:.0f}",
     f"\n**Karar (önceden yazılı):** " + ("✅ GEÇTİ" if (py >= 95 and py >= pe and eski_saat == 0) else "❌ GEÇMEDİ") + f" (şart: yeni ≥ %95, eskiden kötü değil, eski saat 0)"]
open("prim_duzelt_sonuc.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
