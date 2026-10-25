# Önceden yazılı protokol — sinyal saatlerinde coin yerine BTC almak (25.10.2026)
_Gerekçe: hedge_carry_sonuc.md (1): BTC'ye karşı korununca sinyallerin isabeti %40–49'a düşüyor → başarının kaynağı büyük ölçüde BTC'nin yönü. Soru: aynı saatlerde BTC almak daha mı iyi? Veri ve sonuç görülmeden yazıldı._

- Sinyaller: veri_seti.csv.gz gönderilen sinyaller (✅ ana · 🔸 yedek · 📋 panelden), sınıf başına saat sepetleri.
- COIN (taban): her sinyal için coin al, kapanış + %0,10 gecikme cezası, ücret %0,05 + %0,05, fonlama %0,01 × H/8; 🎯 = sınıf k'sı × σ_coin × √H (saatlik en yüksekle; değerse limit çıkış %0,02).
- BTC: aynı saatte, aynı H ile BTC al, kapanış + %0,02, aynı ücret/fonlama; 🎯 = aynı k × σ_BTC × √H. Bir saatte kaç sinyal olursa olsun o saat için tek BTC işlemi (sınıf başına, H = o saatteki sinyallerin en sık H'si).
- Ölçüt: saat isabeti, saat başı net, ayrıca "risk başına kâr" = saat başı net ÷ o saatteki işlemin σ×√H'si (BTC daha az oynak; aynı riskle daha büyük pozisyon alınabilir).
- ŞART (sınıf başına; keşif 2022-06 → 2024-12 iki yarıda ve KONTROL 2025+ ve 2026'da ayrı ayrı): BTC saat isabeti ≥ COIN + 3 puan VE BTC risk başına kâr ≥ COIN risk başına kâr.
- 3 deneme. Geçmezse "bulunamadı". Geçerse önce gölge izleme.
