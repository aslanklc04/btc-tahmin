# Önceden yazılı protokol — ABD makro olayları (FOMC faiz kararı · CPI enflasyon) (25.10.2026)
_Tarihler: makro_tarih.json (resmi takvimler). Saatler: FOMC 14:00 ET, CPI 08:30 ET (yaz saati Mart 2. pazar → Kasım 1. pazar: ET = UTC−4, diğer zaman UTC−5). Veri ve sonuç görülmeden yazıldı._

## M1 — Olay saatini içine alan sinyaller
- Gönderilen sinyaller (veri_seti + karal2_veri, giriş B, vadeli ücret + fonlama, şimdiki 🎯). "Olaylı" = sinyalin tutma aralığı [t, t+H] bir açıklama anını içeriyor.
- Kural F-M: olaylı sinyalleri atmak. Şart (sınıf başına; keşif 2022-06 → 2024-12 iki yarıda, KONTROL 2025+ ve 2026'da): işlem isabeti ≥ taban − 0,5 · saat isabeti ≥ taban − 0,5 · işlem başı net ≥ taban + 0,03 · kalan ≥ %40. 3 deneme.
- Bilgi: olaylı ve olaysız sinyallerin ayrı ayrı isabeti/neti.

## M2 — Testere riski (uyarı için)
- 4 saatlik pencereler (her saat başı), saatlik en yüksek/en düşük ile PROTOKOL_sekil'deki şekil 1 (↕️ testere: up ≥ 1σ ve dn ≥ 1σ). "Olaylı" = pencere bir açıklama anını içeriyor.
- Lift = P(testere | olaylı) / P(testere | olaysız). Şart: araştırma coin'leri keşif (2022-06 → 2024-12) lift ≥ 1,3 · 2025+ ≥ 1,15 · dokunulmamış coin'ler ≥ 1,15. FOMC ve CPI ayrı → 2 deneme.
- Geçerse: mesajlarda o saatlerde "⚠️ FOMC/CPI saati — testere riski ×N" uyarısı önerilir (kullanıcı onayıyla).
