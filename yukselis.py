# yukselis.py — %2+ YÜKSELİŞ DÖNEMLERİ: BTC ve coin'lerde 8 saatte ≥ %2 yükselişten ÖNCE ne farklı? (kullanıcının fikri)
# Hedef: 8 saat sonraki kapanış ≥ +%2 ("yükseliş") · karşılaştırma: ≤ −%2 ("düşüş") — ikisi birden artıyorsa bu yön değil OYNAKLIK bilgisidir.
# Her özellik için: seçim dönemindeki (2020–23; yeni coin'lerde verinin ilk yarısı) ondalık dilimler → en üst/alt dilimde yükseliş ve düşüş olasılığı.
# Tutarlı sayılması için: iki dönemde de (≤2023 / 2024+) aynı dilimde yükseliş olasılığı tabanın ≥ 1,3 katı VE yükseliş katı düşüş katından en az 0,2 fazla (yalnız oynaklık değil, YÖN).
import glob, os, time, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
SYMS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "DOGEUSDT", "SHIBUSDT", "DOTUSDT", "ADAUSDT", "LINKUSDT", "NEARUSDT", "AVAXUSDT", "ARBUSDT", "OPUSDT", "APTUSDT", "SUIUSDT", "PEPEUSDT", "FLOKIUSDT", "INJUSDT", "FETUSDT"]
def kl(sym):
    rows, cur, end = [], int(pd.Timestamp("2017-08-17", tz="UTC").timestamp() * 1000), int(time.time() * 1000)
    for url in EP:
        try:
            rows, cur = [], int(pd.Timestamp("2017-08-17", tz="UTC").timestamp() * 1000)
            while cur < end:
                r = requests.get(url, params=dict(symbol=sym, interval="1h", startTime=cur, endTime=end, limit=1000), timeout=20); r.raise_for_status(); dt = r.json()
                if not dt: break
                rows += dt; cur = dt[-1][0] + 3_600_000
                if len(dt) < 1000: break
            break
        except Exception: rows = []
    d = pd.DataFrame([x[:11] for x in rows], columns=["t", "open", "high", "low", "close", "volume", "ct", "qv", "trades", "tbb", "tbq"]).astype(float)
    d.index = pd.to_datetime(d.t, unit="ms", utc=True) + pd.Timedelta(hours=1); d = d[d.index <= pd.Timestamp.now(tz="UTC")]; return sym, d[~d.index.duplicated()].sort_index()
if os.environ.get("YEREL"):
    _O = pd.read_pickle("/home/claude/lab2/data/o_1h.pkl"); _rg = np.random.default_rng(0)
    def kl(sym):
        d = _O.copy() * (1 if sym == "BTCUSDT" else (1 + 0.02 * _rg.standard_normal(len(_O))).cumsum()[:, None] / np.arange(1, len(_O) + 1)[:, None] + 0)
        d = _O.copy(); d["close"] = d.close * np.exp(0.001 * _rg.standard_normal(len(d)).cumsum() if sym != "BTCUSDT" else 0)
        d["tbb"] = d.volume * _rg.uniform(.3, .7, len(d)); d["trades"] = _rg.integers(100, 1000, len(d)); return sym, d
    SYMS = SYMS[:3]
with ThreadPoolExecutor(6) as ex: K = dict(ex.map(kl, SYMS))
yaz(f"# 🚀 %2+ yükseliş dönemleri — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nVeri: {len(K)} varlık · saatlik Binance · {time.time()-T0:.0f} sn\n")
EXF = {os.path.basename(p)[5:-4]: pd.read_pickle(p) for p in glob.glob("art/**/disa_*USDT.pkl", recursive=True)}
B = K["BTCUSDT"]; bF = features(B[["open", "high", "low", "close", "volume"]])
def ozellik(sym):
    o = K[sym]; F = features(o[["open", "high", "low", "close", "volume"]]).drop(columns=["hs", "hc", "ds", "dc"])
    v, tb = o.volume, o.tbb
    for k in (1, 4, 24): F[f"alim_baskisi_{k}s"] = (2 * tb.rolling(k).sum() - v.rolling(k).sum()) / (v.rolling(k).sum() + 1e-12)
    F["islem_sayisi_z"] = np.log(o.trades + 1) - np.log(o.trades.rolling(168).mean() + 1)
    if sym != "BTCUSDT":
        for k in (4, 24, 168): F[f"btc_gore_{k}s"] = F[f"r{k}"] - bF[f"r{k}"].reindex(F.index)
        F["btc_r24"] = bF.r24.reindex(F.index); F["btc_rsi14"] = bF.rsi14.reindex(F.index); F["btc_ema168"] = bF.ema168.reindex(F.index)
    X = EXF.get(sym)
    if X is not None:
        for k in ("u4", "star", "acls"): F[f"model_{k}"] = X[k].reindex(F.index).astype(float)
    if sym != "BTCUSDT" and "BTCUSDT" in EXF: F["btc_model_u4"] = EXF["BTCUSDT"].u4.reindex(F.index).astype(float)
    F["y8"] = np.log(o.close.shift(-8) / o.close); F["saat"] = F.index.hour; F["gun"] = F.index.dayofweek; F["sym"] = sym
    return F.iloc[720:]
