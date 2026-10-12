# gate_derinlik.py — Gate.io VADELİ emir defteri arşivinden (download.gatedata.org, saatlik dosya, başında tam defter görüntüsü) her saat başı
# fiyatın ±%1'indeki alış / satış derinliği. Yalnız veri: gate_{COIN}.pkl (sütunlar bid1, ask1 — sözleşme × fiyat; z hesabında birim önemsiz).
# Kullanım: python gate_derinlik.py BTC
import sys, io, zlib, time, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
nm = sys.argv[1]; T0 = time.time(); S = requests.Session()
SAAT = pd.date_range("2022-12-01", pd.Timestamp.now(tz="UTC").floor("D") - pd.Timedelta(days=2), freq="1h", tz="UTC")
def bir(t):
    url = f"https://download.gatedata.org/futures_usdt/orderbooks/{t:%Y%m}/{nm}_USDT-{t:%Y%m%d%H}.csv.gz"
    for boy in (131072, 1048576, 8388608):
        for k in range(4):
            try:
                r = S.get(url, headers={"Range": f"bytes=0-{boy - 1}"}, timeout=40)
                if r.status_code == 404: return t, None
                if r.status_code not in (200, 206): time.sleep(1 + 2 * k); continue
                txt = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(r.content).decode("utf-8", "replace"); break
            except Exception: time.sleep(1 + 2 * k)
        else: return t, None
        sat = txt.split("\n"); tam = len(r.content) < boy or any(",set," not in x for x in sat[1:-1] if x)
        if not tam: continue                                                      # görüntü bu parçaya sığmadı → daha büyük parça
        P, Q = [], []
        for x in sat[:-1]:
            if ",set," not in x: break
            a = x.split(","); P.append(float(a[2])); Q.append(float(a[3]))
        if not P: return t, None
        P, Q = np.array(P), np.array(Q); b, s = Q > 0, Q < 0
        if not b.any() or not s.any(): return t, None
        mid = (P[b].max() + P[s].min()) / 2
        if not np.isfinite(mid) or P[b].max() >= P[s].min(): return t, None
        return t, (float((P * Q)[b & (P >= mid * 0.99)].sum()), float((P * -Q)[s & (P <= mid * 1.01)].sum()), mid)
    return t, None
with ThreadPoolExecutor(16) as ex: R = list(ex.map(bir, SAAT))
D = pd.DataFrame([(t, *v) for t, v in R if v is not None], columns=["t", "bid1", "ask1", "mid"]).set_index("t").sort_index()
D.index = pd.DatetimeIndex(D.index).as_unit("ns"); D.to_pickle(f"gate_{nm}.pkl")
print(f"{nm}: {len(D):,}/{len(SAAT):,} saat · ilk {D.index.min() if len(D) else '-'} · {time.time()-T0:.0f} sn", flush=True)
