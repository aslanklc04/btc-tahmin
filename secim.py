# secim.py — HAFTADA ~40–50 SİNYAL: sayıyı düşürürken isabet ve işlem başı kârı artırmak (yalnız test; canlıya dokunmaz).
# Havuz: canlıda mesajı giden tüm AL türleri (BTC 1/4/8 s + ⭐ + A · coin tek / 🤝 / 🔇 · 🧪 24 s · ⛓️ · 🧑) + 💵 ABD alıyor + 🔻 BTC kısa. Sonuç: bugünkü çıkış (süre dolunca sat), giriş sinyal saati kapanışı, limit komisyon.
# HÜCRE = sinyal tipi × coin'in kendi Coinbase primi (⛔ z ≤ −1 · ⚠️ −1…0 · ✅ 0…1 · 💪 > 1).
# ÖNCEDEN YAZILI YÖNTEM: hücre isabeti ve işlem başı neti YALNIZ 2022-06→2023 verisiyle ölçülür (tipin 2024 öncesi ortalamasına doğru büzülür, k = 30).
#   Uygun hücre: büzülmüş isabet ≥ %56 ve net > %0,10. Uygunlar nete göre sıralanır; 2023'teki haftalık sayıları toplamı 45'e ulaşana kadar eklenir.
# ÖNCEDEN KARAR: seçilen küme 2024+'da bugünkünden (⛔ hariç hepsi) isabette ≥ 3 puan ve işlem başı nette ≥ 1,5 kat iyi · 2026'da isabet ve net düşmüyor · 2024+ haftalık sayı 30–60 → canlıya aday.
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
E = pd.DataFrame(EV, columns=["aile", "sinyal", "canli", "H", "t", "r", "nm"]); E = E[(E.canli == "📨")].reset_index(drop=True)
zc = np.full(len(E), np.nan)
for nm, g in E.groupby("nm"):
    if nm in RAW: zc[g.index.values] = RAW[nm].z.reindex(pd.DatetimeIndex(g.t).tz_convert("UTC").as_unit("ns")).values
E["z"] = zc; E["yon"] = 1

# ---------------- 💵 (canlı ayar) ve 🔻 BTC kısa olayları ----------------
PA = pd.read_csv(f"{CD}/prim_acik.csv"); EK = []
for _, r_ in PA.iterrows():
    if r_.coin not in RAW: continue
    D = RAW[r_.coin]; ev = D.index[events((D.z >= r_.esik).fillna(False).values, int(r_.saat))]
    EK.append(pd.DataFrame({"aile": "💵 ABD alıyor (tek başına)", "sinyal": f"💵 {r_.coin}", "canli": "📨", "H": int(r_.saat), "t": ev, "r": np.nan, "nm": r_.coin, "z": D.z.reindex(ev).values, "yon": 1}))
D = RAW["BTC"]; ev = D.index[events((D.z <= -2).fillna(False).values, 24)]
EK.append(pd.DataFrame({"aile": "🔻 BTC kısa", "sinyal": "🔻 BTC kısa", "canli": "📨", "H": 24, "t": ev, "r": np.nan, "nm": "BTC", "z": D.z.reindex(ev).values, "yon": -1}))
E = pd.concat([E] + EK, ignore_index=True); E["t"] = pd.DatetimeIndex(E.t).tz_convert("UTC").as_unit("ns"); E["H"] = E.H.astype(int)
# ---------------- saatlik OHLC ----------------
from concurrent.futures import ThreadPoolExecutor
COINS = sorted(set(E.nm)); BAS = pd.Timestamp("2019-11-01", tz="UTC")
def ohlc(nm):
    try:
        o = fetch_1h(BAS.timestamp() * 1000, time.time() * 1000, sym=f"{nm}USDT"); o.index = pd.DatetimeIndex(o.index).as_unit("ns"); return nm, o[["high", "low", "close"]].astype(float)
    except Exception as e: print(nm, "OHLC alınamadı", e); return nm, None
