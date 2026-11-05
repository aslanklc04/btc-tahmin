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

## Ek 1 (05.11.2026, kullanıcı: "testleri yap, geçerse kur") — PORTFÖY düzeyi sağlamlık testleri (hesaptan önce)
Dürüstlük notu: k 1 · H 30 keşifte seçildi; "her listelemeye %2" portföy görünümü 2024–26 tek-işlem sonuçları görüldükten SONRA bilgi olarak hesaplandı. Bu yüzden
aşağıdaki testler daha önce bakılmamış kesitlerle ve zorlaştırılmış maliyetlerle yapılır; asıl karar canlı gölgede verilir.
- Portföy: her olaya sermayenin %2'si, 1× short, k 1 · H 30; aynı anda en çok 40 açık pozisyon (fazlası atlanır); aylık getiri = o ay kapanan işlemlerin toplamı × 0,02.
- **Şart (2024 · 2025 · 2026 AYRI AYRI, her testte):** yıllık toplam > 0 · en kötü ay ≥ −%10 · yıl içi birikimli en büyük düşüş ≥ −%20 · pozitif ay oranı ≥ %55.
- Testler: P0 temel · P1 kayma %0,30/taraf · P2 negatif fonlama ×1,5 · P3 coin yarısı 0 · P4 coin yarısı 1 (md5; her yarı %2) · P5 en çok kazandıran 5 olay çıkarılmış ·
  P6 komşu ayarlar k 3 · H 30, k 1 · H 14, k 3 · H 14 (her biri ayrı) · P7 P1 + P2 birlikte.
- **Karar:** hepsi geçerse 🆕 gölge (mesajsız) kurulur: her yeni Binance USDT-M perpetual listelemesi kaydedilir, L+1 00:00 UTC açılışında kâğıt üstü short, 30 gün; aylık karne.
  Canlı karar şartı gölgede önceden: ≥ 3 ay ve ≥ 40 kapanmış işlemde aynı portföy şartları (aylık) + işlem başı ort. > 0.

## Ek 2 (05.11.2026) — VERİ DÜZELTMESİ (sonuçtan bağımsız): hisse/emtia/döviz kontratları ayıklanır
Gölge kurulurken Binance'in sembol bilgisi (fapi exchangeInfo, Neon /bilgi) çekildi: 942 kontratın 235'i TRADIFI_PERPETUAL (hisse, emtia, döviz; çoğu 2026'da listelendi).
Bunlar "yeni coin" değil; listeleme sonrası arz/heves düşüşü mekanizması onlarda yok → olaylardan çıkarılır: yalnız underlyingType = COIN ve contractType = PERPETUAL.
(Kapatılmış eski kontratlar bilgide yok; TRADIFI 2025-12'den önce yoktu, o yüzden eski kapatılanlar coin sayılır.) Aynı kurallar ve şartlarla Ek 1 testleri yeniden çalıştırılır;
önceki (kirli) sonuçlar dosyada kalır, yerine geçen sonuç ayrıca yazılır.
