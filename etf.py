# etf.py — "KARANLIK ODA" İZLERİ: ABD spot ETF günlük para akışı (kurumsal alım OTC/Coinbase Prime üzerinden ETF'e girer) ve CFTC haftalık kurumsal pozisyon raporu (CME vadeli).
# Veri: Farside (BTC ve ETH ETF günlük net akış, milyon $, 2024-01'den) · CFTC TFF (Traders in Financial Futures, CME Bitcoin ve Ether: varlık yöneticileri / kaldıraçlı fonlar, 2018'den).
# A) TEK BAŞINA (önceden sabit):
#   ETF: günlük akış z (son 60 işlem günü) ≥ 1,5 → AL · ≤ −1,5 → SAT · 3 günlük toplam z ≥ 1,5 / ≤ −1,5 · giriş: akış gününün ERTESİ günü kapanışı (Farside gece yayımlar), 1 / 3 / 7 gün tut.
#     ETF verisi yalnız 2024'ten → seçim 2024 · doğrulama 2025+ · 2026 ayrıca.
#   CFTC: varlık yöneticisi net uzun (açık pozisyona oranı) haftalık değişim z (52 hafta) ≥ 1,5 / ≤ −1,5 · kaldıraçlı fonlar aynı · yön seçimden · giriş: rapor (salı) + 3 gün (cuma yayımı) kapanışı, 7 / 14 gün.
#     Seçim ≤2023 · doğrulama 2024+.
# B) FİLTRE: canlıda mesajı giden AL sinyalleri (filtre_hepsi.py ile aynı olaylar) — "kötü" koşul: E1 dün ETF'ten net çıkış · E2 dünkü akış z ≤ −1 · E3 son 5 işlem günü toplamı < 0 ·
#    C1 son CFTC raporunda varlık yöneticileri net uzunu azaltmış · C2 kaldıraçlı fonlar net uzunu artırmış (z ≥ 1).  ETF filtreleri: seçim 2024, doğrulama 2025+.  CFTC: seçim 2022-06→2023, doğrulama 2024+.
import os, io, re, json, glob, time, gzip, pickle, zipfile, requests, numpy as np, pandas as pd
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36", "Accept-Language": "en-US,en;q=0.9"}
def farside(url):
    try:
        r = requests.get(url, headers=UA, timeout=60)
        if r.status_code != 200: print(url, r.status_code); return None
        for t in pd.read_html(io.StringIO(r.text)):
            t.columns = [" ".join(map(str, c)) if isinstance(c, tuple) else str(c) for c in t.columns]
            tc = [c for c in t.columns if "Total" in c]
            if not tc: continue
            d = pd.to_datetime(t.iloc[:, 0], format="%d %b %Y", errors="coerce")
            v = t[tc[0]].astype(str).str.replace(",", "").str.replace("(", "-").str.replace(")", "").replace({"-": np.nan, "nan": np.nan})
            s = pd.Series(pd.to_numeric(v, errors="coerce").values, index=d).dropna(); s = s[s.index.notna()]
            if len(s) > 100: s.index = pd.DatetimeIndex(s.index).tz_localize("UTC"); return s[~s.index.duplicated()].sort_index()
    except Exception as e: print(url, e)
    return None
