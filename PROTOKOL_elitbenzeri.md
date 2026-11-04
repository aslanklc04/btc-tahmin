# Önceden yazılı protokol — 💎 ELİT / 🌪️ SEVİYESİNDE YENİ SİNYAL TÜRLERİ (elitbenzeri · 04.11.2026)
_Kullanıcı (04.11): "ELİT ve BTC oynak gibi başka sinyaller bul, tüm matematik bilimini kullan" (tercihen ayrı gün/saatte gelen). Hesaptan önce yazıldı; sonradan değiştirilmez. Canlıya yalnız kullanıcı onayıyla._
## Veri
veri_seti ⋈ karal2 (D_T0 ana ölçü, B_T0 destek) ⋈ garch_rho (ρ); sınıflar ✅ ana · 🔸 yedek · 📋 panelden; ✅ ana'da 🤝 ve 💵 türleri hariç (panele indi).
## Koşullar (24, önceden sabit)
C1 rz ≤ −2 · C2 rz ≥ 2 · C3 fon ≥ 2 · C4 fon ≤ −1 · C5 z ≥ 2 · C6 z ≥ 1 · C7 z < 0 · C8 zB ≥ 1 · C9 zB < 0 · C10 BTC 24 s ≤ −%2 · C11 BTC 24 s ≥ +%2 · C12 b_vr ≥ 1,25 · C13 b_vr ≤ 0,8 · C14 coin 4 s ≤ −%1 · C15 coin 24 s ≤ −%5 · C16 coin 24 s ≥ +%5 · C17 saat 12–16 UTC · C18 saat 0–5 UTC · C19 hafta sonu · C20 ρ ≥ 1,2 · C21 ρ ≤ 0,8 · C22 coin oynaklığı (s) sınıf × yıl içinde üst üçte bir · C23 süre ≥ 24 s · C24 gen24 ≥ 0,5.
Aday tür = sınıf × (tek koşul ya da iki koşulun VE'si) → 3 × (24 + 276) = 900.
## Keşif · doğrulama
- Coin yarıları (md5). **Keşif hücresi:** yarı 0 × 2022-06→24: isabet ≥ %73 VE net ≥ +%0,40 VE ≥ 40 işlem.
- **Doğrulama (5 hücre):** yarı 0 × 2025, yarı 0 × 2026, yarı 1 × 2022-06→24, yarı 1 × 2025, yarı 1 × 2026: her birinde isabet ≥ %70 VE net ≥ +%0,30 VE ≥ 20 işlem; ayrıca B_T0 ile tüm veride net > 0.
- **Plasebo:** koşul matrisinin satırları sınıf × yıl içinde karıştırılır ×20 → aynı süreçten geçen tür sayısı. Gerçek sayı plasebonun en çoğundan büyük değilse "bulunamadı".
- **Bilgi:** geçenlerin haftalık sıklığı, haftada farklı gün/saat, ELİT (ana ∧ (C1 ∨ C3 ∨ 🔀)) ve 🌪️ (ana 🌐🧪 ∧ C12) ile aynı saate düşme oranı.
- Geçen ve plaseboyu aşan türler kullanıcıya önerilir; önce ayrım Ek 1'deki sağlamlık testleri (aylık istikrar, ilk 5 coin hariç, eşik duyarlılığı) uygulanır.

## Ek 1 (04.11.2026, kullanıcı: "Bulduğun yeni türlerin tüm testlerini yap, geçerse canlıya ekle") — sağlamlık testleri ve canlı kural (hesaptan önce)
Adaylar = geçen 10 tür (hepsi ✅ ana, 🤝/💵 hariç): K1 C1+C12 · K2 C3+C14 · K3 C3+C15 · K4 C5+C12 · K5 C6+C12 · K6 C12+C14 · K7 C12+C15 · K8 C12+C20 · K9 C12+C22 · K10 C12+C23.
Testler (PROTOKOL_ayrim Ek 1 ile aynı eşikler; dönemler 2022-06→24 · 2025 · 2026):
- **T1 coin yarıları:** her yarıda tüm dönemler birlikte isabet ≥ %70 VE net > 0; her dönemde ≥ %65.
- **T2 limit giriş (B_T0):** her dönemde ≥ 20 işlem ve isabet ≥ %70.
- **T3 aylık istikrar:** ≥ 5 sinyalli aylarda aday isabeti ≥ aynı ayın geri kalan ✅ ana (🤝/💵 hariç) isabeti olan ay oranı ≥ %60.
- **T4 coin yoğunluğu:** en çok sinyal veren 5 coin çıkınca tüm dönemler isabet ≥ %70 VE net > 0; her dönemde ≥ %65.
- **T5 eşik duyarlılığı:** her koşulun eşiği tek tek iki komşu değere çekilir (diğeri sabit) → her dönemde ≥ 20 işlem, isabet ≥ %70, net > 0.
  Komşular: C1 rz −1,75/−2,25 · C3 fon 1,75/2,25 · C5 z 1,75/2,25 · C6 z 0,75/1,25 · C12 b_vr 1,15/1,35 · C14 −%0,75/−%1,25 · C15 −%4/−%6 · C20 ρ 1,1/1,3 · C22 üst %40 / üst %26,7 · C23 (kesikli H) yok.
- **T8 YENİ KISIM:** adayın zaten 💎 ELİT (C1 ∨ C3 ∨ 🔀) ya da mevcut 🌪️ (🌐🧪 ∧ C12) OLMAYAN sinyalleri: her dönemde ≥ 20 işlem, isabet ≥ %70, net > 0.
  Yeni kısmı < 20 olan aday kullanıcıya yeni sinyal getirmez → canlıya eklenecek bir şey yok (rapor edilir).
**Canlı kural "🌪️+"** = ✅ ana coin (tür 🤝/💵 değil, 🌐🧪 değil — onlarda 🌪️ zaten var) ∧ BTC b_vr ≥ 1,25 ∧ (T1–T5 ve T8'i geçen adayların koşullarından en az biri).
  Canlıda hesaplanamayan C20 (aylık GARCH uydurma) birleşime girmez (önceden karar). C5 ⊂ C6 olduğundan ikisi de geçerse C6 kullanılır. C22 canlıda: coin σ720 · √H ≥ araştırmadaki 2026 ✅ ana s'nin üst üçte bir eşiği (sabit sayı).
  Birleşim de T1–T5 (T5: b_vr 1,15/1,35) ve T8'i geçmeli. **T6 canlı hesap eşitliği** (Actions, Binance saatlik mum): canlı kodun c_r4, c_r24, s, z, H, dip hesabı 2026-09-01 → son araştırma sinyallerinde 🌪️+ işaretini ≥ %98 aynı vermeli. **T7** canlı karne (bilgi).
**Karar:** birleşim T1–T6 + T8'in hepsini geçerse mesaja 🌪️+ satırı eklenir (sinyal kararları, sınıflar, sıralama ve pay değişmez; yalnız bilgi satırı, H1 🌪️ gibi). Geçmezse eklenmez, raporlanır.
