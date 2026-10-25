# Önceden yazılı protokol — fiyat yükselmişken piyasadan alınca 🎯'yi kaydırmak (karal3 · 25.10.2026)
_Kullanıcı (25.10): "Sinyal gelince fiyat yükselmişse piyasadan alırım, çok yakınsa limit emir" · "fiyat yükselmişse kâr-alı biraz yükseltsem ne olur" → "Evet test et". Ön bakış (veri_seti mfe ile kaba hesap, tüm dönemler görüldü) umut verici çıktı; bu yüzden karar YALNIZ bu protokolle, 1 dk mumla verilir. Bu dosya 1 dk veri işlenmeden yazıldı; sonradan değiştirilmez._

## Veri ve ölçüm
- veri_seti.csv.gz sinyalleri (✅ ana · 🔸 yedek · 📋 panelden), Binance 1 dk mum, karal2_veri / giris2 ile aynı ölçüm: 🎯 = G·(1 + k·s) · çıkış 🎯 (limit ücreti) ya da t + H kapanışı (piyasa ücreti) · vadeli ücret + fonlama.
- O7 = mesaj anı (7. dk) açılış fiyatı · yükselme y = O7 / G − 1.

## Kullanıcının giriş pratiği (taban, "Kx")
- y > x ise 7. dk açılışından PİYASA alış; değilse şimdiki kural B (G'ye 60 dk limit). x ∈ {%0,25 · %0,5}. 🎯 sabit (mesajdaki).

## Denenen 4 kural
- x ∈ {%0,25 · %0,5} × kaydırma f ∈ {½ · 1}: y > x iken (piyasadan alınan işlemlerde) 🎯' = 🎯 · (1 + f·y). Diğer işlemler tabanla aynı.

## Ölçüler
- sinyal başı net (dolmayan = 0) · işlem isabeti · saat isabeti (saat sepeti > 0) · ayrıca yalnız y > x olan işlemlerde aynı ölçüler (bilgi).

## KEŞİF (2022-06-01 → 2024-12-31; iki yarı: → 2023-06-30 · 2023-07-01 →), her sınıf ayrı
- Bir kural, kendi x'inin tabanına (Kx, 🎯 sabit) göre İKİ YARIDA DA: sinyal başı net ≥ taban + %0,03 · işlem isabeti ≥ taban − 1 puan · saat isabeti ≥ taban − 1 puan.
- Geçenlerden keşif sinyal başı neti en yüksek TEK kural kontrole gider.

## KONTROL (bir kez): 2025-01-01 → ve 2026-01-01 → — aynı üç şart iki dönemde de → "önerilir".
- Önerilirse mesajda YÜZDE değil, somut fiyat satırı olarak verilir (kullanıcı isteği): "Fiyat $A ise 🎯 $B · $C ise 🎯 $D …".
