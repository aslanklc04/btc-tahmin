# kesit.py — COİN'LER ARASI SIRALAMA: "piyasa çıkar mı?" yerine "hangi coin diğerlerinden iyi gidecek?" (canlı sisteme dokunmaz)
# Her H saatte bir (sabit saatler) coin'ler bir ölçüte göre sıralanır, en iyi 3 coin alınır, H saat tutulur, sonra yeniden sıralanır.
# Kurallar ÖNCEDEN sabit (yukselis.py: coin'lerde düşenin toparlanması, BTC'de trend):
#   TOPARLANMA: son 4 / 24 / 72 saatte EN ÇOK düşen 3 coin · TOPARLANMA-z: 24 saatlik düşüş / 7 günlük oynaklık
#   TREND: son 7 / 30 günde EN ÇOK yükselen 3 coin
# Tutma: 8 ve 24 saat · İki biçim: yalnız alım (spot/vadeli long) ve nötr (en iyi 3 al + en kötü 3 sat; piyasa yönünden bağımsız).
# Komisyon yalnız DEĞİŞEN pozisyonlara: vadeli taker %0,05 · limit %0,02 (her yön). Giriş: sinyal saatinin kapanışı (0 s) ve 1 saat sonrası (gecikme dayanıklılığı).
# Seçim 2020–23 (en iyi kural burada seçilir), karar 2024+. Not: evren bugün yaşayan coin'ler → hayatta kalma yanlılığı (ölen coin'ler yok).
import os, time, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
SYMS = ["ETHUSDT", "BNBUSDT", "DOGEUSDT", "SHIBUSDT", "DOTUSDT", "ADAUSDT", "LINKUSDT", "NEARUSDT", "AVAXUSDT", "ARBUSDT", "OPUSDT", "APTUSDT", "SUIUSDT",
        "PEPEUSDT", "FLOKIUSDT", "INJUSDT", "FETUSDT", "XRPUSDT", "SOLUSDT", "LTCUSDT", "TRXUSDT", "ATOMUSDT", "UNIUSDT", "BCHUSDT", "ETCUSDT", "FILUSDT"]
def kl(sym):
    end = int(time.time() * 1000); rows = []
    for url in EP:
        try:
            rows, cur = [], int(pd.Timestamp("2017-08-17", tz="UTC").timestamp() * 1000)
            while cur < end:
                r = requests.get(url, params=dict(symbol=sym, interval="1h", startTime=cur, endTime=end, limit=1000), timeout=20); r.raise_for_status(); dt = r.json()
                if not dt: break
                rows += dt; cur = dt[-1][0] + 3_600_000
                if len(dt) < 1000: break
            if rows: break
        except Exception: rows = []
    if not rows: return sym, None
    d = pd.DataFrame([x[:6] for x in rows], columns=["t", "open", "high", "low", "close", "volume"]).astype(float)
    d.index = pd.to_datetime(d.t, unit="ms", utc=True) + pd.Timedelta(hours=1); d = d[d.index <= pd.Timestamp.now(tz="UTC")]
    return sym, d[~d.index.duplicated()].sort_index().close
if os.environ.get("YEREL"):
    _O = pd.read_pickle("/home/claude/lab2/data/o_1h.pkl").close; _rg = np.random.default_rng(0)
    def kl(sym): return sym, _O * np.exp(np.cumsum(_rg.normal(0, 0.01, len(_O))))
    SYMS = SYMS[:8]
