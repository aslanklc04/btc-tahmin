# Önceden yazılı protokol — OLASILIK BİLİMİNDEN ÜÇ YÖNTEM (olasilik2 · 03.11.2026)
_Kullanıcı (03.11): "Olasılık biliminden daha şey türet." Hesaptan önce yazıldı; sonradan değiştirilmez. Canlıya yalnız kullanıcı onayıyla._
Veri: veri_seti ⋈ karal2 (D_T0, tüm gönderilen sınıflar), saat sepeti = aynı t'deki sinyallerin ortalama neti. Test yılları: 2024 · 2025 · 2026 (her biri yalnız geçmişle).

## P1 — Markov zinciri / "sıcak el": kazanç kazancı mı getirir?
- Saat sepetleri sırayla (sonucu sinyal anında BİLİNEN önceki sepet: bitişi < t). Durum = önceki bilinen sepet kazandı mı.
- Ölç: P(kazan | önceki kazandı) − P(kazan | önceki kaybetti); ve kural: önceki kazandıysa pay ×1,5, kaybettiyse ×0,5 → ağırlıklı net vs eşit.
- **Geçer:** ÜÇ yılda da fark ≥ +3 puan VE ağırlıklı net ≥ eşit + %0,05 VE plasebo (sıra karıştırma ×200) %95'lik dilimini aşar.

## P2 — Thompson örneklemesi (çok kollu haydut): hangi türe ne kadar pay?
- Kol = sınıf × tür. Her kolun isabeti Beta(1+kazanç, 1+kayıp), yalnız sonucu t'den önce bilinen işlemlerle (son 180 gün). Pay = P(kolun gerçek neti > 0) (net için normal yaklaşım: ort ± std/√n) → pay ∈ [0, 1], ≤ 0,2 olan kol atlanır.
- Ölç: pay ağırlıklı işlem başı net ve isabet vs eşit pay (tüm sinyaller).
- **Geçer:** ÜÇ yılda da ağırlıklı net ≥ eşit + %0,05 VE isabet ≥ eşit.

## P3 — Gizli Markov modeli (HMM): piyasa rejimi
- BTC günlük getirisinden 2 durumlu Gauss HMM; her ay yalnız geçmiş veriyle yeniden kurulur (EM, 50 tekrar); sinyal anındaki durum olasılığı İLERİ algoritmasıyla (geleceğe bakmadan) hesaplanır.
- Durumlar oynaklığa göre adlandırılır: "sakin" / "fırtınalı". Ölç: her durumda sinyal isabeti ve neti.
- Kural: kötü durumun (eğitimde neti düşük olan) olasılığı ≥ 0,7 iken sinyal alma.
- **Geçer:** ÜÇ yılda da kuralın neti ≥ tümü + %0,05 VE isabeti ≥ tümü VE sinyallerin ≥ %50'si kalır.
