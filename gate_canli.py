# gate_canli.py — 💧 için CANLI ölçümün test ölçümüyle aynı olduğunun kontrolü (yalnız ölçüm).
#   kaydet:      Gate API'den (GitHub'dan açık) şu anki emir defteri → fiyatın ±%1'indeki alış/satış derinliği (sözleşme × fiyat) → gate_canli_kayit.csv
#   karsilastir: kaydedilen her ölçümü Gate arşivindeki aynı saatin başındaki tam defter görüntüsüyle karşılaştırır + arşivin yayın gecikmesi
# Kullanım: python gate_canli.py kaydet | karsilastir
import sys, os, zlib, time, requests, numpy as np, pandas as pd
COINS = ["BTC", "ETH", "ADA", "APT", "ARB", "BNB", "DOGE", "DOT", "FLOKI", "LINK", "NEAR", "OP", "PEPE", "SHIB", "SUI"]
S = requests.Session(); S.headers["User-Agent"] = "btc-tahmin-arastirma"; L = []
def yaz(s=""): print(s, flush=True); L.append(s)
def derinlik_api(nm):
    ci = S.get(f"https://api.gateio.ws/api/v4/futures/usdt/contracts/{nm}_USDT", timeout=20).json(); r = float(ci["order_price_round"]); son = None
    for k in (0, 1, 10, 100, 1000, 10000):
        iv = "0" if k == 0 else f"{r * k:.12f}".rstrip("0").rstrip(".")
        d = S.get("https://api.gateio.ws/api/v4/futures/usdt/order_book", params={"contract": f"{nm}_USDT", "limit": 300, "interval": iv}, timeout=20)
        if d.status_code != 200: continue
        d = d.json(); b = np.array([(float(x["p"]), float(x["s"])) for x in d["bids"]]); a = np.array([(float(x["p"]), float(x["s"])) for x in d["asks"]])
        if not len(b) or not len(a): continue
        mid = (b[:, 0].max() + a[:, 0].min()) / 2; kb, ka = 1 - b[:, 0].min() / mid, a[:, 0].max() / mid - 1
        son = (iv, float((b[:, 0] * b[:, 1])[b[:, 0] >= mid * 0.99].sum()), float((a[:, 0] * a[:, 1])[a[:, 0] <= mid * 1.01].sum()), mid, 100 * kb, 100 * ka)
        if kb >= 0.012 and ka >= 0.012: return son
    return son
def arsiv(nm, t):
    url = f"https://download.gatedata.org/futures_usdt/orderbooks/{t:%Y%m}/{nm}_USDT-{t:%Y%m%d%H}.csv.gz"
    for boy in (131072, 1048576, 8388608):
        r = S.get(url, headers={"Range": f"bytes=0-{boy - 1}"}, timeout=40)
        if r.status_code not in (200, 206): return None
        sat = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(r.content).decode("utf-8", "replace").split("\n")
        if len(r.content) < boy or any(",set," not in x for x in sat[1:-1] if x):
            P, Q = [], []
            for x in sat[:-1]:
                if ",set," not in x: break
                a = x.split(","); P.append(float(a[2])); Q.append(float(a[3]))
            P, Q = np.array(P), np.array(Q); b, s = Q > 0, Q < 0; mid = (P[b].max() + P[s].min()) / 2
            return float((P * Q)[b & (P >= mid * 0.99)].sum()), float((P * -Q)[s & (P <= mid * 1.01)].sum()), mid
    return None
if sys.argv[1] == "kaydet":
    t0 = pd.Timestamp.now(tz="UTC"); rows = []
    for nm in COINS:
        try:
            o = derinlik_api(nm)
            if o: rows.append((t0.isoformat(), nm, *o))
        except Exception as e: print(nm, "hata", e)
    X = pd.DataFrame(rows, columns=["zaman", "coin", "aralik", "bid1", "ask1", "mid", "kapsam_alis%", "kapsam_satis%"])
    eski = pd.read_csv("gate_canli_kayit.csv") if os.path.exists("gate_canli_kayit.csv") else None
    (pd.concat([eski, X]) if eski is not None else X).to_csv("gate_canli_kayit.csv", index=False); print(X.round(3).to_string(index=False))
else:
    X = pd.read_csv("gate_canli_kayit.csv"); X["zaman"] = pd.to_datetime(X.zaman, utc=True)
    yaz(f"# 💧 Gate canlı ölçüm ↔ arşiv karşılaştırması — {pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M}\n```")
    out = []
    for r in X.itertuples():
        a = arsiv(r.coin, r.zaman.floor("h"))
        if a: out.append((r.zaman.strftime("%d.%m %H:%M"), r.coin, r.aralik, r.bid1 + r.ask1, a[0] + a[1], np.log((r.bid1 + r.ask1) / (a[0] + a[1]))))
    O = pd.DataFrame(out, columns=["canlı ölçüm (UTC)", "coin", "aralık", "canlı ±%1", "arşiv ±%1 (saat başı)", "log fark"])
    yaz(O.round(3).to_string(index=False) if len(O) else "(arşivde henüz yok)"); yaz("```")
    if len(O): yaz(f"log fark: ortalama {O['log fark'].mean():+.3f} · mutlak medyan {O['log fark'].abs().median():.3f} (karşılaştırma: LD eşiği ≈ 30 günlük ortalamanın 2 standart sapma altı)")
    son = None; t = pd.Timestamp.now(tz="UTC").floor("h")
    for k in range(0, 72):
        if arsiv("BTC", t - pd.Timedelta(hours=k)) is not None: son = t - pd.Timedelta(hours=k); break
    yaz(f"Arşivde en son saat (BTC): {son} → şu andan {((pd.Timestamp.now(tz='UTC') - son).total_seconds() / 3600) if son is not None else float('nan'):.1f} saat geride")
    open("gate_canli_sonuc.md", "w").write("\n".join(L) + "\n")
