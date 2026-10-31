# Önceden yazılı protokol — ÜST ÜSTE SİNYAL (ustuste · 31.10.2026)
_Kullanıcı (31.10): "Bir coinde 24 s sinyali geliyor, o dolmadan aynı coin için 8 s sinyali geliyor ve 8 s tutuyor. Sadece 24 ve 8 değil, diğer sinyallerde de böyle oluyor. Buradan bir şey çıkar mı?" Bu dosya hesaptan önce yazıldı; sonradan değiştirilmez (gerekirse tarihli "Ek"). Canlıya yalnız kullanıcı onayıyla._

## Veri
- Gönderilen tüm sinyaller: veri_seti.csv.gz (✅ ana · 🔸 yedek · 📋 panelden; tekrarlar (t, coin, sınıf, ufuk) anahtarıyla atılır) ⋈ karal2_veri.csv.gz.
- Sonuç: **D_T0** (7. dakikada piyasa giriş, sınıf 🎯'si, vadeli ücret + fonlama; kullanıcının pratiği) · isabet = D_T0 > 0. Bilgi: B_T0 (mesaj fiyatına limit).
- Dönemler (ELİT satırıyla aynı): **A** 2022-06 → 2024 · **B** 2025 · **C** 2026 (→ veri sonu).

## Tanım
- S2 (coin c, saat t2, ufuk H2) **üst üste**dir: aynı coin için daha önce gelen bir S1 (saat t1, ufuk H1) varsa ve t1 < t2 < t1 + H1 (S1'in süresi henüz dolmamış).
- Türler: **U1** herhangi bir açık S1 · **U2** açık S1'in ufku daha uzun (H1 > H2; ör. 24 s açıkken 8 s) · **U3** açık S1'in ufku aynı (H1 = H2) · **U4** açık S1'in ufku daha kısa (H1 < H2) · **U5** aynı anda ≥ 2 açık S1.
- **Kontrol (piyasa etkisini ayırmak için):** aynı coin'de açık sinyal yok ama aynı anda BAŞKA bir coin'de açık sinyal var. Üst üste etkisi "aynı coin"e özgü olmalı.

## Ölçüler
Her tür × S2 sınıfı (hepsi, ✅ ana, 🔸 yedek, 📋 panelden) × dönem: sinyal sayısı · isabet · işlem başı net (D_T0) · fark (üst üste − üst üste olmayan) · fark (üst üste − kontrol).

## Karar
- **"Üst üste işe yarıyor":** bir tür için (S2 sınıfı = hepsi ve ✅ ana ayrı ayrı) ÜÇ dönemde de isabet farkı ≥ +5 puan VE net farkı ≥ +%0,10, hem üst üste olmayanlara hem kontrole göre; her dönemde ≥ 30 üst üste sinyal.
- **"Sinyal adayı":** üst üste sinyaller ÜÇ dönemde de isabet ≥ %70 ve net > 0 (≥ 30).
- Ek kontrol: aynı yönde S1'in sonucu (S1 tuttu mu) S2'yi etkiliyor mu → bilgi (S1'in sonucu S2 anında bilinmediği için kural olamaz).
