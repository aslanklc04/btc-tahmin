# genis_aile.py — GENİŞ TARAMA, AİLE DÜZEYİNDE (yalnız test). genis_analiz.py'de coin coin seçim işe yaramadı (seçim neti ile sonraki net ters ilişkili).
# Soru: coin seçmeden, TÜM yeni coin'lerde hangi sinyal ailesi (🤝 BTC ile ortak · 🔇 BTC sessizken · 🧪 24 saat) kendi primi ≥ 0 iken kazandırıyor?
# ÖNCEDEN YAZILI KARAR (11.10.2026, aile × dönem tablosunu görmeden): aile, kohort A yeni coin'lerin 2022-06→2023 toplamında isabet ≥ %55, net ≥ +%0,20, haftalık blok alt sınır > 0 ise SEÇİLİR;
#   seçilen aile 2024+'da (tüm yeni coin'ler) isabet ≥ %55, net > 0, alt sınır > 0 ve 2026'da net ≥ 0 ise ✅ canlıya aday. Ayrıca aynı saatteki sinyaller tek olay sayılınca isabet ve haftalık mesaj (saat) sayısı.
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
yaz(f"# 👪 Geniş tarama — aile düzeyinde (coin seçmeden) — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nYeni coin: {E[E.yeni].nm.nunique()} (2022–23 verisi olan: {len(KA - CANLI)}) · canlı: {E[~E.yeni].nm.nunique()}\n")
def st(x):
    if len(x) < 8: return f"{len(x)} sinyal"
    e = x.groupby(x.t.dt.floor("h")).net.mean(); hf = max((x.t.max() - x.t.min()).days / 7, 1)
    return (f"{len(x):6d} · %{100*x.ok.mean():.1f} · {100*x.net.mean():+.3f} (alt {100*wboot(x.net.values, x.t.values, 400)[0]:+.2f}) · saat-olayı %{100*(e>0).mean():.1f} · "
            f"mesaj saati/hf {len(e)/hf:.1f}")
DON = (("2022-06→2023", lambda t: (t >= P0) & (t < A24)), ("2024+", lambda t: t >= A24), ("2026", lambda t: t >= A26))
yaz("_sinyal · isabet · işlem başı net % (alt sınır) · aynı saat tek olay isabeti · haftada kaç ayrı saatte mesaj_\n```")
SEC = {}
for aile in ("🤝", "🔇", "🧪"):
    for grup, gm in (("yeni coin'ler", E.yeni & (E.aile == aile)), ("canlı coin'ler", ~E.yeni & (E.aile == aile) & (E.nm != "BTC"))):
        yaz(f"{aile} {grup}")
        for dn, f in DON:
            x = E[gm & f(E.t) & ((E.nm.isin(KA)) if dn == "2022-06→2023" else True)]; yaz(f"   {dn:13s} {st(x)}")
    x = E[E.yeni & (E.aile == aile) & DON[0][1](E.t) & E.nm.isin(KA)]
    SEC[aile] = bool(len(x) >= 30 and x.ok.mean() >= 0.55 and x.net.mean() >= 0.002 and wboot(x.net.values, x.t.values, 400)[0] > 0)
yaz("```\n**Önceden yazılı karar:**")
for aile, s in SEC.items():
    if not s: yaz(f"- {aile}: seçimde geçmedi"); continue
    d = E[E.yeni & (E.aile == aile) & (E.t >= A24)]; y = E[E.yeni & (E.aile == aile) & (E.t >= A26)]
    ok = d.ok.mean() >= 0.55 and d.net.mean() > 0 and wboot(d.net.values, d.t.values, 400)[0] > 0 and (len(y) < 10 or y.net.mean() >= 0)
    yaz(f"- {aile}: seçimde geçti → 2024+ isabet %{100*d.ok.mean():.1f} · net {100*d.net.mean():+.3f} · 2026 net {100*y.net.mean():+.3f} → {'✅ CANLIYA ADAY' if ok else '❌ doğrulamada geçmedi'}")
open("genis_aile_sonuc.md", "w").write("\n".join(L) + "\n")
