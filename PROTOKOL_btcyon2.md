# Önceden yazılı protokol — BTC'NİN YÖNÜ, 2. TUR (btcyon2 · 30.10.2026)
_btcyon (Y1–Y6) sonuçları beklenirken, yeni veri gerektiren ve daha önce hiç denenmemiş yön açıları için yazıldı. Hesaplardan önce kaydedilir; sonradan değiştirilmez (gerekirse tarihli "Ek"). Ortak tanımlar (yön isabeti, işlem, "yön bulundu" ve "sinyal adayı" şartları, plasebo) PROTOKOL_btcyon.md ile aynı. Canlıya yalnız kullanıcı onayıyla._

## Veri (btcyon2_veri.py, GitHub Actions)
- BTC, ETH, SOL **günlük** spot mum (Binance, 2017-08'den) · BTCUSDT vadeli **prim endeksi** 1 s (premiumIndexKlines: vadeli işaret fiyatı − spot endeks) · CoinMetrics günlük: CapMVRVCur (piyasa değeri / gerçekleşmiş değer), AdrActCnt (aktif adres), TxTfrValAdjUSD.

## Y7 — Haftalık/aylık trend (günlük veri, uzun geçmiş)
- Dönemler bu aile için: **K** 2018–2021 · **C1** 2022–2023 · **C2** 2024 → 2026-10-27.
- Kurallar (gün sonu bilinen, ertesi gün açılışında giriş): T1 kapanış > 200 g ort. → AL, altında → SAT · T2 50 g ort. > 200 g ort. → AL, değilse SAT · T3 28 g getiri > 0 → AL, < 0 → SAT · T4 7 g getiri işareti (aynı yön) · T5 yükseliş trendinde geri çekilme: kapanış > 200 g ort. ve 3 g getiri ≤ −%5 → AL · T6 düşüş trendinde tepki: kapanış < 200 g ort. ve 3 g getiri ≥ +%5 → SAT.
- Ufuk 7 · 14 · 28 gün; aynı anda tek işlem. Bilgi: yalnız AL tarafı (SAT yerine nakit) ve "al ve tut" ile kıyas.

## Y8 — Vadeli prim endeksi (vadeli − spot farkı)
- Saatlik prim endeksi; 24 s ortalaması ve önceki 720 s'e göre z. Üst/alt %20 (K eşikleri) → sonraki 4 s / 24 s; yön K'den. Günlük: 3 g ort. üst/alt %20 → 3 g. Dönemler btcyon ile aynı (K 2022–23).

## Y9 — Tasfiye mıknatısı (fiyat, kaldıraçlı pozisyonların tasfiye seviyelerine doğru mu gider?)
- Saatlik açık pozisyon artışı (adet) o saatin fiyatında açılmış sayılır; o saatte agresif alıcı baskınsa yeni pozisyon "uzun", satıcı baskınsa "kısa". Kaldıraç 10x/25x/50x eşit pay → tasfiye fiyatı uzun P·(1 − 1/L), kısa P·(1 + 1/L). Açık poz. düşüşleri tüm kayıtlardan orantılı silinir; fiyat bir tasfiye seviyesini geçince o kayıt silinir; kayıtlar 30 gün yarı ömürle söner.
- Her saat sonu: fiyatın ±%5 bandında yukarıdaki (kısa tasfiye) ve aşağıdaki (uzun tasfiye) toplam miktar; oran = log(yukarı / aşağı). Üst/alt %20 (K) → sonraki 24 s / 72 s; yön K'den (beklenen: büyük küme yönüne).

## Y10 — Fiyat / akış uyumsuzluğu
- Saat sonunda BTC son 72 s'in en düşüğünde (ya da en yükseğinde) iken, 72 s kümülatif vadeli agresif dengesizlik önceki en düşüğün (yüksek) yapıldığı andakinden yüksek (düşük) → "pozitif (negatif) uyumsuzluk". Aynısı Coinbase primiyle. → sonraki 24 s / 72 s; yön K'den.

## Y11 — Zincir üstü değerleme (uzun vade)
- MVRV z (önceki 4 yıl), aktif adres 30 g / 365 g oranı, transfer hacmi 30 g / 365 g → sonraki 28 g ve 90 g getirisi; üst/alt %20, yön K'den (Y7 dönemleri). Bağımsız örnek az olduğundan 28/90 g ufukta en az 6 işlem şartı; sonuç bilgi olarak raporlanır.

## Rapor
btcyon ile birlikte tek "yön" raporu. Geçen kural çıkarsa ETH ve SOL'da aynı kural ek kontrol.
