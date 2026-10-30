# Önceden yazılı protokol — PARA KAZANDIRAN SİSTEM İÇİN DÖRT YOL (dortyol · 30.10.2026)
_Kullanıcı (30.10): "1'den başla sırayla 4'e kadar test et; tüm testler bitince söyle, onaylarsam koda işleriz." Bu dosya hesaplardan önce yazıldı; sonradan değiştirilmez (gerekirse tarihli "Ek"). Hiçbir sonuç kullanıcı onayı olmadan canlıya girmez._

## Ortak veri
- Sinyaller: veri_seti.csv.gz ⋈ karal2_veri.csv.gz (ikisi de TEKRARSIZ). Ana ölçü **D_T0** = 7. dakika açılışından piyasa giriş (kullanıcının pratiği), sınıf 🎯'si, vadeli ücret + fonlama. Bilgi: B_T0 (limit).
- Dönemler: **A** 2022-06 → 2024 · **B** 2025 · **C** 2026 (→ 21.10). 💎 ELİT = ✅ ana ∧ (rz ≤ −2 ∨ fon ≥ 2 ∨ 🔀).

## YOL 1 — Para yönetimi (portföy simülasyonu)
- 1.000 $ başlangıç · kaldıraç 2x (teminat = pozisyon / 2) · açık teminat toplamı ≤ özsermaye (yer yoksa sinyal atlanır) · pozisyon t → t + H + 10 dk kilitli sayılır (🎯 erken kapansa bile — kötümser).
- **P0 eşit:** her ✅ ana pozisyon = özsermayenin %10'u. **P1 saat bütçesi:** P0 + aynı saatteki toplam ≤ %40 (eşit küçültme). **P2 ELİT ağırlıklı:** ELİT %20 · ELİT dışı %5 · saat bütçesi %40. **P3 oynaklık ayarlı:** %10 × (medyan s / s), [0,5 · 2] ile sınırlı · saat bütçesi. **P4 = P2 + düşüş freni:** özsermaye zirveden %15+ aşağıdayken tüm paylar ×0,5. **P5 = P2 + 🔸 yedek %2.**
- Ölçü (dönem başına ve tümü): yıllık getiri · aylık ort. · kârlı ay % · en büyük düşüş (max DD) · en kötü ay.
- **Seçim:** her dönemde yıllık getirisi > 0 olanlar arasında (tüm dönem yıllık getiri / max DD) en yüksek olan. (Karar değil — kullanıcıya sunulur.)

## YOL 2 — Yürütme maliyeti
- Gecikme kaybı = ort. (P / G − 1) (mesaj 7. dk fiyatı / sinyal kapanışı) ✅ ana ve ELİT için, dönem başına. "Anında giriş" tahmini net ≈ D_T0 + (G'den girilseydi kazanılacak fark) = D_T0 + (P − G)/G.
- Ücret payı: işlem başı ücret (giriş %0,05 + çıkış %0,02/0,05) / brüt kâr. "Hepsi limit (maker)" senaryosu: giriş + çıkış %0,02.
- **Karar şartı (öneri için):** anında giriş + maker ile işlem başı iyileşme ≥ +%0,10 ÜÇ dönemde de → otomatik emir botu ÖNERİLİR (canlı kurulum ayrı onayla). Ayrıca YOL 1'in seçilen stratejisi bu netlerle yeniden çalıştırılır (bilgi).

## YOL 3 — Piyasa dönemi (rejim) anahtarı
- Göstergeler (sinyal anında bilinen): **R1** BTC > 200 g ort. (önceki gün kapanışı) · **R2** BTC Coinbase primi zB ≥ 0 · **R3** zB ≥ −1 · **R4** BTC 24 s ≥ −%2 · **R5** gen24 ≥ 0,3 · **R6** BTC oynaklık oranı b_vr ≤ 1,5.
- **Karar:** ✅ ana içinde "rejim açık" alt kümesi ÜÇ dönemde de: işlem başı net ≥ taban + %0,10 VE isabet ≥ taban + 2 puan VE işlemlerin ≥ %40'ı kalır. Geçenlerden A dönemi neti en yüksek → YOL 1 seçilen stratejisiyle "rejim kapalıyken pay ×0,25" portföyü; üç dönemde de (yıllık getiri / max DD) iyileşmeli.

## YOL 4 — Kesitsel sıralama modeli (yeni model)
- Evren: igne2_evren (126) + BTC + 14 ana coin · Binance vadeli 1 s mum + gerçek fonlama, 2022-01 → 2026-10.
- Özellikler (saat i kapanışında, oynaklığa göre ölçekli): getiri 1 · 4 · 24 · 72 · 168 s · oynaklık oranı 24/720 · hacim oranı 24 s / 30 g · 30 g tepe/dip uzaklığı · fonlama (son, z90) · BTC getiri 1 · 4 · 24 s · coin − BTC 24 s · aynı saatteki kesitsel sıralar (r4, r24, hacim) · saat (sin/cos).
- Etiket: i+1 açılışından i+4 kapanışına getiri / (σ·√4), saat içinde kesitsel ortalaması çıkarılmış.
- Model: LightGBM regresyon · **yürüyen test:** her ay önceki 18 ayla (en az 12) yeniden eğit, sonraki ayı tahmin et · test 2024-01 → 2026-10.
- Strateji: her saat en yüksek tahminli 1 coin; yalnız tahmin, eğitim tahminlerinin %90 yüzdeliğinin üstündeyse · aynı coin 4 s bekleme · giriş i+1 açılışı × (1 + %0,1) piyasa · çıkış 4 s sonu ya da 🎯 0,75σ (saatlik mum, aynı mumda kötümser) · ücret + %0,01/8 s fonlama.
- Kıyas: aynı saatlerde rastgele coin · plasebo (etiketleri saat içinde karıştırılmış model).
- **Karar:** 2024 · 2025 · 2026'nın HER birinde: işlem başı net ≥ +%0,40 VE isabet ≥ %60 VE rastgele coin'den ≥ +%0,30 iyi VE plasebo bu şartları sağlamıyor.

## Rapor
- Dört yol bitince tek rapor; geçen/geçmeyen açıkça. Canlıya yalnız kullanıcı onayıyla.
