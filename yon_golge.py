# yon_golge.py — 🧭 BTC YÖN GÖLGE İZLEME (30.10.2026, kullanıcı onayı). MESAJ GÖNDERMEZ, yalnız kayıt.
# Araştırma: arastirma3/PROTOKOL_btcyon3.md (Z2) ve PROTOKOL_btcyon4.md (W4). Parametreler donduruldu: durum/yon_golge_param.json (yon_golge_param.py).
#   🔻 NEG  : BTC 72 s yeni tepe yaparken kümülatif vadeli agresif alım önceki tepedekinden zayıf VE hareket penceresi (oynaklık 24s/720s ≥ eşik ya da sonraki saat 12–15 UTC) → 24 s SAT
#   🧮 W4   : birleşik ridge skoru (balina dengesizliği 4/24 s · Kore primi z ve 24 s değişim · USDT primi z ve 24 s değişim · kalabalık L/S z · dolar 5 g · vadeli uyumsuzluk) üst %10 → AL, alt %10 → SAT, 24 s
# Veri: Binance arşivi (data.binance.vision, bir gün gecikmeli) · Binance spot API · Upbit · Coinbase · Yahoo. Gölge bir gün geriden gelir; bu ölçüm için sorun değil (yalnız ileriye dönük kayıt).
# Kullanım: python yon_golge.py              → durum/yon_golge.csv · .md · _durum.json günceller
#           python yon_golge.py --gecmis A B → yon_golge_dogrula.csv (araştırmayla karşılaştırma için özellik + sinyal)
import io, sys, json, time, zipfile, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
S = requests.Session(); V = "https://data.binance.vision/data/futures/um"; T0 = time.time()
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
PRM = json.load(open("durum/yon_golge_param.json"))
BASLA = pd.Timestamp("2026-10-28", tz="UTC")                                                  # gölge kaydı başlangıcı (araştırma verisinin bittiği yer)
FON_8S, KAYMA, UCRET = 0.0001, 0.001, 0.001                                                   # fonlama yaklaşık %0,01/8 s (arşivde ay bitmeden yok) · kayma · ücret gidiş-dönüş
def log(*a): print(f"[{time.time() - T0:5.0f} sn]", *a, flush=True)
def get(u, **kw):
    for k in range(4):
        try:
            r = S.get(u, timeout=60, **kw)
            if r.status_code == 200: return r
            if r.status_code in (400, 404): return None
        except Exception: pass
        time.sleep(2 + 3 * k)
    return None
def zipcsv(u, cols):
    r = get(u)
    if r is None: return None
    z = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=cols)
    return d[pd.to_numeric(d[cols[0]], errors="coerce").notna()].astype(float)
def gunler(a, b): return pd.date_range(a.floor("D"), b.floor("D"), freq="D").strftime("%Y-%m-%d").tolist()
def vadeli_1s(a, b):
    with ThreadPoolExecutor(8) as ex: P = list(ex.map(lambda g: zipcsv(f"{V}/daily/klines/BTCUSDT/1h/BTCUSDT-1h-{g}.zip", [0, 1, 2, 3, 4, 7, 10]), gunler(a, b)))
    k = pd.concat([p for p in P if p is not None], ignore_index=True); k.columns = ["ot", "o", "h", "l", "c", "qv", "tb"]; k.loc[k.ot > 1e14, "ot"] = k.ot / 1000
    k.index = pd.to_datetime(k.ot, unit="ms", utc=True); return k[~k.index.duplicated()].sort_index().drop(columns="ot")
def balina(a, b):                                                                              # 1 dk → saatlik balina (önceki takvim ayının %95 işlem büyüklüğü eşiği)
    a0 = (a - pd.DateOffset(months=1)).replace(day=1)
    with ThreadPoolExecutor(8) as ex: P = list(ex.map(lambda g: zipcsv(f"{V}/daily/klines/BTCUSDT/1m/BTCUSDT-1m-{g}.zip", [0, 7, 8, 10]), gunler(a0, b)))
    M = pd.concat([p for p in P if p is not None], ignore_index=True); M.columns = ["ot", "qv", "n", "tb"]; M.loc[M.ot > 1e14, "ot"] = M.ot / 1000
    M = M.drop_duplicates("ot").sort_values("ot"); M["t"] = pd.to_datetime(M.ot, unit="ms", utc=True); M["ay"] = M.t.dt.strftime("%Y-%m"); M["boy"] = M.qv / M.n.clip(lower=1)
    M["esik"] = M.ay.map(M.groupby("ay").boy.quantile(0.95).shift(1)); w = M.boy >= M.esik
    M["wq"], M["wtb"] = np.where(w, M.qv, 0.0), np.where(w, M.tb, 0.0); g = M.groupby(M.t.dt.floor("h"))
    return pd.DataFrame({"wq": g.wq.sum(), "wtb": g.wtb.sum()})
