# Önceden yazılı protokol — FİYAT DIŞI VERİ (türev piyasası, opsiyon, duygu) ile sinyal seçimi (turev · 26.10.2026)
_Kullanıcı (26.10): "Bana gerçekten işe yarar sinyal bul … tüm verilere, GitHub'ta her yere bak." veri_yokla2.md: Actions'tan erişilebilen ve geçmişi olan kaynaklar belirlendi. Bu dosya veri işlenmeden yazıldı; sonradan değiştirilmez (gerekirse tarihli "Ek")._

## Soru
Mevcut sinyallerin (veri_seti.csv.gz; ✅ ana · 🔸 yedek · 📋 panelden) gerçekçi sonucunu (karal2_veri B_T0 = mesaj fiyatına limit, 🎯, vadeli ücret + fonlama) fiyatta olmayan bir bilgi belirgin biçimde iyileştiriyor mu? Hedef: **üç dönemde de işlem isabeti ≥ %70 ve kârlı** bir alt küme, mümkün olduğunca sık.

## Özellikler (sinyal anından ÖNCE biten verilerden; hepsi önceden sabit)
Coin başına (Binance vadeli arşivi, data.binance.vision; vadeli sembol yoksa "1000"+coin denenir; bulunamazsa o coin'de özellik boş):
1. `oi24` = açık pozisyon (USDT) son 24 saat log değişimi · `oi4` = son 4 saat
2. `ls_top` = büyük hesapların long/short oranı (sum_toptrader_long_short_ratio), son 720 saate göre z
3. `ls_all` = tüm hesapların long/short oranı (count_long_short_ratio), z
4. `taker` = alıcı/satıcı taker hacim oranı (sum_taker_long_short_vol_ratio), son 24 saat ortalaması, z
5. `fon` = coin'in Binance fonlama oranı (son ödeme), son 90 ödemeye göre z
6. `baz` = vadeli prim (premiumIndex 1 s kapanışı), son 24 saat ortalaması, 720 saate göre z
Piyasa geneli:
7. `dvol` = Deribit BTC opsiyon oynaklık endeksi (DVOL), 720 saate göre z · 8. `dvol24` = DVOL 24 saat değişimi
9. `fg` = Korku-açgözlülük endeksi (önceki günün değeri, 0–100)

## Filtreler
- Her özellik için iki filtre: **düşük uç** (keşif ana sinyallerinde alt %30 sınırının altı) ve **yüksek uç** (üst %30 sınırının üstü). Sınırlar yalnız keşif verisinden, ✅ ana sinyallerinde hesaplanır ve sabitlenir. 9 × 2 = **18 filtre**.
- Plasebo: aynı büyüklükte rastgele alt küme (200 tekrar) → ortalama ve %95.

## KEŞİF (✅ ana, 2022-06-01 → 2024-12-31; iki yarı: → 2023-06-30 · 2023-07-01 →)
- Bir filtre İKİ YARIDA DA: işlem isabeti ≥ taban + 4 puan · işlem başı net ≥ taban + %0,10 · plasebo %95'inin üstünde (isabette) · yarı başına ≥ 100 işlem.
- Geçenlerden keşif işlem isabeti en yüksek ≤ 3 filtre kontrole gider; ayrıca bu 3'ün ikili kesişimleri (≤ 3) bilgi olarak raporlanır (karar değil).

## KONTROL (bir kez): ✅ ana 2025-01-01 → ve 2026-01-01 →
- **Başarı:** iki dönemde de işlem isabeti ≥ %70 · işlem başı net ≥ taban + %0,10 · saat isabeti ≥ %65 · haftada ≥ 1 saat.
- Bilgi (karar değil): aynı filtre 🔸 yedek ve 📋 panelden sinyallerinde · mevcut 💎 ELİT ile birleşim · piyasadan giriş (D_T0).

## Canlıya geçiş şartı
- Başarılı filtrenin özelliği CANLIDA erişilebilir olmalı (Binance vadeli API ABD'den kapalı: canlı karşılık OKX / Deribit / alternative.me ile önce doğrulanır). Kullanıcı onayı olmadan canlıya girmez.

## Ek (26.10.2026, veri işlenmeden ÖNCE — sayım düzeltmesi)
- 1. madde iki özellik içerir (`oi24`, `oi4`) → toplam **10 özellik, 20 filtre** (metindeki "9 × 2 = 18" yanlış sayım). Başka değişiklik yok.
