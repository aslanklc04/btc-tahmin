# Önceden yazılı protokol — HYPERLIQUID'DE BÜYÜK VE KAZANAN HESAPLAR: KAZANÇ KALICI MI, TAKİP EDİLEBİLİR Mİ? (hl · 14.11.2026)
_Kullanıcı (04.11): "Binance'in quant masasını takip eden sistem yap" · (14.11): "Aramaya devam." Binance kendi masasını yayınlamaz; Binance Copy Trading liderlerinde kalıcılık çıkmadı (PROTOKOL_kopya ❌).
Bu araştırmada HİÇ kullanılmamış kaynak: Hyperliquid. Orada TÜM hesapların pozisyonları ve kâr/zarar geçmişi herkese açıktır (zincir üstü) — fonlar ve piyasa yapıcılar dahil; vitrin için seçilmiş liderler değil.
Soru: geçmişte kazanan büyük hesaplar sonraki ay da kazanıyor mu? Evetse pozisyonları canlı izlenip sinyal yapılabilir. Veri görülmeden ve hesaptan önce yazıldı._

## Veri
- Hyperliquid herkese açık API: sıralama tablosu (tüm hesaplar: hesap değeri, dönem kâr/zarar, hacim) + her hesabın "portfolio" geçmişi (birikimli kâr/zarar ve hesap değeri zaman serisi).
- **Evren (kâra göre DEĞİL, etkinliğe göre):** tüm zamanların işlem hacmi en yüksek 3.000 hesap. (Kâra göre seçmek geleceği görmek olurdu.)
## Yürüyen test
- Oluşum tarihleri F: her ayın 1'i, 2025-03-01 → 2026-09-01. Uygun hesap: F'den ≥ 90 gün önce geçmişi var, F'de hesap değeri ≥ 50.000 $, son 90 günde kâr/zararı değişmiş (etkin).
- Sıralama (yalnız F öncesi veri): **S1** son 90 gün kâr/zararı ($) · **S2** son 90 gün getirisi (kâr / dönem ort. hesap değeri) · **S3** istikrar: son 180 günün 30'ar günlük 6 diliminden kaçı kârlı (eşitlikte S2).
- Gruplar: en iyi %10 · en iyi 50 hesap · tüm uygun hesaplar.
- İleri getiri: (F+30 gün kârı − F kârı) / max(F'deki hesap değeri, son 30 gün ort. hesap değeri); ortalamalar için [−%100, +%300] aralığına kırpılır. Takip maliyeti/gecikmesi EKLENMEZ (iyimser).
## "Kalıcılık var" şartı (S1, S2, S3 ayrı ayrı; biri yeter)
- Oluşum tarihlerinin ≥ %70'inde en iyi %10'un medyan ileri getirisi > 0 VE > tüm uygun hesapların medyanı ·
- tüm tarihler birlikte en iyi %10: ortalama > 0, medyan > 0, kârlı hesap oranı ≥ %55 ·
- tarih başına Spearman (sıra ↔ ileri getiri) ortalamasının t değeri ≥ 2.
## Bilinen yanlılıklar (raporda yazılır)
- Sıralama tablosu batıp kapanan hesapları içermiyor olabilir → sonuç OLDUĞUNDAN İYİ görünür. Şart bu yanlılıkla bile tutmazsa güçlü "hayır"; tutarsa asıl kanıt canlı ileriye dönük izlemedir.
- Para yatırma/çekme hesap değerini bozar; paydada bu yüzden kâr/zarar serisi ve ortalama hesap değeri kullanılır.
- Geçerse sonraki adım (ayrı protokol): en iyi hesapların açık pozisyonlarını günlük kaydeden gölge + "çoğunluk yönü" sinyalinin sınanması. Teknik ayrıntılar (API alan adları, seri sıklığı) veri yapısı görülünce yazılır; ŞARTLAR değişmez.
