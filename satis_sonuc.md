# 🔻 Düşüşte satış (kısa pozisyon) sinyali — 08.10.2026 08:55
Canlı erişim (GitHub sunucusundan, HTTP kodu): vadeli emir defteri (fapi depth): 451 · vadeli mum (fapi klines): 451 · spot emir defteri (data-api depth): 200 · spot mum (data-api klines): 200
13051 işlem · 176 sn

## Sonuçlar (işlem başı %, kısa pozisyon: fiyat düşerse kazanç · isabet = fiyatın düştüğü işlem oranı)
```
                                                                   islem  haftada  isabet  brut  fonlama   net   alt  yıllık  maxDD
kural                                               donem                                                                          
B1 akış/defter z ≤ −2 (vadeli defter)               seçim (≤2023)     58     1.14   48.28  0.09     0.02  0.07 -0.28    3.09  -8.69
                                                    2024+            155     1.07   47.74  0.33     0.02  0.31  0.03   17.28 -15.01
                                                    2026              38     0.95   50.00  0.43     0.01  0.40 -0.07   21.03  -8.13
B2 Coinbase primi z ≤ −2                            seçim (≤2023)    353     1.07   52.12  0.43     0.02  0.41  0.09   19.31 -37.24
                                                    2024+            152     1.05   51.32  0.38     0.02  0.36  0.04   19.79 -15.46
                                                    2026              42     1.05   45.24  0.49     0.01  0.46 -0.42   25.73 -12.14
B3 spot satıcı baskısı 24 s z ≤ −2                  seçim (≤2023)    165     0.51   56.36  0.63     0.01  0.60 -0.06   13.82 -38.35
                                                    2024+             89     0.62   44.94 -0.08     0.02 -0.10 -0.59   -4.32 -18.55
                                                    2026              25     0.63   40.00 -0.10     0.01 -0.12 -0.72   -4.70 -10.00
B4 B3 + Coinbase primi z ≤ 0                        seçim (≤2023)    125     0.38   59.20  1.26     0.01  1.24  0.63   26.02 -10.50
                                                    2024+             52     0.36   46.15 -0.02     0.02 -0.04 -0.72   -1.75 -22.54
                                                    2026              12     0.30   50.00  0.47     0.02  0.45 -0.64    6.75  -6.76
B5 spot satıcı baskısı 4 s z ≤ −2 + Coinbase z ≤ −1 seçim (≤2023)    127     0.41   50.39  0.62     0.01  0.60 -0.04   11.89 -24.31
                                                    2024+             55     0.38   45.45 -0.08     0.02 -0.10 -0.73   -2.63 -21.54
                                                    2026              16     0.40   56.25  0.43     0.01  0.40 -0.38    8.40  -6.26
B6 B2 veya B3                                       seçim (≤2023)    469     1.42   50.32  0.37     0.02  0.35  0.07   21.90 -38.66
                                                    2024+            227     1.57   48.46  0.17     0.02  0.15 -0.10   10.12 -21.63
                                                    2026              61     1.53   44.26  0.12     0.01  0.09 -0.51    4.71 -20.47
C1 coin spot satıcı baskısı 24 s z ≤ −2             seçim (≤2023)   1440     4.48   47.08 -0.33     0.01 -0.35 -0.65     NaN    NaN
                                                    2024+           1008     6.99   51.98  0.28     0.01  0.25 -0.11     NaN    NaN
                                                    2026             275     6.90   53.45  0.44    -0.00  0.40 -0.06     NaN    NaN
C2 C1 + BTC Coinbase primi z ≤ 0                    seçim (≤2023)   1066     3.34   47.47 -0.24     0.02 -0.26 -0.63     NaN    NaN
                                                    2024+            700     4.85   52.43  0.35     0.01  0.32 -0.21     NaN    NaN
                                                    2026             181     4.54   51.93  0.43     0.00  0.39 -0.03     NaN    NaN
C3 BTC Coinbase primi z ≤ −2 → coin sat             seçim (≤2023)   2797     8.49   52.45  0.32     0.00  0.29 -0.16     NaN    NaN
                                                    2024+           1672    11.59   55.74  0.56     0.01  0.53 -0.01     NaN    NaN
                                                    2026             462    11.59   50.87  0.23     0.00  0.19 -0.94     NaN    NaN
C4 coin'in kendi Coinbase primi z ≤ −2 (keşif)      seçim (≤2023)    183    15.43   44.26 -0.62     0.04 -0.62 -1.26     NaN    NaN
                                                    2024+           2158    14.96   53.29  0.22     0.01  0.19 -0.07     NaN    NaN
                                                    2026             766    19.22   51.96  0.09     0.00  0.05 -0.45     NaN    NaN
```

## Karar (önceden sabit: seçimde net > 0, 2024+'da net > 0 ve alt sınır > 0)
- ✅ B1 akış/defter z ≤ −2 (vadeli defter): 2024+ haftada 1.1, isabet %48, net %+0.31 (alt +0.03) · 2026: isabet %50, net %+0.40 (38)
- ✅ B2 Coinbase primi z ≤ −2: 2024+ haftada 1.1, isabet %51, net %+0.36 (alt +0.04) · 2026: isabet %45, net %+0.46 (42)
- ❌ B3 spot satıcı baskısı 24 s z ≤ −2: 2024+ haftada 0.6, isabet %45, net %-0.10 (alt -0.59) · 2026: isabet %40, net %-0.12 (25)
- ❌ B4 B3 + Coinbase primi z ≤ 0: 2024+ haftada 0.4, isabet %46, net %-0.04 (alt -0.72) · 2026: isabet %50, net %+0.45 (12)
- ❌ B5 spot satıcı baskısı 4 s z ≤ −2 + Coinbase z ≤ −1: 2024+ haftada 0.4, isabet %45, net %-0.10 (alt -0.73) · 2026: isabet %56, net %+0.40 (16)
- ❌ B6 B2 veya B3: 2024+ haftada 1.6, isabet %48, net %+0.15 (alt -0.10) · 2026: isabet %44, net %+0.09 (61)
- ❌ C1 coin spot satıcı baskısı 24 s z ≤ −2: 2024+ haftada 7.0, isabet %52, net %+0.25 (alt -0.11) · 2026: isabet %53, net %+0.40 (275)
- ❌ C2 C1 + BTC Coinbase primi z ≤ 0: 2024+ haftada 4.9, isabet %52, net %+0.32 (alt -0.21) · 2026: isabet %52, net %+0.39 (181)
- ❌ C3 BTC Coinbase primi z ≤ −2 → coin sat: 2024+ haftada 11.6, isabet %56, net %+0.53 (alt -0.01) · 2026: isabet %51, net %+0.19 (462)
- ❌ C4 coin'in kendi Coinbase primi z ≤ −2 (keşif): 2024+ haftada 15.0, isabet %53, net %+0.19 (alt -0.07) · 2026: isabet %52, net %+0.05 (766) · seçim dönemi yok (keşif)

Şu an (BTC): Coinbase primi z -1.95 · spot satıcı baskısı 24 s z +0.10 · akış/defter z (arşiv, 1 gün gecikmeli) +0.27
_Süre: 177 sn_
