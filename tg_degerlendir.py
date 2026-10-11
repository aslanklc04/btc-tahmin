# tg_degerlendir.py — Telegram'a gelen sinyalleri gerçek fiyatlarla karşılaştırır (son_fiyat.csv.gz, 1 dk Binance spot).
import sys, numpy as np, pandas as pd
from tg_ayristir import ayristir
S, P, B, I = ayristir(sys.argv[1:])
F = pd.read_csv("son_fiyat.csv.gz"); F["t"] = pd.to_datetime(F.t, unit="ms", utc=True)
D = {s.replace("USDT", ""): g.set_index("t").sort_index() for s, g in F.groupby("sym")}
SON = min(d.index[-1] for d in D.values()) + pd.Timedelta(minutes=1)
KOM = 0.0004                                                    # gidiş-dönüş maliyet (limit emir varsayımı)
def kapanis(c, T):                                              # T anındaki fiyat = T'den önceki dakikanın kapanışı
    d = D[c]; x = d.c[d.index < T]; return x.iloc[-1] if len(x) else np.nan
DF = pd.read_csv("/home/claude/main-wt/durum/defter_kayit.csv", parse_dates=["t"]).set_index("t")
L = []
def yaz(s=""): print(s); L.append(s)
# ---- 1) işlem sinyalleri
R = []
for _, s in S.iterrows():
    c = s.coin; et, H = s.et, s.H; bit = s.gonder + pd.Timedelta(hours=H)
    p0 = kapanis(c, et); pm = kapanis(c, et + pd.Timedelta(hours=H)) if et + pd.Timedelta(hours=H) <= SON else np.nan
    d = D[c]; w = d[(d.index >= s.gonder) & (d.index < s.gonder + pd.Timedelta(minutes=60))]
    if pd.notna(s.limit):
        doldu = (w.l.min() <= s.limit) if s.yon > 0 else (w.h.max() >= s.limit); giris = s.limit
    else:
        doldu = True; giris = d.o[d.index >= s.gonder + pd.Timedelta(minutes=1)].iloc[0]
    tamam = bit <= SON
    cik = kapanis(c, bit) if tamam else d.c.iloc[-1]
    yol = d[(d.index >= s.gonder) & (d.index < min(bit, SON))]
    kotu = (yol.l.min() / giris - 1) if s.yon > 0 else -(yol.h.max() / giris - 1)
    pr = s.prim
    if c == "BTC" and pr == "yok":
        z = DF.cb_z[DF.index <= et].iloc[-1] if (DF.index <= et).any() else np.nan
        pr = "⛔" if z <= -1 else "⚠️" if z <= 0 else "✅" if np.isfinite(z) else "yok"
    R.append(dict(zaman=(et + pd.Timedelta(hours=3)).strftime("%d.%m %H:%M"), coin=c, tur=s.tur, prim=pr, fiyat_kontrol=f"{100*(p0/s.fiyat-1):+.2f}%",
                  model=s.yon * (pm / p0 - 1) if np.isfinite(pm) else np.nan, doldu=doldu, net=(s.yon * (cik / giris - 1) - KOM) if doldu else np.nan,
                  bitti=tamam, en_kotu=kotu if doldu else np.nan))
R = pd.DataFrame(R)
pc = lambda x: f"{100*x:+.2f}%" if pd.notna(x) else "—"
yaz("## İşlem sinyalleri — tek tek\n```")
T = R.copy(); T["model"] = T.model.map(pc); T["net"] = T.net.map(pc); T["en_kotu"] = T.en_kotu.map(pc)
yaz(T.drop(columns=["fiyat_kontrol"]).to_string(index=False)); yaz("```")
yaz("fiyat kontrol (mesaj fiyatı vs veri): en büyük sapma " + max(R.fiyat_kontrol, key=lambda v: abs(float(v[:-1]))))
def ozet(g):
    m = g.model.dropna(); n = g.net.dropna()
    return pd.Series(dict(sinyal=len(g), tuttu=f"{int((m > 0).sum())}/{len(m)}", isabet=f"%{100*(m>0).mean():.0f}" if len(m) else "—", model_ort=pc(m.mean()) if len(m) else "—",
                          dolan=f"{int(g.doldu.sum())}/{len(g)}", net_ort=pc(n.mean()) if len(n) else "—", net_toplam=pc(n.sum()) if len(n) else "—", en_kotu=pc(g.en_kotu.min())))
