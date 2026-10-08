# prim_pencere.py — COINBASE PRİMİ: "NORMAL" HANGİ SÜREYE GÖRE ÖLÇÜLMELİ? + PRİM BÜYÜDÜKÇE FİYAT DAHA ÇOK / DAHA HIZLI ARTIYOR MU? (yalnız test; canlıya dokunmaz)
# Prim = log(Coinbase COIN-USD / Binance COINUSDT), saatlik. z = primin son W saatlik ortalamasından sapması / std.  Canlı: W = 720 saat (30 gün).
# Denenen pencereler: 1 gün (24 s) · 1 hafta (168 s) · 30 gün (720 s, canlı) · 3 ay (2160 s) · 6 ay (4320 s).  Her coin KENDİ primiyle; BTC sinyalleri BTC primiyle.
# 1) FİLTRE (tüm canlı sinyal türleri: BTC 1/4/8 s + ⭐ + A · coin tek başına / 🤝 / 🔇 · 🧪 24 s · ⛓️ ETH · 🧑): ✅ z > 0 · ⚠️ −1 < z ≤ 0 · ⛔ z ≤ −1, isabet farkı (✅ − ⛔).
#    ÖNCEDEN KARAR: bir pencere 30 günün yerine ancak — tüm türler birlikte ✅−⛔ farkı 30 günden ≥ 2 puan fazla, HEM 2022-06→2023 HEM 2024+ döneminde · 2026'da daha kötü değil ·
#    2024+ döneminde 7 türün en az 4'ünde 30 günden iyi.
# 2) DOZ-YANIT: tüm saatler, coin coin · z dilimleri (≤−2 … ≥3) · giriş 1 saat sonra · 1/4/8/24/72 saat getirisi, coin'in o dönemdeki ortalamasının ÜSTÜ (fazla getiri) ·
#    "daha hızlı": 24 saatlik fazla getirinin ne kadarı ilk 1/4/8 saatte geliyor.  Coin'ler eşit ağırlıklı.
# 3) TEK BAŞINA 💵 (tüm coin'ler havuz, z ≥ 2 / z ≥ 3 → AL, 4/8/24 s): ÖNCEDEN KARAR: pencere ancak 6 kombinasyonun ≥ 5'inde işlem başı net HEM 2022-06→2023 HEM 2024+ döneminde 30 günden yüksekse.
import os, glob, gzip, json, pickle, time, numpy as np, pandas as pd
from ortak import *
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
f = lambda p: glob.glob(p, recursive=True)
RAW = {k: v.astype("float64") for k, v in pd.read_pickle(f("art3/**/prim_veri.pkl")[0]).items()}; RAW = {k: v for k, v in RAW.items() if len(v) >= 3000}
for k, v in RAW.items(): v.index = pd.DatetimeIndex(v.index).tz_convert("UTC").as_unit("ns")
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
PEN = {"1 gün": (24, 24), "1 hafta": (168, 168), "30 gün": (720, 168), "3 ay": (2160, 540), "6 ay": (4320, 1080)}; CAN = "30 gün"
zf = lambda bp, W, mp: (bp - bp.rolling(W, min_periods=mp).mean()) / (bp.rolling(W, min_periods=mp).std() + 1e-9)
ZW = {pn: {nm: zf(D.bp, W, mp) for nm, D in RAW.items()} for pn, (W, mp) in PEN.items()}
fk = pd.concat([(ZW[CAN][nm] - D.z).abs() for nm, D in RAW.items()]).dropna()
yaz(f"# 💵 Coinbase primi: pencere süresi ve doz-yanıt — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n{len(RAW)} coin · kontrol: 30 gün z yeniden hesap ile kayıtlı z farkı medyan {fk.median():.4f}, %99 {fk.quantile(.99):.3f}\n")
# ======================= olaylar (prim_hepsi.py ile aynı; prim penceresi sonradan) =======================
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
            kaydet("BTC 1/4/8 s + ⭐ + A", f"BTC {H}s {lad} {'↑' if sg > 0 else '↓'}", X.index[ev], sg * (np.exp(y.values[ev]) - 1), H, "BTC", "📨" if act[:1] in ("✅", "🟢", "🔴") else "")
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
    for ad, acik, yon, gun, kos, _ in ZC.KURAL: ev = Zs.index[events(kos(Zs).fillna(False).values, gun)]; gun_isle("⛓️ ETH", f"⛓️ {ad}", ev, "ETH", 6, gun, yon)
