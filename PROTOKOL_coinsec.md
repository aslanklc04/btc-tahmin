# Önceden yazılı protokol — BTC güçlü ↑ saatinde HANGİ COİN? (coinsec · 25.10.2026)
_Kullanıcı: "Araştırma ve keşife devam. Söylediğin farklı coinlerde devam et." Çıkış noktası: btc_yerine ve denetimler, sistemin kazancının büyük ölçüde BTC yönü + coin'lerin BTC'den büyük hareketinden geldiğini gösterdi. Soru: BTC güçlü ↑ dediğinde, coin'e özel model OLMADAN, basit ve önceden bilinen özelliklere göre seçilen coin'ler (gerçekçi ölçümde) kazandırıyor mu — hiç dokunulmamış coin'lerde de? Bu dosya veri indirilmeden yazıldı; sonradan değiştirilmez (değişiklik olursa "Ek" olarak tarihli eklenir)._

## Olaylar
- BTC'nin canlı modelindeki saatlik işaretler (disa_BTCUSDT.pkl: `u4` 4 s Çok güçlü ↑ · `star` ⭐ · `acls` A sınıfı). Olay = bu üçünden biri doğru olan saat; aynı olaydan sonraki 4 saat içinde yeni olay sayılmaz (çakışmasız).
- t = sinyal saatinin kapanışı. Mesaj ~t+5 dk'da sayılır.

## Coin evreni (sekil_liste.json)
- **A (araştırma):** canlı listelerdeki coin'ler (BTC hariç). **B (dokunulmamış):** hiçbir araştırmada kullanılmamış, 2022-06'dan önce listelenmiş, en yüksek hacimli 79 Binance USDT coin'i.
- Veri: Binance spot 5 dk arşivi (data.binance.vision). Olay anında ≥ 720 saat geçmişi olmayan coin o olayda yok sayılır.
- Bilinen sınırlama: listeler bugün işlem gören coin'lerden (hayatta kalan yanlılığı) — iki evrende de aynı.

## Olay anında bilinen özellikler (t'ye kadar biten saatlerden)
- `s` = coin'in 720 saatlik saatlik log-getiri σ'sı · `beta` = 720 saatte BTC'ye göre beta (EKK) · `rho` = 720 saatlik korelasyon
- `rz` = son 24 s getirisi / (s·√24) · `rel` = son 24 s log getiri − beta × BTC'nin 24 s log getirisi, / (s·√24)
- `liq` = log(720 saatlik ortalama saatlik USDT hacmi)

## İşlem ölçümü (gerçekçi; canlı kuralla aynı mantık)
- Süre 4 saat. G = sinyal saatinin kapanış fiyatı. Giriş B: G'ye limit, t+5 → t+65 dk (5 dk mumlar). İlk mumun açılışı ≤ G ise o açılıştan dolar (piyasa ücreti); değilse fiyat G'ye inerse G'den dolar (limit ücreti); dolmazsa işlem yok.
- 🎯 = G·(1 + 0,75·s·√4). Dolumdan SONRAKİ mumlarda en yüksek ≥ 🎯 ise 🎯'den çıkış (limit ücreti); değilse t+4 s+5 dk mumunun kapanışında çıkış (piyasa ücreti). 🎯 ≤ giriş ise hemen piyasa çıkışı.
- Vadeli ücretler: limit %0,02 · piyasa %0,05; fonlama yaklaşığı %0,01 her geçilen 00/08/16 UTC'de. Bilgi için D (t+5 dk açılışından piyasa girişi) da hesaplanır.
- Saat sepeti: o olayda seçilen coin'lere eşit para; dolmayanlar sepete girmez. **Saat isabeti** = sepet neti > 0 olan olay oranı · **saat başı net** = sepet netlerinin ortalaması · işlem isabeti / işlem başı net ayrıca raporlanır.

## Kurallar (olay başına k = 5 coin; hepsi aynı evren ve olaylarda)
- R0 tüm coin'ler (eşit pay) · R1 en yüksek `beta` · R2 en yüksek `s` · R3 en yüksek `rho` · R4 en düşük `rel` (geride kalan) · R5 en yüksek `rel` (öndeki) · R6 en düşük `rz` (son 24 s en çok düşen)
- Her biri ayrıca `L` filtresiyle: yalnız `liq` o olayda evrenin medyanı ve üstü olanlar arasından → toplam 14 kural.
- **Plasebo:** her olayda rastgele 5 coin (200 tekrar; aynı L filtresiyle ayrı) → ortalama ve %95'lik.
- **Taban:** aynı olaylarda yalnız BTC (aynı ölçümle).
- Toplam deneme sayısı (14) raporlanır.

## KEŞİF (yalnız A evreni, 2022-06-01 → 2024-12-31; iki yarı: → 2023-06-30 · 2023-07-01 →)
- Bir kural keşfi ancak İKİ YARIDA DA şunları sağlarsa geçer: saat isabeti ≥ plasebo ortalaması + 3 puan · saat başı net ≥ plasebo ortalaması + %0,10 · saat başı net > 0.
- Geçenlerden keşif saat başı neti en yüksek ≤ 2 kural doğrulamaya gider. Hiçbiri geçmezse doğrulama yalnız bilgi için çalışır, sonuç "keşif yok" olur.

## DOĞRULAMA (bir kez; sonuç ne çıkarsa çıksın değiştirilmez)
- Üç küme: **A 2025-01-01 →** · **B 2022-06-01 → 2024-12-31** · **B 2025-01-01 →**.
- Başarı: ÜÇ KÜMEDE DE saat isabeti ≥ %65 · saat başı net ≥ +%0,15 · plasebodan ≥ 3 puan ve ≥ %0,10 iyi · haftada ≥ 3 olay. 2026 ayrıca raporlanır (karar şartı değil).
- Başarılı olsa bile canlıya doğrudan girmez: önce gölge izleme önerisi, kullanıcı onayı.

## Bilgi (karar değil)
- Aynı olay saatlerinde canlıdaki 🤝 sinyallerinin (coin modeliyle) sonucu ile karşılaştırma (veri_seti.csv.gz) · coin özelliklerinin 5'li dilimlere göre işlem neti tablosu (betimleme).
