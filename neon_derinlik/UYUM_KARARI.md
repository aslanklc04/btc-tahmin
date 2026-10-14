# 💧 Neon ölçümü ↔ Binance arşivi uyum kararı (ÖNCEDEN YAZILDI, 12.10.2026 19:20 TR — karşılaştırma verisi görülmeden)
Kullanıcı kararı: "tutarlılık net çıkar çıkmaz ekle".
Karşılaştırma: aynı UTC saatleri, 13 coin (BTC ve ETH hariç — 1000 seviye ±%1'i kapsamıyor), Neon dakikalık ölçümlerinin saatlik ortalaması (bid1+ask1)
vs Binance arşivi bookDepth ±1 notional saatlik ortalaması (ld_kontrol.py ile aynı tanım).
NET UYUM = aşağıdakilerin HEPSİ (en az 24 ortak saat, coin başına ≥ 20 saat):
  U1 coin başına log(Neon) ile log(arşiv) korelasyonu: medyan ≥ 0,90 ve hiçbir coin < 0,75
  U2 coin başına |log(Neon / arşiv)| medyanı ≤ 0,10 (seviye farkı ≤ ~%10)
  U3 Neon değeriyle hesaplanan z (taban: arşivin son 720 saatlik ortalamaları) ile arşivin kendi z'si arasındaki fark: tüm saatlerde |fark| medyanı ≤ 0,25
     ve LD bayrağı (z ≤ −2) uyuşmazlığı ≤ %2 saat
Uyum varsa → 💧 canlıya (13 coin, ✅ ana sinyale 💧 işareti + öncelik; sinyal sayısı değişmez). Uymayan coin varsa o coin hariç tutulur.
Uyum yoksa → bir gün daha veri toplanır; 3 günde yine yoksa kullanıcıya bildirilir.

## Ek (12.10.2026 ~20:05 TR, karşılaştırma verisi görülmeden)
ld_genis.py'de 💧 geniş liste + 💵 coin'lerinde de geçti (118 coin; K0–K4 hepsi ✅). Neon bu coin'leri 12.10 ~17:10 UTC'den itibaren
dakikada yarısı olmak üzere (tek/çift dakika → saatte ~30 örnek) ölçmeye başladı. Bu coin'ler için de AYNI U1–U3 ölçütleri uygulanır
(coin başına ≥ 20 ortak saat olunca; U1 "hiçbir coin < 0,75" şartı yerine: < 0,75 olan coin hariç tutulur). Uyan coin'lerde 💧 canlıya geçer.
BTC ve ETH: 1000 seviye ±%1'i kapsamıyor → şimdilik hariç.

## Ek 2 (13.10.2026 ~13:10 TR, kullanıcı: "Likidite tekniği tam emin olmadan ekleme" — karşılaştırma verisi görülmeden)
Otomatik canlıya geçiş KALDIRILDI. Ölçütler sıkılaştırıldı:
  - Coin başına en az 72 ortak saat (≥ 3 gün; 20 yerine). U1–U3 aynı.
  - U4 GÜN GÜN TUTARLILIK: U2 ve U3 (tüm coin'lerin medyanı, LD uyuşmazlığı havuzda) ilk 24 ve son 24 ortak saatte ayrı ayrı da geçmeli
    (tek iyi günün şansı elenir; tek günde korelasyon düşük oynaklık yüzünden anlamsız olduğundan U1 günlük aranmaz).
  - U5 💧 OLAYLARI (tüm coin'ler havuzda): arşivde 💧 (z ≤ −2) olan saatlerin ≥ %80'i Neon ölçümüyle de 💧 olmalı, Neon'un fazladan 💧 dediği saat ≤ %2.
    Arşivde 5'ten az 💧 saati varsa karar verilmez, veri toplanmaya devam edilir (en fazla 7 gün).
  - Neon kesintisi: ortak saatlerde beklenen dakika örneklerinin ≥ %95'i ölçülmüş olmalı (ilk 15 coin dakikada bir = 60/saat, ek coin'ler 30/saat).
Hepsi geçse bile 💧 kendiliğinden canlıya EKLENMEZ: sonuç kullanıcıya gösterilir, kullanıcı onay verirse eklenir.

## Ek 3 (14.10.2026 ~12:20 TR, karşılaştırma sonucu görülmeden)
Neon kontrolünde son tam saatte 60 dakikanın 56'sı ölçülmüş (%93; zamanlayıcı ara sıra bir dakika atlıyor). Saatlik ortalama 56 ve 60 örnekle
pratikte aynıdır; ölçüm uyumu zaten U1–U5 ile doğrudan sınanıyor. Kapsam eşiği %95 → %90 (kullanıcı onayı: "hangisi daha iyiyse"). Diğer ölçütler aynı.
