# Önceden yazılı protokol — LİKİDASYON İĞNESİ: önceden konmuş derin limit alış (igne · 27.10.2026)
_Kullanıcı (27.10): "Binance'teki yapısal açıklar" → likidasyon iğneleri önerildi → "Test et". Vadeli piyasada zorunlu satışlar kısa süreli derin düşüşler (iğne) yapar, fiyat çoğu zaman hızla geri gelir. Soru: önceden konmuş derin limit alış emri bu iğneleri kârlı ve ≥ %70 isabetle yakalar mı? Bu dosya veri işlenmeden yazıldı; sonradan değiştirilmez (gerekirse tarihli "Ek")._

## Veri
- **Binance USDT-M VADELİ 1 dk mum** (data.binance.vision arşivi; GitHub Actions'tan erişilebilir). Sembol yoksa "1000"+coin denenir (oranlar ölçeksiz olduğu için fark etmez). Bulunamayan coin/gün atlanır, sayısı raporlanır.
- Limit dolumu: mumun en düşüğü limitin **altına inmeli** (Lo < L; sadece değmek yetmez — kötümser). Hedef kontrolü dolumdan SONRAKİ mumdan başlar.
- Ücretler (vadeli): limit %0,02 · piyasa %0,05 · fonlama %0,01 / geçilen 00-08-16 UTC (dolumdan çıkışa).

## A — Sinyallere "ikinci kademe" (karar: ✅ ana · 🔸 yedek ve 📋 panelden yalnız bilgi)
- Sinyaller: veri_seti.csv.gz (t = sinyal saatinin kapanışı, H, s = σ720·√H, sınıf). Gf = t anındaki vadeli kapanış · 🎯 = Gf·(1 + k·s), k: ana 0,75 · yedek 0,50 · panelden 0,45.
- **Taban (kademe 1):** bugünkü giriş B — 7. dk açılışı ≤ Gf ise oradan (piyasa), değilse 8–66. dk'da Lo < Gf → Gf'den limit; çıkış 🎯 ya da t + H kapanışı.
- **Kademe 2:** 7. dakikadan t + H'ye kadar geçerli limit L = Gf·(1 − d·s), d ∈ {0,5 · 1,0 · 1,5 · 2,0}. Çıkış: **E1** = sinyalin 🎯'si · **E2** = Gf (mesaj fiyatına dönüş); değmezse t + H kapanışı (piyasa). → 8 kural.
- Ölçü (yalnız dolan kademe-2 işlemleri): işlem isabeti (net > 0) · işlem başı net · işlem sayısı · haftada dolum.
- **KEŞİF** (2022-06-01 → 2023-06-30 · 2023-07-01 → 2024-12-31): iki yarıda da işlem isabeti ≥ %70 · işlem başı net ≥ +%0,10 · ≥ 30 işlem. Geçenlerden keşif neti en yüksek TEK kural kontrole gider.
- **KONTROL (bir kez):** 2025-01-01 → ve 2026-01-01 →: aynı üç şart (≥ 20 işlem) VE işlem başı net ≥ aynı dönemin kademe-1 tabanı.
- Bilgi: iki kademe birlikte sinyal başı net · en kötü işlem.

## B — Bağımsız "günlük iğne emri" (sinyalden bağımsız)
- Evren: BTC + ana 14 coin (durum/coin_listesi.txt: ADA APT ARB BNB DOGE DOT ETH FLOKI LINK NEAR OP PEPE SHIB SUI).
- Her gün 00:00 UTC: P = 00:00 mumu açılışı · σd = önceki 720 saatlik 1 s log getirilerin std'si × √24 · L = P·(1 − d·σd), d ∈ {2 · 3 · 4}; emir o gün 23:59'a kadar geçerli.
- Çıkış: **X1** hedef = L + ½(P − L) (yarı yol geri) · **X2** hedef = P (tam geri); değmezse dolumdan 24 saat sonra piyasa. → 6 kural.
- Ölçü: işlem isabeti · işlem başı net · gün isabeti (o gün dolan işlemlerin ortalaması > 0) · ayda işlem · en kötü işlem · dolumdan sonra en derin düşüş (2x / 3x kaldıraçta likidasyon sayısı: −%45 / −%30).
- **KEŞİF** (aynı iki yarı): iki yarıda da işlem isabeti ≥ %70 · işlem başı net ≥ +%0,20 · gün isabeti ≥ %65 · ≥ 30 işlem. Keşif neti en yüksek TEK kural kontrole gider.
- **KONTROL (bir kez):** 2025+ ve 2026: aynı şartlar (≥ 15 işlem) VE hiçbir dönemde 2x kaldıraçta likidasyon yok.

## Veri aralığı
- 2022-06-01 → 2026-10-25 (son sinyal saatleri arşivin günlük dosyaları çıktıkça). Eksik son günler raporlanır.

## Canlıya geçiş
- Geçen kural kullanıcıya somut fiyatlarla örnek mesaj olarak gösterilir; onay olmadan canlıya girmez. Canlıda Binance vadeli API gerekmez (limit fiyatı bizim fiyat verimizden hesaplanır).
