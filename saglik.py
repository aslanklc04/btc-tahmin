# saglik.py — SİSTEM SAĞLIK TARAMASI (19.10.2026, kullanıcı: "baştan sona tara, hata/bozukluk/tutarsızlık var mı, Neon dahil"). Main kökünden çalışır, hiçbir şey göndermez.
import os, glob, gzip, json, pickle, time, subprocess, py_compile, numpy as np, pandas as pd
import ortak as O
L = []; SORUN = []
def yaz(s=""): print(s, flush=True); L.append(str(s))
def sorun(s): SORUN.append(s); yaz(f"   ❌ {s}")
NOW = pd.Timestamp.now(tz="UTC"); H0 = NOW.floor("h")
def oku(p):
    with gzip.open(p, "rb") as f: return pickle.load(f)
yaz(f"# 🩺 Sistem sağlık taraması — {NOW.tz_convert(O.DISPLAY_TZ):%d.%m.%Y %H:%M}\n")
# 1) kod
yaz("## 1) Kod (Python 3.11 derleme)")
bad = []
for p in sorted(glob.glob("*.py")):
    try: py_compile.compile(p, doraise=True)
    except Exception as e: bad.append(f"{p}: {e}")
yaz(f"- {len(glob.glob('*.py'))} dosya · hata {len(bad)}"); [sorun(b) for b in bad]
# 2) modeller
yaz("\n## 2) Modeller")
M = oku("durum/model.pkl.gz"); yaz(f"- BTC v35: eğitim {M['created']:%d.%m.%Y} ({(NOW - M['created']).days} gün)")
if (NOW - M["created"]).days > 40: sorun("BTC modeli 40 günden eski")
for ad, desen in (("ana coin (durum)", "durum/model_*.pkl.gz"), ("geniş liste (modeller)", "modeller/model_*.pkl.gz"), ("24 s ana (durum)", "durum/model24_*.pkl.gz"), ("24 s geniş (modeller)", "modeller/model24_*.pkl.gz")):
    fs = sorted(glob.glob(desen)); cr = []
    for p in fs:
        try: cr.append(oku(p)["created"])
        except Exception as e: sorun(f"{p} okunamadı: {e}")
    if cr: yaz(f"- {ad}: {len(fs)} model · eğitim {min(cr):%d.%m}–{max(cr):%d.%m} · en eski {(NOW - min(cr)).days} gün")
    if cr and (NOW - min(cr)).days > 40: sorun(f"{ad}: 40 günden eski model var")
GEN = [l.strip() for l in open("durum/genis_liste.txt") if l.strip()]; MOD = {os.path.basename(p)[6:-7] for p in glob.glob("modeller/model_*.pkl.gz")} | {os.path.basename(p)[6:-7] for p in glob.glob("durum/model_*.pkl.gz")}
eks = [s for s in GEN if s not in MOD]; yaz(f"- geniş liste {len(GEN)} coin · modeli olmayan: {len(eks)} {eks[:10]}")
if eks: sorun(f"geniş listede modeli olmayan {len(eks)} coin")
# 3) canlı durum önbellekleri
yaz("\n## 3) Canlı durum (önbellek)")
try:
    GB = pickle.load(open("durum/gecmis.pkl", "rb")); son = {H: GB["PG"][H].index[-1] for H in O.CFG}
    yaz(f"- BTC son tahmin saati: " + " · ".join(f"{H}s {t:%d.%m %H:%M}" for H, t in son.items()) + f" · model aynı mı: {'✅' if GB.get('created') == M['created'] else '❌'}")
    if min(son.values()) < H0 - pd.Timedelta(hours=2): sorun("BTC tahmin geçmişi 2 saatten eski")
except Exception as e: sorun(f"gecmis.pkl: {e}")
try:
    GC = pickle.load(open("durum/gecmis_coin.pkl", "rb")); ks = [k for k in GC if isinstance(GC[k], dict) and "PG" in GC[k]]
    eski = [k[:-4] for k in ks if GC[k]["PG"][4].index[-1] < H0 - pd.Timedelta(hours=3)]
    yaz(f"- coin tahmin geçmişi: {len(ks)} coin · 3 saatten eski: {len(eski)} {eski[:12]}")
    if len(eski) > 5: sorun(f"{len(eski)} coin'in tahmini 3 saatten eski")
except Exception as e: sorun(f"gecmis_coin.pkl: {e}")
# 4) Neon + likidite
yaz("\n## 4) Neon / 💧 likidite")
import requests
try:
    r = requests.get(f"{O.FON_URL.rsplit('/', 1)[0]}/saat", params={"h": (H0 - pd.Timedelta(hours=1)).strftime("%Y%m%d%H")}, timeout=60).json()
    c = r.get("coins", {}); ok = sum(1 for x in c.values() if x.get("n", 0) >= 10); yaz(f"- Neon /saat (son tam saat): {len(c)} coin, ≥10 ölçüm olan {ok}")
    if ok < 100: sorun(f"Neon son saatte yalnız {ok} coin'de yeterli ölçüm")
