# Önceden yazılı protokol — fiyat hareket ŞEKİLLERİ atlası ve etkenleri (25.10.2026)
_Kullanıcı: "her saat ne yapmış — direkt yükselen, kısa düşüp uzun yükselen, uzun yükselip sonda düşen, iki yönde çok oynayan… 1 · 4 · 8 · 24 saatte ayrı ayrı; sebeplerini araştır." Veri indirilmeden yazıldı._

## Veri
- Binance spot 5 dk mum (data.binance.vision aylık arşiv), 2022-06 → 2026-09.
- ARAŞTIRMA coin'leri = canlı listeler (genis_liste + coin_listesi). DOKUNULMAMIŞ coin'ler = Binance USDT spot çiftlerinden araştırmalarda hiç kullanılmamış, 2022-06'dan önce listelenmiş, en yüksek hacimli ≤ 120 coin (sabit/kaldıraçlı token hariç).
- Pencereler her saat başında başlar; W ∈ {1, 4, 8, 24} saat. σ_W = coin'in son 720 saatlik saatlik σ'sı × √W (pencere başında bilinir).

## Şekiller (W penceresinde, açılışa göre; up = en yüksek/σ_W, dn = −en düşük/σ_W, r = kapanış getirisi/σ_W) — ilk uyan
1. ↕️ Testere: up ≥ 1 ve dn ≥ 1
2. ➖ Sakin: up < 0,5 ve dn < 0,5 ve |r| < 0,25
3. ⬆️ Direkt yükseliş: r ≥ 0,25 · dn < 0,5 · (up − r) < 0,5
4. ⬆️↘️ Yükselip sonda geri çekildi: r ≥ 0,25 · dn < 0,5 · (up − r) ≥ 0,5
5. ↘️⬆️ Kısa düşüp uzun yükseldi: r ≥ 0,25 · dn ≥ 0,5
6. ⬇️ Direkt düşüş: r ≤ −0,25 · up < 0,5 · (r + dn) < 0,5
7. ⬇️↗️ Düşüp sonda biraz toparladı: r ≤ −0,25 · up < 0,5 · (r + dn) ≥ 0,5
8. ↗️⬇️ Kısa yükselip uzun düştü: r ≤ −0,25 · up ≥ 0,5
9. ↔️ Gidip döndü (yatay kapanış): kalanlar

## Etkenler (pencere başında bilinen; sabit dilimler, veriden seçilmez)
r1 · r4 · r24 = coin'in son 1/4/24 saat getirisi / σ (≤ −1 · arası · ≥ 1) · vol = σ24/σ720 (≤ 0,8 · arası · > 1,25) · hacim = log(son 24 s hacmi / 720 s ortalaması) (≤ −0,4 · arası · > 0,4) · konum = 24 s aralıktaki yer (≤ 0,2 · arası · > 0,8) · btc_r4 · btc_r24 (≤ −1 · arası · ≥ 1) · btc_vol (≤ 0,8 · arası · > 1,25) · saat (TR 00–06 · 06–12 · 12–18 · 18–24) · gün (hafta içi · sonu) · önceki şekil (aynı W'de bir önceki pencere, 9 değer).

## Atlas (yalnız betimleme)
Şekil sıklıkları; saate, güne ve BTC durumuna göre; şekil → bir sonraki pencerenin şekli ve getirisi.

## Keşif kuralı (etkenler)
- KEŞİF = araştırma coin'leri, 2022-06 → 2024-12. DOĞRULAMA A = araştırma coin'leri 2025-01 →. DOĞRULAMA B = dokunulmamış coin'ler, 2022-06 →.
- Kaldıraç (lift) = P(şekil | etken dilimi) / P(şekil). Bir sonuç "KEŞİF" sayılır ancak: keşifte lift ≥ 1,3 (ya da ≤ 0,77) ve ≥ 2.000 olay, VE A'da da B'de de aynı yönde lift ≥ 1,15 (ya da ≤ 0,87) ve her birinde ≥ 1.000 olay.
- Toplam deneme sayısı raporlanır (≈ 4 W × 9 şekil × 41 etken dilimi). Bu aşamada hiçbir şey işlem kuralı olmaz; işlem kuralına çevirmek ayrı, önceden yazılı bir testle yapılır.