with ThreadPoolExecutor(6) as ex: OH = {k: v for k, v in ex.map(ohlc, COINS) if v is not None}
SIG1 = {nm: np.log(o.close).diff().rolling(720, min_periods=168).std() for nm, o in OH.items()}

LMT_ = 0.0002
def taban(ev):
    o = OH.get(ev.nm)
    if o is None: return np.nan
    i = o.index.searchsorted(ev.t)
    if i >= len(o) or o.index[i] != ev.t or i + int(ev.H) >= len(o): return np.nan
    return ev.yon * (o.close.values[i + int(ev.H)] / o.close.values[i] - 1) - 2 * LMT_
E["net"] = [taban(ev) for ev in E.itertuples()]; E = E[np.isfinite(E.net)].copy(); E["ok"] = E.net > 0
def tip(r):
    if r.aile.startswith("coin "): return r.sinyal.split(" ", 1)[1]
    if r.aile.startswith("🧪"): return "🧪 24 s"
    if r.aile.startswith("💵"): return "💵 ABD alıyor"
    return r.sinyal
E["tip"] = [tip(r) for r in E.itertuples()]
E["zb"] = np.select([E.z <= -1, E.z <= 0, E.z <= 1, E.z > 1], ["⛔", "⚠️", "✅", "💪"], default="?")
tt = pd.DatetimeIndex(E.t); A23, A24_, A26_ = pd.Timestamp("2023-01-01", tz="UTC"), pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")
SONT = tt.max(); HAF = {"2023": 52.0, "2024+": (SONT - A24_).days / 7, "2026": (SONT - A26_).days / 7}
yaz(f"# 🎯 Haftada ~45 sinyal: isabet ve kâr için seçim — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nOlay: {len(E):,} · tip: {E.tip.nunique()} · {time.time()-T0:.0f} sn\n")
# ---- hücre puanları (yalnız seçim dönemi) ----
SEC = E[(tt >= P0) & (tt < A24_) & (E.zb != "?")]; ON = E[tt < A24_]; K = 30
tipm = ON.groupby("tip").agg(m_net=("net", "mean"), m_ok=("ok", "mean"))
H_ = SEC.groupby(["tip", "zb"]).agg(n=("net", "size"), net=("net", "mean"), ok=("ok", "mean")).reset_index().merge(tipm, left_on="tip", right_index=True, how="left")
H_["net_b"] = (H_.n * H_.net + K * H_.m_net) / (H_.n + K); H_["ok_b"] = (H_.n * H_.ok + K * H_.m_ok) / (H_.n + K)
s23 = E[(tt >= A23) & (tt < A24_)].groupby(["tip", "zb"]).size().rename("n23").reset_index(); H_ = H_.merge(s23, on=["tip", "zb"], how="left").fillna({"n23": 0}); H_["hafta23"] = H_.n23 / HAF["2023"]
H_ = H_.sort_values("net_b", ascending=False); uy = H_[(H_.ok_b >= 0.56) & (H_.net_b > 0.0010)].copy(); uy["kum"] = uy.hafta23.cumsum()
sec_h = uy[uy.kum.shift(fill_value=0) < 45]; SECILEN = set(zip(sec_h.tip, sec_h.zb))
yaz("## Seçilen hücreler (2022-06→2023 verisiyle; büzülmüş isabet ve net, 2023 haftalık sayı)\n```\n" + sec_h[["tip", "zb", "n", "ok_b", "net_b", "hafta23", "kum"]].assign(ok_b=lambda d: (100 * d.ok_b).round(1), net_b=lambda d: (100 * d.net_b).round(3)).to_string(index=False) + "\n```")
yaz(f"Uygun ama sayı dolduğu için alınmayan: {len(uy) - len(sec_h)} hücre · uygun olmayan: {len(H_) - len(uy)} hücre")
# ---- dönem dışı karşılaştırma ----
E["bugun"] = E.zb != "⛔"; E["secilen"] = [(a, b) in SECILEN for a, b in zip(E.tip, E.zb)]; E["z0"] = E.z >= 0
def oz(x, hf): return dict(hafta=len(x) / hf, isabet=100 * x.ok.mean() if len(x) else np.nan, net=100 * x.net.mean() if len(x) else np.nan, toplam=100 * x.net.sum() / hf)
TB = {}
for ad, col in (("Bugün (⛔ hariç hepsi)", "bugun"), ("SEÇİLEN (~45/hafta)", "secilen"), ("Basit: prim z ≥ 0 olan hepsi", "z0")):
    for dn, lo_ in (("2024+", A24_), ("2026", A26_)):
        x = E[E[col].values & (tt >= lo_) & (E.zb.values != "?")]; TB[(ad, dn)] = oz(x, HAF[dn])
