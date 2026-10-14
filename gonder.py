# gonder.py — SAATLİK İŞİN SON ADIMI: bu saatte sıraya alınan Telegram mesajlarından hangilerinin gideceğine karar verir ve ÖNCELİK SIRASIYLA gönderir.
# Betikler TG_SIRALI=1 iken mesajları durum/tg_kuyruk.json'a yazar (ortak.tg_send). Her mesajın sınıfı var (11.10.2026, secim2.py R5 · secim4.py):
#   ana   → ✅ İŞLEM SİNYALİ, her zaman gider (en iyisi üstte, 🥇🥈🥉)
#   yedek → 🔸 YEDEK SİNYAL olarak her zaman gider (kullanıcı isteği), ana sinyallerin altında; ⛔ olanlar (ABD satıyor, öncelik ≥ 2000) GİTMEZ — testte kaybettirdi
#           12.10.2026'dan beri yedek yalnız coin'in kendi primi ≥ 0 olan 🔇 / 🪙 sinyalleri (BTC saatlik ve primsizler yalnız panel)
#           (🔥 büyük işlem saati yükseltmesi 12.10.2026'da KALDIRILDI — ozet_tum.py: 2026'da %50 · +%0,18)
#           🔥 KuCoin BTC fonlaması z ≥ 2 iken de aynı (fon_vekil.py: %72 · %65 · %79, net +%0,72 · +%0,48 · +%0,88; Binance vadeli API ABD'den kapalı olduğu için KuCoin)
#   panel → hiç gitmez (yalnız panel) · bilgi → raporlar / özetler, her zaman gider
# Kararlar son_durum.md'nin sonuna ve durum/gun_durum.json'a yazılır.
import os, json, time, requests, numpy as np
os.environ.pop("TG_SIRALI", None)                                                             # buradan doğrudan gönder
import pandas as pd
from ortak import tg_send, KUYRUK_F, HATA_F, DISPLAY_TZ
MADALYA = ["🥇", "🥈", "🥉"]
GUN_F = "durum/gun_durum.json"
ADLAR = {"btc": "BTC modeli", "coin": "altcoin", "d24": "24 saat", "zincir": "⛓️ arz/talep", "kucuk": "🧑 küçük yatırımcı", "prim": "💵 prim"}
YEDEK_UST = ("🔸 YEDEK SİNYAL (ana değil) — isabeti ana sinyal çizgisinin (~%59) altında; bu türün test sonucu mesajın içinde yazıyor.\n"
             "İstersen küçük pozisyon, istersen pas geç. Asıl sinyaller ✅ İŞLEM SİNYALİ başlıklı olanlar.")
ALMA_ESIK = 2000                                                                               # sira_puani: ⛔ (ABD satıyor) olanlar +20 grup → ≥ 2000
TERFI_PANEL = "🔥 yükseldi — vadelide fonlama çok yüksek (KuCoin BTC z {z:+.1f}): ABD'nin bu coin'i hafif sattığı (prim −1…0) sinyaller bu saatlerde %77 · %71 · %85 tuttu (2022–23 · 2024+ · 2026), işlem başı +%0,8–1,9"
FON_ANA_NOT = "🔥 FONLAMA ÇOK YÜKSEK (KuCoin BTC z {z:+.1f}): bu saatlerde ✅ ana sinyaller testte %72 · %75 · %86 tuttu (2022–23 · 2024+ · 2026), işlem başı +%0,9–2,2 (normalde %59–67, +%0,4–0,9)"
TERFI_FON = "🔥 yedekten yükseldi — vadelide fonlama çok yüksek (KuCoin BTC z {z:+.1f}): bu saatlerde 🔸 yedekler testte %60–77 tuttu (2022–23 · 2024+; kombin.py), işlem başı +%0,5–3,5"
def fon_z():                                                                                   # fon_vekil.py: KuCoin BTC fonlaması (ABD sunucusundan açık), son 90 ödemeye göre z (≥ 2 → ⛔ olmayan yedek ana olur)
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
def gecikme(m):
    gec = time.time() - m["t"]
    return f"⌛ GECİKMELİ ({gec / 60:.0f} dk) — fiyat değişmiş olabilir, işlem açmadan önce kontrol et\n" if gec > 45 * 60 else ""
def yolla(t):                                                                                 # Telegram sınırı: aynı sohbete art arda çok mesajda ~1 sn ara
    ok = bool(tg_send(t)); time.sleep(1.0); return ok
