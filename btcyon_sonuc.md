# 🧭 BTC'nin YÖNÜ — PROTOKOL_btcyon.md
_30.10.2026 21:29 · hücre: işlem · yön isabeti (fiyat tahmin yönünde gitti) · isabet (masraf sonrası kâr) · işlem başı net % · ✅ yön şartı (her dönemde yön ≥ %57, net > 0) · 🎯 sinyal adayı_

## Y1 — Bileşik yön skoru (günlük, D−1 sonunda bilinen 19 durum)
| kural | K 2022–23 | C1 2024 | C2 2025–26 | |
|---|---|---|---|---|
| skor 1 g (K ile eğitim; C2 için K+C1) | 292 · yön %55 · isabet %52 · +0.61 | 143 · yön %46 · isabet %44 · -0.09 | 202 · yön %50 · isabet %45 · +0.03 |  |
| skor 3 g (K ile eğitim; C2 için K+C1) | 138 · yön %51 · isabet %47 · -1.16 | 71 · yön %58 · isabet %54 · +0.07 | 143 · yön %52 · isabet %49 · -0.34 |  |
| skor 7 g (K ile eğitim; C2 için K+C1) | 68 · yön %53 · isabet %51 · -0.13 | 40 · yön %48 · isabet %48 · -0.16 | 70 · yön %51 · isabet %51 · -0.20 |  |

_K'de 3 g modelinin en ağır 6 durumu (katsayı, baz puan / 1 std): fimb3 -99, fon3 +55, zirve30 -54, r7 -49, dvol3 +33, prim_d3 -26_
| oy kuralı 1 g (BİLGİ — yönler tüm dönemler görülerek seçildi) | 89 · yön %44 · isabet %38 · +0.32 | 31 · yön %48 · isabet %42 · +0.23 | 59 · yön %54 · isabet %49 · +0.06 |  |
| oy kuralı 3 g (BİLGİ — yönler tüm dönemler görülerek seçildi) | 49 · yön %47 · isabet %45 · +1.23 | 17 · yön %59 · isabet %59 · +0.74 | 31 · yön %55 · isabet %55 · +0.44 |  |
| oy kuralı 7 g (BİLGİ — yönler tüm dönemler görülerek seçildi) | 35 · yön %51 · isabet %51 · +1.96 | 12 · yön %67 · isabet %67 · +1.21 | 24 · yön %62 · isabet %62 · -0.21 |  |

**Y1: yön şartını geçen 0 / 3 · sinyal adayı 0** · plasebo (rastgele zaman kaydırma ×20) ortalama 0.0, en çok 0

## Y2 — Hareketi kim sürdü → devam mı, dönüş mü?
_K'de her sınıf için ortalama sonraki getiri (hareket yönünde, %) → seçilen yön; sonra test_

