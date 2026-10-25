# sekil_egim.py — PROTOKOL_sekil.md EK ANALİZ (protokolde yoktu, 25.10): etkenler YÖNÜ değiştiriyor mu?
# Yön eğimi = [P(yükselişle biten: ⬆️ ⬆️↘️ ↘️⬆️) / P(düşüşle biten: ⬇️ ⬇️↗️ ↗️⬇️)] o koşulda ÷ aynı oran genelde. 1'den büyük = yükseliş lehine.
# Şart (önceden, sonuç görülmeden bu dosyada): keşif ≥ 1,15 (≤ 0,87) VE 2025+ ve dokunulmamış coin'lerde aynı yönde ≥ 1,10 (≤ 0,91), her birinde ≥ 5.000 pencere.
import glob, numpy as np, pandas as pd
T1 = pd.concat([pd.read_csv(f) for f in glob.glob("parca/**/sekil_t1_*.csv", recursive=True)]).groupby(["g", "don", "W", "etken", "dilim", "sh"]).n.sum().reset_index()
T2 = pd.concat([pd.read_csv(f) for f in glob.glob("parca/**/sekil_t2_*.csv", recursive=True)]).groupby(["g", "don", "W", "sh"])[["n", "son_top"]].sum().reset_index()
SH = {1: "↕️ Testere", 2: "➖ Sakin", 3: "⬆️ Direkt yükseliş", 4: "⬆️↘️ Yükselip sonda geri çekildi", 5: "↘️⬆️ Kısa düşüp uzun yükseldi", 6: "⬇️ Direkt düşüş", 7: "⬇️↗️ Düşüp sonda toparladı", 8: "↗️⬇️ Kısa yükselip uzun düştü", 9: "↔️ Gidip döndü"}
DL = {"r1": ["son 1 s sert düşmüş", "son 1 s normal", "son 1 s sert yükselmiş"], "r4": ["son 4 s sert düşmüş", "son 4 s normal", "son 4 s sert yükselmiş"], "r24": ["son 24 s sert düşmüş", "son 24 s normal", "son 24 s sert yükselmiş"],
      "vol": ["oynaklık düşük", "oynaklık normal", "oynaklık yüksek"], "hacim": ["hacim düşük", "hacim normal", "hacim yüksek"], "konum": ["24 s dibine yakın", "24 s ortasında", "24 s tepesine yakın"],
      "btc_r4": ["BTC son 4 s sert düşmüş", "BTC 4 s normal", "BTC son 4 s sert yükselmiş"], "btc_r24": ["BTC son 24 s sert düşmüş", "BTC 24 s normal", "BTC son 24 s sert yükselmiş"],
      "btc_vol": ["BTC oynaklığı düşük", "BTC oynaklığı normal", "BTC oynaklığı yüksek"], "saat": ["TR 00–06", "TR 06–12", "TR 12–18", "TR 18–24"], "gun": ["hafta içi", "hafta sonu"], "once": [f"önceki: {SH[i]}" for i in range(1, 10)]}
ad = lambda e, d: DL[e][int(d) - 1] if e == "once" else DL[e][int(d)]
def egim(m):
    d = T1[m].copy(); d["yon"] = np.select([d.sh.isin([3, 4, 5]), d.sh.isin([6, 7, 8])], ["up", "dn"], "x")
    t = d.groupby(["W", "etken", "dilim", "yon"]).n.sum().unstack(fill_value=0); b = d[d.etken == "saat"].groupby(["W", "yon"]).n.sum().unstack()
    oran = (t.up / t.dn) / (b.up / b.dn).reindex(t.index.get_level_values(0)).values
    return pd.DataFrame({"egim": oran, "yuk": t.up / t.sum(1), "n": t.sum(1)})
K = egim((T1.g == "A") & (T1.don == "kesif")); A = egim((T1.g == "A") & (T1.don == "dog")); B = egim(T1.g == "B")
X = K.join(A, rsuffix="_A").join(B, rsuffix="_B").reset_index(); X = X[X.dilim >= 0]
ok = (X.n >= 5000) & (X.n_A >= 5000) & (X.n_B >= 5000) & (((X.egim >= 1.15) & (X.egim_A >= 1.10) & (X.egim_B >= 1.10)) | ((X.egim <= 0.87) & (X.egim_A <= 0.91) & (X.egim_B <= 0.91)))
Y = X[ok].copy(); Y["guc"] = np.abs(np.log(Y[["egim", "egim_A", "egim_B"]])).min(1)
L = ["# 🧭 Ek analiz: etkenler yönü değiştiriyor mu? (PROTOKOL_sekil, protokolde yoktu — şart bu dosyanın başında, sonuçtan önce yazıldı)", "",
     f"_Yön eğimi = o koşulda (yükselişle biten ÷ düşüşle biten) oranı, genele göre. ×1,20 = yükseliş %20 daha olası. {ok.sum()} / {len(X)} koşul şartı geçti._", ""]
for W in (1, 4, 8, 24):
    y = Y[Y.W == W].sort_values("egim")
    L.append(f"## {W} saat — {len(y)} tutarlı yön etkisi"); L.append("| Koşul | yön eğimi keşif · 2025+ · dokunulmamış | yükselişle biten pay (keşif · dokunulmamış) |"); L.append("|---|---|---|")
    for _, r in y.iterrows(): L.append(f"| {ad(r.etken, r.dilim)} | ×{r.egim:.2f} · ×{r.egim_A:.2f} · ×{r.egim_B:.2f} | %{100 * r.yuk:.0f} · %{100 * r.yuk_B:.0f} |")
    L.append("")
L.append("## Şekilden sonra ne geliyor (sonraki pencerenin ortalama getirisi, σ cinsinden; + yükseliş)")
for W in (1, 4, 8, 24):
    s = [f"{SH[sh].split(' ')[0]} " + " / ".join(f"{(T2[(T2.g == g) & ((T2.don == dn) if dn else True) & (T2.W == W) & (T2.sh == sh)].son_top.sum() / T2[(T2.g == g) & ((T2.don == dn) if dn else True) & (T2.W == W) & (T2.sh == sh)].n.sum()):+.3f}" for g, dn in (("A", "kesif"), ("A", "dog"), ("B", None))) for sh in range(1, 10)]
    L.append(f"- **{W} s** (keşif / 2025+ / dokunulmamış): " + " · ".join(s))
open("sekil_egim_sonuc.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
