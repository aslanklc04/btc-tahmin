# uctan_kontrol.py — 22.10.2026 tam denetim: uçtan uca kuru çalıştırmanın kuyruğunu ve gonder.py'nin gerçekte göndereceği metinleri denetler (main kökünde çalışır)
import json, re, sys, os, shutil, importlib
import numpy as np
SORUN, BILGI = [], []
def s(x): SORUN.append(x); print("❌", x)
def b(x): BILGI.append(x); print("ℹ️", x)
import karne, gonder, ortak
q = json.load(open("durum/tg_kuyruk.json", encoding="utf-8"))
b(f"kuyruk: {len(q)} mesaj · sınıflar: " + ", ".join(f"{k} {v}" for k, v in sorted({c: sum(m['c'] == c for m in q) for c in {m['c'] for m in q}}.items())))
SINYAL = ("ana", "yedek", "yedekg", "panely", "panelf", "panelfx", "panelg", "panel")
for m in q:
    t, e = m["m"], m["e"]
    if re.search(r"\bnan\b|\$\?|\bNone\b|\binf\b", t): s(f"bozuk değer ({m['c']}): {e[:60]} → " + "; ".join(re.findall(r".{0,40}(?:\bnan\b|\$\?|\bNone\b|\binf\b).{0,20}", t))[:200])
    if m["c"] in SINYAL:
        g = re.search(r"⏱ SÜRE: (\d+) (SAAT|GÜN)", t); su = (int(g.group(1)) * (24 if g.group(2) == "GÜN" else 1)) if g else ""
        try: r = karne.coz(e, su)
        except Exception as ex: r = None; s(f"karne etiketi çözemedi (hata {ex}): {e[:80]}")
        if r is not None and len(r) == 0 and m["c"] in ("ana", "yedek", "yedekg", "panely"): s(f"karne bu sinyali ÖLÇEMEZ (etiket çözülmedi): [{m['c']}] {e[:90]}")
        if m["c"] in ("ana", "yedek", "yedekg", "panely") and not g: b(f"⏱ SÜRE satırı yok (karne varsayılan süreyi kullanır): [{m['c']}] {e[:70]}")
    if "🎯" in t:
        for l in t.split("\n"):
            if any(k in l for k in ("🐢", "⏩", "⚡ Prim")) and "🎯 hedefe" not in l: s(f"hız notu 🎯 ile çelişiyor: {l.strip()[:90]}")
    if (e.startswith("⛓️") or e.startswith("🧑")) and "🎯" in t: s(f"⛓️/🧑 mesajında 🎯 olmamalı: {e[:60]}")
nld = sum("📋 panelden → ✅ ANA" in m["m"] and m["c"] == "ana" for m in q)
b(f"💧 ile anaya çıkan panelden mesajı: {nld}")
if nld == 0: s("💧 zorlandığı hâlde 📋 panelden → ✅ ana mesajı oluşmadı")
# gonder'in gerçekten göndereceği metinler (iki fonlama durumu)
for fz in ("0.5", "2.5"):
    shutil.copy("durum/tg_kuyruk.json", "/tmp/kuyruk_yedek.json")
    if os.path.exists("durum/gun_durum.json"): shutil.copy("durum/gun_durum.json", "/tmp/gun_yedek.json")
    os.environ["TEST_FZ"] = fz; importlib.reload(gonder); G = []
    gonder.yolla = lambda x: (G.append(x), True)[1]
    gonder.main()
    shutil.copy("/tmp/kuyruk_yedek.json", "durum/tg_kuyruk.json")
    if os.path.exists("/tmp/gun_yedek.json"): shutil.copy("/tmp/gun_yedek.json", "durum/gun_durum.json")
    say = {"ana": 0, "yedek": 0, "panelden": 0, "bilgi": 0}
    for x in G:
        bas = x[:400]
        if "📋 PANELDEN" in bas: tur, beklenen = "panelden", "📋 panelden hedefi +0,45σ"
        elif "🔸 YEDEK SİNYAL" in bas: tur, beklenen = "yedek", "🔸 yedek hedefi +0,50σ"
        elif "✅ İŞLEM SİNYALİ" in bas: tur, beklenen = "ana", "testte ✅ ana isabet"
        else: tur, beklenen = "bilgi", None
        say[tur] += 1
        P = ortak.mesaj_parcala(x)
        if any(len(p) > 4096 for p in P): s(f"[{fz}] parça 4096'dan uzun: {x[:80]!r}")
        if len(P) > 1: b(f"[{fz}] {len(x)} karakterlik mesaj {len(P)} parçaya bölünecek")
        kay = [c for c in re.findall(r"\n• ([^\n]{0,25})", x) if not any(c in p for p in P)]
        if kay: s(f"[{fz}] bölmede kaybolan coin satırı: {kay[:3]}")
        for l in x.split("\n"):
            if "🎯 Kâr-al" in l:
                if beklenen and beklenen not in l: s(f"[🔥 z={fz}] {tur} mesajında yanlış 🎯 hedefi: {l.strip()[:120]}")
                mm = re.search(r"\(\+%([0-9.]+)\)", l)
                if mm and not (0.05 <= float(mm.group(1)) <= 60): s(f"[{fz}] 🎯 yüzdesi tuhaf: {l.strip()[:100]}")
    b(f"🔥 z={fz}: gidecek {len(G)} mesaj → " + ", ".join(f"{k} {v}" for k, v in say.items()))
    if fz == "2.5" and say["yedek"] + say["panelden"] > 0 and any("🔥" in x[:300] for x in G) is False: s("🔥 iken yükselme olmadı")
print("\n" + ("✅ SORUN YOK" if not SORUN else f"❌ {len(SORUN)} SORUN"))
open("uctan_sonuc.md", "w").write("# Uçtan uca denetim\n\n## Sorunlar\n" + ("\n".join("- " + x for x in SORUN) or "- yok") + "\n\n## Bilgi\n" + "\n".join("- " + x for x in BILGI) + "\n")
