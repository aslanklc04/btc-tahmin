# gonder.py — SAATLİK İŞİN SON ADIMI: bu saatte sıraya alınan Telegram mesajlarından hangilerinin gideceğine karar verir ve ÖNCELİK SIRASIYLA gönderir.
# Betikler TG_SIRALI=1 iken mesajları durum/tg_kuyruk.json'a yazar (ortak.tg_send). Her mesajın sınıfı var (11.10.2026, secim2.py R5 + secim4.py G3):
#   ana   → ✅ İŞLEM SİNYALİ, her zaman gider (en iyisi üstte, 🥇🥈🥉)
#   yedek → yalnız o gün (TR) henüz hiç işlem sinyali gitmediyse, bu saatin en iyisi 🔸 YEDEK SİNYAL olarak gider (sessiz gün kalmasın); diğerleri yalnız panelde
#   panel → hiç gitmez (yalnız panel) · bilgi → raporlar / özetler, her zaman gider
# Kararlar son_durum.md'nin sonuna ve durum/gun_durum.json'a yazılır.
import os, json, time
os.environ.pop("TG_SIRALI", None)                                                             # buradan doğrudan gönder
import pandas as pd
from ortak import tg_send, KUYRUK_F, HATA_F, DISPLAY_TZ
MADALYA = ["🥇", "🥈", "🥉"]
GUN_F = "durum/gun_durum.json"
ADLAR = {"btc": "BTC modeli", "coin": "altcoin", "d24": "24 saat", "zincir": "⛓️ arz/talep", "kucuk": "🧑 küçük yatırımcı", "prim": "💵 prim"}
YEDEK_UST = ("🔸 YEDEK SİNYAL — bugün henüz işlem sinyali çıkmadı, günün ilk uygun sinyali bu.\n"
             "Bu tür yedekler geçmişte ortalama ~%0 kazandırdı (isabet ~%55): küçük pozisyon aç ya da pas geç.")
def uyari():                                                                                   # bu saatte hata veren adım / coin varsa tek bir uyarı mesajı
    bozuk = [ADLAR.get(k, k) for k, v in (x.split("=", 1) for x in os.environ.get("ADIMLAR", "").split() if "=" in x) if v == "failure"]
    ayr = open(HATA_F, encoding="utf-8").read().strip().splitlines() if os.path.exists(HATA_F) else []
    if os.path.exists(HATA_F): os.remove(HATA_F)
    if bozuk or ayr:
        tg_send("⚠️ SİSTEM UYARISI — bu saat bazı adımlar hata verdi, sinyaller eksik olabilir:\n" + (f"Adım: {', '.join(bozuk)}\n" if bozuk else "") + "\n".join(ayr[:8]) + "\n(Düzeltilene kadar her saat tekrar eder.)")
def gecikme(m):
    gec = time.time() - m["t"]
    return f"⌛ GECİKMELİ ({gec / 60:.0f} dk) — fiyat değişmiş olabilir, işlem açmadan önce kontrol et\n" if gec > 45 * 60 else ""
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
    n = len(ana); gonderilen = 0; karar = []
    for i, m in enumerate(ana):
        ust = "✅ İŞLEM SİNYALİ" + (f" · {MADALYA[i] if i < 3 else '▫️'} ÖNCELİK {i + 1}/{n}" if n >= 2 else "") + "\n"
        if n >= 2 and i == 0: ust = (f"📋 BU SAAT {n} İŞLEM SİNYALİ — en iyisi üstte (sıra: geçmiş isabet ve kâra göre sinyal türü · aynı türde Coinbase primi yüksek olan önce)\n"
                                     + "\n".join(f"{j + 1}. {x['e']}" for j, x in enumerate(ana)) + "\n━━━━━━━━━━━━\n" + ust)
        ok = bool(tg_send(gecikme(m) + ust + m["m"])); gonderilen += ok; karar.append(("✅ ana", m["e"], "gönderildi" if ok else "GÖNDERİLEMEDİ"))
    GD["giden"] += n
    for j, m in enumerate(yedek):
        if j == 0 and n == 0 and GD["giden"] == 0:
            ust = YEDEK_UST + ("\n⛔ ABD bu sinyalin coin'ini satıyor — risk daha yüksek." if "⛔" in m["e"] else "") + "\n━━━━━━━━━━━━\n"
            ok = bool(tg_send(gecikme(m) + ust + m["m"])); gonderilen += ok; GD["giden"] += 1; karar.append(("🔸 yedek", m["e"], "gönderildi (günün ilk sinyali)" if ok else "GÖNDERİLEMEDİ"))
        else: karar.append(("🔸 yedek", m["e"], "gitmedi — bu saat işlem sinyali var" if n else ("gitmedi — bugün sinyal zaten gitti" if j == 0 else "gitmedi — bu saatin daha iyi yedeği gitti")))
    for m in panel: karar.append(("panel", m["e"], "gitmedi — yalnız panel"))
    for m in bilgi: ok = bool(tg_send(m["m"])); gonderilen += ok; karar.append(("ℹ️ bilgi", m["e"], "gönderildi" if ok else "GÖNDERİLEMEDİ"))
    print(f"Gönderildi: {gonderilen}/{len(q)} (ana {n}, yedek {len(yedek)}, panel {len(panel)}, bilgi {len(bilgi)}) · bugün giden işlem sinyali: {GD['giden']}")
    GD["log"] = (GD["log"] + [dict(t=f"{simdi:%d.%m %H:%M}", s=s_, e=e_, k=k_) for s_, e_, k_ in karar])[-40:]
    os.makedirs(os.path.dirname(GUN_F), exist_ok=True); json.dump(GD, open(GUN_F, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    if os.path.exists("son_durum.md"):                                                         # panel: Telegram kararları
        sat = [f"- {x['t']} · {x['s']} · {x['e']} → {x['k']}" for x in reversed(GD["log"][-20:])]
        open("son_durum.md", "a", encoding="utf-8").write(f"\n\n## 📨 Telegram kararları (son 20) — bugün giden işlem sinyali: {GD['giden']}\n"
            "_✅ ana = işlem sinyali (her zaman gider) · 🔸 yedek = yalnız o gün hiç sinyal gitmediyse en iyisi gider · panel = gönderilmez_\n" + ("\n".join(sat) if sat else "- (henüz yok)") + "\n")
    if os.path.exists(KUYRUK_F): os.remove(KUYRUK_F)
if __name__ == "__main__": main()
