# Önceden yazılı protokol — SİNYAL AYRIMI: TÜR × KOŞUL × COIN (ayrim · 01.11.2026)
_Kullanıcı (01.11): "Ürettiğimiz sinyalleri tür ve koşullara göre ayıralım; ör. SHIB dip 🔥 işaretlilerde çok iyi, 24 saatte kötü. Kötü performanslıları eklemeyelim. Araştırma yap, testleri kendin yap; modele bir şey ekleme, onay verirsem eklersin." Bu dosya hesaptan önce yazıldı; sonradan değiştirilmez (gerekirse tarihli "Ek"). Canlıya yalnız kullanıcı onayıyla._

## Veri · ölçü
- Üretilen tüm sinyaller: veri_seti.csv.gz (✅ ana · 🔸 yedek · 📋 panelden; (t, nm, sinif, H) tekrarsız) ⋈ karal2_veri.csv.gz.
- **Ana ölçü D_T0** (7. dakikada piyasadan giriş, sınıf 🎯'si, vadeli ücret + fonlama) · isabet = D_T0 > 0. Destek: B_T0 (limit giriş).
- Dönemler: **A** 2022-06 → 2024 · **B** 2025 · **C** 2026 (→ veri sonu 21.10).

## Gruplar (sinyal grubu = sınıf × tür)
veri_setindeki `sinif` × `tur` (ör. ✅ ana 🌐🧪, 🔸 yedek G = 🌐🤝 geniş liste, 📋 panelden 💵 …). Her grup için taban = grubun tamamı (dönem dönem).

## Koşullar (eşikler önceden sabit; sinyal anında bilinen)
K1 📉🔥 dip: rz ≤ −2 · K2 🚀 momentum: rz ≥ 2 · K3 🔥 fonlama: fon ≥ 2 · K4 coin primi güçlü: z ≥ 1 · K5 coin primi negatif: z < 0 · K6 ABD BTC satıyor: zB < 0 · K7 BTC 24 s ≤ −%2 · K8 BTC 24 s ≥ +%2 · K9 BTC oynaklığı yüksek: b_vr ≥ 1,25 · K10 coin 4 s düşüşte: c_r4 < 0 · K11 coin 24 s ≤ −%5 · K12 ABD seansı: saat 12–16 UTC · K13 Asya gecesi: saat 0–5 UTC · K14 hafta sonu (Cmt/Paz) · K15 süre 4 s · K16 süre ≥ 24 s.

## Bölüm 1 — tür × koşul hücreleri
- Hücre = grup ∩ koşul. Fark = hücre − (aynı grupta koşulun OLMADIĞI sinyaller).
- **"Kötü hücre (ele adayı)":** ÜÇ dönemde de isabet farkı ≤ −5 puan VE net farkı ≤ −%0,10 VE hücrede her dönem ≥ 30 sinyal.
- **"Mutlak kötü":** ÜÇ dönemde de hücre isabeti < %55 VE net < 0 (≥ 30).
- **"İyi hücre (öne çıkar adayı)":** ÜÇ dönemde de isabet farkı ≥ +5 VE net farkı ≥ +%0,10 (≥ 30).
- Aynı şart **B_T0 ile de** aynı yönde olmalı (her dönem fark işareti aynı) — yoksa "zayıf".
- **Plasebo:** koşul etiketleri grup × dönem içinde rastgele karıştırılır ×50 → kaç hücre tesadüfen "kötü"/"iyi" çıkıyor. Gerçek sayı plasebo ortalamasının belirgin üstünde değilse sonuç kabul edilmez.

## Bölüm 2 — grubun kendisi
- **"Grup ele adayı":** grup ÜÇ dönemde de isabet < %55 VE net < 0 (≥ 30).

## Bölüm 3 — coin düzeyi (kullanıcının SHIB örneği)
- Hücre = coin × grup (ve coin × grup × K1/K3, yalnız bilgi). Dönemlerde ≥ 30 nadir olduğundan: **seçim A'da** (≥ 20 sinyal): isabet ≤ grup − 10 puan VE net < 0 → "kötü coin"; **test B ∪ C'de** (≥ 20): yine grup tabanının altında (isabet farkı ≤ −5 VE net < 0).
- İyi coin için ters yönde aynı şart.
- **Plasebo:** coin etiketleri grup × dönem içinde karıştırılır ×50 → seçim+test'ten tesadüfen geçen coin sayısı. Gerçek sayı plasebonun belirgin üstünde değilse "coin bazında eleme işe yaramıyor" denir.

## Bölüm 4 — eleme etkisi
Geçen tüm "ele" hücreleri (ve geçen kötü coin'ler) çıkarılınca sınıf bazında (✅ / 🔸 / 📋) dönem dönem isabet, net, sinyal sayısı: önce → sonra. Bilgi: kullanıcının örneği (SHIB) için coin × grup × K1/K3 tablosu.

## Karar
Önerilecekler: Bölüm 1–3'te şartı geçen ve plaseboyu belirgin aşanlar. Hiçbiri canlıya kullanıcı onayı olmadan eklenmez.

## Ek 1 (01.11.2026, kullanıcı: "testleri yap geçerse ekle") — iki iyi hücre için sağlamlık testleri (hesaptan önce)
Adaylar: **H1** ✅ ana 🌐🧪 ∧ BTC oynaklığı yüksek (b_vr ≥ 1,25) · **H3** 📋 panelden 💵 ∧ coin 24 s ≤ −%5 (c_r24 ≤ −0,05). (H2 ✅ ana 🌐🧪 ∧ 📉🔥 zaten 💎 ELİT içinde → ek işaret gerekmez.)
- **T1 coin yarıları** (md5 tek/çift): her yarıda tüm dönemler birlikte isabet ≥ %70 VE net > 0; her dönemde ≥ %65.
- **T2 limit giriş (B_T0):** her dönemde isabet ≥ %70.
- **T3 aylık istikrar:** ≥ 5 sinyalli aylarda hücre isabeti, aynı grubun koşulsuz kalanının o ayki isabetinden ≥ olan ayların oranı ≥ %60.
- **T4 coin yoğunluğu:** en çok sinyal veren 5 coin çıkarılınca tüm dönemler isabet ≥ %70 VE net > 0, her dönemde ≥ %65.
- **T5 eşik duyarlılığı:** H1 için b_vr ≥ 1,15 ve ≥ 1,35 · H3 için c_r24 ≤ −0,04 ve ≤ −0,06 → her dönemde isabet ≥ %70 VE net > 0 (bıçak sırtı değil).
- **T6 canlı hesap eşitliği:** canlıya yazılacak işaret kodu (Binance saatlik mumdan b_vr / c_r24) 2026-09-01 → 10-21 araştırma sinyallerinde işareti ≥ %98 aynı vermeli.
- **T7 bilgi:** canlı karne (durum/karne_gercek.csv, 12.10 →) aynı ölçüm, az örnek.
- **Karar:** her aday için T1–T6'nın hepsi geçerse mesaja işaret eklenir (sinyal kararlarına, sınıflara ve gönderime dokunmaz; yalnız bilgi satırı). Biri geçmezse eklenmez, raporlanır.
