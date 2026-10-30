# btcneden.py — PROTOKOL_btcneden.md analiz: A (ne oldu) · B (öncüler) · C (kurallar) → btcneden_sonuc.md
import json, time, itertools, numpy as np, pandas as pd
T0 = time.time(); out = []
def yaz(s=""): out.append(s); print(s, flush=True)
H = pd.read_parquet("btcneden_saat.parquet").set_index("t").sort_index(); GD = pd.read_parquet("btcneden_gun.parquet").set_index("t").sort_index()
DG = pd.read_parquet("btcneden_dogrula.parquet")
MT = json.load(open("makro_tarih.json"))
OLAYG = set(pd.to_datetime(MT["fomc"]).strftime("%Y-%m-%d")) | set(pd.to_datetime(MT["cpi"]).strftime("%Y-%m-%d"))
SON = pd.Timestamp("2026-10-28", tz="UTC")
DON = [("K 2022–23", "2022-01-01", "2024-01-01"), ("C1 2024", "2024-01-01", "2025-01-01"), ("C2 2025–26", "2025-01-01", "2026-10-28")]
def donem(ix):
    ix = pd.DatetimeIndex(ix); d = np.full(len(ix), None, object)
    for ad, a, b in DON: d[(ix >= pd.Timestamp(a, tz="UTC")) & (ix < pd.Timestamp(b, tz="UTC"))] = ad
    return d
