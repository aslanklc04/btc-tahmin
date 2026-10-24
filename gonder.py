# gonder.py — SAATLİK İŞİN SON ADIMI: bu saatte sıraya alınan Telegram mesajlarından hangilerinin gideceğine karar verir ve ÖNCELİK SIRASIYLA gönderir.
# Betikler TG_SIRALI=1 iken mesajları durum/tg_kuyruk.json'a yazar (ortak.tg_send). Her mesajın sınıfı var (11.10.2026, secim2.py R5 · secim4.py):
#   ana   → ✅ İŞLEM SİNYALİ, her zaman gider (en iyisi üstte, 🥇🥈🥉)
#   yedek → 🔸 YEDEK SİNYAL olarak her zaman gider (kullanıcı isteği), ana sinyallerin altında; ⛔ olanlar (ABD satıyor, öncelik ≥ 2000) GİTMEZ — testte kaybettirdi
#           12.10.2026'dan beri yedek yalnız coin'in kendi primi ≥ 0 olan 🔇 / 🪙 sinyalleri (BTC saatlik ve primsizler yalnız panel)
#           (🔥 büyük işlem saati yükseltmesi 12.10.2026'da KALDIRILDI — ozet_tum.py: 2026'da %50 · +%0,18)
#           🔥 KuCoin BTC fonlaması z ≥ 2 iken de aynı (fon_vekil.py: %72 · %65 · %79, net +%0,72 · +%0,48 · +%0,88; Binance vadeli API ABD'den kapalı olduğu için KuCoin)
#   panel → hiç gitmez (yalnız panel) · bilgi → raporlar / özetler, her zaman gider
# Kararlar son_durum.md'nin sonuna ve durum/gun_durum.json'a yazılır.
import os, re, csv, json, time, requests, numpy as np
os.environ.pop("TG_SIRALI", None)                                                             # buradan doğrudan gönder
import pandas as pd
from ortak import tg_send, KUYRUK_F, HATA_F, DISPLAY_TZ, karal_degistir, KARAL_K_YEDEK, KARAL_K_PANEL, eski_isaretle
MADALYA = ["🥇", "🥈", "🥉"]
GUN_F = "durum/gun_durum.json"
RAPOR_F = "durum/haftalik_rapor.md"
KARNE_F = "durum/karne_kayit.csv"                                                             # 15.10.2026 canlı karne: her karar (bilgi hariç) kalıcı kayıt → karne.py sonucu ölçer
ADLAR = {"karne": "📒 canlı karne", "likidite": "💧 likidite ölçümü", "btc": "BTC modeli", "coin": "altcoin", "d24": "24 saat", "zincir": "⛓️ arz/talep", "kucuk": "🧑 küçük yatırımcı", "prim": "💵 prim"}
YEDEK_UST = ("ℹ️ BİLGİ · 🔸 YEDEK SİNYAL (işlem önerisi değil) — 🌐🤝 geniş liste eşik altı (coin primi 0…2). 24.10 gerçekçi ölçüm (mesaj fiyatından limit giriş, vadeli komisyon + fonlama): "
             "2022–24 isabet %69 · işlem başı +%0,14 · 2025+ %64 · −%0,09 · 2026 %70 · +%0,27 → kâr çoğunlukla komisyona gidiyor.\n"
             "İşlem açacaksan kaldıraçsız ve küçük; asıl sinyaller ✅ İŞLEM SİNYALİ başlıklı olanlar.")   # 24.10.2026 kullanıcı onayı: yedek → bilgi (karal2_sonuc.md, denetim)
PANELDEN_UST = ("🔸 YEDEK SİNYAL · 📋 PANELDEN (ana değil) — 💵 ABD alıyor / 🧪 24 s ana coin / 🔇🪙 coin tek türleri: panelden 🎯 hedefiyle (+0,45σ) 📏 gerçekçi ölçümde (mesaj fiyatından limit, vadeli komisyon + fonlama) %69 · %65 · %66 tuttu (2022–24 · 2025+ · 2026), saat isabeti %67 · %64 · %65, işlem başı +%0,21 · +%0,07 · +%0,12.\n"
                "Küçük miktar, kaldıraçsız; istersen pas geç. 30 sinyal kapandığında canlı isabet %55'in altında ya da işlem başı kâr eksideyse kendiliğinden durur.")
