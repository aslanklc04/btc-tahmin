# Önceden yazılı protokol — İĞNE SONRASI ALIM: toparlanan, coin'e özgü iğneler (igne3 · 27.10.2026)
_igne / igne2: önceden konmuş derin limitler ortalamada kârlı ama piyasa geneli çöküş günlerinde (ör. 10.10.2025) hep birlikte batıyor; isabet bazı dönemlerde %50–60. Ders: (1) emri iğneden ÖNCE değil, iğne TOPARLANMAYA başladıktan SONRA ver; (2) BTC'nin de çöktüğü saatleri (piyasa geneli) alma. Bu fikir igne sonuçlarından geldi; ama "iğne sonrası giriş" kuralı hiçbir veride hesaplanmadı. Kullanıcı (27.10): "devam et". Bu dosya veri işlenmeden yazıldı; sonradan değiştirilmez._

## Veri
- Binance USDT-M vadeli 1 dk mum (data.binance.vision), 2022-05 → 2026-10-25 · evren: igne2_evren.txt (126 coin) + BTC + 14 ana coin. (Bugünkü liste → listeden çıkmış coin yok; sonuç iyimser olabilir.)
- Saatlik mum dakikalardan kurulur. σ1 = önceki 720 saatin 1 s log getiri std'si (sinyal saati hariç).

## Sinyal (saat h kapanışında, saatlik sistemle canlıda üretilebilir)
- İğne: saatin en düşüğü ≤ açılış·(1 − k·σ1), k ∈ {4 · 6}.
- Toparlanma: kapanış ≥ en düşük + ½·(açılış − en düşük).
- **BTC filtresi** (iki seçenek): yok · var = aynı saatte BTC'nin saatlik getirisi ≥ −%1,5 (piyasa geneli çöküş değil).
- Aynı coin'de sinyalden sonra 24 saat yeni sinyal yok (kural başına).
## İşlem
- Giriş: sinyal saatinden sonraki 7. dakika açılışı, piyasa (%0,05).
- Hedef: iğne saatinin AÇILIŞ fiyatı (tam toparlanma), limit (%0,02); değmezse H saat sonunda piyasa. H ∈ {4 · 24}. Fonlama %0,01 / 00-08-16 UTC.
- Hedef girişin altındaysa giriş anında piyasa çıkış (≈ ücret kadar zarar).
- → k 2 × BTC filtresi 2 × H 2 = **8 kural**.

## Ölçü
- işlem isabeti · işlem başı net · saat isabeti (aynı saatteki sinyallerin ortalaması > 0) · haftada sinyal · en kötü işlem · 2x likidasyon (girişten sonra en düşük ≤ −%45).

## KEŞİF (2022-06-01 → 2023-06-30 · 2023-07-01 → 2024-12-31)
- İki yarıda da: işlem isabeti ≥ %70 · işlem başı net ≥ +%0,20 · saat isabeti ≥ %65 · ≥ 50 işlem · 2x likidasyon 0. Geçenlerden keşif neti en yüksek TEK kural kontrole gider.
## KONTROL (bir kez): 2025-01-01 → ve 2026-01-01 →
- Aynı şartlar (≥ 30 işlem). Ayrıca bilgi: 10.10.2025 günü, coin'e göre dağılım, 15 ana coin ayrı.

## Canlıya geçiş
- Geçerse kullanıcıya somut fiyatlı örnek mesaj gösterilir; onay olmadan canlıya girmez.
