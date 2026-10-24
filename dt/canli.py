# dt/canli.py — BAĞIMSIZ DENETİM: durum/karne_kayit.csv'deki CANLI sinyallerin gerçek sonucu (Binance 1 dk mum), yalnız ölçüm.
# Giriş: (T) test/karne yöntemi = sinyal saati kapanışı · (M) mesajdaki giriş fiyatı (🤝/🔇/🪙 = saat kapanışı [kodda böyle];
#        🧪/💵 = panel geçmişinden okunan gerçek mesaj fiyatı) · (P) mesaj gönderildiği dakikada piyasa alışı.
# Çıkış: 🎯 hedef (mesajdaki biçimde yuvarlanmış) 1 dk YÜKSEK'e değerse orada, değmezse mesajdaki çıkış saatinde (sinyal saati + H + 6 dk) 1 dk kapanış.
import os, re, sys, time, pickle, glob, numpy as np, pandas as pd, requests
from concurrent.futures import ThreadPoolExecutor
TR = "Europe/Istanbul"; L = []
def yaz(s=""): print(s, flush=True); L.append(s)
V = {}
for f in sorted(glob.glob("dveri/**/veri_*.pkl", recursive=True)): V.update(pickle.load(open(f, "rb")))
BNH = {s: d["bn"] for s, d in V.items() if d["bn"] is not None}
GEN = {l.strip()[:-4] for l in open("dt/genis.txt") if l.strip()}
PA = pd.read_csv("canli/durum/prim_acik.csv")
K = pd.read_csv("canli/durum/karne_kayit.csv", dtype=str).fillna("")
GIR = {}
for l in open("dt/girisler.txt"):
    c, p, ex = l.split(None, 2); GIR[(c, ex.strip())] = float(p.replace(",", ""))
CRE = re.compile(r"([A-Z0-9]{2,12}) \((?:z ([+-]?[\d.]+)[^)]*|prim yok[^)]*)\)")
def coz(e, sure):
    if e.startswith("🤝"): return [(m.group(1), 4, "🌐🤝" if m.group(1) in GEN else "🤝", float(m.group(2)) if m.group(2) else np.nan) for m in CRE.finditer(e.split(":", 1)[1])]
    if e.startswith("🧪"): return [(m.group(1), 24, "🌐🧪" if m.group(1) in GEN else "🧪", float(m.group(2)) if m.group(2) else np.nan) for m in CRE.finditer(e.split(":", 1)[1])]
    if "💵 ABD" in e:
        out = []
        for m in re.finditer(r"([A-Z0-9]{2,12}) \(z ([+-]?[\d.]+)(?:, (\d+) saat)?\)", e.split(":", 1)[1]):
            H = int(m.group(3)) if m.group(3) else (int(PA[PA.coin == m.group(1)].saat.iloc[0]) if (PA.coin == m.group(1)).any() else (int(sure) if sure else 24))
            out.append((m.group(1), H, "💵", float(m.group(2))))
        return out
    m = re.match(r"^(\S+) ([A-Z0-9]{2,12}) .*?· (\d+) saat", e)
    zz = re.search(r"prim \S+ z ([+-]?[\d.]+)", e); zz = float(zz.group(1)) if zz else np.nan
    if m and not e.startswith("₿") and not e.startswith("🔻"): return [(m.group(2), int(m.group(3)), "🔀" if "🔀" in m.group(1) else "🔇/🪙", zz)]
    m = re.match(r"^(🪙|🔇)\S* ([A-Z0-9]{2,12}) (.*?) ·", e)
    if m: return [(m.group(2), 8 if "⭐" in m.group(3) else 4, "🔇/🪙", zz)]
    return []
def sinif(s, k):
    if not k.startswith("gönderildi"): return "gitmedi"
    if "📋" in s: return "panelden"
    if s.startswith("✅"): return "ana"
    if s.startswith("🔸"): return "yedek"
    return "?"
def simdiki(tur, z):                                                       # BUGÜNKÜ kurallarla sınıf (yalnız prim; 📉🔥/🚀/💧/🔥 işaretleri etiketten bilinmez)
    if tur == "🌐🤝": return "ana" if z >= 2 else ("yedek" if z >= 0 else "düşer")
    if tur == "🤝": return "ana" if z >= 0 else "panel"
    if tur == "🌐🧪": return "ana" if z >= 1.5 else "düşer"
    if tur in ("🧪", "💵", "🔇/🪙"): return "panelden" if (np.isfinite(z) and z >= 0) or tur == "💵" else "panel"
    if tur == "🔀": return "ana"
    return "?"
