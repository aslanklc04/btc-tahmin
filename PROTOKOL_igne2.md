# Önceden yazılı protokol — GÜNLÜK İĞNE EMRİ + TREND FİLTRESİ, HİÇ BAKILMAMIŞ coin'lerde (igne2 · 27.10.2026)
_igne_sonuc.md: günlük derin limit (B) BTC + 14 ana coin'de 2023 ikinci yarı → 2024 ve 2026'da çok iyi, 2022–23 düşüş piyasasında kötü; 10.10.2025 çöküşünde 2x'te 10 likidasyon. Trend filtresi fikri BU SONUCA BAKILARAK bulundu → o 15 coin'de kanıt sayılmaz (yalnız bilgi). Karar, günlük iğne kuralının HİÇ hesaplanmadığı 126 coin'de (durum/genis_liste.txt) verilir. Kullanıcı (27.10): "yap". Bu dosya veri işlenmeden yazıldı; sonradan değiştirilmez._

## Veri
- Binance USDT-M vadeli 1 dk mum (data.binance.vision), 2022-06-01 → 2026-10-25. Sembol yoksa "1000"+coin. Vadeli işlemi olmayan / başlamamış günler atlanır.
- **Evren (karar):** durum/genis_liste.txt'teki 126 coin (bugünkü listeden — listeden çıkmış coin'ler yok → sonuçlar iyimser olabilir; bu yüzden şartlar sıkı).
- **Bilgi:** BTC + 14 ana coin (igne'de görüldü).

## Kural (igne B ile aynı ölçüm)
- Her gün 00:00 UTC (03:00 TR): P = 00:00 açılışı · σd = önceki 720 saatlik 1 s log getiri std'si × √24 · L = P·(1 − d·σd), gün boyu geçerli limit alış (dolum: Lo < L).
- **Trend filtresi:** emir yalnız BTC'nin (vadeli BTCUSDT) ÖNCEKİ günlük kapanışı son 200 günlük kapanış ortalamasının üstündeyse konur.
- **Çıkış:** hedef = P (tam geri dönüş, limit ücreti); değmezse dolumdan 24 saat sonra piyasa.
- **Stop (3 seçenek):** yok · S½: L·(1 − ½·d·σd) · S1: L·(1 − d·σd). Stop dolumu = min(stop, o dakikanın açılışı) × (1 − %0,3) kayma, piyasa ücreti. Aynı dakikada hedef ve stop → stop (kötümser).
- d ∈ {3 · 4} → 2 × 3 = **6 kural**.
- Ücret: limit %0,02 · piyasa %0,05 · fonlama %0,01 / geçilen 00-08-16 UTC.

## Ölçü
- işlem isabeti (net > 0) · işlem başı net · gün isabeti (o gün dolan işlemlerin ortalaması > 0) · ayda işlem · en kötü işlem · 2x likidasyon (stopsuzda dolumdan sonraki en derin düşüş ≤ −%45; stoplu kuralda stop çıkış fiyatı ≤ −%45).

## Karar (126 coin, trend filtreli; bir kez)
- Dönemler: ½-1 2022-06-01 → 2023-06-30 · ½-2 2023-07-01 → 2024-12-31 · 2025+ (2025-01-01 →) · 2026 (2026-01-01 →).
- **Başarı:** DÖRT dönemin hepsinde işlem isabeti ≥ %70 · işlem başı net ≥ +%0,20 · gün isabeti ≥ %65 · ≥ 30 işlem (2026: ≥ 15) · 2x likidasyon = 0.
- Birden çok kural geçerse: dört dönemin en kötü işlem başı neti en yüksek olan.
- Bilgi (karar değil): aynı kurallar filtresiz (126 coin) · filtreli 15 eski coin · 10.10.2025 günü ayrı.

## Canlıya geçiş
- Geçen kural kullanıcıya somut fiyatlı örnek mesajla gösterilir; onay olmadan canlıya girmez.

## Ek (27.10.2026, veri işlenmeden ÖNCE — stop dolumu daha kötümser)
- Hızlı çöküşte stop emri stop fiyatından dolmaz: stop dolumu = min(stop, dakikanın açılışı, (stop + dakikanın en düşüğü) / 2) × (1 − %0,3). Başka değişiklik yok.
