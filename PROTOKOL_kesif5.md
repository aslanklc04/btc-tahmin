# Önceden yazılı protokol — BÜYÜK HAREKET AİLELERİ: %70+ isabet, işlem başı ≥ +%2 (kesif5 · 28.10.2026)
_Kullanıcı (28.10): "Artık gerçekten %70+ isabet, kâr %2–3'ten fazla sinyaller bul; fikirleri kendin bul, testleri kendin yap." İşlem başı ≥ %2 ancak çok günlük tutuş ve büyük hareketlerle mümkün → 5 YENİ olay ailesi (bu sistemde hiç test edilmedi). Bu dosya veri işlenmeden yazıldı; sonradan değiştirilmez (gerekirse tarihli "Ek")._

## Veri
- Binance USDT-M vadeli **1 saatlik** mum + **gerçek fonlama oranı** (data.binance.vision aylık; 2022-04 → 2026-09 + Ekim 2026 günlük mum), 2022-06-01 → 2026-10-25.
- Evren: igne4_semboller.csv — **görülmüş** (141 coin, önceki testlerde kullanıldı) ve **bakılmamış** (735 coin, listeden çıkmışlar dahil). Likidite: önceki 7 gün ort. günlük hacim ≥ 2 M$.

## Olay aileleri (saat i kapanışında; aynı aile + aynı coin'de 24 saat bekleme)
- **F1 Kapitülasyon dönüşü:** z72 = 72 s getirisi / (σ1·√72) ≤ {−3 · −4} · 72 saatin dibinin üstünden geçen saat ≥ {0 · 6}.
- **F2 Fonlama sıkışması:** son fonlama < 0 ve son 90 ödemenin yüzdeliği ≤ {%2 · %5} · 24 s getiri ≥ {sınırsız · 0}.
- **F3 Hacimli kırılım:** son 24 s hacmi / önceki 30 günün günlük ortalaması ≥ {3 · 5} · kapanış ≥ önceki 30 günün en yükseğinin %98'i.
- **F4 Liderde geri çekilme:** 7 g getiri − BTC 7 g getiri ≥ {+%15 · +%30} · kapanış / son 24 s en yüksek − 1 ≤ {−%5 · −%10}.
- **F5 Geride kalan:** BTC 24 s getirisi ≥ {+%3 · +%5} · coin 24 s − BTC 24 s ≤ {−%2 · −%4}.
- Ortak seçenek: BTC trend filtresi {yok · BTC kapanışı > 200 günlük ort.}. → 18 × 2 = **36 giriş**.

## İşlem
- Giriş: i+1 saatinin açılışı × (1 + %0,1 kayma), piyasa ücreti %0,05.
- Hedef: giriş × (1 + T), T ∈ {%3 · %5 · %8} (limit %0,02) · Stop: yok · S = son 72 saatin en düşüğü × 0,99 (giriş altındaysa) · Süre H ∈ {24 · 72 · 120} saat, sonunda piyasa.
- Saatlik mum: hedef ve stop aynı mumdaysa stop (kötümser) · stop dolumu = min(stop, mumun açılışı) × (1 − %0,3).
- Fonlama: tutuş süresindeki GERÇEK fonlama ödemeleri (long öder/alır).
- 2x likidasyon: stopsuzda en düşük ≤ −%45 · stopluda stop dolumu ≤ −%45.
- → 3 × 2 × 3 = 18 çıkış · toplam 36 × 18 = **648 kural**.

## Ölçü · dönemler
- işlem isabeti · işlem başı net · gün isabeti (aynı gün açılan işlemlerin ort. > 0) · ayda işlem · en kötü işlem.
- ½-1 2022-06-01 → 2023-06-30 · ½-2 2023-07-01 → 2024-12-31 · 2025+ · 2026.

## Karar
1. **Keşif (görülmüş 141, ½-1 ve ½-2):** ikisinde de isabet ≥ %70 · net ≥ +%2,0 · gün isabeti ≥ %60 · ≥ 20 işlem · likidasyon 0.
2. **Kontrol (görülmüş 141, 2025+ ve 2026):** aynı şartlar (≥ 15 işlem).
3. **Doğrulama (bakılmamış 735, DÖRT dönem):** isabet ≥ %70 · net ≥ +%2,0 · gün isabeti ≥ %60 · ≥ 20 işlem · likidasyon 0.
- 1 ve 2'yi geçen ilk 5 kural (keşif + kontrolün en kötü dönem netine göre) doğrulamaya gider. Doğrulamayı geçen → kullanıcıya somut fiyatlı örnekle canlı önerisi. Hiçbiri geçmezse en yakınlar bilgi olarak raporlanır (karar değil).
