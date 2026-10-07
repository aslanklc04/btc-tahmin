# 🧑🤖 İnsan/bot baskısı → mevcut modele ek bilgi? — 07.10.2026 12:16
İşlem verisi: 730/730 gün · 17,520 saat · 1124 sn
1s yürüyen test bitti · 1258 sn
4s yürüyen test bitti · 1308 sn
1s ikinci aşama + 20 karıştırma bitti · 1362 sn
4s ikinci aşama + 20 karıştırma bitti · 1395 sn

## Mevcut model (S) ile model + insan/bot özellikleri — dışarıda kalan aylar
(Δ = AUC artışı · 'şans %95' = özellikler rastgele karıştırıldığında 20 denemenin %95'lik artışı: gerçek artış bunu geçmeli)
```
                   AUC model (1. yarı)  Δ (1. yarı)  şans %95 (1. yarı)  AUC model (2. yarı)  Δ (2. yarı)  şans %95 (2. yarı)  EK BİLGİ VAR
ufuk aile                                                                                                                                  
1s   insan−bot                  0.5393       0.0001              0.0002               0.5373      -0.0006              0.0012         False
     bot baskısı                0.5393       0.0007             -0.0000               0.5373      -0.0017              0.0016         False
     toplam baskı               0.5393      -0.0007              0.0008               0.5373       0.0000              0.0015         False
     hepsi                      0.5393      -0.0011             -0.0011               0.5373      -0.0017              0.0003         False
4s   insan−bot                  0.5417      -0.0014             -0.0014               0.5489      -0.0075              0.0025         False
     bot baskısı                0.5417      -0.0008              0.0014               0.5489      -0.0073             -0.0004         False
     toplam baskı               0.5417       0.0000             -0.0004               0.5489      -0.0014              0.0005         False
     hepsi                      0.5417      -0.0048              0.0002               0.5489      -0.0069             -0.0013         False
```

Kural: ΔAUC her iki yarıda da hem ≥ +0,002 hem de şans sınırının üstünde. Sonuç: hiçbiri geçmedi · süre 1395 sn
