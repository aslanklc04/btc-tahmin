# Önceden yazılı protokol — BIST FİZİBİLİTE (bist · 01.11.2026)
_Kullanıcı (01.11): "Bu modeli BIST 30 hisseleri için uyarlayabilir miyiz?" → "Başlat". Bu dosya veri indirilmeden ve hesaplardan önce yazıldı; sonradan değiştirilmez (gerekirse tarihli "Ek"). Canlıya yalnız kullanıcı onayıyla._

## Soru
Kripto sisteminin fiyat/hacim tabanlı kısmı (σ'ya göre 🎯 hedef, teknik gösterge kombinasyonları, model) BIST hisselerinde gerçekçi maliyetle **isabet ≥ %70 ve işlem başı ≥ +%0,30** verebilir mi? Kriptoya özgü veriler (fonlama, OI, L/S, tasfiye, opsiyon, zincir) BIST'te yok; bu turda kullanılmaz.

## Veri (bist_veri.py, GitHub Actions, yfinance)
- **Keşif hisseleri = BIST 30** (2026 3. çeyrek listesi): AEFES AKBNK ASELS ASTOR BIMAS DSTKF EKGYO ENKAI EREGL FROTO GARAN GUBRF ISCTR KCHOL KRDMD MGROS PETKM PGSUS SAHOL SASA SISE TAVHL TCELL THYAO TOASO TRALT TTKOM TUPRS VAKBN YKBNK.
- **Doğrulama hisseleri** (BIST 30 dışı büyük/likit BIST 100 hisseleri, veriye bakmadan seçildi): AKSA AKSEN ALARK ARCLK BRSAN BTCIM CCOLA CIMSA DOAS DOHOL ECILC EFOR ENJSA GLRMK HALKB HEKTS ISMEN KONTR KTLEV MAVI MPARK ODAS OTKAR OYAKC PASEU SKBNK SOKM TKFEN TSKB TTRAK ULKER VESTL ZOREN. Yahoo'da verisi olmayan atlanır, raporda yazılır.
- Endeks XU030, XU100 · dolar/TL (TRY=X).
- **Saatlik:** 60 dk mum, Yahoo'nun verdiği son ≈ 730 gün. **Günlük:** düzeltilmiş (bölünme/bedelsiz/temettü) 2010-01 → bugün.
- **Veri temizliği:** BIST'te günlük ±%10 sınırı olduğu için bir mumda −%25'ten büyük düşüş ya da +%30'dan büyük yükseliş = düzeltilmemiş bölünme/hata → o hissede o noktanın ±30 mumu içindeki tetikler ve işlemler atılır (sayısı raporlanır).
- **Bilinen yanlılık:** iki liste de bugünün hayatta kalanları (survivorship). Sonuçlar bu yüzden iyimser olabilir; olumsuz sonuç daha güvenilirdir.

## Dönemler
- **Saatlik:** S1 = ilk 12 ay (seçim) · S2 = sonraki dönem (test). Isınma için ilk 60 seans yalnız gösterge hesabında kullanılır.
- **Günlük:** K 2010–2018 (seçim) · C1 2019–2022 · C2 2023 → bugün.

## Ölçü
- Giriş: tetik mumundan sonraki mumun açılışı × (1 + %0,05 kayma). Ücret: komisyon + BSMV **%0,05 / taraf**. 🎯 limit çıkışta kayma yok; süre sonu ya da stop çıkışında %0,05 kayma. Fonlama yok. Yalnız AL (açığa satış yok).
- 🎯 TL fiyatında; boşlukla (gap) 🎯 üstünde açılırsa çıkış yine 🎯'den (kötümser).
- **Net getiri DOLAR BAZINDA** (karar bununla): (çıkış/USDTRY_çıkış) / (giriş/USDTRY_giriş) − 1 − maliyetler. Bilgi: TL net ve XU030'a göre fazla getiri. (Gerekçe: TL'de yüksek enflasyon "AL"ı yapay iyi gösterir.)
- **isabet = dolar net > 0.**
- Aynı hissede aynı kuralda aynı anda tek işlem.

