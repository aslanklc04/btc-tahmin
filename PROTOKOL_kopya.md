# Önceden yazılı protokol — BİNANCE COPY TRADING: EN İYİ GÖRÜNEN LİDERLERİ TAKİP ETMEK KAZANDIRIR MI? (kopya · 04.11.2026)
_Kullanıcı (04.11): "Binance'in quant modelinin işlemlerini takip eden sistem yap" → "Neon'dan çek". Binance kendi masasını yayınlamaz; herkese açık olan Copy Trading liderleri.
Veri Neon (Frankfurt) /kopya ucuyla çekilir. Hesaptan önce yazıldı; sonradan değiştirilmez. Canlıya / gerçek paraya yalnız onayla._

## Veri
- Liste ucu (timeRange 365D, ROI sıralı, sayfa 30): tüm herkese açık lider portföyleri (04.11'de 9.130) · her biri için 365 günlük günlük ROI serisi (chartItems), aum, mdd, winRate, sharpRatio, startTime, currentCopyCount.
- Günlük getiri: r_d = (1 + ROI_d/100) / (1 + ROI_{d−1}/100) − 1 (ROI birikimli % kabul edilir). Başlamadan önceki günler (ROI = 0 ve startTime öncesi) yok sayılır.

## Yürüyen test (geleceği görmeden)
- Oluşum tarihleri F: pencerenin 120. gününden itibaren her 30 günde bir (≈ 8 tarih). Her F'de yalnız F'den önce ≥ 60 gün geçmişi olan portföyler.
- Sıralama (F'den önceki 90 gün): S1 ROI (Binance listesinin varsayılanı) · S2 günlük getirinin ort./sd'si (Sharpe benzeri).
- Gruplar: "vitrin" ilk 10 · en iyi %10 · hepsi (karşılaştırma).
- İleri getiri: F → F+30 gün birikimli. Kopyalayan için kâr payı: pozitif getirinin %10'u düşülür (kayma/gecikme eklenmez — iyimser).
## "Takip kazandırır" şartı (hepsi)
- Oluşum tarihlerinin ≥ %70'inde en iyi %10'un (S1 ve S2 ayrı ayrı) medyan ileri getirisi > 0 VE > tüm portföylerin medyanı.
- Tüm tarihler birlikte en iyi %10'un ortalama ileri getirisi (kâr payı sonrası) > 0 ve ileri getirisi ≤ −%50 olanların oranı ≤ %10.
- Bilgi: vitrin ilk 10'un aynı ölçüleri · F'deki sıralama ile ileri getiri arasındaki Spearman ilişkisi · tüm portföylerde ileri getiri dağılımı.
## Bilinen yanlılık
Liste yalnız bugün listelenen portföyleri içerir; kapanıp silinenler yok → ileri getiriler OLDUĞUNDAN İYİ görünür. Şart bu yanlılıkla bile tutmazsa sonuç güçlü bir "hayır"dır;
tutarsa canlı ileriye dönük izleme (her gün ilk 50'nin kaydı, 30 gün sonra ölçüm; silinenler dahil) ayrıca kurulur ve karar ona göre verilir.