def ls_gunluk(a, b):                                                                           # hesap L/S: saat içi ort. → günün son saati
    def bir(g):
        r = get(f"{V}/daily/metrics/BTCUSDT/BTCUSDT-metrics-{g}.zip")
        if r is None: return None
        z = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z.open(z.namelist()[0])); d.columns = [c.strip().lower() for c in d.columns]
        d["t"] = pd.to_datetime(d.create_time, utc=True).dt.floor("h"); h = d.groupby("t").count_long_short_ratio.mean(); return pd.Series([h.iloc[-1]], index=[h.index[-1].floor("D")]) if len(h) else None
    with ThreadPoolExecutor(8) as ex: P = [x for x in ex.map(bir, gunler(a, b)) if x is not None]
    return pd.concat(P).sort_index()
def spot_1s(a, b):
    R = []; s = int(a.timestamp() * 1000); e = int(b.timestamp() * 1000)
    while s < e:
        r = get("https://data-api.binance.vision/api/v3/klines", params=dict(symbol="BTCUSDT", interval="1h", startTime=s, limit=1000))
        if r is None or not r.json(): break
        j = r.json(); R += j; s = j[-1][0] + 3600_000
    d = pd.DataFrame(R).iloc[:, [0, 4]].astype(float); d.columns = ["ot", "c"]; d.index = pd.to_datetime(d.ot, unit="ms", utc=True); return d.c[~d.index.duplicated()]
def upbit(a, b):
    R = []; to = b
    while to > a:
        r = get("https://api.upbit.com/v1/candles/minutes/60", params=dict(market="KRW-BTC", to=to.strftime("%Y-%m-%dT%H:%M:%SZ"), count=200), headers=UA)
        if r is None or not r.json(): break
        j = r.json(); R += j; to = pd.Timestamp(j[-1]["candle_date_time_utc"], tz="UTC"); time.sleep(0.12)
    d = pd.DataFrame(R); return pd.Series(d.trade_price.astype(float).values, index=pd.to_datetime(d.candle_date_time_utc).dt.tz_localize("UTC")).sort_index().pipe(lambda s: s[~s.index.duplicated()])
def coinbase(urun, a, b):
    P = []; x = a
    while x < b:
        y = min(x + pd.Timedelta(hours=299), b); r = get(f"https://api.exchange.coinbase.com/products/{urun}/candles", params=dict(granularity=3600, start=x.isoformat(), end=y.isoformat()), headers=UA)
        if r is not None: P += r.json()
        x = y; time.sleep(0.15)
    d = pd.DataFrame(P, columns=["ts", "l", "h", "o", "c", "v"]); d.index = pd.to_datetime(d.ts, unit="s", utc=True); return d.c[~d.index.duplicated()].sort_index()
def yahoo(tk, a):                                                                             # araştırmayla aynı kaynak: yfinance (Yahoo çerez/crumb işini o yapıyor)
    import yfinance as yf
    for k in range(3):
        try:
            h = yf.Ticker(tk).history(start=a.strftime("%Y-%m-%d"), interval="1d", auto_adjust=True)
            if len(h): s = pd.Series(h.Close.values, index=pd.DatetimeIndex(h.index.tz_localize(None).normalize()).tz_localize("UTC")); return s[~s.index.duplicated(keep="last")]
        except Exception as e: log(tk, e)
        time.sleep(3 + 3 * k)
    raise RuntimeError(f"Yahoo {tk} alınamadı")
