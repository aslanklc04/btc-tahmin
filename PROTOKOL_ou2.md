# Önceden yazılı protokol — OU TERS SİNYAL, HİÇ BAKILMAMIŞ COIN'LERDE (ou2 · 04.11.2026)
_Kullanıcı (04.11): "Dikkat çekici bulguyu hiç denemediğin coin'lerde dene." ou_sonuc.md'de BTC'ye göre aşırı ucuzlayan coin'lerin çoğu ucuzlamaya devam etti (isabet %30–48). Bu gözlem SONUÇTAN doğdu; bu yüzden yalnız araştırmada hiç kullanılmamış coin'lerde test edilir. Veri indirilmeden ve hesaptan önce yazıldı; sonradan değiştirilmez._

## Coin'ler (ou2_veri.py, Actions)
Binance spot USDT çiftleri (işlemde), stabil coin'ler ve kaldıraçlı tokenlar hariç, **ou2_eski_coinler.txt'teki 141 coin hariç**; 24 s hacmine göre en büyük 120 coin; 1 s mum 2022-01 → bugün (≥ 3000 saat geçmişi olanlar). BTC: BTCUSDT spot.

## Model: ou.py ile birebir aynı (720 s kayan β, sapma e, AR(1) yarı ömür hl, z).
## Kurallar (önceden sabit)
- **I1 açığa sat:** z ≤ −2,5 VE hl ≤ 48 → sonraki saat açılışında coin SAT (vadeli kısa). Çıkış: z ≥ 0 ya da en fazla min(72, ⌈2·hl⌉) saat. Net = −(coin getirisi) − ücret %0,05 + %0,05 − kayma %0,1 + fonlama ≈ 0 (sabit sayılmaz).
- **I1-H:** kısa coin + uzun β×BTC; ek ücret %0,1.
- **I2 güçlüyü al:** z ≥ +2,5 VE hl ≤ 48 → AL; çıkış z ≤ 0 ya da aynı azami süre; ücret %0,05 + %0,05 + kayma %0,1.
- Coin başına aynı anda tek işlem (kural başına).
## Test
- Dönemler: 2022–23 · 2024 · 2025–26 (yalnız yeni coin'ler; coin yarıları md5).
- **"Sinyal adayı":** 6 hücrenin hepsinde isabet ≥ %60 VE işlem başı net ≥ +%0,30 VE ≥ 30 işlem VE plasebonun (aynı sayıda rastgele giriş, aynı süre, aynı yön ×20) en iyisinden yüksek. **"Umut verici":** hepsinde net > 0 ve plasebodan yüksek.
