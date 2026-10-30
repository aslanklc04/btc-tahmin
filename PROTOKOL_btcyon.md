# Önceden yazılı protokol — BTC'NİN YÖNÜ (btcyon · 30.10.2026)
_Kullanıcı (30.10): "Oynaklığın nedenini buldun, yönünü de bulacaksın; aramaya devam." btcneden (A/B/C) ne zaman büyük hareket olacağını buldu, yönü bulamadı. Bu dosya hesaplardan önce yazıldı; sonradan değiştirilmez (gerekirse tarihli "Ek"). Veri: btcneden_saat/gun/dogrula.parquet (yeni veri yok). Canlıya yalnız kullanıcı onayıyla._

## Ortak
- Dönemler: **K** 2022–23 (keşif) · **C1** 2024 · **C2** 2025-01 → 2026-10-27.
- **Yön isabeti** = tahmin edilen yön ile gerçekleşen getirinin işaretinin aynı olma oranı. **İşlem:** giriş bir sonraki saat açılışı × (1 ± %0,1 kayma), süre sonu çıkış, vadeli ücret %0,1 gidiş-dönüş + gerçek fonlama; kural başına aynı anda tek işlem.
- Yön/eşik/model **yalnız K'den** seçilir (Y5'te yürüyen eğitim), C1 ve C2 dokunulmamış kontroldür.
- **"Yön bulundu" şartı:** her dönemde yön isabeti ≥ %57, işlem başı net > 0 ve ≥ 30 işlem (Y4: ≥ 15).
- **"Sinyal adayı" şartı:** her dönemde isabet (net > 0) ≥ %65 ve işlem başı net ≥ +%0,5 (1 g ve üstü) / +%0,2 (24 s altı).
- Her aile için plasebo: hedef seri rastgele ≥ 90 gün kaydırılır (Y5'te eğitim etiketleri karıştırılır); "tesadüfen geçen" sayısı raporlanır.

## Y1 — Bileşik yön skoru (günlük)
- Özellikler (D−1 sonunda bilinen, btcneden B1 ile aynı tanımlar): hesap L/S, büyük oyuncu L/S, fonlama 3 g, açık poz. 7 g, vadeli agresif 3 g, spot agresif 3 g, Coinbase primi 3 g, prim 3 g değişim, DVOL 3 g değişim, oynaklık 7g/60g, 30 g zirveye uzaklık, 7 g getiri, stablecoin 7 g, borsa net giriş 7 g z, Nasdaq 5 g, dolar 5 g, 10 y faiz 5 g, VIX, korku. Seviye serileri (L/S, fonlama, prim, VIX, korku) önceki 180 güne göre z.
- Model: K'de standartlaştırılmış doğrusal regresyon (ridge λ = 10) → hedef sonraki 1 / 3 / 7 gün log getirisi. C1 için K ile, C2 için K + C1 ile eğitilir.
- Kural: skor eğitim döneminin üst %20'si → AL, alt %20'si → SAT; D günü 00:00 açılışında giriş, 1 / 3 / 7 gün sonra çıkış.
- Bilgi (önceden ilan edilen sızıntı uyarısı): btcneden'de her dönemde aynı yönü gösteren 3 eğilimle "oy" kuralı (kalabalık L/S z ≥ 1 → −1, ≤ −1 → +1; dolar 5 g üst/alt %20 → −1/+1; borsa girişi z ≥ 1,5 → −1). Toplam ≥ +2 AL, ≤ −2 SAT. Yönler tüm dönemler görülerek seçildiği için yalnız bilgi; karar Y1 regresyonuyla.

## Y2 — Hareketi kim sürdü → devam mı dönüş mü?
- Olay: büyük 4 s hareket (btcneden A4 tanımı). Sınıf (bloğun kendi değerleri, önceki 180 bloğa göre z): **T** tasfiye (açık poz. z ≤ −1,5) · **L** yeni kaldıraç (açık poz. z ≥ +1,5) · **S** spot/ABD sürdü (spot agresif ya da Coinbase primi değişimi hareket yönünde |z| ≥ 1,5, T/L değil) · **D** diğer.
- Sonuç: olay bloğundan sonraki 4 s, 24 s, 72 s getirisi. Her sınıf × ufuk için yön (devam/dönüş) K'nin ortalama işaretinden seçilir, C1/C2'de test edilir.
- Aynısı günlük: büyük gün etiketleri (btcneden A3: 💥, 🎰, 🇺🇸, 🏛️, ❓) → sonraki 1 / 3 / 7 gün.

## Y3 — ABD seansının yönü (hafta içi)
- Hedef: 13:00 → 21:00 UTC BTC getirisi. Bilinen (13:00'te): 00→13 getiri · Coinbase primi 00→13 değişim · 12:00 prim z (720 s) · vadeli ve spot agresif 00→13 · açık poz. 00→13 · fonlama · önceki ABD günü ETF akışı z · önceki gün Nasdaq ve dolar getirisi · önceki ABD seansı getirisi (13→21).
- Her biri: K eşikleriyle üst/alt %20 → yön K'deki ortalama işaretinden. Ayrıca K'de eğitilmiş ridge bileşik (Y1 gibi).
- Bilgi: ABD seansının dönem başına ortalama yönü ve Asya (00→08), Avrupa (08→13) seanslarıyla karşılaştırma.

## Y4 — Hafta sonu ve CME boşluğu
- Cuma 21:00 UTC fiyatı F, pazar 23:00 UTC fiyatı S, boşluk g = S / F − 1. Hafta içinde (pazartesi 00:00 → cuma 21:00) fiyatın F'ye dokunma oranı, |g| dilimlerine göre (%0,5 · %1 · %2 · %3+).
- Kural: |g| ≥ %1 ise pazar 23:00'te F yönüne giriş, 🎯 F, çıkış cuma 21:00 (stop yok / boşluk kadar ters).
- Bilgi: cuma ABD seansı getirisi → hafta sonu getirisi; hafta sonu getirisi → pazartesi getirisi (devam/dönüş).

## Y5 — Makine öğrenmesi yön modeli (saatlik)
- Özellikler: btcneden B2'nin saatlik durumları + B1 günlük durumları (son bilinen) + saat/gün. Hedef: sonraki 4 s ve 24 s getirisinin işareti.
- LightGBM sınıflandırma; aylık yürüyen eğitim (başlangıçtan bir ay önceye kadar tüm veri, son 24 s atılır), test 2023-01 → 2026-10. Dönemler: K'nin yalnız 2023'ü, C1, C2.
- Kural: olasılık, eğitim tahminlerinin üst %10'unda → AL, alt %10'unda → SAT. Plasebo: eğitim etiketleri karıştırılmış aynı süreç.

## Y6 — Öncü coin ve akış (saatlik)
- Son saatteki ETH getirisi, SOL getirisi, Coinbase primi değişimi, vadeli agresif ve spot agresif → BTC'nin sonraki 1 s ve 4 s getirisi. Üst/alt %20 dilim, yön K'den.

## Rapor
Her aile için geçen/geçmeyen, plasebo, sade dille "yön için ne bulundu". Sinyal adayı çıkarsa ETH ve SOL'da aynı kural (C1 ∪ C2, net > 0) ek kontrol olarak raporlanır.
