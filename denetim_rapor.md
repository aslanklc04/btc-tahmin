# Bağımsız denetim raporu: Telegram'daki isabet oranları gerçek mi?

_24.10.2026 · dal: `denetim` · canlı koda ve kurallara dokunulmadı · ayrıntılı çıktılar: `dt/analiz_sonuc.md`, `dt/canli_sonuc.md`_

## Kısa cevap
- **Rakamlar hesap olarak doğru.** Kuralları canlı koddan okuyup kendi kodumla yeniden kurdum, testin yöntemini birebir uyguladım. ✅ ana için %69 · %69 · %74, 🔸 yedek için %75 · %73 · %75, 📋 panelden için %71 · %73 · %71 çıktı. Mesajdakilerle neredeyse aynı.
- **Ama bu oranlar canlıda kazanacağın şeyi göstermiyor.** Oranı yükselten şey büyük ölçüde sinyal değil, yakın tutulan 🎯 kâr-al hedefi. Aynı hedefle rastgele bir saatte alsan bile isabet ✅ anada ~%54, 🔸 yedekte ~%60, 📋 panelden ~%63 çıkıyor.
- **Gerçekçi uygulamada isabet biraz, kâr ise çok düşüyor.** Gerçekçi uygulamadan kastım şu: giriş mesaj geldikten sonra, spot komisyon gidiş-dönüş %0,2. Bu durumda ✅ ana ~%67 tutuyor (işlem başı ~+%0,2), 🔸 yedek ~%68 tutuyor (işlem başı ~%0), 📋 panelden ~%66 tutuyor (işlem başı ≈ 0 ya da eksi).
- **Canlıda "%74 · %71 · %76" gibi oranlar beklenebilir ama yanıltıcı.** İsabet %65–75 civarında kalabilir, ama yedek ve panelden sinyallerinde komisyondan sonra kayda değer kâr beklenmemeli. Bir de şu var: kuralların hepsi aynı verinin üzerinde seçildi. Seçimden sonraki tek veri 12 günlük canlı dönem ve orada yalnızca ~17 bağımsız saat var. Bu kadar veriyle hiçbir şey kanıtlanamaz.

## Sinyal türü başına karşılaştırma

Dönemler: 2022-06→2023 · 2024–25 · 2026. Hepsinde isabet = net > 0.

| Tür (🎯 hedef) | Mesajda/testte söylenen | Benim test yöntemi kopyam (maliyet %0,04) | Aynı 🎯 ile **rastgele giriş** | Benim gerçekçi ölçümüm (mesajdan sonra piyasa alışı, 1 dk mum, maliyet %0,2) | Canlı 12.10–24.10 (mesaj fiyatı, 1 dk, maliyet %0,2) |
|---|---|---|---|---|---|
| ✅ ana (+0,75σ) | %69 · %71 · %74, işlem başı +%0,4–0,6 | %69 · %69 · %74 | %54 · %54 · %53 | **~%67**, işlem başı **+%0,19** (örneklem 450) | **%64**, işlem başı **−%0,17**. 45 sinyal / 17 saat; saat bazında %41 |
| 🔸 yedek (+0,50σ) | **%74 · %71 · %76**, işlem başı +%0,05–0,3 | %75 · %73 · %75 | %60 · %60 · %59 (plasebo: %70 · %68 · %71) | **~%68**, işlem başı **+%0,08** | %84 (piyasa alışıyla %80), işlem başı +%0,4–0,5. 179 sinyal / **17 saat**; saat bazında %76; aynı saatlerin plasebosu %65 |
| 📋 panelden (+0,45σ) | %72 · %72 · %72, işlem başı +%0,2 | %71 · %73 · %71 | %63 · %64 · %63 | **~%66**, işlem başı **−%0,06** | Yalnız 3 sinyal var, ölçülemez |

Tablodaki terimler:
- **Rastgele giriş:** Aynı coin'de, sinyal tarihinin ±30 günü içindeki bütün saatlerde aynı 🎯 ve süre kuralıyla alım yapılmış gibi hesaplandı. Sinyalin "hiçbir şey bilmeden" verdiği taban budur.
- **Plasebo (yedek için):** Aynı saatlerde coin sinyali olmayan ama primi aynı aralıkta (0…2) olan geniş liste coin'leri.

Saatlik veriyle, test girişiyle ve maliyet %0,2 ile işlem başı net, dönemlere göre:

| Tür | 2022-06→2023 | 2024–25 | 2026 |
|---|---|---|---|
| ✅ ana | +0,26 | +0,36 | +0,53 |
| 🔸 yedek | +0,05 | −0,03 | +0,14 |
| 📋 panelden | +0,06 | +0,12 | +0,04 |

