# Önceden yazılı protokol — 1 GÜNDE +%50 YÜKSELECEK COIN'İ ÖNCEDEN BULMAK (pompa50 · 06.11.2026)
_Kullanıcı (06.11): "Binance kazananlarda 1 günde %50–60 coinler var, bunları neden bulamıyorsun, araştır." Önceki PROTOKOL_pompa (141 coin, +%10/24 s): büyük hareket
bulundu ama yön yok. Fark: tüm coin vadelileri (≈ 700, kapatılanlar dahil, hisse/emtia/döviz hariç), günlük, hedef +%50. Hesaptan önce yazıldı._

## Veri · olay
- yeniliste_mum/fon (data.binance.vision, günlük 1 g) · coin = vadeli_bilgi'de COIN perpetual ya da bilgide olmayan (kapatılmış).
- Gözlem = (coin, gün t) — t kapanışında bilinenler. **Olay:** t+1 gününün en yükseği ≥ t+1 açılışı × 1,50.
## Özellikler (t kapanışında bilinen)
f1 t günü fonlama toplamı · f2 son 3 gün fonlama toplamı · f3 getiri 1 g / 3 g / 7 g · f4 hacim oranı (t / önceki 30 gün ort.) · f5 listelemeden geçen gün ·
f6 30 g en yükseğe / en düşüğe uzaklık · f7 30 g oynaklık · f8 BTC 1 g getirisi · f9 t günü üst gölge / gövde · f10 coin'in son 90 gündeki +%50 olay sayısı.
## Yöntem
- A) Tek özellik: keşifte (t < 2024) her özelliğin on dilimi; olay oranı tabana göre kat (lift). Bilgi.
- B) HistGradientBoosting (max_iter 300, lr 0,05, max_leaf_nodes 31, min_samples_leaf 100), yıllık yürüyen test: 2024, 2025, 2026 için eğitim = önceki tüm yıllar.
- Seçim: her gün olasılığı en yüksek 3 coin (yoksa az).
## İşlem (seçilenler)
- Long t+1 açılışı × 1,002 · 🎯 +%50 limit (değerse) · stop −%20 (aynı gün ikisi → stop, kötümser) · değmezse t+1 kapanışında çıkış · ücret %0,05+%0,05 + fonlama t+1.
## Karar (2024 · 2025 · 2026 ayrı)
- **"Bulundu":** seçilenlerde olay oranı ≥ 5 × taban VE işlem başı net > 0 VE aynı günlerde rastgele 3 coin seçiminin (×50) en iyisinden yüksek olay oranı ve net.
- Bilgi: olay taban oranı, günde ortalama olay sayısı, seçilenlerin olay oranı, en kötü işlem, stopsuz sürüm.
