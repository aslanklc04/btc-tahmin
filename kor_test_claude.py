# kor_test_claude.py — Claude'un yargısı (sonuç görülmeden, 02.11.2026 02:3x yazıldı). Kuralları sezgimle koydum; her sinyale 'tutma olasılığı' (%) verir.
import pandas as pd
d = pd.read_csv("kor_test_soru.csv")
def yargi(r):
    p = 70.0                                                                                     # taban: üretilen sinyallerin genel isabeti ~%70
    p += 5 if r["hedef%"] < 0.6 else (-6 if (r.H <= 4 and r["hedef%"] > 1.3) else 0)               # yakın hedef kolay, 4 s'te uzak hedef zor
    if r.H >= 24 and r["hedef%"] < 2: p += 3                                                      # uzun süre + makul hedef
    if r.coin24_z <= -2: p += 8 if r.sinif == "✅ ana" else 3                                       # 📉🔥 dip: ana'da güçlü
    if r.btc_oyn >= 1.25: p += 8 if r.tur == "🌐🧪" else 3                                          # BTC oynak: hedefe değme şansı artar
    if r.btc_prim_z >= 1.5: p += 3                                                                # ABD alıyor
    if r.btc_prim_z <= -1: p -= 4                                                                 # ABD satıyor
    if r["btc24%"] <= -3: p -= 4                                            # BTC sert düşüşte: 4 s içinde dönüş belirsiz
    if r.tur == "🤝" and r.sinif == "✅ ana": p -= 5                                                # canlıda en zayıf tür
    if r.H <= 4 and r["coin24%"] >= 6: p -= 3                                                     # zaten çok yükselmiş coin, kısa sürede ek hedef zor
    if r.fon_z >= 1.5: p += 2                                                                     # 🔥 fonlama yüksek (ELİT ipucu)
    if r.coin24_z >= 3 and r.tur != "🚀": p -= 3                                                   # aşırı ısınmış
    return max(30, min(92, p))
d["claude_p"] = d.apply(yargi, axis=1); d["claude_tahmin"] = (d.claude_p >= 72).map({True: "TUTAR", False: "tutmaz"})
d[["id", "claude_p", "claude_tahmin"]].to_csv("kor_test_claude.csv", index=False)
print(d.claude_tahmin.value_counts().to_dict(), "· ort. olasılık", round(d.claude_p.mean(), 1))
