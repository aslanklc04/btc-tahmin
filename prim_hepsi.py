# prim_hepsi.py — COINBASE PRİMİ FİLTRESİ TÜM SİNYAL TÜRLERİNDE (yalnız test; canlıya dokunmaz).
# Her sinyal, geldiği saatteki primle üçe ayrılır: ✅ ABD alıyor (z > 0) · ⚠️ almıyor (−1 < z ≤ 0) · ⛔ satıyor (z ≤ −1).  (z: son 720 saate göre, canlıdaki cb_prim ile aynı)
#   BTC sinyalleri → BTC primi · altcoin ve 24 saat → coin'in KENDİ primi · ⛓️ ETH → ETH primi · 🧑 → BTC ve ETH kendi primi.
# Sinyaller: BTC 1/4/8 saat (her yön ve seviye; canlıda mesajı gidenler işaretli) + ⭐ + 🟢 A (sf_BTCUSDT.pkl, egit_coin.py SF_AKTAR) ·
#   altcoin tek başına / 🤝 BTC ile ortak / 🔇 BTC sessizken (disa_*.pkl + canlı listeler) · 🧪 24 saat (disa24_*.pkl) · ⛓️ ETH arz/talep · 🧑 küçük yatırımcı.
# Sonuç: isabet ve işlem başı net (limit komisyon %0,02 × 2), dönemler: 2022-06→2023 (prim verisi başlangıcı) · 2024+ · 2026. Sayım canlıyla aynı: tutma süresince tekrar yok.
import os, glob, gzip, json, pickle, numpy as np, pandas as pd
from ortak import *
L = []
def yaz(s=""): print(s, flush=True); L.append(s)
f = lambda p: glob.glob(p, recursive=True)
ZP = {k: v.astype("float64") for k, v in pd.read_pickle(f("art3/**/prim_veri.pkl")[0]).items()}
EX = {os.path.basename(p)[5:-4]: pd.read_pickle(p) for p in f("art1/**/disa_*USDT.pkl")}
E24 = {os.path.basename(p)[7:-4]: pd.read_pickle(p) for p in f("art2/**/disa24_*USDT.pkl")}
SFB = pd.read_pickle("sf_BTCUSDT.pkl").astype("float64") if os.path.exists("sf_BTCUSDT.pkl") else None
CD = "canli/durum"; CANLI = [l.strip() for l in open(f"{CD}/coin_listesi.txt") if l.strip()]
JOINT, TEKL = pd.read_csv(f"{CD}/ortak_acik.csv"), pd.read_csv(f"{CD}/tek_acik.csv")
SIGON = {}
for s in CANLI:
    with gzip.open(f"{CD}/model_{s}.pkl.gz", "rb") as g: SIGON[s] = {k: bool(v["on"]) for k, v in pickle.load(g)["SIG"].items()}
with gzip.open(f"{CD}/model.pkl.gz", "rb") as g: MB = pickle.load(g)
BILGI = {"DOGE", "NEAR", "PEPE"}; LMT = 0.0002
P0, A24, A26 = pd.Timestamp("2022-06-01", tz="UTC"), pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")
DON = (("22-06→23", lambda i: (i >= P0) & (i < A24)), ("2024+", lambda i: i >= A24), ("2026", lambda i: i >= A26))
GRP = (("tümü", lambda z: np.isfinite(z)), ("✅ z>0", lambda z: z > 0), ("⚠️ −1<z≤0", lambda z: (z > -1) & (z <= 0)), ("⛔ z≤−1", lambda z: z <= -1))
def zat(nm, idx):
    return ZP[nm].z.reindex(pd.DatetimeIndex(idx)).values if nm in ZP else np.full(len(idx), np.nan)
SATIR = []
def kaydet(aile, ad, t, r, z, H, canli=""):
    """t: olay zamanı, r: yön düzeltilmiş basit getiri, z: o andaki prim."""
    t, r, z = pd.DatetimeIndex(t), np.asarray(r, float), np.asarray(z, float); ok = np.isfinite(r)
    t, r, z = t[ok], r[ok], z[ok]
    for pn, fd in DON:
        md = fd(t)
        for gn, fg in GRP:
            m = md & fg(z); x = r[m]
            SATIR.append(dict(aile=aile, sinyal=ad, canli=canli, H=H, donem=pn, grup=gn, n=int(m.sum()), isabet=100 * (x > 0).mean() if len(x) else np.nan, net=100 * (x - 2 * LMT).mean() if len(x) else np.nan))
