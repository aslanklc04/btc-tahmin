# 🎯 Haftada ~45 sinyal: isabet ve kâr için seçim — 11.10.2026 14:58
Olay: 56,802 · tip: 25 · 168 sn

# 🔀 Coin primi vs BTC primi + sessiz günü olmayan sinyal seti — 11.10.2026 14:58
_Coin sinyalleri: 🤝 BTC ile ortak · 🔇 BTC sessizken · coin tek başına · 🧪 24 saat (BTC hariç). Hücre: haftada · isabet · işlem başı net % (komisyon sonrası) · alt = haftalık blok %5 alt sınır_

## 1) Coin ve BTC primi aynı yönde mi, zıt yönde mi?
```
ikisi de alıyor (coin z>0, BTC z>0)
   2022-06→2023   27.8/hf · %57.2 · +0.186 (alt +0.02)
   2024+          27.9/hf · %60.4 · +0.448 (alt +0.27)
   2026           33.3/hf · %59.1 · +0.293 (alt +0.05)
ABD coin'i alıyor, BTC'yi satıyor (coin z>0, BTC z≤0)
   2022-06→2023    7.6/hf · %61.1 · +0.542 (alt +0.12)
   2024+          10.5/hf · %60.2 · +0.469 (alt +0.15)
   2026           10.1/hf · %66.2 · +0.746 (alt +0.40)
ABD coin'i satıyor, BTC'yi alıyor (coin z≤0, BTC z>0)
   2022-06→2023    7.5/hf · %60.5 · +0.313 (alt -0.20)
   2024+           8.0/hf · %57.9 · +0.390 (alt +0.08)
   2026            9.4/hf · %51.1 · +0.118 (alt -0.14)
ikisi de satıyor (coin z≤0, BTC z≤0)
   2022-06→2023   23.3/hf · %57.0 · +0.186 (alt -0.02)
   2024+          39.9/hf · %55.7 · -0.031 (alt -0.23)
   2026           39.4/hf · %53.6 · -0.056 (alt -0.34)
```
**Güçlü haller** (z ≥ 1 alıyor / z ≤ −1 satıyor):
```
coin güçlü alınıyor, BTC güçlü satılıyor (coin ≥1, BTC ≤−1)
   2022-06→2023    0.5/hf · %51.3 · -0.387 (alt -2.63)
   2024+           0.6/hf · %56.7 · -0.077 (alt -1.21)
   2026            0.7/hf · %46.4 · -0.545 (alt -1.28)
ikisi de güçlü alınıyor (≥1, ≥1)
   2022-06→2023    7.9/hf · %58.3 · +0.154 (alt -0.06)
   2024+           7.6/hf · %64.6 · +0.760 (alt +0.46)
   2026            9.9/hf · %59.0 · +0.229 (alt -0.30)
coin güçlü satılıyor, BTC güçlü alınıyor (≤−1, ≥1)
   2022-06→2023    0.3/hf · %68.2 · -0.933 (alt -3.71)
   2024+           0.4/hf · %50.9 · +1.455 (alt -0.40)
   2026            0.6/hf · %28.0 · -0.745 (alt -1.28)
ikisi de güçlü satılıyor (≤−1, ≤−1)
   2022-06→2023    6.7/hf · %53.3 · +0.311 (alt -0.09)
   2024+          16.0/hf · %54.5 · -0.031 (alt -0.29)
   2026           15.2/hf · %46.3 · -0.316 (alt -0.70)
```

