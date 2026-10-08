# 🐋🧑 BTC yatırımcı tipleri (bitcoin-data.com) — 08.10.2026 13:21
- `coins-addr-10K-BTC` (HTTP 200): 2022-10-08 → 2026-10-07, 1437 gün, sütunlar: coinsAddr10Kbtc
- `coins-addr-10K-1K-BTC` (HTTP 200): 2022-10-08 → 2026-10-07, 1437 gün, sütunlar: coinsAddr10Kto1Kbtc
- `coins-addr-1-BTC` (HTTP 200): 2022-10-08 → 2026-10-07, 1437 gün, sütunlar: coinsAddr1btc
- `balance-addr-1-BTC` (HTTP 200): 2022-10-08 → 2026-10-07, 1437 gün, sütunlar: balAddr1btc
- `supply-adjusted-cdd` (HTTP 200): 2022-10-08 → 2026-10-07, 1459 gün, sütunlar: supplyAdjustedCdd
- `sth-sopr` (HTTP 200): 2022-10-08 → 2026-10-01, 1455 gün, sütunlar: sthSopr
- `lth-sopr` (HTTP 200): 2022-10-08 → 2026-10-01, 1454 gün, sütunlar: lthSopr
- `hodl-waves-supply` (HTTP 200): 2022-10-08 → 2026-10-07, 1461 gün, sütunlar: age_0d_1d, age_1d_1w, age_1w_1m, age_1m_3m, age_3m_6m, age_6m_1y, age_1y_2y, age_2y_3y, age_3y_4y, age_4y_5y, age_5y_7y, age_7y_10y …

HODL dalgası sütunları: age_0d_1d, age_1d_1w, age_1w_1m, age_1m_3m, age_3m_6m, age_6m_1y, age_1y_2y, age_2y_3y, age_3y_4y, age_4y_5y, age_5y_7y, age_7y_10y, age_10y
1 yıldan eski sayılan: age_1y_2y, age_2y_3y, age_3y_4y, age_4y_5y, age_5y_7y, age_7y_10y, age_10y

Özellikler: balina BTC 30g, küçük cüzdan BTC 30g, küçük cüzdan sayısı 30g, eski coin hareketi (CDD 7g), STH-SOPR 7g, LTH-SOPR 7g, 1 yıldan eski arz payı 30g · 27 sn

