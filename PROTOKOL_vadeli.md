# Önceden yazılı protokol — vadeli piyasa verisi (açık pozisyon, alıcı/satıcı oranı, uzun/kısa, coin fonlaması) (24.10.2026)
_Veri indirilmeden ve hiçbir sonuç görülmeden yazıldı. Değişiklik gerekirse ayrı, tarihli ek._

## Veri
- Binance USDT-M arşivi (data.binance.vision): günlük `metrics` (5 dk: sum_open_interest, count_long_short_ratio, sum_toptrader_long_short_ratio, sum_taker_long_short_vol_ratio) ve aylık `fundingRate`; 2022-01 → bugün; canlı listelerdeki coin'ler (arşivde olanlar).
- Saatlik özellikler, t = saat kapanışı, yalnız create_time ≤ t olan satırlarla:
  doi1 / doi4 / doi24 = açık pozisyon (adet) log değişimi 1 / 4 / 24 saat · tk1 / tk4 = son 1 / 4 saatin ortalama alıcı/satıcı hacim oranı (log) · gls = herkesin uzun/kısa hesap oranı (log) · tls = büyük oyuncuların uzun/kısa pozisyon oranı (log) · fr = coin'in son fonlama oranı.
  Her biri coin'in kendi geçmişine göre z: son 720 saat (en az 168), fr için son 90 fonlama.

## A) Mevcut sinyallere filtre (asıl amaç)
- Sinyaller ve gerçekçi sonuç: veri_seti.csv.gz + karal2_veri.csv.gz (B = mesajdaki fiyata limit, vadeli ücret + fonlama, şimdiki 🎯). Özelliği olmayan coin'ler hem tabandan hem filtreden çıkarılır.
- Sınıf başına (✅ ana · 🔸 yedek · 📋 panelden), 8 özellik × 4 seçenek (alt⅓ · üst⅓ · alt⅓'ü at · üst⅓'ü at; tertiller keşif sinyallerinden) = 32 tek filtre; birleşim yok.
- KEŞİF 2022-01 → 2024-12 (iki yarı: → 2023-06 · 2023-07 →). Seçim şartı her iki yarıda: işlem isabeti ≥ taban · saat isabeti ≥ taban − 0,5 · işlem başı net ≥ taban + 0,05 puan · kalan işlem ≥ tabanın %40'ı. Geçenlerden en yüksek netli tek filtre (sınıf başına) kontrole.
- KONTROL 2025-01 → bugün ve ayrıca 2026: aynı şartlar. (Sinyal sonuçları bu dönemde daha önce görüldü; vadeli özellikler hiç görülmedi → kanıt "orta güç".)

## B) Yeni sinyal adayları (yalnız bu 4; uzun yön)
- N1 hırslı alım: tk1 z ≥ 2 VE doi1 z ≥ 2 → 4 saat tut.
- N2 kaldıraç temizliği: doi24 z ≤ −2 VE coin 24 s getirisi ≤ −1·σ24 → 24 saat tut.
- N3 kalabalık kısa: gls z ≤ −2 → 24 saat tut.
- N4 büyük oyuncu uzun: tls z ≥ 2 → 24 saat tut.
- Olaylar arası en az H saat (çakışma yok). Giriş: saat kapanışı + %0,10 gecikme cezası (ölçülen 7 dk kayma medyanı ~%0,06–0,12); ücret piyasa giriş/çıkış %0,05 + %0,05 + fonlama yaklaşığı (%0,01 / 8 saat). Hedef/stop yok.
- Plasebo: aynı coin, aynı takvim ayındaki tüm saatlerden aynı süreli koşulsuz ortalama.
- Şart (keşifin iki yarısında ve kontrolde ayrı ayrı): işlem başı net > +%0,15 VE plasebodan ≥ 0,15 puan iyi VE haftada ≥ 2 olay.

## Genel
- Toplam deneme: 96 filtre + 4 yeni sinyal = 100. Başarısızlık "bulunamadı" diye raporlanır, eşik gevşetilmez.
- Geçen hiçbir şey kullanıcı onayı olmadan canlıya alınmaz; önce gölge izleme.

## Ek 1 (24.10.2026, veri indirilmeden) — uygulama ayrıntıları
- N2'deki σ24 = coin'in son 720 saatlik saatlik log getiri std'si × √24 (24 saatlik hareketin σ'sı).
- Arşivde güncel ayın aylık fundingRate dosyası yoksa o ay için fr eksik sayılır (filtre o sinyallerde uygulanmaz → sinyal hem tabandan hem filtreden çıkar).
- Saatlik toplama: (t−1 s, t] aralığı; oi / gls / tls aralığın son değeri, tk aralığın ortalaması.
- N sinyalleri için fiyat: Binance spot 1 s kapanış (data-api); fonlama yaklaşığı = %0,01 × H/8.
