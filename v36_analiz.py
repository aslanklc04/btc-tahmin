# v36_analiz.py — v36 deneyi: mevcut coin modeli (b) ile yeni girdili model (n) aynı yürüyen testte, CANLI kurallarla karşılaştırılır (yalnız test).
# ÖNCEDEN YAZILI KARAR (12.10.2026, sonuçlar görülmeden):
#   COİN MODELİ (1/4/8 s): yeni model ancak (i) canlı kurallarla seçilen coin ✅ ana sinyallerinde (🤝 prim ≥ 0 + 🔇🔀) ÜÇ dönemde de
#     (2022-06→2023 · 2024+ · 2026) hem isabet hem işlem başı net eskisinden yüksekse, (ii) ham model sinyallerinde (⭐ / 4s / A, 4 saat) üç dönemde de
#     isabet eskisinden yüksekse ve (iii) ✅ ana sinyal sayısı eskisinin en az %70'i ise kabul edilir.
#   24 SAAT MODELİ (🧪): yeni model ancak canlı 10 coin'in 🧪 ✅ ana sinyallerinde (kendi primi ≥ 0) üç dönemde de isabet VE net yüksekse,
#     ham 🧪 sinyallerinde (15 coin) üç dönemde de isabet yüksekse ve sayı en az %70 ise kabul edilir.
#   BTC modeli bu deneyde değişmez: 🤝 / 🔇 için BTC'nin durumu iki varyantta da MEVCUT BTC modelinden alınır.
import glob, gzip, pickle, numpy as np, pandas as pd
from ortak import *
L = []
def yaz(s=""): print(s, flush=True); L.append(s)
V = {}
for p in glob.glob("art/**/v36_*.pkl", recursive=True):
    d = pickle.load(open(p, "rb")); V[d["sym"]] = d
CD = "canli/durum"; JOINT, TEKL = pd.read_csv(f"{CD}/ortak_acik.csv"), pd.read_csv(f"{CD}/tek_acik.csv")
CAN24 = {os.path.basename(p)[8:-11] for p in glob.glob(f"{CD}/model24_*USDT.pkl.gz")}
SIGON = {}
for s in V:
    try:
        with gzip.open(f"{CD}/model_{s}.pkl.gz", "rb") as g: SIGON[s] = {k: bool(v["on"]) for k, v in pickle.load(g)["SIG"].items()}
    except Exception: SIGON[s] = {}
P0, A24, A26 = (pd.Timestamp(x, tz="UTC") for x in ("2022-06-01", "2024-01-01", "2026-01-01"))
yaz(f"# 🧠 Model geliştirme (v36): yeni girdili coin modeli vs mevcut — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n"
    f"Coin: {len(V)} ({', '.join(sorted(s[:-4] for s in V))})" + (f" · yeni girdi: {', '.join(V[next(iter(V))]['EK'])}" if V else "") + "\n")
if "BTCUSDT" not in V: yaz("**BTC sonucu yok — analiz yapılamadı**"); open("v36_sonuc.md", "w").write("\n".join(L) + "\n"); raise SystemExit
BX = V["BTCUSDT"]["EXb"]; BPZ = V["BTCUSDT"]["PC"].z if V["BTCUSDT"]["PC"] is not None else None
def olaylar(var):
    rows = []
    for sym, d in V.items():
        nm = sym[:-4]; pz = d["PC"].z if d["PC"] is not None else None
        if sym != "BTCUSDT":
            X = d["EX" + var]; Bx = BX.reindex(X.index)
            bu4 = Bx.u4.fillna(False).astype(bool).values; bany = (Bx.star.fillna(False).astype(bool) | Bx.u4.fillna(False).astype(bool) | Bx.acls.fillna(False).astype(bool)).values
            jo, te = set(JOINT[JOINT.sym == sym].sinyal), set(TEKL[TEKL.sym == sym].sinyal)
            for k, (H0, yc0) in {"star": (8, "y8"), "u4": (4, "y4"), "acls": (4, "y4")}.items():
                sig = X[k].fillna(False).astype(bool).values
                for aile, kos, acik, H, yc in (("ham", np.ones(len(X), bool), True, 4, "y4"), ("🤝", bu4, k in jo, 4, "y4"), ("🔇", ~bany, k in te, 4, "y4"),
                                               ("🪙", np.ones(len(X), bool), SIGON.get(sym, {}).get(k, False), H0, yc0)):
                    if not acik: continue
                    m = sig & kos & X[yc].notna().values; ev = events(m, H); t = X.index[ev]
                    rows.append(pd.DataFrame({"aile": aile, "k": k, "nm": nm, "t": t, "net": np.exp(X[yc].values[ev]) - 1 - 0.0004,
                                              "z": pz.reindex(t).values if pz is not None else np.nan}))
        X = d["X24" + var]; X = X.reindex(pd.date_range(X.index[0], X.index[-1], freq="1h", tz="UTC")); c = X.close.ffill(limit=3).values; n = len(X)
        m = np.nan_to_num(((X.S24 > 0) & (X.C24 >= X.T10_24)).values).astype(bool) & X.T10_24.notna().values & (np.arange(n) + 25 < n); ev = events(m, 24); t = X.index[ev]
        rows.append(pd.DataFrame({"aile": "🧪", "k": "24", "nm": nm, "t": t, "net": c[ev + 24] / c[ev] - 1 - 0.0004, "z": pz.reindex(t).values if pz is not None else np.nan}))
    E = pd.concat(rows, ignore_index=True); E = E[np.isfinite(E.net)].copy(); E["ok"] = E.net > 0
    E["zB"] = BPZ.reindex(pd.DatetimeIndex(E.t)).values if BPZ is not None else np.nan
    return E
