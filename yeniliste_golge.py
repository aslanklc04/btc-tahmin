# yeniliste_golge.py — 🆕 yeni listeleme short GÖLGESİ (05.11.2026, kullanıcı onayı; arastirma3 PROTOKOL_yeniliste.md Ek 1–2)
# Geçmiş testi TAM GEÇMEDİ (Ek 2 temiz veri: 10 portföy testinin 9u geçti, P3 2024 pozitif ay %42) — GÖZLEM AMAÇLI. Gerçek işlem yok, Telegram mesajı yok, yalnız kayıt.
# Kural: her yeni Binance USDT-M COIN perpetual listelemesi (hisse/emtia/döviz TRADIFI hariç) (L) → L+1 00:00 UTC açılışında kâğıt üstü short, 1×, sermayenin %2'si, L+30 kapanışında çıkış.
# Maliyet: ücret %0,05 + kayma %0,10 (iki taraf) + gerçek fonlama (aylık arşiv dosyası çıkınca kesinleşir; o zamana kadar "geçici").
import io, os, re, zipfile, xml.etree.ElementTree as ET, requests, numpy as np, pandas as pd
S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"; D = "https://data.binance.vision/"
BASLA = pd.Timestamp(os.environ.get("YL_BASLA", "2026-11-05"), tz="UTC"); H = 30; UC = 2 * (0.0005 + 0.001); PAY = 0.02
KF, BF, MF = "durum/yeniliste_golge.csv", "durum/yeniliste_bilinen.txt", "durum/yeniliste_golge.md"
HARIC = re.compile(r"^(USDC|FDUSD|TUSD|BUSD|USDP|DAI|BTCDOM|DEFI|FOOTBALL|BLUEBIRD|XAU|XAG|XPT|XPD|PAXG|AAPL|TSLA|NVDA|MSTR|COIN|AMZN|GOOGL|META|MSFT|HOOD|CRCL|SPY|QQQ|AMD|PLTR|INTC|NFLX|BABA)USDT$")
taban = lambda s: re.sub(r"^(1000000|100000|10000|1000|1M)", "", s[:-4])
def liste(prefix, dizin=True):
    out, mark = [], ""
    while True:
        p = {"prefix": prefix, "marker": mark}
        if dizin: p["delimiter"] = "/"
        x = None
        for i in range(5):
            try: x = ET.fromstring(requests.get(S3, params=p, timeout=60).content); break
            except Exception: pass
        if x is None: raise RuntimeError("S3 listesi alınamadı")
        ns = {"s": x.tag.split("}")[0][1:]}
        ks = [e.text for e in x.findall("s:CommonPrefixes/s:Prefix", ns)] if dizin else [e.text for e in x.findall("s:Contents/s:Key", ns)]
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
def gunler(s):
    ks = [k for k in liste(f"data/futures/um/daily/klines/{s}/1d/", False) if k.endswith(".zip")]
    return sorted(pd.Timestamp(re.search(r"(\d{4}-\d{2}-\d{2})\.zip$", k).group(1), tz="UTC") for k in ks)
def mum(s, g):
    d = zipcsv(f"{D}data/futures/um/daily/klines/{s}/1d/{s}-1d-{g:%Y-%m-%d}.zip"); return None if d is None or not len(d) else d.iloc[0]
NEON = "https://br-still-union-baibtf1k-derinlik.compute.c-8.eu-central-1.aws.neon.tech"
def bilgi():                                                                                        # Neon /bilgi: Binance vadeli sembol türü (05.11: 942'nin 235'i hisse/emtia/döviz)
    for i in range(3):
        try: return {x["s"]: x for x in requests.get(NEON + "/bilgi", timeout=120).json()}
        except Exception: pass
    return None
SEMBOL = [p.rstrip("/").split("/")[-1] for p in liste("data/futures/um/daily/klines/")]
SEMBOL = [s for s in SEMBOL if s.endswith("USDT") and "_" not in s]
bilinen = set(open(BF).read().split()) if os.path.exists(BF) else None
K = pd.read_csv(KF, parse_dates=["L", "giris_t", "cikis_t"]) if os.path.exists(KF) else pd.DataFrame(columns=["s", "L", "giris_t", "giris", "cikis_t", "cikis", "fiyat_net", "fon", "net", "durum"])
bugun = pd.Timestamp.now(tz="UTC").floor("D")
if bilinen is None:                                                                                  # ilk çalışma: bugüne kadar listelenmiş her şey bilinen sayılır
    bilinen = set(SEMBOL); print(f"🆕 gölge başlatıldı: {len(bilinen)} mevcut sembol bilinen sayıldı")
else:
    tabanlar = {taban(s) for s in bilinen}; yeni = sorted(set(SEMBOL) - bilinen); VB = bilgi() if yeni else {}
    for s in yeni:
        if VB is None: print("⚠️ Neon /bilgi alınamadı — yeni semboller sonraki çalışmada"); break
        if s not in VB: continue                                                                    # borsa bilgisinde henüz yok → sonra tekrar bak
        bilinen.add(s)
        if VB[s].get("ut") != "COIN" or VB[s].get("ct") != "PERPETUAL": print(f"· {s} coin değil ({VB[s].get('ut')}), atlandı"); continue
        if HARIC.match(s) or taban(s) in tabanlar: continue
        g = gunler(s)
        if not g or g[0] < BASLA: continue
        tabanlar.add(taban(s)); K.loc[len(K)] = [s, g[0], pd.NaT, np.nan, pd.NaT, np.nan, np.nan, np.nan, np.nan, "bekliyor"]; print(f"🆕 yeni listeleme: {s} · {g[0]:%d.%m.%Y}")
