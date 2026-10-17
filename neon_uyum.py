# neon_uyum.py — 💧 Neon (Frankfurt, dakikalık) ölçümü ↔ Binance arşivi (bookDepth ±1, saatlik ortalama) uyumu. Ölçütler: neon_derinlik/UYUM_KARARI.md (önceden yazıldı; Ek 2: ≥ 72 saat, U4, U5, kapsam).
# Hizalama: Neon /saat?h=H → H:00–H:59 örnekleri; arşiv saatlik ortalaması t = tavan(saat) → aynı aralık arşivde t = H+1.
import io, os, zipfile, time, json, requests, numpy as np, pandas as pd, re
from concurrent.futures import ThreadPoolExecutor
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
U = "https://br-still-union-baibtf1k-derinlik.compute.c-8.eu-central-1.aws.neon.tech"
src = open("neon_derinlik/index.ts").read()
SEMB = dict(re.findall(r"'?([A-Z0-9]+)'?: '([A-Z0-9]+USDT)'", src)); SEMB.pop("BTC", None); SEMB.pop("ETH", None)   # BTC/ETH kapsam yetersiz
S = requests.Session()
def gun(arg):
    nm, g = arg; sym = SEMB[nm]
    for k in range(3):
        try:
            r = S.get(f"https://data.binance.vision/data/futures/um/daily/bookDepth/{sym}/{sym}-bookDepth-{g}.zip", timeout=40)
            if r.status_code == 404: return nm, None
            if r.status_code != 200: time.sleep(1 + k); continue
            z_ = zipfile.ZipFile(io.BytesIO(r.content)); d = pd.read_csv(z_.open(z_.namelist()[0])); d.columns = [c.strip().lower() for c in d.columns]
            if "percentage" not in d.columns: d = pd.read_csv(z_.open(z_.namelist()[0]), header=None, names=["timestamp", "percentage", "depth", "notional"])
            d = d[pd.to_numeric(d.percentage, errors="coerce").isin([1, -1])].copy(); d["t"] = pd.to_datetime(d.timestamp, utc=True).dt.ceil("h")
            d["notional"] = d.notional.astype(float); return nm, d.groupby(["t", "percentage"]).notional.mean().unstack().sum(axis=1)
        except Exception: time.sleep(1 + k)
    return nm, None
bugun = pd.Timestamp.now(tz="UTC").floor("D"); GUNLER = [x.strftime("%Y-%m-%d") for x in pd.date_range(bugun - pd.Timedelta(days=36), bugun, freq="D")]
with ThreadPoolExecutor(24) as ex: R = list(ex.map(gun, [(nm, g) for nm in SEMB for g in GUNLER]))
AR = {}
for nm, s in R:
    if s is not None: AR.setdefault(nm, []).append(s)
AR = {nm: pd.concat(v).groupby(level=0).mean().sort_index() for nm, v in AR.items()}
son_arsiv = max(v.index.max() for v in AR.values())
yaz(f"# 💧 Neon ↔ Binance arşivi uyumu — {pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M}\nArşivde son saat: {son_arsiv} · arşivi gelen coin: {len(AR)} · {time.time()-T0:.0f} sn")
# Neon saatleri
NE, NN = {}, {}
CEK = set(re.findall(r"'?([A-Z0-9]+)'?: '[A-Z0-9]+USDT'", src[src.index('COINS'):src.index('EK')]))
saatler = pd.date_range(pd.Timestamp("2026-10-12 16:00", tz="UTC"), son_arsiv - pd.Timedelta(hours=1), freq="1h")
def ns(H):
    for k in range(3):
        try: return H, S.get(f"{U}/saat", params={"h": H.strftime("%Y%m%d%H")}, timeout=120).json()
        except Exception: time.sleep(3)
    return H, None
with ThreadPoolExecutor(6) as ex:
    for H, d in ex.map(ns, saatler):
        if not d: continue
        for nm, v in d.get("coins", {}).items():
            if v.get("n", 0) >= 10: NE.setdefault(nm, {})[H + pd.Timedelta(hours=1)] = v["bid1"] + v["ask1"]
            NN.setdefault(nm, {})[H + pd.Timedelta(hours=1)] = v.get("n", 0)
KAYIT_F = "neon_derinlik/neon_saat_kayit.pkl"                                                # 17.10: Neon yalnız son 72 saati tutuyor, arşiv ~1,5 gün geride → ortak saat 72'ye ulaşamıyordu. Çekilen saatler kalıcı kaydedilir, birleştirilir.
try:
    ESKI = pd.read_pickle(KAYIT_F)
    for nm, dd in ESKI.get("NE", {}).items():
        for t_, v_ in dd.items(): NE.setdefault(nm, {}).setdefault(t_, v_)
    for nm, dd in ESKI.get("NN", {}).items():
        for t_, v_ in dd.items(): NN.setdefault(nm, {}).setdefault(t_, v_)
