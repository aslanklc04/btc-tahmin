# Önceden yazılı protokol — ✅ ana sınıf ayarı: (1) coin primi z ≥ 3 · (2) uzun süreli ana türler (ana_ayar · 29.10.2026)
_Canlı (12–26.10, karne_gercek.csv): 🌐🤝/🤝 4 s içinde coin primi z ≥ 3 olanlar 6 işlem %33 · −%0,73; ✅ ana 8–24 s türler 20 işlem %50 · −%0,65 (4 s ana 45 işlem %58 · +%0,30). Canlı örnek çok küçük → karar 4,5 yıllık GERÇEKÇİ geçmişte verilir. Kullanıcı (29.10): "Testleri yap". Bu dosya hesaptan önce yazıldı._

## Veri
- veri_seti.csv.gz (tür, coin primi z, süre, sınıf) + karal2_veri.csv.gz gerçekçi sonuç: **D_T0** (7. dk piyasadan giriş — kullanıcının pratiği; karar ölçüsü) ve B_T0 (limit; bilgi). 🎯 sınıfın kuralı, vadeli ücret + fonlama.
- Dönemler (ayrık): 2022-06 → 2024 · 2025 · 2026.

## Test 1 — coin primi z ≥ 3
- Küme: ✅ ana, 4 s, tür 🌐🤝 ya da 🤝. **A** = z ≥ 3 · **B** = 0 ≤ z < 3.
- **Karar:** ÜÇ dönemde de (A ≥ 30 işlem) A'nın işlem isabeti ≤ B − 3 puan VE A'nın işlem başı neti < B'nin → z ≥ 3 olanlar ✅ anadan 🔸 yedeğe iner (🎯 değişmez, yalnız sınıf/etiket). Değilse değişiklik yok.

## Test 2 — uzun süreli ana türler
- **L** = ✅ ana, tür 🌐🧪 / 💵 / 🧪 (8 s ve üstü) · **S** = ✅ ana, 4 s (🤝 · 🌐🤝 · 🔀 · 🚀).
- **Karar:** ÜÇ dönemde de (L ≥ 30 işlem) L'nin işlem isabeti ≤ S − 3 puan VE L'nin neti < S'nin → L türleri 🔸 yedeğe iner. Tür tür sonuçlar bilgi olarak raporlanır (≥ 30 işlemli türde aynı şart sağlanırsa yalnız o tür iner).
- Bilgi: saat isabeti, B_T0.