PANELDEN_GUN, PANELDEN_DUR_F = None, "durum/panelden_dur.json"                                     # 22.10.2026 kullanıcı onayı (panel_karal.py): panely → günde ≤ 2 🔸 yedek · karne.py durdurma kuralını yazar
ALMA_ESIK = 2000                                                                               # sira_puani: ⛔ (ABD satıyor) olanlar +20 grup → ≥ 2000
TERFI_PANEL = "🔥 yükseldi — vadelide fonlama çok yüksek (KuCoin BTC z {z:+.1f}): ABD'nin bu coin'i hafif sattığı (prim −1…0) sinyal · gerçekçi ölçümde bu saatlerde 🔥 ile ✅ ana olan sinyaller %75 · %76 · %69 tuttu (2022–24 · 2025+ · 2026), işlem başı +%0,69 · +%0,74 · +%0,45"
FON_ANA_NOT = "🔥 FONLAMA ÇOK YÜKSEK (KuCoin BTC z {z:+.1f}): gerçekçi ölçümde bu saatlerde 🔥 ile ✅ ana olan sinyaller %75 · %76 · %69 tuttu (2022–24 · 2025+ · 2026), işlem başı +%0,69 · +%0,74 · +%0,45 (normalde %68 · %66 · %69, +%0,53 · +%0,34 · +%0,51)"
TERFI_PANELX = "🔥 yükseldi — vadelide fonlama çok yüksek (KuCoin BTC z {z:+.1f}): ABD bu coin'i satıyor (⛔) · gerçekçi ölçümde bu saatlerde 🔥 ile ✅ ana olan sinyaller %75 · %76 · %69 tuttu (2022–24 · 2025+ · 2026), işlem başı +%0,69 · +%0,74 · +%0,45"
TERFI_PANELG = "🔥 yükseldi — vadelide fonlama çok yüksek (KuCoin BTC z {z:+.1f}): 🌐 geniş liste eşik altı 🤝 · gerçekçi ölçümde bu saatlerde 🔥 ile ✅ ana olan sinyaller %75 · %76 · %69 tuttu (2022–24 · 2025+ · 2026), işlem başı +%0,69 · +%0,74 · +%0,45"
TERFI_FON = "🔥 yedekten yükseldi — vadelide fonlama çok yüksek (KuCoin BTC z {z:+.1f}): gerçekçi ölçümde bu saatlerde 🔥 ile ✅ ana olan sinyaller %75 · %76 · %69 tuttu (2022–24 · 2025+ · 2026), işlem başı +%0,69 · +%0,74 · +%0,45"
TERFI_P = {"panelf": TERFI_PANEL, "panelfx": TERFI_PANELX, "panelg": TERFI_PANELG, "yedekg": TERFI_PANELG, "panely": TERFI_FON}                # 🔥 iken ✅ ana olan panel sınıfları
def fon_z():                                                                                   # fon_vekil.py: KuCoin BTC fonlaması (ABD sunucusundan açık), son 90 ödemeye göre z (≥ 2 → ⛔ olmayan yedek ana olur)
    if os.environ.get("TEST_FZ"): return float(os.environ["TEST_FZ"])                             # yalnız test
    try:
        now = int(time.time() * 1000); out = []
        for k in (2, 1):
            j = requests.get("https://api-futures.kucoin.com/api/v1/contract/funding-rates", params={"symbol": "XBTUSDTM", "from": now - k * 30 * 86400000, "to": now - (k - 1) * 30 * 86400000}, timeout=20).json()
            out += j.get("data", []) if isinstance(j, dict) else []
        d = pd.Series({int(x["timepoint"]): float(x["fundingRate"]) for x in out}).sort_index()
        if len(d) < 30: print("fonlama: az veri", len(d)); return float("nan")
        z = (d - d.rolling(90, min_periods=30).mean()) / (d.rolling(90, min_periods=30).std() + 1e-12); return float(z.iloc[-1])
    except Exception as e: print("fonlama alınamadı:", e); return float("nan")
