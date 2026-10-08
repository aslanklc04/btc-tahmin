# temizlik.py — CANLIDAKİ TÜM COİN SİNYAL TÜRLERİNİN ENVANTERİ ve önceden sabit kuralla SEÇİM (kullanıcı: "zayıf sinyal istemiyorum", haftada 30–40, isabet + kâr, ⛔ gönderilmesin).
# Veri: coin eğitim çıktıları (art1: disa_*.pkl — ⭐ / 4s Çok güçlü ↑ / A sınıfı bayrakları ve 4/8 saat getirileri), 24 saat deneme (art2: disa24_*.pkl),
#       kendi Coinbase primi saatlik z (art3: prim_veri.pkl), canlı listeler (canli/durum: ortak_acik, tek_acik, prim_acik, model SIG bayrakları).
# Aday türler (coin başına): tek başına (modelin kendi denetiminden geçen) · 🤝 BTC ile ortak · 🔇 BTC sessizken · 💵 kendi primi AL · 🧪 24 saat.
#   Her biri iki filtre ile: "⛔ hariç" (kendi primi z ≤ −1 iken gelenler atılır; DOGE/NEAR/PEPE'de filtre yok) ve "yalnız ✅" (z > 0).
# Ölçüm: 2024+ (karar), 2026 (bozulma kontrolü), 2020–23 (bilgi). Net = işlem başı %, limit komisyon %0,02 × 2.
# ÖNCEDEN SABİT SEÇİM: 2024+ ≥ 30 işlem, isabet ≥ %58, net ≥ +%0,05, 2026'da (≥ 10 işlem varsa) isabet ≥ %55 → aday geçer.
#   Coin başına geçenlerden net'i en yüksek TEK tür; toplam haftada 30'un altında kalırsa coin'lere ikinci en iyi tür (farklı aile) eklenir; 40'ı aşarsa en düşük net'liler çıkar.
import os, glob, gzip, pickle, numpy as np, pandas as pd
from ortak import *
L = []
def yaz(s=""): print(s, flush=True); L.append(s)
f = lambda p: glob.glob(p, recursive=True)
EX = {os.path.basename(p)[5:-4]: pd.read_pickle(p) for p in f("art1/**/disa_*USDT.pkl")}
E24 = {os.path.basename(p)[7:-4]: pd.read_pickle(p) for p in f("art2/**/disa24_*USDT.pkl")}
ZP = {k: v.astype("float64") for k, v in pd.read_pickle(f("art3/**/prim_veri.pkl")[0]).items()}
CD = "canli/durum"
JOINT = pd.read_csv(f"{CD}/ortak_acik.csv"); TEKL = pd.read_csv(f"{CD}/tek_acik.csv"); PRIM = pd.read_csv(f"{CD}/prim_acik.csv").set_index("coin")
CANLI = [l.strip() for l in open(f"{CD}/coin_listesi.txt") if l.strip()]
SIGON = {}
for s in CANLI:
    with gzip.open(f"{CD}/model_{s}.pkl.gz", "rb") as g: M = pickle.load(g)
    SIGON[s] = {k: bool(v["on"]) for k, v in M["SIG"].items()}
BILGI = {"DOGE", "NEAR", "PEPE"}; A20, A24, A26, LMT = pd.Timestamp("2020-01-01", tz="UTC"), pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC"), 0.0002
SIMDI = pd.Timestamp.now(tz="UTC")
yaz(f"# 🧹 Sinyal temizliği — envanter ve seçim · {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nCanlı coin'ler: {', '.join(s[:-4] for s in CANLI)} · eğitim çıktısı {len(EX)} · 24 saat {len(E24)} · prim {len(ZP)}\n")
B = EX["BTCUSDT"]; AD = {"star": ("⭐", 8, "y8"), "u4": ("4s ÇG↑", 4, "y4"), "acls": ("A", 4, "y4")}
def stat(t, r, H):
    """t: olay zamanları, r: basit getiri (oran). Dönem başına n, isabet, net, haftada."""
    r = pd.Series(r, index=t).dropna(); out = {}
    for pn, a, b in (("20-23", A20, A24), ("24+", A24, None), ("26", A26, None)):
        x = r[(r.index >= a) & ((r.index < b) if b is not None else True)]
        wk = max(1.0, ((b if b is not None else SIMDI) - max(a, r.index.min() if len(r) else a)).days / 7)
        out[pn] = dict(n=len(x), isabet=100 * (x > 0).mean() if len(x) else np.nan, net=100 * (x - 2 * LMT).mean() if len(x) else np.nan, haftada=len(x) / wk)
    return out