## A) Önceden sabit hipotezler (yön sabit) — işlem · isabet % · işlem başı net % · alt sınır %
```
                                                              seçim (→2024-09)     doğrulama (2024-10→)                     2026
hipotez                                           gun                                                                           
H1 balinalar topluyor → AL                        3    53 · 49 · +0.40 · -0.47  56 · 41 · -1.24 · -2.01  20 · 25 · -2.41 · -3.51
                                                  7    26 · 58 · +0.95 · -1.25  26 · 38 · -2.13 · -4.06   9 · 22 · -4.48 · -8.35
H1b balinalar dağıtıyor → SAT                     3    51 · 47 · -0.20 · -1.03  58 · 40 · -0.75 · -1.60  21 · 48 · -0.57 · -1.79
                                                  7    25 · 60 · +0.41 · -1.76  28 · 36 · -1.62 · -3.20  10 · 40 · -1.25 · -3.94
H2 küçük yatırımcı akını → SAT                    3    27 · 52 · -0.48 · -1.44  36 · 44 · -0.35 · -1.00  21 · 43 · -0.65 · -1.56
                                                  7    13 · 31 · -1.42 · -4.38  16 · 44 · -0.50 · -2.08   8 · 38 · -1.30 · -3.89
H2c küçük cüzdan sayısı fırlıyor → SAT            3    33 · 39 · -1.20 · -2.04  22 · 55 · -0.19 · -1.06        2 · 0 · -3.90 · —
                                                  7    17 · 35 · -1.95 · -4.00  12 · 33 · -2.03 · -3.79        2 · 0 · -5.58 · —
H3 balina topluyor + küçük satıyor → AL           3    45 · 51 · +0.69 · -0.24  19 · 53 · -1.02 · -2.82        5 · 0 · -4.93 · —
                                                  7    23 · 61 · +1.52 · -0.92  10 · 50 · -1.04 · -5.06       3 · 33 · -7.17 · —
H4 eski coin'ler uyanıyor → SAT                   3    35 · 40 · -0.41 · -1.10  35 · 23 · -1.55 · -2.59       6 · 33 · -0.53 · —
                                                  7    15 · 47 · -0.82 · -3.00  19 · 32 · -2.64 · -4.82       4 · 25 · -1.55 · —
H4b eski arz payı düşüyor → SAT                   3    32 · 47 · +0.82 · -0.28  36 · 44 · -1.05 · -2.28   8 · 50 · -2.37 · -5.46
                                                  7    16 · 75 · +1.67 · -0.40  19 · 47 · -3.16 · -6.35       5 · 60 · -4.21 · —
H5 kısa vadeli zararına satıyor (teslimiyet) → AL 3    22 · 45 · +0.67 · -0.41  23 · 52 · +0.63 · -0.94       7 · 57 · +0.91 · —
                                                  7    11 · 45 · +1.97 · -0.81  13 · 69 · +0.89 · -1.66       4 · 50 · -1.23 · —
H5b kısa vadeli büyük kârla satıyor → SAT         3    29 · 41 · -0.67 · -1.83  34 · 35 · -1.03 · -2.11  10 · 30 · -0.82 · -1.75
                                                  7    16 · 25 · -2.26 · -4.40  18 · 44 · -2.31 · -4.20       6 · 50 · -0.98 · —
H6 uzun vadeli büyük kârla satıyor → SAT          3    68 · 44 · -0.51 · -1.42  32 · 44 · -0.98 · -1.76  10 · 70 · +0.59 · -0.04
                                                  7    33 · 52 · -1.11 · -2.78  16 · 38 · -1.51 · -3.41       5 · 40 · -0.72 · —
```
### Karar (A)
- ❌ H1 balinalar topluyor → AL · 7 gün: seçim 26 · 58 · +0.95 · -1.25 · doğrulama 26 · 38 · -2.13 · -4.06 · 2026 9 · 22 · -4.48 · -8.35
- ❌ H1b balinalar dağıtıyor → SAT · 7 gün: seçim 25 · 60 · +0.41 · -1.76 · doğrulama 28 · 36 · -1.62 · -3.20 · 2026 10 · 40 · -1.25 · -3.94
- ❌ H2 küçük yatırımcı akını → SAT · 7 gün: seçim 13 · 31 · -1.42 · -4.38 · doğrulama 16 · 44 · -0.50 · -2.08 · 2026 8 · 38 · -1.30 · -3.89
- ❌ H2c küçük cüzdan sayısı fırlıyor → SAT · 7 gün: seçim 17 · 35 · -1.95 · -4.00 · doğrulama 12 · 33 · -2.03 · -3.79 · 2026 2 · 0 · -5.58 · —
- ❌ H3 balina topluyor + küçük satıyor → AL · 7 gün: seçim 23 · 61 · +1.52 · -0.92 · doğrulama 10 · 50 · -1.04 · -5.06 · 2026 3 · 33 · -7.17 · —
- ❌ H4 eski coin'ler uyanıyor → SAT · 7 gün: seçim 15 · 47 · -0.82 · -3.00 · doğrulama 19 · 32 · -2.64 · -4.82 · 2026 4 · 25 · -1.55 · —
- ❌ H4b eski arz payı düşüyor → SAT · 7 gün: seçim 16 · 75 · +1.67 · -0.40 · doğrulama 19 · 47 · -3.16 · -6.35 · 2026 5 · 60 · -4.21 · —
- ❌ H5 kısa vadeli zararına satıyor (teslimiyet) → AL · 7 gün: seçim 11 · 45 · +1.97 · -0.81 · doğrulama 13 · 69 · +0.89 · -1.66 · 2026 4 · 50 · -1.23 · —
- ❌ H5b kısa vadeli büyük kârla satıyor → SAT · 7 gün: seçim 16 · 25 · -2.26 · -4.40 · doğrulama 18 · 44 · -2.31 · -4.20 · 2026 6 · 50 · -0.98 · —
- ❌ H6 uzun vadeli büyük kârla satıyor → SAT · 7 gün: seçim 33 · 52 · -1.11 · -2.78 · doğrulama 16 · 38 · -1.51 · -3.41 · 2026 5 · 40 · -0.72 · —