T = pd.DataFrame(TB).T.round(2); yaz("\n## Dönem dışı sonuç (hiç görülmemiş veri)\n_haftada sinyal · isabet % · işlem başı net % · haftalık toplam %_\n```\n" + T.to_string() + "\n```")
b24, s24, b26, s26 = TB[("Bugün (⛔ hariç hepsi)", "2024+")], TB[("SEÇİLEN (~45/hafta)", "2024+")], TB[("Bugün (⛔ hariç hepsi)", "2026")], TB[("SEÇİLEN (~45/hafta)", "2026")]
c1 = s24["isabet"] - b24["isabet"] >= 3; c2 = s24["net"] >= 1.5 * b24["net"]; c3 = s26["isabet"] >= b26["isabet"] and s26["net"] >= b26["net"]; c4 = 30 <= s24["hafta"] <= 60
# haftalık blok alt sınır: seçilen − bugün isabet farkı (bugün içinde seçilen vs seçilmeyen)
X = E[(tt >= A24_) & E.bugun.values & (E.zb.values != "?")].copy(); X["h"] = pd.DatetimeIndex(X.t).floor("7D"); rng = np.random.default_rng(0)
C = pd.DataFrame({"na": X.secilen.groupby(X.h).sum(), "oa": (X.ok & X.secilen).groupby(X.h).sum(), "nb": (~X.secilen).groupby(X.h).sum(), "ob": (X.ok & ~X.secilen).groupby(X.h).sum()}).values.astype(float)
S_ = C[rng.integers(0, len(C), (2000, len(C)))].sum(axis=1)
with np.errstate(all="ignore"): fr = 100 * (S_[:, 1] / S_[:, 0] - S_[:, 3] / S_[:, 2])
lb = float(np.percentile(fr[np.isfinite(fr)], 5))
yaz(f"\nSeçilen vs bugünkü kümede seçilmeyenler, 2024+ isabet farkı %5 alt sınır: {lb:+.1f} puan")
yaz(f"\n**Önceden yazılı karar:** isabet ≥ +3 puan {'✅' if c1 else '❌'} · net ≥ 1,5 kat {'✅' if c2 else '❌'} · 2026 düşmüyor {'✅' if c3 else '❌'} · haftada 30–60 {'✅' if c4 else '❌'} → {'✅ CANLIYA ADAY' if all((c1, c2, c3, c4)) else '❌ aday değil'}")
# ---- tip tip: 2024+ ve 2026 (bilgi) ----
P_ = []
for (tp, zb), g in E[tt >= A24_].groupby(["tip", "zb"]):
    g26 = g[pd.DatetimeIndex(g.t) >= A26_]
    P_.append(dict(tip=tp, prim=zb, secildi="✅" if (tp, zb) in SECILEN else "", hafta=round(len(g) / HAF["2024+"], 1), isabet=round(100 * g.ok.mean(), 1), net=round(100 * g.net.mean(), 3),
                   isabet26=round(100 * g26.ok.mean(), 1) if len(g26) else np.nan, net26=round(100 * g26.net.mean(), 3) if len(g26) else np.nan))
yaz("\n## Hücre hücre (2024+ ve 2026, bilgi)\n```\n" + pd.DataFrame(P_).sort_values(["secildi", "net"], ascending=[False, False]).to_string(index=False) + "\n```")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("secim_sonuc.md", "w").write("\n".join(L) + "\n")
