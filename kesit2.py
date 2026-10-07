# kesit2.py — COİN SIRALAMASI, HAYATTA KALMA YANLILIĞI OLMADAN (canlı sisteme dokunmaz)
# kesit.py bugün yaşayan 26 coin'le yapıldı → çöken/listeden çıkan coin'ler (LUNA, FTT, …) yoktu, sonuç olduğundan iyi görünebilir.
# Burada: Binance arşivindeki TÜM USDT çiftleri (listeden çıkanlar dahil). Her yeniden sıralama anında, o an işlem gören ve son 30 günde
# EN ÇOK İŞLEM HACMİ olan 20 coin evreni oluşturur (geleceği bilmeden). Pozisyondaki coin listeden çıkarsa son işlem fiyatından kapanır.
# Kurallar ve ölçütler kesit.py ile aynı (önceden sabit). ÖNCEDEN BELİRLENEN ana hipotez: "TREND 30g · 24s · alım" (kesit.py'de geçen kural).
# Veri: aylık 1 saatlik arşivler (bu ayın günleri hariç → veri geçen ayın sonunda biter).
import os, io, re, time, zipfile, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"; BV = "https://data.binance.vision/"
def s3_list(prefix):
    out, marker = [], ""
    while True:
        for _ in range(4):
            try: r = requests.get(S3, params=dict(delimiter="/", prefix=prefix, marker=marker), timeout=60); r.raise_for_status(); break
            except Exception: time.sleep(3)
        x = r.text; pre = re.findall(r"<Prefix>([^<]+)</Prefix>", x)[1:]; keys = re.findall(r"<Key>([^<]+)</Key>", x)
        out += pre + keys
        if "<IsTruncated>true</IsTruncated>" not in x or not (pre or keys): return out
        marker = (pre + keys)[-1]
STABLE = {"USDC", "BUSD", "TUSD", "FDUSD", "USDP", "PAX", "DAI", "UST", "USTC", "SUSD", "EUR", "GBP", "AUD", "AEUR", "EURI", "USDS", "USDSB", "BKRW", "IDRT", "BIDR", "XUSD", "USD1", "PAXG", "WBTC", "WBETH", "BETH", "RLUSD", "USDE"}
UNDER = {"BTC", "ETH", "BNB", "XRP", "ADA", "DOT", "LINK", "LTC", "TRX", "EOS", "XTZ", "BCH", "YFI", "UNI", "SUSHI", "AAVE", "FIL", "SXP", "1INCH", "XLM"}
def kaldirac(b): return (b.endswith("UP") and b[:-2] in UNDER) or (b[-4:] in ("DOWN", "BULL", "BEAR") and b[:-4] in UNDER)
YEREL = bool(os.environ.get("YEREL"))
if YEREL:
    _O = pd.read_pickle("/home/claude/lab2/data/o_1h.pkl"); _rg = np.random.default_rng(0); SYMS = [f"C{i}USDT" for i in range(40)]
    def yukle(sym):
        n = len(_O); a = _rg.integers(0, n // 2); b = n if _rg.random() < 0.7 else _rg.integers(a + 3000, n)
        c = _O.close.values * np.exp(np.cumsum(_rg.normal(0, 0.012, n))); q = _O.volume.values * c * _rg.uniform(0.1, 3)
        return sym, pd.DataFrame({"c": c[a:b], "q": q[a:b]}, index=_O.index[a:b])
else:
    syms = [p.split("/")[-2] for p in s3_list("data/spot/monthly/klines/")]
    SYMS = sorted(s for s in syms if s.endswith("USDT") and s[:-4] not in STABLE and not kaldirac(s[:-4]))
    yaz(f"Arşivde {len(syms)} sembol · USDT çifti (sabit/kaldıraçlı hariç): {len(SYMS)} · {time.time()-T0:.0f} sn")
    def zip1(key):
        for _ in range(3):
            try:
                r = requests.get(BV + key, timeout=60)
                if r.status_code == 404: return None
                r.raise_for_status(); z = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=[0, 4, 7])
                ot = pd.to_numeric(d[0], errors="coerce"); ok = ot.notna(); ot = ot[ok].values.astype("float64"); ot = np.where(ot > 1e14, ot / 1000, ot)
                return pd.DataFrame({"c": pd.to_numeric(d[4][ok]).values, "q": pd.to_numeric(d[7][ok]).values}, index=pd.to_datetime(ot, unit="ms", utc=True) + pd.Timedelta(hours=1))
            except Exception: time.sleep(2)
        return None
    def yukle(sym):
        keys = [k for k in s3_list(f"data/spot/monthly/klines/{sym}/1h/") if k.endswith(".zip")]
        with ThreadPoolExecutor(6) as ex: parts = [p for p in ex.map(zip1, keys) if p is not None and len(p)]
        if not parts: return sym, None
        d = pd.concat(parts); return sym, d[~d.index.duplicated()].sort_index()
