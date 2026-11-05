# Önceden yazılı protokol — BİNANCE'TE YENİ LİSTELENEN VADELİ KONTRATLAR: LİSTELEME SONRASI DÜŞÜŞ (yeniliste · 05.11.2026)
_Kullanıcı (05.11): "Borsayı alt etmenin yollarını araştır, bul." Kaynak: 2023 Binance vadeli listelemeleri üzerine bir çalışma (FMZ/stocksharp: yeni kontratlar listelemeden sonra
çoğunlukla düşüyor, piyasaya göre de) ve BitMEX 2025-Q1 raporu (Binance listelemelerinin %50'si zirvesini ilk gün görüyor). Bu araştırmada hiç sınanmadı. Hesaptan önce yazıldı._

## Veri (hayatta kalan yanlılığı yok)
- data.binance.vision USDT-M vadeli: TÜM semboller (kapatılanlar dahil) 1 g mumları + fonlama oranları.
- Olay: ilk günlük mumu ≥ 2021-01-01 olan ...USDT perpetual (vade tarihli `_YYMMDD`, BTCDOM/DEFI gibi endeksler, USDC/FDUSD/TUSD gibi sabitler, XAU/XAG ve tokenize hisse hariç). Aynı coin'in 1000-ön ekli ikinci kontratı ayrı olay sayılmaz (ilki).
## İşlem
- Short: listelemeden k gün sonra (L+k) açılışta, H gün sonra kapanışta çıkış. k ∈ {1 · 3 · 7} × H ∈ {7 · 14 · 30} (9 ayar).
- Maliyet: giriş + çıkış ücret %0,05 + kayma %0,10 (her biri) + gerçek fonlama (short pozitif fonlamada alır, negatifte öder). Kaldıraç 1×; getiri = −(çıkış/giriş − 1) − maliyet; zarar −%100'de kesilir (tasfiye).
- Piyasaya göre: aynı pencerede o gün listede olan ve ≥ 365 gündür işlem gören tüm kontratların eşit ağırlıklı getirisi; piyasaya göre net = net + piyasa getirisi (short'un piyasa payı çıkarılır).
## Ayrım · karar
- Keşif: listeleme 2021-01 → 2023-12 · doğrulama: 2024 · 2025 · 2026 ayrı.
- Ayar seçimi YALNIZ keşifte (en yüksek ortalama net, ≥ 40 olay).
- **"Bulundu":** seçilen ayar 2024, 2025, 2026'nın HER BİRİNDE ≥ 20 olay · ortalama net ≥ +%2 · medyan net > 0 · kazanma ≥ %55 · piyasaya göre ortalama net > 0 · −%50'den kötü işlem oranı ≤ %10.
- Bilgi: tüm ayarlar tablosu, en kötü işlem, −%30 stoplu sürüm (günlük yüksekle; aynı gün değerse stop sayılır), yılda olay sayısı.
