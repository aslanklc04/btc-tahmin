# duyuru_golge.py — 📢 Binance duyurusu sonrası short GÖLGESİ (12.11.2026, kullanıcı onayı; arastirma3 PROTOKOL_duyuru.md Ek 1)
# Geçmiş testi VERİ YETERSİZ çıktı (keşif olayı < 25) — GÖZLEM AMAÇLI. Gerçek işlem yok, Telegram mesajı yok, yalnız kayıt.
# İzlenen: D "Binance Will Delist <coinler> on <tarih>" (spot) · S "Binance Will List <ad> (<COIN>)" (perpetual'ı ≥ 7 gün önce listelenmiş).
# Kural: duyurunun UTC günü g → g+1 açılışında kâğıt üstü short, g+7 kapanışında çıkış; 1×, %2; kayma %0,10 + ücret %0,05 (iki taraf) + gerçek fonlama.
import io, os, re, zipfile, xml.etree.ElementTree as ET, requests, numpy as np, pandas as pd
S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"; D = "https://data.binance.vision/"
NEON = "https://br-still-union-baibtf1k-derinlik.compute.c-8.eu-central-1.aws.neon.tech"
BASLA = pd.Timestamp(os.environ.get("DG_BASLA", "2026-11-12"), tz="UTC"); SAYFA = int(os.environ.get("DG_SAYFA", "1")); H, KAY, UCR, PAY = 7, 0.001, 0.001, 0.02
KF, BF, MF = "durum/duyuru_golge.csv", "durum/duyuru_bilinen.txt", "durum/duyuru_golge.md"
taban = lambda s: re.sub(r"^(1000000|100000|10000|1000|1M)", "", s[:-4])
ayir = lambda x: [t.strip().upper() for t in re.split(r",|&| and ", x) if re.fullmatch(r"[A-Za-z0-9]{2,12}", t.strip())]
def liste(prefix):
    out, mark = [], ""
    while True:
        x = None
        for i in range(5):
            try: x = ET.fromstring(requests.get(S3, params={"prefix": prefix, "marker": mark}, timeout=60).content); break
            except Exception: pass
        if x is None: return out
        ns = {"s": x.tag.split("}")[0][1:]}; ks = [e.text for e in x.findall("s:Contents/s:Key", ns)]
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
    return sorted(pd.Timestamp(re.search(r"(\d{4}-\d{2}-\d{2})\.zip$", k).group(1), tz="UTC") for k in liste(f"data/futures/um/daily/klines/{s}/1d/") if k.endswith(".zip"))
mum = lambda s, g: (lambda d: None if d is None or not len(d) else d.iloc[0])(zipcsv(f"{D}data/futures/um/daily/klines/{s}/1d/{s}-1d-{g:%Y-%m-%d}.zip"))
def neon(yol, **prm):
    for i in range(3):
        try: return requests.get(NEON + yol, params=prm, timeout=120).json()
        except Exception: pass
    return None
ts = lambda x: (lambda t: t.tz_localize("UTC") if t.tzinfo is None else t)(pd.Timestamp(x))
K = pd.read_csv(KF) if os.path.exists(KF) else pd.DataFrame(columns=["tur", "g", "coin", "s", "baslik", "giris_g", "giris", "cikis_g", "cikis", "fiyat_net", "fon", "net", "durum"])
bilinen = set(open(BF).read().split()) if os.path.exists(BF) else set()
bugun = pd.Timestamp.now(tz="UTC").floor("D")
# ---- 1) yeni duyurular
ART, tam = [], True
for cat in (161, 48):
    for pg in range(1, SAYFA + 1):
        d = neon("/duyuru", c=cat, p=pg, n=20)
        try: ART += d["data"]["catalogs"][0]["articles"]
        except Exception: tam = False; print(f"⚠️ duyuru listesi alınamadı (katalog {cat}, sayfa {pg}) — sonraki çalışmada")
