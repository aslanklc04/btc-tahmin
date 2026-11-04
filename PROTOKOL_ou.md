# Önceden yazılı protokol — ORNSTEIN–UHLENBECK GERİ DÖNÜŞ SİNYALİ (ou · 04.11.2026)
_Kullanıcı (04.11): "Olasılık biliminden sinyal bul." Stokastik süreç (OU) ile coin'in BTC'ye göre sapmasının geri dönüşü. Hesaptan önce yazıldı; sonradan değiştirilmez. Canlıya yalnız kullanıcı onayıyla._

## Model (her coin, saatlik, yalnız geçmiş 720 saat)
- y = log(coin), x = log(BTC). Kayan 720 s: β = cov(x, y)/var(x), α = ort(y) − β·ort(x), sapma e = y − α − β·x.
- OU ≈ AR(1): b = corr(e_t, e_{t−1}) (720 s); yarı ömür hl = −ln 2 / ln b (0 < b < 1). z = (e − ort(e)) / std(e) (720 s).
## Sinyal (önceden sabit)
- **z ≤ −2,5 VE hl ≤ 48 s** → sonraki saat açılışında AL. Çıkış: z ≥ 0 olunca (o saatin kapanışı) ya da en fazla min(72, ⌈2·hl⌉) saat.
- **L (yalnız coin):** ücret vadeli %0,05 + %0,05, kayma %0,1, fonlama %0,01/8 s.
- **H (coin al + β×BTC sat, piyasadan bağımsız):** L'nin neti − β·BTC getirisi − ek ücret %0,1.
- Coin başına aynı anda tek işlem.
## Test
- Coin yarıları (md5: keşif / doğrulama) × dönemler (2022–23 · 2024 · 2025–26) = 6 hücre.
- **"Sinyal adayı":** 6 hücrenin hepsinde isabet ≥ %65 VE işlem başı net ≥ +%0,30 VE ≥ 30 işlem. **"Umut verici":** hepsinde isabet ≥ %60 VE net > 0.
- **Plasebo:** her coin'de aynı sayıda rastgele giriş saati (aynı çıkış kuralı: aynı süre) ×20 → hücre başına net dağılımı; gerçek net plasebonun en iyisini aşmalı.
- Bilgi: günde sinyal sayısı, ortalama süre, en kötü işlem.
