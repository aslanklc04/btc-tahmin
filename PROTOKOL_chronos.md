# Önceden yazılı protokol — HAVA TAHMİNİ TARZI BÜYÜK ÖN-EĞİTİMLİ MODEL (Chronos-Bolt) kriptoda (chronos · 03.11.2026)
_Kullanıcı (03.11): "Hava durumu tahmini yapan yapay zekâlar gibi kripto borsasına uyarlasak." Amazon'un milyonlarca zaman serisiyle ön-eğitilmiş Chronos-Bolt modeli, kriptoda HİÇ eğitilmeden (sıfır atış) denenir. Hesaptan önce yazıldı._

## Veri · test
- teknik3_mum: BTC, ETH + en uzun geçmişi olan 18 coin (toplam 20), saatlik kapanış.
- Model: amazon/chronos-bolt-small (CPU). Bağlam: son 512 saat. Tahmin: 24 saat ileri, medyan (ve %10/%90).
- Değerlendirme noktaları: 2025-07-01 → 2026-10-28, her gün 00 UTC (modelin yayınından sonra; sızıntı yok).
- **Yön isabeti:** ufuk 1 · 4 · 24 saat için medyan tahmin > son kapanış ⇔ gerçek getiri > 0.
- **İşlem (24 s):** medyan tahmin ≥ son kapanış × 1,0025 ise AL, 24 s tut; ücret %0,25 (gidiş-dönüş, kayma dahil).
- **Kıyaslar:** (a) her gün AL · (b) momentum: son 24 s yükseldiyse AL · (c) yazı-tura (×50).
- **%80 aralık kalibrasyonu (bilgi):** gerçek 24 s fiyatı %10–%90 aralığında kalma oranı.

## Karar
**"İşe yarıyor":** 24 s yön isabeti ≥ %53 VE işlem başı net > 0 VE (a), (b) ve yazı-turanın en iyisinden yüksek — 2025-H2 ve 2026'da ayrı ayrı.