def zof(nm, idx):
    z = ZP[nm].z if nm in ZP else None
    return pd.Series(np.nan, index=idx) if z is None else z.reindex(idx)
rows = []
for s in CANLI:
    nm = s[:-4]; X = EX.get(s)
    if X is None: continue
    Bx = B.reindex(X.index); bu4 = Bx.u4.fillna(False).values.astype(bool); bany = (Bx.star.fillna(False) | Bx.u4.fillna(False) | Bx.acls.fillna(False)).values.astype(bool)
    zc = zof(nm, X.index).values
    jo = set(JOINT[JOINT.sym == s].sinyal); te = set(TEKL[TEKL.sym == s].sinyal)
    aday = [(f"tek başına {AD[k][0]}", k, np.ones(len(X), bool)) for k in AD if SIGON[s].get(k)]
    aday += [(f"🤝 {AD[k][0]}", k, bu4) for k in AD if k in jo] + [(f"🔇 {AD[k][0]}", k, ~bany) for k in AD if k in te]
    for ad, k, kos in aday:
        _, H, yc = AD[k]; base = X[k].fillna(False).values.astype(bool) & kos & X[yc].notna().values
        for fl, fm in (("ham", np.ones(len(X), bool)), ("⛔ hariç", ~(zc <= -1) if nm not in BILGI else np.ones(len(X), bool)), ("yalnız ✅", (zc > 0) if nm not in BILGI else None)):
            if fm is None: continue
            m = base & fm; ev = events(m, H); st = stat(X.index[ev], np.exp(X[yc].values[ev]) - 1, H)
            rows.append(dict(coin=nm, aile=ad.split(" ")[0] if not ad.startswith("tek") else "tek başına", tur=ad, sinyal=k, filtre=fl, H=H, **{f"{p}_{q}": v for p, d in st.items() for q, v in d.items()}))
    if nm in PRIM.index and nm in ZP:                                                                # 💵 kendi primi AL (gecikmesiz)
        r_ = PRIM.loc[nm]; D = ZP[nm]; H = int(r_.saat); m = (D.z >= r_.esik).fillna(False).values; ev = events(m, H); c = D.c.values
        ok = ev[ev + H < len(D)]; st = stat(D.index[ok], c[ok + H] / c[ok] - 1, H)
        rows.append(dict(coin=nm, aile="💵", tur=f"💵 prim z ≥ {r_.esik:.0f} ({H}s)", sinyal="prim", filtre="—", H=H, **{f"{p}_{q}": v for p, d in st.items() for q, v in d.items()}))
for nm, X in E24.items():                                                                           # 🧪 24 saat deneme (gecikmesiz: sinyal saatinde gir, 24 saat sonra çık)
    nm = nm.replace("USDT", "")
    X = X.reindex(pd.date_range(X.index[0], X.index[-1], freq="1h", tz="UTC")); c = X.close.ffill(limit=3).values; n = len(X)
    base = np.nan_to_num(((X.S24 > 0) & (X.C24 >= X.T10_24)).values).astype(bool) & X.T10_24.notna().values & (np.arange(n) + 25 < n)
    zc = zof(nm, X.index).values
    for fl, fm in (("ham", np.ones(n, bool)), ("⛔ hariç", ~(zc <= -1) if nm not in BILGI else np.ones(n, bool)), ("yalnız ✅", (zc > 0) if nm not in BILGI else None)):
        if fm is None: continue
        ev = events(base & fm, 24); st = stat(X.index[ev], c[ev + 24] / c[ev] - 1, 24)
        rows.append(dict(coin=nm, aile="🧪", tur="🧪 24 saat Çok güçlü ↑", sinyal="d24", filtre=fl, H=24, **{f"{p}_{q}": v for p, d in st.items() for q, v in d.items()}))
