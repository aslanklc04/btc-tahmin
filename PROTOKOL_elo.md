# Önceden yazılı protokol — MAÇ TARZI GÜÇ SIRALAMASI (Elo) ile coin seçimi (elo · 03.11.2026)
_Kullanıcı (03.11): "Maç tahmini / hava tahmini yapan yapay zekâlar gibi kripto borsasına uyarlasak belki birkaç yöntem işe yarayabilir." Hesaptan önce yazıldı; sonradan değiştirilmez. Canlıya yalnız kullanıcı onayıyla._

## Veri · işlem
- teknik3_mum (141 coin, Binance vadeli 1 s) → günlük kapanış (00 UTC). 2022-01 → 2026-10.
- Her gün 00 UTC'de puanlar hesaplanır → en yüksek puanlı **4 coin AL**, eşit pay; tutma: **G1** 1 gün · **G7** 7 gün (haftalık yenileme, yalnız Pazartesi). Spot ücret %0,10 + %0,10 + kayma %0,05 her değişen pozisyon için (tutulan coin değişmezse ücret yok).
- **Kıyas:** aynı gün tüm coin'lerin eşit ağırlıklı ortalaması (piyasa) · BTC. **Fazla getiri = seçilen 4 − piyasa** (ücret sonrası).

## Puanlar (önceden sabit, 4 deneme)
- **E1 Elo:** her gün her coin "piyasaya karşı maç" oynar: günlük getirisi piyasa medyanının üstündeyse 1, altındaysa 0; beklenen skor = 1/(1+10^(−(R−1500)/400)); R ← R + 20·(skor − beklenen). Başlangıç 1500.
- **E2 Elo, rakip sırayla:** her gün coin'ler rastgele eşleşir (seed sabit), kazanan = günlük getirisi yüksek olan; K = 20.
- **E3 7 g göreli güç** (son 7 günde piyasaya göre getiri) · **E4 ters: son 7 günün EN ZAYIF 4'ü** (dönüş).
- Yalnız t'ye kadar bilinen veri; ≥ 60 gün geçmişi olan coin'ler.

## Karar
Yıllar: 2022 · 2023 · 2024 · 2025 · 2026 (ayrı). **"İşe yarıyor":** BEŞ yılda da yıllık fazla getiri > 0 (ücret sonrası) VE günlerin ≥ %52'sinde piyasayı yener VE rastgele 4 coin seçiminin (×50) en iyisinden yüksek. Bilgi: en büyük düşüş, BTC'ye göre.
