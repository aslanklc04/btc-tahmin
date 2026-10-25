# Önceden yazılı protokol — BÜYÜK KÂR-AL TARAMASI (karal5 · 25.10.2026)
_Kullanıcı (25.10): "Kâr-alı gerçekten geliştirebiliriz. Denemediğimiz binlerce yöntem var; dener test edersek hem isabeti hem kârı artırabiliriz." Risk: çok kural denenince bazıları şans eseri iyi görünür (karal3 → karal4'te görüldü). Önlem: tarama yalnız 2022–24 sinyal verisinde; seçilen ≤ 5 kural BEŞ bağımsız kümede de geçmeli. Bu dosya veri işlenmeden yazıldı; sonradan değiştirilmez._

## Ortak
- Giriş: şimdiki kural B (mesaj fiyatı G'ye 60 dk limit; 7. dk açılışı ≤ G ise hemen). Dolmayan sinyal 0 sayılır.
- s = σ720·√H (sinyalin hedef birimi) · 🎯(k) = G·(1 + k·s) · çıkış ücreti: hedef / limit çıkışlarında limit (%0,02), süre sonu / stop çıkışlarında piyasa (%0,05) · giriş ücreti B'deki gibi · fonlama %0,01 / geçilen 00-08-16 UTC.
- Hedefe değme: dolumdan SONRAKİ mumlarda en yüksek ≥ hedef (limit dolumunda dolum mumu sayılmaz). Stop: mumun en düşüğü ≤ stop → stop fiyatından. Aynı mumda hem hedef hem stop → stop (kötümser).
- **Taban:** S(k_sınıf) = bugünkü kural (ana 0,75 · yedek 0,50 · panelden 0,45).

## Kural aileleri (toplam sayı sonuçta raporlanır)
1. **S — sabit hedef:** k ∈ {0,2 0,25 0,3 0,35 0,4 0,45 0,5 0,6 0,75 0,9 1,0 1,25 1,5 2,0 · hedefsiz (yalnız süre)}
2. **P — kısmi satış:** payın q'su k1'de, kalanı k2'de ya da süre sonunda · q ∈ {⅓ ½ ⅔} · k1 ∈ {0,25 0,35 0,5 0,6} · k2 ∈ {0,75 1,0 1,25 1,5 2,0 hedefsiz} (k1 < k2)
3. **Z — zamanla inen hedef:** hedef doğrusal olarak k0'dan kend'e iner (süre boyunca) · k0 ∈ {0,75 1,0 1,25 1,5 2,0} · kend ∈ {0 0,25 0,5}
4. **BE — başa baş koruma:** fiyat G·(1+kb·s)'ye değince stop = giriş × 1,0012 · kb ∈ {0,25 0,4 0,5 0,75} · hedef k ∈ {0,75 1,0 1,25 1,5 2,0 hedefsiz} (kb < k)
5. **TR — iz süren:** fiyat G·(1+ka·s)'ye değince stop = önceki mumlara kadarki en yüksek × (1 − τ·s) · ka ∈ {0,25 0,5 0,75} · τ ∈ {0,1 0,2 0,3 0,5} · üst hedef ∈ {yok 1,5}
6. **UZ — uzatma:** hedef k ∈ {0,5 0,75 1,0}; süre sonunda zarardaysa ek süre e ∈ {½H 1H} boyunca çıkış seviyesi ∈ {başa baş (giriş × 1,0012) · k hedefi · 0,25 hedefi}; ek süre bitince piyasa
7. **ER — ara kontrol:** hedef k_sınıf; süre f ∈ {½ ¾} anında kapanış ≥ giriş·(1 + y) ise çık, y ∈ {%0,1 · 0,25·s · 0,5·s}; ayrıca "kapanış ≤ giriş·(1 − 0,5·s) ise çık" (2 kural)
8. **Birleşik:** P + BE (k1'e değince kalanına başa baş stop) · q ½ · k1 ∈ {0,25 0,35 0,5 0,6} · k2 ∈ {1,0 1,5 hedefsiz} · ve P + TR (k1'den sonra kalanı iz süren) · q ∈ {½ ⅔} · k1 ∈ {0,25 0,35 0,5} · τ ∈ {0,2 0,3 0,5}

## Ölçüler
- sinyal başı net · işlem isabeti (net > 0) · saat isabeti (saatin sınıf sepeti > 0). Kısmi satışta işlem neti = ağırlıklı ortalama.
- **İyi** (tabana göre): (sinyal başı net ≥ taban + %0,03 VE işlem isabeti ≥ taban − 1 VE saat isabeti ≥ taban − 1) YA DA (işlem isabeti ≥ taban + 3 VE saat isabeti ≥ taban + 1 VE sinyal başı net ≥ taban).

## Karar (✅ ana için; 🔸 yedek ve 📋 panelden yalnız bilgi)
1. **Tarama / keşif:** sinyal verisi 2022-06 → 2024, iki yarıda da "iyi" olan kurallar → keşif sinyal başı neti en yüksek 5 kural.
2. **Doğrulama (bir kez, 5 küme, hepsinde "iyi"):** sinyal verisi ✅ ana 2025+ · 2026 · YENİ VERİ (coinsec olayları: BTC güçlü ↑ saatleri × 219 coin, 5 dk mum, 4 saat, aynı B girişi, taban S(0,75)) A 2025+ · B 2022–24 · B 2025+ (yeni veride ölçü işlem düzeyinde: net ≥ taban + %0,03 ve isabet ≥ taban − 1, ya da isabet ≥ taban + 3 ve net ≥ taban).
3. Beşini de geçen kural(lar) arasında sinyal verisi 2025+ neti en yüksek olan → kullanıcı ön onaylı, mesaja SOMUT FİYATLARLA eklenir. Hiçbiri geçmezse 🎯 değişmez.

## Ek (26.10.2026, sonuçtan SONRA — protokol değişikliği değil, kullanıcı kararı)
- Önceden yazılı şarta göre hiçbir kural geçmedi (karal5_sonuc.md). En yakın "UZ 1.0 +1.0H be": sinyal verisi 2025+ / 2026 ✅, yeni veri B 2022–24 ✅; yeni veri A 2025+ ve B 2025+'da isabet +16 puan ama net −%0,02 / −%0,01 → ❌.
- Kullanıcıya bu açıkça söylendi; kullanıcı: "İsabet yüksek kâr aynı ise ekle" → ✅ ana için canlıya alındı (main c68e0a0). Karar şartı geçmiş SAYILMAZ; canlı gerçekçi karnede (B_UZ) eski kuralla yan yana izlenir.
