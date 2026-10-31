# Önceden yazılı protokol — KLASİK TEKNİK GÖSTERGE KOMBİNASYONLARI (teknik3 · 31.10.2026)
_Kullanıcı (31.10): "Sinyalleri hep coinin hareket durumuna göre çıkardın; neden teknik göstergelerin kombinasyonları ile sinyal denemiyorsun?" Bu dosya veri indirilmeden ve hesaplardan önce yazıldı; sonradan değiştirilmez (gerekirse tarihli "Ek"). Canlıya yalnız kullanıcı onayıyla._

## Veri
- veri_seti.csv.gz'deki 141 coin + BTC · Binance vadeli 1 s mum (OHLCV), 2022-01 → 2026-10 (teknik3_veri.py, Actions).
- **Coin yarıları:** coin adının md5'i çift → **keşif coin'leri**, tek → **doğrulama coin'leri** (ustuste T1 ile aynı bölme).
- **Dönemler:** K 2022–23 (seçim) · C1 2024 · C2 2025-01 → 2026-10-27.

## Göstergeler (saat kapanışında)
RSI 14 · MACD (12, 26, 9) · Bollinger (20, 2) %B ve bant genişliği · EMA 20 / 50 / 200 · Stochastic %K/%D (14, 3) · ADX 14 (+DI, −DI) · Donchian 20 / 55 · hacim z (24 s toplam / önceki 30 g) · OBV 24 s eğimi · VWAP 24 s · ATR 14 · BTC: kapanış > EMA 200.

## Kurallar (yalnız AL; tetik o saatte oluşur)
- **Tetik (10):** M1 MACD histogramı 0'ı yukarı keser · M2 RSI 30'u yukarı keser · M3 RSI 50'yi yukarı keser · M4 %K, %D'yi 20'nin altında yukarı keser · M5 kapanış önceki 20 saatin en yükseğinin üstünde (Donchian 20) · M6 Donchian 55 · M7 kapanış üst Bollinger'i yukarı keser · M8 kapanış alt Bollinger'in altından içeri döner · M9 EMA 20, EMA 50'yi yukarı keser · M10 kapanış VWAP 24'ü yukarı keser.
- **Trend filtresi (5):** yok · T1 kapanış > EMA 200 · T2 EMA 20 > 50 > 200 · T3 ADX > 25 ve +DI > −DI · T4 BTC > EMA 200.
- **Teyit (5):** yok · V1 hacim z ≥ 2 · V2 OBV 24 s eğimi > 0 · V3 tetikten önceki 24 s içinde Bollinger bant genişliği 30 g'ün en düşük %20'sinde (sıkışma) · V4 kapanış > VWAP 24.
- → 10 × 5 × 5 = **250 kombinasyon**.
- **Çıkış (4):** E1 🎯 +0,75σ (σ = 720 s std × √4), en fazla 4 s · E2 aynı, 8 s · E3 aynı, 24 s · E4 🎯 2×ATR / stop 1×ATR, en fazla 24 s (aynı saatte ikisi → stop, kötümser). Diğerlerinde stop yok, süre sonu çıkış.
- → **1.000 kural.**
- İşlem: tetik saatinden sonraki saatin açılışı × (1 + %0,1 kayma) · ücret giriş %0,05 + çıkış (🎯 %0,02 / diğer %0,05) · fonlama %0,01 / 8 s · aynı coin'de aynı kuralda aynı anda tek işlem.

## Seçim ve test
- **Seçim (yalnız keşif coin'leri × K):** isabet ≥ %65 VE işlem başı net ≥ +%0,30 VE ≥ 100 işlem.
- **Test (6 hücre):** keşif coin'leri × {C1, C2} + doğrulama coin'leri × {K, C1, C2} + keşif × K (seçim hücresi).
- **"Sinyal adayı":** 6 hücrenin hepsinde isabet ≥ %70 VE net ≥ +%0,30 VE ≥ 30 işlem.
- **"Umut verici":** 6 hücrede isabet ≥ %65 VE net ≥ +%0,15.
- **Plasebo:** her kuralın tetik saatleri aynı coin içinde rastgele kaydırılır (≥ 30 gün) ×10 → seçim + test sürecinden kaç kural "tesadüfen" geçer.
- **Kıyas:** aynı dönemde mevcut ✅ ana sinyallerinin gerçekçi ölçümü (D_T0).

## Bölüm B — mevcut sinyallere filtre
- Her kombinasyonun (tetik hariç) trend × teyit durumu ve tek tek göstergelerin durumu (RSI bölgesi, MACD > 0, %B, ADX > 25, Stoch bölgesi), mevcut sinyallerin (veri_seti ⋈ karal2, D_T0) gönderildiği saatte ölçülür.
- **Filtre geçer:** ✅ ana ya da tüm sinyallerde, koşul varken isabet farkı ≥ +5 puan VE net farkı ≥ +%0,10, ÜÇ dönemde de (A 2022-06→2024 · B 2025 · C 2026) ve sinyallerin ≥ %20'si kalır.
