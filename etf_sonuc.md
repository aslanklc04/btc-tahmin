# 🕶️ Karanlık oda izleri: ETF akışı ve CFTC kurumsal pozisyonları — 08.10.2026 19:39
- BTC ETF: alınamadı · CFTC: 2018-04-10 → 2026-09-29, 443 hafta, varlık yöneticisi net +18.3%, kaldıraçlı fon net -35.0%
- ETH ETF: alınamadı · CFTC: 2021-04-06 → 2026-09-29, 287 hafta, varlık yöneticisi net -4.4%, kaldıraçlı fon net -29.5%

## A) Tek başına sinyal
Toplam 16 deneme · ✅ geçen **1** · plasebo geçme oranı %3.8 → tesadüfen ≈ 0.6
_işlem · isabet % · işlem başı net % · alt sınır %_
```
coin                                           sinyal  gun yon             seçim ≤2023         doğrulama 2024+                2026    ok
 BTC   CFTC varlık yöneticisi net uzun artışı z ≥ 1,5    7 SAT 17 · 35 · +0.58 · -2.33      7 · 29 · -1.69 · —  4 · 25 · -1.12 · — False
 BTC   CFTC varlık yöneticisi net uzun artışı z ≥ 1,5   14 SAT 16 · 56 · +2.73 · -1.60      7 · 29 · -4.01 · —   4 · 0 · -3.13 · — False
 BTC CFTC varlık yöneticisi net uzun azalışı z ≤ −1,5    7  AL 16 · 38 · +0.54 · -2.99  8 · 75 · +2.55 · -0.13  5 · 60 · +0.04 · — False
 BTC CFTC varlık yöneticisi net uzun azalışı z ≤ −1,5   14 SAT 14 · 57 · +0.66 · -4.42      7 · 43 · +0.84 · —  4 · 50 · +3.87 · — False
 BTC      CFTC kaldıraçlı fon net uzun artışı z ≥ 1,5    7  AL 16 · 50 · +2.40 · -0.24  9 · 67 · +2.84 · +0.55  3 · 33 · -1.08 · —  True
 BTC      CFTC kaldıraçlı fon net uzun artışı z ≥ 1,5   14  AL 14 · 64 · +2.24 · -0.22  9 · 78 · +2.26 · -3.11  3 · 33 · -4.58 · — False
 BTC    CFTC kaldıraçlı fon net uzun azalışı z ≤ −1,5    7  AL 11 · 64 · +6.19 · +1.12      7 · 57 · +1.09 · — 1 · 100 · +4.09 · — False
 BTC    CFTC kaldıraçlı fon net uzun azalışı z ≤ −1,5   14  AL 11 · 64 · +7.60 · +0.93      7 · 43 · +0.47 · — 1 · 100 · +3.48 · — False
 ETH   CFTC varlık yöneticisi net uzun artışı z ≥ 1,5    7  AL 14 · 50 · +0.69 · -4.19 10 · 70 · +4.02 · -2.01  6 · 83 · +6.09 · — False
 ETH   CFTC varlık yöneticisi net uzun artışı z ≥ 1,5   14  AL 10 · 50 · +0.34 · -4.53  9 · 67 · +5.82 · -0.29  5 · 80 · +6.93 · — False
 ETH CFTC varlık yöneticisi net uzun azalışı z ≤ −1,5    7  AL  9 · 56 · +3.01 · -1.51      5 · 80 · +1.68 · —  4 · 75 · +0.81 · — False
 ETH CFTC varlık yöneticisi net uzun azalışı z ≤ −1,5   14  AL  9 · 44 · +4.11 · -3.03      5 · 60 · +0.43 · —  4 · 75 · +1.98 · — False
 ETH      CFTC kaldıraçlı fon net uzun artışı z ≥ 1,5    7  AL 16 · 56 · +1.13 · -4.51       3 · 0 · -7.79 · —   1 · 0 · -7.18 · — False
 ETH      CFTC kaldıraçlı fon net uzun artışı z ≥ 1,5   14  AL 16 · 38 · +0.59 · -5.99      3 · 33 · -4.26 · —   1 · 0 · -9.49 · — False
 ETH    CFTC kaldıraçlı fon net uzun azalışı z ≤ −1,5    7 SAT      7 · 71 · +0.35 · —      6 · 17 · -3.38 · —   3 · 0 · -2.97 · — False
 ETH    CFTC kaldıraçlı fon net uzun azalışı z ≤ −1,5   14 SAT      7 · 71 · +1.74 · —      6 · 17 · -6.33 · —   3 · 0 · -5.07 · — False
```

