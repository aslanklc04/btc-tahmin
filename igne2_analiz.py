# igne2_analiz.py — PROTOKOL_igne2.md kararı → igne2_sonuc.md
import glob, io, zipfile, numpy as np, pandas as pd, requests
out = []; yaz = lambda s="": (out.append(s), print(s))
L_ = []
for f in sorted(glob.glob("parca/igne2-p-*/igne2_p*.csv.gz")):
    try: L_.append(pd.read_csv(f))
    except pd.errors.EmptyDataError: pass
R = pd.concat(L_, ignore_index=True); R["gun"] = pd.to_datetime(R.gun, utc=True)
eksik = sorted(set(sum([open(f).read().split() for f in glob.glob("parca/igne2-p-*/igne2_eksik_p*.txt")], [])))
# ---- BTC 200 gün trend (vadeli BTCUSDT günlük)
U = "https://data.binance.vision/data/futures/um"; S = requests.Session(); P = []
def al(u):
    for _ in range(5):
        try:
            r = S.get(u, timeout=60)
            if r.status_code == 200:
                z = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=[0, 4])
                return d[pd.to_numeric(d[0], errors="coerce").notna()].astype(float)
            if r.status_code == 404: return None
        except Exception: pass
    return None
for ay in pd.period_range("2021-08", "2026-09", freq="M").strftime("%Y-%m"):
    d = al(f"{U}/monthly/klines/BTCUSDT/1d/BTCUSDT-1d-{ay}.zip"); P += [d] if d is not None else []
for g in pd.date_range("2026-10-01", "2026-10-26").strftime("%Y-%m-%d"):
    d = al(f"{U}/daily/klines/BTCUSDT/1d/BTCUSDT-1d-{g}.zip"); P += [d] if d is not None else []
B = pd.concat(P); B[0] = B[0].where(B[0] < 1e14, B[0] / 1000); B["gun"] = pd.to_datetime(B[0], unit="ms", utc=True)
B = B.drop_duplicates("gun").set_index("gun")[4].sort_index()
ust = (B > B.rolling(200, min_periods=200).mean()).shift(1, freq="D")        # D günü için: D−1 kapanışı > 200 gün ort.
R["trend"] = R.gun.map(ust).fillna(False).astype(bool)
yaz("# 🪡 Günlük iğne emri + BTC 200 gün trend filtresi — PROTOKOL_igne2.md · Binance vadeli 1 dk")
yaz(f"{R.nm.nunique()} coin ({(R.groupby('nm').grup.first() == 'yeni').sum()} yeni) · veri bulunamayan: {len(eksik)} ({', '.join(eksik)}) · son gün {R.gun.max().date()}")
yaz(f"BTC trend üstü gün oranı: " + " · ".join(f"{y}: %{100 * ust[str(y)].mean():.0f}" for y in (2022, 2023, 2024, 2025, 2026)) + "\n")
DON = {"½-1": ("2022-06-01", "2023-07-01"), "½-2": ("2023-07-01", "2025-01-01"), "2025+": ("2025-01-01", "2027-01-01"), "2026": ("2026-01-01", "2027-01-01")}
def ol(b, st):
    x = b.dropna(subset=[st]); n = len(x)
    if not n: return dict(n=0)
    liq = int((x[st + "_mae"] <= -0.45).sum()) if st == "yok" else int((x[st + "_cik"] <= -0.45).sum())
    g = x.groupby("gun")[st].mean(); ay = n / max(b.gun.nunique() / 30.4, 1)
    return dict(n=n, i=100 * (x[st] > 0).mean(), net=100 * x[st].mean(), gi=100 * (g > 0).mean(), kotu=100 * x[st].min(), liq=liq, ay=ay)
f_ = lambda o: (f"{o['n']} · %{o['i']:.1f} · {o['net']:+.2f} · gün %{o['gi']:.0f} · {o['kotu']:+.1f} · liq {o['liq']} · ayda {o['ay']:.0f}" if o["n"] else "0")
KUR = [(d, st) for d in (3, 4) for st in ("yok", "S05", "S1")]
def tablo(b, karar):
    yaz("| Kural | " + " | ".join(DON) + (" | karar |" if karar else " |")); yaz("|---|" + "---|" * (len(DON) + (1 if karar else 0)))
    gec = []
    for d, st in KUR:
        x = b[b.d == d]; oo = {dn: ol(x[(x.gun >= pd.Timestamp(a, tz="UTC")) & (x.gun < pd.Timestamp(z, tz="UTC"))], st) for dn, (a, z) in DON.items()}
        ok = all(o["n"] >= (15 if dn == "2026" else 30) and o["i"] >= 70 and o["net"] >= 0.20 and o["gi"] >= 65 and o["liq"] == 0 for dn, o in oo.items() if True) if all(o["n"] for o in oo.values()) else False
        if ok: gec.append((min(o["net"] for o in oo.values()), (d, st)))
        yaz(f"| d{d} stop {st} | " + " | ".join(f_(o) for o in oo.values()) + (f" | {'✅' if ok else '❌'} |" if karar else " |"))
    return gec
yaz("_hücre: işlem · işlem isabeti · işlem başı net % · gün isabeti · en kötü işlem % · 2x likidasyon · ayda işlem_\n")
yaz("## KARAR — 126 yeni coin, trend filtreli")
gec = tablo(R[(R.grup == "yeni") & R.trend], True)
if gec: k = max(gec)[1]; yaz(f"\n**✅ GEÇTİ: d{k[0]} stop {k[1]}** (geçenler: {', '.join(f'd{a} {b}' for _, (a, b) in sorted(gec, reverse=True))})")
else: yaz("\n**❌ Hiçbir kural dört dönemde de şartı sağlamadı.**")
yaz("\n## Bilgi — 126 yeni coin, FİLTRESİZ"); tablo(R[R.grup == "yeni"], False)
yaz("\n## Bilgi — 15 eski coin (igne'de görüldü), trend filtreli"); tablo(R[(R.grup == "eski") & R.trend], False)
yaz("\n## Bilgi — 10.10.2025 (çöküş günü), yeni coin'ler")
x = R[(R.gun == pd.Timestamp("2025-10-10", tz="UTC")) & (R.grup == "yeni")]
yaz(f"trend filtresi o gün: {'açık (emir konurdu)' if bool(ust.get(pd.Timestamp('2025-10-10', tz='UTC'), False)) else 'kapalı'}")
for d, st in KUR:
    o = ol(x[x.d == d], st); yaz(f"- d{d} stop {st}: " + f_(o))
open("igne2_sonuc.md", "w").write("\n".join(out) + "\n")
