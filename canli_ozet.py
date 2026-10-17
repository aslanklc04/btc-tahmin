# canli_ozet.py — modelin canlıya geçtiğinden beri İÇ ölçüm günlüklerinin (önbellekler) toplamı: her kaynak / tür için kapanan · tutan · isabet · ort. sonuç (yalnız bilgi, 17.10.2026)
import pandas as pd, numpy as np, os
L = []
def yaz(s=""): print(s); L.append(s)
def bul(o, yol=""):
    if isinstance(o, list) and o and isinstance(o[0], dict) and any("ok" in e for e in o): yield yol, o
    elif isinstance(o, dict):
        for k, v in o.items(): yield from bul(v, f"{yol}/{k}")
KAY = {"durum/gecmis.pkl": "₿ BTC modeli", "durum/gecmis_coin.pkl": "🪙 altcoin modelleri (🤝/🔇/🪙 tüm sinyaller)", "durum/gecmis24.pkl": "🧪 24 saat",
       "durum/prim.pkl": "💵 ABD alıyor", "durum/zincir.pkl": "⛓️ ETH arz/talep", "durum/kucuk.pkl": "🧑 küçük yatırımcı"}
yaz(f"# Canlı iç ölçüm — {pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M}\n")
TOP = []
for f, ad in KAY.items():
    if not os.path.exists(f): yaz(f"- {ad}: önbellek yok"); continue
    try: o = pd.read_pickle(f)
    except Exception as e: yaz(f"- {ad}: okunamadı {e}"); continue
    rows = []
    for yol, lst in bul(o):
        for e in lst:
            if "ok" not in e: continue
            r = e.get("ret", e.get("net", np.nan))
            rows.append(dict(t=pd.Timestamp(e["t"]), tip=str(e.get("tip", yol)), ok=bool(e["ok"]), r=float(r) if r is not None else np.nan))
    if not rows: yaz(f"- **{ad}**: sonuçlanan yok"); continue
    D = pd.DataFrame(rows); bas = D.t.min()
    r_ = D.r.mean()
    yaz(f"## {ad} — {bas:%d.%m.%Y} tarihinden beri: {len(D)} kapandı · {int(D.ok.sum())} tuttu (%{100 * D.ok.mean():.0f}) · ort. sonuç %{r_:+.2f}")
    g = D.groupby("tip").agg(n=("ok", "size"), tut=("ok", "sum"), isb=("ok", "mean"), r=("r", "mean")).sort_values("n", ascending=False)
    for tip, x in g.head(15).iterrows(): yaz(f"   - {tip[:60]}: {int(x.n)} · {int(x.tut)} tuttu (%{100 * x.isb:.0f}) · ort %{x.r:+.2f}")
    son = D[D.t >= D.t.max() - pd.Timedelta(days=7)]; yaz(f"   - son 7 gün: {len(son)} · %{100 * son.ok.mean():.0f}")
    TOP.append(D.assign(kaynak=ad))
if TOP:
    A = pd.concat(TOP); yaz(f"\n**HEPSİ:** {len(A)} kapandı · {int(A.ok.sum())} tuttu (%{100 * A.ok.mean():.0f})")
open("canli_ozet_sonuc.md", "w").write("\n".join(L) + "\n")
