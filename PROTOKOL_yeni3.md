# Önceden yazılı protokol — ÜÇ YENİ, DAHA ÖNCE SINANMAMIŞ SİNYAL FİKRİ (yeni3 · 04.11.2026)
_Kullanıcı (04.11): "Bir şey bul, ama yalan kesinlikle yok." Hesaptan önce yazıldı; sonradan değiştirilmez. Canlıya yalnız kullanıcı onayıyla._
Amaç: mevcut ✅ ana / ELİT / 🌪️ sinyallerinden BAĞIMSIZ (fiyat/hacim mumundan) ve ELİT seviyesinde (isabet ≥ %70) yeni sinyal; tercihen başka gün/saatlerde.

## Veri · ölçüm
teknik3_mum (Binance vadeli 1 s, 141 coin, 2022-06 → 2026-10-30). Sinyal t saatinin kapanışında → giriş t+1 açılışı × 1,001 (kayma).
🎯 = giriş × (1 + 0,75 · σ720 · √H) (σ720: coin'in son 720 saatlik log getiri std'si; ✅ ana ile aynı k) · değerse limit satış; değmezse H. saat kapanışında çıkış.
Ücret: giriş %0,05 + 🎯 %0,02 (süre sonu %0,05) + fonlama %0,01 / 8 s. İsabet = net > 0 (D_T0 gibi).

## Fikirler (parametreler sabit)
- **Y1 Gecikmeli takip (lead-lag):** BTC'nin t saatindeki getirisi ≥ 3 × σ_BTC (720 s) VE ≥ +%1. Coin'in BTC'ye beta'sı (720 s) ≥ 0,5 ve coin'in aynı saatteki getirisi ≤ 0,5 · beta · BTC getirisi (geride kaldı) → al, H = 4. O saatte en geride kalan (coin getirisi / (beta · BTC getirisi) en küçük) en çok 3 coin.
- **Y2 Göreli güç:** BTC son 4 saatte ≤ −%2,5 düştü, coin aynı 4 saatte ≥ 0 (düşmedi) → al, H = 12. O saatte 4 s göreli getirisi en yüksek en çok 3 coin.
- **Y3 Hacim kırılımı:** coin'in t saatindeki hacmi ≥ 5 × önceki 168 saat ortalaması VE getirisi ≥ 3 × σ720 VE kapanış o saatin aralığının üst %25'inde VE kapanış > önceki 168 saatin en yükseği → al, H = 4. O saatte hacim oranı en yüksek en çok 3 coin.
- Aynı coin için önceki işlem kapanmadan yeni işlem yok.

## Değerlendirme
- Hücreler: coin yarıları (md5 tek/çift) × dönem (2022-06→24 · 2025 · 2026) = 6 hücre.
- **"Bulundu"**: 6 hücrenin HEPSİNDE ≥ 20 işlem, isabet ≥ %70, işlem başı net ≥ +%0,30 VE her dönemde rastgele seçimin (aynı gün aynı sayıda rastgele coin-saat, aynı 🎯/H/ücret, ×20) en iyisinden yüksek isabet ve net.
- **Bilgi:** haftada sinyal · haftada farklı gün · farklı saat · ✅ ana / ELİT / 🌪️ ile aynı saate düşme oranı (2025+) · en kötü işlem.
- Üç fikir; bulunan olursa canlı öncesi PROTOKOL_ayrim Ek 1 tarzı sağlamlık testleri (aylık istikrar, ilk 5 coin hariç, eşik duyarlılığı) ayrıca yazılır ve yapılır.
