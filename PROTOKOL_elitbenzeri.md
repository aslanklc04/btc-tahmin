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
