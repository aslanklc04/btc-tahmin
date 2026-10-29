# sade.py — SADE MESAJ BİÇİMİ (24.10.2026, kullanıcı onayıyla biçim belirlendi). gonder.py göndermeden hemen önce çağırır; sinyal kararlarına DOKUNMAZ.
# Kalır: sınıf · tür · saat · çıkış · coin satırı (fiyat, ⭐/A/Çok güçlü etiketleri, beklenen fiyat + %80 aralık, prim z, eski test ort./isabet) · 🎯 · 📐 pay ·
#        önemli işaretler (🔥 📉🔥 🚀 💧 💸 ⚡ 🐢 ⛔) · 📏 gerçekçi isabet/kâr · tek kural satırı · ⌛ gecikme uyarısı.
# Çıkar: "3 katı tutmak" analizleri · uzun açıklama notları · BTC geneli prim satırı · tekrar eden kural satırları · eski test dipnotu.
# 24 s 🧪 ve 💵 sinyallerinde model aralık vermediği için %80 aralık oynaklıktan: kapanış × e^(±1,2816·σ720·√H) — 24.10 kalibrasyon: içinde %79–82 (2022–24 · 2025+ · 2026).
# Çözülemeyen biçimde mesaj gelirse yalnız not satırları atılır, gerisi olduğu gibi kalır (güvenli geri dönüş).
import re, math
GR = {  # 📏 gerçekçi ölçüm (mesaj fiyatından limit giriş, vadeli komisyon + fonlama, 🎯 ile; karal2_veri 24.10): işlem isabeti 2022–24 · 2025+ · 2026, işlem başı net
    ("ana", None): ("%68 · %66 · %69", "+%0,59 · +%0,37 · +%0,54"),
    ("ana", "🌐🧪"): ("%68 · %64 · %65", "+%1,01 · +%0,59 · +%0,77"), ("ana", "🌐🤝"): ("%70 · %65 · %74", "+%0,39 · +%0,03 · +%0,64"),
    ("ana", "🤝"): ("%63 · %63 · %68", "+%0,14 · +%0,04 · +%0,36"), ("ana", "🚀"): ("%69 · %65 · %69", "+%0,43 · +%0,31 · +%0,43"),   # 25.10: ✅ ana + coin son 24 s z ≥ 2 (MOM_NOT ile aynı küme)
    ("ana", "₿🚀"): ("%65 · %71 · %80", "+%0,14 · +%0,20 · +%0,37"),                              # 25.10: yalnız BTC 🚀 ana sinyalleri (karal2_veri, B_T0)
    ("ana", "🔀"): ("%69 · %75 · %86", "+%0,56 · +%0,54 · +%0,74"),
    ("yedek", None): ("%69 · %64 · %70", "+%0,14 · −%0,09 · +%0,27"),
    ("panelden", None): ("%69 · %65 · %66", "+%0,21 · +%0,07 · +%0,13"), ("panelden", "💵"): ("%68 · %65 · %67", "+%0,26 · +%0,11 · +%0,20"),
    ("panelden", "🧪"): ("%69 · %65 · %62", "+%0,26 · −%0,02 · −%0,11"), ("panelden", "🔇/🪙"): ("%71 · %65 · %65", "+%0,09 · +%0,03 · +%0,09"),
}
KURAL = {"ana": "Kural: limit 60 dk geçerli · 🎯'ye değerse orada sat, değmezse çıkış saatinde sat · stop yok · kaldıraç en fazla 2–3x, izole · 📐 pay = normal pozisyonuna oran · aynı saatteki sinyaller tek bütçe",
         "panelden": "Kural: limit 60 dk · 🎯'ye değerse sat, değmezse çıkış saatinde · stop yok · küçük miktar, kaldıraçsız · 📐 pay = normal pozisyonuna oran",
         "yedek": "Girersen: kaldıraçsız, küçük · limit 60 dk · stop yok"}
KURAL_TUR = {"⛓️": "Kural: limit 60 dk geçerli · 🎯 yok — çıkış saatinde kapat · stop yok · kaldıraç en fazla 2x, izole",           # 25.10: ⛓️ / 🧑'de 🎯 yok (21.10 kullanıcı)
             "🧑": "Kural: limit 60 dk geçerli · 🎯 yok — çıkış saatinde sat · stop yok · kaldıraç satırdaki sınırı aşma, izole"}
