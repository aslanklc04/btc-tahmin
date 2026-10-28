# Önceden yazılı protokol — SATIŞ (SHORT) AİLELERİ: %70+ isabet, işlem başı ≥ +%2 (kesif6 · 28.10.2026)
_kesif5: 648 alış kuralının hiçbiri geçmedi. Ortak zayıflık: düşüş piyasası (2022–23) ve 2026 (BTC zamanın çoğunda 200 günlük ortalamanın altında). Bu sistemde şimdiye kadar hiç SATIŞ yönlü aile taranmadı (yalnız panelde 🔻 BTC kısa). Kullanıcı vadeli işlem yapıyor → short mümkün. Fikir kesif5 sonucundan geldi; ama short kuralları hiçbir veride hesaplanmadı. Bu dosya veri işlenmeden yazıldı; sonradan değiştirilmez._

## Veri · evren · dönemler
- kesif5 ile aynı: Binance USDT-M vadeli 1 s mum + gerçek fonlama, 2022-06-01 → 2026-10-25 · görülmüş 141 / bakılmamış (igne4_semboller.csv) · likidite ≥ 2 M$/gün · dönemler ½-1 · ½-2 · 2025+ · 2026.

## Olay aileleri (saat i kapanışı; aynı aile + coin'de 24 s bekleme)
- **S1 Pompa yorgunluğu:** z72 ≥ {+4 · +6} · 72 saatin tepesinden bu yana geçen saat ≥ {0 · 6}.
- **S2 Fonlama aşırı pozitif (long kalabalığı):** son fonlama > 0 ve son 90 ödemedeki yüzdeliği ≥ {%98 · %95} · 24 s getiri ≤ {sınırsız · 0}.
- **S3 Hacimli çöküş kırılımı:** son 24 s hacmi / önceki 30 g ort. ≥ {3 · 5} · kapanış ≤ önceki 30 günün en düşüğü × 1,02.
- **S4 Geç düşen:** BTC 24 s ≤ {−%3 · −%5} · coin 24 s − BTC 24 s ≥ {+%2 · +%4}.
- Ortak seçenek: BTC trend filtresi {yok · BTC kapanışı < 200 günlük ort.}. → 16 × 2 = **32 giriş**.

## İşlem (short)
- Giriş: i+1 açılışı × (1 − %0,1 kayma), piyasa %0,05 · Hedef: giriş × (1 − T), T ∈ {%3 · %5 · %8} (limit %0,02) · Stop: yok · S = son 72 saatin en yükseği × 1,01 (giriş üstündeyse) · H ∈ {24 · 72 · 120} saat.
- Saatlik mum: hedef ve stop aynı mumda → stop · stop dolumu = max(stop, mumun açılışı) × (1 + %0,3).
- Fonlama: gerçek ödemeler (short pozitif fonlamada ALIR, negatifte öder).
- 2x likidasyon (short): stopsuzda girişten sonra en yüksek ≥ +%45 · stopluda stop dolumu ≥ +%45.
- → 18 çıkış · toplam 32 × 18 = **576 kural**.

## Karar (kesif5 ile aynı şartlar)
1. Keşif (görülmüş, ½-1 ve ½-2) ve 2. Kontrol (görülmüş, 2025+ ve 2026): isabet ≥ %70 · işlem başı net ≥ +%2,0 · gün isabeti ≥ %60 · ≥ 20 (kontrol ≥ 15) işlem · likidasyon 0.
3. Doğrulama (bakılmamış, dört dönem): aynı şartlar, ≥ 20 işlem. İlk 5 (en kötü dönem neti) doğrulamaya. Geçen → kullanıcıya somut örnek. Hiçbiri geçmezse en yakınlar bilgi.

## Ek (28.10.2026, veri işlenmeden ÖNCE — sayım düzeltmesi)
- Aileler 4 + 4 + 2 + 4 = 14 giriş × 2 trend = **28 giriş** · 28 × 18 = **504 kural** (metindeki 16 / 576 yanlış sayım). Başka değişiklik yok.

## Ek 2 (28.10.2026, sonuçtan SONRA — S2 TANIM HATASI düzeltmesi)
- S2'de fonlama çoğu coin'de taban değerde (%0,01) sabit durur; yüzdelik "son 90 ödemenin ≤ sonuncusu" olduğundan taban fonlama da %98–100 yüzdelik sayıldı → S2 ayda binlerce sahte sinyal üretti, sonucu GEÇERSİZ.
- Düzeltilmiş S2′ (değerlendirmeden önce sabit): son fonlama ≥ %0,03 (tabanın 3 katı) VE yüzdelik ≥ {%98 · %95} · r24 ≤ {sınırsız · 0} · trend {yok · BTC < 200 g} → 8 giriş × 18 çıkış = 144 kural. Aynı karar şartları (keşif + kontrol görülmüş 141, doğrulama bakılmamış). kesif6 verisinden (aday tetiği fr > 0 ve yüzdelik ≥ %95 bu kümeyi kapsar).