ALL = {s: ozellik(s) for s in K if len(K[s]) > 4000}
UP, DN = np.log(1.02), np.log(0.98); A24 = pd.Timestamp("2024-01-01", tz="UTC")
def per(F): sel = F.index < A24; return (sel if sel.sum() >= 24 * 365 else (F.index < F.index[len(F) // 2])), (F.index >= A24)
# ---- taban oranlar ----
rows = []
for s, F in ALL.items():
    a, b = per(F); y = F.y8
    rows.append(dict(varlik=s[:-4], secim_yukselis=100 * (y[a] >= UP).mean(), secim_dusus=100 * (y[a] <= DN).mean(), h24_yukselis=100 * (y[b] >= UP).mean(), h24_dusus=100 * (y[b] <= DN).mean()))
yaz("## Taban: 8 saatte ≥ +%2 yükseliş / ≤ −%2 düşüş sıklığı (% saat)\n```\n" + pd.DataFrame(rows).set_index("varlik").round(1).to_string() + "\n```")
# ---- özellik dilimleri ----
def analiz(names, grup):
    out = []
    feats = [c for c in pd.concat([ALL[s] for s in names]).columns if c not in ("y8", "saat", "gun", "sym")]
    for f in feats:
        acc = {("secim", "ust"): [0, 0, 0, 0], ("secim", "alt"): [0, 0, 0, 0], ("h24", "ust"): [0, 0, 0, 0], ("h24", "alt"): [0, 0, 0, 0], ("secim", "taban"): [0, 0, 0, 0], ("h24", "taban"): [0, 0, 0, 0]}
        for s in names:
            F = ALL[s]
            if f not in F: continue
            a, b = per(F); x = F[f]; y = F.y8; ok = x.notna() & y.notna()
            if f.startswith("model_") or f == "btc_model_u4":
                hi = x == 1; lo = x == 0
            else:
                q = x[a & ok].quantile([0.1, 0.9]);
                if q.isna().any() or q.iloc[0] == q.iloc[1]: continue
                hi = x >= q.iloc[1]; lo = x <= q.iloc[0]
            for pn, pm in (("secim", a), ("h24", b)):
                for dn, dm in (("ust", hi), ("alt", lo), ("taban", pd.Series(True, index=F.index))):
                    m = pm & ok & dm; acc[(pn, dn)][0] += int(m.sum()); acc[(pn, dn)][1] += int((y[m] >= UP).sum()); acc[(pn, dn)][2] += int((y[m] <= DN).sum())
        for dn in ("ust", "alt"):
            r = {"grup": grup, "ozellik": f, "dilim": "en üst %10" if dn == "ust" else "en alt %10"}
            ok_ = True
            for pn in ("secim", "h24"):
                n, ku, kd, _ = acc[(pn, dn)]; nb, bu, bd, _ = acc[(pn, "taban")]
                if n < 200 or nb == 0: ok_ = False; break
                pu, pd_, bu_, bd_ = ku / n, kd / n, bu / nb, bd / nb
                r[f"{'≤2023' if pn == 'secim' else '2024+'} yükseliş %"] = 100 * pu; r[f"{'≤2023' if pn == 'secim' else '2024+'} kat"] = pu / bu_
                r[f"{'≤2023' if pn == 'secim' else '2024+'} düşüş kat"] = pd_ / bd_
            if not ok_: continue
            r["YÖNLÜ & TUTARLI"] = bool(r["≤2023 kat"] >= 1.3 and r["2024+ kat"] >= 1.3 and r["≤2023 kat"] - r["≤2023 düşüş kat"] >= 0.2 and r["2024+ kat"] - r["2024+ düşüş kat"] >= 0.2)
            out.append(r)
    return pd.DataFrame(out)
R1 = analiz(["BTCUSDT"], "BTC"); R2 = analiz([s for s in ALL if s != "BTCUSDT"], "coin'ler")
for R, ad in ((R1, "BTC"), (R2, "Coin'ler (birlikte)")):
    R = R.assign(guc=R[["≤2023 kat", "2024+ kat"]].min(axis=1)).sort_values("guc", ascending=False)
    yaz(f"\n## {ad}: yükselişten önce en çok öne çıkan durumlar (kat = yükseliş olasılığı / taban · düşüş kat > 1 ise oynaklık etkisi de var)\n```\n" + R.head(20).round(2).to_string(index=False) + "\n```")
    Y = R[R["YÖNLÜ & TUTARLI"]]; yaz(f"Yönlü ve iki dönemde tutarlı ({len(Y)}): " + (", ".join(f"{a} [{b}]" for a, b in zip(Y.ozellik, Y.dilim)) or "yok"))
# ---- saat ve gün ----
rows = []
for s, F in ALL.items():
    a, b = per(F)
    for pn, pm in (("≤2023", a), ("2024+", b)):
        G = F[pm & F.y8.notna()]; rows.append(G.assign(p=pn, up=(G.y8 >= UP), dn=(G.y8 <= DN))[["p", "saat", "gun", "up", "dn"]])
Z = pd.concat(rows); Z["saat_tr"] = (Z.saat + 3) % 24
S_ = Z.groupby(["saat_tr", "p"]).up.mean().unstack().mul(100).round(1); D_ = Z.groupby(["gun", "p"]).up.mean().unstack().mul(100).round(1); D_.index = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
yaz("\n## Saat (TR, sinyal saati) ve gün: 8 saatte ≥ +%2 yükseliş olasılığı (%, tüm varlıklar)\n```\n" + S_.T.to_string() + "\n```\n```\n" + D_.T.to_string() + "\n```")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_"); open("yukselis_sonuc.md", "w").write("\n".join(L) + "\n")
