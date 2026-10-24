# Önceden yazılı protokol — 🎯 kâr-al ile modelin fiyat aralığını birleştirmek (24.10.2026)
_Kullanıcı: "kâr al ile fiyat aralığını birleştirmenin yollarını bulursak belki bir şey çıkar." Veri ve sonuç görülmeden yazıldı._

## Neden yürüyen test
Canlıdaki aralık modelleri (egit_coin.py QM, q10/q50/q90 + QC uyumu) en son veriyle bir kez eğitildi → geçmişe uygulanırsa geçmişi "ezberlemiş" olur. Bu yüzden her çeyrek başında yalnız o güne kadarki veriyle yeniden eğitilir: eğitim [başlangıç − 3 yıl, başlangıç − 30 gün), uyum (QC) [başlangıç − 30 gün, başlangıç), aynı ayarlar (LGBM quantile, 400 ağaç, öz. = ortak.features), 4 saat ufku.
Aralık: alt = G·e^(q10 − QC), beklenen = G·e^(q50), üst = G·e^(q90 + QC) (canlıyla aynı). G = sinyal saati kapanışı.

## Sinyaller ve ölçüm
- veri_seti.csv.gz'deki 4 saatlik 🤝 / 🌐🤝 ✅ ana ve 🔸 yedek (🌐🤝 eşik altı) sinyalleri.
- Giriş B (mesaj fiyatına limit 60 dk, t+7'den), Binance 1 dk mum, vadeli ücret (limit %0,02 · piyasa %0,05) + fonlama yaklaşığı. İsabet = net > 0, işlem ve saat bazında.
- T0 = şimdiki 🎯 (ana 0,75σ · yedek 0,50σ).

## Kurallar (yalnız bunlar)
- R1: 🎯 = min(T0 🎯, üst)
- R2: 🎯 = beklenen; beklenen ≤ giriş × 1,002 ise işlem yok
- R3: beklenen ≤ G ise işlem yok (🎯 = T0)
- R4: (üst − G) / (G − alt) < 1 ise işlem yok (🎯 = T0)
- R5: 🎯 = G + 0,5 · (üst − G)

## Karar
- KEŞİF 2022-06 → 2024-12 (iki yarı: → 2023-06 · 2023-07 →), sınıf başına (ana · yedek). Şart her iki yarıda: işlem isabeti ≥ T0 − 0,5 · saat isabeti ≥ T0 − 0,5 · işlem başı net ≥ T0 + 0,03 puan · (R2–R4) kalan işlem ≥ T0'ın %40'ı. Geçenlerden en yüksek netli tek kural (sınıf başına) kontrole.
- KONTROL 2025+ ve 2026 ayrı ayrı, aynı şartlar. (Sinyal sonuçları bu dönemde daha önce görüldü; model aralığı hiç görülmedi → kanıt "orta güç".)
- Toplam deneme 10 (5 kural × 2 sınıf). Başarısızlık "bulunamadı" diye raporlanır. Geçen kural önce gölge izlemeye alınır; kullanıcı onayı olmadan canlıya alınmaz.
