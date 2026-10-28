# Önceden yazılı protokol — BTC / ETH ÇOK GÜNLÜK: opsiyon korkusu, zincir üstü akış, korku endeksi, fonlama (kesif7 · 28.10.2026)
_kesif5 / 6 / 6c: fiyat + fonlama tabanlı ~1.300 altcoin kuralı 2025–26'da tutmadı. Bu sistemde HİÇ kullanılmamış veri türleri: Deribit DVOL (opsiyon zımni oynaklığı), CoinMetrics borsa giriş/çıkışları, korku-açgözlülük endeksi. Hedef: işlem başı ≥ +%2 ve isabet ≥ %70 (çok günlük tutuş). Bu dosya veri işlenmeden yazıldı; sonradan değiştirilmez._

## Veri (GitHub Actions'tan erişilebilir — veri_yokla2.md)
- Binance USDT-M vadeli 1 s mum + gerçek fonlama: BTCUSDT, ETHUSDT (2022-01 → 2026-10-25).
- Deribit DVOL (BTC, ETH) saatlik · CoinMetrics community FlowInExNtv / FlowOutExNtv (btc, eth) günlük · alternative.me korku-açgözlülük (günlük, piyasa geneli).

## Olay (her gün 00:00 UTC; yalnız ÖNCEDEN bilinen veri: akışlar D−2, endeks D−1, DVOL 00:00) · varlık başına aile başına 3 gün bekleme
- **D1 DVOL korku sıçraması:** DVOL(00:00) / DVOL(3 gün önce) − 1 ≥ {+%15 · +%25}.
- **D2 Borsadan net çıkış:** 7 günlük (çıkış − giriş) toplamının, önceki 365 günün 7 günlük toplamlarına göre z'si ≥ {1,5 · 2,5}.
- **D3 Borsaya giriş patlaması + düşüş:** günlük giriş z (365 g) ≥ {2,5 · 3,5} VE 3 günlük getiri ≤ {0 · −%5}.
- **D4 Aşırı korku:** korku-açgözlülük ≤ {15 · 25}.
- **D5 Negatif fonlama + düşüş:** son 3 günün ort. fonlaması < 0 VE 7 günlük getiri ≤ {−%5 · −%10}.
- → 2 + 2 + 4 + 2 + 4 = **14 giriş** (BTC ve ETH birlikte).

## İşlem (long)
- Giriş: D günü 01:00 UTC saatinin açılışı × (1 + %0,1), piyasa %0,05.
- Hedef T ∈ {%3 · %5 · %8} (limit %0,02) · stop: yok · −%8 · −%12 (dolum = min(stop, mum açılışı) × (1 − %0,3); aynı mumda hedef + stop → stop) · süre H ∈ {3 · 7 · 14} gün, sonunda piyasa. Gerçek fonlama (Ekim 2026: %0,01/8 s varsayılır).
- 2x likidasyon: stopsuzda en düşük ≤ −%45.
- → 27 çıkış · toplam 14 × 27 = **378 kural**.

## Dönemler ve karar (örnek az → üç dönem)
- **Keşif:** 2022-06-01 → 2023-12-31 · **Kontrol 1:** 2024 · **Kontrol 2:** 2025-01-01 → 2026-10-25.
- Keşifte geçen (isabet ≥ %70 · işlem başı net ≥ +%2 · ≥ 8 işlem · likidasyon 0) kurallar iki kontrolde de AYNI şartları (≥ 5 işlem) sağlamalı.
- Birden çok geçerse: üç dönemin en kötü netine göre ilk 3 raporlanır. Örnek az olduğu için GEÇSE BİLE önce 🧪 gölge izleme önerilir; bakılmamış coin doğrulaması yapılamaz (veri yalnız BTC/ETH) — bu, sonucun en zayıf yanı olarak yazılır.

## Ek (28.10.2026, veri işlenmeden ÖNCE — sayım düzeltmesi)
- D5 iki seçeneklidir: 2 + 2 + 4 + 2 + 2 = **12 giriş** · 12 × 27 = **324 kural** (metindeki 14 / 378 yanlış sayım). Başka değişiklik yok.