def islem_z():                                                                                 # secim5.py T2: Binance BTC ortalama işlem büyüklüğü (24 s), son 720 saate göre z (≥ 2 → yedek ⛔ değilse ana olur)
    try:
        k = requests.get("https://data-api.binance.vision/api/v3/klines", params=dict(symbol="BTCUSDT", interval="1h", limit=1000), timeout=20).json()
        k = [x for x in k if x[6] < time.time() * 1000]                                          # yalnız kapanmış saatler
        qv = pd.Series([float(x[7]) for x in k]); n = pd.Series([float(x[8]) for x in k])
        s = np.log(qv.rolling(24).sum() / n.rolling(24).sum()); z = (s - s.rolling(720, min_periods=168).mean()) / (s.rolling(720, min_periods=168).std() + 1e-12)
        return float(z.iloc[-1])
    except Exception as e: print("işlem büyüklüğü alınamadı:", e); return float("nan")
def uyari():                                                                                   # bu saatte hata veren adım / coin varsa tek bir uyarı mesajı
    bozuk = [ADLAR.get(k, k) for k, v in (x.split("=", 1) for x in os.environ.get("ADIMLAR", "").split() if "=" in x) if v == "failure"]
    ayr = open(HATA_F, encoding="utf-8").read().strip().splitlines() if os.path.exists(HATA_F) else []
    if os.path.exists(HATA_F): os.remove(HATA_F)
    if bozuk or ayr:
        tg_send("⚠️ SİSTEM UYARISI — bu saat bazı adımlar hata verdi, sinyaller eksik olabilir:\n" + (f"Adım: {', '.join(bozuk)}\n" if bozuk else "") + "\n".join(ayr[:8]) + "\n(Düzeltilene kadar her saat tekrar eder.)")
PAY_RE = re.compile(r"(🎯 Kâr-al \$[0-9.,]+ \(\+%([0-9.]+)\))")
PAY_NOT = "📐 pay = normal pozisyonuna göre önerilen büyüklük: 🎯 uzaksa coin oynak → daha küçük gir (×1'den büyük önerilmez). Aynı saatteki bütün sinyaller tek bütçe sayılır.\n"
def pay_ekle(metin):                                                                          # 24.10.2026 kullanıcı onayı: risk payı işareti (🎯 mesafesi ≥ %1,5 → pozisyon 1,5/mesafe oranında küçülür); gölge ölçüm karne_gercek.py
    def f(m):
        try: w = min(1.0, max(0.25, round(4 * 1.5 / float(m.group(2))) / 4))
        except Exception: return m.group(0)
        return m.group(1) + f" · 📐 pay ×{w:g}".replace(".", ",")
    return PAY_RE.sub(f, metin)
KARAL_RE = re.compile(r"\n[ \t]*🎯 Kâr-al[^\n]*")
def karal_sil(t): return KARAL_RE.sub("", t)                                                    # 21.10.2026 kullanıcı: 🔸 yedekte 🎯 kâr-al yok, tahmin süresi kadar tut (karne: yedekte kâr-al neti yarıya indiriyor)
def gecikme(m):
    gec = time.time() - m["t"]
    return f"⌛ GECİKMELİ ({gec / 60:.0f} dk) — fiyat değişmiş olabilir, işlem açmadan önce kontrol et\n" if gec > 45 * 60 else ""
def yolla(t):                                                                                 # Telegram sınırı: aynı sohbete art arda çok mesajda ~1 sn ara
    t = eski_isaretle(t); ok = bool(tg_send(t)); time.sleep(1.0); return ok
ISARET_RE = re.compile(r"^• ((?:(?:🚀|📉🔥|💧|💸) )+)([A-Z0-9]{2,12})", re.M)
def isaretler(metin):                                                                         # 19.10.2026: coin satırlarındaki işaretler (📉🔥 💧 💸 🚀) karneye ayrı kayıt → "COIN:📉🔥💧|…"
    return "|".join(f"{c}:{m.replace(' ', '')}" for m, c in ISARET_RE.findall(metin or ""))