def zp(s, n=720): return (s - s.rolling(n, min_periods=n // 2).mean().shift(1)) / s.rolling(n, min_periods=n // 2).std().shift(1)
def ozellik(a, b):
    """a: ilk değerlendirilecek saat, b: son saat (dahil değil). Geçmiş pencere için 40 gün önceden veri çekilir."""
    a0 = a - pd.Timedelta(days=40)
    K = vadeli_1s(a0, b); log("vadeli 1 s", len(K), K.index.min(), K.index.max())
    Wb = balina(a - pd.Timedelta(days=3), b).reindex(K.index); log("balina", int(Wb.wq.notna().sum()))
    SP = spot_1s(a0, b).reindex(K.index); UP = upbit(a0, b).reindex(K.index); UT = coinbase("USDT-USD", a0, b).reindex(K.index)
    kr = yahoo("KRW=X", a0 - pd.Timedelta(days=10)); dx = yahoo("DX-Y.NYB", a0 - pd.Timedelta(days=20)); LS = ls_gunluk(a - pd.Timedelta(days=200), b)
    log("spot", int(SP.notna().sum()), "upbit", int(UP.notna().sum()), "usdt", int(UT.notna().sum()), "kur", len(kr), "dxy", len(dx), "L/S gün", len(LS))
    F = pd.DataFrame(index=K.index); qv = K.qv.where(K.qv > 0); tb = K.tb.where(K.qv > 0)
    wn = 2 * Wb.wtb - Wb.wq; F["imb4"] = wn.rolling(4).sum() / Wb.wq.rolling(4).sum(); F["imb24"] = wn.rolling(24).sum() / Wb.wq.rolling(24).sum(); F["wnet24z"] = np.nan   # wnet24z araştırmada etkisizdi (katsayı 0)
    kur = kr.shift(1).reindex(K.index.floor("D"), method="ffill").values; kim = UP / (SP * kur) - 1
    F["kz"] = zp(kim.rolling(24).mean()); F["kd24"] = kim - kim.shift(24)
    us = UT - 1; F["uz"] = zp(us.rolling(24).mean()); F["ud24"] = us - us.shift(24)
    gD = pd.date_range(K.index.min().floor("D"), K.index.max().floor("D"), freq="D")
    gL = pd.date_range(LS.index.min(), gD.max(), freq="D"); x = LS.reindex(gL).shift(1).dropna()                  # B.ls = önceki günün son saati · z: önceki 180 gözlem
    lsz = ((x - x.rolling(180, min_periods=90).mean().shift(1)) / x.rolling(180, min_periods=90).std().shift(1)).reindex(gD)
    F["lsz"] = lsz.reindex(K.index.floor("D")).values
    d5 = (dx / dx.shift(5) - 1); F["dxy5"] = d5.reindex(gD - pd.Timedelta(days=1), method="ffill").set_axis(gD).reindex(K.index.floor("D")).values
    cc = K.c; cvd = (2 * tb - qv).fillna(0).cumsum(); n = np.arange(len(K))
    mn72, mx72 = cc.rolling(72).min(), cc.rolling(72).max(); om, oM = cc.shift(24).rolling(48).min(), cc.shift(24).rolling(48).max()
    im, iM = cc.shift(24).rolling(48).apply(np.argmin, raw=True), cc.shift(24).rolling(48).apply(np.argmax, raw=True)
    def deger(j):
        j = (n - 71 + j.values).astype(float); v = np.full(len(j), np.nan); ok = ~np.isnan(j) & (j >= 0); v[ok] = cvd.values[j[ok].astype(int)]; return v
    F["posdiv"] = (((cc <= mn72) & (cc < om)).values & (cvd.values > deger(im))).astype(float); F["negdiv"] = (((cc >= mx72) & (cc > oM)).values & (cvd.values < deger(iM))).astype(float)
    lr = np.log(cc).diff(); F["vr"] = lr.rolling(24).std() / lr.rolling(720).std()
    w = PRM["w4"]; Z = (F[w["cols"]] - np.array(w["ort"])) / np.array(w["std"]); Z = Z.where(np.isfinite(Z), 0.0)
    F["skor"] = Z.values @ np.array(w["katsayi"]) + w["sabit"]
    F["P"] = (F.vr >= PRM["negdiv"]["vthr"]) | ((((F.index.hour + 1) % 24) // 4) == 3)
    F["sinyal_w4"] = np.where(F.skor >= w["q90"], 1, np.where(F.skor <= w["q10"], -1, 0)); F["sinyal_neg"] = np.where((F.negdiv == 1) & F.P, -1, 0)
    return K, F[(F.index >= a) & (F.index < b)]
def main():
    if len(sys.argv) >= 4 and sys.argv[1] == "--gecmis":
        a, b = pd.Timestamp(sys.argv[2], tz="UTC"), pd.Timestamp(sys.argv[3], tz="UTC"); _, F = ozellik(a, b)
        F.rename_axis("t").reset_index().to_csv("yon_golge_dogrula.csv", index=False); log("doğrulama yazıldı", len(F)); return
    son = pd.Timestamp.now(tz="UTC").floor("D")                                                  # arşivde dün tamam
    K, F = ozellik(BASLA, son); kapanis = K.index.max()
    R = []
    for kural, kol in (("🔻 NEG zayıf alıcı + pencere → SAT", "sinyal_neg"), ("🧮 W4 birleşik skor", "sinyal_w4")):
        serbest = None
        for t, yon in F.loc[F[kol] != 0, kol].items():
            g = t + pd.Timedelta(hours=1); c = g + pd.Timedelta(hours=23); islem = serbest is None or g >= serbest
            gi = K.o.get(g, np.nan); ci = K.c.get(c, np.nan) if c <= kapanis else np.nan
            ham = yon * (ci / gi - 1) if np.isfinite(ci) else np.nan; net = yon * (ci / (gi * (1 + KAYMA * yon)) - 1) - UCRET - yon * 3 * FON_8S if np.isfinite(ci) else np.nan
            R.append(dict(kural=kural, sinyal_saat=t, giris_saat=g, yon="AL" if yon > 0 else "SAT", giris=gi, cikis=ci, ham_yuzde=None if np.isnan(ham) else round(100 * ham, 3),
                          net_yuzde=None if np.isnan(net) else round(100 * net, 3), sayilan=islem, skor=round(float(F.skor[t]), 6)))
            if islem: serbest = c + pd.Timedelta(hours=1)
    D = pd.DataFrame(R, columns=["kural", "sinyal_saat", "giris_saat", "yon", "giris", "cikis", "ham_yuzde", "net_yuzde", "sayilan", "skor"]); D.to_csv("durum/yon_golge.csv", index=False)
    L = [f"# 🧭 BTC yön gölge izleme — {pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M}", "",
         f"_Mesaj göndermez. Başlangıç {BASLA:%d.%m.%Y} · veri {kapanis:%d.%m %H:%M} UTC'ye kadar (arşiv bir gün gecikmeli) · işlem: sinyalden sonraki saat açılışı → 24 s sonu, kayma %0,1 + ücret %0,1 + fonlama ≈ %0,03 · aynı kuralda aynı anda tek işlem._", "",
         "| kural | sinyal saati | sayılan işlem | biten | yön isabeti | isabet (net > 0) | işlem başı net % | araştırma 2025–26 |", "|---|---|---|---|---|---|---|---|"]
    REF = {"🔻 NEG zayıf alıcı + pencere → SAT": "50 · yön %64 · isabet %64 · +0,45", "🧮 W4 birleşik skor": "287 · yön %57 · isabet %51 · +0,04"}
    for kural in REF:
        x = D[(D.kural == kural)]; s = x[x.sayilan]; b_ = s.dropna(subset=["net_yuzde"])
        L.append(f"| {kural} | {len(x)} | {len(s)} | {len(b_)} | " + (f"%{100 * (b_.ham_yuzde > 0).mean():.0f} | %{100 * (b_.net_yuzde > 0).mean():.0f} | {b_.net_yuzde.mean():+.2f}" if len(b_) else "— | — | —") + f" | {REF[kural]} |")
    son5 = D[D.sayilan].tail(8)
    if len(son5):
        L += ["", "**Son işlemler**", "", "| kural | giriş (UTC) | yön | giriş | çıkış | net % |", "|---|---|---|---|---|---|"]
        L += [f"| {r.kural.split()[0]} {r.kural.split()[1]} | {pd.Timestamp(r.giris_saat):%d.%m %H:%M} | {r.yon} | {r.giris:,.0f} | {'—' if pd.isna(r.cikis) else f'{r.cikis:,.0f}'} | {'açık' if pd.isna(r.net_yuzde) else f'{r.net_yuzde:+.2f}'} |" for r in son5.itertuples()]
    open("durum/yon_golge.md", "w").write("\n".join(L) + "\n")
    json.dump(dict(guncelleme=pd.Timestamp.now(tz="UTC").isoformat(), veri_son=str(kapanis), skor_son=float(F.skor.iloc[-1]) if len(F) else None,
                   negdiv_son=int(F.negdiv.iloc[-1]) if len(F) else None, kayit=len(D)), open("durum/yon_golge_durum.json", "w"), ensure_ascii=False, indent=1)
    log("yazıldı", len(D), "kayıt")
if __name__ == "__main__": main()
