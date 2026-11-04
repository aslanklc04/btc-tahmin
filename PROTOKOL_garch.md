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

## Ek 1 (04.11.2026, ilk sonuçtan sonra, hesaptan önce) — geçen tek hücre: ✅ ana ∧ G2 (ρ ≤ 0,8) "kötü" — sağlamlık testleri (ters yönde)
- **T1 coin yarıları:** her yarıda (tüm dönemler) isabet farkı ≤ −5 puan VE net farkı < 0.
- **T2 limit giriş:** her dönemde B_T0 isabet farkı < 0 VE B_T0 net farkı < 0.
- **T3 aylık istikrar:** ≥ 5 sinyalli aylarda hücre isabeti ≤ aynı sınıfın geri kalanı olan ay oranı ≥ %60.
- **T4 coin yoğunluğu:** en çok sinyal veren 5 coin çıkarılınca tüm dönemler isabet farkı ≤ −5 VE net farkı < 0; her dönemde isabet farkı < 0.
- **T5 eşik:** ρ ≤ 0,7 ve ρ ≤ 0,9 ile her dönemde isabet farkı ≤ −3 VE net farkı < 0.
- **Karar:** hepsi geçerse kullanıcıya önerilir: ✅ ana sinyalinde coin'in GARCH oranı ρ ≤ 0,8 ise sinyal panele iner (ya da uyarı). Onaysız canlı yok.

## Ek 2 (04.11.2026, kullanıcı: "tm dene … tüm sinyallerde de, ana'dan panele indirdiğin sinyallerde de; belki yeniden ana'ya çıkar") — GARCH'A GÖRE 🎯 (hesaptan önce)
- **TG:** 🎯 = G·(1 + k·σ720·ρ̃·√H), ρ̃ = ρ'nun [0,5 · 2,0] aralığına kırpılmışı (ρ = σ_GARCH/σ720, garch_rho.csv.gz); k sınıf katsayısı (0,75 · 0,50 · 0,45). Diğer her şey T0 ile aynı (giriş D: 7. dk piyasa · B: limit; süre sonu çıkış; vadeli ücret + fonlama). 1 dk mum yeniden oynatma: garch2_veri.py (Actions).
- **"TG daha iyi" (sınıf başına ve ana 🤝 / ana 💵 için ayrı):** ÜÇ dönemde de (2022-06→24 · 2025 · 2026) D ile isabet ≥ T0 − 1 puan VE işlem başı net ≥ T0 + %0,05; iki coin yarısında da (tüm dönemler) aynı; B ile de üç dönemde net farkı ≥ 0.
- **"Yeniden ana'ya çıkar" (ana 🤝 ve ana 💵):** TG ile ÜÇ dönemde de isabet ≥ %65 VE net > 0 (≥ 30 sinyal; 💵'de dönem başına ≥ 15) VE "TG daha iyi" şartı.
- Geçen olursa kullanıcıya önerilir; onaysız canlı yok.

## Ek 3 (04.11.2026, kullanıcı: "İsabeti düşürmeden: oynaklık fazla olacak dediğinde hedefi biraz uzağa, azalacak dediğinde biraz yakına; birçok kombinasyon dene") — KISMİ GARCH HEDEFİ (hesaptan önce)
- Hedef çarpanı m = ρ^γ↑ (ρ ≥ 1 ise) · ρ^γ↓ (ρ < 1 ise); [0,5 · 2,0] kırpılır, 0,05'e yuvarlanır. 🎯 = G·(1 + k·σ720·√H·m). γ↑ ∈ {0 · 0,25 · 0,5 · 0,75 · 1} × γ↓ ∈ {0 · 0,25 · 0,5 · 0,75 · 1 · 1,5} = **30 kombinasyon** (0/0 = bugünkü T0).
- Veri: garch3_veri.py (Actions) her sinyal için m = 0,50 … 2,00 (0,05 adım, 31 seviye) netlerini 1 dk yoldan hesaplar (D ve B).
- **Seçim (sınıf başına, YALNIZ 2022-06→24, D):** isabet ≥ T0 olan kombinasyonlar içinden işlem başı neti en yüksek olan.
- **Test:** 2025 ve 2026'da ayrı ayrı isabet ≥ T0 − 0,5 puan VE net ≥ T0 + %0,05; iki coin yarısında (tüm dönemler) aynı; B (limit) ile üç dönemde net farkı ≥ 0. Hepsi geçerse kullanıcıya önerilir (önce gölge).
- Tüm 30 kombinasyonun tablosu (3 dönem) bilgi olarak raporlanır.

## Ek 4 (04.11.2026, kullanıcı: "Riski minimize etti mi? Risk azaldıysa tüm testleri yap, geçerse ekle") — ✅ ana, kısmi GARCH (γ↑ 0,25 · γ↓ 1,5) RİSK + TAM TEST (hesaptan önce)
Karşılaştırma bugünkü T0 ile, ✅ ana, D (ana) ve B (destek).
- **R1 risk (her dönemde: 2022-06→24 · 2025 · 2026):** CVaR5 (en kötü %5'in ort.) ≥ T0'ınki (daha kötü değil) VE işlem getirisinin std'si ≤ T0 VE günlük toplam getiri dizisinin en büyük düşüşü (MDD) ≥ T0'ınki − %1 (mutlak).
- **"Risk azaldı":** R1 üç dönemde geçer VE en az iki dönemde CVaR5 ya da std T0'dan belirgin iyi (CVaR5 ≥ +%0,05 ya da std ≤ −%0,02).
- **Tam test (hepsi):** T1 her dönemde isabet ≥ T0 − 0,5 puan VE net ≥ T0 · T2 iki coin yarısında (tüm dönemler) isabet ≥ T0 − 0,5 VE net ≥ T0 VE CVaR5 ≥ T0 · T3 limit (B) üç dönemde net ≥ T0 VE CVaR5 ≥ T0 − %0,05 · T4 aylık: ≥ 20 sinyalli aylarda net ≥ T0 olan ay oranı ≥ %55 · T5 ilk 5 coin hariç (tüm dönemler) isabet ≥ T0 − 0,5 VE net ≥ T0 · T6 komşu kombinasyonlar (γ↑ 0 ve 0,5 × γ↓ 1,0 ve 1,5): her biri üç dönemde net ≥ T0 − %0,02 (bıçak sırtı değil).
- **Karar:** "risk azaldı" VE tam testin hepsi geçerse canlıya eklenir (✅ ana mesajlarında 🎯 bu kurala göre); geçmezse eklenmez.