with ThreadPoolExecutor(8) as ex: K = {s: c for s, c in ex.map(kl, SYMS) if c is not None and len(c) > 2000}
C = pd.DataFrame(K).sort_index(); C = C.reindex(pd.date_range(C.index[0], C.index[-1], freq="1h", tz="UTC")).ffill(limit=3)
yaz(f"# 🔀 Coin'ler arası sıralama — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nVeri: {C.shape[1]} coin · {C.index[0]:%Y-%m} → {C.index[-1]:%Y-%m-%d %H:%M} UTC · {time.time()-T0:.0f} sn\n")
LR = np.log(C); YAS = C.notna().cumsum()                                              # coin'in kaç saattir listede olduğu
VOL = LR.diff().rolling(168, min_periods=100).std()
OLC = {"TOPARLANMA 4s": -(LR - LR.shift(4)), "TOPARLANMA 24s": -(LR - LR.shift(24)), "TOPARLANMA 72s": -(LR - LR.shift(72)),
       "TOPARLANMA-z 24s": -(LR - LR.shift(24)) / (VOL * np.sqrt(24)), "TREND 7g": LR - LR.shift(168), "TREND 30g": LR - LR.shift(720)}
A0, A24 = pd.Timestamp("2020-01-01", tz="UTC"), pd.Timestamp("2024-01-01", tz="UTC"); KK = 3
FEES = {"vadeli %0,05": 0.0005, "limit %0,02": 0.0002}
CI = C.index; CV = C.values; YV = YAS.values
def calis(sc, H, d, notr):
    SV = sc.reindex(columns=C.columns).values; rows = []; prevL, prevS = set(), set()
    idx = np.where((CI >= A0) & (CI.hour % H == 0))[0]; idx = idx[idx + H + d < len(CI)]
    for i in idx:
        p0, p1, s = CV[i + d], CV[i + H + d], SV[i]; gall = p1 / p0 - 1
        ok = (YV[i] >= 720) & np.isfinite(s) & np.isfinite(gall)
        if ok.sum() < 2 * KK + 2: continue
        cols = np.where(ok)[0]; order = cols[np.argsort(-s[cols], kind="stable")]; Lg, Sg = set(order[:KK].tolist()), set(order[-KK:].tolist())
        gl = gall[list(Lg)]; sep = gall[cols].mean(); gs = gall[list(Sg)].mean() if notr else 0.0
        dL = len(Lg - prevL) + len(prevL - Lg); dS = (len(Sg - prevS) + len(prevS - Sg)) if notr else 0
        rows.append((CI[i], gl.mean() - gs, sep, gl.mean() - sep, (gl > 0).mean(), (gl > sep).mean(), (dL + dS) / KK, len(Lg - prevL) + (len(Sg - prevS) if notr else 0)))
        prevL, prevS = Lg, (Sg if notr else set())
    return pd.DataFrame(rows, columns=["t", "brut", "sepet", "fazla", "isabet", "gecti", "degisen", "yeni"])
out = []; SERI = {}
for ad, sc in OLC.items():
    for H in (8, 24):
        for notr in (False, True):
            for d in (0, 1):
                T = calis(sc, H, d, notr); key = (ad, H, "nötr" if notr else "alım", d); SERI[key] = T
                for pn, (a, b) in {"2020–23": (A0, A24), "2024+": (A24, C.index[-1])}.items():
                    x = T[(T.t >= a) & (T.t < b)]
                    if len(x) < 30: continue
                    wk = (b - a).days / 7; yrs = (b - a).days / 365.25
                    r = dict(kural=ad, tut=H, bicim=key[2], gecikme=d, donem=pn, yeniden=len(x), yeni_islem_hafta=x.yeni.sum() / wk, isabet=100 * x.isabet.mean(), sepeti_gecti=100 * x.gecti.mean(),
                             brut=100 * x.brut.mean(), fazla=100 * x.fazla.mean())
                    for fn, fee in FEES.items():
                        net = x.brut.values - fee * x.degisen.values; e = np.cumprod(1 + net); lo, hi = wboot(net, x.t.values)
                        nx = (x.brut.values if notr else x.fazla.values) - fee * x.degisen.values; lx, _ = wboot(nx, x.t.values); r[f"fnet {fn}"] = 100 * nx.mean(); r[f"falt {fn}"] = 100 * lx
                        r[f"net {fn}"] = 100 * net.mean(); r[f"alt {fn}"] = 100 * lo; r[f"yıllık {fn}"] = 100 * (e[-1] ** (1 / yrs) - 1); r[f"maxDD {fn}"] = 100 * (e / np.maximum.accumulate(np.r_[1, e])[1:] - 1).min()
                    out.append(r)
    yaz(f"… {ad} bitti ({time.time()-T0:.0f} sn)")
