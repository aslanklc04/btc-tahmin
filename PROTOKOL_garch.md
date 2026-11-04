# Önceden yazılı protokol — GARCH OYNAKLIK TAHMİNİ ile sinyal ayrımı (garch · 04.11.2026)
_Kullanıcı (04.11): "Araştırmaya olasılık biliminden bir şeyler bul." GARCH(1,1): oynaklık kümelenmesi. Hesaptan önce yazıldı; sonradan değiştirilmez. Canlıya yalnız kullanıcı onayıyla._

## Veri · model
- Sinyaller: veri_seti ⋈ karal2 (D_T0, B_T0), ✅ ana · 🔸 yedek · 📋 panelden, 2022-06 → 2026-10-21.
- Coin saatlik getirisi (teknik3_mum). Her coin için GARCH(1,1) (ortalama sabit, normal dağılım) her ay başında YALNIZ önceki 3000 saatle kurulur; o ay boyunca aynı parametrelerle koşullu varyans süzülür (geleceğe bakmadan).
- Sinyal anında: ufuk H için beklenen saatlik oynaklık σ_G = √(ort_{k=1..H} E[σ²_{t+k}]) · oran **ρ = σ_G / σ720** (σ720 = 🎯'de kullanılan son 720 saat std).
## Koşullar (önceden sabit)
- **G1 oynaklık artacak:** ρ ≥ 1,2 · **G2 oynaklık azalacak:** ρ ≤ 0,8.
## Karar (sınıf başına; ayrim protokolüyle aynı şartlar)
- **"İyi":** ÜÇ dönemde (2022-06→24 · 2025 · 2026) de koşullu grubun isabeti, aynı sınıfta koşulsuz kalanlardan ≥ +5 puan VE net ≥ +%0,10; her dönem ≥ 30; B_T0 ile de üç dönemde fark > 0. **"Kötü":** tersi (≤ −5, ≤ −%0,10).
- **Plasebo:** ρ değerleri sınıf × dönem içinde karıştırılır ×50 → tesadüfen geçen hücre sayısı.
- Geçen hücre olursa ayrim Ek 1'deki T1–T5 sağlamlık testleri (coin yarıları, limit, aylık istikrar, ilk 5 coin hariç, eşik ±0,1) uygulanır; hepsi geçerse kullanıcıya önerilir.