except Exception as e: print("Neon kaydı yok/okunamadı:", e)
pd.to_pickle({"NE": NE, "NN": NN}, KAYIT_F)
yaz(f"Neon saat (istenen): {len(saatler)} · Neon verisi olan coin: {len(NE)} · kayıtla birlikte coin başına en çok {max((len(v) for v in NE.values()), default=0)} saat\n")
rows, HAV = [], []
MINS = int(os.environ.get("NEON_ARA", "72"))                                                 # NEON_ARA: ara kontrol (karar değil)
ARA = "NEON_ARA" in os.environ
for nm in sorted(set(NE) & set(AR)):
    a = AR[nm]; la = np.log(a.where(a > 0)); m720, s720 = la.rolling(720, min_periods=168).mean().shift(1), la.rolling(720, min_periods=168).std().shift(1)
    n = pd.Series(NE[nm]).sort_index(); ix = n.index.intersection(a.index)
    if len(ix) < MINS: rows.append((nm, len(ix), np.nan, np.nan, np.nan, np.nan, np.nan, "az saat")); continue
    ln, la_ = np.log(n[ix]), la[ix]; zn = (ln - m720[ix]) / s720[ix]; za = (la_ - m720[ix]) / s720[ix]
    kor = ln.corr(la_); fark = (ln - la_).abs().median(); zf = (zn - za).abs().median(); uy = ((zn <= -2) != (za <= -2)).mean()
    ok = kor >= 0.75 and fark <= 0.10 and zf <= 0.25 and uy <= 0.02
    bek = 60 if nm in CEK else 30; kap = pd.Series(NN.get(nm, {})).reindex(ix).fillna(0).sum() / (bek * len(ix)); ok = ok and kap >= 0.90
    HAV.append(pd.DataFrame({"coin": nm, "t": ix, "ln": ln.values, "la": la_.values, "zn": zn.values, "za": za.values}))
    rows.append((nm, len(ix), kor, fark, zf, uy, kap, "✅" if ok else "❌"))
T = pd.DataFrame(rows, columns=["coin", "saat", "U1 kor", "U2 |log fark| med", "U3 |z fark| med", "U3 LD uyuşmazlık", "kapsam", "sonuç"])
pd.set_option("display.width", 200); pd.set_option("display.max_rows", 300)
yaz("```\n" + T.round(3).to_string(index=False) + "\n```")
d = T[T["saat"] >= MINS]; ilk13 = d[d.coin.isin(["ADA", "APT", "ARB", "BNB", "DOGE", "DOT", "FLOKI", "LINK", "NEAR", "OP", "PEPE", "SHIB", "SUI"])]
U1g = len(ilk13) >= 10 and ilk13["U1 kor"].median() >= 0.90 and (ilk13["U1 kor"] >= 0.75).all()
yaz(f"\nİlk 13 coin: {len(ilk13)} değerlendirildi · U1 korelasyon medyanı {ilk13['U1 kor'].median():.3f} · U2 medyan {ilk13['U2 |log fark| med'].median():.3f} · "
    f"U3 z farkı medyanı {ilk13['U3 |z fark| med'].median():.3f} · LD uyuşmazlık {ilk13['U3 LD uyuşmazlık'].mean():.3%}")
uyan = d[d["sonuç"] == "✅"].coin.tolist()
# U4 ilk / son 24 ortak saat, U5 💧 olayları (havuz) — Ek 2
HV = pd.concat(HAV) if HAV else pd.DataFrame(columns=["coin", "t", "ln", "la", "zn", "za"]); U4 = U5 = False; u4s = u5s = "veri yok"
if len(HV):
    HV = HV.dropna(); ts = sorted(HV.t.unique()); parcalar = []
    for ad, sec in (("ilk 24 s", ts[:24]), ("son 24 s", ts[-24:])):
        h = HV[HV.t.isin(sec)]; g = h.groupby("coin"); f2 = g.apply(lambda x: (x.ln - x.la).abs().median()).median(); z3 = g.apply(lambda x: (x.zn - x.za).abs().median()).median()
        u3 = ((h.zn <= -2) != (h.za <= -2)).mean(); parcalar.append((ad, f2, z3, u3, f2 <= 0.10 and z3 <= 0.25 and u3 <= 0.02))
    U4 = all(p[4] for p in parcalar); u4s = " · ".join(f"{a}: U2 {b:.3f} · U3 {c:.3f} · LD uyuşmazlık {d_:.2%} {'✅' if e else '❌'}" for a, b, c, d_, e in parcalar)
    na = int((HV.za <= -2).sum()); yak = ((HV.za <= -2) & (HV.zn <= -2)).sum() / max(na, 1); faz = ((HV.zn <= -2) & (HV.za > -2)).mean()
    U5 = na >= 5 and yak >= 0.80 and faz <= 0.02; u5s = f"arşivde 💧 saat {na} · Neon da yakaladı %{100*yak:.0f} · Neon fazladan 💧 %{100*faz:.2f}" + (" (5'ten az 💧 saati → karar yok)" if na < 5 else "")
yaz(f"\n**U4 gün gün:** {u4s} → {'✅' if U4 else '❌'}\n**U5 💧 olayları:** {u5s} → {'✅' if U5 else '❌'}")
NET = U1g and U4 and U5 if len(ilk13) else False                                              # UYUM_KARARI.md: "uymayan coin varsa o coin hariç tutulur" (kullanıcı 15.10: geçenleri ekle, geçmeyenleri ekleme) — uymayan coin listeye girmez
yaz(f"\n## Karar (UYUM_KARARI.md)\n- İlk 13 coin: {'✅ NET UYUM (canlıya EKLENMEZ, kullanıcı onayı beklenir)' if NET else '❌ net değil'}\n- Uyan coin'ler ({len(uyan)}): {', '.join(uyan) or '—'}\n- Uymayan (hariç): {', '.join(d[d['sonuç'] != '✅'].coin.tolist()) or '—'}")
if ARA: L.insert(1, f"**ARA KONTROL (karar değil): coin başına en az {MINS} ortak saat; asıl karar ≥ 72 saatle 16.10'da.**")
if not ARA: open("neon_derinlik/uyumlu_coinler.txt", "w").write("\n".join(uyan) + "\n")
open("neon_uyum_ara_sonuc.md" if ARA else "neon_uyum_sonuc.md", "w").write("\n".join(L) + "\n")