except Exception as e: yaz(f"_⛓️ atlandı: {type(e).__name__} {str(e)[:120]}_")
try:
    j = json.load(open("veri_bgeo/coins-addr-1-BTC.json")); d = pd.DataFrame(j); d.index = pd.to_datetime(d.pop("d"), utc=True).dt.floor("D")
    sm = d.drop(columns=[c for c in d.columns if "ts" in c.lower() or "unix" in c.lower()]).apply(pd.to_numeric, errors="coerce").iloc[:, 0].dropna().sort_index()
    sm = sm[~sm.index.duplicated()].asfreq("D"); zk = np.log(sm).diff(30); zk = (zk - zk.rolling(90, min_periods=30).mean()) / (zk.rolling(90, min_periods=30).std() + 1e-12)
    ev = zk.index[events((zk <= -1.5).fillna(False).values, 7)]
    for nm in ("BTC", "ETH"): gun_isle("🧑 küçük yatırımcı", f"🧑 {nm} AL", ev, nm, 12, 7, 1)
except Exception as e: yaz(f"_🧑 atlandı: {type(e).__name__} {str(e)[:120]}_")
E = pd.DataFrame(EV, columns=["aile", "sinyal", "canli", "H", "t", "r", "nm"]); E = E[(E.canli == "📨") & (pd.DatetimeIndex(E.t) >= P0)].reset_index(drop=True)
for pn in PEN:
    zc = np.full(len(E), np.nan)
    for nm, g in E.groupby("nm"):
        if nm in ZW[pn]: zc[g.index.values] = ZW[pn][nm].reindex(pd.DatetimeIndex(g.t).tz_convert("UTC").as_unit("ns")).values
    E[f"z_{pn}"] = zc
E["net"] = E.r - 2 * LMT; tt = pd.DatetimeIndex(E.t)
yaz(f"Canlıda mesajı giden sinyaller (2022-06+): {len(E):,} · " + " · ".join(f"{a} {n:,}" for a, n in E.aile.value_counts().items()) + f" · primi bilinen (30 gün): {E[f'z_{CAN}'].notna().sum():,} · {time.time()-T0:.0f} sn\n")
# ======================= 1) FİLTRE =======================
AILE = list(E.aile.value_counts().index); FS = {}
def istat(g, z, md):
    o = {}
    for gn, fg in (("✅", lambda z: z > 0), ("⚠️", lambda z: (z > -1) & (z <= 0)), ("⛔", lambda z: z <= -1)):
        m = md & fg(z); o[gn] = (int(m.sum()), 100 * g.r.values[m].__gt__(0).mean() if m.any() else np.nan, 100 * g.net.values[m].mean() if m.any() else np.nan)
    o["n"] = int((md & np.isfinite(z)).sum()); return o
yaz("## 1) Filtre olarak: hangi pencere iyi sinyali kötüden daha iyi ayırıyor?\n_hücre: ✅ isabet / ⛔ isabet (fark) · ⛔ payı — ⛔ = \"ABD satıyor, ALMA\" uyarısı alan sinyaller_")
for dn, fd in DON:
    T = {}
    for aile in AILE + ["HEPSİ"]:
        g = E if aile == "HEPSİ" else E[E.aile == aile]; md = fd(pd.DatetimeIndex(g.t)); T[aile] = {}
        for pn in PEN:
            z = g[f"z_{pn}"].values; o = istat(g, z, md); FS[(dn, aile, pn)] = o; a_, k_ = o["✅"][1], o["⛔"][1]
            T[aile][pn] = f"{a_:.0f}/{k_:.0f} ({a_-k_:+.1f}) %{100*o['⛔'][0]/max(1,o['n']):.0f}" if o["⛔"][0] >= 5 and o["✅"][0] >= 5 else "—"
    yaz(f"\n### {dn}\n```\n" + pd.DataFrame(T).T.reindex(columns=list(PEN)).to_string() + "\n```")