AT = ("⏱ ", "⏱️", "💵 BTC geneli", "💡", "ℹ️", "🌐 = ", "✅ Seçilmiş sinyal", "Coinbase'de bu coin", "BTC 4s Çok güçlü ↑ ve aynı saatte", "⚠️ Tek işleme",
      "🔸 🌐 geniş liste", "🚀 MOMENTUM", "📉🔥 ÖNCELİKLİ", "🚀 = ", "📉🔥 = ", "💸 = ", "💸 ÖNCELİKLİ", "💧 = ", "💧📉🔥 = ", "💧💵 ", "📉🔥 💵 + DİP", "Komisyon sonrası kâr", "* eski test",
      "BTC'de güçlü sinyal yokken", "Geçmiş (", "Geçmiş 2024+", "BTC bu saatte", "4 ve 8 saat birlikte", "1s+4s+8s birlikte", "🔇 BTC sessizken")
SURE_RE = re.compile(r"^⏱ SÜRE: (\d+) (SAAT|GÜN) TUT → çıkış (\d\d\.\d\d \d\d:\d\d)")
TP_RE = re.compile(r"🎯 Kâr-al (\$[0-9.,]+) \(\+%([0-9.]+)\)(?: · 📐 pay ×([0-9,]+))?")
FIY_RE = re.compile(r"\$([0-9.,]+)")
def _f(x):
    try: return float(x.replace(",", ""))
    except Exception: return float("nan")
def _fmt(p):
    if not (p > 0): return "$?"
    if p >= 1000: return f"${p:,.0f}"
    if p >= 1: return f"${p:,.2f}" if p < 100 else f"${p:,.1f}"
    return f"${p:.{min(12, 3 - int(math.floor(math.log10(p))))}f}"
def _tur(etiket, sinif, gen):
    e = etiket or ""
    if e.startswith("⛓️"): return "⛓️"
    if e.startswith("🧑"): return "🧑"
    if sinif == "panelden": return "💵" if "💵" in e else ("🧪" if e.startswith("🧪") else "🔇/🪙")
    if sinif != "ana": return None
    if "🔀" in e.split(" ")[0]: return "🔀"
    if "🚀" in e.split(" ")[0]: return "🚀"
    coins = re.findall(r"([A-Z0-9]{1,12}) \(", e)
    if e.startswith("🧪") and coins and all(c in gen for c in coins): return "🌐🧪"
    if e.startswith("🤝") and coins:
        if all(c in gen for c in coins): return "🌐🤝"
        if not any(c in gen for c in coins): return "🤝"
    return None
def olcu_satiri(sinif, tur):
    if tur in ("⛓️", "🧑"): return "📏 Gerçekçi ölçüm yok (bu türde 🎯 kullanılmıyor) — \"Geçmiş\" satırlarındaki rakamlar eski yöntemle (🎯'siz, süre sonunda satış), örnek az"
    i, n = GR.get((sinif, tur)) or GR.get((sinif, None)) or ("—", "—")
    ek = " → kâr çoğunlukla komisyona gidiyor" if sinif == "yedek" else ""
    return f"📏 Bu sinyal 🎯 ile (2022–24 · 2025+ · 2026) — tüm coin'lerde: isabet {i} · kâr {n}{ek}"
# ---- 26.10.2026 kullanıcı onayı: "eski test" yerine coin'in KENDİ gerçekçi geçmişi (aynı sınıf + tür, 🎯 ile) — durum/coin_gercek.json (coin_gercek_tablo.py, arastirma3)
_CG = None
def _cg():
    global _CG
    if _CG is None:
        import json, os
        try: _CG = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "durum", "coin_gercek.json"), encoding="utf-8"))["tablo"]
        except Exception as e: print("coin_gercek.json okunamadı:", e); _CG = {}
    return _CG
def _yz(x, isaret=True):
    if x is None: return "—"
    if not isaret: return f"%{x:.0f}"
    if abs(x) < 0.005: return "%0,00"
    return ("+" if x >= 0 else "−") + f"%{abs(x):.2f}".replace(".", ",")
def _turler(sinif, etiket, gen, coin, satir):
    e = etiket or ""; e0 = e.split(" ")[0] if e else ""
    if sinif == "yedek": return ["G"]
    if "🚀 " in satir or "🚀" in e0 or e0.startswith("₿"): return ["🚀"]
    if "🔀" in e0: return ["🔀"]
    if e0.startswith(("🔇", "🪙")): return ["🔇/🪙"]
    if "💵" in e: return ["💵"]
    if "🧪" in e.split(":")[0]: return ["🌐🧪", "🧪"] if coin in gen else ["🧪", "🌐🧪"]
    if "🤝" in e.split(":")[0]: return (["🌐🤝", "G", "🤝"] if coin in gen else ["🤝", "🌐🤝", "G"]) + ["P"]
    return []
