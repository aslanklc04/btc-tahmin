# Önceden yazılı protokol — USDT/TL MAKASI: düzenli, coin riski olmayan gelir var mı? (makas · 03.11.2026)
_Kullanıcı (03.11): "Binance'te (yerel ve global) kimsenin keşfetmediği düzenli gelir bul." Veri indirilmeden ve hesaptan önce yazıldı; sonradan değiştirilmez (gerekirse tarihli "Ek"). Canlıya yalnız kullanıcı onayıyla._

## Fikir
Binance'te USDT/TL (USDTTRY) 7/24 işlem görür; bankalar arası USD/TL (Yahoo TRY=X) hafta sonu kapalıdır. **Makas** p = USDTTRY / USDTRY_bankalararası − 1. Makas düzenli olarak ortalamaya dönüyorsa, USDT iskontoluyken al / primliyken sat → coin riski olmadan küçük, tekrarlanan gelir.

## Veri (makas_veri.py, Actions)
- Binance global spot USDTTRY 1 s mum (data-api.binance.vision), 2022-01 → bugün. Bilgi: BTCTRY ve BTCUSDT (TL'deki BTC fiyatından ima edilen kur).
- Yahoo TRY=X saatlik (yfinance, ~730 g) ve günlük (2022 →).
- Dönemler (saatlik makas verisi olan aralıkta): **S** ilk yarı (seçim) · **T** ikinci yarı (test).

## Kurallar (önceden sabit)
- **M1 iskonto al:** p ≤ eşik (S'deki %10'luk dilim) → USDT al; p ≥ 0 (makas kapanınca) ya da 72 s dolunca sat.
- **M2 prim sat (USDT tutan için):** p ≥ S'deki %90'lık dilim → USDT sat (TL'ye geç); p ≤ 0 ya da 72 s → geri al. Getiri = USDT tutmaya göre fark.
- **M3 hafta sonu kalıbı:** Cuma 20:00 UTC al / Pazartesi 08:00 UTC sat ve tersi; getiri USDT/TL değişimi.
- Ücret: işlem başı %0,10 + %0,10 (taker) ve %0,02 kayma; bilgi: %0,075 (BNB indirimli).
- Ölçü: işlem başı net, isabet, ayda işlem sayısı, yıllık getiri (yalnız işlemdeyken), en kötü işlem.
- **Taban:** aynı dönemde USDT'yi sürekli tutmak (TL değer kaybı); M1/M2 getirisi bu tabana göre FAZLA olarak raporlanır.
- **Plasebo:** giriş saatleri aynı dönemde rastgele (aynı sayıda) ×50.

## Karar
**"Düzenli gelir bulundu":** S ve T'de ayrı ayrı işlem başı fazla getiri > 0 (ücret sonrası) VE isabet ≥ %65 VE ayda ≥ 2 işlem VE plasebonun en iyisinden yüksek VE en kötü işlem ≥ −%2. Geçerse önce gölge izleme.
