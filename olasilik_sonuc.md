# 🎲 Olasılık bilimi ile sistem analizi (03.11.2026)
## 1) Rastgele yürüyüş teorisi vs gerçek 🎯 değme oranı (2025+, piyasa girişi; teori = 2·(1 − Φ(k)))
- ✅ ana (k 0,75): teori %45 · gerçek %56 (n 3413) → +11 puan gerçek avantaj
- 🔸 yedek (k 0,50): teori %62 · gerçek %63 (n 5864) → avantaj yok
- 📋 panelden (k 0,45): teori %65 · gerçek %64 (n 2895) → avantaj yok
## 2) Kelly (f* = p − (1−p)/b)
- Tarih 2025+ (D): ana p 0,68 · b 0,61 · f* +0,145 · panelden f* +0,057 · yedek f* −0,154
- Canlı 12.10 → (B): ana n 58 · f* +0,28 · yedek n 247 · f* +0,55 · panelden n 11 · f* +0,26
## 3) Bayes (Beta(1,1)): canlı türlerde gerçek isabet < %65 olasılığı
- ana 💵 0/4 → %99 · ana 🤝 10/19 → %88 · ana 🌐🧪 15/21 → %30 · ana 🌐🤝 10/12 → %11 · yedek 🌐🤝 184/241 → ~%0
## 4) Monte Carlo (✅ ana, 2025+ işlemlerinden yeniden örnekleme, 200 işlem, 5000 yol)
- pay %2: medyan +%1 · zarar olasılığı %16 · pay %5: +%2 · %15 · pay %7: +%3 · %16 · pay %15: +%7 · %16 · en kötü %5: −%1 … −%5
