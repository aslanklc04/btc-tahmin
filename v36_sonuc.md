# 🧠 Model geliştirme (v36): yeni girdili coin modeli vs mevcut — 12.10.2026 06:02
Coin: 15 (ADA, APT, ARB, BNB, BTC, DOGE, DOT, ETH, FLOKI, LINK, NEAR, OP, PEPE, SHIB, SUI) · yeni girdi: x_tb1, x_tb4, x_tb24, x_tb24z, x_ats24z, x_ats1, x_n24z, x_pz, x_pz_d4, x_pz_d24, x_pbp, x_bpz, x_btc_r1, x_btc_r4, x_btc_r24, x_rel24, x_rel72, x_btc_ats24z

_her satır: haftada sinyal · isabet · işlem başı net % (komisyon sonrası) — b = mevcut model, n = yeni girdili model · ▲ = yeni daha iyi (isabet ve net)_
```
                                                     2022-06→2023          |             2024+              |              2026             
Ham model sinyali (⭐ / 4s / A, 4 saat)
  b mevcut                                  135.6/hf · %57.7 · +0.166   | 208.2/hf · %54.1 · +0.059   | 209.5/hf · %52.1 · +0.058  
  n yeni                                    136.5/hf · %58.0 · +0.174 ▲ | 216.0/hf · %54.7 · +0.099 ▲ | 231.2/hf · %52.6 · +0.104 ▲
🤝 BTC ile birlikte (tümü)
  b mevcut                                   30.3/hf · %57.3 · +0.118   |  38.4/hf · %60.3 · +0.199   |  34.4/hf · %62.5 · +0.378  
  n yeni                                     30.9/hf · %57.5 · +0.119 ▲ |  39.8/hf · %59.9 · +0.193   |  36.5/hf · %60.6 · +0.307  
🤝 ✅ ana (kendi primi ≥ 0)
  b mevcut                                   13.5/hf · %56.2 · +0.067   |  15.2/hf · %62.9 · +0.336   |  16.9/hf · %68.7 · +0.538  
  n yeni                                     16.0/hf · %57.3 · +0.108 ▲ |  19.7/hf · %60.5 · +0.251   |  22.6/hf · %62.8 · +0.340  
🔇🔀 ✅ ana
  b mevcut                                    0.8/hf · %70.1 · +0.524   |   0.9/hf · %66.4 · +0.793   |   0.7/hf · %81.5 · +0.959  
  n yeni                                      0.9/hf · %62.8 · +0.242   |   1.1/hf · %66.9 · +0.619   |   1.0/hf · %66.7 · +0.580  
COİN ✅ ANA TOPLAM (🤝 ana + 🔀)
  b mevcut                                   14.3/hf · %56.9 · +0.093   |  16.1/hf · %63.1 · +0.362   |  17.6/hf · %69.2 · +0.554  
  n yeni                                     16.9/hf · %57.6 · +0.116 ▲ |  20.8/hf · %60.9 · +0.270   |  23.5/hf · %63.0 · +0.350  
🔇 BTC sessiz (tümü, yedek)
  b mevcut                                   10.6/hf · %59.1 · +0.242   |  10.8/hf · %60.0 · +0.246   |   9.0/hf · %54.0 · -0.053  
  n yeni                                     10.3/hf · %61.7 · +0.231   |  10.7/hf · %56.9 · +0.233   |  10.1/hf · %51.2 · -0.022  
🪙 coin tek başına (tümü, yedek)
  b mevcut                                   36.6/hf · %59.1 · +0.152   |  35.8/hf · %56.7 · +0.094   |  33.3/hf · %54.6 · +0.037  
  n yeni                                     36.8/hf · %59.4 · +0.173 ▲ |  35.7/hf · %56.6 · +0.109   |  33.7/hf · %53.6 · +0.013  
🧪 24 saat ham (15 coin)
  b mevcut                                   12.9/hf · %55.9 · +0.540   |  18.4/hf · %54.7 · +0.529   |  17.9/hf · %50.9 · +0.225  
  n yeni                                     13.1/hf · %54.5 · +0.475   |  18.6/hf · %55.2 · +0.569 ▲ |  19.6/hf · %49.6 · +0.109  
🧪 ✅ ana (canlı 10 coin, prim ≥ 0)
  b mevcut                                    5.5/hf · %55.2 · +0.736   |   5.3/hf · %60.0 · +1.117   |   5.2/hf · %52.1 · +0.284  
  n yeni                                      7.4/hf · %51.7 · +0.440   |   7.1/hf · %57.2 · +0.771   |   7.1/hf · %50.5 · +0.275  
```
## AUC (yön tahmini, 0,5 = yazı-tura) — 2024+ · coin başına mevcut → yeni
```
 1 s: yeni daha iyi 15/15 coin · ortalama 22-06→23 0.5609→0.5652 · 2024+ 0.5376→0.5463 · 2026 0.5315→0.5500
      ADA 0.535→0.539 · APT 0.527→0.534 · ARB 0.528→0.543 · BNB 0.534→0.538 · BTC 0.550→0.551 · DOGE 0.541→0.542 · DOT 0.535→0.544 · ETH 0.552→0.554 · FLOKI 0.534→0.563 · LINK 0.536→0.541 · NEAR 0.527→0.533 · OP 0.533→0.552 · PEPE 0.553→0.562 · SHIB 0.552→0.568 · SUI 0.529→0.531
 4 s: yeni daha iyi 14/15 coin · ortalama 22-06→23 0.5445→0.5468 · 2024+ 0.5310→0.5359 · 2026 0.5208→0.5293
      ADA 0.530→0.535 · APT 0.518→0.527 · ARB 0.525→0.528 · BNB 0.532→0.531 · BTC 0.555→0.555 · DOGE 0.529→0.533 · DOT 0.528→0.537 · ETH 0.542→0.544 · FLOKI 0.542→0.544 · LINK 0.518→0.525 · NEAR 0.528→0.530 · OP 0.522→0.538 · PEPE 0.531→0.535 · SHIB 0.542→0.549 · SUI 0.523→0.528
 8 s: yeni daha iyi 10/15 coin · ortalama 22-06→23 0.5488→0.5550 · 2024+ 0.5292→0.5315 · 2026 0.5164→0.5179
      ADA 0.537→0.542 · APT 0.520→0.529 · ARB 0.524→0.525 · BNB 0.529→0.522 · BTC 0.528→0.530 · DOGE 0.540→0.538 · DOT 0.531→0.544 · ETH 0.534→0.528 · FLOKI 0.542→0.541 · LINK 0.510→0.521 · NEAR 0.515→0.522 · OP 0.525→0.531 · PEPE 0.514→0.518 · SHIB 0.546→0.548 · SUI 0.545→0.533
24 s: yeni daha iyi 11/15 coin · ortalama 22-06→23 0.5422→0.5309 · 2024+ 0.5195→0.5279 · 2026 0.5102→0.5183
      ADA 0.511→0.543 · APT 0.481→0.481 · ARB 0.498→0.497 · BNB 0.517→0.529 · BTC 0.538→0.559 · DOGE 0.553→0.557 · DOT 0.534→0.543 · ETH 0.534→0.551 · FLOKI 0.537→0.528 · LINK 0.513→0.544 · NEAR 0.499→0.507 · OP 0.496→0.505 · PEPE 0.527→0.515 · SHIB 0.548→0.557 · SUI 0.508→0.504
```

## Önceden yazılı karar
- **Coin modeli (1/4/8 s):** ❌ geçmedi — mevcut model kalır
- **24 saat modeli (🧪):** ❌ geçmedi — mevcut model kalır
