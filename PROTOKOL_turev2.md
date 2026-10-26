# Önceden yazılı protokol — "KALABALIK SATICI" birleşik filtresi (turev2 · 26.10.2026)
_PROTOKOL_turev.md'de hiçbir filtre önceden yazılı keşif şartını geçmedi (turev_sonuc.md). Ancak ✅ ana sinyallerin 2025+ / 2026 sonuçlarında (bilgi bölümü — GÖRÜLDÜ) tutarlı bir tema var: sinyal anında piyasa satıcı tarafa yığılmışsa (taker satış baskısı yüksek, fonlama düşük, long/short oranı düşük, açık pozisyon azalıyor) alış sinyalleri daha iyi. Bu tema ✅ ana verisinden türetildiği için orada kanıt sayılmaz. Bu protokol temayı HİÇ BAKILMAMIŞ sinyallerde sınar: 🔸 yedek ve 📋 panelden (turev_veri.csv.gz'de bu sınıflar için filtre sonucu hiç hesaplanmadı/görülmedi). Bu dosya o hesaptan önce yazıldı._

## Tanım (sınırlar turev keşfinden, ✅ ana 2022-06 → 2024 alt %30 — sabit)
- K1 `taker` ≤ −1,01 · K2 `fon` ≤ 0,0211 · K3 `ls_all` ≤ −0,709 · K4 `oi24` ≤ −0,0771
- **Kalabalık satıcı (KS):** K1–K4'ten EN AZ 2'si doğru (boş özellik "doğru değil" sayılır).

## Test (bir kez) — 🔸 yedek ve 📋 panelden AYRI AYRI, üç dönem: 2022-06→2024 · 2025+ · 2026
- Ölçü: karal2_veri B_T0 (gerçekçi: limit giriş, sınıf 🎯'si, vadeli ücret + fonlama). Taban = aynı sınıfın tüm sinyalleri.
- **Başarı:** her iki sınıfta, her üç dönemde: KS işlem isabeti ≥ taban + 4 puan VE işlem başı net ≥ taban + %0,10 VE ≥ 50 işlem.
- Bilgi (karar değil): ✅ ana'da KS (görülmüş veri) · haftada saat · piyasadan giriş (D_T0) · KS ∧ 💎 ELİT.

## Canlı şartı
- Başarılı olsa bile: K1–K4'ün canlı karşılığı (Binance vadeli API ABD'den kapalı) OKX / spot taker oranı vb. ile kurulup geçmişle uyumu doğrulanmadan ve kullanıcı onayı olmadan mesaja girmez; önce gölge izleme.
