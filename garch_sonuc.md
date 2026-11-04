# 📈 GARCH oynaklık tahmini ile sinyal ayrımı — PROTOKOL_garch.md
_04.11.2026 08:09 · ρ hesaplanan sinyal 25871 / 26862 · ρ medyan 1.19 · hücre: sinyal · isabet · net (fark isabet / net, aynı sınıfta koşulsuzlara göre)_

| sınıf | koşul | 2022-06→24 | 2025 | 2026 | sonuç |
|---|---|---|---|---|---|
| ✅ ana | G1 oynaklık artacak (ρ ≥ 1,2) | 2623 · %72 · +0.55 (+8 / +0.16) | 1157 · %70 · +0.07 (+9 / -0.06) | 730 · %72 · +0.48 (+6 / +0.21) |  |
| ✅ ana | G2 oynaklık azalacak (ρ ≤ 0,8) | 210 · %61 · +0.16 (-8 / -0.35) | 101 · %50 · -0.08 (-17 / -0.18) | 62 · %61 · +0.22 (-9 / -0.18) | ❌ kötü |
| 🔸 yedek | G1 oynaklık artacak (ρ ≥ 1,2) | 2728 · %71 · +0.02 (+1 / -0.16) | 1371 · %61 · -0.67 (-4 / -0.63) | 953 · %73 · +0.22 (+5 / +0.08) |  |
| 🔸 yedek | G2 oynaklık azalacak (ρ ≤ 0,8) | 546 · %63 · +0.13 (-8 / +0.02) | 447 · %60 · -0.08 (-4 / +0.24) | 261 · %61 · +0.11 (-10 / -0.07) |  |
| 📋 panelden | G1 oynaklık artacak (ρ ≥ 1,2) | 1855 · %71 · +0.15 (+2 / -0.03) | 628 · %67 · -0.02 (+0 / -0.12) | 507 · %74 · +0.09 (+9 / +0.02) |  |
| 📋 panelden | G2 oynaklık azalacak (ρ ≤ 0,8) | 260 · %66 · +0.13 (-4 / -0.04) | 122 · %54 · -0.31 (-14 / -0.39) | 147 · %63 · +0.17 (-6 / +0.10) |  |

**Geçen hücre: 1 · plasebo ort. 0.00 (en çok 0)**

## Ek 1 sağlamlık (✅ ana ∧ ρ ≤ 0,8 "kötü")
- T1 coin yarıları: −10,3 / −0,43 · −11,3 / −0,11 ✔
- T2 limit: 2022–24 −9,5 / −0,46 · 2025 −16,5 / −0,43 · 2026 −4,4 / −0,10 ✔
- T3 aylık: 28 ayın %64'ünde kötü ✔
- T4 ilk 5 coin (ETH, DOGE, ADA, CVC, LINK) hariç: −10,0 / −0,20; dönemler −7,3 · −15,5 · −8,9 ✔
- T5 eşik: ρ ≤ 0,9 ✔ (−10,5 · −14,1 · −7,1, net hep < 0) · ρ ≤ 0,7 ✘ (2025: isabet −15 ama net +0,33, n 37)
**→ GEÇMEDİ (T5'te tek alt koşul, küçük örnek). Canlıya alınmaz; öneri: gölge izleme.**
