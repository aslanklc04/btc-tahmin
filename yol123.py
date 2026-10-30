# yol123.py — PROTOKOL_dortyol YOL 1 (para yönetimi) · YOL 2 (yürütme maliyeti) · YOL 3 (rejim anahtarı)
import io, zipfile, numpy as np, pandas as pd, requests
out = []; yaz = lambda s="": (out.append(s), print(s, flush=True))
k = ["t", "nm", "sinif", "H"]
V = pd.read_csv("veri_seti.csv.gz", usecols=k + ["s", "G", "P", "tur", "rz", "fon", "zB", "b_r24", "gen24", "b_vr"]).drop_duplicates(k)
K = pd.read_csv("karal2_veri.csv.gz", usecols=k + ["D_T0", "B_T0"]).drop_duplicates(k)
for x in (V, K): x["t"] = pd.to_datetime(x.t, utc=True)
M = K.merge(V, on=k).sort_values("t").reset_index(drop=True)
M["ana"] = M.sinif.str.startswith("✅"); M["yedek"] = M.sinif.str.startswith("🔸")
M["elit"] = M.ana & ((M.rz <= -2) | (M.fon >= 2) | (M.tur == "🔀"))
U = lambda s: pd.Timestamp(s, tz="UTC")
DON = {"A 2022-06→2024": (U("2022-06-01"), U("2025-01-01")), "B 2025": (U("2025-01-01"), U("2026-01-01")), "C 2026": (U("2026-01-01"), U("2027-01-01"))}
# ---------------- BTC 200 g trendi (R1)
try:
    S = requests.Session(); P_ = []
    for ay in pd.period_range("2021-09", "2026-09", freq="M").strftime("%Y-%m"):
        r = S.get(f"https://data.binance.vision/data/futures/um/monthly/klines/BTCUSDT/1d/BTCUSDT-1d-{ay}.zip", timeout=60)
        if r.status_code == 200:
            z = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=[0, 4]); P_.append(d[pd.to_numeric(d[0], errors="coerce").notna()].astype(float))
    for g in pd.date_range("2026-10-01", "2026-10-25").strftime("%Y-%m-%d"):
        r = S.get(f"https://data.binance.vision/data/futures/um/daily/klines/BTCUSDT/1d/BTCUSDT-1d-{g}.zip", timeout=60)
        if r.status_code == 200:
            z = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=[0, 4]); P_.append(d[pd.to_numeric(d[0], errors="coerce").notna()].astype(float))
    B = pd.concat(P_); B[0] = B[0].where(B[0] < 1e14, B[0] / 1000); B["g"] = pd.to_datetime(B[0], unit="ms", utc=True)
    B = B.drop_duplicates("g").set_index("g")[4].sort_index(); ust = (B > B.rolling(200, min_periods=200).mean()).shift(1, freq="D")
    M["R1"] = M.t.dt.floor("D").map(ust).astype("boolean").fillna(False).astype(bool); R1_OK = True
except Exception as e:
    print("BTC günlük alınamadı:", e); M["R1"] = False; R1_OK = False
# ---------------- YOL 1: portföy simülasyonu
LEV = 2.0
def sim(x, boy, saat_tavan=0.40, fren=False, net="D_T0", carp=None):
    x = x.dropna(subset=[net]).sort_values("t"); E, tepe, acik, egri = 1000.0, 1000.0, [], []
    for t, g in x.groupby("t", sort=True):
        giris = t + pd.Timedelta(minutes=7)
        kal = []
        for (ct, n_, r_) in acik:
            if ct <= giris: E += n_ * r_
            else: kal.append((ct, n_, r_))
        acik = kal; tepe = max(tepe, E); egri.append((giris, E))
        if E <= 0: break
        w = np.array([boy(r) for r in g.itertuples()], float)
        if carp is not None: w = w * np.array([carp(r) for r in g.itertuples()], float)
        if fren and E < 0.85 * tepe: w = w * 0.5
        if w.sum() > saat_tavan: w = w * saat_tavan / w.sum()
        bos = E - sum(n_ / LEV for _, n_, _ in acik)
        nt = w * E
        if nt.sum() / LEV > bos: nt = nt * max(bos, 0) / (nt.sum() / LEV) if nt.sum() > 0 else nt
        for r, n_ in zip(g.itertuples(), nt):
            if n_ > 0: acik.append((r.t + pd.Timedelta(hours=int(r.H), minutes=10), n_, getattr(r, net)))
    for ct, n_, r_ in sorted(acik): E += n_ * r_; egri.append((ct, E))
    e = pd.Series([v for _, v in egri], index=pd.DatetimeIndex([a for a, _ in egri])).sort_index()
    gun = max((e.index.max() - e.index.min()).days, 1); yil = (e.iloc[-1] / 1000) ** (365 / gun) - 1 if e.iloc[-1] > 0 else -1
    dd = (e / e.cummax() - 1).min(); ay = e.resample("ME").last().ffill(); ar = ay.pct_change().fillna(ay.iloc[0] / 1000 - 1)
    return dict(son=e.iloc[-1], yil=100 * yil, dd=100 * dd, ay_ort=100 * ar.mean(), ay_kar=100 * (ar > 0).mean(), ay_kotu=100 * ar.min(), oran=(100 * yil) / max(-100 * dd, 1e-9))
