# yon_golge_param.py — gölge izleme için dondurulmuş parametreler (btcyon4 W4 · btcyon3 Z2 negatif uyumsuzluk + P) + Eylül–Ekim 2026 referans özellik/sinyal
import io, json, contextlib, numpy as np, pandas as pd
with contextlib.redirect_stdout(io.StringIO()): import btcyon4 as W
N = W.N; F, cols, y = W.F, W.cols, W.y
tr = (F.index < W.C1_END - pd.Timedelta(hours=25)) & y.notna().values & (F.index >= W.TS("2022-01-01"))
md = W.rf(F.loc[tr, cols], y[tr]); ptr = W.rp(md, F.loc[tr, cols]); q10, q90 = float(ptr.quantile(0.1)), float(ptr.quantile(0.9))
X = N.X; dn = N.donem(X.index); vthr = float(X.vr[dn == "K 2022–23"].quantile(0.7))
P = {"w4": {"cols": cols, "ort": md[0].tolist(), "std": md[1].tolist(), "katsayi": md[2].tolist(), "sabit": float(md[3]), "q10": q10, "q90": q90, "lam": 10.0,
            "egitim": "2022-01-01 → 2024-12-30 (K + C1), hedef: sonraki saat açılışı → 24 s sonu log getiri"},
     "negdiv": {"vthr": vthr, "tanim": "72 s yeni tepe (kapanış ≥ 72 s maks ve > 24–72 s önceki tepe) ve kümülatif vadeli agresif dengesizlik (2·alıcı−hacim) önceki tepedeki değerden düşük; P: oynaklık 24s/720s ≥ vthr veya sonraki saat 12–15 UTC"},
     "olusturma": pd.Timestamp.now(tz="UTC").isoformat()}
json.dump(P, open("yon_golge_param.json", "w"), indent=1, ensure_ascii=False)
a, b = W.TS("2026-09-01"), W.TS("2026-10-27")
R = F.loc[(F.index >= a) & (F.index < b), cols].copy(); R["skor"] = W.rp(md, R[cols]); R["vr"] = X.vr.reindex(R.index)
R["P"] = ((R.vr >= vthr) | ((((R.index.hour + 1) % 24) // 4) == 3)); R["sinyal_w4"] = np.where(R.skor >= q90, 1, np.where(R.skor <= q10, -1, 0))
R["sinyal_neg"] = np.where((R.negdiv == 1) & R.P, -1, 0)
R.rename_axis("t").reset_index().to_csv("yon_golge_referans.csv", index=False)
print(json.dumps(P, ensure_ascii=False)[:600]); print("referans", len(R), "W4 sinyal", int((R.sinyal_w4 != 0).sum()), "neg sinyal", int((R.sinyal_neg != 0).sum()))
