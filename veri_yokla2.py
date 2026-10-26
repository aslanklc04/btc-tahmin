# veri_yokla2.py — 26.10: fiyat dışı veri kaynakları GitHub Actions'tan erişilebilir mi, ne kadar geriye gidiyor (yalnız tanı)
import io, zipfile, time, requests, pandas as pd
S = requests.Session(); S.headers["User-Agent"] = "btc-tahmin"; L = []
def yaz(s): print(s, flush=True); L.append(s)
def dene(ad, url, **kw):
    try:
        r = S.get(url, timeout=40, **kw); ok = r.status_code
        if r.headers.get("content-type", "").startswith("application/zip") or url.endswith(".zip"):
            if ok == 200:
                z = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z.open(z.namelist()[0]))
                yaz(f"- ✅ {ad}: HTTP 200 · sütunlar {list(d.columns)[:12]} · {len(d)} satır · ilk {d.iloc[0].tolist()[:6]}")
            else: yaz(f"- ❌ {ad}: HTTP {ok}")
            return ok
        t = r.text[:400].replace("\n", " ")
        yaz(f"- {'✅' if ok == 200 else '❌'} {ad}: HTTP {ok} · {t}")
        return ok
    except Exception as e: yaz(f"- ❌ {ad}: {e!r}"[:300]); return None
B = "https://data.binance.vision/data/futures/um"
yaz("## Binance vadeli arşivi (data.binance.vision)")
for gun in ("2021-12-01", "2022-06-01", "2024-01-01", "2026-10-20"):
    dene(f"metrics BTCUSDT {gun}", f"{B}/daily/metrics/BTCUSDT/BTCUSDT-metrics-{gun}.zip")
dene("metrics ETHUSDT 2023-01-01", f"{B}/daily/metrics/ETHUSDT/ETHUSDT-metrics-2023-01-01.zip")
dene("metrics SOLUSDT 2023-01-01", f"{B}/daily/metrics/SOLUSDT/SOLUSDT-metrics-2023-01-01.zip")
for ay in ("2020-01", "2022-06", "2026-09"): dene(f"fundingRate BTCUSDT {ay}", f"{B}/monthly/fundingRate/BTCUSDT/BTCUSDT-fundingRate-{ay}.zip")
dene("premiumIndexKlines 1h BTCUSDT 2022-06", f"{B}/monthly/premiumIndexKlines/BTCUSDT/1h/BTCUSDT-1h-2022-06.zip")
dene("klines 1h BTCUSDT (vadeli) 2022-06", f"{B}/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2022-06.zip")
for gun in ("2022-06-01", "2023-06-01", "2024-06-01"): dene(f"liquidationSnapshot BTCUSDT {gun}", f"{B}/daily/liquidationSnapshot/BTCUSDT/BTCUSDT-liquidationSnapshot-{gun}.zip")
dene("bookDepth BTCUSDT 2024-06-01", f"{B}/daily/bookDepth/BTCUSDT/BTCUSDT-bookDepth-2024-06-01.zip")
dene("coin-m metrics BTCUSD_PERP 2023-01-01", "https://data.binance.vision/data/futures/cm/daily/metrics/BTCUSD_PERP/BTCUSD_PERP-metrics-2023-01-01.zip")
dene("opsiyon BVOLIndex BTCBVOLUSDT 2023-06-01", "https://data.binance.vision/data/option/daily/BVOLIndex/BTCBVOLUSDT/BTCBVOLUSDT-BVOLIndex-2023-06-01.zip")
yaz("\n## Deribit (opsiyon)")
now = int(time.time() * 1000)
dene("DVOL BTC saatlik (son 30 gün)", f"https://www.deribit.com/api/v2/public/get_volatility_index_data?currency=BTC&start_timestamp={now - 30 * 86400000}&end_timestamp={now}&resolution=3600")
dene("DVOL BTC 2021-06", f"https://www.deribit.com/api/v2/public/get_volatility_index_data?currency=BTC&start_timestamp=1622505600000&end_timestamp=1622592000000&resolution=3600")
dene("Deribit fonlama BTC-PERPETUAL", f"https://www.deribit.com/api/v2/public/get_funding_rate_history?instrument_name=BTC-PERPETUAL&start_timestamp={now - 3 * 86400000}&end_timestamp={now}")
dene("Deribit opsiyon özet (put/call)", "https://www.deribit.com/api/v2/public/get_book_summary_by_currency?currency=BTC&kind=option")
yaz("\n## OKX")
dene("OKX long/short hesap oranı", "https://www.okx.com/api/v5/rubik/stat/contracts/long-short-account-ratio?ccy=BTC&period=1H")
dene("OKX açık pozisyon + hacim", "https://www.okx.com/api/v5/rubik/stat/contracts/open-interest-volume?ccy=BTC&period=1H")
dene("OKX opsiyon put/call", "https://www.okx.com/api/v5/rubik/stat/option/open-interest-volume-ratio?ccy=BTC&period=1D")
dene("OKX fonlama geçmişi", "https://www.okx.com/api/v5/public/funding-rate-history?instId=BTC-USDT-SWAP&limit=5")
yaz("\n## Diğer")
dene("Bybit açık pozisyon", "https://api.bybit.com/v5/market/open-interest?category=linear&symbol=BTCUSDT&intervalTime=1h&limit=3")
dene("Binance fapi açık pozisyon geçmişi", "https://fapi.binance.com/futures/data/openInterestHist?symbol=BTCUSDT&period=1h&limit=3")
dene("Korku-açgözlülük (alternative.me)", "https://api.alternative.me/fng/?limit=3")
dene("Korku-açgözlülük tüm geçmiş", "https://api.alternative.me/fng/?limit=0&format=json")
dene("Coinbase BTC-USD", "https://api.exchange.coinbase.com/products/BTC-USD/ticker")
dene("Kraken fonlama/OI (futures)", "https://futures.kraken.com/derivatives/api/v3/tickers")
dene("Hyperliquid fonlama geçmişi", "https://api.hyperliquid.xyz/info", )
dene("blockchain.info borsa girişleri yok — mempool", "https://mempool.space/api/v1/fees/recommended")
dene("CoinMetrics community BTC FlowInExNtv", "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets=btc&metrics=FlowInExNtv,FlowOutExNtv&frequency=1d&page_size=3")
open("veri_yokla2.md", "w").write("# Veri kaynakları yoklaması — 26.10.2026 (GitHub Actions'tan)\n" + "\n".join(L) + "\n")
