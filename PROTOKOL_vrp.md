# Önceden yazılı protokol — OYNAKLIK PRİMİ SATIŞI, ZAMANLAMA BİZİM OYNAKLIK BİLGİMİZLE (vrp · 04.11.2026)
_Kullanıcı (04.11): "O zaman sen bir şeyler üret, bul." Fikir: araştırmanın kanıtlanmış tek gücü oynaklık zamanlaması. Opsiyon piyasasında
ima edilen oynaklık (IV) çoğu zaman gerçekleşenden yüksektir (oynaklık primi); opsiyon SATAN bunu kazanır ama fırtına günlerinde büyük kaybeder.
Soru: fırtınayı önceden sezen göstergelerimizle yalnız sakin günlerde satmak primi korur, kuyruk riskini keser mi? Hesaptan önce yazıldı; canlıya yalnız onayla._

## Veri
- btcyon5_opsiyon.parquet (BTC opsiyon işlemleri, iv · endeks · vade · kullanım fiyatı, 2022-01 → 2026-10-28).
- teknik3_mum BTC 1 s (BTC fiyatı, oynaklık).
- **Günlük IV (08:00 UTC):** 07:00–08:00 arası işlemlerden vadesi 20–52 saat sonra olan, |kullanım/endeks − 1| ≤ %2, 5 < iv < 300 olanların iv medyanı (≥ 5 işlem yoksa o gün yok).

## İşlem (yaklaşık; gerçek opsiyon fiyatı yerine IV'den)
- Her gün 08:00 UTC 1 günlük ATM straddle (alım + satım) SATILIR, ertesi gün 08:00'de vade. Prim ≈ 0,7979 · σ · √(1/365) · S, σ = (IV − 2 puan) / 100 (alış-satış farkı için kötümser).
- Kâr/zarar (S'nin yüzdesi) = prim − |S₁/S₀ − 1| − %0,08 (iki bacak ücret + teslim). S₀/S₁: BTC 08:00 kapanışları.
## Kurallar (göstergeler 08:00'de bilinen)
- R0 her gün sat (taban oynaklık primi) · R1 BTC b_vr (σ24/σ720) < 1,0 ise sat · R2 IV / (σ24 yıllık) ≥ 1,2 ise sat · R3 R1 ∧ R2 · R4 son 24 saatte ✅ ana sinyal yoksa sat.
## Değerlendirme (2022 · 2023–24 · 2025 · 2026 ayrı)
- Gün sayısı, işlem başı ort. %, kazanma oranı, en kötü gün, en büyük birikimli düşüş (günlük toplam), ort./sd.
- **Kural "işe yarar":** HER dönemde ort. > R0'ın ort. VE ort. > 0 VE en kötü gün R0'ınkinden iyi VE aynı sayıda rastgele gün seçiminin (×200) ortalama dağılımının %95'inden yüksek ort.
- Not: bu bir kâğıt üstü yaklaşımdır (gerçek alış-satış fiyatları değil IV'den); geçen olursa canlı öncesi gerçek opsiyon fiyatlarıyla ayrıca sınanır.