rows = []
for r in K.itertuples():
    ts = pd.Timestamp(r.t, tz=TR); t0 = ts.floor("h").tz_convert("UTC")
    for nm, H, tur, z in coz(r.e, r.sure):
        rows.append(dict(ts=ts.tz_convert("UTC"), t0=t0, coin=nm, H=H, tur=tur, z=z, sinif=sinif(r.s, r.k), s=r.s, isr=r.isr))
X = pd.DataFrame(rows).drop_duplicates(["t0", "coin", "H", "tur"]).reset_index(drop=True)
yaz(f"# Canlı karne denetimi — {pd.Timestamp.now(tz=TR):%d.%m.%Y %H:%M}")
yaz(f"_karne_kayit.csv: {len(K)} satır → {len(X)} coin-sinyal (BTC ₿/🔻 panel satırları hariç) · gönderilen: " + ", ".join(f"{k} {v}" for k, v in X[X.sinif != 'gitmedi'].sinif.value_counts().items()) + "_\n")
def k1m(sym, a, b):
    rows_, cur = [], int(a.timestamp() * 1000); end = int(b.timestamp() * 1000); s = requests.Session()
    while cur < end:
        d = None
        for k in range(4):
            try:
                rr = s.get("https://data-api.binance.vision/api/v3/klines", params=dict(symbol=sym, interval="1m", startTime=cur, endTime=end, limit=1000), timeout=20)
                if rr.status_code == 200: d = rr.json(); break
            except Exception: pass
            time.sleep(1 + k)
        if not d: break
        rows_ += d; cur = d[-1][0] + 60_000
        if len(d) < 1000: break
    if not rows_: return None
    m = pd.DataFrame([x[:5] for x in rows_], columns=["t", "o", "h", "l", "c"]).astype(float); m.index = pd.to_datetime(m.t.astype("int64"), unit="ms", utc=True); return m
def fy(p):                                                                  # ortak.fiyat_yaz ile aynı yuvarlama (mesajda görünen fiyat)
    if p >= 1000: return round(p)
    if p >= 1: return round(p, 3)
    return round(p, min(12, 3 - int(np.floor(np.log10(p)))))
def hedef(p, sg, H, k):
    pct = round(100 * 0.75 * sg * np.sqrt(H), 1)                             # üretici 0,75σ yazar (+%x.x), gonder.py yedek/panelden için katsayıyla çevirir
    if k == 0.75: return fy(p * (1 + 0.75 * sg * np.sqrt(H)))
    return fy(p * (1 + pct * k / 0.75 / 100))