| kural | K 2022–23 | C1 2024 | C2 2025–26 | |
|---|---|---|---|---|
| 4 s düşüş · T tasfiye · 4 s · DEVAM (K ort. +0.13, n 31) | 31 · yön %45 · isabet %39 · -0.09 | 19 · yön %37 · isabet %32 · -0.24 | 15 · yön %33 · isabet %20 · -0.48 |  |
| 4 s düşüş · T tasfiye · 24 s · DÖNÜŞ (K ort. -0.20, n 31) | 30 · yön %57 · isabet %53 · +0.28 | 18 · yön %61 · isabet %61 · +1.44 | 14 · yön %64 · isabet %64 · +0.91 |  |
| 4 s düşüş · T tasfiye · 72 s · DÖNÜŞ (K ort. -0.05, n 31) | 29 · yön %55 · isabet %55 · +0.22 | 18 · yön %67 · isabet %67 · +1.93 | 11 · yön %36 · isabet %27 · -2.57 |  |
| 4 s düşüş · L yeni kaldıraç · 4 s · DEVAM (K ort. +0.96, n 9) | 9 · yön %78 · isabet %67 · +0.75 | 7 · yön %29 · isabet %29 · -0.87 | 18 · yön %50 · isabet %39 · -0.46 |  |
| 4 s düşüş · L yeni kaldıraç · 24 s · DEVAM (K ort. +0.24, n 9) | 8 · yön %38 · isabet %38 · +0.28 | 7 · yön %43 · isabet %43 · +0.18 | 18 · yön %44 · isabet %44 · -0.04 |  |
| 4 s düşüş · L yeni kaldıraç · 72 s · DÖNÜŞ (K ort. -1.17, n 9) | 8 · yön %62 · isabet %62 · +1.45 | 7 · yön %43 · isabet %43 · -1.21 | 17 · yön %65 · isabet %65 · +0.19 |  |
| 4 s düşüş · S spot/ABD sürdü · 4 s · DEVAM (K ort. +0.13, n 12) | 12 · yön %50 · isabet %42 · -0.08 | 5 · yön %60 · isabet %60 · +0.16 | 14 · yön %50 · isabet %43 · -0.07 |  |
| 4 s düşüş · S spot/ABD sürdü · 24 s · DEVAM (K ort. +2.07, n 12) | 10 · yön %50 · isabet %50 · +0.40 | 5 · yön %20 · isabet %20 · -1.64 | 14 · yön %50 · isabet %50 · -0.85 |  |
| 4 s düşüş · S spot/ABD sürdü · 72 s · DEVAM (K ort. +2.70, n 12) | 9 · yön %67 · isabet %67 · +0.60 | 5 · yön %20 · isabet %20 · -1.90 | 14 · yön %43 · isabet %43 · -1.12 |  |
| 4 s düşüş · D diğer · 4 s · DÖNÜŞ (K ort. -0.63, n 23) | 23 · yön %61 · isabet %57 · +0.45 | 6 · yön %67 · isabet %67 · +0.34 | 29 · yön %38 · isabet %31 · -0.62 |  |
| 4 s düşüş · D diğer · 24 s · DÖNÜŞ (K ort. -0.47, n 23) | 22 · yön %45 · isabet %45 · -0.15 | 5 · yön %60 · isabet %60 · -0.18 | 27 · yön %56 · isabet %52 · -0.14 |  |
| 4 s düşüş · D diğer · 72 s · DÖNÜŞ (K ort. -0.92, n 23) | 20 · yön %60 · isabet %55 · +0.37 | 5 · yön %60 · isabet %60 · -0.11 | 26 · yön %62 · isabet %54 · +1.08 |  |
| 4 s yükseliş · T tasfiye · 4 s · DEVAM (K ort. +0.25, n 24) | 24 · yön %50 · isabet %46 · +0.07 | 9 · yön %67 · isabet %56 · +0.26 | 11 · yön %45 · isabet %45 · -0.19 |  |
| 4 s yükseliş · T tasfiye · 24 s · DEVAM (K ort. +1.08, n 24) | 21 · yön %67 · isabet %67 · +1.03 | 7 · yön %57 · isabet %57 · +0.53 | 11 · yön %55 · isabet %55 · -1.17 |  |
| 4 s yükseliş · T tasfiye · 72 s · DEVAM (K ort. +2.32, n 24) | 20 · yön %60 · isabet %55 · +1.81 | 7 · yön %57 · isabet %57 · +0.24 | 9 · yön %67 · isabet %67 · +0.70 |  |
| 4 s yükseliş · L yeni kaldıraç · 4 s · DEVAM (K ort. +0.48, n 18) | 18 · yön %67 · isabet %67 · +0.28 | 15 · yön %47 · isabet %40 · -0.28 | 20 · yön %45 · isabet %45 · +0.05 |  |
| 4 s yükseliş · L yeni kaldıraç · 24 s · DEVAM (K ort. +1.80, n 18) | 18 · yön %50 · isabet %44 · +1.71 | 15 · yön %60 · isabet %60 · -0.32 | 20 · yön %50 · isabet %45 · -0.51 |  |
| 4 s yükseliş · L yeni kaldıraç · 72 s · DEVAM (K ort. +1.89, n 18) | 16 · yön %56 · isabet %56 · +1.17 | 14 · yön %86 · isabet %86 · +1.80 | 17 · yön %47 · isabet %47 · +0.44 |  |
| 4 s yükseliş · S spot/ABD sürdü · 4 s · DEVAM (K ort. +0.37, n 13) | 13 · yön %54 · isabet %38 · +0.18 | 15 · yön %53 · isabet %40 · -0.32 | 14 · yön %50 · isabet %43 · -0.14 |  |
| 4 s yükseliş · S spot/ABD sürdü · 24 s · DÖNÜŞ (K ort. -0.38, n 13) | 11 · yön %36 · isabet %36 · +0.11 | 14 · yön %21 · isabet %21 · -1.50 | 14 · yön %36 · isabet %36 · -0.73 |  |
| 4 s yükseliş · S spot/ABD sürdü · 72 s · DEVAM (K ort. +0.30, n 13) | 11 · yön %64 · isabet %64 · +0.22 | 13 · yön %54 · isabet %46 · +1.03 | 14 · yön %43 · isabet %43 · +0.01 |  |
| 4 s yükseliş · D diğer · 4 s · DÖNÜŞ (K ort. -0.10, n 20) | 20 · yön %40 · isabet %40 · -0.13 | 5 · yön %40 · isabet %20 · -0.20 | 13 · yön %38 · isabet %38 · -0.43 |  |
| 4 s yükseliş · D diğer · 24 s · DEVAM (K ort. +0.35, n 20) | 20 · yön %50 · isabet %40 · +0.20 | 5 · yön %100 · isabet %100 · +3.01 | 13 · yön %54 · isabet %46 · +0.12 |  |
| 4 s yükseliş · D diğer · 72 s · DEVAM (K ort. +1.20, n 20) | 19 · yön %63 · isabet %63 · +1.46 | 4 · yön %100 · isabet %100 · +6.06 | 13 · yön %62 · isabet %62 · +1.04 |  |
| büyük gün düşüş 💥 · 1 g · DEVAM (K ort. +2.01, n 10) | 10 · yön %60 · isabet %60 · +1.69 | 3 · yön %0 · isabet %0 · -3.65 | 3 · yön %67 · isabet %67 · +0.78 |  |
| büyük gün düşüş 💥 · 3 g · DÖNÜŞ (K ort. -0.63, n 10) | 10 · yön %60 · isabet %50 · +0.52 | 3 · yön %100 · isabet %100 · +7.55 | 3 · yön %67 · isabet %67 · +0.67 |  |
| büyük gün düşüş 💥 · 7 g · DÖNÜŞ (K ort. -1.54, n 10) | 10 · yön %50 · isabet %50 · +1.62 | 3 · yön %100 · isabet %100 · +9.72 | 3 · yön %0 · isabet %0 · -9.01 |  |
| büyük gün düşüş 🎰 · 1 g · DÖNÜŞ (K ort. -3.65, n 4) | 4 · yön %75 · isabet %75 · +3.66 | 0 | 2 · yön %50 · isabet %50 · -1.20 |  |
| büyük gün düşüş 🎰 · 3 g · DÖNÜŞ (K ort. -0.56, n 4) | 4 · yön %75 · isabet %75 · +0.49 | 0 | 2 · yön %50 · isabet %50 · -3.32 |  |
| büyük gün düşüş 🎰 · 7 g · DEVAM (K ort. +3.58, n 4) | 4 · yön %25 · isabet %25 · +2.71 | 0 | 2 · yön %50 · isabet %50 · +2.33 |  |
| büyük gün düşüş 🇺🇸 · 1 g · DÖNÜŞ (K ort. -3.49, n 3) | 3 · yön %67 · isabet %67 · +3.51 | 5 · yön %80 · isabet %60 · +2.79 | 8 · yön %50 · isabet %50 · -0.73 |  |
| büyük gün düşüş 🇺🇸 · 3 g · DÖNÜŞ (K ort. -4.36, n 3) | 3 · yön %100 · isabet %100 · +4.29 | 5 · yön %60 · isabet %60 · +1.12 | 7 · yön %43 · isabet %43 · -3.69 |  |
| büyük gün düşüş 🇺🇸 · 7 g · DÖNÜŞ (K ort. -2.21, n 3) | 3 · yön %67 · isabet %67 · +2.05 | 4 · yön %50 · isabet %50 · +4.14 | 6 · yön %33 · isabet %33 · -8.03 |  |
| büyük gün düşüş 🏛️ · 1 g · DEVAM (K ort. +0.51, n 10) | 10 · yön %60 · isabet %50 · +0.29 | 4 · yön %50 · isabet %50 · -1.01 | 9 · yön %44 · isabet %44 · -1.49 |  |
| büyük gün düşüş 🏛️ · 3 g · DEVAM (K ort. +2.55, n 10) | 9 · yön %67 · isabet %67 · +2.90 | 4 · yön %50 · isabet %50 · -1.59 | 9 · yön %11 · isabet %11 · -3.02 |  |
| büyük gün düşüş 🏛️ · 7 g · DEVAM (K ort. +4.16, n 10) | 7 · yön %86 · isabet %86 · +5.51 | 3 · yön %67 · isabet %67 · -3.24 | 9 · yön %33 · isabet %33 · -1.61 |  |
| büyük gün düşüş 🪙 · 1 g · DEVAM (K ort. +0.52, n 4) | 4 · yön %50 · isabet %50 · +0.29 | 1 · yön %0 · isabet %0 · -3.86 | 6 · yön %33 · isabet %33 · -1.95 |  |
| büyük gün düşüş 🪙 · 3 g · DEVAM (K ort. +3.62, n 4) | 4 · yön %75 · isabet %75 · +3.29 | 1 · yön %0 · isabet %0 · -6.81 | 6 · yön %33 · isabet %33 · -1.52 |  |
| büyük gün düşüş 🪙 · 7 g · DEVAM (K ort. +3.17, n 4) | 4 · yön %75 · isabet %75 · +2.84 | 1 · yön %0 · isabet %0 · -11.48 | 5 · yön %40 · isabet %40 · +1.92 |  |
| büyük gün yükseliş 💥 · 1 g · DEVAM (K ort. +0.44, n 6) | 6 · yön %33 · isabet %33 · +0.32 | 2 · yön %0 · isabet %0 · -2.21 | 2 · yön %50 · isabet %50 · -0.76 |  |
| büyük gün yükseliş 💥 · 3 g · DEVAM (K ort. +0.39, n 6) | 6 · yön %67 · isabet %67 · +0.27 | 2 · yön %0 · isabet %0 · -3.25 | 2 · yön %50 · isabet %50 · +0.27 |  |
| büyük gün yükseliş 💥 · 7 g · DEVAM (K ort. +6.48, n 6) | 5 · yön %60 · isabet %60 · +8.09 | 2 · yön %50 · isabet %50 · +0.66 | 2 · yön %50 · isabet %50 · -0.56 |  |
| büyük gün yükseliş 🎰 · 1 g · DEVAM (K ort. +0.67, n 5) | 5 · yön %60 · isabet %60 · +0.52 | 4 · yön %25 · isabet %25 · -2.64 | 1 · yön %0 · isabet %0 · -2.20 |  |
| büyük gün yükseliş 🎰 · 3 g · DEVAM (K ort. +1.15, n 5) | 5 · yön %60 · isabet %60 · +1.03 | 4 · yön %50 · isabet %50 · -0.58 | 1 · yön %0 · isabet %0 · -1.37 |  |
| büyük gün yükseliş 🎰 · 7 g · DEVAM (K ort. +1.19, n 5) | 5 · yön %40 · isabet %40 · +1.20 | 4 · yön %75 · isabet %75 · +4.48 | 1 · yön %0 · isabet %0 · -6.06 |  |
| büyük gün yükseliş 🏛️ · 1 g · DÖNÜŞ (K ort. -0.53, n 5) | 5 · yön %60 · isabet %60 · +0.25 | 5 · yön %80 · isabet %80 · +1.37 | 8 · yön %75 · isabet %75 · +0.16 |  |
| büyük gün yükseliş 🏛️ · 3 g · DÖNÜŞ (K ort. -1.78, n 5) | 5 · yön %60 · isabet %60 · +1.34 | 5 · yön %60 · isabet %60 · +1.72 | 8 · yön %62 · isabet %62 · -0.51 |  |
| büyük gün yükseliş 🏛️ · 7 g · DEVAM (K ort. +0.18, n 5) | 5 · yön %40 · isabet %40 · +0.12 | 5 · yön %60 · isabet %60 · +1.68 | 8 · yön %38 · isabet %38 · -1.34 |  |
| büyük gün yükseliş ❓ · 1 g · DEVAM (K ort. +0.30, n 11) | 11 · yön %36 · isabet %36 · +0.12 | 3 · yön %100 · isabet %100 · +4.94 | 8 · yön %38 · isabet %25 · -1.10 |  |
| büyük gün yükseliş ❓ · 3 g · DEVAM (K ort. +0.85, n 11) | 10 · yön %60 · isabet %60 · +0.69 | 3 · yön %67 · isabet %67 · +7.45 | 8 · yön %50 · isabet %50 · -1.14 |  |
| büyük gün yükseliş ❓ · 7 g · DÖNÜŞ (K ort. -0.99, n 11) | 10 · yön %60 · isabet %60 · +0.27 | 3 · yön %0 · isabet %0 · -13.57 | 8 · yön %38 · isabet %38 · +0.69 |  |