with ThreadPoolExecutor(1 if YEREL else 12) as ex: D = {s: d for s, d in ex.map(yukle, SYMS) if d is not None and len(d) > 720}
yaz(f"Yüklenen coin: {len(D)} · {time.time()-T0:.0f} sn")
idx = pd.date_range(min(d.index[0] for d in D.values()), max(d.index[-1] for d in D.values()), freq="1h", tz="UTC")
C = pd.DataFrame({s: d.c.reindex(idx) for s, d in D.items()}).astype("float32"); Q = pd.DataFrame({s: d.q.reindex(idx) for s, d in D.items()}).astype("float32"); del D
CF = C.ffill()                                                                                # listeden çıkan coin: son fiyat (yalnız tutulan pozisyon için)
LR = np.log(CF); VOLH = LR.diff().rolling(168, min_periods=100).std()
Q30 = Q.fillna(0).rolling(720, min_periods=720).sum(); YAS = C.notna().cumsum()
CANLI = C.notna() & (YAS >= 720) & (VOLH > 0.001)                                              # şu an işlem görüyor, ≥30 gün geçmişi var, sabit coin değil
OLC = {"TOPARLANMA 4s": -(LR - LR.shift(4)), "TOPARLANMA 24s": -(LR - LR.shift(24)), "TOPARLANMA 72s": -(LR - LR.shift(72)),
       "TOPARLANMA-z 24s": -(LR - LR.shift(24)) / (VOLH * np.sqrt(24)), "TREND 7g": LR - LR.shift(168), "TREND 30g": LR - LR.shift(720)}
A0, A24 = pd.Timestamp("2020-01-01", tz="UTC"), pd.Timestamp("2024-01-01", tz="UTC"); KK, NU = 3, 20
FEES = {"vadeli %0,05": 0.0005, "limit %0,02": 0.0002}
CI = C.index; CV = CF.values; QV = Q30.values; AV = CANLI.values; CR = C.values
EVREN = {}
for i in np.where(CI >= A0)[0]:
    if CI[i].hour % 8: continue
    ok = AV[i] & np.isfinite(QV[i]); c_ = np.where(ok)[0]
    if len(c_) >= NU: EVREN[i] = c_[np.argsort(-QV[i][c_])[:NU]]
ornek = {str(CI[i].date()): [C.columns[j][:-4] for j in EVREN[i][:NU]] for i in list(EVREN)[::1095][:8]}
yaz("Evren örnekleri (her an hacme göre ilk 20): " + " | ".join(f"{k}: {' '.join(v[:12])}…" for k, v in ornek.items()))
def calis(sc, H, d, notr):
    SV = sc.values; rows = []; prevL, prevS = set(), set()
    for i, U in EVREN.items():
        if CI[i].hour % H or i + H + d >= len(CI): continue
        p0, p1 = CV[i + d], CV[i + H + d]; gall = p1 / p0 - 1; s = SV[i]
        u = U[np.isfinite(s[U]) & np.isfinite(gall[U]) & np.isfinite(CR[i + d][U])]
        if len(u) < 2 * KK + 2: continue
        order = u[np.argsort(-s[u], kind="stable")]; Lg, Sg = set(order[:KK].tolist()), set(order[-KK:].tolist())
        gl = gall[list(Lg)]; sep = gall[u].mean(); gs = gall[list(Sg)].mean() if notr else 0.0
        dL = len(Lg - prevL) + len(prevL - Lg); dS = (len(Sg - prevS) + len(prevS - Sg)) if notr else 0
        rows.append((CI[i], gl.mean() - gs, sep, gl.mean() - sep, (gl > 0).mean(), (gl > sep).mean(), (dL + dS) / KK, len(Lg - prevL) + (len(Sg - prevS) if notr else 0)))
        prevL, prevS = Lg, (Sg if notr else set())
    return pd.DataFrame(rows, columns=["t", "brut", "sepet", "fazla", "isabet", "gecti", "degisen", "yeni"])