KK = {"ana": 0.75, "yedek": 0.50, "panelden": 0.45}
NOW = pd.Timestamp.now(tz="UTC")
def one(r):
    sym = r.coin + "USDT"; h = BNH.get(sym)
    if h is None: return None
    t0, H = r.t0, int(r.H); t1 = t0 + pd.Timedelta(hours=H); ex_t = t1 + pd.Timedelta(minutes=6)
    if ex_t + pd.Timedelta(minutes=2) > NOW or t0 not in h.index: return dict(acik=True)
    c = h.c; sg = np.log(c[c.index <= t0]).diff().dropna().iloc[-720:].std()
    m = k1m(sym, t0 - pd.Timedelta(minutes=1), ex_t + pd.Timedelta(minutes=2))
    if m is None or len(m) < H * 50: return None
    pT = float(c[t0])
    exr = (t0 + pd.Timedelta(hours=H)).tz_convert(TR).strftime("%d.%m %H:%M")
    if r.tur in ("🧪", "🌐🧪", "💵"):
        pM = GIR.get((r.coin, exr)); kay = "panel kaydı" if pM else "≈ +4 dk 1 dk kapanışı"
        if pM is None:
            q = m[m.index == t0 + pd.Timedelta(minutes=3)]; pM = float(q.c.iloc[0]) if len(q) else pT
    else: pM, kay = pT, "saat kapanışı (kod)"
    q = m[m.index == r.ts.floor("min")]; pP = float(q.c.iloc[0]) if len(q) else np.nan
    out = dict(acik=False, pT=pT, pM=pM, pP=pP, kay=kay, sg=sg)
    def run(t_in, p_in, tgt, t_out):
        w = m[(m.index >= t_in) & (m.index < t_out)]
        if not len(w): return np.nan, False
        if tgt is not None and np.isfinite(tgt) and (w.h.values >= tgt).any(): return 100 * (tgt / p_in - 1), True
        return 100 * (float(m[m.index < t_out].c.iloc[-1]) / p_in - 1), False
    k = KK.get(r.sinif) or {"ana": 0.75, "yedek": 0.50, "panelden": 0.45}.get(simdiki(r.tur, r.z), 0.75)
    tgtT = pT * (1 + k * sg * np.sqrt(H)); tgtM = hedef(pM, sg, H, k)
    hT = h.h[(h.index > t0) & (h.index <= t1)]                               # karne yöntemi: saatlik yüksek, sinyal saatinden sonraki mumlar
    out["karne_end"] = 100 * (float(c.get(t1, np.nan)) / pT - 1)
    out["karne_tp"] = 100 * (tgtT / pT - 1) if (hT >= tgtT).any() else out["karne_end"]
    out["M_tp"], out["M_hit"] = run(r.ts.floor("min") + pd.Timedelta(minutes=1), pM, tgtM, ex_t)   # mesajdaki fiyattan (dolduğu varsayımıyla), mesajdan sonra
    out["M_end"], _ = run(r.ts.floor("min") + pd.Timedelta(minutes=1), pM, None, ex_t)
    out["P_tp"], out["P_hit"] = run(r.ts.floor("min") + pd.Timedelta(minutes=1), pP, tgtM, ex_t) if np.isfinite(pP) else (np.nan, False)
    w = m[(m.index >= r.ts.floor("min")) & (m.index < r.ts.floor("min") + pd.Timedelta(minutes=60))]   # limit emir (mesaj fiyatı) 60 dk içinde doldu mu
    f = w.index[w.l.values <= pM]; out["dolar"] = bool(len(f)); out["once_ucuz"] = bool(len(w) and w.o.iloc[0] <= pM)
    if len(f):
        t_in = f[0] + pd.Timedelta(minutes=1); p_in = min(pM, float(w.o.iloc[0])) if out["once_ucuz"] else pM
        out["L_tp"], out["L_hit"] = run(t_in, p_in, tgtM, ex_t)
    else: out["L_tp"], out["L_hit"] = np.nan, False
    out["hedef_pct"] = 100 * (tgtM / pM - 1); out["k"] = k
    return out
with ThreadPoolExecutor(10) as ex: RES = list(ex.map(one, [r for r in X.itertuples()]))
X["res"] = RES; X = X[X.res.notna()]; X = X[[not r["acik"] for r in X.res]].copy()
for key in ("pT", "pM", "pP", "karne_end", "karne_tp", "M_tp", "M_hit", "M_end", "P_tp", "P_hit", "dolar", "L_tp", "L_hit", "hedef_pct", "kay", "k"):
    X[key] = [r.get(key) for r in X.res]
X = X.drop(columns="res"); X["sim"] = [simdiki(t, z) for t, z in zip(X.tur, X.z)]
X.to_csv("dt/canli_olaylar.csv", index=False)
def blok(G, ad):
    if not len(G): return
    nh = G.t0.nunique(); hr = G.groupby("t0").agg(**{c: (c, "mean") for c in ("karne_tp", "M_tp", "P_tp", "M_end")})
    f = lambda v, c: f"%{100 * (np.asarray(v, float)[np.isfinite(np.asarray(v, float))] - c > 0).mean():.0f}"
    m_ = lambda v, c: f"{np.nanmean(np.asarray(v, float)) - c:+.2f}"
    yaz(f"**{ad}** — {len(G)} coin-sinyal, {nh} ayrı saat (mesaj)")
    yaz(f"  - karne/test yöntemi (giriş saat kapanışı, 🎯 saatlik yüksek, maliyet 0,04): isabet {f(G.karne_tp, 0.04)} · net {m_(G.karne_tp, 0.04)} | süre sonu {f(G.karne_end, 0.04)} · {m_(G.karne_end, 0.04)}")
    yaz(f"  - mesaj fiyatı + mesajdaki 🎯 (1 dk), çıkış +6 dk: maliyet 0,04 → {f(G.M_tp, 0.04)} · {m_(G.M_tp, 0.04)} | maliyet 0,20 → {f(G.M_tp, 0.20)} · {m_(G.M_tp, 0.20)} · 🎯'e değen %{100*G.M_hit.mean():.0f} (hedef ort. +%{G.hedef_pct.mean():.2f})")
    yaz(f"  - mesaj anında piyasa alışı + aynı 🎯: maliyet 0,20 → {f(G.P_tp, 0.20)} · {m_(G.P_tp, 0.20)} · mesaj fiyatına göre giriş farkı ort. {100*np.nanmean(G.pP / G.pM - 1):+.2f}%")
    d = G[G.dolar.astype(bool)]
    yaz(f"  - mesaj fiyatından LİMİT (60 dk): dolan %{100*G.dolar.astype(bool).mean():.0f} · dolanlarda maliyet 0,20 → {f(d.L_tp, 0.20) if len(d) else '—'} · {m_(d.L_tp, 0.20) if len(d) else '—'}")
    yaz(f"  - saat-kümeli (aynı mesajdaki coin'ler tek gözlem): karne yöntemi {f(hr.karne_tp, 0.04)} · mesaj+🎯 maliyet 0,20 {f(hr.M_tp, 0.20)} · net {m_(hr.M_tp, 0.20)} ({nh} saat)")
