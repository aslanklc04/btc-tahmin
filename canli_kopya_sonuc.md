# 🔍 Canlı = test denetimi — 21.10.2026 14:07

## 1) Sızıntı testi (veri t anında kesilince sonuç aynı mı?)
- BTC: en büyük fark — özellikler 0.0e+00 · saat içi 0.0e+00 · yol 0.0e+00 · sinyal/eşik 0.0e+00 · z 0.0e+00 → ✅ sızıntı yok
- ETH: en büyük fark — özellikler 0.0e+00 · saat içi 0.0e+00 · yol 0.0e+00 · sinyal/eşik 0.0e+00 · z 0.0e+00 → ✅ sızıntı yok
- OP: en büyük fark — özellikler 0.0e+00 · saat içi 0.0e+00 · yol 0.0e+00 · sinyal/eşik 0.0e+00 · z 0.0e+00 → ✅ sızıntı yok
- LDO: en büyük fark — özellikler 0.0e+00 · saat içi 0.0e+00 · yol 0.0e+00 · sinyal/eşik 0.0e+00 · z 0.0e+00 → ✅ sızıntı yok

## 3) Gönderilen sinyallerde coin primi z: mesajdaki ↔ araştırma yöntemi (aynı saat, taze veri)
- 177 coin-sinyal · |fark| ortalama 0.09 · |fark| > 0,5 olan 6 · eşik tarafı değişen (mesaj ≥ 0 ama araştırma < 0 ya da tersi): 7 · ≥ 2 tarafı değişen: 1
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
18.10 16   TURBO      2.2   ✅ ana                      🧪 24 saat         2.21             2.21 -0.01
18.10 18      OP      0.3   ✅ ana       🤝 4 saat · BTC ile ortak         0.26             0.26  0.04
18.10 18     SEI      1.3 🔸 yedek       🤝 4 saat · BTC ile ortak         1.34             1.34 -0.04
18.10 18     RLC      1.1 🔸 yedek       🤝 4 saat · BTC ile ortak         1.02             1.05  0.08
18.10 18     OGN      0.8 🔸 yedek       🤝 4 saat · BTC ile ortak         0.75             0.76  0.05
18.10 18    MANA      0.8 🔸 yedek       🤝 4 saat · BTC ile ortak         0.76             0.76  0.04
18.10 18     ENS      0.6 🔸 yedek       🤝 4 saat · BTC ile ortak         0.63             0.63 -0.03
18.10 18    VTHO      0.4 🔸 yedek       🤝 4 saat · BTC ile ortak         0.44             0.44 -0.04
18.10 18    PYTH      0.3 🔸 yedek       🤝 4 saat · BTC ile ortak         0.35             0.35 -0.05
18.10 18    ATOM      0.3 🔸 yedek       🤝 4 saat · BTC ile ortak         0.31             0.31 -0.01
18.10 18    STRK      0.2 🔸 yedek       🤝 4 saat · BTC ile ortak         0.15             0.15  0.05
18.10 18     STX      0.1 🔸 yedek       🤝 4 saat · BTC ile ortak         0.11             0.11 -0.01
18.10 18     NMR      0.1 🔸 yedek       🤝 4 saat · BTC ile ortak         0.09             0.09  0.01
18.10 18     JTO      0.1 🔸 yedek       🤝 4 saat · BTC ile ortak         0.07             0.07  0.03
18.10 23    RARE      2.9   ✅ ana       🤝 4 saat · BTC ile ortak         2.90             2.90  0.00
18.10 23   SUSHI      2.8   ✅ ana       🤝 4 saat · BTC ile ortak         2.75             2.75  0.05
18.10 23   TURBO      2.4   ✅ ana       🤝 4 saat · BTC ile ortak         2.37             2.37  0.03
18.10 23     WLD      2.4   ✅ ana       🤝 4 saat · BTC ile ortak         2.35             2.35  0.05
18.10 23    SHIB      0.4   ✅ ana       🤝 4 saat · BTC ile ortak         0.42             0.42 -0.02
18.10 23     DOT      0.2   ✅ ana       🤝 4 saat · BTC ile ortak         0.18             0.18  0.02
18.10 23     JTO      3.5   ✅ ana       🤝 4 saat · BTC ile ortak         3.54             3.54 -0.04
18.10 23    MANA      1.9 🔸 yedek       🤝 4 saat · BTC ile ortak         1.93             1.93 -0.03
18.10 23   SPELL      1.6 🔸 yedek       🤝 4 saat · BTC ile ortak         0.23             0.23  1.37
18.10 23     DIA      1.4 🔸 yedek       🤝 4 saat · BTC ile ortak         1.42             1.42 -0.02
18.10 23    ANKR      1.4 🔸 yedek       🤝 4 saat · BTC ile ortak         1.37             1.38  0.03
18.10 23     GLM      1.3 🔸 yedek       🤝 4 saat · BTC ile ortak         1.30             1.32  0.00
18.10 23    PYTH      1.3 🔸 yedek       🤝 4 saat · BTC ile ortak         1.31             1.31 -0.01
18.10 23     ILV      1.3 🔸 yedek       🤝 4 saat · BTC ile ortak         1.27             1.27  0.03
18.10 23    FIDA      1.2 🔸 yedek       🤝 4 saat · BTC ile ortak         1.19             1.21  0.01
18.10 23    CELR      1.2 🔸 yedek       🤝 4 saat · BTC ile ortak         1.27             1.15 -0.07
18.10 23     LPT      1.0 🔸 yedek       🤝 4 saat · BTC ile ortak         1.01             1.03 -0.01
18.10 23     SEI      1.0 🔸 yedek       🤝 4 saat · BTC ile ortak         1.01             1.01 -0.01
18.10 23    CAKE      1.0 🔸 yedek       🤝 4 saat · BTC ile ortak         1.01             1.01 -0.01
18.10 23    TNSR      1.0 🔸 yedek       🤝 4 saat · BTC ile ortak         0.99             0.99  0.01
18.10 23    ROSE      0.9 🔸 yedek       🤝 4 saat · BTC ile ortak         0.91             0.91 -0.01
18.10 23     SKL      0.9 🔸 yedek       🤝 4 saat · BTC ile ortak         0.91             0.91 -0.01
18.10 23     FET      0.8 🔸 yedek       🤝 4 saat · BTC ile ortak         0.83             0.83 -0.03
18.10 23     SNX      0.8 🔸 yedek       🤝 4 saat · BTC ile ortak         0.81             0.81 -0.01
18.10 23     FIL      0.8 🔸 yedek       🤝 4 saat · BTC ile ortak         0.81             0.81 -0.01
18.10 23    LQTY      0.8 🔸 yedek       🤝 4 saat · BTC ile ortak         0.77             0.80  0.03
18.10 23     ENS      0.8 🔸 yedek       🤝 4 saat · BTC ile ortak         0.80             0.79  0.00
18.10 23    POWR      0.7 🔸 yedek       🤝 4 saat · BTC ile ortak         0.78             0.74 -0.08
18.10 23     POL      0.7 🔸 yedek       🤝 4 saat · BTC ile ortak         0.73             0.73 -0.03
18.10 23    EGLD      0.7 🔸 yedek       🤝 4 saat · BTC ile ortak         0.72             0.71 -0.02
18.10 23    SAND      0.6 🔸 yedek       🤝 4 saat · BTC ile ortak         0.64             0.64 -0.04
18.10 23   SUPER      0.6 🔸 yedek       🤝 4 saat · BTC ile ortak         0.62             0.62 -0.02
18.10 23  PUNDIX      0.5 🔸 yedek       🤝 4 saat · BTC ile ortak         0.77             0.54 -0.27
18.10 23    ARKM      0.5 🔸 yedek       🤝 4 saat · BTC ile ortak         0.51             0.53 -0.01
18.10 23     UMA      0.5 🔸 yedek       🤝 4 saat · BTC ile ortak         0.52             0.53 -0.02
18.10 23     BNT      0.5 🔸 yedek       🤝 4 saat · BTC ile ortak         0.56             0.45 -0.06
18.10 23     ZRX      0.4 🔸 yedek       🤝 4 saat · BTC ile ortak         0.41             0.41 -0.01
18.10 23    BONK      0.4 🔸 yedek       🤝 4 saat · BTC ile ortak         0.39             0.39  0.01
18.10 23    BLUR      0.3 🔸 yedek       🤝 4 saat · BTC ile ortak         0.30             0.30  0.00
18.10 23   METIS      0.3 🔸 yedek       🤝 4 saat · BTC ile ortak         0.29             0.28  0.01
18.10 23    KAVA      0.3 🔸 yedek       🤝 4 saat · BTC ile ortak         0.33             0.28 -0.03
18.10 23   JASMY      0.2 🔸 yedek       🤝 4 saat · BTC ile ortak         0.25             0.25 -0.05
18.10 23    ALGO      0.2 🔸 yedek       🤝 4 saat · BTC ile ortak         0.22             0.22 -0.02
18.10 23      ZK      0.2 🔸 yedek       🤝 4 saat · BTC ile ortak         0.21             0.21 -0.01
18.10 23     C98      0.2 🔸 yedek       🤝 4 saat · BTC ile ortak         0.21             0.21 -0.01
18.10 23    STRK      0.1 🔸 yedek       🤝 4 saat · BTC ile ortak         0.11             0.11 -0.01
18.10 23    CTSI      0.1 🔸 yedek       🤝 4 saat · BTC ile ortak        -0.11            -0.10  0.21
18.10 23     XTZ      0.1 🔸 yedek       🤝 4 saat · BTC ile ortak         0.07             0.07  0.03
18.10 23    DASH      0.1 🔸 yedek       🤝 4 saat · BTC ile ortak         0.07             0.07  0.03
18.10 23     ETC      0.1 🔸 yedek       🤝 4 saat · BTC ile ortak         0.06             0.06  0.04
18.10 23     RLC      0.0 🔸 yedek       🤝 4 saat · BTC ile ortak         0.02             0.05 -0.02
20.10 04     SKL      0.6 🔸 yedek       🤝 4 saat · BTC ile ortak         0.62             0.62 -0.02
```

## 2) Canlı kopya: canlının kaydettiği tahmin ↔ aynı modelle taze veriden yeniden hesap (son 7 gün)
- BTC modeli 04.10 17:40 · canlı geçmişi aynı modelden mi: ✅
- canlı önbellekte 140 coin
- yeniden hesaplanan: 141 coin · atlanan 0: 
- 1 saat: 23688 tahmin · olasılık farkı ort 4.2e-07 · en büyük 2.7e-03 · 'Çok güçlü ↑' saat: canlı 1116 / yeniden 1116 · farklı 0
- 4 saat: 23688 tahmin · olasılık farkı ort 1.3e-04 · en büyük 2.9e-02 · 'Çok güçlü ↑' saat: canlı 1485 / yeniden 1489 · farklı 22
- 8 saat: 23688 tahmin · olasılık farkı ort 6.1e-07 · en büyük 2.5e-03 · 'Çok güçlü ↑' saat: canlı 1570 / yeniden 1570 · farklı 0
```
 coin  H   n     dmax     dort  u_canli  u_yeni  u_fark                    saatler
 TNSR  4 168 0.029185 0.001192       19      22       3 14.10 21 14.10 22 15.10 02
  RLC  4 168 0.006821 0.000251       28      26       2          16.10 16 16.10 23
  SNX  4 168 0.003879 0.000194        1       3       2          15.10 03 15.10 04
  ALT  4 168 0.018504 0.000085       16      15       1                   15.10 05
  FET  4 168 0.011494 0.000402        8       9       1                   15.10 03
  RPL  4 168 0.011358 0.000276       21      20       1                   14.10 15
 MASK  4 168 0.009683 0.000323        9      10       1                   14.10 19
  ZRX  4 168 0.008810 0.000368       12      13       1                   14.10 15
 LQTY  4 168 0.008473 0.000112       23      24       1                   14.10 20
  NMR  4 168 0.006297 0.000066        5       6       1                   14.10 18
  TAO  4 168 0.006080 0.000259        7       6       1                   15.10 01
 FIDA  4 168 0.006014 0.000267        6       7       1                   15.10 06
 STRK  4 168 0.005754 0.000223       48      49       1                   14.10 19
 AAVE  4 168 0.005110 0.000038       14      15       1                   14.10 19
  CRV  4 168 0.003612 0.000037        8       7       1                   15.10 04
 BICO  4 168 0.003502 0.000113       10       9       1                   16.10 19
  RAY  4 168 0.003436 0.000119       26      25       1                   16.10 03
  XLM  4 168 0.002742 0.000087        8       7       1                   16.10 16
    W  4 168 0.017023 0.000813       30      30       0                           
  REZ  4 168 0.016708 0.000106       31      31       0                           
  ICP  4 168 0.016195 0.000498        6       6       0                           
 ROSE  4 168 0.014990 0.000660       17      17       0                           
   IO  4 168 0.014081 0.000754        0       0       0                           
  JTO  4 168 0.011735 0.000268        8       8       0                           
 MINA  4 168 0.008902 0.000348        0       0       0                           
 BONK  4 168 0.008831 0.000048        3       3       0                           
  KSM  4 168 0.008443 0.000218        7       7       0                           
  ADA  4 168 0.007927 0.000246        6       6       0                           
METIS  4 168 0.007280 0.000299       16      16       0                           
  CVC  4 168 0.007258 0.000319        2       2       0                           
 ANKR  4 168 0.006958 0.000336        8       8       0                           
JASMY  4 168 0.006886 0.000093        8       8       0                           
  GRT  4 168 0.006455 0.000322        6       6       0                           
 MANA  4 168 0.006434 0.000348        5       5       0                           
  GMT  4 168 0.006343 0.000223       11      11       0                           
  LTC  4 168 0.006170 0.000145       22      22       0                           
  TIA  4 168 0.006053 0.000029       18      18       0                           
 POWR  4 168 0.006044 0.000271       13      13       0                           
  FIL  4 168 0.005988 0.000227       11      11       0                           
 ARKM  4 168 0.005842 0.000149       10      10       0                           
```

_süre 10 dk_
