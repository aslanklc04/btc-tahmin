# Önceden yazılı protokol — "kârı isabeti düşürmeden artır" + "saat bazında isabet ≥ %70" (24.10.2026)
_Bu dosya veri seti oluşturulmadan ve hiçbir sonuç görülmeden yazıldı. Sonradan değiştirilmez; değişiklik gerekirse ayrı, tarihli ek yazılır._

## Ölçüm
- **Birim = saat sepeti:** aynı saatte gönderilen tüm sinyaller (sınıf başına ayrı ve tümü birlikte) eşit ağırlıklı tek işlem sayılır. **Saat isabeti** = sepetin ortalama neti > 0. İşlem bazı oranlar yalnız bilgi.
- **Giriş:** mesaj t+7 dk'da gelir → t+7 dk 1 dakikalık mumun açılışından piyasa alışı (ana senaryo). Kapanışa limit (60 dk; fiyat zaten altındaysa hemen) ikinci senaryo.
- **Ücret:** vadeli (giriş piyasa %0,05 · 🎯 limit çıkış %0,02 · süre sonu piyasa çıkış %0,05) = ana · spot (%0,10 + %0,10) = ikinci.
- **🎯:** kapanış G × (1 + k·σ·√H), σ = son 720 saatlik saatlik oynaklık (en az 168). Giriş 🎯'nin üstündeyse hemen çıkış (yalnız ücret).

## Dönemler
- **KEŞİF:** 2022-06-01 → 2024-12-31. Bütün seçimler yalnız burada yapılır.
- **DOĞRULAMA:** 2025-01-01 → bugün. Seçim bitene kadar bu döneme ait hiçbir sonuç hesaplanmaz/yazdırılmaz; seçilen en fazla 3 aday bir kez ölçülür.
- **CANLI:** 12.10.2026 → (karne_kayit.csv), yalnız bilgi (çok az saat).
- Dürüstlük notu: canlı listeler, eşikler ve k değerleri daha önce tüm dönemlere bakılarak seçildi → doğrulama dönemi tamamen temiz değil. Gerçek temiz sınav kuralların dondurulduğu andan sonraki canlı ileri test.

## Aday kollar (liste sınırlı; bunların dışında aday eklenmez)
- **K-A Saat filtresi** (sepet düzeyi, sinyal anında bilinen): sepet büyüklüğü n · BTC 4 s ve 24 s getirisi · BTC Coinbase primi z · KuCoin BTC fonlama z · genişlik (son 24 s'te yükselen coin oranı) · BTC oynaklık rejimi (24 s / 720 s) · günün saati (TR 4 dilim) · hafta içi/sonu. Her değişken keşif döneminin üçte birlik dilimlerine bölünür (tertil); tek filtre ve en fazla 2'li birleşim.
- **K-B Saat içi seçim:** sepetten en iyi N (N = 1, 3, 5) sinyal; skor = coin primi z, coin 24 s ivmesi (rz) ya da coin 24 s getirisi.
- **K-C Çıkış:** k ∈ {0,2 · 0,3 · 0,45 · 0,5 · 0,6 · 0,75 · 1,0 · 1,25 · 1,5 · 2,0 · hedefsiz}; yarısı 🎯 + yarısı süre sonu; K-A filtresine göre farklı k.

## Seçim (keşifte) ve başarı (doğrulamada) şartları
- Keşifte bir aday ancak şunları sağlarsa doğrulamaya gider: saat isabeti ≥ %72 (2 puan pay) · saat başı ort. net (vadeli) > 0 ve şimdiki kuralın sepet netinden büyük · haftada ≥ 4 sinyalli saat · keşif içindeki iki yarıda (2022-06→2023-06 · 2023-07→2024-12) ayrı ayrı saat isabeti ≥ %68.
- Doğrulamada BAŞARI: saat isabeti ≥ %70 VE saat başı ort. net (vadeli) > 0 VE işlem başı net ≥ şimdiki kural VE haftada ≥ 3 sinyalli saat. Spot ücretle sonuç ayrıca raporlanır.
- Keşifte denenen toplam kural sayısı raporlanır. Başarısız olursa "bulunamadı" denir; eşik gevşetilip yeniden aranmaz.
- Hiçbir şey kullanıcı onayı olmadan canlıya alınmaz.
