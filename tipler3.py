# tipler3.py — tipler2'nin öne çıkan bulgusunun kontrolü (API çağrısı yok: veri_bgeo/ önbelleği):
# "Küçük cüzdanlar (<1 BTC) 30 günde BTC kaybediyor (küçük yatırımcı kaçıyor) → BTC AL" — z ≤ −1,5 (3 ve 7 gün), z ≤ −1 (7 gün)
# (1) Bu sadece "fiyat düştü, dipten al" mı? Aynı kural fiyatla: BTC 30 g getiri z ≤ −1,5 → AL. Ayrıca küçük cüzdan sinyali fiyat düşmemişken (fiyat z > −1) de çalışıyor mu?
# (2) Giriş saati: veri günü d → d+1 15:00 TR · d+1 kapanışı (araştırma) · d+2 15:00 TR (geç veri)
# (3) İşlem sırasındaki en kötü ters hareket (kaldıraç için)
import json, numpy as np, pandas as pd, requests, time
from ortak import *
L = []
def yaz(s=""): print(s, flush=True); L.append(s)
def oku(ep):
    j = json.load(open(f"veri_bgeo/{ep}.json")); d = pd.DataFrame(j); d.index = pd.to_datetime(d.pop("d"), utc=True).dt.floor("D")
    return d.drop(columns=[c for c in d.columns if "ts" in c.lower() or "unix" in c.lower()]).apply(pd.to_numeric, errors="coerce").iloc[:, 0].sort_index()
sm = oku("coins-addr-1-BTC")
now = pd.Timestamp.now(tz="UTC")
H1 = fetch_1h(pd.Timestamp("2022-06-01", tz="UTC").timestamp() * 1000, now.timestamp() * 1000, sym="BTCUSDT")
px = H1.close[H1.index.hour == 0]; px.index = px.index - pd.Timedelta(days=1)                    # gün d kapanışı (00:00 UTC d+1), indeks = gün d
ix = px.index
def zs(s, n=90): return (s - s.rolling(n, min_periods=30).mean()) / (s.rolling(n, min_periods=30).std() + 1e-12)
zk = zs(np.log(sm).diff(30).reindex(ix)); zp = zs(np.log(px).diff(30))
SEC_END, A26, LMT = pd.Timestamp("2024-10-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC"), 0.0002
DON = (("seçim (→2024-09)", lambda i: i < SEC_END), ("doğrulama (2024-10→)", lambda i: i >= SEC_END), ("2026", lambda i: i >= A26))
GIRIS = {"d+1 15:00 TR": pd.Timedelta(days=1, hours=12), "d+1 kapanışı (araştırma)": pd.Timedelta(days=2), "d+2 15:00 TR (geç)": pd.Timedelta(days=2, hours=12)}
def test(m, HD, dt):
    ev = ix[events(m.reindex(ix).fillna(False).values, HD)]; R = []
    for d in ev:
        t1 = d + dt; t2 = t1 + pd.Timedelta(days=HD)
        if t2 > H1.index[-1] or t1 not in H1.index: continue
        p1 = H1.close.loc[t1]; w = H1.loc[(H1.index > t1) & (H1.index <= t2)]
        R.append(dict(t=d, net=w.close.iloc[-1] / p1 - 1 - 2 * LMT, mae=w.low.min() / p1 - 1))
    E = pd.DataFrame(R).set_index("t") if R else pd.DataFrame(columns=["net", "mae"])
    out = {}
    for pn, f in DON:
        e = E[f(E.index)] if len(E) else E
        out[pn] = (len(e), 100 * (e.net > 0).mean() if len(e) else np.nan, 100 * e.net.mean() if len(e) else np.nan,
                   100 * wboot(e.net.values, e.index.values)[0] if len(e) >= 8 else np.nan, 100 * e.mae.min() if len(e) else np.nan)
    return out
def fmt(o): return " · ".join(("—" if not np.isfinite(v) else (f"{v:.0f}" if i < 2 else (f"{v:+.2f}" if i < 4 else f"{v:.1f}"))) for i, v in enumerate(o))
yaz(f"# 🧑 Küçük yatırımcı kaçıyor → AL: kontrol — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\nVeri: küçük cüzdan (<1 BTC) {sm.index[0]:%Y-%m-%d} → {sm.index[-1]:%Y-%m-%d}\n")
yaz(f"İki ölçünün ilişkisi: küçük cüzdan z ile BTC 30 g getiri z korelasyonu {zk.corr(zp):+.2f} (1 = aynı şey)\n")
K = {"KÜÇÜK z ≤ −1,5": zk <= -1.5, "KÜÇÜK z ≤ −1": zk <= -1, "FİYAT 30 g z ≤ −1,5 (dipten al)": zp <= -1.5, "FİYAT 30 g z ≤ −1": zp <= -1,
     "KÜÇÜK z ≤ −1,5 ve fiyat düşmemiş (z > −1)": (zk <= -1.5) & (zp > -1), "KÜÇÜK z ≤ −1 ve fiyat düşmemiş (z > −1)": (zk <= -1) & (zp > -1)}
rows = []
for k, m in K.items():
    for HD in (3, 7):
        for gn, dt in GIRIS.items():
            if k.startswith("FİYAT") and gn != "d+1 kapanışı (araştırma)": continue
            o = test(m, HD, dt); rows.append(dict(kural=k, gun=HD, giris=gn, **{pn: fmt(o[pn]) for pn, _ in DON}))
yaz("_işlem · isabet % · işlem başı net % · alt sınır % · en kötü ara düşüş %_\n```\n" + pd.DataFrame(rows).set_index(["kural", "gun", "giris"]).to_string() + "\n```")
yaz(f"\nŞu an: küçük cüzdan z {zk.dropna().iloc[-1]:+.2f} · fiyat 30 g z {zp.dropna().iloc[-1]:+.2f} (veri günü {zk.dropna().index[-1]:%d.%m})")
ev = ix[events((zk <= -1.5).fillna(False).values, 7)]
yaz("Son 10 sinyal (z ≤ −1,5, 7 gün): " + ", ".join(f"{d:%d.%m.%y}" for d in ev[-10:]))
open("tipler3_sonuc.md", "w").write("\n".join(L) + "\n")
