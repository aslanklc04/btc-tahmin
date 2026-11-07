# yukselis_golge.py — 🔄 sert yükselişten sonra short GÖLGESİ (07.11.2026; arastirma3 PROTOKOL_tersine.md Ek 2)
# Sağlamlık testlerinin 3'ünde kaldı — GÖZLEM AMAÇLI. Gerçek işlem yok, Telegram mesajı yok, yalnız kayıt.
# Kural: günlük değişim (C[g]/C[g−1] − 1) ≥ +%50 olan COIN perpetual → g+1 açılışında kâğıt üstü short, g+1 kapanışında çıkış; 1×, %2; günde en çok 10.
import io, json, os, re, zipfile, xml.etree.ElementTree as ET, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"; D = "https://data.binance.vision/"
NEON = "https://br-still-union-baibtf1k-derinlik.compute.c-8.eu-central-1.aws.neon.tech"
ESIK, KAY, UCR, PAY, GUNDE = 0.50, 0.001, 0.001, 0.02, 10
KF, SF, CF, MF = "durum/yukselis_golge.csv", "durum/yukselis_son.json", "durum/yukselis_coin.txt", "durum/yukselis_golge.md"
def liste(prefix):
    out, mark = [], ""
    while True:
        x = None
        for i in range(5):
            try: x = ET.fromstring(requests.get(S3, params={"prefix": prefix, "marker": mark, "delimiter": "/"}, timeout=60).content); break
            except Exception: pass
        if x is None: raise RuntimeError("S3 listesi alınamadı")
        ns = {"s": x.tag.split("}")[0][1:]}; ks = [e.text for e in x.findall("s:CommonPrefixes/s:Prefix", ns)]
        out += ks; tr = x.find("s:IsTruncated", ns)
        if tr is None or tr.text != "true" or not ks: return out
        mark = ks[-1]
def zipcsv(url):
    for i in range(4):
        try:
            r = requests.get(url, timeout=60)
            if r.status_code == 404: return None
            z = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z.open(z.namelist()[0]), header=None)
            return d[pd.to_numeric(d[0], errors="coerce").notna()].astype(float)
        except Exception: pass
    return None
mum = lambda s, g: (lambda d: None if d is None or not len(d) else d.iloc[0])(zipcsv(f"{D}data/futures/um/daily/klines/{s}/1d/{s}-1d-{g:%Y-%m-%d}.zip"))
# ---- coin evreni (Neon /bilgi; alınamazsa önceki liste)
COIN = None
try:
    VB = requests.get(NEON + "/bilgi", timeout=120).json()
    COIN = sorted(x["s"] for x in VB if x.get("ut") == "COIN" and x.get("ct") == "PERPETUAL" and x.get("st") == "TRADING" and x["s"].endswith("USDT")); open(CF, "w").write("\n".join(COIN) + "\n")
except Exception: COIN = open(CF).read().split() if os.path.exists(CF) else None
if not COIN: raise SystemExit("coin listesi yok")
SON = json.load(open(SF)) if os.path.exists(SF) else {}                                           # {"gun": "YYYY-MM-DD", "c": {sembol: kapanış}}
K = pd.read_csv(KF) if os.path.exists(KF) else pd.DataFrame(columns=["s", "g", "r", "giris_g", "giris", "cikis", "fiyat_net", "fon", "net", "durum"])
bugun = pd.Timestamp.now(tz="UTC").floor("D")
son_arsiv = next((g for g in (bugun - pd.Timedelta(days=k) for k in (1, 2, 3)) if mum("BTCUSDT", g) is not None), None)
if son_arsiv is None: raise SystemExit("arşiv günü bulunamadı")
basla = pd.Timestamp(SON["gun"], tz="UTC") + pd.Timedelta(days=1) if SON else son_arsiv
for g in pd.date_range(basla, son_arsiv, freq="D"):
    with ThreadPoolExecutor(16) as ex: M = dict(zip(COIN, ex.map(lambda s: mum(s, g), COIN)))
    # 1) bugün girişi olan işlemler: g açılışında short, g kapanışında çıkış
    for i in K.index[(K.durum == "bekliyor") & (K.giris_g == f"{g:%Y-%m-%d}")]:
        m = M.get(K.at[i, "s"])
        if m is None: K.loc[i, "durum"] = "giriş yok"; continue
        pe, ce = m[1] * (1 - KAY), m[4] * (1 + KAY)
        K.loc[i, ["giris", "cikis", "fiyat_net", "durum"]] = [m[1], m[4], max(-(ce / pe - 1), -1.0) - UCR, "kapalı"]
    # 2) g günü olaylar (karar g kapanışında bilinir) → g+1 girişi
    oc = SON.get("c", {}); yeni = []
    for s, m in M.items():
        if m is None: continue
        if s in oc and oc[s] > 0 and m[4] / oc[s] - 1 >= ESIK: yeni.append((m[4] / oc[s] - 1, s))
    for r, s in sorted(yeni, reverse=True)[:GUNDE]:
        K.loc[len(K)] = [s, f"{g:%Y-%m-%d}", r, f"{g + pd.Timedelta(days=1):%Y-%m-%d}", np.nan, np.nan, np.nan, np.nan, np.nan, "bekliyor"]; print(f"🔄 {g:%d.%m} {s} {100 * r:+.0f}% → ertesi gün short (gölge)")
    SON = {"gun": f"{g:%Y-%m-%d}", "c": {**oc, **{s: float(m[4]) for s, m in M.items() if m is not None}}}
