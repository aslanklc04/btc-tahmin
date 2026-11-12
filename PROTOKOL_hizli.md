# Önceden yazılı protokol — AYNI SAATTEKİ SİNYALLERDEN EN HIZLI VE EN KÂRLI OLANI SEÇMEK (hizli · 12.11.2026)
_Kullanıcı (12.11): "Yükselecek tüm coinler arasında en önce ve hızlı, hem de en çok kârlı olacakları bulamaz mıyız?" Önceki: meta-model (tutar/tutmaz) ❌, saatte en iyi 3 ❌ kaldırıldı,
A2 (prim z en yüksek 5) sınırda. Fark: hedef artık "tutma" değil HIZ ve BÜYÜKLÜK. Hesaptan önce yazıldı._

## Veri
veri_seti ⋈ karal2_veri ⋈ garch_rho (tüm sınıflar, 2022-06 → 2026-10) + teknik3_mum saatlik yol. Evren: aynı saatte ≥ 4 sinyal olan saatler (sıralama anlamlı olsun).
- **Hızlı (F):** 🎯 (sınıfın bugünkü hedefi) sürenin ilk çeyreğinde (ilk ⌈H/4⌉ saat, saatlik en yüksekle) değdi.
- **Kâr:** D_T0 (bugünkü kural) ve D_T1_1.0 (kazananı koşturan izleyen stop) · büyüklük: mfeD (süre içindeki en büyük lehte hareket, %).
## Sıralayıcılar (t anında bilinen) — saat başına en üstteki 3 alınır
S1 en oynak (s büyük) · S2 en sakin (s küçük) · S3 prim z en yüksek · S4 son 4 s en çok düşen (c_r4 küçük) · S5 son 4 s en çok yükselen (c_r4 büyük) · S6 24 s z en düşük (rz) ·
S7 GARCH ρ en yüksek · S8 son 24 s en çok yükselen (c_r24 büyük) · M1 model → F olasılığı · M2 model → D_T1_1.0 beklenen net
(HistGradientBoosting, yıllık yürüyen: 2024, 2025, 2026 için eğitim = önceki yıllar; özellikler: s, H, z, rz, fon, zB, b_r4, b_r24, b_vr, gen24, c_r4, c_r24, hod, dow, ρ, sınıf, saatteki sinyal sayısı).
## Karar (dönemler: 2022-06→24 · 2025 · 2026; modeller için 2024 · 2025 · 2026)
Karşılaştırma: aynı saatlerde RASTGELE 3 sinyal (×50).
- **"Bulundu":** bir sıralayıcı ÜÇ dönemin hepsinde: hızlı oranı > rastgelenin en iyisi VE D_T0 net > rastgelenin en iyisi VE isabet ≥ rastgelenin ortalaması − 1 puan.
- **"Yalnız hız/büyüklük":** hızlı oranı ve mfe üç dönemde rastgelenin en iyisinden yüksek ama net değil → raporlanır (kâra dönmüyor).
- Zorunlu bilgi: seçilenlerin en kötü işlemi, net std'si (risk), D_T1_1.0 neti, kaybedenlerin ort. kaybı.
