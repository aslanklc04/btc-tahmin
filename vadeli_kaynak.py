# vadeli_kaynak.py — 24.10.2026 (kullanıcı onayı, öneri 5): vadeli piyasa verisi (açık pozisyon, likidasyon, coin fonlaması, uzun/kısa oranı) hangi kaynaktan, ne kadar geriye erişilebilir? Yalnız erişim yoklaması.
import io, zipfile, time, requests, pandas as pd
S = requests.Session(); S.headers.update({"User-Agent": "btc-tahmin"}); L = []
def dene(ad, url, params=None, f=lambda r: r.text[:160]):
    t = time.time()
    try:
        r = S.get(url, params=params, timeout=25); L.append(f"| {ad} | {r.status_code} | {time.time() - t:.1f} sn | {f(r) if r.status_code == 200 else r.text[:120].replace('|', '/')} |")
    except Exception as e: L.append(f"| {ad} | hata | — | {type(e).__name__}: {str(e)[:100]} |")
def zipcsv(r):
    z = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z.open(z.namelist()[0])); return f"{len(d)} satır · sütunlar: {', '.join(d.columns)[:150]}"
A = "https://data.binance.vision/data/futures/um"
L += ["# Vadeli veri kaynakları yoklaması (GitHub Actions, ABD)", "", "| Kaynak | HTTP | süre | içerik |", "|---|---|---|---|"]
for c, gun in (("BTCUSDT", "2022-01-03"), ("BTCUSDT", "2026-10-22"), ("INJUSDT", "2023-06-01"), ("RLCUSDT", "2024-03-01")):
    dene(f"Binance arşiv metrics {c} {gun} (5 dk OI, uzun/kısa, taker oranı)", f"{A}/daily/metrics/{c}/{c}-metrics-{gun}.zip", f=zipcsv)
dene("Binance arşiv fundingRate INJUSDT 2023-06 (aylık)", f"{A}/monthly/fundingRate/INJUSDT/INJUSDT-fundingRate-2023-06.zip", f=zipcsv)
dene("Binance arşiv liquidationSnapshot BTCUSDT 2023-06-01", f"{A}/daily/liquidationSnapshot/BTCUSDT/BTCUSDT-liquidationSnapshot-2023-06-01.zip", f=zipcsv)
dene("Binance fapi openInterest (canlı)", "https://fapi.binance.com/fapi/v1/openInterest", {"symbol": "BTCUSDT"})
dene("Binance fapi openInterestHist (canlı)", "https://fapi.binance.com/futures/data/openInterestHist", {"symbol": "BTCUSDT", "period": "1h", "limit": 5})
dene("Bybit open-interest", "https://api.bybit.com/v5/market/open-interest", {"category": "linear", "symbol": "BTCUSDT", "intervalTime": "1h", "limit": 5})
dene("Bybit funding history", "https://api.bybit.com/v5/market/funding/history", {"category": "linear", "symbol": "INJUSDT", "limit": 5})
dene("OKX funding history", "https://www.okx.com/api/v5/public/funding-rate-history", {"instId": "INJ-USDT-SWAP", "limit": 5})
dene("OKX open interest", "https://www.okx.com/api/v5/public/open-interest", {"instType": "SWAP", "instId": "BTC-USDT-SWAP"})
dene("KuCoin funding INJ", "https://api-futures.kucoin.com/api/v1/contract/funding-rates", {"symbol": "INJUSDTM", "from": int((time.time() - 86400 * 400) * 1000), "to": int((time.time() - 86400 * 370) * 1000)}, f=lambda r: f"{len(r.json().get('data', []))} kayıt (400–370 gün önce)")
dene("KuCoin contracts active (anlık OI)", "https://api-futures.kucoin.com/api/v1/contracts/active", f=lambda r: f"{len(r.json().get('data', []))} kontrat · örnek alanlar: {', '.join(list(r.json()['data'][0].keys())[:12])}")
dene("Gate.io futures OI/contract_stats", "https://api.gateio.ws/api/v4/futures/usdt/contract_stats", {"contract": "BTC_USDT", "interval": "1h", "limit": 3})
dene("Neon /fonlama (Frankfurt, canlıda kullanılan)", "https://br-still-union-baibtf1k-derinlik.compute.c-8.eu-central-1.aws.neon.tech/fonlama", {"c": "BTC,INJ"}, f=lambda r: r.text[:160])
# arşivde hangi coin'ler var: canlı geniş liste + coin listesi
GEN = [l.strip() for l in open("canli/durum/genis_liste.txt") if l.strip()] + [l.strip() for l in open("canli/durum/coin_listesi.txt") if l.strip()]
var = sum(S.head(f"{A}/daily/metrics/{c}/{c}-metrics-2026-10-20.zip", timeout=15).status_code == 200 for c in GEN)
L.append(f"\nArşivde metrics dosyası olan coin: {var} / {len(GEN)} (canlı listeler, 20.10.2026)")
open("vadeli_kaynak_sonuc.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
