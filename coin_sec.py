# coin_sec.py — eğitim çıktılarından (art/) modelleri durum/'a alır. İlk kurulumda (--ilk) izlenecek coin listesini de yazar:
#   tek başına açık sinyali olan VEYA 🤝 ortak (durum/ortak_acik.csv) ya da 🔇 BTC sessizken (durum/tek_acik.csv) listesinde olan coin'ler.
import glob, gzip, os, pickle, shutil, sys, pandas as pd
os.makedirs("durum", exist_ok=True)
J = set(pd.read_csv("durum/ortak_acik.csv").sym) if os.path.exists("durum/ortak_acik.csv") else set()
J |= set(pd.read_csv("durum/tek_acik.csv").sym) if os.path.exists("durum/tek_acik.csv") else set()      # 🔇 BTC sessizken listesi
liste = [l.strip() for l in open("durum/coin_listesi.txt")] if os.path.exists("durum/coin_listesi.txt") and "--ilk" not in sys.argv else None
sec = []
for f in sorted(glob.glob("art/**/model_*.pkl.gz", recursive=True)):
    sym = os.path.basename(f)[6:-7]
    if sym == "BTCUSDT": continue                                       # BTC kendi sisteminde; burada yalnız ortak analiz için eğitilir
    with gzip.open(f, "rb") as g: M = pickle.load(g)
    aktif = any(v["on"] for v in M["SIG"].values()) or sym in J
    if (liste is None and aktif) or (liste is not None and sym in liste):
        shutil.copy(f, f"durum/model_{sym}.pkl.gz"); sec.append(sym)
        for r in glob.glob(f"art/**/rapor_{sym}.md", recursive=True): shutil.copy(r, f"durum/rapor_{sym}.md")
if liste is None: open("durum/coin_listesi.txt", "w").write("\n".join(sec) + "\n")
print("durum/'a alınan modeller:", ", ".join(s.replace("USDT", "") for s in sec))
