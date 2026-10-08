# kisisel.py — COİN'E ÖZEL PRİM EŞİĞİ ("coin'e özel tedavi"), YÜRÜYEN TEST (yalnız test; canlıya dokunmaz).
# Her ay başında, YALNIZ o güne kadar sonucu belli olmuş sinyallerle (2022-06'dan beri), her coin için prim eşiği seçilir ve o ayın sinyallerine uygulanır:
#   A) Model sinyalleri (canlıda giden tüm AL türleri, coin'in kendi primi): adaylar z > −1 (ESKİ, bugünkü), z ≥ −0,5 / 0 / 0,5 / 1 / 1,5.
#      Kural (önceden): geçmişte ≥ 30 sinyal kalan ve isabeti ESKİ'den ≥ 3 puan yüksek eşikler içinden işlem başı neti en yüksek olan; yoksa ESKİ devam.
#   B) Tek başına 💵 (canlıdaki 15 coin): adaylar z ≥ 2 / 2,5 / 3 / 4 / 5 × 8 / 24 saat. Kural: geçmişte ≥ 10 işlem ve net > 0 olanlardan neti en yüksek; yoksa o ay sinyal yok.
# Karşılaştırma (2024+ ve 2026, hepsi dönem dışı): ESKİ herkese · COİN'E ÖZEL · TEK EŞİK herkese (aynı kural, tüm coin'ler tek havuz).
# ÖNCEDEN KARAR (A): COİN'E ÖZEL canlıya aday ancak — 2024+ isabet ESKİ'den ≥ 2 puan yüksek ve işlem başı net daha yüksek · 2026 isabeti ESKİ'den düşük değil ·
#   atılan sinyallerin isabeti tutulanlardan düşük (haftalık blok %5 alt sınır > 0) · TEK EŞİK'ten kötü değil (isabet ve net).
import os, glob, gzip, json, pickle, time, numpy as np, pandas as pd
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
f = lambda p: glob.glob(p, recursive=True)
RAW = {k: v.astype("float64") for k, v in pd.read_pickle(f("art3/**/prim_veri.pkl")[0]).items()}; RAW = {k: v for k, v in RAW.items() if len(v) >= 3000}
for k, v in RAW.items(): v.index = pd.DatetimeIndex(v.index).tz_convert("UTC").as_unit("ns")
# ---------------- olaylar (prim_pencere.py ile aynı) ----------------
EX = {os.path.basename(p)[5:-4]: pd.read_pickle(p) for p in f("art1/**/disa_*USDT.pkl")}
E24 = {os.path.basename(p)[7:-4]: pd.read_pickle(p) for p in f("art2/**/disa24_*USDT.pkl")}
SFB = pd.read_pickle("sf_BTCUSDT.pkl").astype("float64")
CD = "canli/durum"; CANLI = [l.strip() for l in open(f"{CD}/coin_listesi.txt") if l.strip()]
JOINT, TEKL = pd.read_csv(f"{CD}/ortak_acik.csv"), pd.read_csv(f"{CD}/tek_acik.csv")
SIGON = {}
for s in CANLI:
    with gzip.open(f"{CD}/model_{s}.pkl.gz", "rb") as g: SIGON[s] = {k: bool(v["on"]) for k, v in pickle.load(g)["SIG"].items()}
with gzip.open(f"{CD}/model.pkl.gz", "rb") as g: MB = pickle.load(g)
LMT = 0.0002; P0, A24, A26 = pd.Timestamp("2022-06-01", tz="UTC"), pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")
DON = (("22-06→23", lambda i: (i >= P0) & (i < A24)), ("2024+", lambda i: i >= A24), ("2026", lambda i: i >= A26))
EV = []
def kaydet(aile, ad, t, r, H, nm, canli):
    for ti, ri in zip(pd.DatetimeIndex(t), np.asarray(r, float)):
        if np.isfinite(ri): EV.append((aile, ad, canli, H, ti, ri, nm))