yaz(f"# 💵 Coinbase primi filtresi — tüm sinyal türleri · {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n")
# ---- 1) BTC 1/4/8 saat (her yön/seviye) + ⭐ + A ----
if SFB is not None:
    X = SFB
    for H in (1, 4, 8):
        S, C, T10, T30, y = X[f"S{H}"], X[f"C{H}"], X[f"T10{H}"], X[f"T30{H}"], X[f"y{H}"]
        for sg in (1, -1):
            for li, lad in ((2, "Çok güçlü"), (1, "Güçlü")):
                lvl = np.where(C >= T10, 2, np.where(C >= T30, 1, 0)); m = ((np.sign(S) == sg) & (lvl == li) & T10.notna() & y.notna()).values
                ev = events(m, H); st = MB["R"][H]["STATS"][(li, sg)]; act, _ = action(H, sg, li, st)
                canli = "📨" if act[:1] in ("✅", "🟢", "🔴") else ""
                kaydet("BTC", f"BTC {H}s {lad} {'↑' if sg > 0 else '↓'}", X.index[ev], sg * (np.exp(y.values[ev]) - 1), zat("BTC", X.index[ev]), H, canli)
    star = ((X.S4 > 0) & (X.C4 >= X.T104) & (X.S8 > 0) & (X.C8 >= X.T108) & X.y8.notna()).values; ev = events(star, 8)
    kaydet("BTC", "BTC ⭐ en güçlü (8s)", X.index[ev], np.exp(X.y8.values[ev]) - 1, zat("BTC", X.index[ev]), 8, "📨")
    ac = ((X.am >= 0.85) & X.y4.notna()).values; ev = events(ac, 4)
    kaydet("BTC", "BTC 🟢 A sınıfı (4s)", X.index[ev], np.exp(X.y4.values[ev]) - 1, zat("BTC", X.index[ev]), 4, "📨")
else: yaz("_⚠️ sf_BTCUSDT.pkl yok: BTC ufuk sinyalleri atlandı_")
# ---- 2) altcoin model sinyalleri ----
B = EX["BTCUSDT"]; AD = {"star": ("⭐", 8, "y8"), "u4": ("4s ÇG↑", 4, "y4"), "acls": ("A", 4, "y4")}
for s in CANLI:
    nm = s[:-4]; X = EX.get(s)
    if X is None: continue
    Bx = B.reindex(X.index); bu4 = Bx.u4.fillna(False).values.astype(bool); bany = (Bx.star.fillna(False) | Bx.u4.fillna(False) | Bx.acls.fillna(False)).values.astype(bool)
    jo, te = set(JOINT[JOINT.sym == s].sinyal), set(TEKL[TEKL.sym == s].sinyal); zc = zat(nm, X.index)
    for k, (ad, H0, yc0) in AD.items():
        for aile, kos, acik in (("tek başına", np.ones(len(X), bool), SIGON[s].get(k, False)), ("🤝 ortak", bu4, k in jo), ("🔇 sessiz", ~bany, k in te)):
            H, yc = (H0, yc0) if (aile == "tek başına") else (4, "y4")
            m = X[k].fillna(False).values.astype(bool) & kos & X[yc].notna().values; ev = events(m, H)
            kaydet(f"coin {aile}" + (" (bilgi coin'i)" if nm in BILGI else ""), f"{nm} {aile} {ad}", X.index[ev], np.exp(X[yc].values[ev]) - 1, zc[ev], H, "📨" if acik else "")
# ---- 3) 24 saat deneme ----
for s, X in E24.items():
    nm = s.replace("USDT", ""); X = X.reindex(pd.date_range(X.index[0], X.index[-1], freq="1h", tz="UTC")); c = X.close.ffill(limit=3).values; n = len(X)
    m = np.nan_to_num(((X.S24 > 0) & (X.C24 >= X.T10_24)).values).astype(bool) & X.T10_24.notna().values & (np.arange(n) + 25 < n); ev = events(m, 24)
    kaydet("🧪 24 saat" + (" (bilgi coin'i)" if nm in BILGI else ""), f"{nm} 24s", X.index[ev], c[ev + 24] / c[ev] - 1, zat(nm, X.index[ev]), 24, "📨")
# ---- 4) ⛓️ ETH arz/talep (giriş d+1 06:00 UTC) ve 5) 🧑 küçük yatırımcı (giriş d+1 12:00 UTC) ----
def gun_isle(aile, ad, gunler, nm, saat, HD, yon):
    D = ZP[nm]; t1 = pd.DatetimeIndex(gunler) + pd.Timedelta(days=1, hours=saat); r, z = [], []
    for t in t1:
        t2 = t + pd.Timedelta(days=HD)
        if t in D.index and t2 in D.index: r.append(yon * (D.c.loc[t2] / D.c.loc[t] - 1)); z.append(D.z.loc[t])
        else: r.append(np.nan); z.append(np.nan)
    kaydet(aile, ad, t1, r, z, HD * 24, "📨")