med_s = M[M.ana].s.median()
STR = {"P0 eşit %10": (lambda r: 0.10 if r.ana else 0, 9.99, False),
       "P1 saat bütçesi %40": (lambda r: 0.10 if r.ana else 0, 0.40, False),
       "P2 ELİT %20 · diğer %5": (lambda r: (0.20 if r.elit else 0.05) if r.ana else 0, 0.40, False),
       "P3 oynaklık ayarlı": (lambda r: 0.10 * float(np.clip(med_s / r.s, 0.5, 2)) if r.ana else 0, 0.40, False),
       "P4 P2 + düşüş freni": (lambda r: (0.20 if r.elit else 0.05) if r.ana else 0, 0.40, True),
       "P5 P2 + yedek %2": (lambda r: ((0.20 if r.elit else 0.05) if r.ana else (0.02 if r.yedek else 0)), 0.40, False)}
X1 = M[M.ana | M.yedek]
yaz("# 💰 YOL 1–3 — PROTOKOL_dortyol.md (gerçekçi, piyasadan giriş D_T0, 2x kaldıraç, 1.000 $ başlangıç)\n")
yaz("## YOL 1 — para yönetimi")
yaz("_hücre: yıllık getiri % · en büyük düşüş % · aylık ort. % · kârlı ay % · en kötü ay % · son bakiye $_\n")
yaz("| strateji | " + " | ".join(DON) + " | TÜMÜ (2022-06 →) | getiri/düşüş |"); yaz("|---|" + "---|" * (len(DON) + 2))
R1s = {}
def hucre(o): return f"{o['yil']:+.0f} · {o['dd']:.0f} · {o['ay_ort']:+.1f} · %{o['ay_kar']:.0f} · {o['ay_kotu']:+.1f} · {o['son']:,.0f}"
for ad, (boy, tav, fr) in STR.items():
    rr = {dn: sim(X1[(X1.t >= a) & (X1.t < b)], boy, tav, fr) for dn, (a, b) in DON.items()}; tum = sim(X1[X1.t >= U("2022-06-01")], boy, tav, fr)
    R1s[ad] = (rr, tum); yaz(f"| {ad} | " + " | ".join(hucre(o) for o in rr.values()) + f" | {hucre(tum)} | {tum['oran']:.2f} |")
uyg = [(v[1]["oran"], a) for a, v in R1s.items() if all(o["yil"] > 0 for o in v[0].values())]
SEC = max(uyg)[1] if uyg else max((v[1]["oran"], a) for a, v in R1s.items())[1]
yaz(f"\n**Seçilen (her dönemde yıllık > 0 olanlar arasında getiri/düşüş en yüksek):** {SEC}" + ("" if uyg else " — ⚠️ hiçbir strateji her dönemde kârlı değil; tüm dönem oranına göre seçildi"))
# ---------------- YOL 2: yürütme maliyeti
yaz("\n## YOL 2 — yürütme maliyeti (✅ ana)")
M["gec"] = M.P / M.G - 1
for dn, (a, b) in DON.items():
    x = M[M.ana & (M.t >= a) & (M.t < b)]; e = x[x.elit]
    yaz(f"- {dn}: 7 dk gecikme kaybı ort. %{100 * x.gec.mean():+.3f} (medyan %{100 * x.gec.median():+.3f}) · ELİT %{100 * e.gec.mean():+.3f} · D_T0 net %{100 * x.D_T0.mean():+.2f} · B_T0 net %{100 * x.B_T0.mean():+.2f} (dolum %{100 * x.B_T0.notna().mean():.0f})")
iyi = {}
for dn, (a, b) in DON.items():
    x = M[M.ana & (M.t >= a) & (M.t < b)]; iyi[dn] = 100 * (x.gec.mean() + 0.00045)