X = SFB
for H in (1, 4, 8):
    S, C, T10, T30, y = X[f"S{H}"], X[f"C{H}"], X[f"T10{H}"], X[f"T30{H}"], X[f"y{H}"]
    for sg in (1, -1):
        for li, lad in ((2, "Çok güçlü"), (1, "Güçlü")):
            lvl = np.where(C >= T10, 2, np.where(C >= T30, 1, 0)); m = ((np.sign(S) == sg) & (lvl == li) & T10.notna() & y.notna()).values
            ev = events(m, H); st = MB["R"][H]["STATS"][(li, sg)]; act, _ = action(H, sg, li, st)
            if sg > 0: kaydet("BTC 1/4/8 s + ⭐ + A", f"BTC {H}s {lad} ↑", X.index[ev], np.exp(y.values[ev]) - 1, H, "BTC", "📨" if act[:1] in ("✅", "🟢") else "")
star = ((X.S4 > 0) & (X.C4 >= X.T104) & (X.S8 > 0) & (X.C8 >= X.T108) & X.y8.notna()).values; ev = events(star, 8)
kaydet("BTC 1/4/8 s + ⭐ + A", "BTC ⭐", X.index[ev], np.exp(X.y8.values[ev]) - 1, 8, "BTC", "📨")
ac = ((X.am >= 0.85) & X.y4.notna()).values; ev = events(ac, 4); kaydet("BTC 1/4/8 s + ⭐ + A", "BTC A", X.index[ev], np.exp(X.y4.values[ev]) - 1, 4, "BTC", "📨")
B = EX["BTCUSDT"]; AD = {"star": ("⭐", 8, "y8"), "u4": ("4s ÇG↑", 4, "y4"), "acls": ("A", 4, "y4")}
for s in CANLI:
    nm = s[:-4]; Xc = EX.get(s)
    if Xc is None: continue
    Bx = B.reindex(Xc.index); bu4 = Bx.u4.fillna(False).values.astype(bool); bany = (Bx.star.fillna(False) | Bx.u4.fillna(False) | Bx.acls.fillna(False)).values.astype(bool)
    jo, te = set(JOINT[JOINT.sym == s].sinyal), set(TEKL[TEKL.sym == s].sinyal)
    for k, (ad, H0, yc0) in AD.items():
        for aile, kos, acik in (("coin tek başına", np.ones(len(Xc), bool), SIGON[s].get(k, False)), ("coin 🤝 ortak", bu4, k in jo), ("coin 🔇 sessiz", ~bany, k in te)):
            H, yc = (H0, yc0) if aile == "coin tek başına" else (4, "y4")
            m = Xc[k].fillna(False).values.astype(bool) & kos & Xc[yc].notna().values; ev = events(m, H)
            kaydet(aile, f"{nm} {aile} {ad}", Xc.index[ev], np.exp(Xc[yc].values[ev]) - 1, H, nm, "📨" if acik else "")
for s, Xd in E24.items():
    nm = s.replace("USDT", ""); Xd = Xd.reindex(pd.date_range(Xd.index[0], Xd.index[-1], freq="1h", tz="UTC")); c = Xd.close.ffill(limit=3).values; n = len(Xd)
    m = np.nan_to_num(((Xd.S24 > 0) & (Xd.C24 >= Xd.T10_24)).values).astype(bool) & Xd.T10_24.notna().values & (np.arange(n) + 25 < n); ev = events(m, 24)
    kaydet("🧪 24 saat", f"{nm} 24s", Xd.index[ev], c[ev + 24] / c[ev] - 1, 24, nm, "📨")
def gun_isle(aile, ad, gunler, nm, saat, HD, yon):
    D = RAW[nm]; t1 = pd.DatetimeIndex(gunler) + pd.Timedelta(days=1, hours=saat); t2 = t1 + pd.Timedelta(days=HD)
    r = yon * (D.c.reindex(t2).values / D.c.reindex(t1).values - 1); kaydet(aile, ad, t1, r, HD * 24, nm, "📨")
