# Önceden yazılı protokol — RİSKİ AZALTAN EN İYİ STOP (stop · 01.11.2026)
_Kullanıcı (01.11): "Riski de minimize etmek için en ideal stop kullanımını yap." Bu dosya veri toplanmadan ve hesaplardan önce yazıldı; sonradan değiştirilmez (gerekirse tarihli "Ek"). Testleri geçen kural kullanıcının talimatıyla ("testleri yap, geçerse ekle") mesajlara eklenir; geçmezse eklenmez, raporlanır._

## Neden
Bugün stop yok: 🎯 kâr-al + süre sonu çıkış. Ortalama kâr iyi, ama tek işlemde −%20…−%30 kayıp görülebiliyor. Önceki çıkış araştırması (cikis.py, 08.10) stopların NET'i düşürdüğünü buldu; bu araştırmanın amacı farklı: **kuyruk riskini (en kötü işlemler) azaltırken isabeti ve kârı korumak.**

## Veri
- Sinyaller: veri_seti.csv.gz (✅ ana · 🔸 yedek · 📋 panelden, (t, nm, sinif, H) tekrarsız), 2022-06 → 2026-10-21.
- Fiyat yolu: Binance 1 dk mum, sinyal saatinden t+H'ye kadar (stop_veri.py, Actions; simülasyon da orada).
- Giriş **D** (ana): t+7. dakika açılışı, piyasa, ücret %0,05 · destek **B**: mesaj fiyatına limit (karal2 ile aynı kural).
- 🎯 = sınıf kuralı G·(1 + k·σ720·√H), k: ana 0,75 · yedek 0,50 · panelden 0,45 (bugünkü). Fonlama: geçilen her 00/08/16 UTC −%0,01.
- **Stop dolumu (kötümser):** stop-piyasa; dakika açılışı stopun altındaysa açılıştan, değilse stop seviyesinden × (1 − %0,05 kayma); ücret %0,05. Aynı dakikada hem 🎯 hem stop → STOP sayılır.

## Stop türleri (bu liste dışında aday yok)
- **S0** stop yok (bugünkü).
- **SS-m** oynaklık stopu: Pe·(1 − m·σ720·√H), m ∈ {1 · 1,5 · 2 · 3 · 4}.
- **SY-p** sabit yüzde (felaket) stopu: Pe·(1 − p), p ∈ {%5 · %8 · %12 · %15 · %20}.
- **SA-m** ATR stopu: Pe − m·ATR14·Pe·√(H/4) (ATR14 = son 14 saatin ort. (yüksek−düşük)/kapanış), m ∈ {2 · 3 · 4}.
- **BE-m** başa baş + felaket: fiyat 🎯 yolunun yarısına (Pe + 0,5·(🎯 − Pe)) değince stop Pe·1,001'e çekilir; o ana kadar SS-m stopu, m ∈ {2 · 3}.

## Ölçüler (sınıf × dönem)
işlem · isabet (net > 0) · işlem başı net · **en kötü işlem** · **CVaR5** (en kötü %5 işlemin ortalaması) · stop olan işlem oranı · bilgi: günlük toplam getiri dizisinde en büyük düşüş (MDD, işlem başı eşit pay).

## Dönemler ve karar (sınıf başına ayrı: ✅ ana · 🔸 yedek · 📋 panelden)
- **Seçim A** (2022-06 → 2024): S0'a göre isabet ≥ S0 − 3 puan VE net ≥ S0 − %0,05 olan türler içinden **CVaR5'i en iyi (en az kayıp) olan TEK tür** seçilir.
- **Test B** (2025) ve **C** (2026), ayrı ayrı: aynı iki şart VE CVaR5 S0'a göre en az %20 daha iyi VE en kötü işlem S0'dan iyi.
- **T1 coin yarıları** (md5): her yarıda (tüm dönemler) aynı üç şart.
- **T2 limit giriş (B):** her dönemde net farkı ≥ −%0,05 ve CVaR5 iyileşmesi ≥ %20.
- **T3 canlı (12.10 →, karne_gercek ile aynı sinyaller):** bilgi.
- **Plasebo yok** (stop bir seçim değil, kural); bunun yerine seçim yalnız A'da yapılır, B/C/yarılar görülmemiş veridir.
- **Karar:** sınıf için seçim + B + C + T1 + T2 geçerse o sınıfın mesajına 🛑 stop satırı eklenir. Geçmezse eklenmez ve en iyi aday sayılarıyla raporlanır.
