# Önceden yazılı protokol — İĞNE SONRASI ALIM: formül taraması + BAKILMAMIŞ coin'lerde doğrulama (igne4 · 27.10.2026)
_igne3: iğne sonrası alım (24 s) dört dönemde de kârlı, isabet %67–70, 2025'te 2x'te 7 likidasyon. Kullanıcı (27.10): "Son bulduğun ipucunu zararsız, isabetli ve kârlı nasıl çıkarırız formülasyonunu bul, sonra canlıya alırız." Hiç zararsız işlem mümkün değil → hedef: her dönemde isabet ≥ %70, kâr, sınırlı zarar (iğne dibi altında stop), 2x'te likidasyon yok. Çok kural denenince şans eseri iyi görünen çıkar → tarama YALNIZ görülmüş 141 coin'de; seçilen ≤ 5 formül, HİÇ kullanılmamış (listeden çıkmışlar dahil) Binance vadeli coin'lerinde BİR KEZ doğrulanır. Bu dosya veri işlenmeden yazıldı; sonradan değiştirilmez (gerekirse tarihli "Ek")._

## Veri
- Binance USDT-M vadeli **5 dk** mum (data.binance.vision; aylık 2022-04 → 2026-09 + Ekim 2026 günlük), 2022-06-01 → 2026-10-25.
- **Görülmüş evren (TARAMA):** igne2_evren.txt (126) + BTC + 14 ana coin = 141 (igne3'te kullanıldı).
- **Bakılmamış evren (DOĞRULAMA):** arşivdeki tüm diğer USDT sürekli vadeli sembolleri (listeden çıkmışlar dahil). Hariç: "_" içeren (dönemsel), stabil coin'ler (USDC, BUSD, TUSD, FDUSD, USDP, DAI, USDE), endeksler (BTCDOM, DEFI, FOOTBALL, BLUEBIRD). "1000…" önekli semboller taban adla eşlenir; görülmüş bir coin'e denk gelen atılır.
- Likidite şartı (her iki evren, sabit): son 7 günün ortalama günlük işlem hacmi ≥ 2 M$.

## Aday (saat h kapanışında)
- σ1 = önceki 720 saatin 1 s log getiri std'si · kr = (açılış − en düşük) / (açılış · σ1) · rr = (kapanış − en düşük) / (açılış − en düşük).
- Aday: kr ≥ 3 (tüm adaylar kaydedilir; filtreler analizde).
- Özellikler: rb = aynı saatte BTC 1 s getirisi · nsame = aynı saatte GÖRÜLMÜŞ 141 coin'den kr ≥ 4 iğne yapan sayısı (piyasa geneli ölçüsü; canlıda da hesaplanabilir) · r7 = önceki 7 gün getirisi.

## Giriş filtreleri (tarama ızgarası) — 72
- k (kr ≥) ∈ {4 · 6 · 8} · toparlanma rr ≥ {0,5 · 0,75} · piyasa geneli nsame ≤ {sınırsız · 2 · 5} · BTC rb ≥ {sınırsız · −%1} · coin trendi r7 > {sınırsız · 0}.
- Aynı coin'de son kabul edilen sinyalden sonra 24 saat yeni sinyal yok (filtre başına).

## İşlem (çıkış ızgarası) — 64
- Giriş: sinyal saatinden sonraki 10. dakika açılışı (5 dk mum), piyasa (%0,05). Mesaj ~7. dakikada gelir → kötümser.
- Hedef: L + f·(O − L) (O = iğne saati açılışı, L = iğnenin dibi), f ∈ {0,5 · 0,75 · 1,0 · 1,25}; hedef ≤ giriş ise hemen piyasa çıkış. Limit ücreti %0,02.
- Stop: yok · S0 = L·(1 − %0,2) (dibin hemen altı) · S1 = L·(1 − σ1) · S2 = L·(1 − 2σ1). Stop dolumu = min(stop, mumun açılışı, (stop + mumun en düşüğü)/2) × (1 − %0,3), piyasa ücreti. Aynı mumda hedef ve stop → stop.
- Süre H ∈ {4 · 8 · 24 · 48} saat; sonunda piyasa. Fonlama %0,01 / 00-08-16 UTC.
- 2x likidasyon: stopsuzda girişten sonra en düşük ≤ −%45; stopluda stop dolumu ≤ −%45.
- Toplam 72 × 64 = **4.608 formül**.

## Ölçü ve dönemler
- işlem isabeti (net > 0) · işlem başı net · saat isabeti (aynı saatteki sinyallerin ortalaması > 0) · haftada işlem · en kötü işlem.
- Dönemler: ½-1 2022-06-01 → 2023-06-30 · ½-2 2023-07-01 → 2024-12-31 · 2025+ · 2026.

## TARAMA (görülmüş 141 coin)
- Uygun: DÖRT dönemde de işlem isabeti ≥ %72 · işlem başı net ≥ +%0,30 · saat isabeti ≥ %65 · ≥ 30 işlem (2026: ≥ 20) · 2x likidasyon 0.
- Uygunlar dört dönemin EN KÖTÜ işlem başı netine göre sıralanır → ilk 5 doğrulamaya gider. Uygun yoksa "geçmedi".

## DOĞRULAMA (bir kez, bakılmamış coin'ler)
- DÖRT dönemde de: işlem isabeti ≥ %70 · işlem başı net ≥ +%0,20 · saat isabeti ≥ %65 · ≥ 30 işlem · 2x likidasyon 0.
- Geçenler arasında TARAMA sırasında en üstteki seçilir.

## Canlıya geçiş
- Seçilen formül kullanıcıya somut fiyatlı örnek mesajla gösterilir (giriş, 🎯, stop, çıkış saati). Kullanıcı ön onay verdi ("sonra canlıya alırız"); yine örnek gösterilir. Canlıda ilk haftalar gerçekçi karnede ayrıca izlenir.
- Not: doğrulama aynı tarih aralığında (farklı coin'ler) → aynı piyasa dönemlerini paylaşır; tamamen bağımsız değildir.