def coin_gecmis(sinif, etiket, gen, coin, satir=""):
    """Coin'in kendi gerçekçi geçmişi satırı (yoksa '')."""
    T = _cg().get(sinif, {}); tl = _turler(sinif, etiket, gen, coin, satir)
    if not tl: return ""
    r = next((T[t][coin] for t in tl if coin in T.get(t, {})), None)
    if r is None: return f"📏 {coin} geçmişi: yeterli örnek yok"
    (n1, i1, k1), (n2, i2, k2), (n3, i3, k3) = r; top = n1 + n2
    if top >= 30:
        return (f"📏 {coin} geçmişi: isabet {_yz(i1, False)} · {_yz(i2, False)} · {_yz(i3, False)} · kâr {_yz(k1)} · {_yz(k2)} · {_yz(k3)} ({n1} · {n2} · {n3} işlem)")
    if top >= 10:
        ii = ((i1 or 0) * n1 + (i2 or 0) * n2) / top; kk = ((k1 or 0) * n1 + (k2 or 0) * n2) / top
        return f"📏 {coin} geçmişi: {top} işlem (2022+) · isabet {_yz(ii, False)} · kâr {_yz(kk)} — örnek az"
    return f"📏 {coin} geçmişi: yeterli örnek yok ({top} işlem)"
ESKI_RE = re.compile(r" · eski test (?:ort\. [+−-]%[\d.,]+|isabet [^·]*)")
def eski_at(s):                                                                               # "eski test" parçaları ve etiketlerin yanındaki eski isabet yüzdeleri
    s = ESKI_RE.sub("", s); s = re.sub(r"(⭐ en güçlü|Çok güçlü ↑|Güçlü ↑|Zayıf ↑|A sınıfı) %\d+", r"\1", s); return s.rstrip()
def coin_satiri(s):
    """• satırını sadeleştir: tekrar eden giriş/çıkış/stop parçalarını at, prim ve eski test etiketlerini kısalt."""
    s = s.rstrip()
    g = re.match(r"^• ((?:(?:🚀|📉🔥|💧|💸) )*)([A-Z0-9]{1,12}): kendi primi (z [+-]?[\d.]+(?: \([^)]*\))?) · limit ALIŞ (\$[0-9.,]+).*?(?:geçmiş ort\. sonuç ([+−-]%[\d.]+))?$", s)
    if g:                                                                                     # 💵 biçimi (25.10: coin'e özel süre + çıkış korunur; ortak çıkış başlıktaysa sadelestir siler)
        c = re.search(r"· çıkış (\d\d\.\d\d \d\d:\d\d) \((\d+) saat\)", s)
        return (f"• {g.group(1)}{g.group(2)} {g.group(4)} · prim ✅ {g.group(3)}" + (f" · çıkış {c.group(1)} ({c.group(2)} saat)" if c else "")
                + (f" · eski test ort. {g.group(5)}" if g.group(5) else ""))
    s = re.sub(r" — limit alış \$[0-9.,]+ · çıkış \d\d\.\d\d \d\d:\d\d \(stop koyma\)", "", s)                # 🧪 biçimi
    s = s.replace(" — ", " · ").replace(" → 4s beklenen", " · 4s beklenen").replace(" · 🌐 · 4s", " · 🌐 · 4s")
    s = re.sub(r"💵 [A-Z0-9]{1,12}: ", "prim ", s)
    s = re.sub(r"geçmiş ort\. sonuç", "eski test ort.", s)
    s = re.sub(r"geçmiş 2024\+ isabet %(\d+), 2026 %(\d+)", r"eski test isabet %\1 (2024+) / %\2 (2026)", s)
    return s
def sadelestir(metin, sinif, etiket="", gen=frozenset(), k=None, ust=""):
    """metin: üreticinin mesajı (karal_degistir + pay_ekle sonrası) · sinif: ana / yedek / panelden / bilgi · k: 🎯 katsayısı (aralık için) · ust: sınıf başlığı.
    25.10.2026 kullanıcı: sade biçim önce denenir; coin, giriş fiyatı, çıkış saati, 🎯 ya da süreden biri kaybolursa (ya da hata çıkarsa) None döner → gonder.py eski biçimi yollar."""
    if sinif == "bilgi": return gunluk(metin) if metin.startswith("☀️") else metin
    try: out = _sade(metin, sinif, etiket, gen, k, ust)
    except Exception as e: print("sade biçim hatası → eski biçim:", repr(e)); return None
    if not out: print("sade biçim çözülemedi → eski biçim:", (etiket or metin[:60]).replace("\n", " ")); return None
    eksik = kontrol(metin, out)
    if eksik: print("sade biçimde eksik bilgi → eski biçim:", "; ".join(eksik[:5]), "·", (etiket or "")[:60]); return None
    return out
