# genis_hepsi.py — "BÜTÜN SİNYALLER TÜM COİNLER İÇİN" (kullanıcı isteği 12.10.2026): ilk 24 coin'de geçen ek kuralları 🌐 geniş listede (~126 coin) dener (yalnız test).
# Geniş liste canlı kuralı: 🌐🤝 (BTC 4s çok güçlü ↑ + kendi primi z ≥ 2) ve 🌐🧪 (kendi primi z ≥ 1,5) → ✅ ana; geri kalan geniş sinyaller gönderilmez.
# Koşullar: 💸 coin'in kendi Binance fonlaması z ≥ 2 (son 90 ödeme) · 📉🔥 son 24 s z ≤ −2 · 🚀 son 24 s z ≥ 2.
# ÖNCEDEN YAZILI KARAR (sonuçlar görülmeden; teknik_tara.py ile aynı ölçütler, dönemler 2022-06→2023 · 2024+ · 2026, en az 30 / 30 / 10):
#   ANA+ (💸, 📉🔥): koşullu geniş ✅ ana sinyaller üç dönemde ana ortalamasından isabette ≥ +2 puan VE nette ≥ +0,10 → geniş listede de öne alınır.
#   GÖN+ (🚀, 💸): koşullu GÖNDERİLMEYEN geniş sinyaller üç dönemde ana set ölçütünü geçerse (isabet ≥ %55,9 · %58,6 · %59,1 VE net ≥ +0,30 · +0,647 · +0,589) → ✅ ana.
#   PLASEBO: koşullar 30 ve 60 gün kaydırılarak da denenir; gerçek geçen sayısı plasebo ortalamasından ≥ 2 fazla olmalı YA DA plaseboda hiçbir kural geçmemeli; plaseboda da geçen kural eklenmez.
import glob, io, time, zipfile, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import events, DISPLAY_TZ
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
bul = lambda p: (glob.glob(p, recursive=True) or [None])[0]
def utc(ix): ix = pd.DatetimeIndex(ix); return (ix.tz_localize("UTC") if ix.tz is None else ix.tz_convert("UTC")).as_unit("ns")
GEN = sorted({l.strip()[:-4] for l in open("canli/durum/genis_liste.txt") if l.strip()})
B = pd.read_pickle(bul("ga/**/disa_BTCUSDT.pkl")); B.index = utc(B.index); KOM = 0.0004; EV = []; PRS = {}
for nm in GEN:
    p = bul(f"ga/**/prim_{nm}USDT.pkl")
    if not p: continue
    PR = pd.read_pickle(p).astype("float64"); PR.index = utc(PR.index); PR = PR[~PR.index.duplicated()].sort_index(); PRS[nm] = PR; z = PR.z
    p = bul(f"ga/**/disa_{nm}USDT.pkl")
    if p:
        X = pd.read_pickle(p); X.index = utc(X.index); st_, u4_, ac_ = (X[k].fillna(False).astype(bool).values for k in ("star", "u4", "acls"))
        ev = events((st_ | u4_ | ac_) & X.y4.notna().values, 4); t = X.index[ev]; bu4 = B.u4.reindex(t).fillna(False).astype(bool).values; zz = z.reindex(t).values
        EV.append(pd.DataFrame({"nm": nm, "aile": np.where(bu4, "🌐🤝", "🌐 tek/🔇"), "ana": bu4 & (zz >= 2), "t": t, "net": np.exp(X.y4.values[ev]) - 1 - KOM}))
    p = bul(f"ga/**/disa24_{nm}USDT.pkl")
    if p:
        D = pd.read_pickle(p).astype("float64"); D.index = utc(D.index); D = D.reindex(pd.date_range(D.index[0], D.index[-1], freq="1h")); c = D.close.ffill(limit=3).values; n = len(D)
        mk = np.nan_to_num(((D.S24 > 0) & (D.C24 >= D.T10_24)).values).astype(bool) & D.T10_24.notna().values & (np.arange(n) + 25 < n)
        ev = events(mk, 24); t = D.index[ev]; zz = z.reindex(t).values
        EV.append(pd.DataFrame({"nm": nm, "aile": "🌐🧪", "ana": zz >= 1.5, "t": t, "net": c[ev + 24] / c[ev] - 1 - KOM}))
E = pd.concat(EV, ignore_index=True); E["t"] = utc(E.t); E = E[np.isfinite(E.net)].reset_index(drop=True); E["ok"] = E.net > 0
# ---- fonlama (Binance arşivi, aylık) ----
S = requests.Session(); AYLAR = [d.strftime("%Y-%m") for d in pd.date_range("2022-03-01", "2026-09-01", freq="MS")]
def zcsv(url):
    for k in range(4):
        try:
            r = S.get(url, timeout=30)
            if r.status_code == 404: return None
            if r.status_code == 200: z_ = zipfile.ZipFile(io.BytesIO(r.content)); return pd.read_csv(z_.open(z_.namelist()[0]), header=None, dtype=str)
        except Exception: time.sleep(1 + k)
    return None
def fon(nm):
    for sym in (nm + "USDT", "1000" + nm + "USDT"):
        fr = [x for x in (zcsv(f"https://data.binance.vision/data/futures/um/monthly/fundingRate/{sym}/{sym}-fundingRate-{ym}.zip") for ym in AYLAR) if x is not None]
        if not fr: continue
        f_ = pd.concat(fr); f_ = f_[pd.to_numeric(f_[0], errors="coerce").notna()]; ft = f_[0].astype(float).values; ft = np.where(ft > 1e14, ft / 1000, ft)
        s = pd.Series(f_.iloc[:, -1].astype(float).values, index=pd.DatetimeIndex(pd.to_datetime(ft, unit="ms", utc=True)).round("min").as_unit("ns")); s = s[~s.index.duplicated()].sort_index()
        return nm, (s - s.rolling(90, min_periods=30).mean()) / (s.rolling(90, min_periods=30).std() + 1e-12)
    return nm, None
