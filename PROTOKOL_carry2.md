# Önceden yazılı ölçüm — BÜYÜK COIN'LERDE FONLAMA GELİRİ (spot al + vadeli sat), YIL YIL (carry2 · 12.11.2026)
_Kullanıcı (12.11): "Borsada sürekli gelir elde edilecek yollar bul." hedge_carry (25.10) tüm coin'lerde fonlama eşiğiyle gir-çık kuralını sınadı ❌. Burada en sade hali ölçülür:
büyük coin'lerde sürekli tutulan piyasa-nötr pozisyon. Not: BTC'nin yıllık fonlama toplamları bu protokol yazılmadan görüldü (2022 %4, 2025 %5, 2026 ilk 10 ay %2,6) → bu bir keşif değil ÖLÇÜMDÜR._
- Veri: yeniliste_fon (Binance USDT-M gerçek fonlama, 2020 → 2026-10). Sabit liste: BTC ETH SOL BNB XRP DOGE ADA LINK AVAX LTC.
- Sermaye = spot tutarı × 1,5 (vadeli short için %50 teminat; ~+%45 yükselişte teminat ekleme gerekir). Getiri = fonlama toplamı / 1,5.
- K1 tek coin sürekli · K2 10 coin eşit ağırlık sürekli · K3 aylık dönüş: her ay başı, önceki 30 günün fonlaması en yüksek coin (değişirse maliyet %0,30 / 1,5) ·
  K4 K2 ama yalnız sepetin önceki 7 gün ort. fonlaması > %0,01 / 8 s iken (değilse nakit; her giriş-çıkış %0,30 / 1,5).
- Ölçüt: "anlamlı sürekli gelir" = 2022–2026'nın HER yılında sermaye üzerinden net ≥ %6 (USDT Earn üst sınırı) ve negatif ay oranı ≤ %25.