yeni = [a for a in ART if a.get("code") and a["code"] not in bilinen and a.get("title") and a.get("releaseDate")]
if yeni:
    VB = neon("/bilgi"); EV = []
    if VB is None: print("⚠️ Neon /bilgi alınamadı — yeni duyurular sonraki çalışmada")
    else:
        PERP = {}
        for x in VB:
            if x.get("ut") == "COIN" and x.get("ct") == "PERPETUAL" and x["s"].endswith("USDT"): PERP.setdefault(taban(x["s"]), x)
        for a in sorted(yeni, key=lambda a: a["releaseDate"]):
            bilinen.add(a["code"]); T = a["title"]; g = pd.Timestamp(a["releaseDate"], unit="ms", tz="UTC").floor("D")
            if g < BASLA: continue
            m = re.match(r"Binance Will Delist (.+?) on \d{4}-\d{2}-\d{2}", T)
            if m and not re.search(r"Futures|Margin|Pair|Options|Leveraged|Loan|Earn|Contract", T): EV += [("D", g, c, T) for c in ayir(m.group(1))]
            if T.startswith("Binance Will List "): EV += [("S", g, c.upper(), T) for c in re.findall(r"\(([A-Za-z0-9]{2,12})\)", T)]
        for tur, g, coin, T in EV:
            x = PERP.get(coin)
            if x is None: print(f"· {tur} {coin}: vadelisi yok, atlandı"); continue
            if tur == "S" and not (x.get("od") and pd.Timestamp(x["od"], unit="ms", tz="UTC") <= g - pd.Timedelta(days=7)): print(f"· S {coin}: vadelisi 7 günden yeni, atlandı"); continue
            e = K[(K.tur == tur) & (K.s == x["s"])]
            if len(e) and (g - ts(e.g.iloc[-1])).days < 30: continue
            K.loc[len(K)] = [tur, f"{g:%Y-%m-%d}", coin, x["s"], T[:120], f"{g + pd.Timedelta(days=1):%Y-%m-%d}", np.nan, f"{g + pd.Timedelta(days=H):%Y-%m-%d}", np.nan, np.nan, np.nan, np.nan, "bekliyor"]
            print(f"📢 {tur} {coin} ({x['s']}) · duyuru {g:%d.%m} → {g + pd.Timedelta(days=1):%d.%m} açılışında short (gölge)")
# ---- 2) işlemleri güncelle
for i, r in K.iterrows():
    gg, cg = ts(r.giris_g), ts(r.cikis_g)
    if r.durum == "bekliyor":
        m = mum(r.s, gg)
        if m is not None: K.loc[i, ["giris", "durum"]] = [m[1], "açık"]
        elif bugun > gg + pd.Timedelta(days=4): K.loc[i, "durum"] = "giriş yok"
    if K.loc[i, "durum"] == "açık":
        m = mum(r.s, cg); ct = cg
        if m is None and bugun > cg + pd.Timedelta(days=3):                                         # kontrat erken kapandıysa son kapanış
            gl = [x for x in gunler(r.s) if gg <= x <= cg]
            if gl: ct = gl[-1]; m = mum(r.s, ct)
        if m is not None:
            pe, ce = float(K.loc[i, "giris"]) * (1 - KAY), m[4] * (1 + KAY)
            K.loc[i, ["cikis_g", "cikis", "fiyat_net", "durum"]] = [f"{ct:%Y-%m-%d}", m[4], max(-(ce / pe - 1), -1.0) - UCR, "kapalı"]
for i, r in K[(K.durum == "kapalı") & K.fon.isna()].iterrows():                                      # fonlama: aylık arşiv çıkınca kesinleşir
    gg, cg = ts(r.giris_g), ts(r.cikis_g); parca = []
    for a in pd.period_range(gg.tz_convert(None), cg.tz_convert(None), freq="M"):
        d = zipcsv(f"{D}data/futures/um/monthly/fundingRate/{r.s}/{r.s}-fundingRate-{a.year}-{a.month:02d}.zip")
        if d is None: parca = None; break
        parca.append(d)
    if parca is None: continue
    f = pd.concat(parca); ft = pd.to_datetime(f[0], unit="ms", utc=True); fon = f[2][(ft >= gg) & (ft < cg + pd.Timedelta(days=1))].sum()
    K.loc[i, ["fon", "net"]] = [fon, max(r.fiyat_net + fon, -1.0)]