try:
    import zincir_canli as ZC
    Zs = ZC.olcu(ZC.cm("eth", gun=1700), ZC.stabil())
    for ad, acik, yon, gun, kos, _ in ZC.KURAL:
        if yon > 0: ev = Zs.index[events(kos(Zs).fillna(False).values, gun)]; gun_isle("⛓️ ETH", f"⛓️ {ad}", ev, "ETH", 6, gun, yon)
except Exception as e: yaz(f"_⛓️ atlandı: {type(e).__name__} {str(e)[:120]}_")
try:
    j = json.load(open("veri_bgeo/coins-addr-1-BTC.json")); d = pd.DataFrame(j); d.index = pd.to_datetime(d.pop("d"), utc=True).dt.floor("D")
    sm = d.drop(columns=[c for c in d.columns if "ts" in c.lower() or "unix" in c.lower()]).apply(pd.to_numeric, errors="coerce").iloc[:, 0].dropna().sort_index()
    sm = sm[~sm.index.duplicated()].asfreq("D"); zk = np.log(sm).diff(30); zk = (zk - zk.rolling(90, min_periods=30).mean()) / (zk.rolling(90, min_periods=30).std() + 1e-12)
    ev = zk.index[events((zk <= -1.5).fillna(False).values, 7)]
    for nm in ("BTC", "ETH"): gun_isle("🧑 küçük yatırımcı", f"🧑 {nm} AL", ev, nm, 12, 7, 1)
except Exception as e: yaz(f"_🧑 atlandı: {type(e).__name__} {str(e)[:120]}_")
E = pd.DataFrame(EV, columns=["aile", "sinyal", "canli", "H", "t", "r", "nm"]); E = E[(E.canli == "📨") & (pd.DatetimeIndex(E.t) >= P0)].reset_index(drop=True)
zc = np.full(len(E), np.nan)
for nm, g in E.groupby("nm"):
    if nm in RAW: zc[g.index.values] = RAW[nm].z.reindex(pd.DatetimeIndex(g.t).tz_convert("UTC").as_unit("ns")).values
E["z"] = zc; E["net"] = E.r - 2 * LMT; E = E[np.isfinite(E.z)].reset_index(drop=True); tt = pd.DatetimeIndex(E.t)
E["ok"] = E.r > 0; E["bitis"] = tt + pd.to_timedelta(E.H.astype(float), unit="h"); E["hafta"] = tt.floor("7D")
SONT = max(D.index[-1] for D in RAW.values()); AYLAR = pd.date_range(A24, SONT, freq="MS")
HAF = {"2024+": (SONT - A24).days / 7, "2026": (SONT - A26).days / 7}; OOS = (("2024+", lambda i: i >= A24), ("2026", lambda i: i >= A26))
ADAY = [-1, -0.5, 0, 0.5, 1, 1.5]; KAD = lambda k: "ESKİ (z > −1)" if k == -1 else f"z ≥ {k:g}"
def tut(z, k): return np.where(np.asarray(k) == -1, z > -1, z >= np.asarray(k))
def sec(G):
    eski = G[tut(G.z.values, -1)]
    if len(eski) < 30: return -1
    he = eski.ok.mean(); best, bnet = -1, None
    for k in ADAY[1:]:
        x = G[tut(G.z.values, k)]
        if len(x) >= 30 and x.ok.mean() >= he + 0.03 and (bnet is None or x.net.mean() > bnet): best, bnet = k, x.net.mean()
    return best
E["k_ozel"] = np.nan; E["k_tek"] = np.nan; SECIM = {}
for m in AYLAR:
    me = m + pd.offsets.MonthBegin(1); gec = E[E.bitis < m]; bu = ((tt >= m) & (tt < me))
    E.loc[bu, "k_tek"] = sec(gec)
    for nm, g in gec.groupby("nm"):
        k = sec(g); SECIM[(m, nm)] = k; E.loc[bu & (E.nm == nm).values, "k_ozel"] = k
    E.loc[bu & E.k_ozel.isna().values, "k_ozel"] = -1
