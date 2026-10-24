# sade.py — SADE MESAJ BİÇİMİ (24.10.2026, kullanıcı onayıyla biçim belirlendi). gonder.py göndermeden hemen önce çağırır; sinyal kararlarına DOKUNMAZ.
# Kalır: sınıf · tür · saat · çıkış · coin satırı (fiyat, ⭐/A/Çok güçlü etiketleri, beklenen fiyat + %80 aralık, prim z, eski test ort./isabet) · 🎯 · 📐 pay ·
#        önemli işaretler (🔥 📉🔥 🚀 💧 💸 ⚡ 🐢 ⛔) · 📏 gerçekçi isabet/kâr · tek kural satırı · ⌛ gecikme uyarısı.
# Çıkar: "3 katı tutmak" analizleri · uzun açıklama notları · BTC geneli prim satırı · tekrar eden kural satırları · eski test dipnotu.
# 24 s 🧪 ve 💵 sinyallerinde model aralık vermediği için %80 aralık oynaklıktan: kapanış × e^(±1,2816·σ720·√H) — 24.10 kalibrasyon: içinde %79–82 (2022–24 · 2025+ · 2026).
# Çözülemeyen biçimde mesaj gelirse yalnız not satırları atılır, gerisi olduğu gibi kalır (güvenli geri dönüş).
import re, math
GR = {  # 📏 gerçekçi ölçüm (mesaj fiyatından limit giriş, vadeli komisyon + fonlama, 🎯 ile; karal2_veri 24.10): işlem isabeti 2022–24 · 2025+ · 2026, işlem başı net
    ("ana", None): ("%68 · %66 · %69", "+%0,53 · +%0,34 · +%0,51"),
    ("ana", "🌐🧪"): ("%68 · %64 · %65", "+%1,01 · +%0,59 · +%0,77"), ("ana", "🌐🤝"): ("%70 · %65 · %74", "+%0,39 · +%0,03 · +%0,64"),
    ("ana", "🤝"): ("%64 · %63 · %69", "+%0,14 · +%0,04 · +%0,36"), ("ana", "🚀"): ("%68 · %73 · %80", "+%0,32 · +%0,53 · +%0,53"),
    ("ana", "🔀"): ("%70 · %75 · %86", "+%0,54 · +%0,53 · +%0,73"),
    ("yedek", None): ("%69 · %64 · %70", "+%0,14 · −%0,09 · +%0,27"),
    ("panelden", None): ("%69 · %65 · %66", "+%0,21 · +%0,07 · +%0,12"), ("panelden", "💵"): ("%68 · %65 · %67", "+%0,26 · +%0,11 · +%0,20"),
    ("panelden", "🧪"): ("%69 · %65 · %62", "+%0,27 · −%0,02 · −%0,11"), ("panelden", "🔇/🪙"): ("%72 · %65 · %65", "+%0,09 · +%0,03 · +%0,09"),
}
KURAL = {"ana": "Kural: limit 60 dk geçerli · 🎯'ye değerse orada sat, değmezse çıkış saatinde sat · stop yok · kaldıraç en fazla 2–3x, izole · 📐 pay = normal pozisyonuna oran · aynı saatteki sinyaller tek bütçe",
         "panelden": "Kural: limit 60 dk · 🎯'ye değerse sat, değmezse çıkış saatinde · stop yok · küçük miktar, kaldıraçsız · 📐 pay = normal pozisyonuna oran",
         "yedek": "Girersen: kaldıraçsız, küçük · limit 60 dk · stop yok"}
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
    if sinif == "panelden": return "💵" if "💵" in e else ("🧪" if e.startswith("🧪") else "🔇/🪙")
    if sinif != "ana": return None
    if "🔀" in e.split(" ")[0]: return "🔀"
    if "🚀" in e.split(" ")[0]: return "🚀"
    coins = re.findall(r"([A-Z0-9]{2,12}) \(", e)
    if e.startswith("🧪") and coins and all(c in gen for c in coins): return "🌐🧪"
    if e.startswith("🤝") and coins:
        if all(c in gen for c in coins): return "🌐🤝"
        if not any(c in gen for c in coins): return "🤝"
    return None
def olcu_satiri(sinif, tur):
    i, n = GR.get((sinif, tur)) or GR.get((sinif, None)) or ("—", "—")
    ek = " → kâr çoğunlukla komisyona gidiyor" if sinif == "yedek" else ""
    return f"📏 Gerçekçi{' (' + tur + ')' if tur else ''}: isabet {i} · işlem başı {n} (2022–24 · 2025+ · 2026){ek}"
