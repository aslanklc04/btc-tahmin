# Önceden yazılı protokol — GÜNDE +%10 YÜKSELECEK COIN'İ ÖNCEDEN BULMAK (pompa · 02.11.2026)
_Kullanıcı (02.11): "Gerçek tahmin yapan, gerçekten günde %10'dan fazla yükselecek; her gün 3–4 sinyal, ayrı ayrı saatlerde gelecek sinyaller bul." Hesaptan önce yazıldı; sonradan değiştirilmez (gerekirse tarihli "Ek"). Canlıya yalnız kullanıcı onayıyla._

## Veri · olay
- teknik3_mum (Binance vadeli 1 s, 141 coin, 2021-11 → 2026-10-30).
- Giriş: t saatinin kapanışında sinyal → t+1 açılışı × (1 + %0,1 kayma).
- **Olay (etiket):** sonraki 24 saat içinde en yüksek ≥ giriş × 1,10.
- **İşlem:** 🎯 giriş × 1,10'a limit satış; değmezse 24. saatin kapanışında çık. Ücret vadeli (giriş %0,05 + 🎯 %0,02 / süre sonu %0,05) + fonlama %0,01/8 s. Stop yok (bilgi: −%10 stoplu sürüm).

## Özellikler (t kapanışında bilinen)
Getiriler 1/4/12/24/72/168 s · oynaklık 24 s ve 168 s ve oranı · hacim z (24 s / önceki 30 g) ve son 1 s hacim / 24 s ort. · 24 s ve 7 g en yükseğe/en düşüğe uzaklık · RSI 14 · Bollinger %B ve bant genişliği · üst gölge/alt gölge (son 4 s) · BTC 4/24 s getirisi ve oynaklık oranı · coin'in BTC'ye göre 24 s göreli getirisi · coin'in son 30 gündeki +%10 olay sayısı · saat · gün.

## Model · yürüyen test
- HistGradientBoostingClassifier (max_iter 300, lr 0,05, max_leaf_nodes 63, min_samples_leaf 200, random_state 0); eğitimde tüm olaylar + olay olmayanlardan %10 rastgele örnek (ağırlık 10).
- **Çeyreklik yürüyen test 2024-Q1 → 2026-Q4:** her çeyrek için eğitim = t < çeyrek başı − 2 gün; çeyrek tahmin edilir.
- **Seçim:** her UTC günü, olasılığı en yüksek adaylardan **en fazla 4**, her biri **farklı saatte** ve farklı coin; aday olasılığı o çeyreğin eğitimindeki olayların taban oranının ≥ 3 katı olmalı (yoksa o gün daha az sinyal).

## Değerlendirme (2024 · 2025 · 2026 ayrı)
- Taban oranı (tüm coin-saatlerde olay oranı) · seçilenlerde olay oranı (isabet) · işlem başı net · günlük toplam · en kötü işlem · günde ortalama sinyal.
- **Plasebo:** her gün aynı sayıda rastgele coin-saat (farklı saat kuralıyla) ×20 → isabet ve net dağılımı.
- **"Bulundu":** ÜÇ yılda da seçilenlerde olay oranı ≥ 3 × taban VE plasebonun en iyisinden yüksek VE işlem başı net > 0 VE günde ≥ 2 sinyal.
- **"Kullanıcı hedefi":** ÜÇ yılda da olay oranı ≥ %50.

## Ek 1 (02.11.2026, kullanıcı: "Senin işin sadece oynaklığı mı bulmak, coin'in yönünü bulsana") — YÖN modeli (hesaptan önce)
İlk sonuç: model büyük hareketi bulur (+%10 isabeti %6–9 → %23–27) ama yön yok, net −%1…−3,4. Şimdi yön:
- **Yön etiketi:** sonraki 24 s'te önce hangisi: +%10 (1) mi −%10 (0) mı (saatlik sıra; aynı saatte ikisi → −%10 sayılır, kötümser). İkisine de değmeyenler yön modeline girmez.
- **Yön modeli:** aynı özellikler, aynı ayarlar ve çeyreklik yürüyen test; yalnız iki bariyerden birine değmiş satırlarla eğitilir.
- **Seçim:** her gün, büyük hareket olasılığı (pompa modeli) ≥ 3 × taban olan adaylar içinde **yukarı olasılığı en yüksek** en fazla 4 (farklı saat, farklı coin), ve yukarı olasılığı ≥ 0,5 olmalı.
- **İşlem:** 🎯 +%10 · stop −%10 (aynı saatte ikisi → stop) · değmezse 24 s sonra çıkış; ücret ve fonlama aynı.
- **"Yön bulundu":** ÜÇ yılda da seçilenlerde (bariyere değenler arasında) yukarı önce oranı ≥ %60 VE işlem başı net > 0 VE rastgele seçimin (aynı aday havuzundan, ×20) en iyisinden iyi.
