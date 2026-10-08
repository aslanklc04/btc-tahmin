# 🐋🧑 Zincir üstü yatırımcı tipleri — 08.10.2026 13:17
**BTC** — katalogda tip ölçüsü 5, veri gelen 5: `AdrActCnt`, `AdrBalCnt`, `CapMVRVCur`, `SplyCur`, `SplyExpFut10yr`
**ETH** — katalogda tip ölçüsü 5, veri gelen 5: `AdrActCnt`, `AdrBalCnt`, `CapMVRVCur`, `SplyCur`, `SplyExpFut10yr`
_9 sn_

## A) Önceden sabit hipotezler (7 gün tut; yön önceden sabit) — işlem · isabet % · işlem başı net % · alt sınır %
### BTC — balina: `None` · küçük yatırımcı: `None` · eski coin: `None` (hareketsiz pay) · kârlılık: `CapMVRVCur`
```
                                                          ≤2023                    2024+                     2026
hipotez                           gun                                                                            
H5 yatırımcılar çok kârda → SAT   3    135 · 42 · -1.82 · -2.90  42 · 45 · -1.10 · -2.27            0 · — · — · —
                                  7     64 · 38 · -4.01 · -6.57  19 · 42 · -2.14 · -5.13            0 · — · — · —
H5b yatırımcılar çok zararda → AL 3    129 · 49 · +0.37 · -0.75  65 · 54 · -0.28 · -0.98  40 · 52 · -0.26 · -1.27
                                  7     62 · 61 · +1.28 · -0.93  30 · 50 · -0.44 · -2.04  18 · 50 · -0.69 · -2.89
```
Şu an: MVRV z +0.50 (veri günü 07.10)

### ETH — balina: `None` · küçük yatırımcı: `None` · eski coin: `None` (hareketsiz pay) · kârlılık: `CapMVRVCur`
```
                                                          ≤2023                    2024+                     2026
hipotez                           gun                                                                            
H5 yatırımcılar çok kârda → SAT   3     86 · 47 · -0.98 · -2.48  36 · 53 · -0.31 · -1.85            0 · — · — · —
                                  7     46 · 57 · -1.86 · -5.14  17 · 35 · -1.48 · -5.03            0 · — · — · —
H5b yatırımcılar çok zararda → AL 3    122 · 49 · -0.27 · -1.76  53 · 45 · +0.56 · -0.95  20 · 45 · -0.31 · -2.52
                                  7     63 · 43 · -0.89 · -3.91  29 · 62 · +2.46 · -1.38  11 · 45 · +0.25 · -4.31
```
Şu an: MVRV z +0.66 (veri günü 07.10)

### Karar (A)
- ❌ BTC · H5 yatırımcılar çok kârda → SAT · 7 gün: ≤2023 64 · 38 · -4.01 · -6.57 · 2024+ 19 · 42 · -2.14 · -5.13 · 2026 0 · — · — · —
- ❌ BTC · H5b yatırımcılar çok zararda → AL · 7 gün: ≤2023 62 · 61 · +1.28 · -0.93 · 2024+ 30 · 50 · -0.44 · -2.04 · 2026 18 · 50 · -0.69 · -2.89
- ❌ ETH · H5 yatırımcılar çok kârda → SAT · 7 gün: ≤2023 46 · 57 · -1.86 · -5.14 · 2024+ 17 · 35 · -1.48 · -5.03 · 2026 0 · — · — · —
- ❌ ETH · H5b yatırımcılar çok zararda → AL · 7 gün: ≤2023 63 · 43 · -0.89 · -3.91 · 2024+ 29 · 62 · +2.46 · -1.38 · 2026 11 · 45 · +0.25 · -4.31

