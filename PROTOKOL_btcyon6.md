# Önceden yazılı protokol — BTC'NİN YÖNÜ, 6. TUR: KORKU VE RAHATLIK DÖNGÜSÜ (btcyon6 · 30.10.2026)
_5. tur ipucu: opsiyon ATM IV'si 3 günde sert yükselince (üst %20) sonraki 72 s BTC yön %63/%56/%62, net +1,98/+1,22/+0,36 (yalnız C1 yön şartının 1 puan altında). Aynı fikir daha uzun ve saatlik veriyle (Deribit DVOL, 2021-10'dan) ve fiyat bağlamıyla test edilir. Hesaplardan önce yazıldı; sonradan değiştirilmez. Ortak tanımlar/şartlar PROTOKOL_btcyon.md ile aynı (K 2022–23 · C1 2024 · C2 2025-01 → 2026-10-27). Canlıya yalnız kullanıcı onayıyla._

## Durumlar (gün sonu 23:00 UTC'de bilinen; giriş ertesi gün 00:00)
- **dv3** = DVOL / 3 gün önceki DVOL − 1 · **dvz** = DVOL'un önceki 90 güne göre z'si · **r3** = BTC 3 g getiri · **lsz** = kalabalık L/S z (btcneden).
- Eşikler K'den (üst/alt %20, %10).

## Kurallar (yön önceden sabit — mantık: korku zirvesi = dip, rahatlık = tepe riski)
- **R1 korku sıçraması:** dv3 ≥ K %80 → AL · ayrıca ≥ K %90.
- **R2 korku + düşüş (panik):** dv3 ≥ K %80 ve r3 ≤ 0 → AL.
- **R3 korku + yükseliş (kısa sıkışması):** dv3 ≥ K %80 ve r3 > 0 → AL (bilgi: yön aynı mı).
- **R4 aşırı korku seviyesi:** dvz ≥ 2 → AL.
- **R5 rahatlık:** dvz ≤ K %10 ve lsz ≥ 1 (kalabalık uzun) → SAT.
- **R6 panik + kalabalık kısa:** R2 ve lsz ≤ 0 → AL.
- Ufuklar: 72 s ve 168 s (7 g); aynı anda tek işlem; vadeli maliyet + gerçek fonlama.
- **Ek kontrol:** her kural ETH ve SOL'da (BTC durumu ile) C1 ∪ C2 net > 0.

## Şartlar
"Yön bulundu": her dönemde yön ≥ %57, net > 0, ≥ 15 işlem (günlük kural, seyrek). "Sinyal adayı": isabet ≥ %65, net ≥ +%0,5. Plasebo zaman kaydırma ×50.
