# tg_ayristir.py — Telegram dışa aktarımını (metin) sinyal tablosuna çevirir. Saatler Türkiye saati (UTC+3).
import re, sys, json, pandas as pd
TR = pd.Timedelta(hours=3)
def zaman(s, yil=2026):                                   # "07.10 06:00" veya "07.10.2026 06:05" → UTC Timestamp
    s = s.strip(); f = "%d.%m.%Y %H:%M" if s.count(".") == 2 else "%d.%m %H:%M"
    t = pd.to_datetime(s if s.count(".") == 2 else f"{s}", format=f)
    if t.year == 1900: t = t.replace(year=yil)
    return (t - TR).tz_localize("UTC")
num = lambda s: float(s.replace(",", "").replace("$", ""))
def mesajlar(yollar):
    gor, M = set(), []
    for y in yollar:
        cur = None
        for ln in open(y, encoding="utf-8").read().splitlines():
            m = re.match(r"^\[(\d\d\.\d\d\.\d{4} \d\d:\d\d)\] [^:]+: (.*)$", ln)
            if m:
                cur = [m.group(1), [m.group(2)]]; M.append(cur)
            elif cur: cur[1].append(ln)
    out = []
    for g, L in M:
        k = (g, "\n".join(L))
        if k in gor: continue
        gor.add(k); out.append((zaman(g), "\n".join(L)))
    return out
YON = {"⬆️": 1, "⬇️": -1}
def prim(txt, coin):                                       # sinyalin bağlı olduğu prim durumu
    for ln in txt.splitlines():
        if "💵" in ln and "z " in ln:
            seg = ln.split("BTC geneli")[0]
            if "z " not in seg: continue
            for e in ("⛔", "⚠️", "✅"):
                if e in seg: return e
    return "yok"
def ayristir(yollar):
    S, P, B, I = [], [], [], []                            # S: işlem sinyalleri, P: yön tahminleri, B: 🎯 bariyer, I: %80 aralık/beklenen
    for gonder, t in mesajlar(yollar):
        bas = t.splitlines()[0]
        if "24 SAAT ÇOK GÜÇLÜ" in t:
            et = zaman(re.search(r"24 SAAT ÇOK GÜÇLÜ ↑ — (\d\d\.\d\d \d\d:\d\d)", t).group(1))
            for coin, p, lim, cik, rest in re.findall(r"• (\w+) \$([\d,\.]+) — limit alış \$([\d,\.]+) · çıkış (\d\d\.\d\d \d\d:\d\d)([^\n]*\n?(?:   💵[^\n]*)?)", t):
                pr = "⛔" if "⛔" in rest else "⚠️" if "⚠️" in rest else "✅" if "✅" in rest else "yok"
                S.append(dict(gonder=gonder, et=et, coin=coin, tur="🧪 24 saat deneme", H=24, yon=1, fiyat=num(p), limit=num(lim), prim=pr))
        elif "🔻 BTC KISA" in t:
            m = re.search(r"🧭 BTC (\d\d\.\d\d \d\d:\d\d) · \$([\d,\.]+)", t); lim = re.search(r"kısa \(satış\) \$([\d,\.]+)", t)
            S.append(dict(gonder=gonder, et=zaman(m.group(1)), coin="BTC", tur="🔻 BTC kısa (24s)", H=24, yon=-1, fiyat=num(m.group(2)), limit=num(lim.group(1)), prim="kısa"))
        elif "⛓️🔻" in t:
            m = re.search(r"Limit SATIŞ \(kısa\) \$([\d,\.]+) · çıkış (\d\d\.\d\d \d\d:\d\d)", t); coin = re.search(r"⛓️🔻 (\w+)", t).group(1)
            S.append(dict(gonder=gonder, et=gonder.floor("h"), coin=coin, tur="⛓️ arz/talep kısa (7 gün)", H=168, yon=-1, fiyat=num(m.group(1)), limit=num(m.group(1)), prim="kısa"))
        else:
            pass
        if any(k in t for k in ("24 SAAT ÇOK GÜÇLÜ", "🔻 BTC KISA", "⛓️🔻")): continue
        m = re.search(r"🧭 (\w+) (\d\d\.\d\d \d\d:\d\d) · \$([\d,\.]+)", t)
        if m:
            coin, et, fiyat = m.group(1), zaman(m.group(2)), num(m.group(3))
            ozet = "Günlük özet" in bas
            # yön tahminleri (tek satır ya da çok satır)
            for h, yon, guc in re.findall(r"(\d) saat: (⬆️|⬇️) (Çok güçlü|Güçlü|Zayıf)", t):
                P.append(dict(gonder=gonder, et=et, coin=coin, H=int(h), yon=YON[yon], guc=guc, fiyat=fiyat, ozet=ozet))
            for h, bek, a, b in re.findall(r"(\d) saat:[^\n]*\n\s+beklenen \$([\d,\.]+) · %80 aralık \$([\d,\.]+)–\$([\d,\.]+)", t):
                I.append(dict(et=et, coin=coin, H=int(h), bek=num(bek), a=num(a), b=num(b), fiyat=fiyat, ozet=ozet))
            for h, hd, st, ilk, guc, gec in re.findall(r"🎯 (\d)s: hedef \$([\d,\.]+) / stop \$([\d,\.]+) → önce (HEDEF|STOP) \(([^,]+), geçmiş %(\d+)\)", t):
                B.append(dict(et=et, coin=coin, H=int(h), hedef=num(hd), stop=num(st), tahmin=ilk, guc=guc, gecmis=int(gec), fiyat=fiyat))
            if ozet: continue
            pr = prim(t, coin)
            gl = re.search(r"Giriş \(limit\) \$([\d,\.]+) → çıkış (\d\d\.\d\d \d\d:\d\d)", t)
            gir = num(gl.group(1)) if gl else None
            def ekle(tur, H):
                S.append(dict(gonder=gonder, et=et, coin=coin, tur=tur, H=H, yon=1, fiyat=fiyat, limit=gir, prim=pr))
            if "A SINIFI SİNYAL" in bas: ekle("₿ A sınıfı (4s)", 4)
            elif "⭐ EN GÜÇLÜ — BTC SESSİZKEN" in bas: ekle("🔇 coin ⭐ BTC sessizken (4s)", 4)
            elif "⭐ EN GÜÇLÜ SİNYAL" in bas: ekle("🪙 coin ⭐ (4s)", 4); ekle("🪙 coin ⭐ (8s)", 8)
            elif "🟢 A SINIFI" in bas and coin != "BTC": ekle("🪙 coin A sınıfı (4s)", 4)
            elif "4 SAAT ÇOK GÜÇLÜ" in bas: ekle("🪙 coin 4s çok güçlü (4s)", 4)
            if coin == "BTC" and "✅ ALIM SİNYALİ — 8 saat" in t: ekle("₿ 8s ALIM SİNYALİ", 8)
            if coin == "BTC" and re.search(r"1 saat (Çok güçlü|Güçlü) ↑ — Giriş", t): ekle("₿ 1s güçlü ↑ (girişli)", 1)
            if coin == "BTC" and "⏰ İyi saat diliminde" in t: ekle("₿ 4s ⏰ iyi saat", 4)
            continue
    return [pd.DataFrame(x) for x in (S, P, B, I)]
if __name__ == "__main__":
    S, P, B, I = ayristir(sys.argv[1:])
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 300)
    print(S.to_string()); print(len(P), "yön", len(B), "bariyer", len(I), "aralık")
    print(P.groupby(["coin", "H", "guc"]).size())
