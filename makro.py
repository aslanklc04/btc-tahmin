# makro.py — PROTOKOL_makro.md (kod sonuçtan önce kaydedildi)
import sys, json, time, numpy as np, pandas as pd
sys.path.insert(0, "canli"); from ortak import fetch_1h
from concurrent.futures import ThreadPoolExecutor
T0 = time.time(); L = []; yaz = lambda s="": (print(s, flush=True), L.append(s))
MT = json.load(open("makro_tarih.json")); LS = json.load(open("sekil_liste.json"))
def utc(gun, saat, dk):
    t = pd.Timestamp(f"{gun} {saat:02d}:{dk:02d}", tz="America/New_York"); return t.tz_convert("UTC")
EV = {"FOMC": pd.DatetimeIndex([utc(g, 14, 0) for g in MT["fomc"]]), "CPI": pd.DatetimeIndex([utc(g, 8, 30) for g in MT["cpi"]])}
HER = EV["FOMC"].union(EV["CPI"])
def icerir(t, H, ev): t = pd.DatetimeIndex(t); i = ev.searchsorted(t, side="left"); ok = i < len(ev); out = np.zeros(len(t), bool); out[ok] = ev[i[ok]] <= t[ok] + pd.to_timedelta(np.asarray(H)[ok], unit="h"); return out
A25, A26, Y2, P0 = (pd.Timestamp(x, tz="UTC") for x in ("2025-01-01", "2026-01-01", "2023-07-01", "2022-06-01"))
yaz(f"# 🏛️ ABD makro olayları (FOMC · CPI) — PROTOKOL_makro.md · {pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M}\n")
# ---- M1 ----
D = pd.read_csv("karal2_veri.csv.gz"); D["t"] = pd.to_datetime(D.t, utc=True); X = D[["t", "nm", "sinif", "H", "B_T0"]].dropna(subset=["B_T0"]).copy()
X["olay"] = icerir(X.t, X.H, HER); SON = X.t.max() + pd.Timedelta(hours=1)
def olc(d):
    if len(d) == 0: return dict(n=0, ii=np.nan, si=np.nan, net=np.nan)
    sp = d.groupby("t").B_T0.mean(); return dict(n=len(d), ii=100 * (d.B_T0 > 0).mean(), si=100 * (sp > 0).mean(), net=100 * d.B_T0.mean())
def sart(o, b): return o["n"] >= 0.4 * b["n"] and o["ii"] >= b["ii"] - 0.5 and o["si"] >= b["si"] - 0.5 and o["net"] >= b["net"] + 0.03
DON = [("keşif ½-1", P0, Y2), ("keşif ½-2", Y2, A25), ("KONTROL 2025+", A25, SON), ("KONTROL 2026", A26, SON)]
yaz(f"## M1 — sinyalin tutma süresi FOMC/CPI açıklamasını içeriyor mu ({X.olay.mean() * 100:.1f}% sinyal olaylı)")
for sn in ["✅ ana (+0,75σ)", "🔸 yedek (+0,50σ)", "📋 panelden (+0,45σ)"]:
    d = X[X.sinif == sn]; sat = []; ok = True
    for dn, a, z in DON:
        x = d[(d.t >= a) & (d.t < z)]; b, f, ol = olc(x), olc(x[~x.olay]), olc(x[x.olay]); g = sart(f, b); ok &= g
        sat.append(f"{dn}: olaylı {ol['n']} · %{ol['ii']:.0f} · {ol['net']:+.2f} | olaysız %{f['ii']:.0f} · {f['net']:+.2f} | at → saat %{b['si']:.0f}→%{f['si']:.0f}, net {b['net']:+.3f}→{f['net']:+.3f} {'✅' if g else '❌'}")
    yaz(f"- **{sn}**: " + " ‖ ".join(sat) + f" → {'**GEÇTİ**' if ok else 'geçmedi'}")
# ---- M2 ----
def ohl(c):
    try: o = fetch_1h(pd.Timestamp("2022-04-01", tz="UTC").timestamp() * 1000, time.time() * 1000, sym=f"{c}USDT"); return c, o[["open", "high", "low", "close"]].astype(float)
    except Exception: return c, None
with ThreadPoolExecutor(10) as ex: OH = {c: o for c, o in ex.map(ohl, LS["A"] + LS["B"]) if o is not None}
yaz(f"\n## M2 — 4 saatlik pencerede ↕️ testere riski (fiyat: {len(OH)} coin)")
def testere(c):
    o = OH[c]; o.index = o.index - pd.Timedelta(hours=1)                                      # indeks = saat başlangıcı
    s = np.log(o.close).diff().rolling(720, min_periods=168).std().shift(1) * 2                  # σ_4s, pencere başında bilinen
    up = o.high[::-1].rolling(4, min_periods=4).max()[::-1] / o.open - 1; dn = 1 - o.low[::-1].rolling(4, min_periods=4).min()[::-1] / o.open
    ts = ((up >= s) & (dn >= s)).where(s.notna() & up.notna()); d = pd.DataFrame({"ts": ts}).dropna(); d = d[d.index >= P0]
    for k, ev in EV.items(): d[k] = icerir(d.index, np.full(len(d), 4), ev)
    d["g"] = "A" if c in LS["A"] else "B"; return d
T = pd.concat([testere(c) for c in OH]); T["don"] = np.where(T.index < A25, "kesif", "dog")
for k in EV:
    sat = []; ok = True
    for ad, m, esik in (("keşif", (T.g == "A") & (T.don == "kesif"), 1.3), ("2025+", (T.g == "A") & (T.don == "dog"), 1.15), ("dokunulmamış", T.g == "B", 1.15)):
        x = T[m]; p1, p0 = x[x[k]].ts.mean(), x[~x[k] & ~x[[e for e in EV if e != k]].any(axis=1)].ts.mean(); lift = p1 / p0; ok &= lift >= esik
        sat.append(f"{ad}: olaylı %{100 * p1:.1f} vs olaysız %{100 * p0:.1f} → ×{lift:.2f} {'✅' if lift >= esik else '❌'} (n {int(x[k].sum()):,})")
    yaz(f"- **{k}**: " + " | ".join(sat) + f" → {'**GEÇTİ**' if ok else 'geçmedi'}")
yaz(f"\n_5 deneme · süre {time.time() - T0:.0f} sn_")
open("makro_sonuc.md", "w").write("\n".join(L) + "\n")