**Y2: yön şartını geçen 0 / 51 · sinyal adayı 0** · plasebo (rastgele zaman kaydırma ×20) ortalama 0.0, en çok 0

## Y3 — ABD seansının yönü (13:00 → 21:00 UTC = TR 16:00 → 24:00, hafta içi)
_bilgi — seansların ortalama getirisi % ve yükselen gün oranı (hafta içi):_
- K 2022–23: Asya 00→08 -0.021 (%46) · Avrupa 08→13 +0.040 (%53) · **ABD 13→21 -0.059 (%46)** · gece 21→24 +0.019 (%54)
- C1 2024: Asya 00→08 +0.038 (%56) · Avrupa 08→13 +0.090 (%55) · **ABD 13→21 +0.034 (%52)** · gece 21→24 +0.083 (%56)
- C2 2025–26: Asya 00→08 -0.029 (%51) · Avrupa 08→13 +0.032 (%52) · **ABD 13→21 -0.056 (%50)** · gece 21→24 +0.019 (%50)

| kural | K 2022–23 | C1 2024 | C2 2025–26 | |
|---|---|---|---|---|
| 00→13 getiri alt %20 → SAT (K ort. -0.012) | 104 · yön %50 · isabet %47 · -0.23 | 47 · yön %45 · isabet %38 · -0.40 | 98 · yön %51 · isabet %48 · -0.09 |  |
| 00→13 getiri üst %20 → SAT (K ort. -0.056) | 104 · yön %57 · isabet %43 · -0.17 | 67 · yön %31 · isabet %30 · -0.74 | 91 · yön %49 · isabet %43 · -0.13 |  |
| Coinbase primi 00→13 değişim alt %20 → AL (K ort. +0.216) | 104 · yön %40 · isabet %37 · +0.05 | 74 · yön %42 · isabet %38 · -0.65 | 65 · yön %43 · isabet %40 · -0.55 |  |
| Coinbase primi 00→13 değişim üst %20 → SAT (K ort. -0.221) | 104 · yön %51 · isabet %45 · -0.00 | 62 · yön %45 · isabet %45 · -0.49 | 96 · yön %45 · isabet %40 · -0.29 |  |
| Coinbase primi z (12:00) alt %20 → SAT (K ort. -0.246) | 104 · yön %62 · isabet %55 · +0.01 | 59 · yön %49 · isabet %41 · +0.07 | 102 · yön %57 · isabet %50 · +0.03 |  |
| Coinbase primi z (12:00) üst %20 → SAT (K ort. -0.202) | 104 · yön %58 · isabet %50 · -0.02 | 62 · yön %45 · isabet %42 · -0.29 | 125 · yön %50 · isabet %45 · -0.29 |  |
| vadeli agresif 00→13 alt %20 → SAT (K ort. -0.406) | 104 · yön %55 · isabet %46 · +0.19 | 65 · yön %54 · isabet %46 · +0.00 | 141 · yön %48 · isabet %40 · -0.18 |  |
| vadeli agresif 00→13 üst %20 → SAT (K ort. -0.024) | 104 · yön %55 · isabet %43 · -0.19 | 40 · yön %40 · isabet %38 · -0.12 | 93 · yön %52 · isabet %45 · -0.21 |  |
| spot agresif 00→13 alt %20 → SAT (K ort. -0.038) | 104 · yön %55 · isabet %43 · -0.18 | 68 · yön %50 · isabet %41 · -0.30 | 183 · yön %50 · isabet %45 · -0.14 |  |
| spot agresif 00→13 üst %20 → SAT (K ort. -0.523) | 104 · yön %61 · isabet %53 · +0.31 | 84 · yön %43 · isabet %40 · -0.28 | 155 · yön %46 · isabet %42 · -0.24 |  |
| açık poz. 00→13 alt %20 → SAT (K ort. -0.007) | 104 · yön %51 · isabet %43 · -0.22 | 49 · yön %43 · isabet %35 · -0.63 | 157 · yön %55 · isabet %49 · -0.00 |  |
| açık poz. 00→13 üst %20 → SAT (K ort. -0.537) | 104 · yön %62 · isabet %52 · +0.31 | 36 · yön %53 · isabet %47 · +0.14 | 32 · yön %41 · isabet %34 · -0.25 |  |
| fonlama alt %20 → AL (K ort. +0.013) | 104 · yön %48 · isabet %38 · -0.15 | 21 · yön %71 · isabet %71 · +0.55 | 81 · yön %48 · isabet %42 · -0.24 |  |
| fonlama üst %20 → SAT (K ort. -0.493) | 13 · yön %62 · isabet %62 · +0.30 | 56 · yön %54 · isabet %48 · -0.30 | 0 |  |
| önceki gün ETF akışı z alt %20 → AL (K ort. +0.370) | 0 | 45 · yön %56 · isabet %53 · +0.20 | 91 · yön %51 · isabet %41 · -0.34 |  |
| önceki gün ETF akışı z üst %20 → AL (K ort. +0.235) | 0 | 44 · yön %61 · isabet %59 · +0.04 | 102 · yön %58 · isabet %53 · +0.02 |  |
| önceki gün Nasdaq alt %20 → AL (K ort. +0.278) | 104 · yön %54 · isabet %45 · +0.11 | 25 · yön %64 · isabet %56 · +0.29 | 59 · yön %56 · isabet %56 · +0.20 |  |
| önceki gün Nasdaq üst %20 → SAT (K ort. -0.319) | 104 · yön %61 · isabet %55 · +0.10 | 28 · yön %57 · isabet %54 · +0.16 | 58 · yön %47 · isabet %38 · -0.25 |  |
| önceki gün dolar alt %20 → SAT (K ort. -0.176) | 104 · yön %55 · isabet %45 · -0.06 | 33 · yön %52 · isabet %42 · -0.63 | 77 · yön %47 · isabet %42 · -0.36 |  |
| önceki gün dolar üst %20 → SAT (K ort. -0.135) | 103 · yön %58 · isabet %50 · -0.08 | 29 · yön %45 · isabet %34 · -0.12 | 49 · yön %49 · isabet %41 · -0.17 |  |
| önceki ABD seansı alt %20 → AL (K ort. +0.276) | 104 · yön %57 · isabet %46 · +0.10 | 56 · yön %64 · isabet %62 · +0.36 | 75 · yön %57 · isabet %53 · -0.11 |  |
| önceki ABD seansı üst %20 → SAT (K ort. -0.226) | 104 · yön %53 · isabet %48 · +0.01 | 65 · yön %49 · isabet %49 · +0.13 | 86 · yön %48 · isabet %43 · -0.21 |  |
| bileşik ABD seansı skoru (ridge) | 208 · yön %56 · isabet %50 · +0.47 | 115 · yön %56 · isabet %51 · +0.35 | 228 · yön %47 · isabet %43 · -0.16 |  |

