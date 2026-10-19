# canli_olay.py — DENETİM (18.10.2026, yalnız bilgi): canlıda GÖNDERİLEN her ana/yedek sinyalin gerçek sonucu, olay (saat) bazında + o pencerede BTC ne yaptı. 
# karne.py ile aynı ölçüm (sinyal saati kapanışı → süre sonu kapanışı, %0,04). Main kökünden çalışır.
import numpy as np, pandas as pd
from karne import coz, sinif, KAYIT_F
from ortak import fetch_1h, DISPLAY_TZ
L = []
def yaz(s=""): print(s, flush=True); L.append(str(s))
K = pd.read_csv(KAYIT_F, dtype=str).fillna(""); rows = []
for r in K.itertuples():
    su = int(float(r.sure)) if r.sure else None; t0 = pd.Timestamp(r.t, tz=DISPLAY_TZ).floor("h").tz_convert("UTC")
    for nm, H, yon, tur, isr in coz(r.e, su): rows.append(dict(t0=t0, sinif=sinif(r.s, r.k), coin=nm, H=H, yon=yon, tur=tur + (" 🔥" if "🔥" in r.s else "")))
X = pd.DataFrame(rows).drop_duplicates(["t0", "coin", "H", "yon", "tur"]).reset_index(drop=True)
now = pd.Timestamp.now(tz="UTC"); bas = X.t0.min() - pd.Timedelta(hours=2); P = {}
for nm in set(X.coin) | {"BTC"}:
    try: P[nm] = fetch_1h(bas.value // 10**6, now.value // 10**6, sym=nm + "USDT")
    except Exception as e: print("fiyat yok", nm, e)
out = []
for r in X.itertuples():
    o = P.get(r.coin); b = P["BTC"]; t1 = r.t0 + pd.Timedelta(hours=int(r.H))
    if o is None or r.t0 not in o.index: continue
    k_ = t1 in o.index; c = o.close; p1 = c[t1] if k_ else c.iloc[-1]; w = o[(o.index > r.t0) & (o.index <= t1)]
    out.append(dict(saat=r.t0.tz_convert(DISPLAY_TZ).strftime("%d.%m %H"), sinif=r.sinif, tur=r.tur, coin=r.coin, H=r.H, kap=k_,
                    net=round(r.yon * 100 * (p1 / c[r.t0] - 1) - 0.04, 2), en_iyi=round(100 * (w.high.max() / c[r.t0] - 1), 2) if len(w) else np.nan,
                    en_kotu=round(100 * (w.low.min() / c[r.t0] - 1), 2) if len(w) else np.nan, btc=round(100 * ((b.close[t1] if t1 in b.index else b.close.iloc[-1]) / b.close[r.t0] - 1), 2)))
Y = pd.DataFrame(out); pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500)
yaz(f"# Canlı olaylar — {now.tz_convert(DISPLAY_TZ):%d.%m %H:%M}\n")
for sn in ("ana", "yedek"):
    S = Y[(Y.sinif == sn) & Y.kap]
    g = S.groupby(["saat", "tur"]).agg(n=("net", "size"), tuttu=("net", lambda v: int((v > 0).sum())), ort_net=("net", "mean"), btc=("btc", "first"), H=("H", "first")).reset_index()
    yaz(f"## {sn}: {len(S)} kapanan sinyal · %{100 * (S.net > 0).mean():.0f} · ort net {S.net.mean():+.2f} → {g.saat.nunique()} ayrı saat (olay)")
    gs = S.groupby("saat").net.mean(); yaz(f"   olay bazında: {int((gs > 0).sum())}/{len(gs)} saat kârda · olay ortalaması {gs.mean():+.2f}")
    yaz("```"); yaz(g.round(2).to_string(index=False)); yaz("```")
yaz("## Tüm gönderilen satırlar\n```"); yaz(Y[Y.sinif != "panel"].to_string(index=False)); yaz("```")
P_ = Y[(Y.sinif == "panel") & Y.kap]; yaz(f"\n## panel: {len(P_)} kapanan · %{100 * (P_.net > 0).mean():.0f} · ort {P_.net.mean():+.2f}")
yaz("```"); yaz(P_.groupby("tur").net.agg(["size", lambda v: 100 * (v > 0).mean(), "mean"]).round(2).to_string()); yaz("```")
open("canli_olay_sonuc.md", "w").write("\n".join(L) + "\n")