R = pd.DataFrame(rows)
R["gecer"] = (R["24+_n"] >= 30) & (R["24+_isabet"] >= 58) & (R["24+_net"] >= 0.05) & ((R["26_n"] < 10) | (R["26_isabet"] >= 55))
R.to_csv("temizlik_tum.csv", index=False)
def satir(r): return (f"| {r.coin} | {r.tur} | {r.filtre} | {int(r['24+_n'])} · %{r['24+_isabet']:.0f} · {r['24+_net']:+.2f} · {r['24+_haftada']:.1f}/hf | "
                      + (f"{int(r['26_n'])} · %{r['26_isabet']:.0f} · {r['26_net']:+.2f}" if r["26_n"] else "—") + " | " + (f"{int(r['20-23_n'])} · %{r['20-23_isabet']:.0f}" if r["20-23_n"] else "—") + f" | {'✅' if r.gecer else '❌'} |")
BAS = "| Coin | Tür | Filtre | 2024+: işlem · isabet · net % · haftada | 2026 | 2020–23 | Geçer |\n|---|---|---|---|---|---|---|"
yaz(f"## 1. Envanter (tüm türler, {len(R)} satır) — geçen: {int(R.gecer.sum())}\n{BAS}\n" + "\n".join(satir(r) for _, r in R.sort_values(["coin", "gecer", "24+_net"], ascending=[True, False, False]).iterrows()))
# ---- seçim ----
G = R[R.gecer].sort_values("24+_net", ascending=False)
sec = G.groupby("coin").head(1)
def toplam(x): return x["24+_haftada"].sum()
if toplam(sec) < 30:
    for _, r in G.iterrows():
        if toplam(sec) >= 30: break
        if ((sec.coin == r.coin) & (sec.aile == r.aile)).any() or ((sec.coin == r.coin).sum() >= 2): continue
        sec = pd.concat([sec, r.to_frame().T])
while toplam(sec) > 40 and len(sec) > 1: sec = sec.sort_values("24+_net").iloc[1:]
sec = sec.sort_values("24+_net", ascending=False)
yaz(f"\n## 2. Seçilen coin sinyalleri ({len(sec)} tür, toplam ~{toplam(sec):.1f} sinyal/hafta; 2026'da ~{sec['26_haftada'].sum():.1f}/hafta)\n{BAS}\n" + "\n".join(satir(r) for _, r in sec.iterrows()))
yok = [c for c in R.coin.unique() if c not in set(sec.coin)]
yaz(f"\nHiçbir türü geçmeyen (susturulacak) coin'ler: {', '.join(yok) if yok else '—'}")
w = (sec["24+_n"] * sec["24+_isabet"]).sum() / sec["24+_n"].sum(); w26 = (sec["26_n"] * sec["26_isabet"]).sum() / max(1, sec["26_n"].sum())
yaz(f"Seçilenlerin ağırlıklı isabeti: 2024+ %{w:.1f} · 2026 %{w26:.1f} · ortalama net 2024+ %{(sec['24+_n'] * sec['24+_net']).sum() / sec['24+_n'].sum():+.2f}")
sec[["coin", "aile", "tur", "sinyal", "filtre", "H", "24+_n", "24+_isabet", "24+_net", "24+_haftada", "26_n", "26_isabet", "26_net"]].to_csv("secim_acik.csv", index=False)
# ---- BTC türleri (bilgi; aynı ölçüt) ----
zb = zof("BTC", B.index).values; br = []
for k, (ad, H, yc) in AD.items():
    for fl, fm in (("ham", np.ones(len(B), bool)), ("⛔ hariç", ~(zb <= -1)), ("yalnız ✅", zb > 0)):
        m = B[k].fillna(False).values.astype(bool) & B[yc].notna().values & fm; ev = events(m, H); st = stat(B.index[ev], np.exp(B[yc].values[ev]) - 1, H)
        br.append(dict(coin="BTC", aile="BTC", tur=f"BTC {ad}", sinyal=k, filtre=fl, H=H, **{f"{p}_{q}": v for p, d in st.items() for q, v in d.items()}))
BR = pd.DataFrame(br); BR["gecer"] = (BR["24+_n"] >= 30) & (BR["24+_isabet"] >= 58) & (BR["24+_net"] >= 0.05) & ((BR["26_n"] < 10) | (BR["26_isabet"] >= 55))
yaz(f"\n## 3. BTC sinyalleri (aynı ölçüt)\n{BAS}\n" + "\n".join(satir(r) for _, r in BR.iterrows())); BR.to_csv("temizlik_btc.csv", index=False)
open("temizlik_sonuc.md", "w").write("\n".join(L) + "\n")
