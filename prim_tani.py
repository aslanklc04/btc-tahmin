# prim_tani.py — TEŞHİS (18.10.2026, yalnız bilgi): canlı mesajdaki coin primi z'si neden araştırmadakinden farklı çıktı?
# Varsayım: canlı ortak.cb_prim son Coinbase mumu yoksa 3 saate kadar ESKİ z'yi kullanıyor; testte o saat NaN → sinyal yok.
# Her canlı sinyal için: t anında Coinbase mumu var mı, hacmi, z(t−k) k=0..3 ve mesajdaki z'ye en yakın k. + geniş listede mum eksikliği sıklığı.
import re, time, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import fetch_1h, DISPLAY_TZ
L = []
def yaz(s=""): print(s, flush=True); L.append(str(s))
NOW = pd.Timestamp.now(tz="UTC"); UA = {"User-Agent": "btc-tahmin-tani"}
def cb(nm, a, b):
    out, cur = [], a
    while cur < b:
        nx = min(cur + pd.Timedelta(hours=300), b)
        for k in range(4):
            try:
                r = requests.get(f"https://api.exchange.coinbase.com/products/{nm}-USD/candles", params=dict(granularity=3600, start=cur.isoformat(), end=nx.isoformat()), headers=UA, timeout=20)
                if r.status_code == 404: return None
                if r.status_code == 200: out += r.json(); break
            except Exception: pass
            time.sleep(1 + k)
        cur = nx; time.sleep(0.15)
    if not out: return None
    d = pd.DataFrame(out, columns=["t", "low", "high", "open", "close", "volume"]).drop_duplicates("t")
    d.index = pd.to_datetime(d.t, unit="s", utc=True) + pd.Timedelta(hours=1); return d.sort_index()
K = pd.read_csv("canli/durum/karne_kayit.csv"); K = K[K.s != "panel"]; R = []
for _, r in K.iterrows():
    t = pd.Timestamp(r.t, tz=DISPLAY_TZ).floor("h").tz_convert("UTC")
    for nm, zv in re.findall(r"([A-Z0-9]{2,10}) \(z ([+\-−]?\d+\.\d)", r.e): R.append((t, nm, float(zv.replace("−", "-")), r.s))
    m = re.search(r"([A-Z0-9]{2,10}) .*?prim ✅ z ([+-]?\d+\.\d)", r.e)
    if m: R.append((t, m.group(1), float(m.group(2)), r.s))
R = pd.DataFrame(R, columns=["t", "nm", "z_mesaj", "s"])
GEN = [l.strip()[:-4] for l in open("canli/durum/genis_liste.txt") if l.strip()]
def veri(nm):
    try:
        c = cb(nm, NOW - pd.Timedelta(days=120), NOW); b = fetch_1h((NOW - pd.Timedelta(days=120)).timestamp() * 1000, NOW.timestamp() * 1000, sym=f"{nm}USDT")
        if c is None: return nm, None
        ix = b.index[b.index >= c.index[0]]; p = np.log(c.close.reindex(ix) / b.close.reindex(ix))
        z = (p - p.rolling(720, min_periods=168).mean()) / (p.rolling(720, min_periods=168).std() + 1e-12)
        return nm, dict(c=c, z=z, ix=ix)
    except Exception as e: print(nm, e); return nm, None
with ThreadPoolExecutor(4) as ex: V = dict(ex.map(veri, sorted(set(R.nm) | set(GEN))))
out = []
for r in R.itertuples():
    d = V.get(r.nm)
    if d is None: out.append(dict(mum_t=None)); continue
    zs = {k: float(d["z"].get(r.t - pd.Timedelta(hours=k), np.nan)) for k in range(4)}
    kb = min(zs, key=lambda k: abs(zs[k] - r.z_mesaj) if np.isfinite(zs[k]) else 99)
    out.append(dict(mum_t=r.t in d["c"].index, hacim_usd=round(float(d["c"].volume.get(r.t, 0) * d["c"].close.get(r.t, np.nan)), 0) if r.t in d["c"].index else 0,
                    z0=round(zs[0], 2), z1=round(zs[1], 2), z2=round(zs[2], 2), z3=round(zs[3], 2), en_yakin_k=kb, fark=round(r.z_mesaj - zs[kb], 2) if np.isfinite(zs[kb]) else np.nan))
R = pd.concat([R.reset_index(drop=True), pd.DataFrame(out)], axis=1); R["t"] = R.t.dt.tz_convert(DISPLAY_TZ).dt.strftime("%d.%m %H")
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 300)
yaz(f"# 🔬 Prim teşhisi — {NOW.tz_convert(DISPLAY_TZ):%d.%m %H:%M}\n")
ok0 = (R.z_mesaj - R.z0).abs() <= 0.2
yaz(f"- {len(R)} coin-sinyal · mesajdaki z = aynı saatin z'si (±0,2): {int(ok0.sum())} · farklı: {int((~ok0).sum())}")
yaz(f"- farklı olanlarda t saatinde Coinbase mumu YOK: {int(((~ok0) & (R.mum_t == False)).sum())} · var: {int(((~ok0) & (R.mum_t == True)).sum())} · en yakın eski saat (k≥1, ±0,2): {int(((~ok0) & (R.en_yakin_k >= 1) & (R.fark.abs() <= 0.2)).sum())}")
yaz("```"); yaz(R[~ok0].to_string(index=False)); yaz("```")
yaz("\n## Mum eksikliği: geniş liste + sinyal coin'leri, son 120 gün (canlıda 'eski z' riski)")
rows = []
for nm, d in V.items():
    if d is None: continue
    ix = d["ix"]; ix = ix[ix >= ix[0] + pd.Timedelta(days=31)]; var = ix.isin(d["c"].index)
    rows.append(dict(coin=nm, saat=len(ix), mum_yok_yuzde=round(100 * (1 - var.mean()), 1), med_hacim_usd=round(float((d["c"].volume * d["c"].close).median()), 0)))
M = pd.DataFrame(rows).sort_values("mum_yok_yuzde", ascending=False)
yaz(f"- {len(M)} coin · mum eksik saat oranı medyan %{M.mum_yok_yuzde.median():.1f} · > %5 olan coin: {int((M.mum_yok_yuzde > 5).sum())} · > %20: {int((M.mum_yok_yuzde > 20).sum())}")
yaz("```"); yaz(M.head(40).to_string(index=False)); yaz("```")
open("prim_tani_sonuc.md", "w").write("\n".join(L) + "\n")
