# tarama_rapor.py — coin taraması raporu: her coin'in sinyalleri, öz-denetim sonucu ve "BTC aynı saatte sinyal verirken" isabet
import os, glob, gzip, pickle, shutil, numpy as np, pandas as pd
from ortak import *
CANLI = ["ETHUSDT", "BNBUSDT", "DOGEUSDT"]                          # zaten canlı olanlar: yeniden eğitilmiş modelleri her durumda alınır
L = []
def yaz(s=""): print(s, flush=True); L.append(s)
MS = {}
for f in sorted(glob.glob("art/**/model_*.pkl.gz", recursive=True)):
    sym = os.path.basename(f)[6:-7]
    with gzip.open(f, "rb") as g: MS[sym] = (pickle.load(g), f)
EXB = pd.read_pickle(glob.glob("art/**/disa_BTCUSDT.pkl", recursive=True)[0]) if glob.glob("art/**/disa_BTCUSDT.pkl", recursive=True) else None
yaz(f"# 🪙 Coin taraması — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}")
yaz("Kural (önceden sabit): değerlendirme döneminde isabet ≥ %58, ≥ 50 sinyal, dönemin iki yarısında da ≥ %55 → bildirim AÇIK. Değerlendirme dönemi: 2024+ (yeni coin'lerde test başlangıcından beri).\n")
rows, secilen, ort = [], [], []
for sym, (M, f) in MS.items():
    if sym == "BTCUSDT": continue
    S = M["SIG"]; nm = sym.replace("USDT", ""); on = [k for k, v in S.items() if v["on"]]
    r = {"Coin": nm, "Değ. başlangıcı": f"{M['EVAL0']:%Y-%m}", "AUC 4s": round(M["AUC"][4], 3), "AUC 8s": round(M["AUC"][8], 3)}
    for k, lab in [("star", "⭐"), ("u4", "4s ÇG↑"), ("acls", "A")]:
        v = S[k]; r[f"{lab} %"] = round(v["olcu"], 1); r[f"{lab} yarılar"] = f"{v['y1']:.0f}/{v['y2']:.0f}"; r[f"{lab} n"] = v["n_h"]; r[f"{lab}"] = "✅" if v["on"] else "—"
    r["Haftada (açık)"] = round(sum(S[k]["wk"] for k in on), 1); rows.append(r)
    if on or sym in CANLI: secilen.append((sym, f, on))
    # BTC aynı saatte sinyal verirken / vermezken isabet (senin sorduğun)
    ex = glob.glob(f"art/**/disa_{sym}.pkl", recursive=True)
    if EXB is not None and ex:
        X = pd.read_pickle(ex[0]); X = X[X.index >= M["EVAL0"]]; B = EXB.reindex(X.index)
        bany = (B.star.fillna(False) | B.u4.fillna(False) | B.acls.fillna(False)).values.astype(bool); bstr = (B.star.fillna(False) | B.u4.fillna(False)).values.astype(bool)
        for k, H in [("star", 8), ("u4", 4), ("acls", 4)]:
            m = X[k].values.astype(bool) & X.y4.notna().values; ev = events(m, H); hit = (X.y4.values[ev] > 0)
            for lab, mm in [("BTC de sinyal verdi", bany[ev]), ("BTC 4s Çok güçlü ↑ / ⭐", bstr[ev]), ("BTC sinyal yok", ~bany[ev])]:
                ort.append({"Coin": nm, "Sinyal": {"star": "⭐", "u4": "4s ÇG↑", "acls": "A"}[k], "Durum": lab, "n": int(mm.sum()), "isabet": hit[mm].mean() * 100 if mm.any() else np.nan})
T = pd.DataFrame(rows).set_index("Coin").sort_values("Haftada (açık)", ascending=False)
yaz("## 1) Coin'ler ve sinyaller (isabet = değerlendirme dönemi, 4 saat sonra)\n```\n" + T.to_string() + "\n```")
yaz("\n## 2) Bildirimi açılan coin'ler\n" + "\n".join(f"- **{s.replace('USDT','')}**: " + (", ".join({'star':'⭐','u4':'4s Çok güçlü ↑','acls':'🟢 A sınıfı'}[k] for k in on) if on else "(açık sinyal yok — izlenmeyecek)") for s, _, on in secilen))
if ort:
    O = pd.DataFrame(ort); yaz("\n## 3) BTC ile aynı saatte mi daha isabetli? (coin sinyalinin 4 saat sonraki isabeti)")
    P = O.assign(k=O.n * O.isabet / 100).groupby(["Sinyal", "Durum"]).agg(n=("n", "sum"), k=("k", "sum")); P["isabet %"] = (100 * P.k / P.n).round(1)
    yaz("Tüm coin'ler birlikte:\n```\n" + P.drop(columns="k").to_string() + "\n```")
    W = O.pivot_table(index=["Coin", "Sinyal"], columns="Durum", values=["isabet", "n"]).round(1); yaz("Coin bazında:\n```\n" + W.to_string() + "\n```")
os.makedirs("durum", exist_ok=True)
for sym, f, on in secilen:
    shutil.copy(f, f"durum/model_{sym}.pkl.gz"); rp = glob.glob(f"art/**/rapor_{sym}.md", recursive=True)
    if rp: shutil.copy(rp[0], f"durum/rapor_{sym}.md")
open("tarama_sonuc.md", "w").write("\n".join(L) + "\n"); open("secilen_coinler.txt", "w").write("\n".join(s for s, _, on in secilen if on) + "\n")