**Y3: yön şartını geçen 0 / 23 · sinyal adayı 0** · plasebo (rastgele zaman kaydırma ×20) ortalama 0.0, en çok 0

## Y4 — Hafta sonu ve CME boşluğu
_hafta içinde fiyatın cuma 21:00 seviyesine geri dönme oranı (boşluk büyüklüğüne göre):_
| |boşluk| | K 2022–23 | C1 2024 | C2 2025–26 |
|---|---|---|---|
| %0.0–%0 | %95 (38) | %92 (13) | %94 (31) |
| %0.5–%1 | %100 (14) | %90 (10) | %100 (19) |
| %1.0–%2 | %81 (27) | %76 (17) | %90 (20) |
| %2.0–%3 | %44 (9) | %80 (5) | %83 (12) |
| %3.0–… | %50 (16) | %29 (7) | %67 (12) |

| kural | K 2022–23 | C1 2024 | C2 2025–26 | |
|---|---|---|---|---|
| boşluk ≥ %1 → F'ye doğru · 🎯 F · stop yok | 53 · yön %70 · isabet %72 · -0.89 | 29 · yön %66 · isabet %66 · -0.83 | 44 · yön %82 · isabet %84 · +1.13 |  |
| boşluk ≥ %1 → F'ye doğru · 🎯 F · stop boşluk kadar | 53 · yön %32 · isabet %28 · -1.01 | 29 · yön %41 · isabet %41 · -0.87 | 44 · yön %59 · isabet %57 · +0.58 |  |
- K 2022–23: cuma ABD seansı ile hafta sonu aynı yönde %50 · hafta sonu ile pazartesi aynı yönde %50 (n 104)
- C1 2024: cuma ABD seansı ile hafta sonu aynı yönde %46 · hafta sonu ile pazartesi aynı yönde %54 (n 52)
- C2 2025–26: cuma ABD seansı ile hafta sonu aynı yönde %46 · hafta sonu ile pazartesi aynı yönde %47 (n 94)