yaz("\n_işlem başı net % (✅ / ⛔), tüm türler birlikte:_ " + " · ".join(f"{pn}: " + " | ".join(f"{dn} {FS[(dn,'HEPSİ',pn)]['✅'][2]:+.2f}/{FS[(dn,'HEPSİ',pn)]['⛔'][2]:+.2f}" for dn, _ in DON) for pn in PEN))
fr = lambda dn, a, pn: FS[(dn, a, pn)]["✅"][1] - FS[(dn, a, pn)]["⛔"][1]
yaz("\n**Önceden yazılı karar (filtre):**")
for pn in PEN:
    if pn == CAN: continue
    c1 = fr("22-06→23", "HEPSİ", pn) - fr("22-06→23", "HEPSİ", CAN); c2 = fr("2024+", "HEPSİ", pn) - fr("2024+", "HEPSİ", CAN); c3 = fr("2026", "HEPSİ", pn) - fr("2026", "HEPSİ", CAN)
    kac = sum(bool(np.isfinite(fr("2024+", a, pn)) and fr("2024+", a, pn) > fr("2024+", a, CAN)) for a in AILE)
    ok = c1 >= 2 and c2 >= 2 and c3 >= 0 and kac >= 4
    yaz(f"- {pn}: fark 30 güne göre {c1:+.1f} (22-06→23) · {c2:+.1f} (2024+) · {c3:+.1f} (2026) · 2024+ daha iyi tür {kac}/{len(AILE)} → {'✅ 30 GÜNDEN İYİ' if ok else '❌ 30 günden iyi değil'}")
# ======================= 2) DOZ-YANIT =======================
BK = ((-np.inf, -2, "≤−2"), (-2, -1, "−2…−1"), (-1, 0, "−1…0"), (0, 1, "0…1"), (1, 2, "1…2"), (2, 3, "2…3"), (3, np.inf, "≥3")); HS = (1, 4, 8, 24, 72)
FW = {nm: {H: (D.c.shift(-(1 + H)) / D.c.shift(-1) - 1) for H in HS} for nm, D in RAW.items()}
DR = []
for pn in PEN:
    for nm, D in RAW.items():
        z = ZW[pn][nm]; ix = D.index
        for dn, fd in DON[:2]:
            md = fd(ix) & z.notna().values
            if md.sum() < 500: continue
            base = {H: FW[nm][H].values[md & FW[nm][H].notna().values].mean() for H in HS}
            for lo, hi, bn in BK:
                m = md & (z.values > lo) & (z.values <= hi)
                if m.sum() < 20: continue
                row = dict(pencere=pn, donem=dn, coin=nm, dilim=bn, n=int(m.sum()))
                for H in HS:
                    v = FW[nm][H].values[m]; v = v[np.isfinite(v)]; row[f"f{H}"] = 100 * (v.mean() - base[H]) if len(v) else np.nan
                v = FW[nm][24].values[m]; v = v[np.isfinite(v)]; row["isabet24"] = 100 * (v > 0).mean() if len(v) else np.nan; DR.append(row)
DR = pd.DataFrame(DR); DR.to_csv("prim_pencere_doz.csv", index=False)
yaz("\n## 2) Prim büyüdükçe fiyat daha çok / daha hızlı artıyor mu?\n_Tüm saatler, coin'ler eşit ağırlık. Değer: o z diliminde, giriş 1 saat sonra, coin'in o dönemki ortalamasının ÜSTÜNDEKİ getiri % (fazla getiri). \"coin +\" = 24 saatte fazla getirisi pozitif coin oranı._")
for pn in PEN:
    for dn, _ in DON[:2]:
        G = DR[(DR.pencere == pn) & (DR.donem == dn)]
        if G.empty: continue
        P_ = G.groupby("dilim", sort=False).agg(coin=("coin", "nunique"), saat=("n", "sum"), **{f"{H} s": (f"f{H}", "mean") for H in HS}, isabet24=("isabet24", "mean"), coin_arti=("f24", lambda x: 100 * (x > 0).mean()))
        P_ = P_.reindex([b for _, _, b in BK]).dropna(how="all"); P_["ilk 4 s payı"] = (100 * P_["4 s"] / P_["24 s"]).where(P_["24 s"].abs() > 0.05)
        yaz(f"\n### {pn} · {dn}\n```\n" + P_.round(2).to_string() + "\n```")
