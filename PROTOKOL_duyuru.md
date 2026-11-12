# Önceden yazılı protokol — BİNANCE DUYURULARINDAN SONRAKİ GÜNLERDE FİYAT SÜRÜKLENMESİ (duyuru · 12.11.2026)
_Kullanıcı (12.11): "Kimsenin bilmediği, fark etmediği yöntemleri bul." Bu araştırmada hiç kullanılmamış veri: Binance'in kendi duyuru arşivi. Botlar duyuruya saniyeler içinde tepki verir;
burada sınanan şey İLK TEPKİDEN SONRAKİ günlerdeki sürüklenme (giriş ertesi gün açılışı). Hesaptan ve duyuru verisi görülmeden önce yazıldı._

## Veri
- Duyurular: Binance CMS (katalog 161 delisting · 48 yeni listeleme · 49 haberler), Neon (Frankfurt) üzerinden; başlık + yayın zamanı.
- Fiyat: yeniliste_mum/fon (USDT-M vadeli günlük, kapatılanlar dahil, 2020 → 2026-10) · yalnız COIN perpetual.
## Olaylar (g = duyurunun UTC günü; coin'in o gün Binance'te işlem gören USDT perpetual'ı olmalı)
- **D listeden çıkarma:** başlık "Binance Will Delist <coinler> on <tarih>" (spot; "Futures", "Margin", "Trading Pairs" içerenler hariç).
- **M izleme etiketi:** başlık "... Monitoring Tag to Include <coinler>".
- **S spot listeleme (vadelisi önceden var):** başlık "Binance Will List <ad> (<COIN>)" ve perpetual'ın ilk günü ≤ g − 7.
- Aynı coin için aynı türde 30 gün içinde ikinci olay sayılmaz.
## İşlem
- Yön: D ve M short · S short (duyuru sıçramasının geri verilmesi). Her tür için TERS yön de bilgi olarak raporlanır.
- Giriş g+1 açılışı (kayma %0,10 aleyhe), çıkış g+H kapanışı (kayma %0,10); kontrat erken kapanırsa son kapanış. H: D ∈ {1 · 3 · 7} · M ∈ {7 · 14 · 30} · S ∈ {1 · 3 · 7}.
- Ücret %0,05 + %0,05 · gerçek fonlama · 1× · kayıp en çok −%100. Piyasaya göre: aynı pencerede ≥ 365 günlük tüm coin kontratlarının eşit ağırlıklı getirisi.
## Ayrım · karar (tür başına ayrı)
- Keşif: olay ≤ 2024-12-31 → H seçimi (en yüksek ort. net, ≥ 25 olay). Doğrulama: 2025 ve 2026 ayrı.
- **"Bulundu":** 2025 ve 2026'nın her birinde ≥ 15 olay · ort. net ≥ +%2 · medyan > 0 · kazanma ≥ %55 · piyasaya göre ort. > 0 · ≤ −%50 oranı ≤ %10 ·
  aynı coin'lerde rastgele (olaysız) günlerde aynı işlemin (×200) ort. net %95'inden yüksek.
- Yeterli olay yoksa (keşif < 25 ya da doğrulama yılı < 15) "veri yetersiz" raporlanır — sonuç zorlanmaz.
- Bilgi: g günü (duyuru günü) getirisi, tüm H tablosu, en kötü işlem, ortalama fonlama.

## Ek 1 (12.11.2026, kullanıcı: "Ekle") — duyuru gölgesi (gözlem amaçlı; kural ve karar şartı önceden)
Ana test: üç türde de keşif olayı < 25 → VERİ YETERSİZ. H 7, 2025–26 tablosu görüldükten sonra seçildi (dürüstlük notu) → asıl sınav bu gölgedir.
- İzlenen: **D** "Binance Will Delist <coinler> on <tarih>" (spot) ve **S** "Binance Will List <ad> (<COIN>)" (perpetual'ı duyurudan ≥ 7 gün önce listelenmiş). M (izleme etiketi) izlenmez (2026'da ortalama eksi).
- Kural: duyurunun UTC günü g → g+1 açılışında kâğıt üstü short (kayma %0,10 aleyhe), g+7 kapanışında çıkış (kayma %0,10; kontrat erken kapanırsa son kapanış), ücret %0,05 + %0,05, gerçek fonlama, 1×, her işleme %2.
  Yalnız Binance USDT-M COIN perpetual'ı olan coin'ler (Neon /bilgi). Aynı coin + tür için 30 gün içinde ikinci olay sayılmaz. Başlangıç 12.11.2026 sonrası duyurular.
- **Önceden yazılı karar:** ≥ 40 kapanan işlem (D + S birlikte) → işlem başı ort. > 0 · medyan > 0 · kârlı ≥ %55 · −%50'den kötü ≤ %10 · %2'lik payla toplam > 0 ve en kötü ay ≥ −%10
  → gerçek parayla küçük deneme kullanıcıya sorulur. Aksi halde gölge kapatılır.
