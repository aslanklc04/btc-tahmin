# Önceden yazılı protokol — BTC NEDEN DÜŞÜYOR, NEDEN YÜKSELİYOR? (btcneden · 30.10.2026)
_Kullanıcı (30.10): "BTC'nin kendi düşüş ve yükselişini derin araştır, BTC neden düşüp neden yükseliyor cevap ara; asıl amaç düşüşlere ve yükselişlere gerçek cevaplar bulmak." Bu dosya veri toplanmadan ve hesaplardan önce yazıldı; sonradan değiştirilmez (gerekirse tarihli "Ek"). Hiçbir sonuç kullanıcı onayı olmadan canlıya girmez._

## Dönemler
**K** keşif 2022-01-01 → 2023-12-31 · **C1** kontrol 2024 · **C2** kontrol 2025-01-01 → 2026-10-27. (ETF verisi yalnız 2024'ten: ETF'li ölçümlerde C1 keşif, C2 kontrol.)

## Veri (btcneden_veri.py, GitHub Actions)
- Saatlik BTC: Binance vadeli 1 s mum (+ agresif alıcı hacmi) · Binance spot 1 s mum (+ agresif alıcı hacmi) · Coinbase BTC-USD 1 s (ABD primi = Coinbase / Binance spot − 1) · Binance "metrics" 5 dk → saatlik: açık pozisyon (coin adedi ve $), büyük oyuncu L/S, hesap L/S, agresif alıcı/satıcı oranı · fonlama (8 s) · Deribit DVOL (saatlik).
- Günlük: Nasdaq (^IXIC), S&P 500, dolar endeksi (DX-Y.NYB), ABD 10 y faizi (^TNX), VIX, altın (GC=F) — Yahoo · ABD spot BTC ETF net akışı (Farside, yoksa BGeometrics) · stablecoin toplam arzı (DefiLlama) · borsalara BTC giriş/çıkışı (CoinMetrics) · korku-açgözlülük endeksi · FOMC/CPI günleri (makro_tarih.json).
- Doğrulama coin'leri: ETH, SOL vadeli 1 s + fonlama.
- Açık pozisyon değişimi **coin adediyle** ölçülür (dolar değeri fiyatla mekanik değişir).

## Olaylar
- Günlük (UTC günü kapanıştan kapanışa) getiri r; σ = önceki 60 günün günlük getiri std'si. **Büyük düşüş günü:** r ≤ −2σ ve r ≤ −%3. **Büyük yükseliş günü:** r ≥ +2σ ve r ≥ +%3.
- 4 saatlik (00·04·08·12·16·20 UTC blokları) getiri; σ4 = önceki 30 günün 4 s std'si. **Büyük 4 s düşüş/yükseliş:** |r| ≥ 2,5σ4 ve |r| ≥ %1,5.

## A — "Ne oldu?" (hareketle AYNI anda olanlar · açıklama, tahmin değil)
Faktörler (aynı UTC günü): A-WS Nasdaq getirisi, VIX değişimi · A-DOL dolar endeksi, 10 y faiz (baz puan), altın · A-ABD Coinbase primi değişimi (gün ort. − önceki gün ort.), ETF net akışı · A-VAD vadeli agresif alıcı dengesizliği, açık pozisyon (adet) % değişimi, tasfiye vekili (saatlik açık pozisyon düşüşü ≥ %1,5 olan saat sayısı) · A-SPOT spot agresif alıcı dengesizliği · A-ZİN borsalara net giriş, stablecoin arzı değişimi · A-OPS DVOL değişimi (yarı mekanik: fiyat düşünce korku yükselir — ayrı not edilir).
- **A1 açıklanan pay:** BTC günlük getirisi ~ faktörler (standart hâle getirilmiş OLS, ABD işlem günleri). Dönem başına R², her grubun tek başına R²'si ve "grubu çıkarınca kaybolan R²". ETF'li model ayrıca (C1, C2).
- **A2 büyük gün profili:** büyük düşüş/yükseliş günlerinde her faktörün medyanı vs sıradan günler; faktörün aynı yönde aşırı (|z| ≥ 1,5, z = önceki 90 gün) olduğu günlerin oranı.
- **A3 sebep etiketi** (çoklu etiket, sabit kurallar; z = önceki 90 gün):
  - 🏛️ Wall Street/makro: Nasdaq aynı yönde |z| ≥ 1,5 · ya da dolar endeksi ters yönde |z| ≥ 1,5 · ya da o gün FOMC/CPI.
  - 🇺🇸 ABD spot talebi: Coinbase primi değişimi aynı yönde |z| ≥ 1,5 · ya da ETF akışı aynı yönde |z| ≥ 1,5 (60 işlem günü).
  - 💥 Kaldıraç tasfiyesi: açık pozisyon (adet) günde ≤ −%5 (düşüşte uzunların, yükselişte kısaların tasfiyesi).
  - 🎰 Kaldıraçlı yeni pozisyon: açık pozisyon günde ≥ +%5.
  - 🪙 Borsa akışı: düşüşte borsaya net giriş z ≥ 1,5 · yükselişte net çıkış z ≥ 1,5.
  - ❓ Ölçülen sebep yok (haber/bilinmeyen).
  Yıl başına etiket payları + en büyük 25 düşüş ve 25 yükseliş günü tek tek (etiketler + o günün değerleri).
