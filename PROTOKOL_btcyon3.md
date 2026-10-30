# Önceden yazılı protokol — BTC'NİN YÖNÜ, 3. TUR: ZAMAN + YÖN BİRLEŞİMİ (btcyon3 · 30.10.2026)
_btcyon / btcyon2 bulguları: (1) büyük hareketin ZAMANI önceden görülüyor (btcneden B2: oynaklık genişlemesi, 12–16 UTC); (2) 4 s ML modelinin yön isabeti 2023 %62, 2024 %58 ama hareket masrafa yetmiyor; (3) "yeni tepe + zayıf vadeli alım" uyumsuzluğu 24 s yönünde %63/%55/%60. Bu tur bunları birleştirir. Hesaplardan önce yazıldı; sonradan değiştirilmez. Ortak tanımlar ve şartlar PROTOKOL_btcyon.md ile aynı (K 2022–23 · C1 2024 · C2 2025–26; Z1/Z3'te K yalnız 2023). Canlıya yalnız kullanıcı onayıyla._

## Hareket penceresi (btcneden B2'den, eşikler K'den)
**P** = saat sonunda oynaklık oranı (24 s / 720 s) K'nin üst %30'unda **veya** sonraki 4 s bloğu 12–16 UTC.

## Z1 — Yön modeli yalnız hareket penceresinde
- btcyon Y5'in aynısı (LightGBM, aylık yürüyen eğitim, 4 s ve 24 s, olasılık eğitim tahminlerinin üst/alt %10'u). Fark: işlem yalnız P doğruyken açılır.
- Bilgi: aynı işlemler limit emirle (giriş ve çıkış %0,02, kayma yok) yapılsaydı net.
- Plasebo: eğitim etiketleri karıştırılmış aynı süreç.

## Z2 — Uyumsuzluk + kalabalık + trend
- btcyon2 Y10 vadeli uyumsuzluğu, yön mantıktan sabit: negatif (yeni 72 s tepe, kümülatif agresif alım önceki tepeden zayıf) → SAT · pozitif → AL; 24 s ve 72 s.
- Filtreler (ayrı ayrı ve birlikte): **a** kalabalık: SAT için hesap L/S z (180 g) ≥ 0, AL için ≤ 0 · **b** trend: SAT için fiyat < 200 g ort., AL için > 200 g ort. · **c** P penceresi.
- Plasebo: zaman kaydırma ×20.

## Z3 — Büyük hareketin yönü modeli
- Eğitim yalnız sonraki 4 s'te büyük hareket olan saatlerde (|r| ≥ 2,5σ4 ve ≥ %1,5); hedef hareketin işareti. Özellikler Z1 ile aynı. Aylık yürüyen eğitim.
- İşlem: P doğru ve model olasılığı eğitim tahminlerinin üst/alt %20'sinde → 4 s AL/SAT.
- Plasebo: eğitim etiketleri karıştırılmış.

## Z4 — Günlük skor yalnız trend yönünde
- btcyon Y1 ridge skoru (1 / 3 / 7 g). Fiyat > 200 g ort. iken yalnız AL sinyalleri, altındayken yalnız SAT sinyalleri.
- Plasebo: zaman kaydırma ×20.

## Karar
"Yön bulundu" ve "sinyal adayı" şartları btcyon ile aynı. Geçen çıkarsa ETH ve SOL'da aynı BTC sinyali (C1 ∪ C2).