def zprev(s, n, mn=None):                                                                   # z: önceki n gözleme göre (NaN'ler atlanır)
    x = s.dropna(); m = x.rolling(n, min_periods=mn or n // 2).mean().shift(1); sd = x.rolling(n, min_periods=mn or n // 2).std().shift(1)
    return ((x - m) / sd).reindex(s.index)
# ---------------- saatlik türetilmiş ----------------
H["fon"] = H.fon.ffill(); H["p"] = H.cb_c / H.s_c - 1
H["f_al"], H["s_al"] = H.f_tbqv, H.s_tbqv
lc = np.log(H.f_c); H["lr"] = lc.diff()
# ---------------- günlük ----------------
g = H.groupby(H.index.floor("D"))
D = pd.DataFrame({"c": g.f_c.last(), "h": g.f_h.max(), "l": g.f_l.min(), "fqv": g.f_qv.sum(), "fal": g.f_al.sum(), "sqv": g.s_qv.sum(), "sal": g.s_al.sum(),
                  "p": g.p.mean(), "oi": g.oi.last(), "dvol": g.dvol.last(), "top_ls": g.top_ls.last(), "ls": g.ls.last()})
oih = H.oi.pct_change(fill_method=None); D["tasfiye"] = (oih <= -0.015).groupby(H.index.floor("D")).sum()
FP = H.fon.where(H.index.hour % 8 == 0); D["fon_gun"] = FP.groupby(H.index.floor("D")).mean()
D = D[D.index < SON]
D["r"] = np.log(D.c / D.c.shift(1)); D["sig"] = D.r.rolling(60, min_periods=40).std().shift(1)
D["dus"] = (D.r <= -2 * D.sig) & (D.r <= np.log(0.97)); D["yuk"] = (D.r >= 2 * D.sig) & (D.r >= np.log(1.03))
D["f_imb"] = (2 * D.fal - D.fqv) / D.fqv; D["s_imb"] = (2 * D.sal - D.sqv) / D.sqv
D["prim_deg"] = D.p - D.p.shift(1); D["oi_deg"] = D.oi / D.oi.shift(1) - 1; D["dvol_deg"] = D.dvol - D.dvol.shift(1)
M = GD.reindex(D.index)
for a in ("nasdaq", "sp500", "dxy", "altin", "vix"):
    s = GD[a].dropna(); D[a + "_r"] = np.log(s / s.shift(1)).reindex(D.index)
s = GD.faiz10.dropna(); D["faiz_d"] = (100 * (s - s.shift(1))).reindex(D.index)              # baz puan
D["etf"] = GD.etf.reindex(D.index) if "etf" in GD else np.nan
st = GD.stabil.dropna() if "stabil" in GD else pd.Series(dtype=float)
D["stabil_deg"] = (st.shift(-1) / st - 1).reindex(D.index) if len(st) else np.nan               # D 00:00 → D+1 00:00
D["net_giris"] = (GD.borsa_giris - GD.borsa_cikis).reindex(D.index) if "borsa_giris" in GD else np.nan
D["olay"] = D.index.strftime("%Y-%m-%d").isin(OLAYG); D["haftasonu"] = D.index.dayofweek >= 5
D["don"] = donem(D.index)
Z = {}
for c, n in (("nasdaq_r", 90), ("dxy_r", 90), ("vix_r", 90), ("faiz_d", 90), ("altin_r", 90), ("prim_deg", 90), ("f_imb", 90), ("s_imb", 90), ("net_giris", 90), ("stabil_deg", 90), ("dvol_deg", 90), ("etf", 60), ("oi_deg", 90)):
    Z[c] = zprev(D[c], n, 30 if c == "etf" else None)
Z = pd.DataFrame(Z)
yaz("# ₿ BTC neden düşüyor, neden yükseliyor? — PROTOKOL_btcneden.md")
yaz(f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · BTC saatlik {H.index.min():%Y-%m-%d} → {H.index.max():%Y-%m-%d} · dolu: Coinbase %{100 * H.cb_c.notna().mean():.0f}, açık poz. %{100 * H.oi.notna().mean():.0f}, DVOL %{100 * H.dvol.notna().mean():.0f} · günlük: "
    + ", ".join(f"{c} {GD[c].notna().sum()}" for c in GD.columns) + "_\n")
EV = D[D.don.notna()]
yaz("## Olay sayıları (büyük gün: |getiri| ≥ 2σ ve ≥ %3)")
yaz("| dönem | gün | büyük düşüş | büyük yükseliş |"); yaz("|---|---|---|---|")
for ad, _, _ in DON:
    x = EV[EV.don == ad]; yaz(f"| {ad} | {len(x)} | {int(x.dus.sum())} | {int(x.yuk.sum())} |")
# ================= A1 =================
yaz("\n## A1 — BTC'nin günlük hareketinin ne kadarı neyle birlikte oluyor? (aynı gün · açıklama, tahmin değil)")
GR = {"🏛️ Wall Street (Nasdaq, VIX)": ["nasdaq_r", "vix_r"], "💵 Dolar/faiz/altın": ["dxy_r", "faiz_d", "altin_r"], "🇺🇸 ABD primi (Coinbase)": ["prim_deg"],
      "🪙 Zincir/likidite (borsa akışı, stablecoin)": ["net_giris", "stabil_deg"], "📈 Vadeli (agresif emir, açık poz., tasfiye)": ["f_imb", "oi_deg", "tasfiye"],
      "🛒 Spot agresif emir": ["s_imb"], "😨 Opsiyon korkusu (DVOL, yarı mekanik)": ["dvol_deg"]}
def r2(X, y):
    X = np.column_stack([np.ones(len(y)), X]); b, *_ = np.linalg.lstsq(X, y, rcond=None); e = y - X @ b; return 1 - e.var() / y.var()
def a1(sub, gruplar, baslik):
    cols = sum(gruplar.values(), []); x = sub.dropna(subset=cols + ["r"])
    if len(x) < 60: yaz(f"- {baslik}: yetersiz veri ({len(x)})"); return
    Xs = (x[cols] - x[cols].mean()) / x[cols].std(); y = x.r.values; full = r2(Xs.values, y)
    yaz(f"\n**{baslik}** — {len(x)} gün · tüm faktörler birlikte R² = **%{100 * full:.0f}**")
    yaz("| grup | tek başına | grup çıkarılınca kaybolan |"); yaz("|---|---|---|")
    for gad, gc in gruplar.items():
        tek = r2(Xs[gc].values, y); kalan = [c for c in cols if c not in gc]; kay = full - (r2(Xs[kalan].values, y) if kalan else 0)
        yaz(f"| {gad} | %{100 * tek:.0f} | %{100 * kay:.1f} |")
    return full
DIS = {k: v for k, v in GR.items() if k.split()[0] in ("🏛️", "💵", "🇺🇸", "🪙")}
for ad, _, _ in DON:
    sub = EV[(EV.don == ad) & ~EV.haftasonu]
    a1(sub, GR, f"{ad} · ABD işlem günleri · tüm gruplar")
    a1(sub, DIS, f"{ad} · yalnız DIŞ sebepler (kripto içi emir akışı hariç)")
for ad in ("C1 2024", "C2 2025–26"):
    sub = EV[(EV.don == ad) & ~EV.haftasonu]; g2 = dict(DIS); g2["🏦 ETF akışı"] = ["etf"]; a1(sub, g2, f"{ad} · dış sebepler + ETF")
for ad, _, _ in DON:
    sub = EV[EV.don == ad]; g3 = {k: v for k, v in GR.items() if k.split()[0] in ("🇺🇸", "🪙", "📈", "🛒", "😨")}; a1(sub, g3, f"{ad} · TÜM günler (hafta sonu dahil) · kripto içi")
# ================= A2 =================
yaz("\n## A2 — Büyük günlerde faktörler (aşırı = önceki 90 güne göre |z| ≥ 1,5)")
yaz("_hücre: büyük düşüş günlerinde % (z ≤ −1,5 / z ≥ +1,5) ‖ büyük yükseliş günlerinde % ‖ sıradan günlerde % · tüm dönemler_")
yaz("| faktör | düşüş günü | yükseliş günü | sıradan gün |"); yaz("|---|---|---|---|")
AD = {"nasdaq_r": "Nasdaq getirisi", "vix_r": "VIX", "dxy_r": "Dolar endeksi", "faiz_d": "ABD 10 y faiz", "altin_r": "Altın", "prim_deg": "Coinbase primi değişimi", "etf": "ETF akışı",
      "f_imb": "Vadeli agresif alıcı−satıcı", "s_imb": "Spot agresif alıcı−satıcı", "oi_deg": "Açık pozisyon değişimi", "net_giris": "Borsalara net BTC girişi", "stabil_deg": "Stablecoin arzı değişimi", "dvol_deg": "DVOL (opsiyon korkusu)"}
ZE = Z.loc[EV.index]; nor = ~(EV.dus | EV.yuk)
def pz(m, c):
    z = ZE.loc[m.values, c].dropna(); return f"%{100 * (z <= -1.5).mean():.0f} / %{100 * (z >= 1.5).mean():.0f} (n {len(z)})" if len(z) else "—"
for c in AD: yaz(f"| {AD[c]} | {pz(EV.dus, c)} | {pz(EV.yuk, c)} | {pz(nor, c)} |")
yaz("\n_medyanlar (ham değer):_")
yaz("| faktör | düşüş günü | yükseliş günü | sıradan gün |"); yaz("|---|---|---|---|")
for c, f in (("r", 100), ("nasdaq_r", 100), ("dxy_r", 100), ("faiz_d", 1), ("prim_deg", 1e4), ("etf", 1), ("f_imb", 100), ("s_imb", 100), ("oi_deg", 100), ("tasfiye", 1), ("net_giris", 1), ("dvol_deg", 1)):
    yaz(f"| {AD.get(c, 'BTC getirisi %')}{' (baz puan)' if c == 'prim_deg' else ''}{' (milyon $)' if c == 'etf' else ''}{' (saat sayısı, ≥%1,5 düşüş)' if c == 'tasfiye' else ''} | " + " | ".join(f"{f * EV.loc[m, c].median():+.2f}" for m in (EV.dus, EV.yuk, nor)) + " |")
# ================= A3 =================
yaz("\n## A3 — Her büyük güne sebep etiketi (birden çok olabilir)")
def etiket(t, yon):
    z = Z.loc[t]; e = []; d = D.loc[t]
    if (not d.haftasonu) and ((yon * z.nasdaq_r >= 1.5) or (-yon * z.dxy_r >= 1.5) or d.olay): e.append("🏛️")
    if (yon * z.prim_deg >= 1.5) or (yon * z.etf >= 1.5): e.append("🇺🇸")
    if d.oi_deg <= -0.05: e.append("💥")
    if d.oi_deg >= 0.05: e.append("🎰")
    if -yon * z.net_giris >= 1.5: e.append("🪙")
    return e or ["❓"]
ETK = ["🏛️", "🇺🇸", "💥", "🎰", "🪙", "❓"]
yaz("_🏛️ Wall Street/makro (Nasdaq aynı yön, dolar ters yön, FOMC/CPI günü) · 🇺🇸 ABD spot talebi (Coinbase primi, ETF) · 💥 kaldıraç tasfiyesi (açık poz. ≤ −%5) · 🎰 yeni kaldıraç (açık poz. ≥ +%5) · 🪙 borsa akışı · ❓ ölçülen sebep yok_\n")
E = []
for t in EV.index[EV.dus | EV.yuk]:
    yon = -1 if EV.loc[t, "dus"] else 1; E.append(dict(t=t, yon=yon, r=EV.loc[t, "r"], e=etiket(t, yon), yil=t.year))
E = pd.DataFrame(E)
for yon, ad in ((-1, "BÜYÜK DÜŞÜŞLER"), (1, "BÜYÜK YÜKSELİŞLER")):
    x = E[E.yon == yon]; yaz(f"**{ad}** (gün sayısı; etiket payı %)"); yaz("| yıl | gün | " + " | ".join(ETK) + " |"); yaz("|---|---|" + "---|" * len(ETK))
    for yil, gx in list(x.groupby("yil")) + [("hepsi", x)]:
        yaz(f"| {yil} | {len(gx)} | " + " | ".join(f"%{100 * gx.e.apply(lambda l: k in l).mean():.0f}" for k in ETK) + " |")
    yaz("")
def liste(yon, n=25):
    x = E[E.yon == yon].assign(a=lambda d: d.r.abs()).sort_values("a", ascending=False).head(n)
    yaz("| gün | BTC | etiket | Nasdaq | dolar | prim Δ (bp) | ETF (m$) | açık poz. | tasfiye saat | vadeli/spot agresif | borsa giriş z |"); yaz("|---|---|---|---|---|---|---|---|---|---|---|")
    for r_ in x.itertuples():
        d = D.loc[r_.t]; z = Z.loc[r_.t]
        f = lambda v, k=100, p=1: "—" if pd.isna(v) else f"{k * v:+.{p}f}"
        yaz(f"| {r_.t:%Y-%m-%d %a} | {100 * (np.exp(r_.r) - 1):+.1f}% | {' '.join(r_.e)} | {f(d.nasdaq_r)}% | {f(d.dxy_r, 100, 2)}% | {f(d.prim_deg, 1e4, 0)} | {f(d.etf, 1, 0)} | {f(d.oi_deg)}% | {int(d.tasfiye)} | {f(d.f_imb, 100, 1)} / {f(d.s_imb, 100, 1)} | {f(z.net_giris, 1, 1)} |")
yaz("### En büyük 25 düşüş günü"); liste(-1); yaz("\n### En büyük 25 yükseliş günü"); liste(1)
E.assign(e=E.e.apply(" ".join)).to_csv("btcneden_olaylar.csv", index=False)
# ================= A4 =================
yaz("\n## A4 — 4 saatlik büyük hareketler: kim başlattı, ne zaman oluyor?")
hh = H.index.floor("4h")
g4 = H.groupby(hh)
B4 = pd.DataFrame({"o": g4.f_o.first(), "c": g4.f_c.last(), "fqv": g4.f_qv.sum(), "fal": g4.f_al.sum(), "sqv": g4.s_qv.sum(), "sal": g4.s_al.sum(), "p0": g4.p.first(), "p1": g4.p.last(), "oi1": g4.oi.last()})
B4 = B4[B4.index < SON]; B4["r"] = np.log(B4.c / B4.c.shift(1)); B4["sig"] = B4.r.rolling(180, min_periods=120).std().shift(1)
B4["dus"] = (B4.r <= -2.5 * B4.sig) & (B4.r <= np.log(1 - 0.015)); B4["yuk"] = (B4.r >= 2.5 * B4.sig) & (B4.r >= np.log(1.015))
B4["f_imb"] = (2 * B4.fal - B4.fqv) / B4.fqv; B4["s_imb"] = (2 * B4.sal - B4.sqv) / B4.sqv; B4["prim_d"] = B4.p1 - B4.p1.shift(1)
B4["oi_d"] = B4.oi1 / B4.oi1.shift(1) - 1; B4["don"] = donem(B4.index)
for c in ("f_imb", "s_imb", "prim_d", "oi_d"): B4["z_" + c] = zprev(B4[c], 180)
# ilk saat: hangi akış en aşırı (hareket yönünde)
Hall = H.copy(); Hall["fi"] = (2 * Hall.f_al - Hall.f_qv) / Hall.f_qv; Hall["si"] = (2 * Hall.s_al - Hall.s_qv) / Hall.s_qv; Hall["pd"] = Hall.p.diff()
zf, zs, zp = zprev(Hall.fi, 720), zprev(Hall.si, 720), zprev(Hall.pd, 720)
B4["z1_f"], B4["z1_s"], B4["z1_p"] = zf.reindex(B4.index).values, zs.reindex(B4.index).values, zp.reindex(B4.index).values
X4 = B4[B4.don.notna()]
for yon, kol, ad in ((-1, "dus", "düşüş"), (1, "yuk", "yükseliş")):
    x = X4[X4[kol]]; kk = x[["z1_f", "z1_s", "z1_p"]].mul(yon).dropna()
    lid = kk.idxmax(axis=1).map({"z1_f": "vadeli", "z1_s": "spot", "z1_p": "ABD (Coinbase)"}); nn = X4[["z1_f", "z1_s", "z1_p"]].mul(yon).dropna().idxmax(axis=1).map({"z1_f": "vadeli", "z1_s": "spot", "z1_p": "ABD (Coinbase)"})
    yaz(f"\n**Büyük 4 s {ad}: {len(x)} olay** (K {int((x.don == 'K 2022–23').sum())} · C1 {int((x.don == 'C1 2024').sum())} · C2 {int((x.don == 'C2 2025–26').sum())})")
    yaz(f"- İlk saatte en aşırı (hareket yönünde) akış: " + " · ".join(f"{k} %{100 * v:.0f}" for k, v in lid.value_counts(normalize=True).items()) + f" ‖ tüm 4 s bloklarında: " + " · ".join(f"{k} %{100 * v:.0f}" for k, v in nn.value_counts(normalize=True).items()))
    for c, ad2 in (("z_f_imb", "vadeli agresif"), ("z_s_imb", "spot agresif"), ("z_prim_d", "Coinbase primi Δ"), ("z_oi_d", "açık poz. Δ")):
        v = x[c].dropna(); yaz(f"- {ad2}: medyan z {v.median():+.2f} · aynı yönde |z| ≥ 1,5: %{100 * ((yon * v) >= 1.5).mean():.0f}" if c != "z_oi_d" else f"- {ad2}: medyan z {v.median():+.2f} · z ≤ −1,5 (tasfiye): %{100 * (v <= -1.5).mean():.0f} · z ≥ +1,5: %{100 * (v >= 1.5).mean():.0f}")
    sa = x.index.hour.value_counts().sort_index(); yaz("- Başladığı 4 s blok (UTC → TR +3): " + " · ".join(f"{h:02d}–{h + 4:02d} %{100 * sa.get(h, 0) / len(x):.0f}" for h in range(0, 24, 4)) + " (eşit dağılım %17)")
    gn = x.index.dayofweek.value_counts().sort_index(); tg = X4.index.dayofweek.value_counts().sort_index()
    yaz("- Gün (olay oranı / ortalama): " + " · ".join(f"{a} ×{(gn.get(i, 0) / tg[i]) / (len(x) / len(X4)):.2f}" for i, a in enumerate(["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"])))
# ================= B1 =================
yaz("\n## B1 — Önceden belli miydi? (D−1 sonunda bilinen durum → D…D+2 içinde büyük gün)")
cD = D.c; hi = D.h
B = pd.DataFrame(index=D.index)
fon_g = H.fon.where(H.index.hour % 8 == 0).dropna(); fon_g = fon_g[~fon_g.index.duplicated()]
f3 = fon_g.rolling("3D").mean(); B["fon3"] = f3.reindex(D.index - pd.Timedelta(seconds=1), method="ffill").values
B["oi7"] = (D.oi / D.oi.shift(7) - 1).shift(1); B["top_ls"] = D.top_ls.shift(1); B["ls"] = D.ls.shift(1)
B["fimb3"] = ((2 * D.fal.rolling(3).sum() - D.fqv.rolling(3).sum()) / D.fqv.rolling(3).sum()).shift(1)
B["simb3"] = ((2 * D.sal.rolling(3).sum() - D.sqv.rolling(3).sum()) / D.sqv.rolling(3).sum()).shift(1)
B["prim3"] = D.p.rolling(3).mean().shift(1); B["prim_d3"] = (D.p - D.p.shift(3)).shift(1)
B["dvol"] = D.dvol.shift(1); B["dvol3"] = (D.dvol / D.dvol.shift(3) - 1).shift(1)
B["sikisma"] = (D.r.rolling(7).std() / D.r.rolling(60).std()).shift(1); B["zirve30"] = (cD / hi.rolling(30).max() - 1).shift(1)
B["r7"] = (cD / cD.shift(7) - 1).shift(1)
B["stabil7"] = (st / st.shift(7) - 1).reindex(D.index) if len(st) else np.nan                  # D 00:00 anlık görüntü (bilinen)
ng = (GD.borsa_giris - GD.borsa_cikis).reindex(D.index) if "borsa_giris" in GD else pd.Series(np.nan, D.index)
n7 = ng.rolling(7).sum(); B["borsa7z"] = ((n7 - n7.rolling(365, min_periods=200).mean().shift(1)) / n7.rolling(365, min_periods=200).std().shift(1)).shift(2)   # yayın gecikmesi: D−2
if "etf" in GD:
    e = GD.etf.dropna(); e3 = e.rolling(3).sum(); B["etf3"] = e3.reindex(D.index - pd.Timedelta(days=2), method="ffill").values   # ≤ D−2 günü (temkinli)
else: B["etf3"] = np.nan
B["korku"] = GD.korku.reindex(D.index) if "korku" in GD else np.nan
def son_islem(sr, f):                                                                        # D'den önceki son ABD işlem günü değeri
    s_ = sr.dropna(); v = f(s_); return v.reindex(D.index - pd.Timedelta(days=1), method="ffill").values
B["nasdaq5"] = son_islem(GD.nasdaq, lambda s_: s_ / s_.shift(5) - 1); B["dxy5"] = son_islem(GD.dxy, lambda s_: s_ / s_.shift(5) - 1)
B["faiz5"] = son_islem(GD.faiz10, lambda s_: s_ - s_.shift(5)); B["vix"] = son_islem(GD.vix, lambda s_: s_)
B["olay"] = D.olay.astype(float); B["haftasonu"] = D.haftasonu.astype(float)
B["hacim7"] = (D.fqv.rolling(7).sum() / D.sqv.rolling(7).sum()).shift(1)
BAD = {"fon3": "fonlama 3 g ort.", "oi7": "açık poz. 7 g değişim", "top_ls": "büyük oyuncu L/S", "ls": "hesap L/S (kalabalık)", "fimb3": "vadeli agresif 3 g", "simb3": "spot agresif 3 g",
       "prim3": "Coinbase primi 3 g", "prim_d3": "Coinbase primi 3 g değişim", "dvol": "DVOL seviye", "dvol3": "DVOL 3 g değişim", "sikisma": "oynaklık 7g/60g", "zirve30": "30 g zirveye uzaklık",
       "r7": "7 g getiri", "stabil7": "stablecoin arzı 7 g", "borsa7z": "borsa net giriş 7 g z", "etf3": "ETF 3 g akış", "korku": "korku endeksi", "nasdaq5": "Nasdaq 5 g", "dxy5": "dolar 5 g",
       "faiz5": "10 y faiz 5 g", "vix": "VIX", "olay": "FOMC/CPI günü", "haftasonu": "hafta sonu", "hacim7": "vadeli/spot hacim 7 g"}
YD = pd.DataFrame({"dus3": D.dus.astype(float).rolling(3).max().shift(-2), "yuk3": D.yuk.astype(float).rolling(3).max().shift(-2)}, index=D.index)
YD["r3"] = np.log(D.c.shift(-2) / D.c.shift(1))                                             # D açılışı (≈ D−1 kapanışı) → D+2 kapanışı
DONB = donem(B.index)
def esik(v, s):
    ilk = "C1 2024" if v == "etf3" else "K 2022–23"; x = s[DONB == ilk].dropna()
    return (x.quantile(0.2), x.quantile(0.8)) if len(x) > 50 else (np.nan, np.nan)
def kovalar(v, s):
    if v in ("olay", "haftasonu"): return {"=1": s == 1}
    a, b = esik(v, s); return {"alt %20": s <= a, "üst %20": s > b}
def b1_test(Bx, kayit=False):
    gecen = []; tablo = []
    for v in BAD:
        s = Bx[v]
        for kad, m in kovalar(v, s).items():
            for hd in ("dus3", "yuk3"):
                ok = True; hs = []
                for ad, _, _ in DON:
                    if v == "etf3" and ad.startswith("K"): hs.append("—"); continue
                    sel = (DONB == ad) & s.notna().values & YD[hd].notna().values
                    if sel.sum() == 0: ok = False; hs.append("yok"); continue
                    base = YD[hd].values[sel].mean(); mm = sel & m.fillna(False).values; n_ev = YD[hd].values[mm].sum(); rate = YD[hd].values[mm].mean() if mm.sum() else np.nan
                    lift = rate / base if base > 0 else np.nan; hs.append(f"×{lift:.2f} ({int(n_ev)}/{int(mm.sum())})")
                    if not (lift >= 1.5 and n_ev >= 8): ok = False
                tablo.append((v, kad, hd, hs, ok))
                if ok: gecen.append((v, kad, hd))
    return gecen, tablo
GEC, TAB = b1_test(B)
yaz("_hücre: kaldıraç (lift) = o dilimde 3 gün içinde büyük gün olasılığı / dönem tabanı · (olay / gün). Şart: her dönemde ×1,5+ ve ≥ 8 olay._\n")
for ad, _, _ in DON:
    sel = DONB == ad; yaz(f"- taban {ad}: 3 gün içinde büyük düşüş %{100 * YD.dus3[sel].mean():.0f} · büyük yükseliş %{100 * YD.yuk3[sel].mean():.0f}")
yaz("\n| durum | dilim | hedef | K 2022–23 | C1 2024 | C2 2025–26 | geçti |"); yaz("|---|---|---|---|---|---|---|")
for v, kad, hd, hs, ok in TAB: yaz(f"| {BAD[v]} | {kad} | {'düşüş' if hd == 'dus3' else 'yükseliş'} | " + " | ".join(hs) + f" | {'✅' if ok else ''} |")
rng = np.random.default_rng(11); PL = []
for k in range(50):
    Bp = B.copy()
    for v in BAD:
        if v in ("olay", "haftasonu"): continue
        sh = int(rng.integers(90, len(B) - 90)); Bp[v] = np.roll(B[v].values, sh)
    PL.append(len(b1_test(Bp)[0]))
yaz(f"\n**B1 geçen: {len(GEC)}** · plasebo (50 rastgele kaydırma) ortalama {np.mean(PL):.1f}, en çok {max(PL)} · " + ("geçenler: " + "; ".join(f"{BAD[v]} {k} → {'düşüş' if h == 'dus3' else 'yükseliş'}" for v, k, h in GEC) if GEC else "geçen yok"))
yaz("\n_bilgi — her durumun en alt / en üst diliminde sonraki 3 gün ortalama BTC getirisi % (K · C1 · C2):_")
for v in BAD:
    s = B[v]; ks = kovalar(v, s); parts = []
    for kad, m in ks.items():
        parts.append(f"{kad}: " + " · ".join(f"{100 * YD.r3[(DONB == ad) & m.fillna(False).values].mean():+.2f}" for ad, _, _ in DON))
    yaz(f"- {BAD[v]} — " + " ‖ ".join(parts))
# ================= B2 =================
yaz("\n## B2 — 4 saatlik: saat sonunda bilinen durum → sonraki 4 saatte büyük hareket")
X = pd.DataFrame(index=H.index)
fi = (2 * H.f_al - H.f_qv); si = (2 * H.s_al - H.s_qv)
p24 = H.p.rolling(24).mean(); X["primz"] = (p24 - p24.rolling(720, min_periods=360).mean()) / p24.rolling(720, min_periods=360).std()
X["prim4"] = H.p - H.p.shift(4); X["fimb4"] = fi.rolling(4).sum() / H.f_qv.rolling(4).sum(); X["simb4"] = si.rolling(4).sum() / H.s_qv.rolling(4).sum()
X["oi4"] = H.oi / H.oi.shift(4) - 1; X["oi24"] = H.oi / H.oi.shift(24) - 1; X["fon"] = H.fon; X["dvol4"] = H.dvol - H.dvol.shift(4)
X["vr"] = H.lr.rolling(24).std() / H.lr.rolling(720).std(); X["r24"] = lc - lc.shift(24)
r4 = lc.shift(-4) - lc; s4 = r4.rolling(720, min_periods=480).std().shift(4)
YH = pd.DataFrame({"dus": ((r4 <= -2.5 * s4) & (r4 <= np.log(0.985))).astype(float).where(r4.notna()), "yuk": ((r4 >= 2.5 * s4) & (r4 >= np.log(1.015))).astype(float).where(r4.notna())})
blok = ((H.index.hour + 1) % 24) // 4
for b_ in range(6): X[f"saat{b_}"] = (blok == b_).astype(float)
XAD = {"primz": "Coinbase primi z (24 s)", "prim4": "prim 4 s değişim", "fimb4": "vadeli agresif 4 s", "simb4": "spot agresif 4 s", "oi4": "açık poz. 4 s", "oi24": "açık poz. 24 s",
       "fon": "fonlama", "dvol4": "DVOL 4 s değişim", "vr": "oynaklık 24s/720s", "r24": "24 s getiri"} | {f"saat{b_}": f"sonraki 4 s {4 * b_:02d}–{4 * b_ + 4:02d} UTC" for b_ in range(6)}
X = X[X.index < SON - pd.Timedelta(hours=5)]; YH = YH.loc[X.index]; DONH = donem(X.index)
def b2_test(Xx):
    gecen, tab = [], []
    for v in XAD:
        s = Xx[v]
        if v.startswith("saat"): ks = {"=1": s == 1}
        else:
            x = s[DONH == "K 2022–23"].dropna(); a, b = x.quantile(0.2), x.quantile(0.8); ks = {"alt %20": s <= a, "üst %20": s > b}
        for kad, m in ks.items():
            for hd in ("dus", "yuk"):
                ok = True; hs = []
                for ad, _, _ in DON:
                    sel = (DONH == ad) & s.notna().values & YH[hd].notna().values; base = YH[hd].values[sel].mean(); mm = sel & m.fillna(False).values
                    n_ev = YH[hd].values[mm].sum(); lift = YH[hd].values[mm].mean() / base if base > 0 and mm.sum() else np.nan
                    hs.append(f"×{lift:.2f} ({int(n_ev)})")
                    if not (lift >= 1.5 and n_ev >= 30): ok = False
                tab.append((v, kad, hd, hs, ok))
                if ok: gecen.append((v, kad, hd))
    return gecen, tab
GEC2, TAB2 = b2_test(X)
for ad, _, _ in DON:
    sel = DONH == ad; yaz(f"- taban {ad}: bir saatten sonraki 4 s içinde büyük düşüş %{100 * YH.dus[sel].mean():.2f} · büyük yükseliş %{100 * YH.yuk[sel].mean():.2f}")
yaz("\n| durum | dilim | hedef | K | C1 | C2 | geçti |"); yaz("|---|---|---|---|---|---|---|")
for v, kad, hd, hs, ok in TAB2: yaz(f"| {XAD[v]} | {kad} | {'düşüş' if hd == 'dus' else 'yükseliş'} | " + " | ".join(hs) + f" | {'✅' if ok else ''} |")
PL2 = []
for k in range(20):
    Xp = X.copy()
    for v in XAD:
        if v.startswith("saat"): continue
        Xp[v] = np.roll(X[v].values, int(rng.integers(2160, len(X) - 2160)))
    PL2.append(len(b2_test(Xp)[0]))
yaz(f"\n**B2 geçen: {len(GEC2)}** · plasebo (20 kaydırma) ortalama {np.mean(PL2):.1f}, en çok {max(PL2)} · " + ("geçenler: " + "; ".join(f"{XAD[v]} {k} → {'düşüş' if h == 'dus' else 'yükseliş'}" for v, k, h in GEC2) if GEC2 else "geçen yok"))
# ================= C =================
yaz("\n## C — Tahmin kuralları (yalnız B'den geçenlerle)")
def islem(K, gir_ix, yon, T, stop, nsaat):                                                    # K: saatlik o,h,l,c,fon (ödeme saatlerinde) · gir_ix: giriş saati satırı
    o, h, l, c, fn = K.o.values, K.h.values, K.l.values, K.c.values, K.fonp.values
    Pe = o[gir_ix] * (1 + 0.001 * yon); tp = Pe * (1 + yon * T); sp = Pe * (1 - yon * stop) if stop else None; fon = 0.0
    son = min(gir_ix + nsaat, len(o)) - 1
    for j in range(gir_ix, son + 1):
        if j > gir_ix and not np.isnan(fn[j]): fon += fn[j]
        if sp is not None and ((yon == 1 and l[j] <= sp) or (yon == -1 and h[j] >= sp)): return yon * (sp / Pe - 1) - 0.001 - yon * fon, j
        if (yon == 1 and h[j] >= tp) or (yon == -1 and l[j] <= tp): return T - 0.0007 - yon * fon, j
    return yon * (c[son] / Pe - 1) - 0.001 - yon * fon, son
def kitap(hs):
    K = pd.DataFrame({"o": hs.f_o if "f_o" in hs else hs.o, "h": hs.f_h if "f_h" in hs else hs.h, "l": hs.f_l if "f_l" in hs else hs.l, "c": hs.f_c if "f_c" in hs else hs.c})
    fr = hs.fon.copy() if "f_o" not in hs else H.fon.where(H.index.hour % 8 == 0)
    K["fonp"] = fr.where(K.index.hour % 8 == 0); return K
KB = kitap(H); KD = {c: kitap(g.set_index("t").sort_index()) for c, g in DG.groupby("coin")}
for c_, g in DG.groupby("coin"):
    gg = g.set_index("t").sort_index(); KD[c_]["fonp"] = gg.fon.reindex(KD[c_].index)
def kural_sim(K, gunler, yon, T, stop, Hg):
    R = []; serbest = None; ix = K.index
    for d in gunler:
        if serbest is not None and d <= serbest: continue
        i = ix.searchsorted(d)
        if i >= len(ix) or ix[i] != d or i + Hg * 24 >= len(ix): continue
        net, j = islem(K, i, yon, T, stop, Hg * 24); R.append((d, net)); serbest = ix[j]
    return pd.DataFrame(R, columns=["t", "net"])
KOS = []
for v, kad, hd in GEC:
    m = kovalar(v, B[v])[kad].fillna(False); KOS.append((f"{BAD[v]} {kad}", m, -1 if hd == "dus3" else 1))
for (a1_, m1, y1), (a2_, m2, y2) in itertools.combinations(list(KOS), 2):
    if y1 == y2: KOS.append((f"{a1_} VE {a2_}", m1 & m2, y1))
if not KOS: yaz("B1'den geçen durum yok → günlük kural denenmedi.")
GECC = []
for ad_, m, yon in KOS:
    gun = B.index[m.values]
    for T, stop, Hg in itertools.product((0.03, 0.05), (None, 0.08), (3, 7)):
        R = kural_sim(KB, gun, yon, T, stop, Hg); R["don"] = donem(R.t); ok = True; hs = []
        for dad, _, _ in DON:
            x = R[R.don == dad]; hs.append(f"{len(x)} · %{100 * (x.net > 0).mean():.0f} · {100 * x.net.mean():+.2f}" if len(x) else "0")
            if not (len(x) >= 8 and (x.net > 0).mean() >= 0.70 and x.net.mean() >= 0.01): ok = False
        dg = []
        for c_, K in KD.items():
            Rc = kural_sim(K, [d for d in gun if d >= pd.Timestamp("2024-01-01", tz="UTC")], yon, T, stop, Hg); dg.append(f"{c_} {len(Rc)} · {100 * Rc.net.mean():+.2f}" if len(Rc) else f"{c_} 0")
            if not (len(Rc) and Rc.net.mean() > 0): ok = False
        yaz(f"- {'✅' if ok else '❌'} {ad_} → {'AL' if yon == 1 else 'SAT'} · 🎯%{100 * T:.0f} · stop {'yok' if stop is None else f'%{100 * stop:.0f}'} · {Hg} g: " + " | ".join(hs) + " ‖ " + " · ".join(dg))
        if ok: GECC.append(ad_)
if GEC2:
    yaz("\n_4 saatlik kurallar (giriş sonraki saat açılışı · 🎯 1σ4 · 4 s):_")
    for v, kad, hd in GEC2:
        s = X[v]
        if v.startswith("saat"): m = s == 1
        else:
            x = s[DONH == "K 2022–23"].dropna(); m = (s <= x.quantile(0.2)) if kad.startswith("alt") else (s > x.quantile(0.8))
        yon = -1 if hd == "dus" else 1; R = []; serbest = None
        for t in X.index[m.fillna(False).values]:
            if serbest is not None and t < serbest: continue
            i = KB.index.searchsorted(t) + 1
            if i + 4 >= len(KB): continue
            T = float(s4.iloc[i - 1]) if not np.isnan(s4.iloc[i - 1]) else 0.01
            net, j = islem(KB, i, yon, T, None, 4); R.append((t, net)); serbest = KB.index[j]
        R = pd.DataFrame(R, columns=["t", "net"]); R["don"] = donem(R.t); ok = True; hs = []
        for dad, _, _ in DON:
            x = R[R.don == dad]; hs.append(f"{len(x)} · %{100 * (x.net > 0).mean():.0f} · {100 * x.net.mean():+.2f}" if len(x) else "0")
            if not (len(x) >= 8 and (x.net > 0).mean() >= 0.70 and x.net.mean() >= 0.003): ok = False
        yaz(f"- {'✅' if ok else '❌'} {XAD[v]} {kad} → {'AL' if yon == 1 else 'SAT'}: " + " | ".join(hs)); GECC += [XAD[v]] if ok else []
yaz(f"\n**C sonucu: geçen kural {len(GECC)}**" + (": " + "; ".join(GECC) if GECC else ""))
yaz(f"\n_süre {time.time() - T0:.0f} sn_")
open("btcneden_sonuc.md", "w").write("\n".join(out) + "\n")
