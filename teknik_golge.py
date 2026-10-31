# teknik_golge.py — 📐 TEKNİK GÖSTERGE GÖLGE İZLEME (31.10.2026, kullanıcı onayı "tm yap"). MESAJ GÖNDERMEZ, yalnız kayıt.
# Araştırma: arastirma3/PROTOKOL_teknik3.md — "M8 alt Bollinger'den dönüş · T4 BTC > EMA200 · V1 hacim z ≥ 2 · 🎯 +0,75σ·√4, en fazla 24 s":
#   keşif coin'leri %78 · %87 · %79 · yeni coin'ler %78 · %84 · %83 (2022–23 · 2024 · 2025–26), işlem başı +%0,14…+%0,55. Seçim eşiğini (+%0,30) 2022–23'te tutturamadığı için gölgede doğrulanıyor.
# Veri: Binance vadeli arşivi (bir gün gecikmeli) · 141 coin (durum/teknik_golge_coinler.txt) · günde bir (06 UTC).
# Kullanım: python teknik_golge.py  → durum/teknik_golge.csv · .md · _durum.json   |   python teknik_golge.py --gecmis A B → teknik_golge_dogrula.csv
import io, sys, json, time, zipfile, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
S = requests.Session(); V = "https://data.binance.vision/data"; T0 = time.time()
BASLA = pd.Timestamp("2026-10-28", tz="UTC"); FP, FL, SLIP, FON8 = 0.0005, 0.0002, 0.001, 0.0001
COINS = [l.strip() for l in open("durum/teknik_golge_coinler.txt") if l.strip()]
def log(*a): print(f"[{time.time() - T0:5.0f} sn]", *a, flush=True)
def get(u):
    for k in range(4):
        try:
            r = S.get(u, timeout=60)
            if r.status_code == 200: return r.content
            if r.status_code == 404: return None
        except Exception: pass
        time.sleep(2 + 2 * k)
    return None
def mum(nm, a, b):
    gun = pd.date_range(a.floor("D"), b.floor("D"), freq="D").strftime("%Y-%m-%d")
    for pazar, sym in (("futures/um", f"{nm}USDT"), ("futures/um", f"1000{nm}USDT"), ("spot", f"{nm}USDT")):
        P = []
        for g in gun:
            x = get(f"{V}/{pazar}/daily/klines/{sym}/1h/{sym}-1h-{g}.zip")
            if x:
                z = zipfile.ZipFile(io.BytesIO(x)); d = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=[0, 1, 2, 3, 4, 7]); P.append(d[pd.to_numeric(d[0], errors="coerce").notna()].astype(float))
            elif not P and g == gun[-1]: break
        if P:
            k = pd.concat(P, ignore_index=True); k.columns = ["ot", "o", "h", "l", "c", "qv"]; k.loc[k.ot > 1e14, "ot"] = k.ot / 1000
            k = k.drop_duplicates("ot").sort_values("ot"); k.index = pd.to_datetime(k.ot, unit="ms", utc=True); return nm, k.drop(columns="ot").astype("float32").astype(float)
    return nm, None
def hesap(a, b):
    with ThreadPoolExecutor(16) as ex: D = dict(ex.map(lambda nm: mum(nm, a - pd.Timedelta(days=40), b), COINS))
    _, Bt = mum("BTC", a - pd.Timedelta(days=90), b); btr = Bt.c > Bt.c.ewm(span=200, adjust=False).mean()
    log("mum", sum(v is not None for v in D.values()), "/", len(COINS))
    R = []
    for nm, d in D.items():
        if d is None or len(d) < 800: continue
        c, h, l, o, q = d.c, d.h, d.l, d.o, d.qv
        m20, s20 = c.rolling(20).mean(), c.rolling(20).std(); lb = m20 - 2 * s20
        m8 = (c > lb) & (c.shift() <= lb.shift())
        q24 = q.rolling(24).sum(); vz = (q24 - q24.rolling(720).mean().shift(24)) / q24.rolling(720).std().shift(24)
        sig = np.log(c).diff().rolling(720, min_periods=480).std()
        m = m8 & (vz >= 2) & btr.reindex(d.index).fillna(False).astype(bool) & (d.index >= a) & (d.index < b)
        for t in d.index[m.values]: R.append(dict(t=t, coin=nm, sigma=float(sig[t]), vz=float(vz[t])))
    return D, pd.DataFrame(R, columns=["t", "coin", "sigma", "vz"])