out = []; SERI = {}; END = CI[-1]
for ad, sc in OLC.items():
    for H in (8, 24):
        for notr in (False, True):
            for d in (0, 1):
                T = calis(sc, H, d, notr); key = (ad, H, "nötr" if notr else "alım", d); SERI[key] = T
                for pn, (a, b) in {"2020–23": (A0, A24), "2024+": (A24, END)}.items():
                    x = T[(T.t >= a) & (T.t < b)]
                    if len(x) < 30: continue
                    wk = (b - a).days / 7; yrs = (b - a).days / 365.25
                    r = dict(kural=ad, tut=H, bicim=key[2], gecikme=d, donem=pn, yeniden=len(x), yeni_islem_hafta=x.yeni.sum() / wk, isabet=100 * x.isabet.mean(), sepeti_gecti=100 * x.gecti.mean(),
                             brut=100 * x.brut.mean(), fazla=100 * x.fazla.mean())
                    for fn, fee in FEES.items():
                        net = x.brut.values - fee * x.degisen.values; e = np.cumprod(1 + net)
                        nx = (x.brut.values if notr else x.fazla.values) - fee * x.degisen.values; lx, _ = wboot(nx, x.t.values); r[f"fnet {fn}"] = 100 * nx.mean(); r[f"falt {fn}"] = 100 * lx
                        r[f"net {fn}"] = 100 * net.mean(); r[f"yıllık {fn}"] = 100 * (e[-1] ** (1 / yrs) - 1); r[f"maxDD {fn}"] = 100 * (e / np.maximum.accumulate(np.r_[1, e])[1:] - 1).min()
                    out.append(r)
    yaz(f"… {ad} bitti ({time.time()-T0:.0f} sn)")
S = pd.DataFrame(out)
for pn, (a, b) in {"2020–23": (A0, A24), "2024+": (A24, END)}.items():
    T = SERI[("TREND 30g", 24, "alım", 0)]; x = T[(T.t >= a) & (T.t < b)]; e = np.cumprod(1 + x.sepet.values); yrs = (b - a).days / 365.25
    yaz(f"Karşılaştırma — evrendeki 20 coin eşit, her gün yenilenir ({pn}): yıllık %{100*(e[-1]**(1/yrs)-1):.1f}, maxDD %{100*(e/np.maximum.accumulate(e)-1).min():.1f}")
cols = ["yeniden", "yeni_islem_hafta", "isabet", "sepeti_gecti", "brut", "fazla", "net vadeli %0,05", "net limit %0,02", "fnet limit %0,02", "falt limit %0,02", "yıllık vadeli %0,05", "yıllık limit %0,02", "maxDD vadeli %0,05"]
for d in (1, 0):
    for pn in ("2020–23", "2024+"):
        x = S[(S.gecikme == d) & (S.donem == pn)].copy(); x["ad"] = x.kural + " · " + x.tut.astype(str) + "s · " + x.bicim
        yaz(f"\n## {pn} · giriş {'sinyal saati kapanışı' if d == 0 else '1 saat gecikmeli'}\n```\n" + x.set_index("ad")[cols].round(3).to_string() + "\n```")
z = S[(S.gecikme == 1)].copy(); z["ad"] = z.kural + " · " + z.tut.astype(str) + "s · " + z.bicim
def satir(a_):
    p = z[(z.ad == a_) & (z.donem == "2020–23")]; q = z[(z.ad == a_) & (z.donem == "2024+")]
    if not len(p) or not len(q): return f"- {a_}: veri yok"
    p, q = p.iloc[0], q.iloc[0]; ok = q["fnet limit %0,02"] > 0 and q["falt limit %0,02"] > 0
    return (f"- {'✅' if ok else '❌'} {a_}: sepet-üstü net 2020–23 %{p['fnet limit %0,02']:.3f} → 2024+ %{q['fnet limit %0,02']:.3f} (alt %{q['falt limit %0,02']:.3f}) · mutlak net 2024+ %{q['net limit %0,02']:.3f}"
            f" · haftada {q.yeni_islem_hafta:.0f} yeni alım · isabet %{q.isabet:.0f} · sepeti geçme %{q.sepeti_gecti:.0f} · yıllık %{q['yıllık limit %0,02']:.0f} · maxDD %{q['maxDD vadeli %0,05']:.0f}")
yaz("\n## Ana hipotez (önceden belirlendi; 1 saat gecikme, limit komisyon) — ölçüt: 2024+ sepet-üstü net > 0 ve alt sınır > 0")
yaz(satir("TREND 30g · 24s · alım"))
yaz("\n## Ek: 2020–23'te sepeti en çok geçen 3 kural → 2024+")
for a_ in z[z.donem == "2020–23"].sort_values("fnet limit %0,02", ascending=False).head(3).ad: yaz(satir(a_))
yaz(f"\n_Süre: {time.time()-T0:.0f} sn · veri sonu {END:%Y-%m-%d} · brüt/net = her yeniden sıralama dönemi başına portföy getirisi % · fazla = seçilenlerin evren ortalamasına göre fazlası · fnet/falt = sepet-üstü net ve alt sınırı · alt = haftalık blok bootstrap %90_")
open("kesit2_sonuc.md", "w").write("\n".join(L) + "\n")