try:
    import zincir_canli as ZC
    Zs = ZC.olcu(ZC.cm("eth", gun=1700), ZC.stabil())
    for ad, acik, yon, gun, kos, _ in ZC.KURAL:
        ev = Zs.index[events(kos(Zs).fillna(False).values, gun)]; gun_isle("⛓️ ETH", f"⛓️ {ad}", ev, "ETH", 6, gun, yon)
except Exception as e: yaz(f"_⛓️ atlandı: {type(e).__name__} {str(e)[:120]}_")
try:
    j = json.load(open("veri_bgeo/coins-addr-1-BTC.json")); d = pd.DataFrame(j); d.index = pd.to_datetime(d.pop("d"), utc=True).dt.floor("D")
    sm = d.drop(columns=[c for c in d.columns if "ts" in c.lower() or "unix" in c.lower()]).apply(pd.to_numeric, errors="coerce").iloc[:, 0].dropna().sort_index()
    sm = sm[~sm.index.duplicated()].asfreq("D"); zk = np.log(sm).diff(30); zk = (zk - zk.rolling(90, min_periods=30).mean()) / (zk.rolling(90, min_periods=30).std() + 1e-12)
    ev = zk.index[events((zk <= -1.5).fillna(False).values, 7)]
    for nm in ("BTC", "ETH"): gun_isle("🧑 küçük yatırımcı", f"🧑 {nm} AL", ev, nm, 12, 7, 1)
except Exception as e: yaz(f"_🧑 atlandı: {type(e).__name__} {str(e)[:120]}_")
R = pd.DataFrame(SATIR); R.to_csv("prim_hepsi_tum.csv", index=False)
# ---- rapor ----
def hucre(x): return f"%{x.isabet:.0f} · {x.net:+.2f} ({int(x.n)})" if x.n >= 5 else (f"({int(x.n)})" if x.n else "—")
def tablo(G, baslik):
    P = {}
    for (sig, pn), g in G.groupby(["sinyal", "donem"], sort=False):
        P.setdefault(sig, {"📨": g.canli.iloc[0]}); P[sig].update({f"{pn} {r.grup}": hucre(r) for _, r in g.iterrows()})
    T = pd.DataFrame(P).T
    cols = ["📨"] + [f"{pn} {gn}" for pn in ("2024+", "2026") for gn, _ in GRP]
    yaz(f"### {baslik}\n_hücre: isabet · işlem başı net % (işlem sayısı) · 📨 = canlıda mesajı gidiyor_\n```\n" + T.reindex(columns=cols).to_string() + "\n```")
def havuz(G):                                                                                         # aynı aile içinde tüm sinyaller birlikte
    out = []
    for (pn, gn), g in G.groupby(["donem", "grup"], sort=False):
        n = g.n.sum(); out.append(dict(donem=pn, grup=gn, n=int(n), isabet=(g.isabet.fillna(0) * g.n).sum() / max(1, n), net=(g.net.fillna(0) * g.n).sum() / max(1, n)))
    return pd.DataFrame(out)
yaz("## Özet: aile başına (canlıda mesajı giden türler birlikte)\n_isabet · işlem başı net % (işlem)_\n")
oz = []
for aile, g in R[R.canli == "📨"].groupby("aile", sort=False):
    h = havuz(g)
    for _, r in h.iterrows(): oz.append(dict(aile=aile, donem=r.donem, grup=r.grup, deger=f"%{r.isabet:.0f} · {r.net:+.2f} ({r.n})" if r.n >= 5 else f"({r.n})"))
O = pd.DataFrame(oz).pivot_table(index=["aile", "donem"], columns="grup", values="deger", aggfunc="first")
yaz("```\n" + O.reindex(columns=[gn for gn, _ in GRP]).to_string() + "\n```")
yaz("\n## Ayrıntı")
for aile, g in R.groupby("aile", sort=False): tablo(g, aile)
yaz(f"\n_BTC ⭐/A ve 1/4/8 saat sinyalleri araştırma eğitiminin (egit_coin.py, BTCUSDT) yürüyen test çıktısından; canlı BTC modeli aynı yöntem. Prim verisi 2022-06'dan._")
open("prim_hepsi_sonuc.md", "w").write("\n".join(L) + "\n")
