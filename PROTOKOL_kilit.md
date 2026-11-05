# Önceden yazılı protokol — TOKEN KİLİT AÇILIMLARI ÖNCESİ SHORT (kilit · 05.11.2026)
_Kullanıcı (05.11): "Tüm testlere başla, her şey objektif." Kaynak: Keyrock (16.000+ açılım): açılımların ~%90'ı fiyatı aşağı iter, etki ~30 gün önce başlar, ekip açılımları en sert.
Takvim: DefiLlama açık kaynak emissions-adapters (GitHub) kodundan üretilir (DefiLlama API'si ücretli oldu). Fiyat: data.binance.vision USDT-M vadeli 1 g (kapatılanlar dahil, yeniliste verisi).
Hesaptan önce yazıldı; sonradan değiştirilmez. Canlıya yalnız onayla._

## Olay
- Her proje için takvimdeki AYRIK (tek seferlik / cliff) açılımlar; sürekli doğrusal akış günlük birikir: bir takvim gününde açılan toplam ≥ dolaşımdaki arzın %1'i olan günler "büyük açılım".
  Dolaşımdaki arz yaklaşığı = takvime göre o güne kadar açılmış toplam (takvim dışı arz bilinmiyorsa); bulunamazsa toplam arzın %1'i.
- Alıcı türü takvim etiketinden: ekip/çekirdek katkıcı · yatırımcı/özel satış · topluluk/ekosistem/hazine · diğer.
- Eşleşme: projenin token sembolü ↔ Binance USDT-M perpetual tabanı (1000-önekleri ayıklanmış). Açılım tarihi kontratın ilk gününden ≥ 45 gün sonra olmalı. Aynı coin'de 30 günden yakın büyük açılımlar birleştirilir (ilki).
## İşlem
- Short giriş: açılımdan E gün önce açılışta; çıkış: açılım gününden 1 gün sonra kapanışta. E ∈ {30 · 14 · 7}.
- Maliyet: ücret %0,05 + kayma %0,10 (iki taraf) + gerçek fonlama · 1× · kayıp en çok −%100. Piyasaya göre: aynı pencerede ≥ 365 günlük tüm kontratların eşit ağırlıklı getirisi.
## Ayrım · karar
- Keşif: açılım tarihi 2021-01 → 2023-12 · doğrulama 2024 · 2025 · 2026 ayrı.
- E ve alıcı türü (tümü / ekip / yatırımcı / ekip+yatırımcı) keşifte seçilir: en yüksek ort. net, ≥ 30 olay.
- **"Bulundu":** seçilen ayar 2024, 2025, 2026'nın her birinde ≥ 15 olay · ort. net ≥ +%2 · medyan > 0 · kazanma ≥ %55 · piyasaya göre ort. > 0 · ≤ −%50 oranı ≤ %10 ·
  aynı coin'lerde rastgele (açılım olmayan) tarihli aynı uzunlukta short'ların (×200) ort. net %95'inden yüksek.
- Bilgi: tüm ayarlar tablosu, büyüklük dilimleri (%1–5 · %5–10 · > %10), eşleşen proje/olay sayısı.
## Bilinen yanlılıklar (raporda yazılır)
- Takvimler bugünkü bilgiyle kodlanmış; bazı geçmiş açılımlar önceden bilinmiyor olabilir → sonuç iyimser olabilir.
- Takvim kodu hatalı/eksik projeler olabilir; yalnız çalışan adaptörler kullanılır, sayısı raporlanır.
