# Önceden yazılı protokol — GİRİŞ KURALI: limit dolmazsa ne yapmalı? (giris2 · 25.10.2026)
_Kullanıcı (25.10): canlı karnede ✅ ana limit emirleri dolmayanlar kazananlardı (17 dolmayan: piyasadan girilseydi %88, +%1,23) → "test et". Bu dosya veri işlenmeden yazıldı; sonradan değiştirilmez (gerekirse tarihli "Ek")._

## Veri
- veri_seti.csv.gz'deki tüm sinyaller (✅ ana · 🔸 yedek · 📋 panelden; t = sinyal saatinin kapanışı, G = kapanış fiyatı, s = σ720·√H). Binance 1 dk mum, t → t + H saat + 70 dk.
- 🎯 = G·(1 + k·s) (ana 0,75 · yedek 0,50 · panelden 0,45) — mesajdaki sabit fiyat, girişe göre değişmez. Çıkış: 🎯'ye değerse 🎯'den (limit ücreti), değmezse t + H kapanışı (piyasa ücreti). Vadeli ücret limit %0,02 · piyasa %0,05 · fonlama %0,01 / geçilen 00-08-16 UTC. (karal2_veri.py ile aynı ölçüm.)

## Giriş kuralları (dakika 7 = mesajın geldiği an)
- **B (şimdiki):** 7. dk açılışı ≤ G → o açılıştan (piyasa ücreti); değilse 8–66. dk'da en düşük ≤ G → G'den limit; dolmazsa işlem yok.
- **D7:** 7. dk açılışından piyasa.
- **E15 · E30 · E60:** B gibi, ama limit penceresi 15 / 30 / 60 dk; dolmazsa pencere sonunda (7+N. dk açılışı) piyasadan gir.
- **P10 · P25 · P50:** limit fiyatı G·(1 + %0,10 / %0,25 / %0,50) ("biraz pahalı limit"), pencere 60 dk; dolmazsa işlem yok.
- **P25E60:** limit G·(1+%0,25), 60 dk'da dolmazsa piyasadan.
- Toplam 8 alternatif · her sınıf ayrı.

## Ölçüler
- **sinyal başı net** = (dolan işlemlerin net toplamı) / (TÜM sinyal sayısı) — dolmayan sinyal 0 sayılır; girişleri adil karşılaştıran ana ölçü.
- işlem isabeti · işlem başı net · saat isabeti (saatteki işlemlerin eşit pay sepeti > 0) · saat başı net · dolum oranı.

## KEŞİF (2022-06-01 → 2024-12-31; iki yarı: → 2023-06-30 · 2023-07-01 →)
- Bir alternatif o sınıf için keşfi ancak İKİ YARIDA DA B'ye göre şunları sağlarsa geçer: sinyal başı net ≥ B + %0,03 · saat isabeti ≥ B − 1 puan · işlem isabeti ≥ B − 2 puan.
- Geçenlerden keşif sinyal başı neti en yüksek TEK alternatif kontrole gider.

## KONTROL (bir kez): 2025-01-01 → ve 2026-01-01 →
- Aynı üç şart iki kontrol döneminde de sağlanırsa → "B yerine önerilir" (kullanıcı onayıyla canlıya). Sağlanmazsa B kalır.
- Bilgi: canlı karne (karne_gercek.csv, 12.10 →) aynı ölçülerle; karar şartı değil (örnek az).