## B) Geniş tarama: tüm ücretsiz tip ölçüleri (yön ≤2023'ten; 2024+ net > 0 ve alt > 0 → ✅)
Toplam 32 deneme · ✅ geçen **0** · plasebo geçme oranı %5.6 → tesadüfen beklenen ≈ **1.8**
### ✅ Geçenler
```
(yok)
```
### Tümü
```
coin           olcu   sinyal  gun yon                    ≤2023                   2024+                    2026
 BTC      AdrActCnt  z ≥ 1,5    3  AL 129 · 51 · +0.69 · -0.10 51 · 55 · +0.20 · -0.81 12 · 33 · -0.57 · -1.92
 BTC      AdrActCnt  z ≥ 1,5    7  AL 110 · 50 · +1.07 · -0.36 42 · 52 · +1.40 · -0.13  9 · 56 · +0.13 · -2.84
 BTC      AdrActCnt z ≤ −1,5    3 SAT 128 · 49 · +0.03 · -1.13 64 · 48 · -0.46 · -1.53 19 · 42 · +0.15 · -1.40
 BTC      AdrActCnt z ≤ −1,5    7  AL 106 · 52 · +0.92 · -0.90 58 · 47 · +0.90 · -0.51 19 · 58 · -0.19 · -2.22
 BTC      AdrBalCnt  z ≥ 1,5    3  AL 124 · 58 · +1.13 · -0.04 34 · 50 · -0.16 · -0.84     2 · 100 · +3.82 · —
 BTC      AdrBalCnt  z ≥ 1,5    7  AL  61 · 59 · +3.01 · +0.04 17 · 53 · -0.02 · -1.90     2 · 100 · +5.50 · —
 BTC      AdrBalCnt z ≤ −1,5    3 SAT 130 · 47 · +0.08 · -0.99 48 · 46 · -1.08 · -2.45 16 · 69 · +0.13 · -2.75
 BTC      AdrBalCnt z ≤ −1,5    7 SAT  67 · 52 · -0.40 · -2.64 26 · 54 · -2.67 · -5.93  8 · 88 · +1.06 · -4.89
 BTC     CapMVRVCur  z ≥ 1,5    3  AL 135 · 58 · +1.74 · +0.73 42 · 55 · +1.02 · -0.03           0 · — · — · —
 BTC     CapMVRVCur  z ≥ 1,5    7  AL  64 · 62 · +3.93 · +1.44 19 · 58 · +2.06 · -0.91           0 · — · — · —
 BTC     CapMVRVCur z ≤ −1,5    3  AL 129 · 49 · +0.37 · -0.75 65 · 54 · -0.28 · -0.98 40 · 52 · -0.26 · -1.27
 BTC     CapMVRVCur z ≤ −1,5    7  AL  62 · 61 · +1.28 · -0.93 30 · 50 · -0.44 · -2.04 18 · 50 · -0.69 · -2.89
 BTC SplyExpFut10yr  z ≥ 1,5    3 SAT 178 · 48 · -0.15 · -0.94 50 · 48 · +0.17 · -0.68      6 · 83 · +4.22 · —
 BTC SplyExpFut10yr  z ≥ 1,5    7  AL  85 · 51 · +0.52 · -1.17 24 · 42 · -0.36 · -2.25       3 · 0 · -7.36 · —
 BTC SplyExpFut10yr z ≤ −1,5    3 SAT  80 · 56 · +0.46 · -0.49 47 · 51 · -0.28 · -1.13 26 · 50 · -0.06 · -1.13
 BTC SplyExpFut10yr z ≤ −1,5    7 SAT  41 · 56 · +1.79 · -0.57 25 · 44 · -1.91 · -4.33 13 · 46 · -0.28 · -2.94
 ETH      AdrActCnt  z ≥ 1,5    3  AL 117 · 55 · +1.31 · +0.30 50 · 36 · -1.14 · -2.19 11 · 18 · -3.00 · -5.55
 ETH      AdrActCnt  z ≥ 1,5    7  AL  84 · 51 · +2.98 · +0.69 33 · 55 · -1.84 · -4.14      7 · 57 · -3.33 · —
 ETH      AdrActCnt z ≤ −1,5    3 SAT  89 · 47 · -0.03 · -1.51 46 · 43 · -0.04 · -1.11 14 · 36 · -0.28 · -1.78
 ETH      AdrActCnt z ≤ −1,5    7  AL  65 · 46 · +1.06 · -1.51 35 · 57 · +0.89 · -0.73 10 · 60 · +1.63 · -1.22
 ETH      AdrBalCnt  z ≥ 1,5    3  AL 102 · 57 · +1.01 · -0.69 70 · 61 · +0.64 · -0.48 10 · 40 · -2.02 · -4.65
 ETH      AdrBalCnt  z ≥ 1,5    7  AL  47 · 51 · +3.44 · -0.13 35 · 57 · +1.12 · -1.37      5 · 40 · -2.93 · —
 ETH      AdrBalCnt z ≤ −1,5    3  AL 147 · 54 · +0.78 · -0.37 46 · 54 · -0.30 · -1.67 22 · 68 · +1.52 · -0.13
 ETH      AdrBalCnt z ≤ −1,5    7  AL  71 · 58 · +1.64 · -0.60 22 · 50 · -0.95 · -3.81 11 · 64 · +2.80 · -1.19
 ETH     CapMVRVCur  z ≥ 1,5    3  AL  86 · 53 · +0.90 · -0.49 36 · 47 · +0.23 · -1.41           0 · — · — · —
 ETH     CapMVRVCur  z ≥ 1,5    7  AL  46 · 43 · +1.78 · -1.41 17 · 65 · +1.40 · -2.24           0 · — · — · —
 ETH     CapMVRVCur z ≤ −1,5    3 SAT 122 · 51 · +0.19 · -1.34 53 · 51 · -0.64 · -2.27 20 · 55 · +0.23 · -1.69
 ETH     CapMVRVCur z ≤ −1,5    7 SAT  63 · 57 · +0.81 · -1.77 29 · 38 · -2.54 · -6.46 11 · 55 · -0.33 · -4.86
 ETH SplyExpFut10yr  z ≥ 1,5    3  AL  70 · 60 · +0.85 · -0.59           0 · — · — · —           0 · — · — · —
 ETH SplyExpFut10yr  z ≥ 1,5    7  AL  36 · 56 · +4.44 · +1.11           0 · — · — · —           0 · — · — · —
 ETH SplyExpFut10yr z ≤ −1,5    3 SAT 131 · 51 · +0.03 · -1.37           0 · — · — · —           0 · — · — · —
 ETH SplyExpFut10yr z ≤ −1,5    7 SAT  66 · 59 · +0.92 · -1.53           0 · — · — · —           0 · — · — · —
```

_Süre: 15 sn_
