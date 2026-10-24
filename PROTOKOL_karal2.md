# Önceden yazılı protokol — kâr-al formülü geliştirme: "isabeti düşürmeden kârı artır" (24.10.2026)
_Veri toplanmadan ve hiçbir sonuç görülmeden yazıldı. Değişiklik gerekirse ayrı, tarihli ek._

## Kapsam ve ölçüm
- Sinyaller: veri_seti.csv.gz'deki gönderilen sinyaller (✅ ana · 🔸 yedek · 📋 panelden), giriş/sınıf/süre aynen.
- Fiyat yolu: Binance 1 dakikalık mum, sinyal saatinden t+2H'ye kadar (tam yol; saatlik yaklaşık yok).
- Giriş: **B = mesajdaki fiyata limit** (kullanıcının kullandığı; 60 dk, fiyat zaten altındaysa hemen) ana; D = t+7 dk piyasa ikinci.
- Ücret: vadeli (limit %0,02 · piyasa/stop %0,05) + **fonlama yaklaşığı**: tutulan süre içinde geçilen her 00/08/16 UTC için −%0,01.
- İsabet: net > 0, hem işlem hem saat sepeti bazında raporlanır.

## Formüller (bu liste dışında aday eklenmez)
- **T0 (şimdiki):** 🎯 = G·(1 + k·σ720·√H), değerse limitten çık, değmezse süre sonu.
- **T1 takip eden kâr-al:** 🎯'ye değince satılmaz; durdurma seviyesi = max(taban, o ana kadarki en yüksek × (1 − τ·σ1)), σ1 = saatlik σ720, taban = giriş × 1,002. Fiyat durdurmaya inerse çık (stop ücreti), süre sonunda hâlâ açıksa kapanıştan çık. τ ∈ {0,25 · 0,5 · 1,0}.
- **T2 farklı oynaklık:** 🎯 = G·(1 + k·σ_x·√H), σ_x ∈ {σ168, σ24, ATR14 (son 14 saatin ortalama (yüksek−düşük)/kapanış)}; k ∈ {0,3 · 0,45 · 0,6 · 0,75 · 0,9 · 1,1}. Karşılaştırma **eşit isabette**: her sınıf için T0'ın keşif işlem isabetine en yakın k seçilir, net karşılaştırılır.
- **T3 zarardakini uzat (yalnız bilgi, önerilmez):** süre sonunda 🎯'ye değmemiş ve zarardaysa H kadar daha tut; 🎯'ye ya da giriş × 1,0007'ye değerse limitten çık, değmezse 2H sonunda kapanıştan.
- **T1+T3** birleşimi yalnız bilgi.

## Dönemler ve karar
- KEŞİF 2022-06 → 2024-12: τ ve σ_x/k seçimi yalnız burada.
- KONTROL 2025-01 → bugün: **ikinci kullanım** (PROTOKOL_saat70 doğrulamasında taban görüldü) → tam temiz değil; sonuç "destekleyici kanıt" diye raporlanır, kesin kanıt canlı ileri testtir.
- Keşifte seçim şartı (sınıf başına): işlem isabeti ≥ T0 − 0,5 puan VE saat isabeti ≥ T0 − 0,5 puan VE işlem başı net ≥ T0 + 0,03 puan, keşifin iki yarısında ayrı ayrı. Şartı geçen en yüksek netli tek varyant (sınıf başına) kontrole gider.
- Kontrolde başarı: aynı üç şart 2025+ ve 2026'da ayrı ayrı.
- T1'de stop doluşu yaklaşık (1 dk mum içinde stop seviyesinden dolduğu varsayılır, kayma yok) — gerçekte biraz daha kötü olabilir; bu not sonuçla birlikte yazılır.
- Kullanıcı onayı olmadan canlıya hiçbir şey alınmaz.