for i, r in K.iterrows():
    L = pd.Timestamp(r.L)
    if L.tzinfo is None: L = L.tz_localize("UTC")
    if r.durum == "bekliyor":
        m = mum(r.s, L + pd.Timedelta(days=1))
        if m is not None: K.loc[i, ["giris_t", "giris", "durum"]] = [L + pd.Timedelta(days=1), m[1], "açık"]
        elif bugun > L + pd.Timedelta(days=4): K.loc[i, "durum"] = "giriş yok"
    if K.loc[i, "durum"] == "açık":
        hedef = L + pd.Timedelta(days=H); m = mum(r.s, hedef); ct = hedef
        if m is None and bugun > hedef + pd.Timedelta(days=3):                                      # kapatıldıysa son kapanış
            g = [x for x in gunler(r.s) if L < x <= hedef]
            if g: ct = g[-1]; m = mum(r.s, ct)
        if m is not None:
            o = float(K.loc[i, "giris"]); c = m[4]; K.loc[i, ["cikis_t", "cikis", "fiyat_net", "durum"]] = [ct, c, max(-(c / o - 1), -1.0) - UC, "kapalı"]
for i, r in K[(K.durum == "kapalı") & K.fon.isna()].iterrows():                                      # fonlama: aylık arşiv çıkınca kesinleşir
    gt, ct = pd.Timestamp(r.giris_t), pd.Timestamp(r.cikis_t)
    gt, ct = (gt.tz_localize("UTC") if gt.tzinfo is None else gt), (ct.tz_localize("UTC") if ct.tzinfo is None else ct)
    aylar = pd.period_range(gt.tz_convert(None), ct.tz_convert(None), freq="M"); parca = []
    for a in aylar:
        d = zipcsv(f"{D}data/futures/um/monthly/fundingRate/{r.s}/{r.s}-fundingRate-{a.year}-{a.month:02d}.zip")
        if d is None: parca = None; break
        parca.append(d)
    if parca is None: continue
    f = pd.concat(parca); ft = pd.to_datetime(f[0], unit="ms", utc=True); fon = f[2][(ft >= gt) & (ft < ct + pd.Timedelta(days=1))].sum()
    K.loc[i, ["fon", "net"]] = [fon, max(r.fiyat_net + fon, -1.0)]
K = K.sort_values("L").reset_index(drop=True); K.to_csv(KF, index=False); open(BF, "w").write("\n".join(sorted(bilinen)) + "\n")
# ---- özet
Kp = K[K.durum == "kapalı"].copy(); Kp["n_"] = Kp.net.fillna(Kp.fiyat_net); Kp["ay"] = pd.to_datetime(Kp.cikis_t, utc=True).dt.tz_convert(None).dt.to_period("M")
L_ = ["# 🆕 Yeni listeleme short — GÖLGE (gözlem amaçlı; gerçek işlem ve mesaj yok)",
      f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · başlangıç {BASLA:%d.%m.%Y} · kural: listelemeden 1 gün sonra short, 30 gün, 1×, her işleme %2 · ücret+kayma %0,30 + gerçek fonlama_",
      "_⚠️ Geçmiş testi tam geçmedi (yalnız coin verisiyle 10 portföy testinin 9u geçti; coin yarısı 0, 2024 pozitif ay %42 < %55); bu yüzden yalnız gözlem. 2026 2. yarıda ayda yalnız 1–3 yeni coin listeleniyor. Fonlaması kesinleşmemiş işlemler 'geçici'._\n",
      f"**Durum:** bekleyen {int((K.durum == 'bekliyor').sum())} · açık {int((K.durum == 'açık').sum())} · kapanan {len(Kp)} (fonlaması kesin {int(Kp.net.notna().sum())}) · girişsiz {int((K.durum == 'giriş yok').sum())}"]
if len(Kp):
    m = Kp.groupby("ay").n_.sum() * PAY; c = m.cumsum(); dd = (c - c.cummax()).min()
    L_ += [f"**Kapananlar:** işlem başı ort. {100 * Kp.n_.mean():+.1f}% · medyan {100 * Kp.n_.median():+.1f}% · kârlı %{100 * (Kp.n_ > 0).mean():.0f} · −%50'den kötü %{100 * (Kp.n_ <= -0.5).mean():.0f}",
           "| ay | işlem | aylık (%2'lik payla) |", "|---|---|---|"] + [f"| {a} | {int((Kp.ay == a).sum())} | {100 * v:+.1f}% |" for a, v in m.items()]
    L_ += [f"\nToplam {100 * m.sum():+.1f}% · pozitif ay %{100 * (m > 0).mean():.0f} · en kötü ay {100 * m.min():+.1f}% · en büyük düşüş {100 * dd:.1f}%"]
    ay_n = len(m); karar = ay_n >= 3 and len(Kp) >= 40
    if karar:
        ok = m.sum() > 0 and m.min() >= -0.10 and dd >= -0.20 and (m > 0).mean() >= 0.55 and Kp.n_.mean() > 0
        L_ += [f"\n**Önceden yazılı karar şartı (≥ 3 ay, ≥ 40 işlem; toplam > 0, en kötü ay ≥ −%10, düşüş ≥ −%20, pozitif ay ≥ %55, işlem ort. > 0): {'✅ SAĞLANDI — gerçek parayla küçük deneme kullanıcıya sorulabilir' if ok else '❌ sağlanmadı'}**"]
    else: L_ += [f"\n_Karar için ≥ 3 ay ve ≥ 40 kapanan işlem gerekiyor (şu an {ay_n} ay · {len(Kp)} işlem)._"]
open(MF, "w").write("\n".join(L_) + "\n"); print("\n".join(L_[3:5]))