S = pd.DataFrame(out)
# sepet (eşit ağırlık, hep tut) — karşılaştırma
for pn, (a, b) in {"2020–23": (A0, A24), "2024+": (A24, C.index[-1])}.items():
    T = SERI[("TREND 7g", 24, "alım", 0)]; x = T[(T.t >= a) & (T.t < b)]; e = np.cumprod(1 + x.sepet.values); yrs = (b - a).days / 365.25
    yaz(f"Karşılaştırma — tüm coin'ler eşit, al-tut ({pn}): yıllık %{100*(e[-1]**(1/yrs)-1):.1f}, maxDD %{100*(e/np.maximum.accumulate(e)-1).min():.1f}")
cols = ["yeniden", "yeni_islem_hafta", "isabet", "sepeti_gecti", "brut", "fazla", "net vadeli %0,05", "net limit %0,02", "fnet limit %0,02", "falt limit %0,02", "yıllık vadeli %0,05", "yıllık limit %0,02", "maxDD vadeli %0,05"]
for d in (0, 1):
    for pn in ("2020–23", "2024+"):
        x = S[(S.gecikme == d) & (S.donem == pn)].copy(); x["ad"] = x.kural + " · " + x.tut.astype(str) + "s · " + x.bicim
        yaz(f"\n## {pn} · giriş {'sinyal saati kapanışı' if d == 0 else '1 saat gecikmeli'}\n```\n" + x.set_index("ad")[cols].round(3).to_string() + "\n```")
# ---- seçim → karar (önceden sabit): 2020–23'te 1 saat gecikmeli, limit komisyonlu net'i en yüksek 3 kural → 2024+ ----
yaz("\n## Karar: 2020–23'te SEPETİ EN ÇOK GEÇEN 3 kural (1 saat gecikme, limit komisyon sonrası) → 2024+ · ölçüt: sepet-üstü net > 0 ve alt sınır > 0\n(sepet-üstü: alım biçiminde 'tüm coin'leri eşit tutmaya göre fazla', nötrde kendisi — piyasa yükseldi diye kazanmak sayılmaz)")
z = S[(S.gecikme == 1)].copy(); z["ad"] = z.kural + " · " + z.tut.astype(str) + "s · " + z.bicim
sec = z[z.donem == "2020–23"].sort_values("fnet limit %0,02", ascending=False).head(3).ad
for a_ in sec:
    p = z[(z.ad == a_) & (z.donem == "2020–23")].iloc[0]; q = z[(z.ad == a_) & (z.donem == "2024+")]
    if not len(q): continue
    q = q.iloc[0]; ok = q["fnet limit %0,02"] > 0 and q["falt limit %0,02"] > 0
    yaz(f"- {'✅' if ok else '❌'} {a_}: sepet-üstü net 2020–23 %{p['fnet limit %0,02']:.3f} → 2024+ %{q['fnet limit %0,02']:.3f} (alt %{q['falt limit %0,02']:.3f}) · mutlak net 2024+ %{q['net limit %0,02']:.3f} · haftada {q.yeni_islem_hafta:.0f} yeni alım · isabet %{q.isabet:.0f} · sepeti geçme %{q.sepeti_gecti:.0f} · yıllık %{q['yıllık limit %0,02']:.0f} · maxDD %{q['maxDD vadeli %0,05']:.0f}")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn · brüt/net = her yeniden sıralama dönemi başına portföy getirisi % · fazla = seçilenlerin tüm coin ortalamasına göre fazlası (komisyon öncesi) · fnet/falt = sepet-üstü net ve alt sınırı · isabet = seçilen coin'lerin yükselme oranı · alt = haftalık blok bootstrap %90 alt sınırı_")
open("kesit_sonuc.md", "w").write("\n".join(L) + "\n")