yaz(f"- Tahmini iyileşme (anında giriş + maker ücret %0,02 giriş/çıkış ≈ +%0,045): " + " · ".join(f"{d} {v:+.3f} puan" for d, v in iyi.items()))
k2 = all(v >= 0.10 for v in iyi.values()); yaz(f"\n**Karar YOL 2: {'✅ ≥ +%0,10 her dönemde → otomatik emir botu ÖNERİLİR' if k2 else '❌ iyileşme her dönemde +%0,10 değil → bot önerilmez'}**")
M["D_hizli"] = M.D_T0 + M.gec + 0.00045; X1 = M[M.ana | M.yedek].copy()
boy, tav, fr = STR[SEC]
rr = {dn: sim(X1[(X1.t >= a) & (X1.t < b)], boy, tav, fr, net="D_hizli") for dn, (a, b) in DON.items()}
yaz(f"- bilgi: {SEC} anında + maker ile: " + " | ".join(f"{d} {hucre(o)}" for d, o in rr.items()))
# ---------------- YOL 3: rejim anahtarı
yaz("\n## YOL 3 — piyasa dönemi anahtarı (✅ ana, D_T0)")
REJ = {"R1 BTC > 200 g": lambda m: m.R1, "R2 BTC primi zB ≥ 0": lambda m: m.zB >= 0, "R3 zB ≥ −1": lambda m: m.zB >= -1, "R4 BTC 24 s ≥ −%2": lambda m: m.b_r24 >= -0.02,
       "R5 gen24 ≥ 0,3": lambda m: m.gen24 >= 0.3, "R6 b_vr ≤ 1,5": lambda m: m.b_vr <= 1.5}
if not R1_OK: REJ.pop("R1 BTC > 200 g")
yaz("| rejim | " + " | ".join(DON) + " | karar |"); yaz("|---|" + "---|" * (len(DON) + 1))
ana = M[M.ana]; tab = {dn: ana[(ana.t >= a) & (ana.t < b)].D_T0 for dn, (a, b) in DON.items()}
yaz("| taban (tüm ana) | " + " | ".join(f"{len(v)} · %{100 * (v > 0).mean():.1f} · {100 * v.mean():+.2f}" for v in tab.values()) + " | — |")
gec3 = []
for ad, fn in REJ.items():
    hs, ok = [], True
    for dn, (a, b) in DON.items():
        x = ana[(ana.t >= a) & (ana.t < b)]; on = x[fn(x).fillna(False).astype(bool)].D_T0; t_ = tab[dn]
        ok = ok and len(on) >= 0.4 * len(t_) and 100 * on.mean() >= 100 * t_.mean() + 0.10 and 100 * (on > 0).mean() >= 100 * (t_ > 0).mean() + 2
        hs.append(f"{len(on)} ({100 * len(on) / max(len(t_), 1):.0f}%) · %{100 * (on > 0).mean():.1f} · {100 * on.mean():+.2f}")
    if ok: gec3.append((100 * ana[(ana.t >= DON['A 2022-06→2024'][0]) & (ana.t < DON['A 2022-06→2024'][1]) & fn(ana).fillna(False).astype(bool)].D_T0.mean(), ad))
    yaz(f"| {ad} | " + " | ".join(hs) + f" | {'✅' if ok else '❌'} |")
if gec3:
    ad = max(gec3)[1]; fn = REJ[ad]; yaz(f"\n**Rejim filtresi geçti: {ad}** → {SEC} + rejim kapalıyken pay ×0,25:")
    X1["rej"] = fn(X1).fillna(False).astype(bool).values
    rr2 = {dn: sim(X1[(X1.t >= a) & (X1.t < b)], boy, tav, fr, carp=lambda r: 1.0 if r.rej else 0.25) for dn, (a, b) in DON.items()}
    iy = all(rr2[d]["oran"] > R1s[SEC][0][d]["oran"] for d in DON)
    yaz("- " + " | ".join(f"{d} {hucre(o)} (oran {o['oran']:.2f} ← {R1s[SEC][0][d]['oran']:.2f})" for d, o in rr2.items()))
    yaz(f"\n**Karar YOL 3: {'✅ üç dönemde de getiri/düşüş iyileşti' if iy else '❌ portföyde üç dönemde birden iyileşmedi'}**")
else: yaz("\n**Karar YOL 3: ❌ hiçbir rejim filtresi üç dönemde de şartı sağlamadı**")
open("yol123_sonuc.md", "w").write("\n".join(out) + "\n")