- **A4 saatlik:** büyük 4 s hareketlerinde Coinbase primi değişimi, vadeli/spot agresif dengesizliği, açık pozisyon değişimi; hareketi kimin başlattığı (vadeli mi spot mu ABD mi): hareketin ilk saatinde en aşırı z hangisi. Büyük hareketlerin saat (UTC) ve gün dağılımı vs normal.

## B — "Önceden belli miydi?" (öncü işaretler · tahmin)
- **B1 günlük:** D−1 günü sonunda bilinen 24 durum: fonlama 3 g ort. · açık pozisyon 7 g değişim · büyük oyuncu L/S · hesap L/S · vadeli agresif dengesizlik 3 g · spot agresif dengesizlik 3 g · Coinbase primi 3 g ort. · prim 3 g değişim · DVOL seviye · DVOL 3 g değişim · oynaklık sıkışması (7 g / 60 g std) · 30 g zirveye uzaklık · 7 g getiri · stablecoin arzı 7 g değişim · borsa net giriş 7 g z · ETF 3 g akış · korku endeksi · Nasdaq 5 g getiri · dolar 5 g değişim · 10 y faiz 5 g değişim · VIX seviye · D günü FOMC/CPI · D günü hafta sonu · vadeli/spot hacim oranı 7 g.
- Hedef: D … D+2 içinde büyük düşüş günü / büyük yükseliş günü; bilgi: sonraki 3 g ortalama getiri.
- Yöntem: her durum K'deki eşiklerle 5 dilime ayrılır (ETF: C1'de). En alt ve en üst dilimde olasılık / dönem taban oranı = **kaldıraç (lift)**.
- **Geçme şartı:** aynı dilim + aynı hedef için lift ≥ 1,5 HER dönemde (K, C1, C2; ETF: C1, C2) ve her dönemde o dilimde ≥ 8 olay.
- **Plasebo:** her durum serisi rastgele ≥ 90 gün kaydırılarak 50 kez; ortalama "tesadüfen geçen" sayısı raporlanır.
- **B2 4 saatlik:** saat h sonunda bilinen: prim z (24 s) · prim 4 s değişim · vadeli agresif 4 s · spot agresif 4 s · açık pozisyon 4 s ve 24 s değişim · fonlama · DVOL 4 s değişim · oynaklık oranı 24 s/720 s · 24 s getiri · günün saati (6 blok). Hedef: h+1 … h+4 içinde büyük 4 s hareket (kayan pencere, |r| ≥ 2,5σ4 ve ≥ %1,5). Aynı lift şartı, her hücrede ≥ 30 olay.

## C — Tahmin kuralları (yalnız B'den geçenlerle)
- B1'den geçen her durum (ve geçenlerin ikili VE birleşimi): düşüş riskli dilim → BTC SAT (kısa), yükseliş dilimi → BTC AL. Giriş D günü 00:00 açılışı × (1 ± %0,1 kayma) · 🎯 %3 / %5 · stop yok / %8 · süre 3 / 7 gün · vadeli ücret (giriş %0,05, 🎯 %0,02, diğer çıkış %0,05) + gerçek fonlama · kural başına aynı anda tek işlem.
- B2'den geçenler: giriş h+1 açılışı, 🎯 1σ4, süre 4 s.
- **Geçme şartı:** HER dönemde isabet ≥ %70 VE işlem başı net ≥ +%1,0 (günlük) / +%0,3 (4 s) VE ≥ 8 işlem; ayrıca aynı kural ETH ve SOL'da C1 ∪ C2'de net > 0 (ana coin'lere taşınabilir mi).

## Rapor
Önce A (sebepler, sade dille ve örnek günlerle), sonra B (önceden görülebilenler), sonra C (işlem kuralı çıktı mı). Geçen/geçmeyen açıkça; canlıya yalnız kullanıcı onayıyla.