with ThreadPoolExecutor(12) as ex: FON = {k: v for k, v in ex.map(fon, sorted(set(E.nm))) if v is not None}
yaz(f"# 🌐 Geniş listede ek kurallar (💸 · 📉🔥 · 🚀) — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n"
    f"Coin: {E.nm.nunique()} · fonlama arşivi olan: {len(FON)} · sinyal: ✅ ana {int(E.ana.sum()):,} · gönderilmeyen {int((~E.ana).sum()):,} · {time.time()-T0:.0f} sn\n")
tz_, nmv = pd.DatetimeIndex(E.t), E.nm.values; ANA = E.ana.values.astype(bool); GON = ~ANA
P0, A24, A26 = (pd.Timestamp(x, tz="UTC") for x in ("2022-06-01", "2024-01-01", "2026-01-01")); SONT = tz_.max()
DN = (("2022-06→2023", (tz_ >= P0) & (tz_ < A24), (A24 - P0).days / 7), ("2024+", tz_ >= A24, (SONT - A24).days / 7), ("2026", tz_ >= A26, (SONT - A26).days / 7))
BEN = {"2022-06→2023": (55.9, 0.30), "2024+": (58.6, 0.647), "2026": (59.1, 0.589)}; MIN = {"2022-06→2023": 30, "2024+": 30, "2026": 10}
def kosullar(kay):
    tt = tz_ - pd.Timedelta(hours=kay); rz = np.full(len(E), np.nan); fz = np.full(len(E), np.nan)
    for nm in set(nmv):
        m = nmv == nm; c = PRS[nm].c; lr = np.log(c); sg = lr.diff().rolling(720, min_periods=168).std()
        rz[m] = ((lr - lr.shift(24)) / (sg * np.sqrt(24))).reindex(tt[m]).values
        if nm in FON:
            fs = FON[nm].dropna(); i = fs.index.searchsorted(tt[m], side="right") - 1; fz[m] = np.where(i >= 0, fs.values[np.clip(i, 0, None)], np.nan)
    return {"💸 coin fonlaması z ≥ 2": fz >= 2, "📉🔥 son 24 s z ≤ −2 (dip)": rz <= -2, "🚀 son 24 s z ≥ 2 (momentum)": rz >= 2}
OK, NET = E.ok.values, E.net.values
def ist(m): return {dn: (int((m & md).sum()), 100 * OK[m & md].mean() if (m & md).any() else np.nan, 100 * NET[m & md].mean() if (m & md).any() else np.nan) for dn, md, _ in DN}
def yazi(o): return " | ".join(f"{o[dn][0]/hf:5.1f}/hf · %{o[dn][1]:4.1f} · {o[dn][2]:+.2f} ({o[dn][0]})" if o[dn][0] >= 5 else f"{o[dn][0]:5d} az" for dn, _, hf in DN)
def yeter(o): return all(o[dn][0] >= MIN[dn] for dn in MIN)
OANA = ist(ANA)
def kurallar(K):
    gec = []
    for ad, c in K.items():
        oa, og = ist(ANA & c), ist(GON & c)
        if not ad.startswith("🚀") and yeter(oa) and all(oa[dn][1] >= OANA[dn][1] + 2 and oa[dn][2] >= OANA[dn][2] + 0.10 for dn in MIN): gec.append(("ANA+", ad))
        if not ad.startswith("📉") and yeter(og) and all(og[dn][1] >= BEN[dn][0] and og[dn][2] >= BEN[dn][1] for dn in MIN): gec.append(("GÖN+", ad))
    return gec
K0 = kosullar(0)
yaz("_haftada · isabet · işlem başı net % (sinyal) — 2022-06→2023 | 2024+ | 2026_\n```")
yaz(f"{'🌐 ✅ ANA (hepsi)':40s}{yazi(OANA)}\n{'🌐 GÖNDERİLMEYEN (hepsi)':40s}{yazi(ist(GON))}")
for ad, c in K0.items(): yaz(f"\n{ad}\n  {'✅ ana + koşul':38s}{yazi(ist(ANA & c))}\n  {'gönderilmeyen + koşul':38s}{yazi(ist(GON & c))}")
yaz("```")
G0 = kurallar(K0); GP1, GP2 = kurallar(kosullar(720)), kurallar(kosullar(1440)); PS = set(GP1) | set(GP2)
GENEL = len(G0) >= (len(GP1) + len(GP2)) / 2 + 2 or (len(G0) >= 1 and not PS)
KAB = [(g, a) for g, a in G0 if (g, a) not in PS] if GENEL else []
yaz(f"\n**Gerçek veride geçen:** {len(G0)} ({', '.join(f'{g} {a}' for g, a in G0) or '—'}) · **plasebo:** 30 gün {len(GP1)}, 60 gün {len(GP2)}")
yaz("\n## Önceden yazılı karar\n" + ("\n".join(f"- ✅ KABUL {g}: **{a}** → geniş listede de canlıya" for g, a in KAB) if KAB else "- Geniş listede eklenecek kural yok"))
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("genis_hepsi_sonuc.md", "w").write("\n".join(L) + "\n")