O = E[tt >= A24].copy(); ot = pd.DatetimeIndex(O.t)
O["eski"] = O.z.values > -1; O["ozel"] = tut(O.z.values, O.k_ozel.values); O["tek"] = tut(O.z.values, O.k_tek.values)
def satir(x, hf): return f"%{100*x.ok.mean():.1f} · {100*x.net.mean():+.3f} · {len(x)/hf:.1f}/hafta · toplam {100*x.net.sum()/hf:+.1f}/hafta" if len(x) else "—"
yaz(f"# 🩺 Coin'e özel prim eşiği — yürüyen test (her ay yalnız geçmişle seçim) — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n{len(RAW)} coin · AL sinyali {len(E):,} (2022-06+) · dönem dışı (2024+) {len(O):,}\n")
yaz("## A) Model sinyalleri — dönem dışı sonuç (isabet · işlem başı net % · sinyal sayısı · haftalık toplam %)\n```")
R_ = {}
for ad, col in (("ESKİ herkese (bugün)", "eski"), ("COİN'E ÖZEL", "ozel"), ("TEK EŞİK herkese", "tek")):
    R_[ad] = {}
    for dn, fd in OOS:
        x = O[O[col].values & fd(ot)]; R_[ad][dn] = (100 * x.ok.mean(), 100 * x.net.mean(), len(x)); yaz(f"{ad:22s} {dn:6s} {satir(x, HAF[dn])}")
yaz("```")
# atılan / tutulan (ESKİ'nin aldığı sinyaller içinde)
A_ = O[O.eski.values & (ot >= A24)]; kt, at_ = A_.ozel.values, ~A_.ozel.values
def lb(ok, a, b, h, reps=2000):
    rng = np.random.default_rng(0); d = pd.DataFrame({"ok": ok.astype(float), "a": a, "b": b, "h": h})
    C = pd.DataFrame({"na": d.a.groupby(d.h).sum(), "oa": (d.ok * d.a).groupby(d.h).sum(), "nb": d.b.groupby(d.h).sum(), "ob": (d.ok * d.b).groupby(d.h).sum()}).values.astype(float)
    S_ = C[rng.integers(0, len(C), (reps, len(C)))].sum(axis=1)
    with np.errstate(all="ignore"): fr = 100 * (S_[:, 1] / S_[:, 0] - S_[:, 3] / S_[:, 2])
    fr = fr[np.isfinite(fr)]; return float(np.percentile(fr, 5)) if len(fr) else np.nan
alt = lb(A_.ok.values, kt, at_, A_.hafta.values)
yaz(f"Coin'e özel kuralın ATTIĞI sinyaller (2024+): {int(at_.sum())} · isabet %{100*A_.ok.values[at_].mean():.1f} · net {100*A_.net.values[at_].mean():+.3f}  |  TUTTUĞU: {int(kt.sum())} · isabet %{100*A_.ok.values[kt].mean():.1f} · net {100*A_.net.values[kt].mean():+.3f}  |  fark alt sınır {alt:+.1f} puan")
e, o_, t_ = R_["ESKİ herkese (bugün)"], R_["COİN'E ÖZEL"], R_["TEK EŞİK herkese"]
c1 = o_["2024+"][0] - e["2024+"][0] >= 2 and o_["2024+"][1] > e["2024+"][1]; c2 = o_["2026"][0] >= e["2026"][0]; c3 = alt > 0; c4 = o_["2024+"][0] >= t_["2024+"][0] and o_["2024+"][1] >= t_["2024+"][1]
yaz(f"\n**Önceden yazılı karar (A):** isabet +{o_['2024+'][0]-e['2024+'][0]:.1f} puan ve net {'↑' if o_['2024+'][1] > e['2024+'][1] else '↓'} {'✅' if c1 else '❌'} · 2026 düşmedi {'✅' if c2 else '❌'} · atılanlar daha kötü {'✅' if c3 else '❌'} · tek eşikten kötü değil {'✅' if c4 else '❌'} → {'✅ CANLIYA ADAY' if all((c1, c2, c3, c4)) else '❌ canlıya aday değil'}")
# coin coin
yaz("\n### Coin coin (2024+, dönem dışı) — ESKİ ve COİN'E ÖZEL · bugünkü seçim = tüm geçmişle şu an seçilecek eşik · yeni teknik kullanılan ay oranı")
son_m = AYLAR[-1]; P_ = []
for nm, g in O.groupby("nm"):
    gt = pd.DatetimeIndex(g.t); x_e, x_o = g[g.eski.values], g[g.ozel.values]; ay = [SECIM.get((m, nm), -1) for m in AYLAR]
    P_.append(dict(coin=nm, bugunku_secim=KAD(sec(E[(E.nm == nm) & (E.bitis < SONT)])), yeni_ay=f"%{100*np.mean([a != -1 for a in ay]):.0f}",
                   eski=f"%{100*x_e.ok.mean():.0f} {100*x_e.net.mean():+.2f} ({len(x_e)})", ozel=f"%{100*x_o.ok.mean():.0f} {100*x_o.net.mean():+.2f} ({len(x_o)})" if len(x_o) else "—"))