## 2) Coin primi BTC priminden ne kadar yüksek? (fark = coin z − BTC z)
```
[tüm coin sinyalleri]
  fark ≤ -2     2022-06→2023:   1.5/hf · %45.5 · -0.856 | 2024+:   1.9/hf · %46.3 · +0.321 | 2026:   3.3/hf · %40.2 · -0.381
  fark -2…-1    2022-06→2023:   5.2/hf · %52.0 · +0.161 | 2024+:   5.4/hf · %54.5 · +0.148 | 2026:   7.4/hf · %57.8 · +0.264
  fark -1…0     2022-06→2023:  24.8/hf · %58.0 · +0.171 | 2024+:  28.6/hf · %59.2 · +0.291 | 2026:  31.2/hf · %58.7 · +0.204
  fark 0…1      2022-06→2023:  25.9/hf · %59.0 · +0.324 | 2024+:  36.8/hf · %57.8 · +0.181 | 2026:  36.6/hf · %54.7 · +0.078
  fark 1…2      2022-06→2023:   6.1/hf · %59.8 · +0.217 | 2024+:   9.7/hf · %57.5 · +0.125 | 2026:   9.2/hf · %60.9 · +0.476
  fark > 2      2022-06→2023:   2.8/hf · %61.4 · +0.882 | 2024+:   3.9/hf · %61.8 · +0.445 | 2026:   4.5/hf · %60.2 · +0.432
[yalnız coin z ≥ 0 olanlar]
  fark ≤ -2     2022-06→2023:   0.1/hf · %36.4 · -1.257 | 2024+:   0.4/hf · %59.3 · +0.819 | 2026:   0.9/hf · %56.8 · +0.076
  fark -2…-1    2022-06→2023:   1.3/hf · %43.3 · -0.029 | 2024+:   1.7/hf · %54.4 · +0.326 | 2026:   2.8/hf · %59.8 · +0.667
  fark -1…0     2022-06→2023:  12.5/hf · %56.4 · +0.057 | 2024+:  11.4/hf · %61.1 · +0.500 | 2026:  14.8/hf · %62.1 · +0.368
  fark 0…1      2022-06→2023:  15.6/hf · %60.2 · +0.427 | 2024+:  17.2/hf · %60.1 · +0.431 | 2026:  17.0/hf · %59.9 · +0.313
  fark 1…2      2022-06→2023:   4.0/hf · %60.6 · +0.281 | 2024+:   4.9/hf · %59.4 · +0.357 | 2026:   4.5/hf · %59.8 · +0.660
  fark > 2      2022-06→2023:   1.9/hf · %57.6 · +0.517 | 2024+:   2.8/hf · %64.5 · +0.605 | 2026:   3.4/hf · %62.0 · +0.483
[yalnız BTC z ≤ −1 iken (ABD BTC satıyor)]
  fark ≤ -2     2022-06→2023:   0.3/hf · %20.8 · -2.400 | 2024+:   0.0/hf · %33.3 · -1.195 | 2026:   0.1/hf · az örnek
  fark -2…-1    2022-06→2023:   0.2/hf · %57.1 · +0.734 | 2024+:   0.3/hf · %54.3 · +0.402 | 2026:   0.5/hf · %57.9 · -0.138
  fark -1…0     2022-06→2023:   2.4/hf · %52.5 · +0.170 | 2024+:   5.6/hf · %55.7 · +0.102 | 2026:   5.5/hf · %48.6 · -0.482
  fark 0…1      2022-06→2023:   4.7/hf · %52.5 · +0.197 | 2024+:  12.9/hf · %52.8 · -0.172 | 2026:  13.8/hf · %43.0 · -0.317
  fark 1…2      2022-06→2023:   2.9/hf · %58.2 · -0.000 | 2024+:   5.9/hf · %55.9 · -0.046 | 2026:   5.7/hf · %61.6 · +0.441
  fark > 2      2022-06→2023:   1.8/hf · %58.8 · +0.831 | 2024+:   2.9/hf · %60.9 · +0.253 | 2026:   3.4/hf · %58.8 · +0.435
```

