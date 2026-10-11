# genis_esik.py — KULLANICI ŞARTI: "isabeti VE kârı yükselten coin'leri ekle, düşürenleri ekleme". Coin coin seçim geçmişte işe yaramadığı için (genis_analiz: seçim ↔ sonraki ters ilişki)
# coin'i değil KURALI seçiyoruz: geniş listenin 🤝 / 🧪 sinyallerinde coin'in kendi Coinbase primi eşiği yükseltilince ve/veya likidite dilimiyle
# isabet ve işlem başı kâr, canlıdaki ✅ ana setin (secim2 R5) ortalamasını üç dönemde de GEÇİYOR mu?
# ÖNCEDEN YAZILI KARAR (11.10.2026): ana set ortalaması — 2022-06→2023 %55,9 · +0,433 | 2024+ %58,6 · +0,647 | 2026 %59,1 · +0,589.
#   Bir (aile × eşik × dilim) seçeneği ancak ÜÇ dönemde de isabet ≥ ana set VE net ≥ ana set ise (2022–23: yalnız 2022-06 öncesi listelenmiş coin'ler, ≥ 30 sinyal; 2024+ ≥ 30; 2026 ≥ 10) eklenir.
#   Birden çok seçenek geçerse 2022–23'te sinyal sayısı en fazla olan (en geniş) seçilir. Hiçbiri geçmezse geniş liste EKLENMEZ.
import glob, os, numpy as np, pandas as pd
from ortak import events, wboot, DISPLAY_TZ
L = []
def yaz(s=""): print(s, flush=True); L.append(s)
def bul(p):
    x = glob.glob(p, recursive=True); return x[0] if x else None
SY = sorted({os.path.basename(p)[5:-4] for p in glob.glob("ga/**/disa_*USDT.pkl", recursive=True)})
CANLI = set()
for f in ("canli/durum/coin_listesi.txt", "canli/durum/deneme24_liste.txt"):
    if os.path.exists(f): CANLI |= {l.strip().replace("USDT", "") for l in open(f) if l.strip()}
EVR = pd.read_csv(bul("**/genis_evren.csv") or "genis_evren.csv") if (bul("**/genis_evren.csv") or os.path.exists("genis_evren.csv")) else None
B = pd.read_pickle(bul("ga/**/disa_BTCUSDT.pkl")); B.index = pd.DatetimeIndex(B.index).tz_convert("UTC")
KOM = 0.0004; P0, A24, A25, A26 = (pd.Timestamp(x, tz="UTC") for x in ("2022-06-01", "2024-01-01", "2025-01-01", "2026-01-01"))
EV, yok = [], []
for sym in SY:
    nm = sym[:-4]
    pz, d24 = bul(f"ga/**/prim_{sym}.pkl"), bul(f"ga/**/disa24_{sym}.pkl")
    if pz is None: yok.append(f"{nm} (prim yok)"); continue
    Z = pd.read_pickle(pz).astype("float64"); Z.index = pd.DatetimeIndex(Z.index).tz_convert("UTC")
    X = pd.read_pickle(bul(f"ga/**/disa_{sym}.pkl")); X.index = pd.DatetimeIndex(X.index).tz_convert("UTC")
    if nm != "BTC":
        Bx = B.reindex(X.index); bu4 = Bx.u4.fillna(False).astype(bool).values; bany = (Bx.star.fillna(False).astype(bool) | Bx.u4.fillna(False).astype(bool) | Bx.acls.fillna(False).astype(bool)).values
        any_ = (X.star.fillna(False).astype(bool) | X.u4.fillna(False).astype(bool) | X.acls.fillna(False).astype(bool)).values & X.y4.notna().values
        for aile, kos in (("🤝", bu4), ("🔇", ~bany)):
            ev = events(any_ & kos, 4); t = X.index[ev]
            EV.append(pd.DataFrame({"nm": nm, "aile": aile, "t": t, "r": np.exp(X.y4.values[ev]) - 1, "z": Z.z.reindex(t).values}))
    if d24:
        D = pd.read_pickle(d24).astype("float64"); D.index = pd.DatetimeIndex(D.index).tz_convert("UTC")
        D = D.reindex(pd.date_range(D.index[0], D.index[-1], freq="1h", tz="UTC")); c = D.close.ffill(limit=3).values; n = len(D)
        m = np.nan_to_num(((D.S24 > 0) & (D.C24 >= D.T10_24)).values).astype(bool) & D.T10_24.notna().values & (np.arange(n) + 25 < n)
        ev = events(m, 24); t = D.index[ev]
        EV.append(pd.DataFrame({"nm": nm, "aile": "🧪", "t": t, "r": c[ev + 24] / c[ev] - 1, "z": Z.z.reindex(t).values}))