_SAYI = lambda x: _f(x.lstrip("$"))
GIRIS_RE = re.compile(r"(?:LİMİT alış|limit ALIŞ|limit alış|Limit ALIŞ|Limit SATIŞ \(kısa\)|Giriş \(limit\)) (\$[0-9.,]+)")
CIKIS_RE = re.compile(r"[çÇ]ıkış(?: \(ikisi için\):)? (\d\d\.\d\d \d\d:\d\d)")
COIN_RE = re.compile(r"(?m)^• (?:(?:🚀|📉🔥|💧|💸) )*([A-Z0-9]{1,12})\b")
def kontrol(ham, out):
    """Sade çıktıda temel bilgiler duruyor mu: her coin · her giriş fiyatı · her çıkış saati · her 🎯 fiyatı · süre. Dönüş: eksiklerin listesi (boşsa tamam)."""
    eksik = []; fiy = [_SAYI(x) for x in re.findall(r"\$[0-9][0-9.,]*", out)]
    var = lambda v: any(abs(f - v) <= 0.003 * v for f in fiy if f == f)
    for c in set(COIN_RE.findall(ham)) | set(re.findall(r"^🪙\S*\s+([A-Z0-9]{1,12}) ", ham, re.M)):
        if not re.search(rf"\b{re.escape(c)}\b", out): eksik.append(f"coin {c}")
    for x in set(GIRIS_RE.findall(ham)):
        v = _SAYI(x)
        if v == v and v > 0 and not var(v): eksik.append(f"giriş {x}")
    for x in set(re.findall(r"🎯 Kâr-al (\$[0-9.,]+)", ham)):
        v = _SAYI(x)
        if v == v and v > 0 and not var(v): eksik.append(f"🎯 {x}")
    for x in set(CIKIS_RE.findall(ham)) | set(m.group(3) for m in map(SURE_RE.match, ham.split("\n")) if m):
        if x not in out: eksik.append(f"çıkış {x}")
    if re.search(r"(SAAT|GÜN) TUT", ham) and not re.search(r"\d+ (saat|gün)", out): eksik.append("süre")
    return eksik
def _son_cikis(metin):
    c = CIKIS_RE.findall(metin); return max(c, key=lambda x: (x[3:5], x[0:2], x[6:])) if c else None
