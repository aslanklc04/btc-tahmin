# 🔍 Canlı = test denetimi — 18.10.2026 11:07

## 1) Sızıntı testi (veri t anında kesilince sonuç aynı mı?)
- BTC: en büyük fark — özellikler 0.0e+00 · saat içi 0.0e+00 · yol 0.0e+00 · sinyal/eşik 0.0e+00 · z 0.0e+00 → ✅ sızıntı yok
- ETH: en büyük fark — özellikler 0.0e+00 · saat içi 0.0e+00 · yol 0.0e+00 · sinyal/eşik 0.0e+00 · z 0.0e+00 → ✅ sızıntı yok
- OP: en büyük fark — özellikler 0.0e+00 · saat içi 0.0e+00 · yol 0.0e+00 · sinyal/eşik 0.0e+00 · z 0.0e+00 → ✅ sızıntı yok
- LDO: en büyük fark — özellikler 0.0e+00 · saat içi 0.0e+00 · yol 0.0e+00 · sinyal/eşik 0.0e+00 · z 0.0e+00 → ✅ sızıntı yok

## 3) Gönderilen sinyallerde coin primi z: mesajdaki ↔ araştırma yöntemi (aynı saat, taze veri)
- 111 coin-sinyal · |fark| ortalama 0.11 · |fark| > 0,5 olan 5 · eşik tarafı değişen (mesaj ≥ 0 ama araştırma < 0 ya da tersi): 6 · ≥ 2 tarafı değişen: 1
```
       t      nm  z_mesaj       s                            tur  z_arastirma  z_canli_yeniden  fark
13.10 00    BLUR      1.6   ✅ ana                      🧪 24 saat         1.56             1.59  0.04
13.10 00    NEAR      2.2   ✅ ana             💵 ABD güçlü alıyor         2.19             2.19  0.01
13.10 04     VET      4.5   ✅ ana                      🧪 24 saat         4.45             4.45  0.05
13.10 04     ZEN      3.5   ✅ ana                      🧪 24 saat         3.52             3.52 -0.02
13.10 04     NMR      2.7   ✅ ana                      🧪 24 saat         2.70             2.74  0.00
13.10 04     LPT      1.8   ✅ ana                      🧪 24 saat         1.81             1.82 -0.01
13.10 04    SHIB      1.7   ✅ ana                      🧪 24 saat         1.71             1.71 -0.01
13.10 18    AAVE      2.0   ✅ ana             💵 ABD güçlü alıyor         2.01             2.01 -0.01
14.10 10     CRV      3.2   ✅ ana             💵 ABD güçlü alıyor         3.24             3.24 -0.04
14.10 11   MAGIC      1.9   ✅ ana                      🧪 24 saat         1.83             1.87  0.07
14.10 17    SHIB      0.4   ✅ ana                      🧪 24 saat         0.36             0.36  0.04
14.10 17     FIL      5.0   ✅ ana             💵 ABD güçlü alıyor         5.05             5.05 -0.05
14.10 19     RPL      2.2   ✅ ana                      🧪 24 saat         0.55             0.59  1.65
14.10 19     BNB      0.4 🔸 yedek 🪙 BNB 4s Çok güçlü ↑ · 4 saat          0.39             0.39  0.01
15.10 06     FIL     13.6 🔸 yedek             💵 ABD güçlü alıyor        13.60            13.60  0.00
15.10 06     DOT      0.4 🔸 yedek 🔇 DOT ⭐ en güçlü · 8 saat · is         0.37             0.37  0.03
15.10 12     INJ      3.2 🔸 yedek             💵 ABD güçlü alıyor         3.19             3.19  0.01
15.10 16     FIL      3.7 🔸 yedek             💵 ABD güçlü alıyor         3.69             3.69  0.01
15.10 17    DOGE      0.1 🔸 yedek 🪙 DOGE ⭐ en güçlü · 8 saat · i         0.07             0.07  0.03
16.10 21     ARB      1.8   ✅ ana       🤝 4 saat · BTC ile ortak         1.75             1.75  0.05
16.10 22     DIA      1.0 🔸 yedek       🤝 4 saat · BTC ile ortak         1.01             1.02 -0.01
16.10 22    POWR      0.6 🔸 yedek       🤝 4 saat · BTC ile ortak         0.69             0.64 -0.09
16.10 22     ILV      0.6 🔸 yedek       🤝 4 saat · BTC ile ortak         0.57             0.57  0.03
16.10 22     GNO      0.5 🔸 yedek       🤝 4 saat · BTC ile ortak         0.50             0.54  0.00
16.10 22    CELR      0.4 🔸 yedek       🤝 4 saat · BTC ile ortak         0.46             0.38 -0.06
16.10 22     TRB      0.2 🔸 yedek       🤝 4 saat · BTC ile ortak         0.24             0.24 -0.04
16.10 22     KSM      0.1 🔸 yedek       🤝 4 saat · BTC ile ortak         0.09             0.10  0.01
17.10 06     GNO      0.2 🔸 yedek       🤝 4 saat · BTC ile ortak          NaN             0.21   NaN
17.10 06   TURBO      0.1 🔸 yedek       🤝 4 saat · BTC ile ortak         0.12             0.12 -0.02
17.10 16      OP      0.8   ✅ ana       🤝 4 saat · BTC ile ortak         0.81             0.81 -0.01
17.10 16     DOT      0.2   ✅ ana       🤝 4 saat · BTC ile ortak         0.21             0.21 -0.01
17.10 16     GLM      1.8 🔸 yedek       🤝 4 saat · BTC ile ortak        -0.36            -0.37  2.16
17.10 16   SUSHI      0.9 🔸 yedek       🤝 4 saat · BTC ile ortak         0.86             0.86  0.04
17.10 16     KNC      0.8 🔸 yedek       🤝 4 saat · BTC ile ortak        -0.78            -0.79  1.58
17.10 16   SPELL      0.6 🔸 yedek       🤝 4 saat · BTC ile ortak         0.61             0.61 -0.01
17.10 16     INJ      0.3 🔸 yedek       🤝 4 saat · BTC ile ortak         0.32             0.32 -0.02
17.10 16     VET      0.3 🔸 yedek       🤝 4 saat · BTC ile ortak         0.31             0.31 -0.01
17.10 16    ROSE      0.3 🔸 yedek       🤝 4 saat · BTC ile ortak         0.27             0.27  0.03
17.10 17     AXL      0.8 🔸 yedek       🤝 4 saat · BTC ile ortak         0.76             0.75  0.04
17.10 19     BNT      1.1 🔸 yedek       🤝 4 saat · BTC ile ortak         0.64             0.51  0.46
17.10 19  PUNDIX      0.7 🔸 yedek       🤝 4 saat · BTC ile ortak         0.48             0.31  0.22
17.10 19   AUDIO      0.7 🔸 yedek       🤝 4 saat · BTC ile ortak         0.68             0.69  0.02
17.10 19     JTO      0.5 🔸 yedek       🤝 4 saat · BTC ile ortak         0.53             0.53 -0.03
17.10 19   SUPER      0.4 🔸 yedek       🤝 4 saat · BTC ile ortak         0.45             0.45 -0.05
17.10 19    LQTY      0.4 🔸 yedek       🤝 4 saat · BTC ile ortak         0.63             0.64 -0.23
17.10 19     STX      0.2 🔸 yedek       🤝 4 saat · BTC ile ortak         0.20             0.20  0.00
17.10 19     ETC      0.2 🔸 yedek       🤝 4 saat · BTC ile ortak         0.16             0.16  0.04
17.10 20     ZRX      1.9 🔸 yedek       🤝 4 saat · BTC ile ortak         1.89             1.89  0.01
17.10 20     FET      1.7 🔸 yedek       🤝 4 saat · BTC ile ortak         1.70             1.70  0.00
17.10 20  PUNDIX      1.3 🔸 yedek       🤝 4 saat · BTC ile ortak         1.71             1.27 -0.41
17.10 20    PYTH      1.1 🔸 yedek       🤝 4 saat · BTC ile ortak         1.14             1.14 -0.04
17.10 20    CELR      1.1 🔸 yedek       🤝 4 saat · BTC ile ortak        -0.59            -0.57  1.69
17.10 20     XTZ      1.1 🔸 yedek       🤝 4 saat · BTC ile ortak         1.06             1.06  0.04
17.10 20    ARPA      0.9 🔸 yedek       🤝 4 saat · BTC ile ortak         0.92             0.94 -0.02
17.10 20    ARKM      0.8 🔸 yedek       🤝 4 saat · BTC ile ortak        -0.05            -0.04  0.85
17.10 20     C98      0.6 🔸 yedek       🤝 4 saat · BTC ile ortak          NaN             0.64   NaN
17.10 20     QNT      0.6 🔸 yedek       🤝 4 saat · BTC ile ortak         0.64             0.64 -0.04
17.10 20   ETHFI      0.6 🔸 yedek       🤝 4 saat · BTC ile ortak         0.60             0.60  0.00
17.10 20    DASH      0.3 🔸 yedek       🤝 4 saat · BTC ile ortak         0.25             0.25  0.05
17.10 20     REZ      0.1 🔸 yedek       🤝 4 saat · BTC ile ortak         0.12             0.12 -0.02
17.10 20     KNC      0.1 🔸 yedek       🤝 4 saat · BTC ile ortak         0.18             0.11 -0.08
17.10 20    STRK      0.1 🔸 yedek       🤝 4 saat · BTC ile ortak         0.10             0.10  0.00
17.10 20   SUSHI      0.0 🔸 yedek       🤝 4 saat · BTC ile ortak         0.04             0.04 -0.04
18.10 01     LDO      2.8   ✅ ana       🤝 4 saat · BTC ile ortak         2.78             2.78  0.02
18.10 01     VET      2.7   ✅ ana       🤝 4 saat · BTC ile ortak         2.66             2.66  0.04
18.10 01     XTZ      2.6   ✅ ana       🤝 4 saat · BTC ile ortak         2.61             2.61 -0.01
18.10 01     TRB      2.6   ✅ ana       🤝 4 saat · BTC ile ortak         2.56             2.56  0.04
18.10 01    RARE      2.5   ✅ ana       🤝 4 saat · BTC ile ortak         2.52             2.52 -0.02
18.10 01     YFI      2.4   ✅ ana       🤝 4 saat · BTC ile ortak         2.44             2.44 -0.04
18.10 01    MANA      2.4   ✅ ana       🤝 4 saat · BTC ile ortak         2.37             2.37  0.03
18.10 01     KSM      2.0   ✅ ana       🤝 4 saat · BTC ile ortak         2.02             2.01 -0.02
18.10 01   FLOKI      1.5   ✅ ana       🤝 4 saat · BTC ile ortak         1.45             1.45  0.05
18.10 01     APT      0.9   ✅ ana       🤝 4 saat · BTC ile ortak         0.90             0.90  0.00
18.10 01      OP      0.2   ✅ ana       🤝 4 saat · BTC ile ortak         0.19             0.19  0.01
18.10 01     ARB      0.2   ✅ ana       🤝 4 saat · BTC ile ortak         0.16             0.16  0.04
18.10 01     DOT      3.4   ✅ ana       🤝 4 saat · BTC ile ortak         3.36             3.36  0.04
18.10 01     KSM      2.0   ✅ ana                      🧪 24 saat         2.02             2.01 -0.02
18.10 01    ATOM      1.7 🔸 yedek       🤝 4 saat · BTC ile ortak         1.73             1.73 -0.03
18.10 01   SUPER      1.6 🔸 yedek       🤝 4 saat · BTC ile ortak         1.62             1.62 -0.02
18.10 01    DASH      1.6 🔸 yedek       🤝 4 saat · BTC ile ortak         1.61             1.61 -0.01
18.10 01   TURBO      1.5 🔸 yedek       🤝 4 saat · BTC ile ortak         1.51             1.51 -0.01
18.10 01 AUCTION      1.4 🔸 yedek       🤝 4 saat · BTC ile ortak         1.45             1.45 -0.05
18.10 01     ZRX      1.4 🔸 yedek       🤝 4 saat · BTC ile ortak         1.40             1.40  0.00
18.10 01     CHZ      1.3 🔸 yedek       🤝 4 saat · BTC ile ortak         1.33             1.33 -0.03
18.10 01   METIS      1.2 🔸 yedek       🤝 4 saat · BTC ile ortak         1.20             1.20  0.00
18.10 01     IMX      1.0 🔸 yedek       🤝 4 saat · BTC ile ortak         1.03             1.03 -0.03
18.10 01    CAKE      1.0 🔸 yedek       🤝 4 saat · BTC ile ortak         0.99             1.00  0.01
18.10 01     C98      0.9 🔸 yedek       🤝 4 saat · BTC ile ortak         0.88             0.90  0.02
18.10 01     ENS      0.8 🔸 yedek       🤝 4 saat · BTC ile ortak         0.84             0.84 -0.04
18.10 01    ROSE      0.8 🔸 yedek       🤝 4 saat · BTC ile ortak         0.76             0.76  0.04
18.10 01     UNI      0.7 🔸 yedek       🤝 4 saat · BTC ile ortak         0.71             0.71 -0.01
18.10 01     ZEN      0.7 🔸 yedek       🤝 4 saat · BTC ile ortak         0.65             0.66  0.05
18.10 01    ARPA      0.6 🔸 yedek       🤝 4 saat · BTC ile ortak         0.61             0.62 -0.01
18.10 01   SUSHI      0.6 🔸 yedek       🤝 4 saat · BTC ile ortak         0.59             0.59  0.01
18.10 01     KNC      0.5 🔸 yedek       🤝 4 saat · BTC ile ortak         0.57             0.48 -0.07
18.10 01    ANKR      0.5 🔸 yedek       🤝 4 saat · BTC ile ortak         0.47             0.47  0.03
18.10 01    STRK      0.4 🔸 yedek       🤝 4 saat · BTC ile ortak         0.40             0.40  0.00
18.10 01    CTSI      0.4 🔸 yedek       🤝 4 saat · BTC ile ortak         0.37             0.37  0.03
18.10 01     WLD      0.3 🔸 yedek       🤝 4 saat · BTC ile ortak         0.28             0.28  0.02
18.10 01    BAND      0.3 🔸 yedek       🤝 4 saat · BTC ile ortak         0.28             0.27  0.02
18.10 01     XLM      0.3 🔸 yedek       🤝 4 saat · BTC ile ortak         0.26             0.26  0.04
18.10 01    MASK      0.3 🔸 yedek       🤝 4 saat · BTC ile ortak         0.24             0.25  0.06
18.10 01     STX      0.2 🔸 yedek       🤝 4 saat · BTC ile ortak         0.25             0.25 -0.05
18.10 01    TNSR      0.2 🔸 yedek       🤝 4 saat · BTC ile ortak         0.20             0.21  0.00
18.10 01     RLC      0.2 🔸 yedek       🤝 4 saat · BTC ile ortak         0.18             0.18  0.02
18.10 01   AUDIO      0.1 🔸 yedek       🤝 4 saat · BTC ile ortak         0.12             0.15 -0.02
18.10 01    CELR      0.1 🔸 yedek       🤝 4 saat · BTC ile ortak         0.11             0.07 -0.01
18.10 01  PUNDIX      0.1 🔸 yedek       🤝 4 saat · BTC ile ortak         0.23             0.12 -0.13
18.10 01     FET      0.1 🔸 yedek       🤝 4 saat · BTC ile ortak         0.10             0.10  0.00
18.10 01   ETHFI      0.1 🔸 yedek       🤝 4 saat · BTC ile ortak         0.07             0.07  0.03
18.10 01     GRT      0.0 🔸 yedek       🤝 4 saat · BTC ile ortak         0.04             0.04 -0.04
```