- Yedek ve panelden için %90 güven aralıkları sıfırı içeriyor.
- Alt türlerde: 🤝 ana coin −0,02 · −0,03 · +0,24. 🌐🤝 +0,19 · +0,32 · +0,59. 🌐🧪 +0,53 · +0,67 · +0,78. 🌐🧪 canlıda 12 sinyalde %58 tuttu, ortalama −%1,6.

## Kontrol sonuçları

**1. Geleceğe bakma (look-ahead) — veri hizasında bulamadım (eminim).**
- Kullanılan model çıktılarındaki kapanış fiyatları ve y4 etiketleri, kendi indirdiğim Binance fiyatlarıyla gecikme 0'da birebir eşleşiyor.
- Önceki araştırmanın prim z'si benimkiyle gecikme 0'da örtüşüyor (korelasyon 0,997–0,9999). ±1 saatte örtüşmüyor.
- Testte kullanılan BTC "4s Çok güçlü ↑" serisi, canlı BTC modeliyle 1345 saatte %99,5 aynı.
- Modeller aylık yürüyen testle eğitiliyor ve yalnız geçmiş veriyi görüyor.
- Bir **seçim kaynaklı geleceğe bakma** var: bugünkü listeler ve "açık" sinyal bayrakları 2022'den itibaren geriye uygulanıyor. Bu listeler şunlar: 126 geniş coin, `ortak_acik`, `prim_acik`, modellerin "on" bayrakları. Hepsi bu dönemlerin sonuçlarına bakılarak seçildi (bkz. madde 4).

**2. Giriş fiyatı gerçekçi değil (eminim).**
- Test sinyal saatinin kapanışından giriyor. 🎯'e değip değmediğini de o saatin ilk dakikalarını içeren saatlik en yüksek fiyatla kontrol ediyor.
- 1 dakikalık mumla, mesajdan sonra (+6 dk) piyasadan girince yedek isabeti ~7–9 puan, net ~0,13 puan düşüyor. Panelden'de etki ~2 puan, ana'da ~1 puan.
- 🤝 mesajındaki "Giriş (limit)" fiyatı kodda saat kapanışı. Canlıda bu fiyattan limit emir 60 dakikada ancak %72–79 oranında doldu.
- Somut örnek, BLUR (13.10). Mesaj geldiğinde fiyat zaten kapanışın %3,3 üstündeydi. Test bu işlemi +%4,5 "tuttu" sayıyor, mesajdaki fiyatla gerçek sonuç **−%24,6**.

**3. Komisyon ve 🎯 hesabı.**
- Testler ve karne gidiş-dönüş **%0,04** maliyet kullanıyor. Bu ancak her iki tarafı da vadeli piyasada limit emirle (maker) yapılan işlemlere uyar. Binance spotta standart ücret işlem başına %0,1, yani gidiş-dönüş %0,2 (BNB indirimiyle %0,15). Süre sonu çıkışı ise piyasa emri.
- 🎯 formülü (giriş × (1 + k·σ·√H), σ = son 720 saatlik oynaklık) kodda doğru uygulanmış. Benim kopyam karne.md ile birebir aynı çıktı: ✅ %71 / +0,61, 🔸 %85 / +0,71.
- **Asıl sorun hedefin kendisi:** k değerleri, "isabeti %70'in üstünde tutan en uzak hedef" diye seçildi (esik70.py). Hedef yaklaştıkça isabet mekanik olarak artıyor, ortalama kâr düşüyor. Örnekler (maliyet %0,2):
  - Yedek 2026: süre sonu +0,39 → 🎯 ile +0,14.
  - Ana 2024–25: +0,75 → +0,36.
- 21.10'dan önceki mesajlarda 🎯 satırı hiç yoktu. Karne ise 🎯 kuralını bu mesajlara da geriye dönük uyguluyor.

**4. Aşırı uyum (emin, ama etkinin büyüklüğü belirsiz).**
- Eşikler (z ≥ 2 / 1,5 / 0), k değerleri ve coin listeleri "üç dönem"in üçüne birden bakılarak seçildi. Ayrı tutulmuş (hold-out) bir dönem yok.
- Araştırmada taranıp listeye **alınmayan** 15 geniş coin aynı kurallarla açıkça daha kötü:
  - Yedek isabeti %71 · %69 · %66.
  - Maliyet %0,2 ile net her dönemde eksi.
  - Yani liste geçmişe bakılarak süzülmüş; listedeki coin'lerin test sonucu iyimser.