def main():
    uyari()
    simdi = pd.Timestamp.now(tz=DISPLAY_TZ); bugun = f"{simdi:%Y-%m-%d}"
    try: GD = json.load(open(GUN_F, encoding="utf-8"))
    except Exception: GD = {}
    if GD.get("gun") != bugun: GD.update(gun=bugun, giden=0)
    GD.setdefault("log", [])
    if not os.path.exists(KUYRUK_F): print("Kuyruk boş — gönderilecek mesaj yok"); q = []
    else:
        try: q = json.load(open(KUYRUK_F, encoding="utf-8"))
        except Exception as e: print("Kuyruk okunamadı:", e); q = []
    for m in q: m.setdefault("c", "ana" if m["o"] < 9000 else "bilgi")                         # eski biçim
    ana = sorted([m for m in q if m["c"] == "ana"], key=lambda m: (m["o"], m["s"])); yedek = sorted([m for m in q if m["c"] == "yedek"], key=lambda m: (m["o"], m["s"]))
    bilgi = sorted([m for m in q if m["c"] == "bilgi"], key=lambda m: m["s"]); panel = [m for m in q if m["c"] in ("panel", "panelf")]
    FZ = fon_z() if (yedek or ana or any(m["c"] == "panelf" for m in panel)) else float("nan")
    FON_ANA = FON_ANA_NOT.format(z=FZ) if np.isfinite(FZ) and FZ >= 2 else None                # fon_ana.py: ✅ ana + BTC fonlaması z ≥ 2 → 🔥 (K0–K4 geçti)
    TERFI = TERFI_FON.format(z=FZ) if np.isfinite(FZ) and FZ >= 2 else None                    # yalnız fonlama (büyük işlem saati kaldırıldı)
    terfi = [m for m in yedek if m["o"] < ALMA_ESIK] if TERFI else []
    if terfi:                                                                                  # 🔥 yedek → ana (asıl ana sinyallerin altında sıralanır)
        for m in terfi: m["terfi"] = True
        yedek = [m for m in yedek if not m.get("terfi")]; ana = ana + sorted(terfi, key=lambda m: (m["o"], m["s"]))
    pterfi = [m for m in panel if m["c"] == "panelf"] if TERFI else []                       # 14.10 gozden.py B: coin primi −1…0 + 🔥 → ✅ ana (%77 · %71 · %85)
    if pterfi:
        for m in pterfi: m["terfi"] = "panel"
        panel = [m for m in panel if not m.get("terfi")]; ana = ana + sorted(pterfi, key=lambda m: (m["o"], m["s"]))
    n = len(ana); gonderilen = 0; karar = []
    for i, m in enumerate(ana):
        ust = "✅ İŞLEM SİNYALİ" + (f" · {MADALYA[i] if i < 3 else '▫️'} ÖNCELİK {i + 1}/{n}" if n >= 2 else "") + "\n" + ((TERFI_PANEL.format(z=FZ) if m.get("terfi") == "panel" else TERFI) + "\n" if m.get("terfi") else "") + (FON_ANA + "\n" if FON_ANA and not m.get("terfi") else "")
        if n >= 2 and i == 0: ust = (f"📋 BU SAAT {n} İŞLEM SİNYALİ — en iyisi üstte (sıra: test edilmiş isabet ve kâra göre sinyal türü · aynı türde Coinbase primi yüksek olan önce, z ≥ 3 geriye)\n"
                                     + "\n".join(f"{j + 1}. {x['e']}" for j, x in enumerate(ana)) + (f"\n(+ altta {sum(m_['o'] < ALMA_ESIK for m_ in yedek)} 🔸 yedek sinyal)" if any(m_["o"] < ALMA_ESIK for m_ in yedek) else "") + "\n━━━━━━━━━━━━\n" + ust)
        ok = yolla(gecikme(m) + ust + m["m"]); gonderilen += ok; karar.append(("✅ ana" + ((" (🔥 panelden)" if m.get("terfi") == "panel" else " (🔥 yedekten)") if m.get("terfi") else ""), m["e"], "gönderildi" if ok else "GÖNDERİLEMEDİ"))
    GD["giden"] += n
    gidecek = [m for m in yedek if m["o"] < ALMA_ESIK]; ny = len(gidecek)
    for j, m in enumerate(gidecek):
        ust = YEDEK_UST.replace("🔸 YEDEK SİNYAL", f"🔸 YEDEK SİNYAL {j + 1}/{ny}" if ny >= 2 else "🔸 YEDEK SİNYAL", 1) + "\n━━━━━━━━━━━━\n"
        ok = yolla(gecikme(m) + ust + m["m"]); gonderilen += ok; GD["giden"] += 1; karar.append(("🔸 yedek", m["e"], "gönderildi" if ok else "GÖNDERİLEMEDİ"))
    for m in yedek:
        if m["o"] >= ALMA_ESIK: karar.append(("🔸 yedek", m["e"], "gitmedi — ⛔ ABD satıyor (testte kaybettirdi)"))
    for m in panel: karar.append(("panel", m["e"], "gitmedi — yalnız panel"))
    for m in bilgi: ok = yolla(m["m"]); gonderilen += ok; karar.append(("ℹ️ bilgi", m["e"], "gönderildi" if ok else "GÖNDERİLEMEDİ"))
    print(f"Gönderildi: {gonderilen}/{len(q)} (ana {n}, yedek {len(yedek)}, panel {len(panel)}, bilgi {len(bilgi)}) · bugün giden sinyal: {GD['giden']}")
    GD["log"] = (GD["log"] + [dict(t=f"{simdi:%d.%m %H:%M}", s=s_, e=e_, k=k_) for s_, e_, k_ in karar])[-40:]
    os.makedirs(os.path.dirname(GUN_F), exist_ok=True); json.dump(GD, open(GUN_F, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    if os.path.exists("son_durum.md"):                                                         # panel: Telegram kararları
        sat = [f"- {x['t']} · {x['s']} · {x['e']} → {x['k']}" for x in reversed(GD["log"][-20:])]
        open("son_durum.md", "a", encoding="utf-8").write(f"\n\n## 📨 Telegram kararları (son 20) — bugün giden sinyal: {GD['giden']}\n"
            "_✅ ana = işlem sinyali · 🔸 yedek = seçilmiş sette olmayan sinyal (⛔ olanlar hariç gider) · panel = gönderilmez_\n" + ("\n".join(sat) if sat else "- (henüz yok)") + "\n")
    if os.path.exists(KUYRUK_F): os.remove(KUYRUK_F)
if __name__ == "__main__": main()
