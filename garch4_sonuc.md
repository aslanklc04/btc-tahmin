# 📈 Kısmi GARCH hedefi (γ↑ 0,25 · γ↓ 1,5) — risk ve tam test (PROTOKOL_garch.md Ek 4, ✅ ana)
_04.11.2026 09:51_

| dönem | bugünkü (T0) | kısmi GARCH |
|---|---|---|
| 2022-06→24 | %68.7 · +0.492 · CVaR5 -7.11 · std 2.60 · MDD -246 · en kötü -17.3 | %68.7 · +0.529 · CVaR5 -7.31 · std 2.71 · MDD -256 · en kötü -17.4 |
| 2025 | %66.1 · +0.093 · CVaR5 -10.68 · std 3.58 · MDD -280 · en kötü -30.1 | %66.8 · +0.144 · CVaR5 -10.64 · std 3.63 · MDD -254 · en kötü -30.1 |
| 2026 | %69.6 · +0.386 · CVaR5 -5.72 · std 2.03 · MDD -39 · en kötü -14.0 | %70.3 · +0.427 · CVaR5 -5.74 · std 2.08 · MDD -38 · en kötü -14.0 |
- yarı 0: %68.0 · +0.335 · CVaR5 -7.85 · std 2.80 · MDD -235 · en kötü -29.3 → %68.2 · +0.383 · CVaR5 -7.89 · std 2.88 · MDD -220 · en kötü -29.3
- yarı 1: %68.3 · +0.402 · CVaR5 -8.08 · std 2.85 · MDD -150 · en kötü -30.1 → %68.7 · +0.435 · CVaR5 -8.23 · std 2.93 · MDD -135 · en kötü -30.1
- limit 2022-06→24: %67.8 · +0.590 · CVaR5 -7.50 · std 2.76 · MDD -229 · en kötü -17.2 → %67.6 · +0.639 · CVaR5 -7.71 · std 2.90 · MDD -241 · en kötü -17.3
- limit 2025: %64.4 · +0.235 · CVaR5 -10.60 · std 3.68 · MDD -257 · en kötü -29.3 → %64.4 · +0.285 · CVaR5 -10.54 · std 3.74 · MDD -234 · en kötü -29.3
- limit 2026: %68.9 · +0.542 · CVaR5 -5.79 · std 2.19 · MDD -22 · en kötü -13.8 → %68.9 · +0.572 · CVaR5 -5.81 · std 2.26 · MDD -23 · en kötü -13.8
- aylık: 53 ay · kısmi ≥ bugünkü olan ay oranı %68
- ilk 5 coin (ETH, ADA, DOGE, LINK, DOT) hariç: %69.0 · +0.422 · CVaR5 -8.64 · std 3.04 · MDD -229 · en kötü -30.1 → %69.4 · +0.466 · CVaR5 -8.75 · std 3.14 · MDD -227 · en kötü -30.1
- komşu γ↑ 0 · γ↓ 1.0: net farkı +0.001 · -0.008 · -0.004
- komşu γ↑ 0 · γ↓ 1.5: net farkı +0.000 · +0.000 · -0.007
- komşu γ↑ 0.5 · γ↓ 1.0: net farkı +0.087 · +0.095 · +0.089
- komşu γ↑ 0.5 · γ↓ 1.5: net farkı +0.087 · +0.103 · +0.085

**Risk azaldı mı: ❌ HAYIR** (R1 üç dönemde ✘, belirgin iyileşme 0/3 dönem)
**Tam test:** T1 dönemler ✔ · T2 coin yarıları ✘ · T3 limit ✘ · T4 aylık ✔ · T5 ilk 5 coin hariç ✔ · T6 komşular ✔
**→ ❌ GEÇMEDİ: eklenmez**
