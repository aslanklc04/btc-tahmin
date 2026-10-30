# 🧭 BTC'nin YÖNÜ — 3. tur: ZAMAN + YÖN · PROTOKOL_btcyon3.md
_30.10.2026 21:42 · hücre: işlem · yön isabeti · isabet (masraf sonrası kâr) · işlem başı net % · ✅ yön şartı · 🎯 sinyal adayı_

_Hareket penceresi P: oynaklık oranı ≥ 1.00 (K üst %30) veya sonraki blok 12–16 UTC · saatlerin %44'i_

## Z1 — Yön modeli (btcyon Y5) yalnız hareket penceresinde (K = yalnız 2023)
| kural | K | C1 2024 | C2 2025–26 | |
|---|---|---|---|---|
| model 4 s · tüm saatler | 653 · yön %60 · isabet %40 · -0.15 | 805 · yön %55 · isabet %44 · -0.17 | 1120 · yön %53 · isabet %39 · -0.19 |  | ‖ limit emirle net: +0.01 · -0.01 · -0.03
| model 4 s · yalnız P | 296 · yön %56 · isabet %42 · -0.15 | 398 · yön %54 · isabet %44 · -0.15 | 540 · yön %53 · isabet %41 · -0.23 |  | ‖ limit emirle net: +0.01 · +0.01 · -0.07
| PLASEBO model 4 s · tüm saatler | 479 · yön %47 · isabet %32 · -0.23 | 468 · yön %53 · isabet %41 · -0.14 | 840 · yön %50 · isabet %34 · -0.23 |  |
| PLASEBO model 4 s · yalnız P | 234 · yön %44 · isabet %36 · -0.23 | 235 · yön %54 · isabet %43 · -0.12 | 435 · yön %47 · isabet %34 · -0.28 |  |
| model 24 s · tüm saatler | 61 · yön %67 · isabet %54 · +0.20 | 86 · yön %53 · isabet %50 · -0.14 | 100 · yön %53 · isabet %46 · -0.08 |  | ‖ limit emirle net: +0.36 · +0.02 · +0.08
| model 24 s · yalnız P | 45 · yön %67 · isabet %49 · +0.21 | 68 · yön %59 · isabet %54 · -0.17 | 81 · yön %52 · isabet %46 · -0.11 |  | ‖ limit emirle net: +0.37 · -0.01 · +0.05
| PLASEBO model 24 s · tüm saatler | 199 · yön %51 · isabet %43 · -0.23 | 195 · yön %48 · isabet %42 · -0.45 | 344 · yön %49 · isabet %44 · -0.22 |  |
| PLASEBO model 24 s · yalnız P | 118 · yön %47 · isabet %41 · -0.46 | 122 · yön %52 · isabet %48 · -0.35 | 212 · yön %54 · isabet %51 · -0.08 |  |