## B) Filtre olarak (iyi / kötü isabet %, kötü işlem sayısı) — 0 / 30 geçti
```
                  aile                                          filtre  kotu_pay          secim                          dogrulama    alt         y2026 ok
          BTC 1 saat ↑                        E1 dün ETF'ten net çıkış       0.0   60 / nan (0)    56 / nan (0) · net -0.03 / +nan    NaN  56 / nan (0)  ❌
          BTC 1 saat ↑                       E2 dünkü ETF akışı z ≤ −1       0.0   60 / nan (0)    56 / nan (0) · net -0.03 / +nan    NaN  56 / nan (0)  ❌
          BTC 1 saat ↑                    E3 son 5 gün ETF toplamı < 0       0.0   60 / nan (0)    56 / nan (0) · net -0.03 / +nan    NaN  56 / nan (0)  ❌
          BTC 1 saat ↑       C1 varlık yöneticileri net uzunu azaltmış      53.0  62 / 60 (974) 57 / 57 (1933) · net -0.01 / -0.02  -2.68 54 / 57 (589)  ❌
          BTC 1 saat ↑ C2 kaldıraçlı fonlar net uzunu artırmış (z ≥ 1)      14.4  61 / 62 (253)  58 / 56 (525) · net -0.01 / -0.02  -2.27 55 / 59 (124)  ❌
BTC 4/8 saat ↑ + ⭐ + A                        E1 dün ETF'ten net çıkış       0.0   60 / nan (0)    56 / nan (0) · net -0.01 / +nan    NaN  55 / nan (0)  ❌
BTC 4/8 saat ↑ + ⭐ + A                       E2 dünkü ETF akışı z ≤ −1       0.0   60 / nan (0)    56 / nan (0) · net -0.01 / +nan    NaN  55 / nan (0)  ❌
BTC 4/8 saat ↑ + ⭐ + A                    E3 son 5 gün ETF toplamı < 0       0.0   60 / nan (0)    56 / nan (0) · net -0.01 / +nan    NaN  55 / nan (0)  ❌
BTC 4/8 saat ↑ + ⭐ + A       C1 varlık yöneticileri net uzunu azaltmış      51.9 58 / 59 (1443) 58 / 58 (2770) · net +0.07 / +0.02  -3.55 57 / 53 (832)  ❌
BTC 4/8 saat ↑ + ⭐ + A C2 kaldıraçlı fonlar net uzunu artırmış (z ≥ 1)      12.5  59 / 58 (393)  58 / 57 (668) · net +0.04 / +0.11  -5.38 55 / 49 (148)  ❌
       coin tek başına                        E1 dün ETF'ten net çıkış       0.0   62 / nan (0)    56 / nan (0) · net +0.02 / +nan    NaN  56 / nan (0)  ❌
       coin tek başına                       E2 dünkü ETF akışı z ≤ −1       0.0   62 / nan (0)    56 / nan (0) · net +0.02 / +nan    NaN  56 / nan (0)  ❌
       coin tek başına                    E3 son 5 gün ETF toplamı < 0       0.0   62 / nan (0)    56 / nan (0) · net +0.02 / +nan    NaN  56 / nan (0)  ❌
       coin tek başına       C1 varlık yöneticileri net uzunu azaltmış      50.5 63 / 58 (1373) 59 / 57 (2600) · net +0.10 / +0.09  -1.20 57 / 56 (753)  ❌
       coin tek başına C2 kaldıraçlı fonlar net uzunu artırmış (z ≥ 1)      11.7  60 / 62 (400)  58 / 58 (602) · net +0.08 / +0.20  -5.46 57 / 52 (157)  ❌
         coin 🔇 sessiz                        E1 dün ETF'ten net çıkış       0.0   66 / nan (0)    57 / nan (0) · net +0.02 / +nan    NaN  54 / nan (0)  ❌
         coin 🔇 sessiz                       E2 dünkü ETF akışı z ≤ −1       0.0   66 / nan (0)    57 / nan (0) · net +0.02 / +nan    NaN  54 / nan (0)  ❌
         coin 🔇 sessiz                    E3 son 5 gün ETF toplamı < 0       0.0   66 / nan (0)    57 / nan (0) · net +0.02 / +nan    NaN  54 / nan (0)  ❌
         coin 🔇 sessiz       C1 varlık yöneticileri net uzunu azaltmış      50.0  59 / 61 (335)  63 / 58 (777) · net +0.39 / +0.09   0.21 56 / 52 (202)  ❌
         coin 🔇 sessiz C2 kaldıraçlı fonlar net uzunu artırmış (z ≥ 1)      12.2  60 / 60 (144)  60 / 61 (189) · net +0.25 / +0.20  -8.73  54 / 54 (48)  ❌
          coin 🤝 ortak                        E1 dün ETF'ten net çıkış       0.0   64 / nan (0)    60 / nan (0) · net +0.12 / +nan    NaN  63 / nan (0)  ❌
          coin 🤝 ortak                       E2 dünkü ETF akışı z ≤ −1       0.0   64 / nan (0)    60 / nan (0) · net +0.12 / +nan    NaN  63 / nan (0)  ❌
          coin 🤝 ortak                    E3 son 5 gün ETF toplamı < 0       0.0   64 / nan (0)    60 / nan (0) · net +0.12 / +nan    NaN  63 / nan (0)  ❌
          coin 🤝 ortak       C1 varlık yöneticileri net uzunu azaltmış      51.3 57 / 60 (1082) 62 / 60 (2851) · net +0.24 / +0.16  -3.77 68 / 60 (780)  ❌
          coin 🤝 ortak C2 kaldıraçlı fonlar net uzunu artırmış (z ≥ 1)      12.7  58 / 59 (258)  61 / 60 (706) · net +0.19 / +0.29  -8.91 64 / 57 (183)  ❌
             🧪 24 saat                        E1 dün ETF'ten net çıkış       0.0   57 / nan (0)    53 / nan (0) · net +0.34 / +nan    NaN  50 / nan (0)  ❌
             🧪 24 saat                       E2 dünkü ETF akışı z ≤ −1       0.0   57 / nan (0)    53 / nan (0) · net +0.34 / +nan    NaN  50 / nan (0)  ❌
             🧪 24 saat                    E3 son 5 gün ETF toplamı < 0       0.0   57 / nan (0)    53 / nan (0) · net +0.34 / +nan    NaN  50 / nan (0)  ❌
             🧪 24 saat       C1 varlık yöneticileri net uzunu azaltmış      46.7  54 / 59 (476) 56 / 53 (1237) · net +0.73 / +0.26  -2.98 49 / 52 (365)  ❌
             🧪 24 saat C2 kaldıraçlı fonlar net uzunu artırmış (z ≥ 1)      10.6  56 / 57 (138)  54 / 62 (280) · net +0.46 / +0.98 -17.94  49 / 63 (89)  ❌
```

_Süre: 12 sn_