def kalabalik(ana):                                                                            # 19.10.2026 yontem3.py Y3 (önceden yazılı, üç dönem + plasebo geçti): aynı saatte ≥ 4 adet
    """4 saatlik ✅ ana coin sinyali varsa primi en yüksek 3'ü öne çıkar (paranın tamamı bu 3'e). Dönüş: mesaj satırı ya da ''."""
    S = []
    for m in ana:
        g = re.search(r"⏱ SÜRE: (\d+) SAAT", m.get("m", ""))
        if not g or int(g.group(1)) != 4: continue
        e = m.get("e", "")
        x = re.findall(r"([A-Z0-9]{2,12}) \((?:z ([+-]?[\d.]+)|prim yok)", e.split(":", 1)[-1]) if ":" in e else []
        if not x:
            h = re.match(r"^\S+ ([A-Z0-9]{2,12}) .*?prim \S+ z ([+-]?[\d.]+)", e); x = [(h.group(1), h.group(2))] if h else []
        S += [(c, float(z) if z else float("-inf")) for c, z in x]
    S = list(dict(S).items())                                                               # aynı coin bir kez
    if len(S) < 4: return ""
    ust = sorted(S, key=lambda x: -x[1])[:3]
    return (f"🎯 KALABALIK SAAT — {len(S)} adet 4 saatlik ana sinyal: parayı hepsine bölmek yerine primi en yüksek 3'üne koy → "
            + ", ".join(f"{c} (z {z:+.1f})" if np.isfinite(z) else c for c, z in ust)
            + "\n   📏 gerçekçi ölçümde (mesaj fiyatından limit, vadeli komisyon + fonlama) en iyi 3'e koymak saat başı kârı 2022–24'te +%0,17→0,21 artırdı, 2025+'da değiştirmedi (+%0,19), 2026'da düşürdü (+%0,45→0,40) → üstünlüğü kanıtlanmadı; hepsine bölmek de olur.\n")
