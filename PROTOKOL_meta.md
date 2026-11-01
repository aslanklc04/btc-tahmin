# Önceden yazılı protokol — META-MODEL: HANGİ SİNYAL TUTAR? (meta · 02.11.2026)
_Kullanıcı (02.11): "Gerçekten bir yol olmalı, bu yolu bul." Fon yöntemi "meta-labeling": birincil sistem sinyal üretir, ikinci model sinyalin tutup tutmayacağını tahmin eder; yalnız güvenilirler alınır, güvene göre pay verilir. Hesaptan önce yazıldı; sonradan değiştirilmez (gerekirse tarihli "Ek"). Canlıya yalnız kullanıcı onayıyla._

## Veri · etiket
- veri_seti.csv.gz ⋈ karal2_veri.csv.gz (tekrarsız; ✅ ana · 🔸 yedek · 📋 panelden), 2022-06 → 2026-10-21.
- **Etiket:** D_T0 > 0 (piyasadan giriş, sınıf 🎯'si, vadeli ücret + fonlama). Destek: B_T0.
- **Özellikler (yalnız sinyal anında bilinen):** sınıf, tür, aile, H, s (σ720·√H), z, rz, fon, zB, b_r4, b_r24, b_vr, gen24, c_r4, c_r24, hod, dow, aynı saatteki sinyal sayısı, coin'in **o ana kadar sonuçlanmış** son 20 sinyalinin isabeti ve ortalama neti (sonucu t'den önce kesinleşenler; yoksa boş).

## Model · yürüyen test
- HistGradientBoostingClassifier (max_iter 300, learning_rate 0,05, max_leaf_nodes 31, min_samples_leaf 100, random_state 0).
- **Aylık yürüyen test 2024-01 → 2026-10:** her ay m için eğitim = sinyal zamanı < m − 8 gün (etiket süresi ≤ 7 g, sızıntı yok); m ayının sinyalleri tahmin edilir. Böylece 2024, 2025, 2026'nın tamamı örneklem dışı.
- **Seçim kuralları (2 deneme, önceden sabit):** Q50 = olasılık ≥ o eğitimdeki tahminlerin medyanı · Q70 = ≥ %70'lik dilim (üst %30).

## Değerlendirme (her yıl ayrı: 2024 · 2025 · 2026; tümü ve sınıf başına)
- Taban = aynı yılın tüm sinyalleri. Filtreli = kuraldan geçenler.
- **"İşe yarıyor":** ÜÇ yılda da isabet ≥ taban + 5 puan VE işlem başı net ≥ taban + %0,10 VE sinyallerin ≥ %20'si kalır; B_T0 ile de üç yılda net farkı > 0.
- **"Hedef":** ÜÇ yılda da filtreli isabet ≥ %80 VE net ≥ +%0,50.
- **Plasebo:** etiketler ay içinde karıştırılarak aynı yürüyen test ×10 → plasebo filtreli isabet/net farkları; gerçek fark plasebo dağılımının en büyüğünü üç yılda da aşmalı.
- **Bilgi:** güvene göre pay (pay = olasılık sırasına göre 0,5× / 1× / 1,5×) ile işlem başı getiri ve oynaklık; saat sepeti isabeti; özellik önemleri (permütasyon).
- Geçerse: önce gölge izleme (mesaja dokunmadan her sinyale "meta olasılığı" kaydı), sonra kullanıcı onayı.