def ishares(pid, slug, ad):                                                                              # Farside kapalıysa: iShares (IBIT / ETHA) günlük pay sayısı × NAV → akış (milyon $)
    url = f"https://www.ishares.com/us/products/{pid}/{slug}/1521942788811.ajax?fileType=xls&fileName={ad}_fund&dataType=fund"
    try:
        sy = requests.get(f"https://www.ishares.com/us/products/{pid}/{slug}", headers=UA, timeout=90).text
        lk = sorted(set(re.findall(r'["\']([^"\'\s]*\.ajax\?fileType=(?:xls|csv)[^"\'\s]*)["\']', sy))); print(ad, "indirme bağlantıları:", lk[:8])
        fx = [u for u in lk if "fileType=xls" in u and "_fund" in u]
        if fx: url = "https://www.ishares.com" + fx[0].replace("&amp;", "&") if fx[0].startswith("/") else fx[0].replace("&amp;", "&")
        r = requests.get(url, headers=UA, timeout=90); print(ad, url, r.status_code, len(r.content))
        if r.status_code != 200: return None
        b = r.content; print("ilk baytlar:", b[:16])
        x = b.decode("utf-16") if b[:2] in (b"\xff\xfe", b"\xfe\xff") else b.decode("utf-8-sig", errors="ignore")
        print("başı:", repr(x[:200])); print("sayfalar:", re.findall(r'Worksheet\s+ss:Name="([^"]+)"', x), "| 'Shares Outstanding' sayısı:", x.count("Shares Outstanding"))
        w = re.search(r'Worksheet\s+ss:Name="Historical".*?</ss:Worksheet>', x, re.S)
        if not w: return None
        R = [[re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<ss:Cell[^>]*>(.*?)</ss:Cell>", row, re.S)] for row in re.findall(r"<ss:Row[^>]*>(.*?)</ss:Row>", w.group(0), re.S)]
        h = next(i for i, rr in enumerate(R) if any("Shares Outstanding" in c for c in rr)); H_ = R[h]; print("başlık:", H_, "| ilk:", R[h + 1][:6], "| son:", R[-1][:6])
        D = pd.DataFrame([rr[:len(H_)] for rr in R[h + 1:] if len(rr) >= len(H_)], columns=H_)
        num = lambda c: pd.to_numeric(D[[k for k in H_ if c in k][0]].str.replace(",", "").str.replace("$", ""), errors="coerce")
        t = pd.to_datetime(D[H_[0]], errors="coerce", format="mixed"); so, nav = num("Shares Outstanding"), num("NAV")
        s = pd.DataFrame({"so": so.values, "nav": nav.values}, index=t).dropna(); s = s[s.index.notna()].sort_index(); s = s[~s.index.duplicated()]
        f_ = (s.so.diff() * s.nav / 1e6).dropna(); f_.index = pd.DatetimeIndex(f_.index).tz_localize("UTC"); return f_ if len(f_) > 100 else None
    except Exception as e: print(ad, "hata", e); return None
def bgeo_etf():                                                                                        # BGeometrics ücretsiz API: tüm ABD spot BTC ETF'leri günlük akış (anahtar yok, günde 15 istek)
    f_ = "veri_bgeo/etf-flow-btc.json"; os.makedirs("veri_bgeo", exist_ok=True)
    try:
        if not (os.path.exists(f_) and time.time() - os.path.getmtime(f_) < 20 * 3600):
            r = requests.get("https://bitcoin-data.com/v1/etf-flow-btc", timeout=60, headers={"User-Agent": "btc-tahmin-arastirma"}); print("bgeo etf", r.status_code, len(r.content))
            if r.status_code == 200 and r.text.lstrip().startswith("["): open(f_, "w").write(r.text)
        J = pd.DataFrame(json.load(open(f_))); print("bgeo alanlar:", list(J.columns), "| son:", J.iloc[-1].to_dict())
        sy = [c for c in J.columns if c not in ("d", "unixTs")]; N = J[sy].apply(pd.to_numeric, errors="coerce")
        tc = [c for c in sy if "total" in c.lower()] or ([sy[0]] if len(sy) == 1 else [])
        v = N[tc[0]] if tc else N.sum(axis=1, min_count=1); s = pd.Series(v.values, index=pd.to_datetime(J.d).dt.tz_localize("UTC")).dropna().sort_index()
        print("bgeo seçilen:", tc or "toplam(" + ",".join(sy) + ")"); return s[~s.index.duplicated()] if len(s) > 100 else None
    except Exception as e: print("bgeo hata", e); return None
ETF = {"BTC": farside("https://farside.co.uk/bitcoin-etf-flow-all-data/"), "ETH": farside("https://farside.co.uk/ethereum-etf-flow-all-data/")}
KAYNAK = {k: "Farside (tüm ABD spot ETF'leri)" for k, v in ETF.items() if v is not None}
if ETF["BTC"] is None:
    ETF["BTC"] = bgeo_etf(); KAYNAK["BTC"] = "BGeometrics (tüm ABD spot BTC ETF'leri)"
for a, pid, slug, ad in (("BTC", 333011, "ishares-bitcoin-trust-etf", "iShares-Bitcoin-Trust-ETF"), ("ETH", 337614, "ishares-ethereum-trust-etf", "iShares-Ethereum-Trust-ETF")):
    if ETF[a] is None: ETF[a] = ishares(pid, slug, ad); KAYNAK[a] = "iShares " + ("IBIT" if a == "BTC" else "ETHA") + " (en büyük ETF, pay sayısı değişimi × NAV)"
def cftc():
    rows = []
    for y in range(2018, pd.Timestamp.now().year + 1):
        try:
            r = requests.get(f"https://www.cftc.gov/files/dea/history/fut_fin_txt_{y}.zip", headers=UA, timeout=90)
            if r.status_code != 200: print("cftc", y, r.status_code); continue
            z = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z.open(z.namelist()[0]), low_memory=False); rows.append(d)
        except Exception as e: print("cftc", y, e)
    if not rows: return None
    D = pd.concat(rows, ignore_index=True); D.columns = [c.strip() for c in D.columns]; return D
TFF = cftc()
COT = {}
if TFF is not None:
    mcol = [c for c in TFF.columns if c.startswith("Market_and_Exchange_Names")][0]; dcol = [c for c in TFF.columns if "YYYY-MM-DD" in c][0]
    for a, pat in (("BTC", r"^BITCOIN - CHICAGO MERCANTILE"), ("ETH", r"^ETHER CASH SETTLED - CHICAGO MERCANTILE|^ETHER - CHICAGO MERCANTILE")):
        x = TFF[TFF[mcol].astype(str).str.match(pat)].copy()
        if x.empty: continue
        x.index = pd.to_datetime(x[dcol]).dt.tz_localize("UTC"); x = x.sort_index(); x = x[~x.index.duplicated()]
        g = lambda c: pd.to_numeric(x[c], errors="coerce")
        oi = g("Open_Interest_All"); am = (g("Asset_Mgr_Positions_Long_All") - g("Asset_Mgr_Positions_Short_All")) / oi; lm = (g("Lev_Money_Positions_Long_All") - g("Lev_Money_Positions_Short_All")) / oi
        COT[a] = pd.DataFrame({"am": am, "lm": lm})
yaz(f"# 🕶️ Karanlık oda izleri: ETF akışı ve CFTC kurumsal pozisyonları — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}")
for a in ("BTC", "ETH"):
    s = ETF.get(a); c = COT.get(a)
    yaz(f"- {a} ETF: " + ("alınamadı" if s is None else f"[{KAYNAK.get(a)}] {s.index[0]:%Y-%m-%d} → {s.index[-1]:%Y-%m-%d}, {len(s)} gün, son 5 gün toplam {s.iloc[-5:].sum():+,.0f} milyon $")
        + " · CFTC: " + ("yok" if c is None else f"{c.index[0]:%Y-%m-%d} → {c.index[-1]:%Y-%m-%d}, {len(c)} hafta, varlık yöneticisi net {c.am.iloc[-1]:+.1%}, kaldıraçlı fon net {c.lm.iloc[-1]:+.1%}"))
def gunluk(sym):
    rows, cur = [], int(pd.Timestamp("2017-12-01", tz="UTC").timestamp() * 1000)
    while True:
        r = requests.get(EP[0], params=dict(symbol=sym, interval="1d", startTime=cur, limit=1000), timeout=20).json()
        if not r: break
        rows += r; cur = r[-1][0] + 86_400_000
        if len(r) < 1000: break
    d = pd.DataFrame([x[:5] for x in rows], columns=["t", "o", "h", "l", "c"]).astype(float); return pd.Series(d.c.values, index=pd.to_datetime(d.t, unit="ms", utc=True))
PX = {"BTC": gunluk("BTCUSDT"), "ETH": gunluk("ETHUSDT")}
LMT = 0.0002
def ozet(net, DON, reps=800):
    out = {}
    for pn, a, b in DON:
        x = net[(net.index >= a) & (net.index < b)]; out[pn] = (len(x), 100 * (x > 0).mean() if len(x) else np.nan, 100 * x.mean() if len(x) else np.nan, 100 * wboot(x.values, x.index.values, reps)[0] if len(x) >= 8 else np.nan)
    return out
def fmt(o): return " · ".join(("—" if not np.isfinite(v) else (f"{v:.0f}" if i < 2 else f"{v:+.2f}")) for i, v in enumerate(o))
TS = lambda s: pd.Timestamp(s, tz="UTC")
D_ETF = (("seçim 2024", TS("2024-01-01"), TS("2025-01-01")), ("doğrulama 2025+", TS("2025-01-01"), TS("2030-01-01")), ("2026", TS("2026-01-01"), TS("2030-01-01")))
D_COT = (("seçim ≤2023", TS("2018-01-01"), TS("2024-01-01")), ("doğrulama 2024+", TS("2024-01-01"), TS("2030-01-01")), ("2026", TS("2026-01-01"), TS("2030-01-01")))
def gecti(o, D): s, d = o[D[0][0]], o[D[1][0]]; return bool(s[0] >= 8 and s[2] > 0 and d[0] >= 8 and d[2] > 0 and d[3] > 0)
rows = []
rng = np.random.default_rng(0); pl = [0, 0]
def test(ad, a, m, gecikme, HDs, D):
    px = PX[a]; ix = px.index
    for HD in HDs:
        y = px.shift(-(gecikme + HD)) / px.shift(-gecikme) - 1
        ev = ix[events(m.reindex(ix).fillna(False).values, HD)]; e1 = y.reindex(ev).dropna(); e1 = e1[(e1.index >= D[0][1]) & (e1.index < D[0][2])]
        if len(e1) < 5: continue
        yon = 1 if e1.mean() > 0 else -1; net = (yon * y.reindex(ev) - 2 * LMT).dropna(); o = ozet(net, D)
        rows.append(dict(coin=a, sinyal=ad, gun=HD, yon="AL" if yon > 0 else "SAT", **{pn: fmt(o[pn]) for pn, _, _ in D}, ok=gecti(o, D)))
        mv = m.reindex(ix).fillna(False).values
        for _ in range(10):
            sh = int(rng.integers(30, len(mv) - 30)); ev2 = ix[events(np.roll(mv, sh), HD)]; y2 = y.reindex(ev2).dropna(); e2 = y2[(y2.index >= D[0][1]) & (y2.index < D[0][2])]
            if len(e2) < 5: continue
            po = ozet((1 if e2.mean() > 0 else -1) * y2 - 2 * LMT, D, reps=200); pl[0] += 1; pl[1] += gecti(po, D)
for a in ("BTC", "ETH"):
    s = ETF.get(a)
    if s is not None:
        z1 = (s - s.rolling(60, min_periods=20).mean()) / (s.rolling(60, min_periods=20).std() + 1e-9); s3 = s.rolling(3).sum(); z3 = (s3 - s3.rolling(60, min_periods=20).mean()) / (s3.rolling(60, min_periods=20).std() + 1e-9)
        for ad, m in (("ETF akışı z ≥ 1,5", z1 >= 1.5), ("ETF akışı z ≤ −1,5", z1 <= -1.5), ("ETF 3 g toplam z ≥ 1,5", z3 >= 1.5), ("ETF 3 g toplam z ≤ −1,5", z3 <= -1.5)):
            test(ad, a, m, 1, (1, 3, 7), D_ETF)
    c = COT.get(a)
    if c is not None:
        for k, adk in (("am", "varlık yöneticisi"), ("lm", "kaldıraçlı fon")):
            d = c[k].diff(); zz = (d - d.rolling(52, min_periods=20).mean()) / (d.rolling(52, min_periods=20).std() + 1e-9); zz.index = zz.index + pd.Timedelta(days=3)   # cuma yayımı
            for ad, m in ((f"CFTC {adk} net uzun artışı z ≥ 1,5", zz >= 1.5), (f"CFTC {adk} net uzun azalışı z ≤ −1,5", zz <= -1.5)):
                test(ad, a, m, 0, (7, 14), D_COT)
R = pd.DataFrame(rows)
yaz(f"\n## A) Tek başına sinyal\nToplam {len(R)} deneme · ✅ geçen **{int(R.ok.sum()) if len(R) else 0}** · plasebo geçme oranı %{100*pl[1]/max(1,pl[0]):.1f} → tesadüfen ≈ {pl[1]/max(1,pl[0])*len(R):.1f}\n_işlem · isabet % · işlem başı net % · alt sınır %_")
for D, ad in ((D_ETF, "ETF"), (D_COT, "CFTC")):
    G = R[R.sinyal.str.startswith(ad)]
    if len(G): yaz(f"```\n" + G[["coin", "sinyal", "gun", "yon"] + [pn for pn, _, _ in D] + ["ok"]].to_string(index=False) + "\n```")
# ---- B) filtre: mevcut sinyallere ----
fh = open("filtre_hepsi.py").read(); _k = fh[fh.index("f = lambda p"):fh.index("# ---------- durum değişkenleri ----------")]; _k = re.sub(r"\nyaz\(f\"# 🔎.*?\n", "\n", _k, flags=re.S); exec(_k)     # E: olaylar (aile, coin, t, r, H)
E["net"] = E.r - 2 * LMT; E["ok"] = E.r > 0; tt = pd.DatetimeIndex(E.t); E["hafta"] = tt.floor("7D")
def asof(s, t):
    if s is None: return np.full(len(t), np.nan)
    s = s.dropna(); s.index = pd.DatetimeIndex(s.index).as_unit("ns")
    L_ = pd.DataFrame({"t": pd.DatetimeIndex(t).as_unit("ns"), "i": np.arange(len(t))}).sort_values("t")
    return pd.merge_asof(L_, pd.DataFrame({"t": s.index, "v": s.values.astype(float)}), on="t", direction="backward").sort_values("i").v.values
gun_once = (tt - pd.Timedelta(hours=14)).floor("D") - pd.Timedelta(days=1)   # T günü akışı ancak T+1 14:00 UTC'den sonra kullanılır (temkinli)                                                         # dünün (ABD günü) akışı: sinyal gününden önce bilinen
sb = ETF.get("BTC"); E["etf"] = asof(sb, gun_once); E["etf_z"] = asof((sb - sb.rolling(60, min_periods=20).mean()) / (sb.rolling(60, min_periods=20).std() + 1e-9) if sb is not None else None, gun_once)
E["etf5"] = asof(sb.rolling(5).sum() if sb is not None else None, gun_once)
cb = COT.get("BTC")
if cb is not None:
    am_d = cb.am.diff(); am_d.index = am_d.index + pd.Timedelta(days=4); lm_d = cb.lm.diff(); lmz = (lm_d - lm_d.rolling(52, min_periods=20).mean()) / (lm_d.rolling(52, min_periods=20).std() + 1e-9); lmz.index = lmz.index + pd.Timedelta(days=4)
    E["am_d"] = asof(am_d, tt); E["lm_z"] = asof(lmz, tt)
else: E["am_d"] = np.nan; E["lm_z"] = np.nan
KOT = {"E1 dün ETF'ten net çıkış": (E.etf < 0, "etf"), "E2 dünkü ETF akışı z ≤ −1": (E.etf_z <= -1, "etf"), "E3 son 5 gün ETF toplamı < 0": (E.etf5 < 0, "etf"),
       "C1 varlık yöneticileri net uzunu azaltmış": (E.am_d < 0, "cot"), "C2 kaldıraçlı fonlar net uzunu artırmış (z ≥ 1)": (E.lm_z >= 1, "cot")}
def fark_boot(ok, kotu, hafta, reps=1000):
    d = pd.DataFrame({"ok": ok.astype(float), "k": kotu.astype(bool), "h": hafta})
    C = pd.DataFrame({"ni": (~d.k).groupby(d.h).sum(), "oi": (d.ok * ~d.k).groupby(d.h).sum(), "nk": d.k.groupby(d.h).sum(), "ok_": (d.ok * d.k).groupby(d.h).sum()}).values.astype(float)
    idx = rng.integers(0, len(C), (reps, len(C))); S_ = C[idx].sum(axis=1)
    with np.errstate(all="ignore"): fr = 100 * (S_[:, 1] / S_[:, 0] - S_[:, 3] / S_[:, 2])
    fr = fr[np.isfinite(fr)]; return np.percentile(fr, 5) if len(fr) else np.nan
FD = {"etf": (("seçim 2024", TS("2024-01-01"), TS("2025-01-01")), ("doğrulama 2025+", TS("2025-01-01"), TS("2030-01-01")), ("2026", TS("2026-01-01"), TS("2030-01-01"))),
      "cot": (("seçim 22-06→23", TS("2022-06-01"), TS("2024-01-01")), ("doğrulama 2024+", TS("2024-01-01"), TS("2030-01-01")), ("2026", TS("2026-01-01"), TS("2030-01-01")))}
FR_ = []
for aile, G in E.groupby("aile"):
    for kn, (kv, tur) in KOT.items():
        D = FD[tur]; k = kv.reindex(G.index).fillna(False).astype(bool); gt = pd.DatetimeIndex(G.t); r = {}
        for pn, a, b in D:
            m = (gt >= a) & (gt < b); g, kk = G[m], k[m]
            r[pn] = dict(n=len(g), kn=int(kk.sum()), pay=100 * kk.mean() if len(g) else np.nan, iyi=100 * g.ok[~kk].mean() if (~kk).any() else np.nan, kot=100 * g.ok[kk].mean() if kk.any() else np.nan,
                         iyi_net=100 * g.net[~kk].mean() if (~kk).any() else np.nan, kot_net=100 * g.net[kk].mean() if kk.any() else np.nan)
            r[pn]["fark"] = r[pn]["iyi"] - r[pn]["kot"]
        m2 = (gt >= D[1][1]); alt = fark_boot(G.ok[m2].values, k[m2].values, G.hafta[m2].values) if k[m2].sum() >= 20 else np.nan
        s_, d_, z_ = r[D[0][0]], r[D[1][0]], r["2026"]
        ok = bool(5 <= d_["pay"] <= 60 and s_["fark"] >= 2 and d_["fark"] >= 3 and alt > 0 and (z_["kn"] < 20 or z_["fark"] > 0))
        FR_.append(dict(aile=aile, filtre=kn, kotu_pay=round(d_["pay"], 1), secim=f"{s_['iyi']:.0f} / {s_['kot']:.0f} ({s_['kn']})", dogrulama=f"{d_['iyi']:.0f} / {d_['kot']:.0f} ({d_['kn']}) · net {d_['iyi_net']:+.2f} / {d_['kot_net']:+.2f}",
                        alt=round(alt, 2) if np.isfinite(alt) else np.nan, y2026=f"{z_['iyi']:.0f} / {z_['kot']:.0f} ({z_['kn']})", ok="✅" if ok else "❌"))
F = pd.DataFrame(FR_)
yaz(f"\n## B) Filtre olarak (iyi / kötü isabet %, kötü işlem sayısı) — {int((F.ok=='✅').sum())} / {len(F)} geçti\n```\n" + F.to_string(index=False) + "\n```")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("etf_sonuc.md", "w").write("\n".join(L) + "\n")
