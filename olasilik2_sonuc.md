# 🎲 Olasılık bilimi 2 — Markov · Thompson · HMM (PROTOKOL_olasilik2.md)
_03.11.2026 23:30 · 26862 sinyal · ölçü D_T0_

## P1 — Markov zinciri / sıcak el (saat sepeti)
| yıl | sepet | P(kazan│önceki kazandı) − P(kazan│önceki kaybetti) | ×1,5/×0,5 pay: net farkı | plasebo %95 (fark / net) |
|---|---|---|---|---|
| 2024 | 1676 | +4.2 puan | +0.020% | +3.4 / +0.032% |
| 2025 | 1790 | +0.0 puan | +0.001% | +4.3 / +0.037% |
| 2026 | 1566 | +4.6 puan | -0.014% | +3.5 / +0.029% |
**P1 → ❌ geçmedi**

## P2 — Thompson örneklemesi (kol = sınıf × tür, son 180 gün, yalnız sonucu bilinenler)
| yıl | eşit pay | haydut ağırlıklı | fark net | atlanan sinyal |
|---|---|---|---|---|
| 2024 | 6668 · %72 · +0.369% | %71 · +0.377% | +0.008% | %4 |
| 2025 | 7210 · %65 · -0.099% | %64 · -0.115% | -0.016% | %40 |
| 2026 | 4962 · %69 · +0.204% | %69 · +0.219% | +0.015% | %23 |
**P2 → ❌ geçmedi**

## P3 — Gizli Markov modeli (BTC günlük, 2 durum, ileri algoritma)
| yıl | sakin (p_f < 0,3) | fırtınalı (p_f ≥ 0,7) | tümü | kural: kötü durumda alma | kalan |
|---|---|---|---|---|---|
| 2024 | 4579 · %71 · +0.301% | 1150 · %78 · +0.795% | 6666 · %72 · +0.368% | fırtınada alma → 5516 · %70 · +0.279% | %83 |
| 2025 | 5510 · %64 · -0.202% | 645 · %72 · +0.447% | 7210 · %65 · -0.099% | sakinde alma → 1700 · %69 · +0.233% | %24 |
| 2026 | 3690 · %69 · +0.184% | 614 · %74 · +0.262% | 4962 · %69 · +0.204% | sakinde alma → 1272 · %71 · +0.263% | %26 |
**P3 → ❌ geçmedi**

## Özet: P1 ❌ · P2 ❌ · P3 ❌