yaz("## Gönderilen sinyaller (gönderildiği andaki sınıf)")
yaz("_🎯 = bugünkü sınıf hedefi (✅ +0,75σ · 🔸 +0,50σ · 📋 +0,45σ), karne de geçmişe böyle uygular; 21.10 öncesi mesajlarda 🎯 satırı YOKTU (o mesajlar için 'süre sonu' satırı geçerli)._\n")
for sn in ("ana", "yedek", "panelden"): blok(X[X.sinif == sn], {"ana": "✅ ana", "yedek": "🔸 yedek", "panelden": "🔸 yedek · 📋 panelden"}[sn])
for (sn, tur), G in X[X.sinif != "gitmedi"].groupby(["sinif", "tur"]):
    if len(G) >= 3: blok(G, f"  ↳ {sn} · {tur}")
yaz("\n## Bugünkü kurallarla (yalnız prim z'sine göre yeniden sınıflanmış; gönderilmemiş panel satırları dahil)")
for sn in ("ana", "yedek", "panelden"): blok(X[X.sim == sn], f"bugünkü kural · {sn}")
yaz("\n## Kural konduktan SONRA gelen sinyaller (seçimden sonraki veri)")
for ad, t_, m_ in (("🔸 yedek = 🌐🤝 eşik altı (16.10 18:09 UTC)", pd.Timestamp("2026-10-16 18:09", tz="UTC"), X.sim == "yedek"),
                   ("🎯 sınıf hedefleri (22.10 20:05 UTC) · gönderilen hepsi", pd.Timestamp("2026-10-22 20:05", tz="UTC"), X.sinif != "gitmedi"),
                   ("✅ ana 🎯 0,75σ (21.10 06:47 UTC)", pd.Timestamp("2026-10-21 06:47", tz="UTC"), X.sinif == "ana")):
    blok(X[m_ & (X.ts >= t_)], ad)
# rastgele giriş tabanı (canlı dönem): geniş liste coin'leri, tüm saatler, 4 saat, 🎯 0,50σ, saatlik yöntem
yaz("\n## Rastgele giriş tabanı — canlı dönemde (12.10 → bugün), geniş liste coin'leri, her saat giriş, 4 saat, saatlik yöntem, maliyet 0,04")
for k in (0.75, 0.50, 0.45):
    hits, nets = [], []
    for s in GEN:
        h = BNH.get(s + "USDT")
        if h is None: continue
        h = h.reindex(pd.date_range(h.index[0], h.index[-1], freq="1h", tz="UTC")); c = h.c
        sg = np.log(c).diff().rolling(720, min_periods=168).std(); fmax = h.h.shift(-1).rolling(4).max().shift(-3)
        tr = k * sg * np.sqrt(4); ret = np.where(fmax >= c * (1 + tr), tr, c.shift(-4) / c - 1)
        ret = pd.Series(ret, index=c.index)[(c.index >= pd.Timestamp("2026-10-12", tz="UTC"))].dropna() * 100 - 0.04
        hits += list(ret > 0); nets += list(ret)
    yaz(f"- 🎯 {k}σ: {len(hits)} giriş · isabet %{100*np.mean(hits):.0f} · net {np.mean(nets):+.2f}")
open("dt/canli_sonuc.md", "w").write("\n".join(L) + "\n")
