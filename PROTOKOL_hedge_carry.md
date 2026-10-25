# Önceden yazılı protokol — (1) BTC'ye karşı korumalı sinyal · (2) fonlama kazancı (spot al + vadeli sat) (25.10.2026)
_Kullanıcı: "araştırmaya devam et, bir şey bulmadan bulmuş sayma." Veri ve sonuç görülmeden yazıldı._

## (1) BTC korumalı sinyal — mevcut gönderilen sinyaller (veri_seti.csv.gz; ✅ ana · 🔸 yedek · 📋 panelden)
- İşlem: sinyal saatinde coin AL + aynı tutarda BTC vadeli SAT; süre sonunda ikisini kapat. Getiri = coin getirisi − BTC getirisi.
- Giriş: kapanış + %0,10 gecikme cezası (coin) ve %0,02 (BTC, çok likit); ücret: coin %0,05 + %0,05 · BTC %0,05 + %0,05; fonlama: coin uzun −%0,01/8 s, BTC kısa +%0,01/8 s → net 0 sayılır. 🎯 yok (süre sonu).
- Karşılaştırma: aynı sinyaller korumasız (coin al, süre sonu, aynı giriş cezası ve ücret).
- Şart (sınıf başına, keşif 2022-06 → 2024-12 iki yarıda ayrı ayrı VE KONTROL 2025+ ve 2026'da): korumalı işlem isabeti ≥ korumasız + 5 puan VE korumalı işlem başı net > 0 VE saat isabeti ≥ korumasız + 5 puan.
- 3 deneme (sınıf başına bir).

## (2) Fonlama kazancı — Binance USDT-M sürekli kontratlar
- Veri: data.binance.vision aylık fundingRate + aylık 1 s vadeli kline (fiyat) + spot 1 s kline. Coin'ler: araştırma listesi (KEŞİF 2022-01 → 2024-12, KONTROL A 2025+) ve dokunulmamış liste (KONTROL B), ikisinde de vadeli kontratı olanlar.
- Giriş: son 3 fonlamanın ortalaması ≥ X iken bir sonraki saat başında spot AL + vadeli SAT (eşit tutar). Çıkış: son fonlama < %0,01 olunca ya da 14 gün dolunca, bir sonraki saat başında ikisini kapat. Aynı coin'de açıkken yeni giriş yok.
- X ∈ {%0,03 · %0,05 · %0,10} (8 saatlik oran) → 3 deneme.
- Getiri = (spot çıkış/giriş − 1) − (vadeli çıkış/giriş − 1) + Σ alınan fonlama − ücret (spot %0,10 + %0,10, vadeli %0,05 + %0,05 = %0,30) − kayma %0,10 (iki bacak, giriş+çıkış toplam).
- Şart (keşif iki yarıda, KONTROL A ve B'de ayrı ayrı): işlem isabeti ≥ %70 · işlem başı net ≥ +%0,30 · ayda ≥ 2 işlem · en kötü işlem ≥ −%10.
- Raporlanır: yıllık getiri (sermaye = spot tutarı × 1,5, vadeli teminat dahil), en kötü işlem, ortalama süre.

## Genel
- Toplam 6 deneme. Geçmeyen "bulunamadı" diye raporlanır. Geçen önce gölge izlemeye alınır; kullanıcı onayı olmadan canlıya bir şey alınmaz.
