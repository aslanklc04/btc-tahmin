# Önceden yazılı protokol — İŞLEM ÇİFTİ KALDIRMA / EKLEME DUYURULARI: SESSİZ İLGİ GÖSTERGESİ (cift · 12.11.2026)
_Kullanıcı (12.11): "Ekle, sonra aramaya devam." Fikir: Binance neredeyse her hafta "Notice of Removal of Spot Trading Pairs" yayınlar (ör. XXX/BTC, XXX/FDUSD kaldırılır; XXX/USDT kalır).
Gerekçesi düşük likidite/hacimdir → coin'e ilginin söndüğünün resmi, sıkıcı ve kimsenin haber saymadığı bir işareti; izleme etiketi ve listeden çıkarmanın da öncüsü olabilir.
Ayna fikir: yeni çift EKLENEN coin'e ilgi artıyor. Duyuru gövdeleri görülmeden ve hesaptan önce yazıldı._

## Veri
- duyuru_liste.json'daki başlığında "Trading Pairs" geçen duyuruların (Margin/Futures/Options hariç, 2022-01 →) GÖVDELERİ (Binance CMS, Neon üzerinden); gövdedeki ÇİFT kalıpları (XXX/YYY).
- Fiyat: yeniliste_mum/fon (USDT-M COIN perpetual, günlük, kapatılanlar dahil).
## Olaylar (g = duyurunun UTC günü; taban coin'in o gün işlem gören USDT perpetual'ı var)
- **PR çift kaldırma:** başlık "Removal of ... Trading Pairs" → gövdedeki çiftlerin taban coin'leri. **PA çift ekleme:** başlık "Add(s) ... Trading Pairs" → eklenen çiftlerin taban coin'leri.
- Hariç (önceden): taban ∈ {BTC ETH BNB SOL XRP DOGE ADA TRX LINK AVAX LTC DOT} ve sabit paralar (konu coin değil karşı taraf) ·
  karşı taraf ∈ {BUSD TUSD USDP PAX USDS AEUR UST DAI BIDR IDRT UAH RUB NGN GBP AUD VAI BKRW ZAR PLN RON ARS JPY MXN CZK COP} olan çiftler (kaldırılan/eklenen şey karşı para birimi) ·
  XXX/USDT çiftinin kendisi kaldırılıyorsa (bu listeden çıkarmadır, PROTOKOL_duyuru D).
- Aynı coin + tür için 30 gün içinde ikinci olay sayılmaz.
## İşlem
- PR → SHORT · PA → LONG. Giriş g+1 açılışı (kayma %0,10 aleyhe), çıkış g+H kapanışı (kayma %0,10), H ∈ {7 · 14 · 30}. Ücret %0,05 + %0,05 · gerçek fonlama · 1× · kayıp en çok −%100.
- Piyasaya göre: aynı pencerede ≥ 365 günlük tüm coin kontratlarının eşit ağırlıklı getirisi.
## Ayrım · karar (tür başına)
- Keşif: olay ≤ 2024-12-31 → H seçimi (en yüksek ort. net, ≥ 40 olay). Doğrulama: 2025 ve 2026 ayrı.
- **"Bulundu":** 2025 ve 2026'nın her birinde ≥ 30 olay · ort. net ≥ +%2 · medyan > 0 · kazanma ≥ %55 · piyasaya göre ort. > 0 · ≤ −%50 oranı ≤ %10 ·
  aynı coin'lerde rastgele (olaysız) günlerde aynı işlemin (×200) ort. net %95'inden yüksek.
- Olay sayısı yetmezse "veri yetersiz". Bilgi: tüm H tablosu, duyuru günü getirisi, en kötü işlem, fonlama, haftada olay.
