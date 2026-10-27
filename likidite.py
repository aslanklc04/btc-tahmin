# likidite.py — 💧 LİKİDİTE DİPTE (ld_kontrol.py / ld_genis.py: K0–K4 geçti; neon_uyum.py: canlı ölçüm arşivle uyumlu). Her saat çalışır.
# Ölçü: coin'in Binance USDT-M vadeli emir defterinde fiyatın ±%1'indeki alış + satış derinliği ($), saatlik ortalama → log → son 720 saate göre z.
# Kaynak: geçmiş = Binance arşivi bookDepth (ilk kurulumda, son ~32 gün) · güncel = Neon (Frankfurt, dakikada bir ölçüm) /saat. Saat etiketi = saatin BİTİŞİ (arşivle aynı).
# Çıktı: durum/likidite_z.json {"t": son saat (UTC), "z": {coin: z}} — ortak.ld_mu() okur. Yalnız durum/likidite_coinler.txt'teki (uyumu doğrulanmış) coin'ler; liste boşsa 💧 hiç çıkmaz.
import io, os, json, time, zipfile, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
U = "https://br-still-union-baibtf1k-derinlik.compute.c-8.eu-central-1.aws.neon.tech"
F, OUT = "durum/derinlik_saat.pkl", "durum/likidite_z.json"
COINS = os.environ["LD_COINS"].split(",") if os.environ.get("LD_COINS") else [l.strip() for l in open("durum/likidite_coinler.txt") if l.strip() and not l.startswith("#")]   # LD_COINS: yalnız kuru test
SEMB = pd.read_csv("durum/likidite_semboller.csv").set_index("coin").sym.to_dict()
S = requests.Session(); now = pd.Timestamp.now(tz="UTC").floor("h"); T0 = time.time()
if not COINS:
    json.dump({"t": None, "z": {}}, open(OUT, "w")); print("💧 coin listesi boş → 💧 kapalı"); raise SystemExit(0)
D = pd.read_pickle(F) if os.path.exists(F) else pd.DataFrame()
D = D.reindex(columns=sorted(set(D.columns) | set(COINS)))
def arsiv_gun(arg):
    nm, g = arg; sym = SEMB.get(nm)
    for k in range(3):
        try:
            r = S.get(f"https://data.binance.vision/data/futures/um/daily/bookDepth/{sym}/{sym}-bookDepth-{g}.zip", timeout=40)
            if r.status_code == 404: return nm, None
            if r.status_code != 200: time.sleep(1 + k); continue
            z_ = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z_.open(z_.namelist()[0])); d.columns = [c.strip().lower() for c in d.columns]
            if "percentage" not in d.columns: d = pd.read_csv(z_.open(z_.namelist()[0]), header=None, names=["timestamp", "percentage", "depth", "notional"])
            d = d[pd.to_numeric(d.percentage, errors="coerce").isin([1, -1])].copy(); d["t"] = pd.to_datetime(d.timestamp, utc=True).dt.ceil("h")
            d["notional"] = d.notional.astype(float); return nm, d.groupby(["t", "percentage"]).notional.mean().unstack().sum(axis=1)
        except Exception: time.sleep(1 + k)
    return nm, None
# 1) ilk kurulum / eksik coin: arşivden son 32 gün
eksik = [nm for nm in COINS if nm not in D.columns or D[nm].dropna().shape[0] < 400]
if eksik:
    gunler = [x.strftime("%Y-%m-%d") for x in pd.date_range(now - pd.Timedelta(days=33), now, freq="D")]
    with ThreadPoolExecutor(16) as ex: R = list(ex.map(arsiv_gun, [(nm, g) for nm in eksik for g in gunler]))
    for nm in eksik:
        parca = [s for n_, s in R if n_ == nm and s is not None]
        if parca:
            s = pd.concat(parca).groupby(level=0).mean(); s.index = pd.DatetimeIndex(s.index).as_unit("ns")
            D = D.reindex(D.index.union(s.index)); D.loc[s.index, nm] = D.loc[s.index, nm].fillna(s)
    print(f"arşivden dolduruldu: {len(eksik)} coin · {time.time()-T0:.0f} sn")
# 2) Neon: son 72 saatte eksik saatler (etiket H+1 = saatin bitişi)
def neon(H):
    for k in range(3):
        try: return H, S.get(f"{U}/saat", params={"h": H.strftime("%Y%m%d%H")}, timeout=90).json()
        except Exception: time.sleep(2 + 2 * k)
    return H, None
saatler = [now - pd.Timedelta(hours=k) for k in range(1, 72)]
gerek = [H for H in saatler if (H + pd.Timedelta(hours=1)) not in D.index or D.loc[H + pd.Timedelta(hours=1), COINS].isna().mean() > 0.2]
with ThreadPoolExecutor(6) as ex: NR = list(ex.map(neon, gerek))
for H, d in NR:
    if not d: continue
    lab = H + pd.Timedelta(hours=1)
    v = {nm: x["bid1"] + x["ask1"] for nm, x in d.get("coins", {}).items() if x.get("n", 0) >= 6 and nm in D.columns}   # 27.10: Neon 3 dk/örnek → ana 20, ek coin 10 ölçüm/saat (önce 60/30)
    if v:
        if lab not in D.index: D = D.reindex(D.index.union(pd.DatetimeIndex([lab])))
        for nm, x in v.items(): D.loc[lab, nm] = x
D = D.sort_index(); D = D[D.index >= now - pd.Timedelta(days=40)]
D.index = pd.DatetimeIndex(D.index).as_unit("ns"); D.to_pickle(F)
# 3) z (ld_kontrol.py ile aynı: z720, en az 168 saat)
L = np.log(D[COINS].where(D[COINS] > 0)); Z = (L - L.rolling(720, min_periods=168).mean()) / (L.rolling(720, min_periods=168).std() + 1e-12)
son = Z.index.max(); zz = Z.loc[son]
json.dump({"t": son.isoformat(), "z": {nm: (None if not np.isfinite(v) else round(float(v), 3)) for nm, v in zz.items()}}, open(OUT, "w"))
print(f"💧 son saat {son} · z ≤ −2: {', '.join(k for k, v in zz.items() if np.isfinite(v) and v <= -2) or '—'} · Neon {len(gerek)} saat · {time.time()-T0:.0f} sn")