E = pd.concat(EV, ignore_index=True); E = E[np.isfinite(E.r) & np.isfinite(E.z) & (E.z >= 0)].copy(); E["net"] = E.r - KOM; E["ok"] = E.net > 0
E["yeni"] = ~E.nm.isin(CANLI | {"BTC"}); KA = {nm for nm, g in E.groupby("nm") if ((g.t >= P0) & (g.t < A24)).sum() >= 15}
HAC = {}
if EVR is not None: HAC = dict(zip(EVR.nm, EVR.hacim))
sira = sorted([nm for nm in E[E.yeni].nm.unique()], key=lambda x: -HAC.get(x, 0)); UST = set(sira[:40])
ZE = {}                                                                                            # olay saatindeki kendi primi (E.z zaten ≥ 0 süzülmüş; eşikler bunun üstünde)
BEN = {"2022-06→2023": (55.9, 0.433), "2024+": (58.6, 0.647), "2026": (59.1, 0.589)}
DON = (("2022-06→2023", lambda t: (t >= P0) & (t < A24)), ("2024+", lambda t: t >= A24), ("2026", lambda t: t >= A26))
yaz(f"# 🎯 Geniş liste: isabeti VE kârı yükselten kural var mı? — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nYeni coin: {E[E.yeni].nm.nunique()} · hacimce ilk 40: {', '.join(sira[:40])}\n"
    "_hücre: sinyal · isabet · işlem başı net % · aynı saat tek olay isabeti · haftada mesaj saati — ✅ = ana setten iyi (isabet ve net)_\n```")
GEC = []
for aile in ("🤝", "🧪"):
    for esik in (0, 0.5, 1, 1.5, 2):
        for dilim, dm in (("tüm yeni coin'ler", E.yeni), ("hacimce ilk 40", E.yeni & E.nm.isin(UST))):
            m0 = dm & (E.aile == aile) & (E.z >= esik); parca, ok = [], True; n22 = 0
            for dn, f_ in DON:
                x = E[m0 & f_(E.t) & ((E.nm.isin(KA)) if dn == "2022-06→2023" else True)]
                if len(x) < (10 if dn == "2026" else 30): parca.append(f"{dn}: {len(x)} sinyal (az)"); ok = False; continue
                e = x.groupby(x.t.dt.floor("h")).net.mean(); hf = max((x.t.max() - x.t.min()).days / 7, 1); h, nn = 100 * x.ok.mean(), 100 * x.net.mean()
                iy = h >= BEN[dn][0] and nn >= BEN[dn][1]; ok &= iy
                if dn == "2022-06→2023": n22 = len(x)
                parca.append(f"{dn}: {len(x):5d} · %{h:.1f} · {nn:+.3f} · saat %{100*(e>0).mean():.0f} · {len(e)/hf:.1f}/hf {'✅' if iy else '·'}")
            yaz(f"{aile} kendi primi z ≥ {esik:<3} · {dilim:17s} {'★ GEÇTİ' if ok else ''}\n   " + "\n   ".join(parca))
            if ok: GEC.append((n22, aile, esik, dilim))
yaz("```")
if GEC:
    yaz("\n**Önceden yazılı karar:** geçen seçenekler: " + " · ".join(f"{a} z≥{e} {d}" for _, a, e, d in GEC))
    for aile in ("🤝", "🧪"):
        g = sorted([x for x in GEC if x[1] == aile], reverse=True)
        if g: yaz(f"- {aile}: seçilen → **z ≥ {g[0][2]} · {g[0][3]}** (2022–23'te {g[0][0]} sinyal)")
        else: yaz(f"- {aile}: hiçbir seçenek ana seti geçemedi → eklenmez")
else: yaz("\n**Önceden yazılı karar:** hiçbir seçenek isabet VE kârda ana seti üç dönemde birden geçemedi → geniş liste eklenmez")
open("genis_esik_sonuc.md", "w").write("\n".join(L) + "\n")
