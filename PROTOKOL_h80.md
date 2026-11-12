# Önceden yazılı protokol — %80+ İSABET VE KÂR: SİNYAL ALT KÜMESİ × HEDEF UZAKLIĞI BİRLİKTE TASARIM (h80 · 12.11.2026)
_Kullanıcı (12.11): "Model istediğim gibi isabetli değil. %80+ ve kârlı tahminler için tüm verileri yeniden tara, yeni teknikler türet." Önceki denemeler: meta-model (hangi sinyal tutar) ❌,
900 koşul taraması (ELİT-benzeri) → yeni sinyal yok, kısmi GARCH hedefi ❌. Denenmemiş olan: sinyal SEÇİMİNİ ve 🎯 UZAKLIĞINI birlikte, doğrudan "%80 isabet + kâr" hedefiyle tasarlamak.
Hesaptan önce yazıldı; sonradan değiştirilmez. Canlıya yalnız kullanıcı onayıyla._

## Veri · ölçüm
veri_seti.csv.gz (26.862 sinyal, 2022-06 → 2026-10; 1 dk yol): her sinyal için 🎯 = G·(1 + k·s) (s = σ720·√H) hedefine değip değmediği, k ∈ {0,2 · 0,3 · 0,45 · 0,5 · 0,6 · 0,75 · 1,0}.
- D: 7. dakikada piyasadan giriş (P). 🎯 ≤ P ise hemen çıkış (−%0,10). Değdiyse 🎯'den limit satış (ücret %0,05 + %0,02), değmediyse süre sonu kapanışında (ücret %0,05 + %0,05). Fonlama %0,01 / 8 s.
- B: mesaj fiyatına 60 dk limit (dolmayan sayılmaz). İsabet = net > 0.
- Doğrulama: hesap, sınıfın bugünkü k'sında karal2'deki D_T0 ile karşılaştırılır (ilişki ≥ 0,98 olmalı; değilse test durur).
## Aday aile (13 alt küme × 6 hedef = 78)
Alt kümeler: A1 ✅ ana (🤝/💵 hariç) · A2 💎 ELİT · A3 🌪️ · A4 ELİT ∪ 🌪️ · A5 ✅ ana 🌐🤝 · A6 ✅ ana 🌐🧪 · A7 ✅ ana 🌐 · A8 ✅ ana ∧ BTC oynak (b_vr ≥ 1,25) ·
Y1 🔸 yedek · Y2 yedek ∧ b_vr ≥ 1,25 · Y3 yedek ∧ fon ≥ 2 · P1 📋 panelden · T1 tüm sinyaller ∧ b_vr ≥ 1,25. Hedef k ∈ {0,2 · 0,3 · 0,45 · 0,5 · 0,6 · 0,75}.
## Seçim → doğrulama
- **Keşif hücresi:** coin yarısı 0 (md5) × 2022-06→2024, D. Alt küme başına: n ≥ 40 ve isabet ≥ %80 ve net ≥ +%0,15 sağlayan k'lar içinden neti en yüksek olan (yoksa alt küme elenir).
- **Doğrulama (D):** diğer 5 hücrenin (yarı × dönem) her birinde n ≥ 20, isabet ≥ %75, net > 0 · VE 2025 ve 2026'nın her birinde (iki yarı birlikte) isabet ≥ %80 ve net ≥ +%0,15.
- **Limit (B):** 2025 ve 2026'nın her birinde isabet ≥ %78 ve net > 0.
- **Plasebo:** aynı aile, alt küme etiketleri sınıf × dönem içinde karıştırılmış ×50 → doğrulamayı geçen sayısı; gerçek sayı plasebonun en çoğundan fazla olmalı.
- **"Bulundu":** en az bir aday hepsini geçer.
## Dürüstlük — her geçen aday için ZORUNLU risk tablosu
İsabet hedefi yakınlaştırarak yükseltilirse kazançlar küçülür, kayıplar aynı kalır. Bu yüzden: ortalama kazanç / ortalama kayıp, kaç kazanç bir kaybı siler, en kötü işlem, en kötü %5'in ortalaması,
bugünkü hedefle (sınıf k'sı) aynı sinyallerin net'i (kâr feda edildi mi), haftada sinyal. Aynı alt kümenin tüm k tablosu bilgi olarak verilir.

## Ek 1 (12.11.2026) — LİMİT GİRİŞ (B) ÖNCELİKLİ sürüm (hesaptan önce; dürüstlük notuyla)
Ana test ❌ (D ölçümünde %80 + kâr yok: 7. dakikada piyasadan girince yakın hedefin çoğu zaten geçilmiş oluyor). Ama ana testin tablosunda 2025 ve 2026 **limit girişli (B)** sütunları
görüldü: yakın hedefte isabet %80–95 ve net artı. **Bu fikir o sütunlar görüldükten sonra doğdu** → 2025/26 B sonuçları artık "hiç bakılmamış" değil; bu ek bir ön doğrulamadır,
asıl kanıt canlı gölgeden gelir. Mesajlardaki talimat zaten limit giriş olduğu için B gerçek kullanımı temsil eder.
- Aynı 13 alt küme × 6 hedef. Roller değişir: **keşif** yarı 0 × 2022-06→24, **B**: n ≥ 40, isabet ≥ %80, net ≥ +%0,15 sağlayan k'lar içinden neti en yüksek.
- **Doğrulama (B):** diğer 5 hücrenin her birinde n ≥ 20, isabet ≥ %75, net > 0 · 2025 ve 2026'nın her birinde isabet ≥ %80 ve net ≥ +%0,15.
- Plasebo aynı (etiket karıştırma ×50). D sonuçları bilgi olarak verilir (şart değil).
- Zorunlu risk tablosu + limit dolma oranı + "aynı sinyaller bugünkü hedefle" karşılaştırması (kârdan ne feda ediliyor).
- Geçen olursa: canlıya yalnız GÖLGE satırı (gerçekçi karnede aynı sinyallerin yakın hedefle sonucu); mesajlardaki 🎯 değişmez — değişiklik ancak gölge sonucu + kullanıcı onayıyla.
