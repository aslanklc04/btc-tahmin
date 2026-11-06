# Önceden yazılı protokol — +%50 YÜKSELİŞLERDEN ÖNCE NE OLUYOR? ORTAK DURUMLAR · YÖN AYRIMI · BÜYÜTENLER (pompaonce · 06.11.2026)
_Kullanıcı (06.11): "Bir günde yükselmiş tüm coinlerin yükselişten önce ne yaşadığını, neyin etkisini artırdığını araştır; ortak durumlar var mı?" Veri: pompa50 ile aynı
(682 coin vadelisi, günlük, kapatılanlar dahil, hisse/emtia/döviz hariç). Hesaptan önce yazıldı._

## Olaylar (gün t+1; özellikler t kapanışında ve öncesinde)
- **Y (yükseliş):** t+1 en yüksek ≥ t+1 açılış × 1,5 · **Y+ (tutunan):** ayrıca t+1 kapanış ≥ açılış × 1,3.
- **D (çöküş, karşıt):** t+1 en düşük ≤ t+1 açılış × 0,7 (ve Y değil).
- **K (kontrol):** diğer tüm coin-günler.
## 1. Ortak durumlar (tanımlayıcı)
Özellikler: fonlama t ve 3 g · getiri t, t−1, t−2 (gün gün) ve 7 g · art arda yeşil gün · hacim oranı t ve t−1 · yaş · 30 g dibe/zirveye uzaklık · 30 g oynaklık ·
BTC 1 g ve 7 g · aynı gün kaç coin'in Y olduğu (piyasa çılgınlığı; bilgi, t+1'de bilinir) · haftanın günü.
Her özellik için Y / D / K medyanları ve "Y'de %X, K'de %Y" oranları; dönem ayrı: 2021–23 · 2024 · 2025 · 2026.
## 2. Yön ayrımı (asıl soru) — Y'yi D'den ayıran var mı?
- Her özelliğin keşif (2021–23) beşte birlik dilimlerinde yukarı payı = Y / (Y + D).
- **"Yön işareti bulundu":** bir dilim keşifte n ≥ 30 ve yukarı payı ≥ %60 VE 2024, 2025, 2026'nın HER BİRİNDE n ≥ 30 ve yukarı payı ≥ %60 VE o yılın genel yukarı payından ≥ 10 puan yüksek.
- Bulunan olursa işlem testi ayrıca yazılır (bu protokol işlem kuralı koymaz).
## 3. Büyütenler — Y içinde yükselişin boyu (en yüksek / açılış) ile özelliklerin Spearman ilişkisi, dönem ayrı (bilgi).
## 4. Sonrası — Y gününün kapanışından sonraki 1 / 3 / 7 gün getirisi (medyan, pozitif oranı), dönem ayrı (bilgi).

## Ek 1 (06.11.2026, kullanıcı: "%30'dan fazla yükselenleri, normal en fazla %10 yükselenlerden ayıran ne?") — hesaptan önce
- Günlük değişim r = C[t+1] / C[t] − 1 (Binance kazananlar listesi gibi). **B30:** r ≥ +%30 · **N10:** 0 < r ≤ +%10 (normal yükselen) · karşılaştırma için **Ç30:** r ≤ −%30.
- Her özellik (t kapanışında bilinen, bölüm 1'dekiler; "aynı gün Y sayısı" hariç) için dönem dönem: B30 / N10 medyanları ve ayırma gücü AUC (rastgele bir B30'un özelliği rastgele bir N10'dan büyük olma olasılığı).
- **"Ayırt edici":** dört dönemin HER BİRİNDE |AUC − 0,5| ≥ 0,10 ve aynı yönde. Aynı ölçü B30 ↔ Ç30 için de verilir (yön ayrımı); orada da ayırt edici çıkarsa "yön işareti" sayılır.
- Bilgi: tüm özelliklerle HistGradientBoosting yıllık yürüyen test AUC (B30 ↔ N10 ve B30 ↔ Ç30).