yaz("\n## Türe göre\n```"); yaz(R.groupby("tur").apply(ozet).to_string()); yaz("```")
AL = R[R.tur.str.contains("🔻|⛓️") == False]
yaz("\n## Alış sinyalleri — Coinbase primi filtresine göre\n```"); yaz(AL.groupby("prim").apply(ozet).to_string()); yaz("```")
yaz("\n## Alış sinyalleri — coin'e göre\n```"); yaz(AL.groupby("coin").apply(ozet).to_string()); yaz("```")
# ---- 2) BTC saatlik yön tahminleri
P = P.drop_duplicates(["et", "coin", "H"]).copy()
P["son"] = [kapanis(c, e + pd.Timedelta(hours=int(h))) if e + pd.Timedelta(hours=int(h)) <= SON else np.nan for c, e, h in zip(P.coin, P.et, P.H)]
P["p0"] = [kapanis(c, e) for c, e in zip(P.coin, P.et)]
P["r"] = P.yon * (P.son / P.p0 - 1); P = P.dropna(subset=["r"])
yaz("\n## Mesajlardaki tüm yön tahminleri (1/4/8 saat, ufuk sonunda yön tuttu mu)\n```")
G = P.groupby(["coin", "H", "guc"]).apply(lambda g: pd.Series(dict(n=len(g), isabet=f"%{100*(g.r>0).mean():.0f}", ort=pc(g.r.mean())))).reset_index()
B_ = P[P.coin == "BTC"].groupby(["H", "guc"]).apply(lambda g: pd.Series(dict(n=len(g), isabet=f"%{100*(g.r>0).mean():.0f}", ort=pc(g.r.mean()))))
yaz("BTC:\n" + B_.to_string())
yaz("BTC yöne göre (Güçlü+Çok güçlü):\n" + P[(P.coin == "BTC") & (P.guc != "Zayıf")].groupby(["H", "yon"]).apply(lambda g: pd.Series(dict(n=len(g), isabet=f"%{100*(g.r>0).mean():.0f}", ort=pc(g.r.mean())))).to_string())
yaz("Coin'ler (hepsi birlikte):\n" + P[P.coin != "BTC"].groupby(["H", "guc"]).apply(lambda g: pd.Series(dict(n=len(g), isabet=f"%{100*(g.r>0).mean():.0f}", ort=pc(g.r.mean())))).to_string())
yaz("```")
# ---- 3) %80 aralık ve beklenen fiyat
I = I.drop_duplicates(["et", "coin", "H"]).copy()
I["son"] = [kapanis(c, e + pd.Timedelta(hours=int(h))) if e + pd.Timedelta(hours=int(h)) <= SON else np.nan for c, e, h in zip(I.coin, I.et, I.H)]
I = I.dropna(subset=["son"]); I["icinde"] = (I.son >= I.a) & (I.son <= I.b)
I["hata_bek"] = (I.son / I.bek - 1).abs(); I["hata_sabit"] = (I.son / I.fiyat - 1).abs()
yaz("\n## %80 aralık tuttu mu (ideal %80) ve 'beklenen fiyat' işe yarıyor mu\n```")
yaz(I.groupby(I.coin.eq("BTC").map({True: "BTC", False: "coin"})).apply(lambda g: pd.Series(dict(n=len(g), aralik_icinde=f"%{100*g.icinde.mean():.0f}",
     altinda=f"%{100*(g.son < g.a).mean():.0f}", ustunde=f"%{100*(g.son > g.b).mean():.0f}"))).to_string())
yaz(I.groupby("H").apply(lambda g: pd.Series(dict(n=len(g), aralik_icinde=f"%{100*g.icinde.mean():.0f}", bek_hata=pc(g.hata_bek.mean()), degismez_hata=pc(g.hata_sabit.mean()),
     bek_daha_iyi=f"%{100*(g.hata_bek < g.hata_sabit).mean():.0f}"))).to_string())
yaz("```")
# ---- 4) 🎯 hedef/stop
B = B.drop_duplicates(["et", "coin", "H"]).copy(); sonuc = []
for _, b in B.iterrows():
    bit = b.et + pd.Timedelta(hours=int(b.H))
    if bit > SON: sonuc.append("bitmedi"); continue
    d = D[b.coin]; y = d[(d.index >= b.et) & (d.index < bit)]
    th = y.index[y.h >= b.hedef]; ts = y.index[y.l <= b.stop]
    a1 = th[0] if len(th) else None; a2 = ts[0] if len(ts) else None
    sonuc.append("hiçbiri" if a1 is None and a2 is None else "HEDEF" if a2 is None or (a1 is not None and a1 < a2) else "STOP" if a1 is None or a2 < a1 else "aynı dk")
B["olan"] = sonuc; Bk = B[B.olan.isin(["HEDEF", "STOP"])]
yaz("\n## 🎯 'önce HEDEF / önce STOP' tahmini\n```")
yaz("olanlar: " + B.olan.value_counts().to_string().replace("\n", " · "))
yaz(Bk.groupby(["H", "guc"]).apply(lambda g: pd.Series(dict(n=len(g), dogru=f"%{100*(g.tahmin == g.olan).mean():.0f}", tahmin_hedef=int((g.tahmin == 'HEDEF').sum()), olan_hedef=int((g.olan == 'HEDEF').sum())))).to_string())
yaz(f"toplam doğru: {(Bk.tahmin == Bk.olan).sum()}/{len(Bk)} (%{100*(Bk.tahmin == Bk.olan).mean():.0f}) · hep 'STOP' deseydik: %{100*(Bk.olan == 'STOP').mean():.0f}")
yaz("```")
yaz(f"\n_Veri sonu: {(SON + pd.Timedelta(hours=3)):%d.%m %H:%M} TR · net = limit giriş, çıkış saatinde kapanış, %{100*KOM:.2f} maliyet düşülmüş, kaldıraçsız_")
open("tg_degerlendirme.md", "w").write("\n".join(L) + "\n")
R.to_csv("tg_sinyal_sonuc.csv", index=False)