K.to_csv(KF, index=False)
if tam or bilinen: open(BF, "w").write("\n".join(sorted(bilinen)) + "\n")
# ---- 3) özet
Kp = K[K.durum == "kapalı"].copy(); Kp["n_"] = pd.to_numeric(Kp.net, errors="coerce").fillna(pd.to_numeric(Kp.fiyat_net, errors="coerce")); Kp["ay"] = pd.to_datetime(Kp.cikis_g).dt.to_period("M")
L_ = ["# 📢 Binance duyurusu sonrası 7 gün short — GÖLGE (gözlem amaçlı; gerçek işlem ve mesaj yok)",
      f"_{pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M} · başlangıç {BASLA:%d.%m.%Y} · D: listeden çıkarma duyurusu · S: vadelisi olan coin'in spot listelenmesi · duyurudan sonraki gün açılışta short, 7. gün kapanışta çıkış · 1× · %2 · ücret+kayma %0,40 + gerçek fonlama_",
      "_⚠️ Geçmiş testi 'veri yetersiz' çıktı (arastirma3 PROTOKOL_duyuru); yalnız gözlem. Fonlaması kesinleşmemiş işlemler 'geçici'._\n",
      f"**Durum:** bekleyen {int((K.durum == 'bekliyor').sum())} · açık {int((K.durum == 'açık').sum())} · kapanan {len(Kp)} (D {int((Kp.tur == 'D').sum())} · S {int((Kp.tur == 'S').sum())}; fonlaması kesin {int(pd.to_numeric(Kp.net, errors='coerce').notna().sum())}) · girişsiz {int((K.durum == 'giriş yok').sum())}"]
ac = K[K.durum.isin(["bekliyor", "açık"])]
if len(ac): L_ += ["| tür | coin | duyuru | giriş | çıkış | durum |", "|---|---|---|---|---|---|"] + [f"| {r.tur} | {r.coin} | {r.g} | {r.giris_g} | {r.cikis_g} | {r.durum} |" for r in ac.itertuples()]
if len(Kp):
    m = Kp.groupby("ay").n_.sum() * PAY
    L_ += [f"**Kapananlar:** işlem başı ort. {100 * Kp.n_.mean():+.1f}% · medyan {100 * Kp.n_.median():+.1f}% · kârlı %{100 * (Kp.n_ > 0).mean():.0f} · −%50'den kötü %{100 * (Kp.n_ <= -0.5).mean():.0f}",
           "| ay | işlem | aylık (%2'lik payla) |", "|---|---|---|"] + [f"| {a} | {int((Kp.ay == a).sum())} | {100 * v:+.1f}% |" for a, v in m.items()]
    if len(Kp) >= 40:
        ok = Kp.n_.mean() > 0 and Kp.n_.median() > 0 and (Kp.n_ > 0).mean() >= 0.55 and (Kp.n_ <= -0.5).mean() <= 0.10 and m.sum() > 0 and m.min() >= -0.10
        L_ += [f"\n**Önceden yazılı karar (≥ 40 işlem; ort. > 0, medyan > 0, kârlı ≥ %55, −%50'den kötü ≤ %10, toplam > 0, en kötü ay ≥ −%10): {'✅ SAĞLANDI — gerçek parayla küçük deneme kullanıcıya sorulabilir' if ok else '❌ sağlanmadı → gölge kapatılmalı'}**"]
    else: L_ += [f"\n_Karar için ≥ 40 kapanan işlem gerekiyor (şu an {len(Kp)})._"]
open(MF, "w").write("\n".join(L_) + "\n"); print(L_[3])
