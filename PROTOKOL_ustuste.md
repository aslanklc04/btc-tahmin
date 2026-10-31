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

## Ek 1 (31.10.2026, ilk sonuçlardan SONRA, hesaptan önce yazıldı) — "önceki sinyal zaten tuttu mu?"
_İlk sonuç: üst üste olmak tek başına fark yaratmıyor; ama önceki sinyal (S1) sonunda tuttuysa S2 %75·%75·%76, tutmadıysa %59·%57·%54. S1'in sonu S2 anında bilinmez; bilinen kısmı test edilir. Bu hipotez veriye bakılarak doğdu — bu yüzden şart, kontrol grubu ve üç dönem şartı aynen geçerli, ayrıca "momentum kontrolü" eklendi._
- Coin saatlik vadeli mum (yoksa spot). S1 🎯 = G·(1 + k·s) (k sınıfın σ katı: ana 0,75 · yedek 0,50 · panelden 0,45). S1 "**zaten tuttu**": t1'den başlayan saatlerden birinin en yükseği 🎯'ye değdi VE o saatin sonu ≤ t2 (S2 anında bilinir).
- S2 grupları (üst üste olanlar): **Z1** S1 zaten tuttu · **Z2** S1 tutmadı ama S2 anında kârda (t2'den önceki saatin kapanışı > S1 giriş fiyatı P) · **Z3** S1 tutmadı ve zararda.
- Kontroller: üst üste olmayanlar · **momentum kontrolü** = üst üste olmayan ve coin'in sinyal öncesi 24 s getirisi (c_r24) Z1'in o dönemdeki medyanından yüksek olanlar (Z1 yalnızca "coin zaten yükseliyordu" demek mi?).
- Karar (Z1 için, S2 sınıfı = hepsi ve ✅ ana ayrı): üç dönemde de isabet farkı ≥ +5 puan VE net farkı ≥ +%0,10 hem üst üste olmayanlara hem momentum kontrolüne; her dönem ≥ 30. "Sinyal adayı": üç dönemde isabet ≥ %70 ve net > 0. Z3 için aynı şartlar ters yönde ("S2'yi atla" kuralı).

## Ek 2 (31.10.2026, kullanıcı: "direkt ekle ama önce tüm testleri yap") — 📋 panelden + önceki 🎯 vurmuş (Z1) için sağlamlık testleri (hesaptan önce)
- **T1 coin yarıları:** coin adının md5'inin tek/çift olmasına göre iki ayrı coin grubu. Her yarıda (tüm dönemler birlikte) isabet ≥ %70 ve net > 0, her dönemde ≥ %65.
- **T2 limit giriş (B_T0):** her dönemde Z1 isabeti üst üste olmayan 📋'den ≥ +3 puan (bilgi + destek).
- **T3 katı vuruş:** S1'in ilk saati (mesajdan önceki dakikaları içerir) sayılmaz; vuruş t1 + 1 s'ten sonraki saatlerde. Z1 yine üç dönemde ≥ %70 ve net > 0.
- **T4 aylık istikrar:** en az 5 Z1 sinyali olan aylarda Z1 isabeti, üst üste olmayan 📋'nin o ayki isabetinden ≥ olan ayların oranı ≥ %60.
- **T5 coin yoğunluğu:** en çok Z1 sinyali veren 5 coin çıkarılınca (tüm dönemler) isabet ≥ %70 ve net > 0, her dönemde ≥ %65.
- **T6 bilgi:** S1'in sınıfı ve ufku, vuruşun ne kadar önce olduğu (son 4 s / daha önce).
- **T7 canlı (12.10.2026 →, durum/karne_gercek.csv):** canlıda gönderilmiş sinyallerde aynı ölçüm (az örnek; bilgi).
- **Karar:** T1, T3, T4 ve T5 geçerse kullanıcının talimatıyla mesajlara "♻️ önceki sinyal 🎯 vurdu" işareti eklenir (📋 panelden için test sonucuyla; diğer sınıflarda yalnız bilgi). Biri geçmezse eklenmez, sonuç raporlanır.