EV = {"b": olaylar("b"), "n": olaylar("n")}
def gruplar(E):
    z, zB, a = E.z.values, E.zB.values, E.aile.values
    return {"Ham model sinyali (⭐ / 4s / A, 4 saat)": a == "ham",
            "🤝 BTC ile birlikte (tümü)": a == "🤝",
            "🤝 ✅ ana (kendi primi ≥ 0)": (a == "🤝") & (z >= 0),
            "🔇🔀 ✅ ana": (a == "🔇") & (z > 0) & (zB > -1) & (zB <= 0) & (E.nm.values != "BTC"),
            "COİN ✅ ANA TOPLAM (🤝 ana + 🔀)": ((a == "🤝") & (z >= 0)) | ((a == "🔇") & (z > 0) & (zB > -1) & (zB <= 0)),
            "🔇 BTC sessiz (tümü, yedek)": a == "🔇",
            "🪙 coin tek başına (tümü, yedek)": a == "🪙",
            "🧪 24 saat ham (15 coin)": a == "🧪",
            "🧪 ✅ ana (canlı 10 coin, prim ≥ 0)": (a == "🧪") & E.nm.isin(CAN24).values & (z >= 0)}
DON = (("2022-06→2023", lambda t: (t >= P0) & (t < A24), (A24 - P0).days / 7), ("2024+", lambda t: t >= A24, None), ("2026", lambda t: t >= A26, None))
SON = max(pd.DatetimeIndex(e.t).max() for e in EV.values())
def ist(E, m):
    o = {}
    for dn, f_, hf in DON:
        x = E[m & f_(pd.DatetimeIndex(E.t))]; h = hf or (SON - (A24 if dn == "2024+" else A26)).days / 7
        o[dn] = (len(x), len(x) / h, 100 * x.ok.mean() if len(x) else np.nan, 100 * x.net.mean() if len(x) else np.nan)
    return o
GB, GN = gruplar(EV["b"]), gruplar(EV["n"]); R = {}
yaz("_her satır: haftada sinyal · isabet · işlem başı net % (komisyon sonrası) — b = mevcut model, n = yeni girdili model · ▲ = yeni daha iyi (isabet ve net)_\n```")
yaz(f"{'':44s}" + " | ".join(f"{dn:^30s}" for dn, _, _ in DON))
for g in GB:
    ob, on = ist(EV["b"], GB[g]), ist(EV["n"], GN[g]); R[g] = (ob, on)
    yaz(f"{g}")
    yaz(f"  {'b mevcut':42s}" + " | ".join(f"{ob[dn][1]:5.1f}/hf · %{ob[dn][2]:4.1f} · {ob[dn][3]:+.3f}  " for dn, _, _ in DON))
    yaz(f"  {'n yeni':42s}" + " | ".join(f"{on[dn][1]:5.1f}/hf · %{on[dn][2]:4.1f} · {on[dn][3]:+.3f} {'▲' if on[dn][2] > ob[dn][2] and on[dn][3] > ob[dn][3] else ' '}" for dn, _, _ in DON))
yaz("```\n## AUC (yön tahmini, 0,5 = yazı-tura) — 2024+ · coin başına mevcut → yeni\n```")
for H in (1, 4, 8, 24):
    sat, art = [], 0
    for s, d in sorted(V.items()):
        ab, an = d["AUCb"][H]["2024+"], d["AUCn"][H]["2024+"]; art += an > ab; sat.append(f"{s[:-4]} {ab:.3f}→{an:.3f}")
    ort = lambda v, dn: np.nanmean([d[v][H][dn] for d in V.values()])
    yaz(f"{H:>2} s: yeni daha iyi {art}/{len(V)} coin · ortalama " + " · ".join(f"{dn} {ort('AUCb', dn):.4f}→{ort('AUCn', dn):.4f}" for dn in ("22-06→23", "2024+", "2026")))
    yaz("      " + " · ".join(sat))
yaz("```")
def ustun(g, net=True):
    ob, on = R[g]; return all(on[dn][2] > ob[dn][2] and (not net or on[dn][3] > ob[dn][3]) for dn, _, _ in DON)
def sayi(g): ob, on = R[g]; return all(on[dn][0] >= 0.7 * ob[dn][0] for dn, _, _ in DON)
K1 = ustun("COİN ✅ ANA TOPLAM (🤝 ana + 🔀)") and ustun("Ham model sinyali (⭐ / 4s / A, 4 saat)", net=False) and sayi("COİN ✅ ANA TOPLAM (🤝 ana + 🔀)")
K2 = ustun("🧪 ✅ ana (canlı 10 coin, prim ≥ 0)") and ustun("🧪 24 saat ham (15 coin)", net=False) and sayi("🧪 ✅ ana (canlı 10 coin, prim ≥ 0)")
yaz("\n## Önceden yazılı karar")
yaz(f"- **Coin modeli (1/4/8 s):** {'✅ GEÇTİ — yeni girdili model canlıya aday' if K1 else '❌ geçmedi — mevcut model kalır'}")
yaz(f"- **24 saat modeli (🧪):** {'✅ GEÇTİ — yeni girdili model canlıya aday' if K2 else '❌ geçmedi — mevcut model kalır'}")
open("v36_sonuc.md", "w").write("\n".join(L) + "\n")