def coin_satiri(s):
    """• satırını sadeleştir: tekrar eden giriş/çıkış/stop parçalarını at, prim ve eski test etiketlerini kısalt."""
    s = s.rstrip()
    g = re.match(r"^• ((?:(?:🚀|📉🔥|💧|💸) )*)([A-Z0-9]{2,12}): kendi primi (z [+-]?[\d.]+(?: \([^)]*\))?) · limit ALIŞ (\$[0-9.,]+).*?(?:geçmiş ort\. sonuç ([+−-]%[\d.]+))?$", s)
    if g:                                                                                     # 💵 biçimi
        return f"• {g.group(1)}{g.group(2)} {g.group(4)} · prim ✅ {g.group(3)}" + (f" · eski test ort. {g.group(5)}" if g.group(5) else "")
    s = re.sub(r" — limit alış \$[0-9.,]+ · çıkış \d\d\.\d\d \d\d:\d\d \(stop koyma\)", "", s)                # 🧪 biçimi
    s = s.replace(" — ", " · ").replace(" → 4s beklenen", " · 4s beklenen").replace(" · 🌐 · 4s", " · 🌐 · 4s")
    s = re.sub(r"💵 [A-Z0-9]{2,12}: ", "prim ", s)
    s = re.sub(r"geçmiş ort\. sonuç", "eski test ort.", s)
    s = re.sub(r"geçmiş 2024\+ isabet %(\d+), 2026 %(\d+)", r"eski test isabet %\1 (2024+) / %\2 (2026)", s)
    return s
def sadelestir(metin, sinif, etiket="", gen=frozenset(), k=None, ust=""):
    """metin: üreticinin mesajı (karal_degistir + pay_ekle sonrası) · sinif: ana / yedek / panelden / bilgi · k: 🎯 katsayısı (aralık için) · ust: sınıf başlığı."""
    if sinif == "bilgi": return gunluk(metin) if metin.startswith("☀️") else metin
    L = metin.split("\n"); sure = cikis = None; baslik = None; out = []; cur = None; beklenen_var = "beklenen" in metin
    for s in L:
        m = SURE_RE.match(s)
        if m: sure, cikis = f"{m.group(1)} {'saat' if m.group(2) == 'SAAT' else 'gün'}", m.group(3); continue
        if s.startswith("• "):
            cur = coin_satiri(s); out.append([cur, []]); continue
        if s.startswith("   ") and out:
            t = s.strip()
            if t.startswith("Giriş (limit)"):
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
            g = re.match(r"💵 [A-Z0-9]{2,12} kendi Coinbase primi (z [+-]?[\d.]+) (✅|⛔|⚠️)", t)
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
        t = tek_coin(metin, sinif, etiket, gen, ust)                                         # 🔇 / 🪙 / 🔀 tek coin biçimi
        return t if t else not_at(metin)                                                   # çözülemedi → güvenli geri dönüş
    ilk = (ust.strip() + " — " if ust else "") + (baslik or "") + (f" · {sure}" if sure else "") + (f" · çıkış {cikis}" if cikis else "")
    sat = [ilk, olcu_satiri(sinif, _tur(etiket, sinif, gen))]
    for c, alt in out: sat.append(c); sat += ["   " + a for a in alt]
    sat.append(KURAL.get(sinif, ""))
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
        elif re.match(r"^💵 [A-Z0-9]{2,12}: ", x):
            g = re.search(r"z ([+-]?[\d.]+)\)\s*(✅|⛔|⚠️)?", x); prim = f"prim {g.group(2) or ''} z {g.group(1)}".replace("  ", " ") if g else ""
            if "⛔ ALMA" in x: prim += " ⛔ ALMA"
        elif x.strip().startswith("🎯 Kâr-al"):
            g = TP_RE.search(x); tp = (f"🎯 {g.group(1)} (+%{g.group(2).replace('.', ',')})" + (f" · 📐 pay ×{g.group(3)}" if g.group(3) else "")) if g else ""
        i += 1
    if not bas or not tp: return None
    g = re.match(r"^🪙\S*\s+([A-Z0-9]{2,12}) (.*?) — (?:.*?— )?🧭 \S+ (\d\d\.\d\d \d\d:\d\d) · (\$[0-9.,]+)", bas)
    if not g: return None
    nm, ad, saat, fiyat = g.groups(); isr = re.match(r"^((?:(?:🚀|📉🔥|💧|💸) )*)", etiket.split(" ", 1)[1] if " " in etiket else "").group(1) if etiket else ""
    ilk = (ust.strip() + " — " if ust else "") + f"🪙 {ad} · {saat}" + (" · 🔇 BTC sessizken" if "🔇" in bas else "") + (f" · {sure}" if sure else "") + (f" · çıkış {cikis}" if cikis else "")
    sat = [ilk, olcu_satiri(sinif, _tur(etiket, sinif, gen)), f"• {isr}{nm} {fiyat}" + (f" · {prim}" if prim else "") + (f" · ayrıca {ek}" if ek else "") + (f" · {eis}" if eis else "")] + ufuk + ["   " + tp, KURAL.get(sinif, "")]
    return "\n".join(x for x in sat if x)