def main():
    uyari()
    simdi = pd.Timestamp.now(tz=DISPLAY_TZ); bugun = f"{simdi:%Y-%m-%d}"
    try: GD = json.load(open(GUN_F, encoding="utf-8"))
    except Exception: GD = {}
    if GD.get("gun") != bugun: GD.update(gun=bugun, giden=0, panelden=0)
    GD.setdefault("panelden", 0)
    GD.setdefault("log", [])
    if not os.path.exists(KUYRUK_F): print("Kuyruk boş — gönderilecek mesaj yok"); q = []
    else:
        try: q = json.load(open(KUYRUK_F, encoding="utf-8"))
        except Exception as e: print("Kuyruk okunamadı:", e); q = []
    for m in q: m.setdefault("c", "ana" if m["o"] < 9000 else "bilgi")                         # eski biçim
    ana = sorted([m for m in q if m["c"] == "ana"], key=lambda m: (m["o"], m["s"])); yedek = sorted([m for m in q if m["c"] in ("yedek", "yedekg")], key=lambda m: (m["o"], m["s"]))   # 16.10: yedek = yalnız 🌐🤝 eşik altı (yedekg)
    bilgi = sorted([m for m in q if m["c"] == "bilgi"], key=lambda m: m["s"]); panel = [m for m in q if m["c"] in ("panel", "panelf", "panelfx", "panelg", "panely")]   # panely = 16.10'da panele inen eski yedekler (💵 / ana coin 🧪 / 🔇🪙)
    rapor = [m for m in q if m["c"] == "rapor"]                                               # 15.10: eski haftalık model raporları Telegram'a gitmez (yerine 📒 karne) → panele
    FZ = fon_z() if (yedek or ana or any(m["c"] in TERFI_P for m in panel)) else float("nan")
    FON_ANA = FON_ANA_NOT.format(z=FZ) if np.isfinite(FZ) and FZ >= 2 else None                # fon_ana.py: ✅ ana + BTC fonlaması z ≥ 2 → 🔥 (K0–K4 geçti)
    TERFI = TERFI_FON.format(z=FZ) if np.isfinite(FZ) and FZ >= 2 else None                    # yalnız fonlama (büyük işlem saati kaldırıldı)
    terfi = [m for m in yedek if m["o"] < ALMA_ESIK] if TERFI else []
    if terfi:                                                                                  # 🔥 yedek → ana (asıl ana sinyallerin altında sıralanır)
        for m in terfi: m["terfi"] = m["c"] if m["c"] in TERFI_P else True
        yedek = [m for m in yedek if not m.get("terfi")]; ana = ana + sorted(terfi, key=lambda m: (m["o"], m["s"]))
    pterfi = [m for m in panel if m["c"] in TERFI_P] if TERFI else []                        # 14.10 gozden.py B: coin primi −1…0 + 🔥 → ✅ ana · 15.10 ekle_ara.py: ⛔ + 🔥 ve 🌐 eşik altı + 🔥 → ✅ ana
    if pterfi:
        for m in pterfi: m["terfi"] = m["c"]; m["m"] = m["m"].replace("⛔ ALMA", "⛔ ama 🔥 fonlama çok yüksek")
        panel = [m for m in panel if not m.get("terfi")]; ana = ana + sorted(pterfi, key=lambda m: (m["o"], m["s"]))
    n = len(ana); gonderilen = 0; karar = []
    KAL = kalabalik(ana)
    for i, m in enumerate(ana):
        ust = "✅ İŞLEM SİNYALİ" + (f" · {MADALYA[i] if i < 3 else '▫️'} ÖNCELİK {i + 1}/{n}" if n >= 2 else "") + "\n" + ((TERFI_P[m["terfi"]].format(z=FZ) if m.get("terfi") in TERFI_P else TERFI) + "\n" if m.get("terfi") else "") + (FON_ANA + "\n" if FON_ANA and not m.get("terfi") else "")
        if n >= 2 and i == 0: ust = (f"📋 BU SAAT {n} İŞLEM SİNYALİ — en iyisi üstte (sıra: test edilmiş isabet ve kâra göre sinyal türü · aynı türde Coinbase primi yüksek olan önce, z ≥ 3 geriye)\n"
                                     + "\n".join(f"{j + 1}. {x['e']}" for j, x in enumerate(ana)) + (f"\n(+ altta {sum(m_['o'] < ALMA_ESIK for m_ in yedek)} 🔸 yedek sinyal)" if any(m_["o"] < ALMA_ESIK for m_ in yedek) else "") + "\n━━━━━━━━━━━━\n" + ust)
        if i == 0 and KAL: ust = KAL + "━━━━━━━━━━━━\n" + ust if n < 2 else ust.replace("━━━━━━━━━━━━\n", KAL + "━━━━━━━━━━━━\n", 1)
        ok = yolla(gecikme(m) + ust + PAY_NOT + pay_ekle(m["m"])); gonderilen += ok; karar.append(("✅ ana" + ((" (🔥 yedekten)" if m.get("terfi") in (True, "panely", "yedekg") else " (🔥 panelden)") if m.get("terfi") else ""), m["e"], "gönderildi" if ok else "GÖNDERİLEMEDİ", m))
    GD["giden"] += n
    gidecek = [m for m in yedek if m["o"] < ALMA_ESIK]; ny = len(gidecek)
    for j, m in enumerate(gidecek):
        ust = YEDEK_UST.replace("🔸 YEDEK SİNYAL", f"🔸 YEDEK SİNYAL {j + 1}/{ny}" if ny >= 2 else "🔸 YEDEK SİNYAL", 1) + "\n━━━━━━━━━━━━\n"
        ok = yolla(gecikme(m) + ust + PAY_NOT + pay_ekle(karal_degistir(m["m"], KARAL_K_YEDEK, "🔸 yedek hedefi +0,50σ (gerçekçi ölçümde isabet %64–70, kâr çok küçük)"))); gonderilen += ok; GD["giden"] += 1; karar.append(("🔸 yedek", m["e"], "gönderildi" if ok else "GÖNDERİLEMEDİ", m))   # 21.10 akşam: 🔸 yedekte de 🎯 kâr-al · 22.10: karne kaydı yorum satırında kalmıştı → düzeltildi
    for m in yedek:
        if m["o"] >= ALMA_ESIK: karar.append(("🔸 yedek", m["e"], "gitmedi — ⛔ ABD satıyor (testte kaybettirdi)", m))
    pden = sorted([m for m in panel if m["c"] == "panely" and m["o"] < ALMA_ESIK], key=lambda m: (m["o"], m["s"]))   # 22.10: 📋 panelden → 🔸 yedek (günde ≤ 2, ⛔ hariç)
    if pden and not os.path.exists(PANELDEN_DUR_F):
        hak = len(pden) if PANELDEN_GUN is None else max(0, PANELDEN_GUN - GD["panelden"]); gid_ = pden[:hak]; np_ = len(gid_)   # 22.10 akşam kullanıcı: yedek gibi sınırsız
        for j, m in enumerate(gid_):
            ust = PANELDEN_UST.replace("📋 PANELDEN", f"📋 PANELDEN {j + 1}/{np_}" if np_ >= 2 else "📋 PANELDEN", 1) + "\n━━━━━━━━━━━━\n"
            ok = yolla(gecikme(m) + ust + PAY_NOT + pay_ekle(karal_degistir(m["m"], KARAL_K_PANEL, "📋 panelden hedefi +0,45σ (gerçekçi isabet %65–69, kâr küçük)"))); gonderilen += ok; GD["giden"] += 1; GD["panelden"] += 1; karar.append(("🔸 yedek 📋 panelden", m["e"], "gönderildi" if ok else "GÖNDERİLEMEDİ", m))
        panel = [m for m in panel if m not in gid_]
    for m in panel: karar.append(("panel", m["e"], "gitmedi — yalnız panel" + (" (📋 bugünkü hak doldu)" if PANELDEN_GUN is not None and m["c"] == "panely" and m["o"] < ALMA_ESIK and not os.path.exists(PANELDEN_DUR_F) else ""), m))
    for m in bilgi: ok = yolla(m["m"]); gonderilen += ok; karar.append(("ℹ️ bilgi", m["e"], "gönderildi" if ok else "GÖNDERİLEMEDİ", m))
    print(f"Gönderildi: {gonderilen}/{len(q)} (ana {n}, yedek {len(yedek)}, panel {len(panel)}, bilgi {len(bilgi)}) · bugün giden sinyal: {GD['giden']}")
    GD["log"] = (GD["log"] + [dict(t=f"{simdi:%d.%m %H:%M}", s=s_, e=e_, k=k_) for s_, e_, k_, _ in karar])[-40:]
    try:                                                                                       # canlı karne kaydı (bilgi hariç): saat · sınıf · etiket · karar · süre (mesajın ⏱ SÜRE satırı) · 🔥 fonlama z
        yeni = not os.path.exists(KARNE_F)
        if not yeni and "isr" not in open(KARNE_F, encoding="utf-8").readline():          # eski başlık → isr sütunu eklenir (bir kez)
            _k = pd.read_csv(KARNE_F, dtype=str).fillna(""); _k["isr"] = ""; _k.to_csv(KARNE_F, index=False)
        with open(KARNE_F, "a", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            if yeni: w.writerow(["t", "s", "e", "k", "sure", "fz", "isr"])
            for s_, e_, k_, m_ in karar:
                if s_.startswith("ℹ️"): continue
                g = re.search(r"⏱ SÜRE: (\d+) (SAAT|GÜN)", m_.get("m", "")); su = (int(g.group(1)) * (24 if g.group(2) == "GÜN" else 1)) if g else ""
                w.writerow([f"{simdi:%Y-%m-%d %H:%M}", s_, e_, k_, su, f"{FZ:.2f}" if np.isfinite(FZ) else "", isaretler(m_.get("m", ""))])
    except Exception as e: print("karne kaydı yazılamadı:", e)
    os.makedirs(os.path.dirname(GUN_F), exist_ok=True); json.dump(GD, open(GUN_F, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    if os.path.exists("son_durum.md"):                                                         # panel: Telegram kararları
        sat = [f"- {x['t']} · {x['s']} · {x['e']} → {x['k']}" for x in reversed(GD["log"][-20:])]
        open("son_durum.md", "a", encoding="utf-8").write(f"\n\n## 📨 Telegram kararları (son 20) — bugün giden sinyal: {GD['giden']}\n"
            "_✅ ana = işlem sinyali · 🔸 yedek = seçilmiş sette olmayan sinyal (⛔ olanlar hariç gider) · panel = gönderilmez_\n" + ("\n".join(sat) if sat else "- (henüz yok)") + "\n")
    if rapor:                                                                                  # son haftalık model raporları: durum/haftalik_rapor.md (en yenisi üstte, son 30)
        try:
            eski = open(RAPOR_F, encoding="utf-8").read().split("\n\n---\n\n") if os.path.exists(RAPOR_F) else []
            yeni = [f"### {simdi:%d.%m.%Y %H:%M}\n" + m["m"] for m in rapor]
            open(RAPOR_F, "w", encoding="utf-8").write("\n\n---\n\n".join((yeni + [x for x in eski if x.strip() and not x.startswith("# ")])[:30]))
            if os.path.exists("son_durum.md"): open("son_durum.md", "a", encoding="utf-8").write("\n\n## 📊 Haftalık model raporları (Telegram'a gitmez — yerine 📒 karne)\n" + "\n\n".join("```\n" + m["m"] + "\n```" for m in rapor) + "\n")
        except Exception as e: print("rapor yazılamadı:", e)
    if os.path.exists(KUYRUK_F): os.remove(KUYRUK_F)
if __name__ == "__main__": main()
