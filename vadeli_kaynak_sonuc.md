# Vadeli veri kaynakları yoklaması (GitHub Actions, ABD)

| Kaynak | HTTP | süre | içerik |
|---|---|---|---|
| Binance arşiv metrics BTCUSDT 2022-01-03 (5 dk OI, uzun/kısa, taker oranı) | 200 | 0.6 sn | 288 satır · sütunlar: create_time, symbol, sum_open_interest, sum_open_interest_value, count_toptrader_long_short_ratio, sum_toptrader_long_short_ratio, count_long_short_ra |
| Binance arşiv metrics BTCUSDT 2026-10-22 (5 dk OI, uzun/kısa, taker oranı) | 200 | 0.2 sn | 288 satır · sütunlar: create_time, symbol, sum_open_interest, sum_open_interest_value, count_toptrader_long_short_ratio, sum_toptrader_long_short_ratio, count_long_short_ra |
| Binance arşiv metrics INJUSDT 2023-06-01 (5 dk OI, uzun/kısa, taker oranı) | 200 | 0.5 sn | 288 satır · sütunlar: create_time, symbol, sum_open_interest, sum_open_interest_value, count_toptrader_long_short_ratio, sum_toptrader_long_short_ratio, count_long_short_ra |
| Binance arşiv metrics RLCUSDT 2024-03-01 (5 dk OI, uzun/kısa, taker oranı) | 200 | 0.5 sn | 288 satır · sütunlar: create_time, symbol, sum_open_interest, sum_open_interest_value, count_toptrader_long_short_ratio, sum_toptrader_long_short_ratio, count_long_short_ra |
| Binance arşiv fundingRate INJUSDT 2023-06 (aylık) | 200 | 0.5 sn | 90 satır · sütunlar: calc_time, funding_interval_hours, last_funding_rate |
| Binance arşiv liquidationSnapshot BTCUSDT 2023-06-01 | 404 | 0.4 sn | <?xml version="1.0" encoding="UTF-8"?>
<Error><Code>NoSuchKey</Code><Message>The specified key does not exist.</Message> |
| Binance fapi openInterest (canlı) | 200 | 0.3 sn | {"symbol":"BTCUSDT","openInterest":"95866.868","time":1792867250864} |
| Binance fapi openInterestHist (canlı) | 200 | 0.2 sn | [{"symbol":"BTCUSDT","sumOpenInterest":"94622.99200000","sumOpenInterestValue":"7631987741.14560000","CMCCirculatingSupply":"20102640.00000000","timestamp":1792 |
| Bybit open-interest | 200 | 0.4 sn | {"retCode":0,"retMsg":"OK","result":{"symbol":"BTCUSDT","category":"linear","list":[{"openInterest":"64603.99400000","singleOpenInterest":"32301.997","timestamp |
| Bybit funding history | 200 | 0.2 sn | {"retCode":0,"retMsg":"OK","result":{"category":"linear","list":[{"symbol":"INJUSDT","fundingRate":"0.00002949","fundingRateTimestamp":"1792857600000"},{"symbol |
| OKX funding history | 200 | 0.3 sn | {"code":"0","data":[{"formulaType":"withRate","fundingRate":"-0.0000104483903124","fundingTime":"1792857600000","instId":"INJ-USDT-SWAP","instType":"SWAP","meth |
| OKX open interest | 200 | 0.2 sn | {"code":"0","data":[{"instId":"BTC-USDT-SWAP","instType":"SWAP","oi":"3060753.2500000122","oiCcy":"30607.532500000122","oiUsd":"2458247033.4907597984422","ts":" |
| KuCoin funding INJ | 200 | 0.3 sn | 90 kayıt (400–370 gün önce) |
| KuCoin contracts active (anlık OI) | 200 | 0.2 sn | 706 kontrat · örnek alanlar: symbol, displaySymbol, rootSymbol, type, firstOpenDate, expireDate, settleDate, baseCurrency, displayBaseCurrency, quoteCurrency, settleCurrency, maxOrderQty |
| Gate.io futures OI/contract_stats | 200 | 0.9 sn | [{"time":1792857600,"lsr_taker":0.9613926588556938,"lsr_account":2.0780375974323704,"long_liq_size":3250,"short_liq_size":46093,"open_interest":582535632,"short |
| Neon /fonlama (Frankfurt, canlıda kullanılan) | 200 | 1.6 sn | {"t":"2026-10-24T18:41:02.010Z","coins":{"BTC":[[1790006400002,0.00005485],[1790035200000,0.00007663],[1790064000004,0.0001],[1790092800000,0.00002784],[1790121 |

Arşivde metrics dosyası olan coin: 127 / 140 (canlı listeler, 20.10.2026)