## Göstergeler (mum kapanışında; "seans" = bir işlem günü)
RSI 14 · MACD (12, 26, 9) · Bollinger (20, 2) · EMA 20/50/200 · Stochastic (14, 3) · ADX 14 · Donchian 20/55 · hacim z (son 1 seans hacmi / önceki 30 seansın ort. ve std.; günlükte son gün / önceki 30 gün) · OBV 1 seans eğimi · VWAP (1 seans; günlükte 5 gün) · ATR 14 · **endeks filtresi: XU030 > EMA 200**. σ = getiri std. (saatlik: önceki 60 seansın mumları; günlük: 250 gün).

## Bölüm A — taban
Her mumda koşulsuz AL: 🎯 isabeti ve net (her çıkış, her hücre). "Hiçbir şey yapmadan" ne çıkıyor.

## Bölüm B — teknik kombinasyonlar (teknik3 ile aynı yapı)
- Tetik 10 (M1–M10) × trend 5 (yok · T1 kapanış > EMA200 · T2 EMA20>50>200 · T3 ADX>25 ve +DI>−DI · **T4 XU030 > EMA200**) × teyit 5 (yok · V1 hacim z ≥ 2 · V2 OBV eğimi > 0 · V3 Bollinger sıkışması · V4 kapanış > VWAP) = 250.
- **Saatlik çıkışlar:** E1 🎯 +0,75σ·√4, en fazla 4 mum · E2 aynı, 8 mum (≈ 1 seans) · E3 aynı, 24 mum (≈ 3 seans) · E4 🎯 2×ATR / stop 1×ATR, en fazla 24 mum. → 1.000 kural.
- **Günlük çıkışlar:** G1 🎯 +0,75σ_g, en fazla 3 gün · G2 🎯 +0,75σ_g·√2, en fazla 5 gün · G3 🎯 +0,75σ_g·√4, en fazla 10 gün · G4 🎯 2×ATR / stop 1×ATR, en fazla 10 gün. → 1.000 kural.

## Bölüm C — model (ana sistemin karşılığı)
- Özellikler (yalnız fiyat/hacim/endeks/dolar): 1/4/8/24 mum ve 3/5/20 seans getirileri, σ, hacim z, RSI, MACD hist./σ, %B, bant genişliği, ADX, EMA uzaklıkları, Stoch, hissenin XU030'a göre 5 seanslık göreli getirisi, XU030 getirileri, USDTRY 1/5 seans değişimi, seans içi saat, haftanın günü.
- Hedef: E3 (saatlik) / G2 (günlük) 🎯'ye ulaştı mı. HistGradientBoosting, yalnız keşif hisseleri × seçim döneminde eğitilir; eşik = eğitimde en yüksek %10 olasılık. Test hücrelerinde eşik üstü sinyaller aynı ölçüyle.

## Hücreler ve karar
- **Saatlik (3 test hücresi):** BIST30 × S2 · doğrulama × S1 · doğrulama × S2. **Günlük (5 test hücresi):** BIST30 × C1, C2 · doğrulama × K, C1, C2.
- **Seçim (keşif × seçim dönemi):** isabet ≥ %65 VE dolar net ≥ +%0,30 VE ≥ 50 işlem (saatlik) / ≥ 100 (günlük).
- **"Sinyal adayı":** seçimi geçen kural/model, TÜM test hücrelerinde isabet ≥ %70 VE net ≥ +%0,30 VE ≥ 30 işlem.
- **"Umut verici":** tüm test hücrelerinde isabet ≥ %65 VE net ≥ +%0,15.
- **Plasebo:** tetik zamanları aynı hisse içinde rastgele kaydırılır (≥ 30 seans) ×10 → seçim+test sürecinden kaç kural tesadüfen geçer. Gerçek sonuç plasebonun belirgin üstünde değilse kabul edilmez.
- **Sonuç cümlesi:** "BIST'e uyarlanabilir (aday var)" · "umut var, ek veri gerekli" · "fiyat/hacimle olmuyor" — üçünden biri, sayılarla.