except Exception as e: sorun(f"Neon /saat: {e}")
LC = [l.strip() for l in open("durum/likidite_coinler.txt") if l.strip() and not l.startswith("#")]
if os.path.exists("durum/derinlik_saat.pkl"):
    D = pd.read_pickle("durum/derinlik_saat.pkl"); son72 = D[D.index > H0 - pd.Timedelta(hours=72)][[c for c in LC if c in D.columns]]
    yaz(f"- derinlik geçmişi: son saat {D.index.max():%d.%m %H:%M} · son 72 saatte dolu oran %{100 * son72.notna().mean().mean():.0f} · hiç verisi olmayan coin {int((son72.notna().sum() == 0).sum())}")
else: sorun("derinlik_saat.pkl önbellekte yok")
t0 = time.time(); p = subprocess.run(["python", "likidite.py"], capture_output=True, text=True, timeout=600); yaz(f"- likidite.py: çıkış {p.returncode} · {time.time() - t0:.0f} sn · {p.stdout.strip().splitlines()[-1][:200] if p.stdout.strip() else p.stderr[-300:]}")
if p.returncode != 0: sorun("likidite.py hata verdi")
try:
    J = json.load(open("durum/likidite_z.json")); zt = pd.Timestamp(J["t"]); zz = {k: v for k, v in J["z"].items() if v is not None}
    yaz(f"- likidite_z: saat {zt:%d.%m %H:%M} ({(NOW - zt).total_seconds() / 3600:.1f} saat önce) · z hesaplanan {len(zz)}/{len(LC)} · 💧 (z ≤ −2) şu an: {', '.join(k for k, v in zz.items() if v <= -2) or 'yok'}")
    if (NOW - zt) > pd.Timedelta(hours=3): sorun("likidite_z 3 saatten eski → 💧 hiç çıkmaz")
    if len(zz) < 0.9 * len(LC): sorun(f"likidite z yalnız {len(zz)}/{len(LC)} coin'de")
    O._LDZ = None; yaz(f"- ortak.ld_z okuyor mu: ETH {O.ld_z('ETH'):+.2f} · SOL {O.ld_z('SOL'):+.2f} · LDO {O.ld_z('LDO'):+.2f}")
except Exception as e: sorun(f"likidite_z.json: {e}")
fz = {c: O.fon_coin_z(c) for c in O.FON_COINS}; yaz(f"- 💸 coin fonlaması (Neon /fonlama): {sum(np.isfinite(v) for v in fz.values())}/{len(fz)} coin · z ≥ 2: {[k for k, v in fz.items() if np.isfinite(v) and v >= 2] or 'yok'}")
if sum(np.isfinite(v) for v in fz.values()) < 20: sorun("Neon fonlama verisi eksik")
# 5) dış kaynaklar
yaz("\n## 5) Dış veri kaynakları")
for nm in ("BTC", "ETH", "LDO"):
    d = O.cb_prim(nm, path=f"/tmp/sg_{nm}.json"); yaz(f"- Coinbase primi {nm}: " + (f"z {d['z']:+.2f} · saat {pd.Timestamp(d['t']):%H:%M}" if d else "❌ alınamadı"))
    if not d: sorun(f"Coinbase primi {nm} alınamadı")
os.environ.pop("TG_SIRALI", None); import gonder; fzz = gonder.fon_z(); yaz(f"- 🔥 KuCoin BTC fonlaması z: {fzz:+.2f}" if np.isfinite(fzz) else "- 🔥 KuCoin: ❌ alınamadı")
if not np.isfinite(fzz): sorun("KuCoin fonlaması alınamadı")
o = O.fetch_1h((NOW - pd.Timedelta(hours=5)).timestamp() * 1000, NOW.timestamp() * 1000); yaz(f"- Binance BTC son mum {o.index[-1]:%d.%m %H:%M}")
# 6) karne / kayıt
yaz("\n## 6) Karne ve kayıt")
K = pd.read_csv("durum/karne_kayit.csv"); yaz(f"- karne kaydı: {len(K)} satır · son {K.t.iloc[-1]} · ilk satırı karne.md: {open('durum/karne.md').readline().strip()}")
yaz(f"- likidite listesi {len(LC)} coin · sembol tablosunda olmayan: {[c for c in LC if c not in set(pd.read_csv('durum/likidite_semboller.csv').coin)]}")
yaz(f"\n## Sonuç: {'✅ sorun bulunmadı' if not SORUN else '❌ ' + str(len(SORUN)) + ' sorun: ' + ' · '.join(SORUN)}")
open("saglik_sonuc.md", "w").write("\n".join(L) + "\n")
