# prim_yeniden_test.py — TEST (18.10.2026, önceden yazılı): canlı prim (ortak.cb_prim, main) saat başından +2/+3/+8/+12/+15/+20 dk'da okunursa
# kesin değere (+65 dk, aynı yöntem) ne kadar oturuyor? 2 ardışık saat, 50 coin (40 az işlem gören + 10 likit).
# ŞART (önceden): iki saatin İKİSİNDE de |z − kesin| ≤ 0,2 (ya da ikisi de yok) oranı ≥ %95 olan EN ERKEN dakika seçilir;
# o dakika +3'ten belirgin iyi değilse (iki saatin ortalamasında ≥ +10 puan) yeniden okuma EKLENMEZ.
import importlib.util, os, sys, time, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "eski"); import ortak as O; sys.path.pop(0)
C = ["REQ", "ARPA", "PUNDIX", "BAND", "KNC", "C98", "GNO", "BNT", "MASK", "BLUR", "T", "CVC", "CELR", "AUDIO", "ALT", "KAVA", "UMA", "RPL", "ARKM", "GMT",
     "GTC", "POWR", "RLC", "AUCTION", "LQTY", "GLM", "ALICE", "RARE", "LPT", "AGLD", "1INCH", "CTSI", "FIDA", "MINA", "OGN", "API3", "G", "SUSHI", "VET", "ROSE",
     "BTC", "ETH", "SOL", "OP", "DOT", "LINK", "AVAX", "DOGE", "ARB", "LDO"]
DK = [2, 3, 8, 12, 15, 20]; os.makedirs("/tmp/py", exist_ok=True)
def bekle(t):
    while pd.Timestamp.now(tz="UTC") < t: time.sleep(3)
def oku(h0, dk):
    def f(nm):
        d = O.cb_prim(nm, path=f"/tmp/py/{h0:%H}_{dk}_{nm}.json"); return nm, (O.cb_z(d) if d and d.get("t") == str(h0) else np.nan), (d or {}).get("t")
    with ThreadPoolExecutor(6) as ex: return {nm: (z, t) for nm, z, t in ex.map(f, C)}
H0 = pd.Timestamp.now(tz="UTC").ceil("h"); SAAT = [H0, H0 + pd.Timedelta(hours=1)]; R = {h: {} for h in SAAT}
plan = sorted([(h + pd.Timedelta(minutes=dk), h, dk) for h in SAAT for dk in DK] + [(h + pd.Timedelta(minutes=65), h, "kesin") for h in SAAT])
for t, h, dk in plan:
    bekle(t); t0 = time.time(); R[h][dk] = oku(h, dk); print(f"{h:%H}:00 +{dk} okundu ({time.time() - t0:.0f} sn)", flush=True)
L = [f"# 🔁 Prim yeniden okuma testi — saatler {SAAT[0].tz_convert('Europe/Istanbul'):%d.%m %H:00} ve {SAAT[1].tz_convert('Europe/Istanbul'):%H:00} (TR)"]
oran = {}
for h in SAAT:
    K = {nm: R[h]["kesin"][nm][0] for nm in C}; L.append(f"\n## {h.tz_convert('Europe/Istanbul'):%H}:00\n```")
    rows = []
    for nm in C:
        r = {"coin": nm, "kesin": round(K[nm], 2) if np.isfinite(K[nm]) else np.nan}
        for dk in DK: r[f"+{dk}"] = round(R[h][dk][nm][0], 2) if np.isfinite(R[h][dk][nm][0]) else np.nan
        rows.append(r)
    X = pd.DataFrame(rows); L.append(X.to_string(index=False)); L.append("```")
    for dk in DK:
        z = X[f"+{dk}"]; ok = (z.isna() & X.kesin.isna()) | (z - X.kesin).abs().le(0.2); oran[(h, dk)] = 100 * ok.mean()
        kat = ((z >= 0) != (X.kesin >= 0)) & z.notna() & X.kesin.notna()
        L.append(f"- +{dk} dk: doğru %{oran[(h, dk)]:.0f} · az işlem gören 40: %{100 * ok[:40].mean():.0f} · likit 10: %{100 * ok[40:].mean():.0f} · z ≥ 0 tarafı yanlış: {int(kat.sum())}")
gec = [dk for dk in DK if all(oran[(h, dk)] >= 95 for h in SAAT)]; o3 = np.mean([oran[(h, 3)] for h in SAAT])
sec = gec[0] if gec else None; iy = (np.mean([oran[(h, sec)] for h in SAAT]) - o3) if sec else np.nan
L.append(f"\n**Karar (önceden yazılı):** " + (f"✅ +{sec} dk ≥ %95 (iki saatte de) · +3'e göre {iy:+.0f} puan → " + ("EKLENİR" if iy >= 10 else "fark küçük → EKLENMEZ") if sec else "❌ hiçbir dakika iki saatte de %95'e ulaşmadı → EKLENMEZ"))
open("prim_yeniden_sonuc.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
