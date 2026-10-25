# Önceden yazılı protokol — tepe filtresi ve dip sinyali (25.10.2026; sekil_egim_sonuc.md'den çıkan iki soru)
_Kullanıcı onayı: "tm önerileri onaylıyorum". Veri ve sonuç görülmeden yazıldı._

## Etkenler (sinyal saatinde, t = saat kapanışı; yalnız t'ye kadar kapanmış saatler)
konum = (fiyat − son 24 saatin en düşüğü) / (en yüksek − en düşük) · r1z = son 1 saat getirisi / σ1 · r4z = son 4 saat getirisi / (σ1·2) · r24z = son 24 saat getirisi / (σ1·√24) · σ1 = son 720 saatlik saatlik σ. BTC için aynıları (btc_r24z).

## A) Tepe filtresi — mevcut gönderilen sinyaller (✅ ana · 🔸 yedek · 📋 panelden; veri_seti + karal2_veri, giriş B, vadeli ücret + fonlama, şimdiki 🎯)
- F1: konum > 0,8 olanları at · F2: r4z ≥ 1 olanları at · F3: r1z ≥ 1 olanları at · F4: F1 veya F2 olanları at.
- Keşif 2022-06 → 2024-12 (iki yarı). Şart her iki yarıda: işlem isabeti ≥ taban − 0,5 · saat isabeti ≥ taban − 0,5 · işlem başı net ≥ taban + 0,03 puan · kalan ≥ tabanın %40'ı. Geçen en iyi tek filtre (sınıf başına) KONTROL 2025+ ve 2026'da aynı şartla.
- 12 deneme (4 filtre × 3 sınıf).

## B) Dip sinyali — yeni alım adayı
- Koşul: coin r24z ≤ −1 VE btc_r24z ≤ −1 VE konum ≤ 0,2. Olaylar arası en az H saat.
- Varyantlar: H = 4 ve 24 saat; 🎯 yok ya da 🎯 = G·(1 + 0,75·σ1·√H) (saatlik en yüksekle) → 4 deneme.
- Giriş: kapanış + %0,10 gecikme cezası; ücret piyasa %0,05 + %0,05 (🎯 çıkışı limit %0,02) + fonlama %0,01 × H/8.
- Plasebo: aynı coin, aynı takvim ayında tüm saatlerden aynı kuralla (aynı H, aynı 🎯) koşulsuz ortalama.
- Veri: araştırma coin'leri (keşif 2022-06 → 2024-12 iki yarı; KONTROL A 2025+) ve dokunulmamış coin'ler (KONTROL B, sekil_liste.json'daki B listesi).
- Şart her birinde (keşif ½-1, ½-2, A, B): işlem başı net > +%0,15 · plasebodan ≥ 0,15 puan iyi · isabet ≥ %55 · haftada ≥ 2 olay.

Geçen hiçbir şey kullanıcı onayı olmadan canlıya alınmaz; önce gölge izleme.