def main():
    if len(sys.argv) >= 4 and sys.argv[1] == "--gecmis":
        _, R = hesap(pd.Timestamp(sys.argv[2], tz="UTC"), pd.Timestamp(sys.argv[3], tz="UTC")); R.to_csv("teknik_golge_dogrula.csv", index=False); log("doğrulama", len(R)); return
    son = pd.Timestamp.now(tz="UTC").floor("D"); D, R = hesap(BASLA, son); out = []; serbest = {}
    for r in R.sort_values("t").itertuples():
        d = D[r.coin]; i = d.index.searchsorted(r.t); e = i + 1; islem = r.t >= serbest.get(r.coin, pd.Timestamp(0, tz="UTC"))
        sat = dict(sinyal_saat=r.t, coin=r.coin, vz=round(r.vz, 2), sayilan=bool(islem), giris=np.nan, cikis=np.nan, hedef=np.nan, sonuc="açık", net_yuzde=np.nan)
        if e < len(d) and np.isfinite(r.sigma):
            Pe = d.o.iloc[e] * (1 + SLIP); tp = Pe * (1 + 0.75 * r.sigma * 2.0); sat.update(giris=round(float(d.o.iloc[e]), 8), hedef=round(float(tp), 8))
            w = d.iloc[e:e + 24]; hit = np.where(w.h.values >= tp)[0]
            if len(hit): j = hit[0]; net = tp / Pe - 1 - FP - FL - FON8 * (j + 1) / 8; sat.update(cikis=round(float(tp), 8), sonuc="🎯", net_yuzde=round(100 * net, 3))
            elif len(w) == 24: j = 23; net = w.c.iloc[-1] / Pe - 1 - 2 * FP - FON8 * 3; sat.update(cikis=round(float(w.c.iloc[-1]), 8), sonuc="süre", net_yuzde=round(100 * net, 3))
            else: j = 23
            if islem: serbest[r.coin] = d.index[min(e + j, len(d) - 1)] + pd.Timedelta(hours=1) if e + j < len(d) else r.t + pd.Timedelta(hours=26)
        out.append(sat)
    X = pd.DataFrame(out, columns=["sinyal_saat", "coin", "vz", "sayilan", "giris", "hedef", "cikis", "sonuc", "net_yuzde"]); X.to_csv("durum/teknik_golge.csv", index=False)
    s = X[X.sayilan]; b_ = s.dropna(subset=["net_yuzde"]); gun = max((son - BASLA).days, 1)
    L = [f"# 📐 Teknik gösterge gölge izleme — {pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M}", "",
         "_Mesaj göndermez. Kural: alt Bollinger'den dönüş + BTC > EMA200 + hacim z ≥ 2 → sonraki saat açılışında AL, 🎯 +0,75σ·√4, en fazla 24 s (kayma %0,1, vadeli ücret, fonlama ≈ %0,01/8 s). Coin başına aynı anda tek işlem. Veri arşivden, bir gün gecikmeli._", "",
         f"- Başlangıç {BASLA:%d.%m.%Y} · sinyal {len(X)} (sayılan {len(s)}, biten {len(b_)}) · günde ≈ {len(s) / gun:.1f}",
         f"- **Canlı gölge:** " + (f"isabet %{100 * (b_.net_yuzde > 0).mean():.0f} · 🎯 oranı %{100 * (b_.sonuc == '🎯').mean():.0f} · işlem başı {b_.net_yuzde.mean():+.2f}%" if len(b_) else "henüz biten işlem yok"),
         "- **Araştırma (karşılaştırma):** isabet %78 · %87 · %79 / yeni coin'ler %78 · %84 · %83 · işlem başı +0,14…+0,55 · haftada ≈ 10–15 sinyal"]
    son8 = s.tail(10)
    if len(son8):
        L += ["", "| sinyal (UTC) | coin | hacim z | giriş | 🎯 | sonuç | net % |", "|---|---|---|---|---|---|---|"]
        L += [f"| {pd.Timestamp(r.sinyal_saat):%d.%m %H:%M} | {r.coin} | {r.vz:+.1f} | {r.giris:.6g} | {r.hedef:.6g} | {r.sonuc} | {'—' if pd.isna(r.net_yuzde) else f'{r.net_yuzde:+.2f}'} |" for r in son8.itertuples()]
    open("durum/teknik_golge.md", "w").write("\n".join(L) + "\n")
    json.dump(dict(guncelleme=pd.Timestamp.now(tz="UTC").isoformat(), sinyal=len(X), biten=len(b_), isabet=float((b_.net_yuzde > 0).mean()) if len(b_) else None), open("durum/teknik_golge_durum.json", "w"), indent=1)
    log("yazıldı", len(X))
if __name__ == "__main__": main()
