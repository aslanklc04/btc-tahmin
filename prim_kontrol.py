# prim_kontrol.py — 💵 PRİM YENİDEN KONTROL (18.10.2026, kullanıcı onayı): Coinbase kapanan saatin mumunu ilk dakikalarda eksik veriyor
# (prim_gecikme.py / prim_tani.py: 282 canlı sinyalin 31'inde prim sonradan değişti, 13'ünde sınıf değişti — hepsi yukarı yönlü hata, kaçırılan yok).
# Saatlik işin SONUNDA, saat başından KONTROL_DK dakika sonra bu saat gönderilen ✅ ana / 🔸 yedek sinyallerin coin primi yeniden okunur;
# sınıfı düşen (ana → yedek / panel, yedek → panel) varsa tek bir "⚠️ DÜZELTME" mesajı gider + durum/iptal_kayit.csv. 🔥 ile yükselenlere dokunulmaz.
import os, re, csv, time, numpy as np, pandas as pd
os.environ.pop("TG_SIRALI", None)                                                             # doğrudan gönder (gonder.py bitti)
from ortak import cb_prim, cb_z, tg_send, DISPLAY_TZ
DK = int(os.environ.get("KONTROL_DK", "15"))
K_F, I_F = "durum/karne_kayit.csv", "durum/iptal_kayit.csv"
GEN = {l.strip()[:-4] for l in open("durum/genis_liste.txt") if l.strip()} if os.path.exists("durum/genis_liste.txt") else set()
PA = pd.read_csv("durum/prim_acik.csv") if os.path.exists("durum/prim_acik.csv") else pd.DataFrame(columns=["coin", "esik", "saat"])
RE_Z = re.compile(r"([A-Z0-9]{2,12}) \(z ([+-]?[\d.]+)")
def coz(e, s):
    sn = "ana" if s.startswith("✅") else "yedek"
    if e.startswith("🤝"): return [(c, float(z), "🌐🤝" if c in GEN else "🤝", sn) for c, z in RE_Z.findall(e.split(":", 1)[-1])]
    if e.startswith("🧪"): return [(c, float(z), "🌐🧪" if c in GEN else "🧪", sn) for c, z in RE_Z.findall(e.split(":", 1)[-1])]
    if "💵 ABD" in e: return [(c, float(z), "💵", sn) for c, z in RE_Z.findall(e.split(":", 1)[-1])]
    g = re.match(r"^(\S+) ([A-Z0-9]{2,12}) .*?prim ✅ z ([+-]?[\d.]+)", e)
    return [(g.group(2), float(g.group(3)), "🔇/🪙", sn)] if g else []
RANK = {"panel": 0, "yedek": 1, "ana": 2}
def sinif(tur, nm, z, sn):                                                                   # canlıdaki kurallarla aynı (tahmin_coin / tahmin24 / prim_canli)
    if not np.isfinite(z): return "panel"
    if tur == "🌐🤝": return "ana" if z >= 2 else ("yedek" if z >= 0 else "panel")
    if tur == "🌐🧪": return "ana" if z >= 1.5 else "panel"
    if tur in ("🤝", "🧪"): return "ana" if z >= 0 else "panel"
    if tur == "💵":
        r = PA[PA.coin == nm]; es = float(r.esik.min()) if len(r) else 2.0; return sn if z >= es else "panel"
    return sn if z > 0 else "panel"                                                          # 🔇 / 🪙 / 🔀: coin primi > 0
def main():
    h = pd.Timestamp(os.environ["PK_SAAT"], tz="UTC") if os.environ.get("PK_SAAT") else pd.Timestamp.now(tz="UTC").floor("h"); hedef = h + pd.Timedelta(minutes=DK)   # PK_SAAT: yalnız kuru test
    if not os.environ.get("PK_SAAT") and pd.Timestamp.now(tz="UTC") > h + pd.Timedelta(minutes=45): print("prim kontrol: saat çok ilerledi, atlandı"); return
    if not os.path.exists(K_F): print("prim kontrol: karne kaydı yok"); return
    K = pd.read_csv(K_F, dtype=str).fillna(""); ht = h.tz_convert(DISPLAY_TZ)
    tt = pd.to_datetime(K.t).dt.tz_localize(DISPLAY_TZ)
    K = K[(tt >= ht) & (tt < ht + pd.Timedelta(hours=1)) & K.s.str.match(r"^(✅|🔸)") & K.k.str.startswith("gönderildi") & ~K.s.str.contains("🔥")]
    S = [x for r in K.itertuples() for x in coz(r.e, r.s)]
    if not S: print("prim kontrol: bu saat primli ana/yedek sinyal yok"); return
    while pd.Timestamp.now(tz="UTC") < hedef: time.sleep(5)
    out = []
    for nm, zm, tur, sn in S:
        p = f"/tmp/cb_kontrol_{nm}.json"
        if os.path.exists(p): os.remove(p)
        d = cb_prim(nm, path=p)
        if d is None: time.sleep(20); d = cb_prim(nm, path=p)
        if d is None: print(f"{nm}: prim okunamadı → dokunulmaz"); continue                    # bağlantı hatası olabilir: emin değilsek iptal yok
        zy = cb_z(d) if d.get("t") == str(h) else float("nan")                                     # Coinbase'te bu saatin mumu yok (eski saat) → testteki gibi primsiz
        yeni = sinif(tur, nm, zy, sn); out.append((nm, tur, sn, zm, zy, yeni)); print(f"{nm} {tur} {sn}: z {zm:+.1f} → {zy:+.2f} → {yeni}")
    dus = [x for x in out if RANK[x[5]] < RANK[x[2]]]
    if not dus: print(f"prim kontrol: {len(out)} sinyal, hepsi geçerli"); return
    ad = {"ana": "✅ ana", "yedek": "🔸 yedek", "panel": "geçersiz"}
    sat = [f"• {nm} ({ad[sn]}, {tur}): prim z {zm:+.1f} → {('z ' + format(zy, '+.1f')) if np.isfinite(zy) else 'bu saat Coinbase işlemi yok'} → "
           + ("❌ GEÇERSİZ" if yeni == "panel" else "🔸 yedek seviyesine düştü") for nm, tur, sn, zm, zy, yeni in dus]
    gonder = (lambda m: print("KURU — gönderilmedi:\n" + m)) if os.environ.get("PK_KURU") else tg_send
    gonder(f"⚠️ DÜZELTME — {ht:%d.%m %H:00} sinyalleri (Coinbase verisi {DK}. dakikada kesinleşti)\n" + "\n".join(sat)
            + "\n👉 ❌ geçersiz olanlarda limit emir dolmadıysa İPTAL et; dolduysa çıkış saatinde sat. 🔸'ya düşenler yedek gibi düşün (küçük pozisyon ya da pas)."
            + f"\nℹ️ Coinbase saatlik veriyi ilk dakikalarda eksik veriyor; az işlem gören coin'lerde prim yanlış okunabiliyor. Bu saatin diğer {len(out) - len(dus)} sinyali geçerli.")
    if os.environ.get("PK_KURU"): return
    yeni_d = not os.path.exists(I_F)
    with open(I_F, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if yeni_d: w.writerow(["t", "coin", "tur", "sinif_mesaj", "sinif_yeni", "z_mesaj", "z_yeni"])
        for nm, tur, sn, zm, zy, yeni in dus: w.writerow([f"{ht:%Y-%m-%d %H:%M}", nm, tur, sn, yeni, zm, round(zy, 2) if np.isfinite(zy) else ""])
if __name__ == "__main__": main()