- Kuraldan sonraki tek veri canlı dönem:
  - 🔸 yedek kuralı 16.10'dan beri geçerli: 173 sinyal ama yalnızca 12 ayrı saat. %85 tuttu (saat bazında %75).
  - Sınıf hedefleri 22.10'dan beri geçerli: yalnızca 4 saat var.
  - Bu kadar az bağımsız gözlemle hiçbir oran doğrulanamaz.

**5. Bağlı sinyaller isabeti şişiriyor mu? (evet, eminim).**
- Geçmişte yedeklerin saat başına ortalaması ~11,8 sinyal: 21.146 sinyal 1.792 ayrı saate dağılıyor. Canlıda tek bir saatte 44 coin gelmiş.
- Karne her coin'i ayrı başarı sayıyor. Saat bazında sayınca canlı ✅ ana isabeti %71'den %41'e düşüyor, çünkü kazananlar birkaç saatte toplanmış. Yedekte %85'ten %76'ya düşüyor.
- Geçmişte yedeklerin saat bazında neti maliyet %0,2 ile +0,04 · −0,06 · +0,03, yani sıfır.
- Coin'in kendi sinyalinin katkısı plaseboya göre küçük: geçmişte isabette +4–5 puan, nette +0,04–0,05.

**6. Canlı karne (Binance 1 dk, mesaj fiyatı ve mesajdaki 🎯 ile; ayrıntı `dt/canli_olaylar.csv`).**

| Sınıf | Sinyal / ayrı saat | Karne yöntemi | Mesaj fiyatı + 🎯, maliyet %0,2 | Mesaj anında piyasa alışı | Mesaj fiyatından limit (60 dk) |
|---|---|---|---|---|---|
| ✅ ana | 45 / 17 | %71, +0,61 | %64, −0,17 | %62, −0,37 | %76 doldu; dolanlar %56, −0,59 |
| 🔸 yedek | 179 / 17 | %85, +0,71 | %84, +0,54 | %80, +0,39 | %73 doldu; dolanlar %80, +0,55 |

- Yedeğin bu iyi sonucu çoğunlukla genel piyasa yükselişinden geliyor. Aynı saatlerde sinyalsiz geniş coin'ler %65–67 tuttu (net +0,31–0,34). Aynı dönemde rastgele saatlerde giriş %51 tuttu (net −0,23).
- 💵 sinyalleri 14.10'dan önce ana olarak gönderildi: 4'te 0.

## Ne kadar eminim
- **Eminim:**
  - Test oranlarının aritmetiği doğru.
  - Veri hizasında geleceğe bakma yok.
  - Komisyon varsayımı spot için gerçekçi değil.
  - 🎯 isabeti mekanik olarak yükseltiyor ve kârı düşürüyor.
  - Bağlı sinyaller canlı oranları şişiriyor.
  - Kurallar aynı veride seçildi.
- **Orta derecede eminim:** "Gerçekçi isabet ~%66–68" rakamı. 450'lik rastgele örneklemlerden geliyor, girişi +6 dk varsaydım. Mesajın geliş süresi değişirse sonuç birkaç puan oynar.
- **Emin değilim:**
  - Canlıda ✅ ana gerçekte kârlı mı? Canlı veri çok az.
  - Yeniden kurduğum sinyal sayıları önceki araştırmanınkinden ~1,7 kat fazla (oranlar aynı). Bunu tekrar sayımı canlı koddaki gibi tür bazında yaptığım için olduğunu düşünüyorum, doğrulamadım.
  - 💧 likidite ve 🔥 fonlama terfileri, ⛓️ ve 🧑 sinyallerini veri olmadığı için test etmedim. Canlı dönemde 🔥 terfisi hiç olmadı.
  - Geniş listenin bugünkü hacme göre seçilmesinin yarattığı hayatta kalma yanlılığını ölçmedim.

## Dosyalar (dal `denetim`)
- `dt/veri.py`: Binance 1 saatlik fiyat ve Coinbase primi, kendi indirmem.
- `dt/analiz.py`: canlı kurallarla geçmiş yeniden kurulum, rastgele/plasebo karşılaştırması, 1 dakikalık gerçekçi uygulama.
- `dt/canli.py`: karne_kayit.csv'nin 1 dakikalık mumla denetimi.
- Sonuçlar: `dt/analiz_sonuc.md`, `dt/canli_sonuc.md`.
- Gizli anahtar kullanılmadı, Telegram tetiklenmedi, main ve arastirma3 dallarına yazılmadı.