Şu an: balina BTC 30g z +0.18 · küçük cüzdan BTC 30g z +0.61 · küçük cüzdan sayısı 30g z +1.23 · eski coin hareketi (CDD 7g) z +0.34 · STH-SOPR 7g z +0.17 · LTH-SOPR 7g z +1.29 · 1 yıldan eski arz payı 30g z -1.64

## B) Geniş tarama (yön seçim döneminden; doğrulamada net > 0 ve alt > 0 → ✅)
Toplam 53 deneme · ✅ geçen **11** · plasebo geçme oranı %8.5 → tesadüfen beklenen ≈ **4.5**
```
                       olcu   sinyal  gun yon        seçim (→2024-09)    doğrulama (2024-10→)                    2026    ok
             balina BTC 30g  z ≥ 1,5    3  AL 31 · 58 · +0.79 · -0.40 39 · 44 · -1.51 · -2.70 12 · 33 · -2.16 · -5.09 False
             balina BTC 30g  z ≥ 1,5    7  AL 16 · 69 · +2.42 · -0.21 19 · 42 · -1.94 · -4.24      5 · 20 · -4.25 · — False
             balina BTC 30g z ≤ −1,5    3 SAT 31 · 55 · -0.01 · -1.30 35 · 46 · -0.38 · -1.13 16 · 50 · -0.34 · -1.53 False
             balina BTC 30g z ≤ −1,5    7  AL 15 · 60 · +0.72 · -1.98 19 · 58 · +0.89 · -1.37      7 · 57 · +0.26 · — False
             balina BTC 30g    z ≥ 1    3  AL 53 · 49 · +0.40 · -0.47 56 · 41 · -1.24 · -2.01 20 · 25 · -2.41 · -3.51 False
             balina BTC 30g    z ≥ 1    7  AL 26 · 58 · +0.95 · -1.25 26 · 38 · -2.13 · -4.06  9 · 22 · -4.48 · -8.35 False
             balina BTC 30g   z ≤ −1    3  AL 51 · 53 · +0.12 · -0.60 58 · 59 · +0.67 · -0.10 21 · 52 · +0.49 · -0.55 False
             balina BTC 30g   z ≤ −1    7 SAT 25 · 60 · +0.41 · -1.76 28 · 36 · -1.62 · -3.20 10 · 40 · -1.25 · -3.94 False
       küçük cüzdan BTC 30g  z ≥ 1,5    3  AL 27 · 44 · +0.40 · -0.41 36 · 56 · +0.27 · -0.39 21 · 57 · +0.57 · -0.49 False
       küçük cüzdan BTC 30g  z ≥ 1,5    7  AL 13 · 69 · +1.34 · -1.29 16 · 56 · +0.42 · -1.27  8 · 62 · +1.22 · -1.29 False
       küçük cüzdan BTC 30g z ≤ −1,5    3  AL 35 · 69 · +2.12 · +1.15 45 · 64 · +1.69 · +0.53 17 · 53 · +1.65 · -0.00  True
       küçük cüzdan BTC 30g z ≤ −1,5    7  AL 17 · 82 · +4.41 · +2.36 22 · 73 · +2.97 · +0.66  8 · 75 · +3.21 · -0.70  True
       küçük cüzdan BTC 30g    z ≥ 1    3  AL 51 · 45 · +0.16 · -0.71 69 · 51 · -0.17 · -0.66 27 · 59 · +0.33 · -0.46 False
       küçük cüzdan BTC 30g    z ≥ 1    7  AL 24 · 54 · +0.13 · -1.62 32 · 56 · -0.39 · -1.95 12 · 58 · +0.23 · -1.87 False
       küçük cüzdan BTC 30g   z ≤ −1    3  AL 63 · 65 · +1.88 · +0.91 74 · 53 · +0.85 · -0.05 21 · 62 · +1.56 · +0.04 False
       küçük cüzdan BTC 30g   z ≤ −1    7  AL 30 · 73 · +3.92 · +1.88 35 · 60 · +2.07 · +0.43 10 · 60 · +2.99 · -0.27  True
    küçük cüzdan sayısı 30g  z ≥ 1,5    3  AL 33 · 58 · +1.12 · +0.41 22 · 45 · +0.11 · -0.61     2 · 100 · +3.82 · — False
    küçük cüzdan sayısı 30g  z ≥ 1,5    7  AL 17 · 65 · +1.87 · -0.22 12 · 67 · +1.95 · -0.06     2 · 100 · +5.50 · — False
    küçük cüzdan sayısı 30g z ≤ −1,5    3  AL 34 · 59 · +1.84 · +0.61 31 · 39 · -0.29 · -1.74 14 · 29 · -1.51 · -3.05 False
    küçük cüzdan sayısı 30g z ≤ −1,5    7  AL 17 · 76 · +5.02 · +2.43 20 · 40 · -0.12 · -2.73  8 · 25 · -3.17 · -6.07 False
    küçük cüzdan sayısı 30g    z ≥ 1    3  AL 57 · 60 · +0.50 · -0.15 49 · 63 · +0.79 · +0.11 11 · 82 · +2.33 · +1.35  True
    küçük cüzdan sayısı 30g    z ≥ 1    7  AL 28 · 50 · +0.52 · -1.17 27 · 63 · +1.31 · -0.23  8 · 88 · +2.98 · +1.60 False
    küçük cüzdan sayısı 30g   z ≤ −1    3  AL 55 · 55 · +1.64 · +0.55 66 · 55 · +0.58 · -0.44 23 · 48 · -0.19 · -2.33 False
    küçük cüzdan sayısı 30g   z ≤ −1    7  AL 26 · 69 · +3.74 · +2.01 36 · 53 · +0.78 · -1.19 12 · 58 · +0.34 · -3.17 False
eski coin hareketi (CDD 7g)  z ≥ 1,5    3  AL 35 · 60 · +0.33 · -0.41 35 · 77 · +1.47 · +0.49      6 · 67 · +0.45 · —  True
eski coin hareketi (CDD 7g)  z ≥ 1,5    7  AL 15 · 53 · +0.74 · -1.61 19 · 68 · +2.56 · +0.06      4 · 75 · +1.47 · —  True
eski coin hareketi (CDD 7g)    z ≥ 1    3  AL 50 · 60 · +0.61 · -0.10 57 · 63 · +0.46 · -0.36 12 · 58 · -0.36 · -1.76 False
eski coin hareketi (CDD 7g)    z ≥ 1    7  AL 22 · 59 · +1.40 · -0.60 29 · 66 · +1.49 · -0.37      7 · 43 · -0.16 · — False
eski coin hareketi (CDD 7g)   z ≤ −1    3  AL 36 · 50 · +0.05 · -0.85 31 · 52 · -0.34 · -1.44 10 · 60 · +0.29 · -1.17 False
eski coin hareketi (CDD 7g)   z ≤ −1    7  AL 22 · 59 · +1.56 · -0.60 17 · 47 · -0.02 · -1.58      7 · 43 · -0.08 · — False
                STH-SOPR 7g  z ≥ 1,5    3  AL 29 · 59 · +0.59 · -0.64 34 · 65 · +0.95 · +0.07 10 · 70 · +0.74 · -0.05  True
                STH-SOPR 7g  z ≥ 1,5    7  AL 16 · 69 · +2.18 · +0.10 18 · 56 · +2.23 · +0.48      6 · 50 · +0.90 · —  True
                STH-SOPR 7g z ≤ −1,5    3  AL 22 · 45 · +0.67 · -0.41 23 · 52 · +0.63 · -0.94      7 · 57 · +0.91 · — False
                STH-SOPR 7g z ≤ −1,5    7  AL 11 · 45 · +1.97 · -0.81 13 · 69 · +0.89 · -1.66      4 · 50 · -1.23 · — False
                STH-SOPR 7g    z ≥ 1    3  AL 47 · 53 · +0.75 · -0.16 59 · 59 · +0.91 · +0.12 20 · 55 · +0.70 · -0.65  True
                STH-SOPR 7g    z ≥ 1    7  AL 25 · 68 · +2.44 · +0.64 26 · 58 · +1.58 · -0.48  9 · 56 · +0.96 · -1.80 False
                STH-SOPR 7g   z ≤ −1    3  AL 47 · 66 · +1.42 · +0.54 49 · 55 · +0.00 · -0.90 10 · 40 · -1.39 · -5.18 False
                STH-SOPR 7g   z ≤ −1    7  AL 26 · 65 · +3.31 · +1.05 24 · 58 · -0.35 · -2.75      6 · 33 · -2.24 · — False
                LTH-SOPR 7g  z ≥ 1,5    3  AL 68 · 54 · +0.43 · -0.33 32 · 56 · +0.90 · +0.15 10 · 30 · -0.67 · -1.43  True
                LTH-SOPR 7g  z ≥ 1,5    7  AL 33 · 48 · +1.03 · -0.52 16 · 62 · +1.43 · -0.19      5 · 60 · +0.64 · — False
                LTH-SOPR 7g z ≤ −1,5    3  AL 12 · 67 · +1.37 · +0.31 31 · 55 · +0.48 · -0.75 16 · 56 · +1.04 · -0.68 False
                LTH-SOPR 7g    z ≥ 1    3  AL 90 · 57 · +0.70 · -0.11 48 · 56 · +0.58 · -0.10 18 · 50 · -0.01 · -0.80 False
                LTH-SOPR 7g    z ≥ 1    7  AL 41 · 59 · +1.89 · +0.05 25 · 52 · +0.53 · -1.08  9 · 33 · -0.08 · -2.23 False
                LTH-SOPR 7g   z ≤ −1    3  AL 23 · 74 · +0.79 · -0.15 67 · 58 · -0.38 · -1.19 33 · 58 · -0.26 · -1.57 False
                LTH-SOPR 7g   z ≤ −1    7  AL 13 · 62 · +1.03 · -0.77 33 · 42 · -0.73 · -2.60 16 · 38 · -1.16 · -3.45 False
 1 yıldan eski arz payı 30g  z ≥ 1,5    3 SAT 31 · 48 · +0.11 · -1.34 45 · 47 · +0.87 · -0.04 11 · 45 · +1.75 · -0.50 False
 1 yıldan eski arz payı 30g  z ≥ 1,5    7 SAT 16 · 62 · +0.22 · -2.63 21 · 57 · +1.89 · -0.25      5 · 80 · +4.16 · — False
 1 yıldan eski arz payı 30g z ≤ −1,5    3 SAT 32 · 47 · +0.82 · -0.28 36 · 44 · -1.05 · -2.28  8 · 50 · -2.37 · -5.46 False
 1 yıldan eski arz payı 30g z ≤ −1,5    7 SAT 16 · 75 · +1.67 · -0.40 19 · 47 · -3.16 · -6.35      5 · 60 · -4.21 · — False
 1 yıldan eski arz payı 30g    z ≥ 1    3  AL 55 · 55 · +0.70 · -0.64 65 · 49 · -0.68 · -1.39 16 · 56 · -1.10 · -3.21 False
 1 yıldan eski arz payı 30g    z ≥ 1    7  AL 27 · 56 · +1.13 · -1.57 31 · 42 · -1.46 · -3.09  8 · 38 · -1.86 · -5.72 False
 1 yıldan eski arz payı 30g   z ≤ −1    3  AL 60 · 53 · +0.41 · -0.54 56 · 52 · +0.77 · -0.02 13 · 38 · +1.00 · -1.23 False
 1 yıldan eski arz payı 30g   z ≤ −1    7  AL 30 · 53 · +1.79 · -0.31 26 · 54 · +2.54 · +0.47      7 · 29 · +1.41 · —  True
```

_Süre: 48 sn_