def btc_sade(metin, sinif, etiket, ust):
    """₿ BTC ⭐ / A sınıfı / saatlik mesaj → sade biçim: başlık · süre/çıkış · 📏 · prim · giriş/çıkış (💡) · 🎯 · ufuk satırları · kural."""
    L = metin.split("\n"); sure = cikis = None; sure_t = ""; bas = None; prim = ""; eis = ""; hiz = ""; emir = []; ufuk = []; diger = []; i = 0
    while i < len(L):
        x = L[i]; t = x.strip(); m = SURE_RE.match(x)
        if m: sure, cikis = f"{m.group(1)} {'saat' if m.group(2) == 'SAAT' else 'gün'}", m.group(3)
        elif x.startswith("⏱ SÜRE:"): h_ = re.findall(r"(\d+) SAAT", x); sure_t = ("süre " + " · ".join(dict.fromkeys(h_)) + " saat (her sinyalin çıkışı satırında)") if h_ else ""
        elif "— 🧭 BTC" in x and bas is None: bas = x.strip().replace(" — ", " · ")
        elif x.startswith(("💵 ABD", "💵 BTC")):
            g = re.search(r"z ([+-]?[\d.]+)\)\s*(✅|⛔|⚠️)?", x); prim = (f"prim {g.group(2) or ''} z {g.group(1)}".replace("  ", " ") if g else "") + (" (ABD satıyor)" if "⛔" in x else "")
        elif x.startswith(("4 ve 8 saat birlikte", "Geçmiş (", "1s+4s+8s birlikte")) and "isabet %" in x and not eis:
            eis = "eski test isabet " + " · ".join(f"%{b}" + (f" ({a.strip()})" if a else "") for a, b in re.findall(r"(\d+s )?isabet %([\d.]+)", x))
        elif x.startswith(("⚡", "🐢", "⏩")): hiz = x.split(":")[0].strip()
        elif x.startswith("💡"):
            e = t[1:].strip()
            g = re.match(r"Emir önerisi: LİMİT alış (\$[0-9.,]+)", e)
            if g: e = f"Giriş: LİMİT alış {g.group(1)} (60 dk geçerli)"
            g = re.match(r"(.*?)Giriş \(limit\) (\$[0-9.,]+) → çıkış (\d\d\.\d\d \d\d:\d\d)'de (sat|kapat) \([^)]*\)(?: · geçmiş ort\. sonuç ([+−-]%[\d.]+))?", e)
            if g: e = (g.group(1).rstrip(" —") + " · " if g.group(1).strip() else "") + f"giriş {g.group(2)} · çıkış {g.group(3)}" + (f" · eski test ort. {g.group(5)}" if g.group(5) else "")
            emir.append(e)
        elif x.startswith("   ") and (emir and L[i - 1].startswith(("💡", "   "))) and not re.match(r"^\s+beklenen", x):
            g = re.match(r"Çıkış (\d\d\.\d\d \d\d:\d\d): .*?(?:geçmiş ort\. sonuç ([+−-]%[\d.]+))?$", t)
            if g: emir.append(f"Çıkış {g.group(1)}: LİMİT satış (60 dk'da dolmazsa piyasa)" + (f" · eski test ort. {g.group(2)}" if g.group(2) else ""))
            elif t.startswith("🎯 Kâr-al"):
                g = TP_RE.search(t); emir.append((f"🎯 {g.group(1)} (+%{g.group(2).replace('.', ',')})" + (f" · 📐 pay ×{g.group(3)}" if g.group(3) else "")) if g else t)
            else: emir.append(t)
        elif re.match(r"^\d+ saat: ", x):
            b = re.search(r"beklenen (\$[0-9.,]+) · %80 aralık (\$[0-9.,]+)–(\$[0-9.,]+)", L[i + 1]) if i + 1 < len(L) else None
            ufuk.append(f"{x.split(' saat:')[0]} s: {x.split(': ', 1)[1].split(' — ')[0]}" + (f" · beklenen {b.group(1)} (%80: {b.group(2)}–{b.group(3)})" if b else ""))
            if b: i += 1
        elif x.startswith("🪙 Geçmişte bu sinyalden"): pass                                         # uzun bilgi notu (eski biçimde kalır)
        elif re.match(r"^🎯 \d+s: hedef", x): pass                                                   # bariyer modeli (stop'lu) — işlem kuralı değil, sade biçimde yok
        elif x.startswith(AT) or not t or x.startswith("━"): pass
        else: diger.append(x.rstrip())
        i += 1
    if not bas or not emir: return None
    tur = "₿🚀" if "🚀" in (etiket or "") else None
    ilk = (ust.strip() + " — " if ust else "") + bas + (f" · {sure}" if sure else (f" · {sure_t}" if sure_t else "")) + (f" · çıkış {cikis}" if cikis else "")
    cg = coin_gecmis(sinif, etiket, frozenset(), "BTC", "🚀 " if tur else "")
    sat = [ilk, olcu_satiri(sinif, tur), makro_satiri(cikis or _son_cikis(metin)), " · ".join(z for z in ("• BTC" + (" 🚀 momentum" if tur else ""), prim, hiz) if z)] + (["   " + cg] if cg else [])
    sat += ["   " + eski_at(e) for e in emir] + ["   " + u for u in ufuk] + diger + [KURAL.get(sinif, "")]
    return "\n".join(z for z in sat if z)