# 3) fonlama: aylık arşiv çıkınca kesinleşir
for i, r in K[(K.durum == "kapalı") & K.fon.isna()].iterrows():
    gg = pd.Timestamp(r.giris_g, tz="UTC"); d = zipcsv(f"{D}data/futures/um/monthly/fundingRate/{r.s}/{r.s}-fundingRate-{gg.year}-{gg.month:02d}.zip")
    if d is None: continue
    ft = pd.to_datetime(d[0], unit="ms", utc=True); fon = d[2][(ft >= gg) & (ft < gg + pd.Timedelta(days=1))].sum()
    K.loc[i, ["fon", "net"]] = [fon, max(r.fiyat_net + fon, -1.0)]
K.to_csv(KF, index=False); json.dump(SON, open(SF, "w"))
# ---- özet
Kp = K[K.durum == "kapalı"].copy(); Kp["n_"] = Kp.net.fillna(Kp.fiyat_net); Kp["ay"] = pd.to_datetime(Kp.giris_g).dt.to_period("M")
L_ = ["# 🔄 Sert yükselişten (+%50) sonra 1 gün short — GÖLGE (gözlem amaçlı; gerçek işlem ve mesaj yok)",
      f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · son işlenen gün {SON.get('gun', '—')} · coin {len(COIN)} · kural: günlük ≥ +%50 → ertesi gün açılışta short, kapanışta çıkış · 1× · %2 · günde ≤ 10 · ücret+kayma %0,40 + gerçek fonlama_",
      "_⚠️ Sağlamlık testlerinin 3'ünde kaldı (arastirma3 PROTOKOL_tersine Ek 1–2); yalnız gözlem. Fonlaması kesinleşmemiş işlemler 'geçici'._\n",
      f"**Durum:** bekleyen {int((K.durum == 'bekliyor').sum())} · kapanan {len(Kp)} (fonlaması kesin {int(Kp.net.notna().sum())}) · girişsiz {int((K.durum == 'giriş yok').sum())}"]
if len(Kp):
    m = Kp.groupby("ay").n_.sum() * PAY
    L_ += [f"**Kapananlar:** işlem başı ort. {100 * Kp.n_.mean():+.1f}% · medyan {100 * Kp.n_.median():+.1f}% · kârlı %{100 * (Kp.n_ > 0).mean():.0f} · −%50'den kötü %{100 * (Kp.n_ <= -0.5).mean():.0f}",
           "| ay | işlem | aylık (%2'lik payla) |", "|---|---|---|"] + [f"| {a} | {int((Kp.ay == a).sum())} | {100 * v:+.1f}% |" for a, v in m.items()]
    L_ += [f"\nToplam {100 * m.sum():+.1f}% · pozitif ay %{100 * (m > 0).mean():.0f} · en kötü ay {100 * m.min():+.1f}%"]
    if len(m) >= 2 and len(Kp) >= 60:
        ok = m.sum() > 0 and m.min() >= -0.10 and (m > 0).mean() >= 0.55 and Kp.n_.mean() > 0
        L_ += [f"\n**Önceden yazılı canlı para şartı (≥ 2 ay, ≥ 60 işlem; toplam > 0, en kötü ay ≥ −%10, pozitif ay ≥ %55, işlem ort. > 0): {'✅ SAĞLANDI — gerçek parayla küçük deneme kullanıcıya sorulabilir' if ok else '❌ sağlanmadı'}**"]
    else: L_ += [f"\n_Karar için ≥ 2 ay ve ≥ 60 kapanan işlem gerekiyor (şu an {len(m)} ay · {len(Kp)} işlem)._"]
open(MF, "w").write("\n".join(L_) + "\n"); print("\n".join(L_[3:5]))