# coin coin: tek bakışta (2024+), her pencere için 24 s fazla getiri, dilim dilim + sıralama uyumu (Spearman)
yaz("\n### Coin coin (2024+) — 24 saat fazla getiri %, z dilimine göre · ρ: z büyüdükçe getiri artıyor mu (1 = tam uyum)")
for pn in PEN:
    G = DR[(DR.pencere == pn) & (DR.donem == "2024+")]
    if G.empty: continue
    P_ = G.pivot_table(index="coin", columns="dilim", values="f24").reindex(columns=[b for _, _, b in BK])
    P_["ρ"] = [pd.Series(r.dropna().values).corr(pd.Series(np.arange(len(r.dropna()))), method="spearman") if r.notna().sum() >= 4 else np.nan for _, r in P_.iterrows()]
    P_ = P_.sort_values("ρ", ascending=False)
    yaz(f"\n**{pn}** — ρ > 0 olan coin: {int((P_['ρ'] > 0).sum())}/{int(P_['ρ'].notna().sum())} · ortalama ρ {P_['ρ'].mean():+.2f}\n```\n" + P_.round(2).to_string() + "\n```")
# ======================= 3) TEK BAŞINA 💵 =======================
yaz("\n## 3) Tek başına 💵 sinyal (tüm coin'ler havuz): pencereye göre\n_işlem · isabet % · işlem başı net % · alt sınır %_")
def net_ser(D, z, k, H):
    y = D.c.shift(-(1 + H)) / D.c.shift(-1) - 1; ev = D.index[events((z >= k).fillna(False).values, H)]; return y.reindex(ev).dropna() - 2 * LMT
TB, NET = [], {}
for pn in PEN:
    for k in (2, 3):
        for H in (4, 8, 24):
            net = pd.concat([net_ser(D, ZW[pn][nm], k, H) for nm, D in RAW.items()]).sort_index(); row = dict(pencere=pn, kural=f"z ≥ {k}", saat=H)
            for dn, fd in DON:
                x = net[fd(net.index)]; NET[(pn, k, H, dn)] = x.mean() if len(x) else np.nan
                row[dn] = f"{len(x)} · {100*(x>0).mean():.0f} · {100*x.mean():+.2f} · {100*wboot(x.values, x.index.values, 400)[0]:+.2f}" if len(x) >= 8 else "—"
            TB.append(row)
yaz("```\n" + pd.DataFrame(TB).set_index(["kural", "saat", "pencere"]).sort_index().to_string() + "\n```")
# canlıdaki 15 coin ayarıyla (esik, saat canlıda 30 güne göre seçildi → 30 gün lehine yanlı; yalnız bilgi)
PA = pd.read_csv(f"{CD}/prim_acik.csv"); CL = []
for pn in PEN:
    net = pd.concat([net_ser(RAW[r.coin], ZW[pn][r.coin], r.esik, int(r.saat)) for _, r in PA.iterrows() if r.coin in RAW]).sort_index()
    CL.append(dict(pencere=pn, **{dn: f"{len(x)} · {100*(x>0).mean():.0f} · {100*x.mean():+.2f}" for dn, fd in DON for x in [net[fd(net.index)]]}))
yaz("\n_Canlı 15 coin ayarıyla (30 güne göre seçildiği için 30 gün lehine yanlı):_\n```\n" + pd.DataFrame(CL).to_string(index=False) + "\n```")
yaz("\n**Önceden yazılı karar (tek başına):**")
for pn in PEN:
    if pn == CAN: continue
    s1 = sum(bool(NET[(pn, k, H, "22-06→23")] > NET[(CAN, k, H, "22-06→23")]) for k in (2, 3) for H in (4, 8, 24)); s2 = sum(bool(NET[(pn, k, H, "2024+")] > NET[(CAN, k, H, "2024+")]) for k in (2, 3) for H in (4, 8, 24))
    yaz(f"- {pn}: 30 günden yüksek net — 22-06→23: {s1}/6 · 2024+: {s2}/6 → {'✅ 30 GÜNDEN İYİ' if s1 >= 5 and s2 >= 5 else '❌ 30 günden iyi değil'}")
yaz(f"\n_Not: 3 ve 6 ay pencereleri için veri 2022-05'te başladığından ilk aylarda pencere eksik doluydu (en az 540 / 1080 saatle). Süre: {time.time()-T0:.0f} sn_")
open("prim_pencere_sonuc.md", "w").write("\n".join(L) + "\n")