## 3) Her gün sinyal: dolgu kuralları (son 24 saatte hiç sinyal gitmediyse bir sonraki 'dolgu' sinyali gönderilir)
_hücre: haftada · isabet · işlem başı net % · haftalık toplam % · sessiz gün % · en uzun sessizlik (saat) · dolgu sinyallerinin kendi net %'si_
```
R0 bugün (⛔ hariç hepsi): 2022-06→2023: 126/hf · %56.7 · +0.213 · sessiz gün %1 · en uzun 57 s | 2024+: 132/hf · %57.0 · +0.288 · sessiz gün %3 · en uzun 66 s | 2026: 137/hf · %56.4 · +0.288 · sessiz gün %1 · en uzun 45 s
R5 (BTC ve coin-tek yok, coin z ≥ 0) + dolgu yok
   2022-06→2023:   43/hf · %55.8 · +0.451 · top +19.2 · sessiz %11.1 · en uzun 202 s · dolgu 0.0/hf +nan
   2024+:   47/hf · %58.3 · +0.652 · top +30.9 · sessiz %11.7 · en uzun 251 s · dolgu 0.0/hf +nan
   2026:   51/hf · %58.7 · +0.605 · top +30.6 · sessiz %5.4 · en uzun 73 s · dolgu 0.0/hf +nan
R5 (BTC ve coin-tek yok, coin z ≥ 0) + F1 dolgu: R4 (BTC/coin-tek yok, ⛔ hariç)
   2022-06→2023:   43/hf · %55.8 · +0.445 · top +19.1 · sessiz %8.1 · en uzun 114 s · dolgu 0.4/hf -0.08
   2024+:   48/hf · %58.3 · +0.647 · top +30.9 · sessiz %8.9 · en uzun 111 s · dolgu 0.4/hf -0.08
   2026:   51/hf · %58.8 · +0.607 · top +30.9 · sessiz %3.9 · en uzun 73 s · dolgu 0.3/hf +1.07
R5 (BTC ve coin-tek yok, coin z ≥ 0) + F2 dolgu: R0 (⛔ hariç hepsi)
   2022-06→2023:   43/hf · %55.9 · +0.440 · top +19.2 · sessiz %4.1 · en uzun 59 s · dolgu 0.9/hf -0.02
   2024+:   48/hf · %58.2 · +0.642 · top +31.0 · sessiz %5.8 · en uzun 76 s · dolgu 0.9/hf +0.06
   2026:   51/hf · %58.6 · +0.605 · top +30.9 · sessiz %2.1 · en uzun 64 s · dolgu 0.5/hf +0.67
R5 (BTC ve coin-tek yok, coin z ≥ 0) + F3 dolgu: R4 + ABD satarken BTC kısa
   2022-06→2023:   43/hf · %55.9 · +0.451 · top +19.4 · sessiz %7.4 · en uzun 117 s · dolgu 0.6/hf +0.47
   2024+:   48/hf · %58.3 · +0.644 · top +30.9 · sessiz %6.6 · en uzun 111 s · dolgu 0.6/hf +0.02
   2026:   51/hf · %58.7 · +0.606 · top +30.9 · sessiz %2.9 · en uzun 73 s · dolgu 0.4/hf +0.84
S1 (R5 + fark ≥ 1 ve coin z > −1) + dolgu yok
   2022-06→2023:   44/hf · %55.9 · +0.449 · top +19.7 · sessiz %10.7 · en uzun 202 s · dolgu 0.0/hf +nan
   2024+:   51/hf · %58.2 · +0.605 · top +30.7 · sessiz %10.3 · en uzun 251 s · dolgu 0.0/hf +nan
   2026:   54/hf · %59.2 · +0.598 · top +32.5 · sessiz %4.6 · en uzun 73 s · dolgu 0.0/hf +nan
S1 (R5 + fark ≥ 1 ve coin z > −1) + F1 dolgu: R4 (BTC/coin-tek yok, ⛔ hariç)
   2022-06→2023:   44/hf · %55.9 · +0.443 · top +19.6 · sessiz %7.9 · en uzun 114 s · dolgu 0.4/hf -0.18
   2024+:   51/hf · %58.2 · +0.599 · top +30.6 · sessiz %8.3 · en uzun 111 s · dolgu 0.3/hf -0.49
   2026:   55/hf · %59.2 · +0.600 · top +32.7 · sessiz %3.6 · en uzun 73 s · dolgu 0.2/hf +1.08
S1 (R5 + fark ≥ 1 ve coin z > −1) + F2 dolgu: R0 (⛔ hariç hepsi)
   2022-06→2023:   45/hf · %56.0 · +0.439 · top +19.7 · sessiz %4.0 · en uzun 59 s · dolgu 0.9/hf -0.04
   2024+:   51/hf · %58.1 · +0.595 · top +30.6 · sessiz %5.5 · en uzun 76 s · dolgu 0.8/hf -0.11
   2026:   55/hf · %59.1 · +0.599 · top +32.8 · sessiz %2.1 · en uzun 64 s · dolgu 0.4/hf +0.72
S1 (R5 + fark ≥ 1 ve coin z > −1) + F3 dolgu: R4 + ABD satarken BTC kısa
   2022-06→2023:   44/hf · %56.0 · +0.449 · top +19.9 · sessiz %7.3 · en uzun 117 s · dolgu 0.5/hf +0.41
   2024+:   51/hf · %58.2 · +0.598 · top +30.6 · sessiz %6.4 · en uzun 111 s · dolgu 0.5/hf -0.23
   2026:   55/hf · %59.2 · +0.601 · top +32.8 · sessiz %2.9 · en uzun 73 s · dolgu 0.3/hf +1.08
S2 (fark ≥ 0,5 ve coin z > −1) + dolgu yok
   2022-06→2023:   29/hf · %56.4 · +0.546 · top +16.0 · sessiz %14.0 · en uzun 211 s · dolgu 0.0/hf +nan
   2024+:   37/hf · %56.7 · +0.564 · top +20.6 · sessiz %11.6 · en uzun 173 s · dolgu 0.0/hf +nan
   2026:   38/hf · %56.7 · +0.564 · top +21.7 · sessiz %5.4 · en uzun 73 s · dolgu 0.0/hf +nan
S2 (fark ≥ 0,5 ve coin z > −1) + F1 dolgu: R4 (BTC/coin-tek yok, ⛔ hariç)
   2022-06→2023:   30/hf · %56.4 · +0.535 · top +16.0 · sessiz %8.8 · en uzun 114 s · dolgu 0.6/hf +0.03
   2024+:   37/hf · %56.5 · +0.552 · top +20.4 · sessiz %8.8 · en uzun 111 s · dolgu 0.5/hf -0.41
   2026:   39/hf · %56.6 · +0.560 · top +21.6 · sessiz %4.3 · en uzun 73 s · dolgu 0.2/hf -0.17
S2 (fark ≥ 0,5 ve coin z > −1) + F2 dolgu: R0 (⛔ hariç hepsi)
   2022-06→2023:   31/hf · %56.6 · +0.522 · top +16.0 · sessiz %4.3 · en uzun 59 s · dolgu 1.2/hf -0.05
   2024+:   38/hf · %56.4 · +0.546 · top +20.5 · sessiz %6.0 · en uzun 76 s · dolgu 0.9/hf -0.16
   2026:   39/hf · %56.6 · +0.560 · top +21.8 · sessiz %3.6 · en uzun 64 s · dolgu 0.5/hf +0.19
S2 (fark ≥ 0,5 ve coin z > −1) + F3 dolgu: R4 + ABD satarken BTC kısa
   2022-06→2023:   30/hf · %56.4 · +0.538 · top +16.2 · sessiz %7.9 · en uzun 117 s · dolgu 0.8/hf +0.22
   2024+:   37/hf · %56.5 · +0.551 · top +20.5 · sessiz %6.9 · en uzun 111 s · dolgu 0.6/hf -0.19
   2026:   39/hf · %56.6 · +0.561 · top +21.7 · sessiz %3.6 · en uzun 73 s · dolgu 0.3/hf +0.09
```