def _sade(metin, sinif, etiket="", gen=frozenset(), k=None, ust=""):
    L = metin.split("\n"); sure = cikis = None; baslik = None; out = []; cur = None; beklenen_var = "beklenen" in metin
    for s in L:
        m = SURE_RE.match(s)
        if m: sure, cikis = f"{m.group(1)} {'saat' if m.group(2) == 'SAAT' else 'gün'}", m.group(3); continue
        if s.startswith("• "):
            cur = coin_satiri(s); out.append([cur, []]); continue
        if s.startswith("   ") and out:
            t = s.strip()
            if t.startswith("Giriş (limit)"):
                gp = re.match(r"Giriş \(limit\) (\$[0-9.,]+)", t)                                 # 26.10: coin satırındaki yuvarlanmış fiyat yerine emirdeki tam limit fiyatı
                if gp: out[-1][0] = re.sub(r"^(• (?:(?:🚀|📉🔥|💧|💸) )*[A-Z0-9]{1,12} )\$[0-9.,]+", lambda z: z.group(1) + gp.group(1), out[-1][0], count=1)
                g = re.search(r"geçmiş ort\. sonuç ([+−-]%[\d.]+)", t)
                if g: out[-1][0] += f" · eski test ort. {g.group(1)}"
                continue
            if t.startswith("🎯 Kâr-al"):
                g = TP_RE.search(t)
                if not g: out[-1][1].append(t); continue
                tp = f"🎯 {g.group(1)} (+%{g.group(2).replace('.', ',')})" + (f" · 📐 pay ×{g.group(3)}" if g.group(3) else "")
                if not beklenen_var and k:                                                  # 🧪 / 💵: oynaklığa göre %80 aralık
                    fy = FIY_RE.search(out[-1][0]); p = _f(fy.group(1)) if fy else float("nan"); sx = float(g.group(2)) / 100 / k
                    if p > 0 and sx > 0: tp += f" · %80 aralık {_fmt(p * math.exp(-1.2816 * sx))}–{_fmt(p * math.exp(1.2816 * sx))} (oynaklığa göre)"
                out[-1][1].append(tp); continue
            g = re.match(r"💵 [A-Z0-9]{1,12} kendi Coinbase primi (z [+-]?[\d.]+) (✅|⛔|⚠️)", t)
            if g: out[-1][0] += f" · prim {g.group(2)} {g.group(1)}"; continue
            if t.startswith("🐢"): out[-1][1].append("🐢 yavaş yükseliş — 🎯'ye değmeden çıkma"); continue
            if t.startswith("⚡"): out[-1][1].append("⚡ hızlı yükseliş — hemen gir, 🎯'ye değmeden çıkma"); continue
            g = re.match(r"Geçmiş 2024\+: (\d+) işlem, isabet %(\d+)[^·]*· 2026: (\d+) işlem, %(\d+)", t)
            if g: out[-1][0] += f" · eski test isabet %{g.group(2)} (2024+, {g.group(1)} işlem) / %{g.group(4)} (2026)"; continue
            out[-1][1].append(t); continue
        if re.search(r" — (?:🧭 \S+ )?\d\d\.\d\d \d\d:\d\d", s) and not s.startswith(("✅ İŞLEM", "🔸", "📋", "ℹ️ BİLGİ", "•", " ")):
            if baslik is None: baslik = s.strip().replace(" — ", " · ")
            continue                                                                         # birleşik mesajlarda tekrar eden başlık
        if s.startswith(AT) or not s.strip() or s.startswith("━"): continue
        out.append([s.rstrip(), []])                                                       # bilinmeyen satır: koru
    if not any(o[0].startswith("• ") for o in out):
        if "— 🧭 BTC" in metin and not re.search(r"(?m)^🪙.* — .*🧭", metin): return btc_sade(metin, sinif, etiket, ust)   # 25.10: ₿ BTC ⭐ / A / saatlik
        return tek_coin(metin, sinif, etiket, gen, ust)                                      # 🔇 / 🪙 / 🔀 tek coin biçimi · çözülemezse None → gonder eski biçimi yollar
    if cikis:                                                                                # tek ortak çıkış başlıkta → coin satırında tekrar etmesin
        for o in out: o[0] = re.sub(rf" · çıkış {re.escape(cikis)} \(\d+ saat\)", "", o[0])
    tur = _tur(etiket, sinif, gen)
    ilk = (ust.strip() + " — " if ust else "") + (baslik or "") + (f" · {sure}" if sure else "") + (f" · çıkış {cikis}" if cikis else "")
    sat = [ilk, olcu_satiri(sinif, tur), makro_satiri(cikis or _son_cikis(metin))]
    for c, alt in out:
        c = eski_at(c); sat.append(c); m_ = COIN_RE.match(c)
        cg = coin_gecmis(sinif, etiket, gen, m_.group(1), c) if m_ and tur not in ("⛓️", "🧑") else ""
        sat += (["   " + cg] if cg else []) + ["   " + a for a in alt]
    sat.append(KURAL_TUR.get(tur) or KURAL.get(sinif, ""))
    return "\n".join(x for x in sat if x)
def not_at(metin):                                                                           # güvenli geri dönüş: yalnız not satırlarını at (⏱ SÜRE satırı kalır)
    return "\n".join(s for s in metin.split("\n") if SURE_RE.match(s) or not s.startswith(AT))
