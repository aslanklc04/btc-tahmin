# Önceden yazılı protokol — SERT YÜKSELİŞTEN SONRA SHORT · SERT ÇÖKÜŞTEN SONRA LONG (tersine · 06.11.2026)
_Kullanıcı (06.11): "Yükselişten sonraki gün kazancı geri veriyor; buradan long ya da short çıkmaz mı?" pompaonce bilgisi (yükseliş günü kapanışından sonra 1 g medyan −%4…−6,
7 g −%7…−17) görüldükten SONRA yazıldı; bu yüzden ayar seçimi yalnız keşifte, karar yalnız doğrulama yıllarında. Hesaptan önce yazıldı._

## Veri · olay
pompa50/pompaonce ile aynı (682 coin vadelisi, günlük, kapatılanlar dahil, hisse/emtia/döviz hariç). Olay günü g: r = C[g] / C[g−1] − 1 (kazananlar listesi gibi).
- **S (short):** r ≥ eşik, eşik ∈ {+%30 · +%50}. **L (long):** r ≤ −%30.
## İşlem
- Giriş g+1 açılışı (kayma aleyhe %0,10), çıkış g+H kapanışı, H ∈ {1 · 3 · 7}. Stop ∈ {yok · S: giriş × 1,40 / L: giriş × 0,70} (günlük en yüksek/en düşük; değdiği gün stop, kayma %0,10).
- Ücret %0,05 + %0,05 · gerçek fonlama (short pozitifte alır, negatifte öder; long tersi) · 1× · kayıp en çok −%100. Aynı coin'de açık işlem varken yeni işlem yok.
## Ayrım · karar
- Keşif 2021–23: S için 12 ayar (eşik × H × stop), L için 6 ayar (H × stop) — her biri için ayrı ayrı en yüksek ort. net, ≥ 40 olay.
- **"Bulundu" (S ve L ayrı):** seçilen ayar 2024, 2025, 2026'nın HER BİRİNDE ≥ 30 olay · ort. net ≥ +%1 · medyan > 0 · kazanma ≥ %55 · ≤ −%50 oranı ≤ %10 ·
  aynı coin'lerde rastgele (olay olmayan) günlerde aynı yönlü aynı süreli işlemlerin (×200) ort. net %95'inden yüksek.
- Bilgi: tüm ayarlar tablosu, en kötü işlem, ortalama fonlama, %2'lik portföyle yıllık toplam / en kötü ay.

## Ek 1 (06.11.2026) — S (yükselişten sonra short) GEÇTİ: seçilen ayar +%50 · H 1 · stop yok. Sağlamlık testleri (hesaptan önce)
2024, 2025, 2026 her birinde (şart: ort. net > 0 ve kazanma ≥ %55; R7 hariç):
- R1 coin yarısı 0 · R2 coin yarısı 1 (md5) · R3 en çok kazandıran 5 işlem çıkarılmış · R4 kayma %0,30/taraf · R5 ödenen fonlama ×1,5 · R6 komşu ayarlar: eşik +%40 ve +%60, H 2 (ayrı ayrı) ·
- R7 portföy (her işleme %2, aynı gün en çok 10 işlem): yıllık toplam > 0 · en kötü ay ≥ −%10 · pozitif ay ≥ %55.
- Hepsi geçerse: önce GÖLGE (mesajsız, kâğıt üstü) — canlı para için en az 2 ay ve 60 işlem gölge şartı: aynı R7 ölçütleri + işlem başı ort. > 0.

## Ek 2 (07.11.2026) — Gölge kararı
Ek 1 sonucu: 10 testin 7'si geçti (R1 coin yarısı 0 · 2025, R6b eşik +%60 · 2024, R7 2026 pozitif ay %50 kaldı) → kural gereği "gölge kurulur" şartı sağlanmadı.
Kullanıcı (07.11) kararı Claude'a bıraktı: risk ve mesaj içermediği için GÖZLEM AMAÇLI gölge kurulur ve kayıtlarda bu durum yazılır.
- Gölge kuralı (değişmez): günlük değişim (C[g]/C[g−1] − 1) ≥ +%50 olan COIN perpetual'lar (Neon /bilgi; hisse/emtia/döviz hariç) → g+1 açılışında kâğıt üstü short
  (kayma %0,10 aleyhe), g+1 kapanışında çıkış (kayma %0,10), ücret %0,05 + %0,05, gerçek fonlama (aylık arşivle kesinleşir), 1×, her işleme %2; aynı gün en çok 10 işlem
  (en yüksek günlük değişimden başlayarak — karar anında bilinen sıra).
- Canlı para şartı: ≥ 2 ay ve ≥ 60 kapanan işlem · toplam > 0 · en kötü ay ≥ −%10 · pozitif ay ≥ %55 · işlem başı ort. > 0.
- Not: Ek 1 R7'de "günde en çok 10" seçimi sonuca göre (en kötü 10) yapılmıştı — kötümser ama gerçekçi değil; gölgede karar anında bilinen sıra kullanılır.
