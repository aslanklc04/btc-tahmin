# sekil_birlestir.py — PROTOKOL_sekil.md: parça tablolarını birleştir → atlas + etken keşifleri (keşif / doğrulama A / doğrulama B)
import glob, numpy as np, pandas as pd
rd = lambda p: pd.concat([pd.read_csv(f) for f in glob.glob(f"parca/**/{p}_*.csv", recursive=True)])
T1 = rd("sekil_t1").groupby(["g", "don", "W", "etken", "dilim", "sh"]).n.sum().reset_index()
T2 = rd("sekil_t2").groupby(["g", "don", "W", "sh"])[["n", "r_top", "son_top", "yuk_top"]].sum().reset_index()
T3 = rd("sekil_t3").groupby(["g", "don", "W", "sh", "son_sh"]).n.sum().reset_index()
SH = {1: "↕️ Testere", 2: "➖ Sakin", 3: "⬆️ Direkt yükseliş", 4: "⬆️↘️ Yükselip sonda geri çekildi", 5: "↘️⬆️ Kısa düşüp uzun yükseldi", 6: "⬇️ Direkt düşüş", 7: "⬇️↗️ Düşüp sonda toparladı", 8: "↗️⬇️ Kısa yükselip uzun düştü", 9: "↔️ Gidip döndü"}
DL = {"r1": ["son 1 s sert düşmüş", "son 1 s normal", "son 1 s sert yükselmiş"], "r4": ["son 4 s sert düşmüş", "son 4 s normal", "son 4 s sert yükselmiş"],
      "r24": ["son 24 s sert düşmüş", "son 24 s normal", "son 24 s sert yükselmiş"], "vol": ["oynaklık düşük", "oynaklık normal", "oynaklık yüksek"],
      "hacim": ["hacim düşük", "hacim normal", "hacim yüksek"], "konum": ["24 s dibine yakın", "24 s ortasında", "24 s tepesine yakın"],
      "btc_r4": ["BTC son 4 s sert düşmüş", "BTC 4 s normal", "BTC son 4 s sert yükselmiş"], "btc_r24": ["BTC son 24 s sert düşmüş", "BTC 24 s normal", "BTC son 24 s sert yükselmiş"],
      "btc_vol": ["BTC oynaklığı düşük", "BTC oynaklığı normal", "BTC oynaklığı yüksek"], "saat": ["TR 00–06", "TR 06–12", "TR 12–18", "TR 18–24"], "gun": ["hafta içi", "hafta sonu"],
      "once": [f"önceki pencere: {SH[i]}" for i in range(1, 10)]}
def ad(e, d): return (DL[e][int(d) - 1] if e == "once" else DL[e][int(d)]) if d >= 0 else "?"
GR = {"kesif": (T1.g == "A") & (T1.don == "kesif"), "A": (T1.g == "A") & (T1.don == "dog"), "B": T1.g == "B"}
L = ["# 🧭 Fiyat hareket şekilleri — atlas ve etkenler · PROTOKOL_sekil.md", ""]
n_tot = T2.groupby(["g", "don"]).n.sum()
L.append(f"_Pencere sayısı (her saat başı, 4 ufuk toplam): araştırma keşif {n_tot.get(('A', 'kesif'), 0):,} · araştırma 2025+ {n_tot.get(('A', 'dog'), 0):,} · dokunulmamış {n_tot[n_tot.index.get_level_values(0) == 'B'].sum():,}. Pencereler üst üste biner (her saat başlar) → sayılar bağımsız değildir._\n")
for W in (1, 4, 8, 24):
    L.append(f"## {W} saatlik pencere — şekil sıklığı ve sonrası")
    L.append("| Şekil | keşif % | 2025+ % | dokunulmamış % | sonraki pencere ort. getiri (σ) | sonraki pencerede ⬆️ (r ≥ 0,25σ) |"); L.append("|---|---|---|---|---|---|")
    for s in range(1, 10):
        def p(g, don=None):
            d = T2[(T2.g == g) & (T2.W == W) & ((T2.don == don) if don else True)]; return 100 * d[d.sh == s].n.sum() / d.n.sum()
        a = T2[(T2.g == "A") & (T2.W == W) & (T2.sh == s)]
        L.append(f"| {SH[s]} | %{p('A', 'kesif'):.1f} | %{p('A', 'dog'):.1f} | %{p('B'):.1f} | {a.son_top.sum() / a.n.sum():+.3f} | %{100 * a.yuk_top.sum() / a.n.sum():.0f} |")
    t = T3[(T3.g == "A") & (T3.W == W)].groupby(["sh", "son_sh"]).n.sum().unstack(fill_value=0); t = t.div(t.sum(1), axis=0)
    L.append("\n_Şekil → bir sonraki pencerenin en olası şekli (araştırma coin'leri, tüm dönem):_ " + " · ".join(f"{SH[s].split(' ')[0]} → {SH[int(t.loc[s].idxmax())].split(' ')[0]} %{100 * t.loc[s].max():.0f}" for s in t.index) + "\n")
# ---- etken keşifleri ----
def tablo(m):
    d = T1[m]; tot = d.groupby(["W", "etken", "dilim"]).n.sum(); base = d[d.etken == "saat"].groupby(["W", "sh"]).n.sum() / d[d.etken == "saat"].groupby("W").n.sum()
    x = d.groupby(["W", "etken", "dilim", "sh"]).n.sum().reset_index(); x["p"] = x.n / tot.reindex(pd.MultiIndex.from_frame(x[["W", "etken", "dilim"]])).values
    x["lift"] = x.p / base.reindex(pd.MultiIndex.from_frame(x[["W", "sh"]])).values; return x.set_index(["W", "etken", "dilim", "sh"])
K, A_, B_ = tablo(GR["kesif"]), tablo(GR["A"]), tablo(GR["B"])
J = K.join(A_[["n", "lift"]], rsuffix="_A").join(B_[["n", "lift"]], rsuffix="_B").reset_index(); J = J[J.dilim >= 0]
ntest = len(J); yuk = (J.lift >= 1.3) & (J.lift_A >= 1.15) & (J.lift_B >= 1.15); dus = (J.lift <= 0.77) & (J.lift_A <= 0.87) & (J.lift_B <= 0.87)
KE = J[(J.n >= 2000) & (J.n_A >= 1000) & (J.n_B >= 1000) & (yuk | dus)].copy(); KE["guc"] = np.abs(np.log(KE[["lift", "lift_A", "lift_B"]])).min(1)
L.append(f"## Etken keşifleri — {len(KE)} / {ntest} deneme şartları geçti (keşifte lift ≥ 1,3 / ≤ 0,77, doğrulama A ve B'de aynı yönde ≥ 1,15 / ≤ 0,87)")
for W in (1, 4, 8, 24):
    k = KE[KE.W == W].sort_values("guc", ascending=False)
    L.append(f"\n### {W} saat — {len(k)} keşif (en güçlü 25; lift = o koşulda şeklin normale göre kaç kat sık görüldüğü)")
    L.append("| Koşul (pencere başında) | Şekil | keşif lift (n) | 2025+ lift | dokunulmamış lift |"); L.append("|---|---|---|---|---|")
    for _, r in k.head(25).iterrows(): L.append(f"| {ad(r.etken, r.dilim)} | {SH[int(r.sh)]} | ×{r.lift:.2f} ({int(r.n):,}) | ×{r.lift_A:.2f} | ×{r.lift_B:.2f} |")
KE.to_csv("sekil_kesifler.csv", index=False)
open("sekil_sonuc.md", "w").write("\n".join(L) + "\n"); print("\n".join(L[:80]))
