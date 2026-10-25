# Önceden yazılı protokol — mesaj anında fiyat YÜKSELMİŞ ya da DÜŞMÜŞSE 🎯'yi fiyata göre ayarlamak (karal4 · 25.10.2026)
_Kullanıcı (25.10): "Bence biz bunu avantaja çevirebiliriz: fiyat giriş fiyatından düşmüşse şurada gir gibi. Bulduğun diğer iki bulguyu (🎯'yi yükselmenin yarısı / tamamı kadar kaydırmak) daha çok veriyle dene, geçerse hemen ekleyelim." karal3'te yukarı kaydırma etkilenen işlemlerde her dönemde iyi çıktı ama tüm sinyal verisi görüldü → karar bu kez HİÇ KULLANILMAMIŞ veride. Bu dosya veri işlenmeden yazıldı; sonradan değiştirilmez._

## Tanımlar
- G = mesajdaki fiyat (sinyal saatinin kapanışı) · 🎯 = G·(1 + k·s) · O = mesaj anı açılış fiyatı · y = O/G − 1.
- Giriş: mesaj anında piyasa alış (y < 0 iken kullanıcının limiti de zaten bu fiyattan hemen dolar).
- Kurallar (🎯 yeni = 🎯 · (1 + f·y)):
  - **YUKARI** (y > +%0,25): U0 = 🎯 sabit (taban) · **U½** f = ½ · **U1** f = 1
  - **AŞAĞI** (y < −%0,25): A0 = 🎯 sabit (taban) · **A½** f = ½ (🎯 düşen fiyatın yarısı kadar iner) · **A1** f = 1
- Çıkış: 🎯'ye değerse 🎯'den (limit ücreti), değmezse süre sonu (piyasa ücreti) · vadeli ücret + fonlama yaklaşığı.
- %0,5 eşiği yalnız bilgi olarak raporlanır.

## Veri kümeleri
1. **Sinyal verisi** (veri_seti.csv.gz, 1 dk mum; ✅ ana · 🔸 yedek · 📋 panelden ayrı) — YUKARI kurallar için GÖRÜLDÜ (karal3) → yalnız bilgi; AŞAĞI kurallar için keşif + kontrol.
2. **Yeni veri — coinsec olayları** (BTC güçlü ↑ saatleri × 219 coin, 5 dk mum, 4 saat, 🎯 +0,75σ; giriş t+5 dk açılışı). Bu soru için hiç kullanılmadı. Üç küme: **A 2025+ · B (dokunulmamış) 2022-06→2024 · B 2025+**.

## Ölçü (yalnız etkilenen işlemler: y eşiği aşanlar)
- işlem isabeti · işlem başı net.
- Bir kural tabanına göre "iyi": (net ≥ taban + %0,03 VE isabet ≥ taban − 1 puan) YA DA (isabet ≥ taban + 3 puan VE net ≥ taban).

## Karar
- **YUKARI:** U½ ve U1, yeni verinin ÜÇ kümesinde de "iyi" olmalı. İkisi de geçerse üç kümenin ortalama netine göre büyük olan seçilir.
- **AŞAĞI:** Keşif = sinyal verisi 2022-06 → 2024 iki yarı, ✅ ana + 📋 panelden + 🔸 yedek her biri ayrı; iki yarıda da "iyi" olan, keşif neti en yüksek tek kural (A½ / A1) → kontrol: sinyal verisi 2025+ ve 2026 (aynı sınıf) + yeni verinin üç kümesi — hepsinde "iyi" olmalı.
- Geçen kural (kullanıcı ön onayıyla) mesaja YÜZDE değil somut fiyat satırı olarak eklenir: "Fiyat $A ise 🎯 $B · $C ise 🎯 $D …". Geçmeyen yön eklenmez.
