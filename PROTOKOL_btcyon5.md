# Önceden yazılı protokol — BTC'NİN YÖNÜ, 5. TUR: EMİR DEFTERİ VE OPSİYONLAR (btcyon5 · 30.10.2026)
_Kullanıcı (30.10): "Gölge izleme ve 5. tur başlasın; yön hedefinde cevap aramaya devam." 1–4. turlar (≈350 kural) şartı geçen bulamadı; bu tur yön için hiç bakılmamış iki bilgiyi dener: emir defterindeki alım/satım duvarları ve opsiyon piyasasındaki korunma/iddia akışı. Hesaplardan önce yazıldı; sonradan değiştirilmez. Ortak tanımlar ve şartlar PROTOKOL_btcyon.md ile aynı. Canlıya yalnız kullanıcı onayıyla._

## Veri (btcyon5_veri.py, GitHub Actions)
- **Binance vadeli emir defteri arşivi** (bookDepth, BTCUSDT): fiyatın ±%1…±%5 bandındaki toplam alım (−) ve satım (+) emri ($), ~30 sn'de bir → saatlik ortalama.
- **Deribit opsiyon işlemleri** (history.deribit.com, BTC): her gün 00:00 ve 12:00 UTC'den başlayan ilk 1.000'er işlem (örneklem) — işlem yönü (alıcı/satıcı agresif), opsiyon türü, kullanım fiyatı, vade, örtük oynaklık (IV), endeks fiyatı.

## Dönemler
Standart (K 2022–23 · C1 2024 · C2 2025-01 → 2026-10-27). Emir defteri arşivi daha geç başlıyorsa K = arşivin ilk 12 ayı, C1 = sonraki 12 ay, C2 = kalanı (rapor başında yazılır).

## V1 — Emir defteri dengesizliği (saatlik)
- d_k = (alım$ − satım$) / (alım$ + satım$), k ∈ {%1, %2, %5} bandı; saatlik ortalama. Durumlar: d1, d2, d5 seviye · d2'nin 24 s değişimi · "yakın/uzak" farkı d1 − d5.
- Üst/alt %20 (K eşikleri) → sonraki 4 s / 24 s; yön K'nin ortalama işaretinden.

## V2 — Opsiyon akışı (günlük, örneklem)
- Agresif alım primi ($ = fiyat × miktar × endeks): put alım / call alım oranı (log) · agresif net yön = (call alım − call satım) − (put alım − put satım), toplam prime bölünmüş.
- Çarpıklık: vade 7–60 g; %5–15 OTM put'ların ortalama IV'si − %5–15 OTM call'ların ortalama IV'si. ATM (±%2) IV'nin 3 g değişimi.
- D günü örneklemi → D+1 açılışından 1 g / 3 g; üst/alt %20 (K) → yön K'den.

## V3 — Birleşik
- V1 (d2, d1 − d5) + V2 (put/call alım oranı, net yön, çarpıklık) + btcyon4 W4 skoru → K'de ridge (λ = 10) 24 s getirisi; C1 için K, C2 için K + C1 ile eğitim; üst/alt %10 → AL/SAT 24 s. (V2 günlük değeri o günün saatlerine ertesi gün 00:00'dan itibaren aktarılır.)

## Şartlar
"Yön bulundu" (her dönemde yön ≥ %57, net > 0, ≥ 30 işlem) ve "sinyal adayı" (isabet ≥ %65, net ≥ +%0,2 / +%0,5); plasebo zaman kaydırma ×20.