Koşulları (sessiz gün ≤ %2, haftada 35–80) sağlayan aday yok

## 4) Takvim günü dolgusu — o gün hiç sinyal gitmediyse (temel: R5)
_hücre: haftada · isabet · net · sessiz gün % · dolgu: haftada / isabet / net_
```
G1: gün boşsa R4
   2022-06→2023:   44/hf · %55.7 · +0.429 · sessiz %6.2 · en uzun 114 s · dolgu 1.4/hf %53 -0.214
   2024+:   49/hf · %58.1 · +0.628 · sessiz %7.1 · en uzun 111 s · dolgu 1.6/hf %52 -0.085
   2026:   53/hf · %58.6 · +0.583 · sessiz %2.1 · en uzun 73 s · dolgu 1.9/hf %56 +0.030
G2: gün boşsa R0
   2022-06→2023:   47/hf · %55.8 · +0.405 · sessiz %0.9 · en uzun 57 s · dolgu 4.2/hf %56 -0.054
   2024+:   52/hf · %58.0 · +0.608 · sessiz %3.2 · en uzun 67 s · dolgu 4.3/hf %55 +0.115
   2026:   55/hf · %58.3 · +0.555 · sessiz %0.7 · en uzun 45 s · dolgu 4.5/hf %54 +0.001
G3: gün boşsa her şey
   2022-06→2023:   47/hf · %56.0 · +0.410 · sessiz %0.7 · en uzun 53 s · dolgu 4.6/hf %57 +0.041
   2024+:   52/hf · %58.0 · +0.595 · sessiz %1.3 · en uzun 52 s · dolgu 4.9/hf %55 +0.033
   2026:   56/hf · %58.3 · +0.554 · sessiz %0.0 · en uzun 42 s · dolgu 5.0/hf %54 +0.039
G4: kademeli (R4 → 12:00'den sonra R0 → 18:00'den sonra her şey)
   2022-06→2023:   45/hf · %55.8 · +0.425 · sessiz %1.6 · en uzun 85 s · dolgu 2.0/hf %55 -0.121
   2024+:   50/hf · %58.1 · +0.621 · sessiz %3.7 · en uzun 72 s · dolgu 2.2/hf %53 -0.041
   2026:   53/hf · %58.7 · +0.586 · sessiz %1.1 · en uzun 64 s · dolgu 2.2/hf %58 +0.166
   ↳ R4 kademesi: 2022-06→2023:   1.2/hf · %53.5 · -0.237 | 2024+:   1.5/hf · %54.3 · +0.024 | 2026:   1.8/hf · %58.9 · +0.223
   ↳ R0 kademesi: 2022-06→2023:   0.7/hf · %59.3 · +0.057 | 2024+:   0.6/hf · %54.8 · -0.117 | 2026:   0.2/hf · %70.0 · +0.222
   ↳ her şey kademesi: 2022-06→2023:   0.1/hf · %42.9 · +0.053 | 2024+:   0.2/hf · %34.6 · -0.319 | 2026:   0.1/hf · %20.0 · -0.788
```

_Süre: 169 sn_
