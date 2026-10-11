# gonder.py — SAATLİK İŞİN SON ADIMI: bu saatte sıraya alınan Telegram mesajlarından hangilerinin gideceğine karar verir ve ÖNCELİK SIRASIYLA gönderir.
# Betikler TG_SIRALI=1 iken mesajları durum/tg_kuyruk.json'a yazar (ortak.tg_send). Her mesajın sınıfı var (11.10.2026, secim2.py R5 · secim4.py):
#   ana   → ✅ İŞLEM SİNYALİ, her zaman gider (en iyisi üstte, 🥇🥈🥉)
#   yedek → 🔸 YEDEK SİNYAL olarak her zaman gider (kullanıcı isteği), ana sinyallerin altında; ⛔ olanlar (ABD satıyor, öncelik ≥ 2000) GİTMEZ — testte kaybettirdi
#           🔥 Binance BTC ort. işlem büyüklüğü z ≥ 2 iken (büyük oyuncular aktif) ⛔ olmayan yedekler ✅ ana olur (secim5.py T2: 2022–23 %66 · 2024+ %61 · 2026 net +%0,27)
#   panel → hiç gitmez (yalnız panel) · bilgi → raporlar / özetler, her zaman gider
# Kararlar son_durum.md'nin sonuna ve durum/gun_durum.json'a yazılır.
import os, json, time, requests, numpy as np
os.environ.pop("TG_SIRALI", None)                                                             # buradan doğrudan gönder
import pandas as pd
from ortak import tg_send, KUYRUK_F, HATA_F, DISPLAY_TZ
MADALYA = ["🥇", "🥈", "🥉"]
GUN_F = "durum/gun_durum.json"
ADLAR = {"btc": "BTC modeli", "coin": "altcoin", "d24": "24 saat", "zincir": "⛓️ arz/talep", "kucuk": "🧑 küçük yatırımcı", "prim": "💵 prim"}
YEDEK_UST = ("🔸 YEDEK SİNYAL (ana değil) — seçilmiş sette değil: bu tür sinyaller geçmişte ortalama ~%0 kazandırdı (isabet ~%55).\n"
             "İstersen küçük pozisyon, istersen pas geç. Asıl sinyaller ✅ İŞLEM SİNYALİ başlıklı olanlar.")
ALMA_ESIK = 2000                                                                               # sira_puani: ⛔ (ABD satıyor) olanlar +20 grup → ≥ 2000
TERFI_UST = "✅ İŞLEM SİNYALİ · 🔥 yedekten yükseldi — büyük oyuncular aktif (BTC ort. işlem büyüklüğü z {z:+.1f}): bu saatlerde yedekler geçmişte %61 tuttu, işlem başı +%0,4"
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
    bilgi = sorted([m for m in q if m["c"] == "bilgi"], key=lambda m: m["s"]); panel = [m for m in q if m["c"] == "panel"]
    IZ = islem_z() if yedek else float("nan"); terfi = [m for m in yedek if m["o"] < ALMA_ESIK] if np.isfinite(IZ) and IZ >= 2 else []
    if terfi:                                                                                  # 🔥 yedek → ana (asıl ana sinyallerin altında sıralanır)
        for m in terfi: m["terfi"] = True
        yedek = [m for m in yedek if not m.get("terfi")]; ana = ana + sorted(terfi, key=lambda m: (m["o"], m["s"]))
    n = len(ana); gonderilen = 0; karar = []
    for i, m in enumerate(ana):
        ust = (TERFI_UST.format(z=IZ) if m.get("terfi") else "✅ İŞLEM SİNYALİ") + (f" · {MADALYA[i] if i < 3 else '▫️'} ÖNCELİK {i + 1}/{n}" if n >= 2 else "") + "\n"
        if n >= 2 and i == 0: ust = (f"📋 BU SAAT {n} İŞLEM SİNYALİ — en iyisi üstte (sıra: geçmiş isabet ve kâra göre sinyal türü · aynı türde Coinbase primi yüksek olan önce)\n"
                                     + "\n".join(f"{j + 1}. {x['e']}" for j, x in enumerate(ana)) + (f"\n(+ altta {sum(m_['o'] < ALMA_ESIK for m_ in yedek)} 🔸 yedek sinyal)" if any(m_["o"] < ALMA_ESIK for m_ in yedek) else "") + "\n━━━━━━━━━━━━\n" + ust)
        ok = yolla(gecikme(m) + ust + m["m"]); gonderilen += ok; karar.append(("✅ ana" + (" (🔥 yedekten)" if m.get("terfi") else ""), m["e"], "gönderildi" if ok else "GÖNDERİLEMEDİ"))
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