## 2) Canlı kopya: canlının kaydettiği tahmin ↔ aynı modelle taze veriden yeniden hesap (son 7 gün)
- BTC modeli 04.10 17:40 · canlı geçmişi aynı modelden mi: ✅
- canlı önbellekte 140 coin
- yeniden hesaplanan: 141 coin · atlanan 0: 
- 1 saat: 22761 tahmin · olasılık farkı ort 7.4e-07 · en büyük 2.6e-03 · 'Çok güçlü ↑' saat: canlı 1541 / yeniden 1541 · farklı 0
- 4 saat: 22761 tahmin · olasılık farkı ort 2.2e-05 · en büyük 1.5e-02 · 'Çok güçlü ↑' saat: canlı 1659 / yeniden 1660 · farklı 1
- 8 saat: 22761 tahmin · olasılık farkı ort 1.3e-06 · en büyük 3.1e-03 · 'Çok güçlü ↑' saat: canlı 1556 / yeniden 1556 · farklı 0
```
  coin  H   n     dmax     dort  u_canli  u_yeni  u_fark  saatler
   ARB  4 168 0.010662 0.000385        4       5       1 15.10 04
   DOT  4 168 0.014600 0.000516       18      18       0         
    OP  4 168 0.010758 0.000292        1       1       0         
   ADA  4 168 0.009148 0.000292       14      14       0         
  NEAR  4 168 0.008468 0.000318       20      20       0         
   BTC  4 168 0.007992 0.000313       10      10       0         
  LINK  4 168 0.007562 0.000165        7       7       0         
 FLOKI  4 168 0.006264 0.000070       22      22       0         
   BNB  4 168 0.005933 0.000170       18      18       0         
   ZRX  4 161 0.004210 0.000013       10      10       0         
  PEPE  4 168 0.003822 0.000113        3       3       0         
  SHIB  4 168 0.003285 0.000125       11      11       0         
   APT  4 168 0.003223 0.000069       15      15       0         
 METIS  8 161 0.003051 0.000012        7       7       0         
   ZEC  4 161 0.003027 0.000010       25      25       0         
   ENS  1 161 0.002555 0.000009       15      15       0         
   ETH  8 168 0.002547 0.000010       38      38       0         
   SUI  4 168 0.002134 0.000024       13      13       0         
   CVC  8 160 0.002069 0.000006       20      20       0         
  SHIB  1 168 0.001958 0.000006       10      10       0         
   CRV  8 161 0.001805 0.000006        9       9       0         
  FIDA  8 160 0.001625 0.000007        4       4       0         
  DOGE  4 168 0.001484 0.000040       15      15       0         
  MASK  8 160 0.001310 0.000004       21      21       0         
   AXS  1 161 0.001288 0.000004        7       7       0         
   FET  8 161 0.001186 0.000004       25      25       0         
  CTSI  8 161 0.001146 0.000006        0       0       0         
  DASH  4 161 0.001102 0.000004       11      11       0         
   ETH  4 168 0.000685 0.000019       24      24       0         
   ARB  1 168 0.000396 0.000001       15      15       0         
    AI  1 160 0.000371 0.000002       10      10       0         
   XLM  1 161 0.000104 0.000001        9       9       0         
RENDER  8 161 0.000022 0.000006        0       0       0         
   AMP  4 161 0.000018 0.000004        1       1       0         
RENDER  4 161 0.000017 0.000004        9       9       0         
   REQ  8 160 0.000016 0.000004        7       7       0         
   JTO  8 161 0.000015 0.000002        9       9       0         
   CHZ  4 160 0.000015 0.000003        3       3       0         
 SPELL  8 160 0.000013 0.000003       10      10       0         
  TNSR  8 160 0.000013 0.000003       12      12       0         
```

_süre 8 dk_