## Z2 — Vadeli uyumsuzluk + kalabalık + trend + pencere (yön mantıktan sabit)
| kural | K | C1 2024 | C2 2025–26 | |
|---|---|---|---|---|
| uyumsuzluk (SAT+AL) · filtresiz · 24 s | 112 · yön %62 · isabet %58 · +0.13 | 74 · yön %54 · isabet %51 · -0.25 | 132 · yön %58 · isabet %53 · -0.02 |  |
| yalnız negatif → SAT · filtresiz · 24 s | 71 · yön %63 · isabet %59 · +0.20 | 67 · yön %55 · isabet %52 · -0.12 | 85 · yön %60 · isabet %55 · +0.24 |  |
| uyumsuzluk (SAT+AL) · a kalabalık · 24 s | 41 · yön %59 · isabet %56 · +0.04 | 31 · yön %48 · isabet %48 · -0.24 | 83 · yön %58 · isabet %52 · +0.05 |  |
| yalnız negatif → SAT · a kalabalık · 24 s | 23 · yön %61 · isabet %61 · +0.25 | 27 · yön %52 · isabet %52 · +0.02 | 51 · yön %61 · isabet %55 · +0.27 |  |
| uyumsuzluk (SAT+AL) · b trend · 24 s | 31 · yön %65 · isabet %61 · +0.44 | 19 · yön %47 · isabet %42 · -0.76 | 50 · yön %66 · isabet %60 · +0.40 |  |
| yalnız negatif → SAT · b trend · 24 s | 30 · yön %63 · isabet %60 · +0.40 | 13 · yön %62 · isabet %54 · +0.08 | 33 · yön %58 · isabet %48 · +0.07 |  |
| uyumsuzluk (SAT+AL) · c pencere · 24 s | 65 · yön %60 · isabet %55 · +0.30 | 36 · yön %56 · isabet %50 · -0.17 | 77 · yön %60 · isabet %58 · +0.12 |  |
| yalnız negatif → SAT · c pencere · 24 s | 38 · yön %68 · isabet %63 · +0.50 | 34 · yön %56 · isabet %50 · -0.06 | 50 · yön %64 · isabet %64 · +0.45 |  |
| uyumsuzluk (SAT+AL) · a+b · 24 s | 14 · yön %64 · isabet %64 · +0.43 | 8 · yön %38 · isabet %38 · -0.91 | 38 · yön %66 · isabet %58 · +0.31 |  |
| yalnız negatif → SAT · a+b · 24 s | 13 · yön %62 · isabet %62 · +0.34 | 5 · yön %60 · isabet %60 · +0.44 | 29 · yön %59 · isabet %48 · +0.09 |  |
| uyumsuzluk (SAT+AL) · a+b+c · 24 s | 8 · yön %75 · isabet %75 · +1.04 | 1 · yön %0 · isabet %0 · -5.68 | 21 · yön %67 · isabet %67 · +0.43 |  |
| yalnız negatif → SAT · a+b+c · 24 s | 7 · yön %71 · isabet %71 · +0.97 | 0 | 15 · yön %60 · isabet %60 · +0.12 |  |
| uyumsuzluk (SAT+AL) · filtresiz · 72 s | 92 · yön %55 · isabet %53 · +0.09 | 57 · yön %37 · isabet %37 · -1.47 | 101 · yön %56 · isabet %54 · +0.32 |  |
| yalnız negatif → SAT · filtresiz · 72 s | 60 · yön %58 · isabet %57 · +0.12 | 51 · yön %39 · isabet %39 · -1.15 | 68 · yön %59 · isabet %57 · +0.25 |  |
| uyumsuzluk (SAT+AL) · a kalabalık · 72 s | 37 · yön %51 · isabet %51 · -0.25 | 29 · yön %41 · isabet %41 · -0.26 | 69 · yön %57 · isabet %54 · +0.36 |  |
| yalnız negatif → SAT · a kalabalık · 72 s | 21 · yön %52 · isabet %52 · -0.06 | 25 · yön %44 · isabet %44 · +0.19 | 40 · yön %55 · isabet %52 · -0.04 |  |
| uyumsuzluk (SAT+AL) · b trend · 72 s | 26 · yön %54 · isabet %54 · +0.91 | 16 · yön %19 · isabet %19 · -3.16 | 43 · yön %60 · isabet %58 · +0.87 |  |
| yalnız negatif → SAT · b trend · 72 s | 25 · yön %52 · isabet %52 · +0.50 | 11 · yön %27 · isabet %27 · -2.23 | 28 · yön %57 · isabet %54 · +0.04 |  |
| uyumsuzluk (SAT+AL) · c pencere · 72 s | 58 · yön %52 · isabet %50 · -0.44 | 30 · yön %37 · isabet %40 · -1.73 | 67 · yön %57 · isabet %55 · +0.50 |  |
| yalnız negatif → SAT · c pencere · 72 s | 34 · yön %56 · isabet %53 · -0.05 | 29 · yön %34 · isabet %38 · -1.83 | 43 · yön %58 · isabet %58 · +0.64 |  |
| uyumsuzluk (SAT+AL) · a+b · 72 s | 13 · yön %54 · isabet %54 · +0.92 | 7 · yön %14 · isabet %14 · -4.48 | 32 · yön %59 · isabet %56 · +0.88 |  |
| yalnız negatif → SAT · a+b · 72 s | 12 · yön %50 · isabet %50 · +0.07 | 4 · yön %25 · isabet %25 · -3.77 | 24 · yön %54 · isabet %50 · -0.10 |  |
| uyumsuzluk (SAT+AL) · a+b+c · 72 s | 8 · yön %62 · isabet %62 · +1.98 | 1 · yön %0 · isabet %0 · -5.67 | 20 · yön %60 · isabet %60 · +1.44 |  |
| yalnız negatif → SAT · a+b+c · 72 s | 7 · yön %57 · isabet %57 · +0.69 | 0 | 14 · yön %50 · isabet %50 · +0.38 |  |

**Z2: yön şartı ✅ 0 / 24 · sinyal adayı 0** · plasebo (zaman kaydırma ×20) ortalama 0.0, en çok 0

## Z3 — Büyük hareketin yönü modeli (yalnız büyük hareket saatlerinde eğitilir; işlem P içinde)
| kural | K | C1 2024 | C2 2025–26 | |
|---|---|---|---|---|
| büyük hareket yön modeli · 4 s · P içinde | 109 · yön %47 · isabet %32 · -0.22 | 19 · yön %58 · isabet %42 · +0.15 | 125 · yön %54 · isabet %48 · +0.02 |  | ‖ limit emirle net: -0.06 · +0.31 · +0.18
| PLASEBO büyük hareket yön modeli · 4 s · P içinde | 217 · yön %47 · isabet %29 · -0.45 | 141 · yön %50 · isabet %43 · -0.14 | 304 · yön %49 · isabet %37 · -0.28 |  |

## Z4 — Günlük bileşik skor (btcyon Y1) yalnız trend yönünde
| kural | K | C1 2024 | C2 2025–26 | |
|---|---|---|---|---|
| skor 1 g · yalnız trend yönünde | 125 · yön %55 · isabet %52 · +0.78 | 40 · yön %48 · isabet %38 · -0.31 | 124 · yön %50 · isabet %44 · +0.13 |  |
| skor 3 g · yalnız trend yönünde | 56 · yön %59 · isabet %55 · +2.59 | 13 · yön %31 · isabet %31 · -1.89 | 55 · yön %65 · isabet %62 · +0.59 |  |
| skor 7 g · yalnız trend yönünde | 41 · yön %61 · isabet %59 · +4.37 | 11 · yön %27 · isabet %27 · -2.52 | 35 · yön %57 · isabet %54 · +0.80 |  |

**Z4: yön şartı ✅ 0 / 3 · sinyal adayı 0** · plasebo (zaman kaydırma ×20) ortalama 0.0, en çok 0

## Özet
- Z1: 4 kural · yön ✅ 0 · sinyal adayı 🎯 0
- Z1p: 4 kural · yön ✅ 0 · sinyal adayı 🎯 0
- Z2: 24 kural · yön ✅ 0 · sinyal adayı 🎯 0
- Z3: 1 kural · yön ✅ 0 · sinyal adayı 🎯 0
- Z3p: 1 kural · yön ✅ 0 · sinyal adayı 🎯 0
- Z4: 3 kural · yön ✅ 0 · sinyal adayı 🎯 0

_süre 451 sn_