## Y5 — Makine öğrenmesi yön modeli (LightGBM, aylık yürüyen eğitim)
| kural | K 2022–23 | C1 2024 | C2 2025–26 | |
|---|---|---|---|---|
| model 4 s (yalnız 2023 K'de) | 675 · yön %62 · isabet %40 · -0.16 | 799 · yön %58 · isabet %45 · -0.11 | 1163 · yön %51 · isabet %37 · -0.22 |  |
| PLASEBO model 4 s (yalnız 2023 K'de) | 414 · yön %50 · isabet %31 · -0.20 | 420 · yön %53 · isabet %40 · -0.15 | 814 · yön %51 · isabet %39 · -0.17 |  |
| model 24 s (yalnız 2023 K'de) | 61 · yön %67 · isabet %54 · +0.20 | 86 · yön %53 · isabet %50 · -0.14 | 100 · yön %53 · isabet %46 · -0.08 |  |
| PLASEBO model 24 s (yalnız 2023 K'de) | 199 · yön %51 · isabet %43 · -0.23 | 195 · yön %48 · isabet %42 · -0.45 | 344 · yön %49 · isabet %44 · -0.22 |  |

## Y6 — Öncü coin ve akış (son saat → BTC'nin sonraki 1 s / 4 s)
| kural | K 2022–23 | C1 2024 | C2 2025–26 | |
|---|---|---|---|---|
| ETH son saat alt %20 → 1 s SAT | 3504 · yön %44 · isabet %29 · -0.20 | 1906 · yön %44 · isabet %26 · -0.24 | 3442 · yön %48 · isabet %28 · -0.19 |  |
| ETH son saat üst %20 → 1 s AL | 3503 · yön %45 · isabet %28 · -0.20 | 1970 · yön %45 · isabet %27 · -0.21 | 3472 · yön %48 · isabet %26 · -0.20 |  |
| SOL son saat alt %20 → 1 s AL | 3480 · yön %56 · isabet %34 · -0.20 | 1658 · yön %54 · isabet %36 · -0.20 | 2262 · yön %52 · isabet %32 · -0.20 |  |
| SOL son saat üst %20 → 1 s AL | 3479 · yön %48 · isabet %27 · -0.18 | 1720 · yön %45 · isabet %28 · -0.21 | 2272 · yön %49 · isabet %29 · -0.19 |  |
| ETH − BTC son saat alt %20 → 1 s SAT | 3504 · yön %49 · isabet %32 · -0.19 | 2267 · yön %48 · isabet %29 · -0.21 | 3650 · yön %49 · isabet %28 · -0.19 |  |
| ETH − BTC son saat üst %20 → 1 s AL | 3503 · yön %50 · isabet %30 · -0.18 | 2045 · yön %51 · isabet %30 · -0.19 | 3636 · yön %50 · isabet %27 · -0.19 |  |
| Coinbase primi son saat Δ alt %20 → 1 s SAT | 3504 · yön %50 · isabet %28 · -0.19 | 1879 · yön %51 · isabet %31 · -0.18 | 2258 · yön %49 · isabet %27 · -0.20 |  |
| Coinbase primi son saat Δ üst %20 → 1 s AL | 3502 · yön %51 · isabet %29 · -0.19 | 1848 · yön %52 · isabet %33 · -0.17 | 2206 · yön %50 · isabet %27 · -0.19 |  |
| vadeli agresif son saat alt %20 → 1 s AL | 3503 · yön %57 · isabet %27 · -0.18 | 2141 · yön %55 · isabet %30 · -0.18 | 4399 · yön %51 · isabet %24 · -0.21 |  |
| vadeli agresif son saat üst %20 → 1 s SAT | 3504 · yön %56 · isabet %26 · -0.19 | 1759 · yön %53 · isabet %28 · -0.20 | 3967 · yön %52 · isabet %23 · -0.20 |  |
| spot agresif son saat alt %20 → 1 s AL | 3503 · yön %57 · isabet %26 · -0.18 | 2745 · yön %55 · isabet %30 · -0.18 | 6060 · yön %52 · isabet %25 · -0.19 |  |
| spot agresif son saat üst %20 → 1 s SAT | 3504 · yön %54 · isabet %28 · -0.19 | 2920 · yön %53 · isabet %30 · -0.20 | 5672 · yön %51 · isabet %25 · -0.20 |  |
| ETH son saat alt %20 → 4 s SAT | 2054 · yön %47 · isabet %37 · -0.21 | 1136 · yön %45 · isabet %36 · -0.26 | 2006 · yön %48 · isabet %36 · -0.20 |  |
| ETH son saat üst %20 → 4 s AL | 2050 · yön %48 · isabet %37 · -0.17 | 1162 · yön %48 · isabet %38 · -0.18 | 2045 · yön %50 · isabet %36 · -0.21 |  |
| SOL son saat alt %20 → 4 s SAT | 2073 · yön %47 · isabet %35 · -0.20 | 1022 · yön %46 · isabet %37 · -0.25 | 1482 · yön %48 · isabet %36 · -0.20 |  |
| SOL son saat üst %20 → 4 s AL | 2067 · yön %49 · isabet %36 · -0.15 | 1058 · yön %51 · isabet %40 · -0.14 | 1458 · yön %51 · isabet %38 · -0.18 |  |
| ETH − BTC son saat alt %20 → 4 s SAT | 2047 · yön %50 · isabet %39 · -0.20 | 1249 · yön %47 · isabet %37 · -0.25 | 2074 · yön %49 · isabet %36 · -0.21 |  |
| ETH − BTC son saat üst %20 → 4 s SAT | 2064 · yön %49 · isabet %37 · -0.21 | 1171 · yön %48 · isabet %37 · -0.23 | 2059 · yön %49 · isabet %35 · -0.21 |  |
| Coinbase primi son saat Δ alt %20 → 4 s SAT | 2282 · yön %50 · isabet %37 · -0.19 | 1191 · yön %48 · isabet %38 · -0.23 | 1683 · yön %48 · isabet %33 · -0.21 |  |
| Coinbase primi son saat Δ üst %20 → 4 s SAT | 2286 · yön %49 · isabet %36 · -0.21 | 1188 · yön %45 · isabet %36 · -0.28 | 1646 · yön %50 · isabet %36 · -0.21 |  |
| vadeli agresif son saat alt %20 → 4 s AL | 2154 · yön %54 · isabet %35 · -0.19 | 1261 · yön %53 · isabet %38 · -0.16 | 2399 · yön %51 · isabet %36 · -0.20 |  |
| vadeli agresif son saat üst %20 → 4 s SAT | 2219 · yön %54 · isabet %37 · -0.19 | 1109 · yön %51 · isabet %36 · -0.22 | 2236 · yön %51 · isabet %34 · -0.19 |  |
| spot agresif son saat alt %20 → 4 s AL | 1751 · yön %53 · isabet %36 · -0.19 | 1342 · yön %53 · isabet %40 · -0.15 | 2705 · yön %53 · isabet %37 · -0.19 |  |
| spot agresif son saat üst %20 → 4 s AL | 1998 · yön %47 · isabet %34 · -0.21 | 1421 · yön %51 · isabet %38 · -0.15 | 2601 · yön %50 · isabet %35 · -0.20 |  |

**Y6: yön şartını geçen 0 / 24 · sinyal adayı 0** · plasebo (rastgele zaman kaydırma ×10) ortalama 0.0, en çok 0

## Özet
- Y1: 3 kural · yön şartı ✅ 0 · sinyal adayı 🎯 0
- Y2: 51 kural · yön şartı ✅ 0 · sinyal adayı 🎯 0
- Y3: 23 kural · yön şartı ✅ 0 · sinyal adayı 🎯 0
- Y4: 2 kural · yön şartı ✅ 0 · sinyal adayı 🎯 0
- Y5: 2 kural · yön şartı ✅ 0 · sinyal adayı 🎯 0
- Y5p: 2 kural · yön şartı ✅ 0 · sinyal adayı 🎯 0
- Y6: 24 kural · yön şartı ✅ 0 · sinyal adayı 🎯 0

_süre 926 sn_