def gunluk(metin):
    out = []; L = metin.split("\n"); i = 0
    while i < len(L):
        s = L[i]
        if s.startswith("ℹ️ Bilgi mesajı"): i += 1; continue
        g = re.match(r"^(\d+) saat: (.+?) — (.*)$", s)
        if g and i + 1 < len(L) and "beklenen" in L[i + 1]:
            b = re.search(r"beklenen (\$[0-9,]+) · %80 aralık (\$[0-9,]+)–(\$[0-9,]+)", L[i + 1]); a = g.group(3)
            out.append(f"{g.group(1)} s: {g.group(2)}" + (f" · {a.split(' — ')[0]}" if a.startswith(("✅", "🟢", "🔴")) else "") + (f" · beklenen {b.group(1)} (%80: {b.group(2)}–{b.group(3)})" if b else "")); i += 2; continue
        out.append(s); i += 1
    return "\n".join(out)

def tek_coin(metin, sinif, etiket, gen, ust):
    """🪙 / 🔇 / 🔀 tek coin mesajı: başlık · ufuk satırları (beklenen + %80) · prim · 🎯 → sade biçim. Çözülemezse None."""
    L = metin.split("\n"); sure = cikis = None; bas = None; ufuk = []; prim = ""; tp = ""; ek = ""; eis = ""; i = 0
    while i < len(L):
        x = L[i]; m = SURE_RE.match(x)
        if m: sure, cikis = f"{m.group(1)} {'saat' if m.group(2) == 'SAAT' else 'gün'}", m.group(3)
        elif x.startswith("🪙") and bas is None: bas = x.strip()
        elif x.startswith("Bu saatte ayrıca:"): ek = x.split(":", 1)[1].strip()
        elif x.startswith(("4 ve 8 saat birlikte", "BTC'de güçlü sinyal yokken", "Geçmiş (", "1s+4s+8s birlikte")) and "isabet %" in x and not eis:
            eis = "eski test isabet " + " · ".join(f"%{b}" + (f" ({a.strip()})" if a else "") for a, b in re.findall(r"(\d+s )?isabet %(\d+)", x))
        elif re.match(r"^\d+ saat: ", x):
            b = re.search(r"beklenen (\$[0-9.,]+) · %80 aralık (\$[0-9.,]+)–(\$[0-9.,]+)", L[i + 1]) if i + 1 < len(L) else None
            ufuk.append(f"   {x.split(' saat:')[0]} s: {x.split(': ', 1)[1].split(' — ')[0]}" + (f" · beklenen {b.group(1)} (%80: {b.group(2)}–{b.group(3)})" if b else ""))
            if b: i += 1
        elif re.match(r"^💵 [A-Z0-9]{1,12}: ", x):
            g = re.search(r"z ([+-]?[\d.]+)\)\s*(✅|⛔|⚠️)?", x); prim = f"prim {g.group(2) or ''} z {g.group(1)}".replace("  ", " ") if g else ""
            if "⛔ ALMA" in x: prim += " ⛔ ALMA"
        elif x.strip().startswith("🎯 Kâr-al"):
            g = TP_RE.search(x); tp = (f"🎯 {g.group(1)} (+%{g.group(2).replace('.', ',')})" + (f" · 📐 pay ×{g.group(3)}" if g.group(3) else "")) if g else ""
        i += 1
    if not bas or not tp: return None
    g = re.match(r"^🪙\S*\s+([A-Z0-9]{1,12}) (.*?) — (?:.*?— )?🧭 \S+ (\d\d\.\d\d \d\d:\d\d) · (\$[0-9.,]+)", bas)
    if not g: return None
    nm, ad, saat, fiyat = g.groups(); gf = GIRIS_RE.search(metin); fiyat = gf.group(1) if gf else fiyat   # 25.10: limit fiyatı başlıktaki yuvarlanmış fiyattan değil emir satırından
    isr = re.match(r"^((?:(?:🚀|📉🔥|💧|💸) )*)", etiket.split(" ", 1)[1] if " " in etiket else "").group(1) if etiket else ""
    ilk = (ust.strip() + " — " if ust else "") + f"🪙 {ad} · {saat}" + (" · 🔇 BTC sessizken" if "🔇" in bas else "") + (f" · {sure}" if sure else "") + (f" · çıkış {cikis}" if cikis else "")
    cg = coin_gecmis(sinif, etiket, gen, nm, isr)
    sat = [ilk, olcu_satiri(sinif, _tur(etiket, sinif, gen)), makro_satiri(cikis), eski_at(f"• {isr}{nm} {fiyat}" + (f" · {prim}" if prim else "") + (f" · ayrıca {ek}" if ek else ""))] + (["   " + cg] if cg else []) + ufuk + ["   " + tp, KURAL.get(sinif, "")]
    return "\n".join(x for x in sat if x)

