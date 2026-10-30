# Önceden yazılı protokol — BTC'NİN YÖNÜ, 4. TUR: BALİNA, KORE, STABLECOIN (btcyon4 · 30.10.2026)
_btcyon 1–3. turlar: 297 kural, şartı geçen yok; en yakınlar "yeni tepe + zayıf vadeli alım → SAT" ve 4 s yön modeli, ikisi de 2024 boğa yılında zayıf. Bu tur daha önce hiç kullanılmamış üç para akışı kaynağını dener. Hesaplardan önce yazıldı; sonradan değiştirilmez. Ortak tanımlar/şartlar PROTOKOL_btcyon.md ile aynı (K 2022–23 · C1 2024 · C2 2025-01 → 2026-10-27). Canlıya yalnız kullanıcı onayıyla._

## Veri (btcyon4_veri.py, GitHub Actions)
- Binance vadeli BTCUSDT **1 dakikalık** mum (işlem sayısı + agresif alıcı hacmi) 2022-01 → 2026-10.
- Upbit KRW-BTC saatlik (Kore borsası) · Yahoo USD/KRW günlük kur.
- Coinbase USDT-USD saatlik (dolar → stablecoin talebi).

## W1 — Balina agresif emirleri
- Dakika başı ortalama işlem büyüklüğü = hacim / işlem sayısı. **Balina dakikası** = bir önceki takvim ayının dakikalarında %95 yüzdeliğin üstü.
- Saatlik: balina dengesizliği = Σ(agresif alım − agresif satım) / Σ hacim (yalnız balina dakikaları) · balina hacim payı.
- Durumlar: balina dengesizliği 4 s ve 24 s toplamı · balina net (alım − satım, $) 24 s z (720 s). → sonraki 4 s / 24 s / 72 s.

## W2 — Kore primi (kimchi)
- prim = Upbit KRW-BTC / (Binance BTCUSDT spot × USD/KRW) − 1 (kur son bilinen günlük kapanış).
- Durumlar: 24 s ort. z (önceki 720 s) · 24 s değişim · günlük 3 g ort. → sonraki 24 s / 72 s.

## W3 — Stablecoin talebi
- USDT primi = Coinbase USDT-USD − 1 (dolardan stablecoin'e talep).
- Durumlar: 24 s ort. z (720 s) · 24 s değişim → sonraki 24 s / 72 s.

## Kurallar ve şartlar
- Her durum K eşikleriyle üst/alt %20 → yön K'deki ortalama işaretinden; aynı anda tek işlem; giriş sonraki saat açılışı.
- **W4 birleşik:** W1–W3 durumları + btcneden B1 kalabalık L/S z + dolar 5 g + btcyon2 vadeli uyumsuzluk bayrağı → K'de ridge (λ = 10) ile 24 s getirisi; C1 için K, C2 için K+C1 ile eğitilir; skor eğitim üst/alt %10 → AL/SAT 24 s.
- "Yön bulundu" ve "sinyal adayı" şartları btcyon ile aynı; plasebo zaman kaydırma ×20 (aile başına).