yaz("```\n" + pd.DataFrame(P_).to_string(index=False) + "\n```")
# ---------------- B) tek başına 💵, canlıdaki 15 coin ----------------
PA = pd.read_csv(f"{CD}/prim_acik.csv"); PAC = [c for c in PA.coin if c in RAW]
BK = [(k, H) for k in (2, 2.5, 3, 4, 5) for H in (8, 24)]; EVB = {}
for nm in PAC:
    D = RAW[nm]
    for k, H in BK:
        y = D.c.shift(-(1 + H)) / D.c.shift(-1) - 1; ev = D.index[events((D.z >= k).fillna(False).values, H)]; x = (y.reindex(ev) - 2 * LMT).dropna(); x = x[x.index >= P0]
        EVB[(nm, k, H)] = x
def bsec(nm, m):
    best, bn = None, None
    for k, H in BK:
        x = EVB[(nm, k, H)]; x = x[x.index + pd.Timedelta(hours=H + 1) < m]
        if len(x) >= 10 and x.mean() > 0 and (bn is None or x.mean() > bn): best, bn = (k, H), x.mean()
    return best
OZ, SAB, CAN = [], [], []
for m in AYLAR:
    me = m + pd.offsets.MonthBegin(1)
    for nm in PAC:
        s = bsec(nm, m)
        if s: x = EVB[(nm, *s)]; OZ.append(x[(x.index >= m) & (x.index < me)])
        x = EVB[(nm, 2, 24)]; SAB.append(x[(x.index >= m) & (x.index < me)])
        r = PA[PA.coin == nm].iloc[0]; x = EVB.get((nm, float(r.esik) if float(r.esik) != int(r.esik) else int(r.esik), int(r.saat)))
        if x is not None: CAN.append(x[(x.index >= m) & (x.index < me)])
yaz("\n## B) Tek başına 💵 (canlıdaki 15 coin) — dönem dışı\n```")
for ad, parts in (("z ≥ 2 · 24 s herkese", SAB), ("COİN'E ÖZEL (yürüyen)", OZ), ("canlı ayar (bilgi: seçimi 2024+'yı gördü)", CAN)):
    X = pd.concat(parts).sort_index() if parts else pd.Series(dtype=float)
    for dn, fd in OOS:
        x = X[fd(X.index)]; yaz(f"{ad:42s} {dn:6s} " + (f"%{100*(x>0).mean():.1f} · {100*x.mean():+.3f} · {len(x)/HAF[dn]:.1f}/hafta · toplam {100*x.sum()/HAF[dn]:+.1f}/hafta" if len(x) else "—"))
yaz("```\nBugünkü seçim (tüm geçmişle): " + " · ".join(f"{nm} " + (f"z≥{s[0]:g}/{s[1]}s" if (s := bsec(nm, SONT + pd.Timedelta(days=1))) else "yok") for nm in PAC))
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("kisisel_sonuc.md", "w").write("\n".join(L) + "\n")