# ---- 25.10.2026 kullanıcı onayı: ⚠️ testere (iki yönde sert hareket) riski — PROTOKOL_sekil keşfi: oynaklık σ24/σ720 > 1,25 ya da hacim log(24 s / 720 s ort.) > 0,4
#      iken pencerenin ↕️ testere olma ihtimali 3,3–3,6 kat (keşif · 2025+ · dokunulmamış coin'ler, 1–24 s). Sinyali değiştirmez, yalnız kaldıraç uyarısı.
RISK = {}
COIN_SAT_RE = re.compile(r"^• (?:(?:🚀|📉🔥|💧|💸) )*([A-Z0-9]{1,12})\b")
def risk_hesapla(coinler):
    import requests, numpy as np, time as _t
    from concurrent.futures import ThreadPoolExecutor
    def bir(c):
        try:
            k = requests.get("https://data-api.binance.vision/api/v3/klines", params=dict(symbol=f"{c}USDT", interval="1h", limit=760), timeout=5).json()
            k = [x for x in k if x[6] < _t.time() * 1000]
            if len(k) < 300: return c, None
            cl = np.array([float(x[4]) for x in k]); qv = np.array([float(x[7]) for x in k]); lr = np.diff(np.log(cl))
            vol = lr[-24:].std() / lr[-720:].std(); hac = np.log(qv[-24:].sum() / (qv[-720:].mean() * 24))
            return c, (vol, hac)
        except Exception: return c, None
    with ThreadPoolExecutor(8) as ex:
        for c, v in ex.map(bir, sorted(set(coinler))):
            if v and (v[0] > 1.25 or v[1] > 0.4): RISK[c] = v
def risk_ekle(metin):
    out = []
    for x in metin.split("\n"):
        m = COIN_SAT_RE.match(x)
        if m and m.group(1) in RISK:
            v, h = RISK[m.group(1)]; x += " · ⚠️ testere riski ×3,5 (" + ("oynaklık" if v > 1.25 else "") + (" + " if v > 1.25 and h > 0.4 else "") + ("hacim" if h > 0.4 else "") + " yüksek) — kaldıracı düşür"
        out.append(x)
    return "\n".join(out)

# ---- 25.10.2026 kullanıcı onayı: FOMC / CPI uyarısı — PROTOKOL_makro M2: açıklamayı içeren 4 saatlik pencerede ↕️ testere ihtimali ×2,4–4,7
#      (keşif · 2025+ · dokunulmamış coin'ler). Tarihler durum/makro_tarih.json (resmi takvimler; her yıl güncellenmeli). Sinyali değiştirmez.
def _olaylar():
    import json, pandas as pd
    try: M = json.load(open("durum/makro_tarih.json", encoding="utf-8"))
    except Exception: return []
    ev = [(pd.Timestamp(f"{g} 14:00", tz="America/New_York"), "FOMC faiz kararı") for g in M.get("fomc", [])] + [(pd.Timestamp(f"{g} 08:30", tz="America/New_York"), "CPI enflasyon") for g in M.get("cpi", [])]
    return sorted(ev)
def makro_satiri(cikis):
    """cikis: 'gg.aa SS:DD' (TR). Şimdi → çıkış arasında FOMC/CPI açıklaması varsa uyarı satırı, yoksa ''."""
    import pandas as pd
    if not cikis: return ""
    try:
        now = pd.Timestamp.now(tz="Europe/Istanbul"); c = pd.Timestamp(f"{now.year}-{cikis[3:5]}-{cikis[0:2]} {cikis[6:11]}", tz="Europe/Istanbul")
        if c < now - pd.Timedelta(days=1): c = c + pd.DateOffset(years=1)
        ic = [(t.tz_convert("Europe/Istanbul"), ad) for t, ad in _olaylar() if now <= t <= c]
    except Exception: return ""
    if not ic: return ""
    return "⚠️ " + " · ".join(f"{ad} {t:%d.%m %H:%M} TR" for t, ad in ic[:2]) + " bu süre içinde — testere (iki yönde sert hareket) riski ×3 → kaldıracı düşür"
def takvim_uyari():
    import pandas as pd
    ev = _olaylar(); now = pd.Timestamp.now(tz="UTC")
    son_fomc = max((t for t, ad in ev if ad.startswith("FOMC")), default=None)
    return ["📅 durum/makro_tarih.json: ileriki FOMC tarihi kalmadı — yeni yılın takvimi eklenmeli (federalreserve.gov · bls.gov)"] if son_fomc is None or son_fomc < now + pd.Timedelta(days=45) else []
