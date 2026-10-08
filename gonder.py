# gonder.py — SAATLİK İŞİN SON ADIMI: bu saatte sıraya alınan Telegram mesajlarını ÖNCELİK SIRASIYLA gönderir (en iyi sinyal en üstte).
# Betikler TG_SIRALI=1 iken mesajları durum/tg_kuyruk.json'a yazar (ortak.tg_send). Sıra: ortak.sira_puani (sinyal türü → aynı türde Coinbase primi yüksek olan önce → ⛔ en sonda).
# Sinyal mesajlarının başına "🥇 1/3" gibi sıra yazılır; birden çok sinyal varsa ilk mesajın başında bu saatin kısa listesi olur. Raporlar ve bilgi mesajları sinyallerden sonra gider.
import os, json, time
os.environ.pop("TG_SIRALI", None)                                                             # buradan doğrudan gönder
from ortak import tg_send, KUYRUK_F
MADALYA = ["🥇", "🥈", "🥉"]
def main():
    if not os.path.exists(KUYRUK_F): print("Kuyruk boş — gönderilecek mesaj yok"); return
    try: q = json.load(open(KUYRUK_F, encoding="utf-8"))
    except Exception as e: print("Kuyruk okunamadı:", e); q = []
    sinyal = sorted([m for m in q if m["o"] < 9000], key=lambda m: (m["o"], m["s"])); diger = sorted([m for m in q if m["o"] >= 9000], key=lambda m: m["s"])
    n = len(sinyal); gonderilen = 0
    for i, m in enumerate(sinyal):
        ust = ""
        if n >= 2:
            ust = f"{MADALYA[i] if i < 3 else '▫️'} ÖNCELİK {i + 1}/{n}\n"
            if i == 0: ust = (f"📋 BU SAAT {n} SİNYAL — en iyisi üstte (sıra: geçmiş isabet ve kâra göre sinyal türü · aynı türde Coinbase primi yüksek olan önce · ⛔ olanlar en sonda)\n"
                              + "\n".join(f"{j + 1}. {x['e']}" for j, x in enumerate(sinyal)) + "\n━━━━━━━━━━━━\n" + ust)
        gec = time.time() - m["t"]
        if gec > 45 * 60: ust = f"⌛ GECİKMELİ ({gec / 60:.0f} dk) — fiyat değişmiş olabilir, işlem açmadan önce kontrol et\n" + ust
        gonderilen += bool(tg_send(ust + m["m"]))
    for m in diger: gonderilen += bool(tg_send(m["m"]))
    print(f"Gönderildi: {gonderilen}/{len(q)} (sinyal {n}, diğer {len(diger)})")
    os.remove(KUYRUK_F)
if __name__ == "__main__": main()
