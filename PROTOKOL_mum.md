# Önceden yazılı protokol — BTC MUM ÖRÜNTÜLERİ (renk · gövde · gölge · seri · diziler) (mum · 04.11.2026)
_Kullanıcı (04.11): "BTC'nin mum sayılarından, renklerinden, uzunluk kısalığından, gölge uzunluğundan, aynı renkte gelen mum sayısından, sonrasından ve binlerce sıralanıştan örüntüleri ara." Hesaptan önce yazıldı; sonradan değiştirilmez. Canlıya yalnız kullanıcı onayıyla._

## Veri
teknik3_mum BTC (Binance vadeli 1 s, 2021-11 → 2026-10-30). 4 s ve 1 g mumlar 1 s'ten (UTC hizalı) üretilir.

## Mum kodu (t mumunun kapanışında bilinen)
- Renk: kapanış > açılış → Y (yeşil), değilse K (kırmızı).
- Gövde |c−o|/o, üst gölge (h−max(o,c))/o, alt gölge (min(o,c)−l)/o: her biri son 720 mumun (1 g: 365) — t hariç — 1/3 ve 2/3 dilimlerine göre kısa (1) / orta (2) / uzun (3).
## Aileler (dizi t'de biter)
- F1 renk dizisi, uzunluk 1–6 · F2 aynı renk serisi uzunluğu 1–7 ve 8+ (× renk) · F3 (renk, gövde) dizisi 1–3 · F4 (renk, gövde, üst, alt) dizisi 1–2.
## Sonuç · işlem
- Giriş t+1 açılışı, çıkış t+h kapanışı; h: 1 s → {1, 4} · 4 s → {1, 3} · 1 g → {1, 3}. r = C[t+h] / O[t+1] − 1.
- Yön keşifte ortalamanın işaretiyle belirlenir (long/short). İşlem neti = yön · r − %0,12 (vadeli %0,05 + %0,05 + kayma %0,02).
## Ayrım
- Keşif: t < 2024-07-01 · Doğrulama V1: 2024-07-01 → 2025-12-31 · V2: 2026.
- **Keşifte seçim:** n ≥ 100 (1 g: ≥ 30) · t = ort / (sd/√n) / √h (örtüşme için kaba düzeltme) · tüm testler üzerinde Benjamini–Hochberg yanlış keşif oranı q = 0,05 · yön yönünde net ort. > 0.
- **Doğrulama:** V1 ve V2'nin HER BİRİNDE n ≥ 30 (1 g: ≥ 10) ve aynı yönde net ort. > 0; V1+V2 birlikte t ≥ 2.
- **Plasebo:** getiri serisi her zaman diliminde rastgele bir kaydırmayla (uzunluğun %10–90'ı, dairesel) örüntülerden koparılır ×20 → aynı seçim + doğrulama → geçen sayısı.
- **"Bulundu":** gerçek veride doğrulamayı geçen ≥ 1 VE plasebonun en çoğundan fazla.
- Bilgi: geçenlerin isabeti (net > 0 oranı), haftada sinyal, farklı gün; her ailede test sayısı ve keşif seçimi sayısı.
