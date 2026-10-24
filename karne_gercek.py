# karne_gercek.py — GERÇEKÇİ KARNE + GÖLGE İZLEME (24.10.2026, kullanıcı onayı: "tm önereni uygula"). Sinyallere ve mesajlara DOKUNMAZ; yalnız ölçer.
# Neden: bağımsız denetim (denetim dalı) ve PROTOKOL_saat70 / PROTOKOL_karal2 (arastirma3): eski karne girişi saat kapanışından, maliyeti %0,04 sayıyor,
#   aynı saatteki onlarca coin'i ayrı başarı sayıyordu → iyimser. Bu karne:
#   · giriş = mesajın GERÇEK gönderim dakikası (karne_kayit.csv t) · B: kapanış fiyatına limit 60 dk (fiyat zaten altındaysa hemen) · D: o dakika piyasadan
#   · Binance 1 dk mum, vadeli ücret (limit %0,02 · piyasa/stop %0,05) + fonlama yaklaşığı (her 00/08/16 UTC −%0,01)
#   · 🎯 = kapanış × (1 + k·σ720·√H), k: ✅ ana 0,75 · 🔸 yedek 0,50 · 📋 panelden 0,45 (bugünkü kural; 22.10'dan önceki mesajlara da aynı kural uygulanır)
#   · sonuç hem İŞLEM hem SAAT bazında (aynı saatteki sinyaller tek sepet)
#   GÖLGE (yalnız kayıt, mesaj gitmez): T1 takip eden kâr-al (τ 0,25) · T3 zarardakini 2H'ye uzat · A2 = PROTOKOL_saat70 sınırda geçen kural
#     (KuCoin BTC fonlama z > 0,51 saatlerinde, coin primi z'si en yüksek 5 sinyal; k: ana 0,45 · yedek 0,50 · panelden 0,30).
# Çıktı: durum/karne_gercek.csv (kapanan satırlar önbelleği) · durum/karne_gercek.md · pazar TR 20:00 sonrası haftada bir kısa Telegram özeti.
import os, re, json, time, numpy as np, pandas as pd, requests
from ortak import fetch_1h, tg_send, DISPLAY_TZ
from karne import coz
KAYIT_F, CSV_F, MD_F, DUR_F = "durum/karne_kayit.csv", "durum/karne_gercek.csv", "durum/karne_gercek.md", "durum/karne_gercek_durum.json"
K0 = {"ana": 0.75, "yedek": 0.5, "panelden": 0.45}; KA2 = {"ana": 0.45, "yedek": 0.5, "panelden": 0.3}; FZ_A2, N_A2 = 0.5098, 5
FL, FP, FON, TAU = 0.0002, 0.0005, 0.0001, 0.25
U1 = "https://data-api.binance.vision/api/v3/klines"; S = requests.Session()
def kl1m(sym, a, b):
    out, cur, son = [], int(a.timestamp() * 1000), int(b.timestamp() * 1000)
    while cur < son:
        x = None
        for k in range(4):
            try:
                r = S.get(U1, params=dict(symbol=sym, interval="1m", startTime=cur, endTime=son - 1, limit=1000), timeout=20)
                if r.status_code in (418, 429): time.sleep(10 + 10 * k); continue
                x = r.json(); break
            except Exception: time.sleep(2 + k)
        if not isinstance(x, list) or not x: break
        out += x; cur = x[-1][0] + 60_000
        if len(x) < 1000: break
    return out
def fon_serisi(bas):
    out, a = [], bas
    while a < pd.Timestamp.now(tz="UTC"):
        b = a + pd.Timedelta(days=30)
        try:
            j = S.get("https://api-futures.kucoin.com/api/v1/contract/funding-rates", params={"symbol": "XBTUSDTM", "from": int(a.timestamp() * 1000), "to": int(b.timestamp() * 1000)}, timeout=20).json()
            out += j.get("data", []) if isinstance(j, dict) else []
        except Exception as e: print("fonlama:", e)
        a = b
    if not out: return pd.Series(dtype=float)
    d = pd.Series({int(x["timepoint"]): float(x["fundingRate"]) for x in out}).sort_index(); d.index = pd.to_datetime(d.index, unit="ms", utc=True)
    return ((d - d.rolling(90, min_periods=30).mean()) / (d.rolling(90, min_periods=30).std() + 1e-12)).dropna()
def sim(M, a, Pe, fin, chk, tp, Hm, t0m, tau=None, s1=None, uzat=False):
    O, Hh, Lo, C = M[:, 0], M[:, 1], M[:, 2], M[:, 3]
    if tp <= Pe: return -fin - FP
    n = min(len(C), Hm); w = np.where(Hh[chk:n] >= tp)[0]
    if len(w):
        m = chk + w[0]
        if tau is None: cik, fo, j = tp, FL, m
        else:
            rm = np.maximum.accumulate(np.maximum(Hh[m:n], tp)); st = np.maximum(Pe * 1.002, np.concatenate([[tp], rm[:-1]]) * (1 - tau * s1))
            ww = np.where(Lo[m:n][1:] <= st[1:])[0]
            if len(ww): j = m + 1 + ww[0]; cik, fo = st[1 + ww[0]], FP
            else: j = n - 1; cik, fo = C[n - 1], FP
    else:
        j = n - 1; cik, fo = C[n - 1], FP
        if uzat:
            if len(C) < 2 * Hm: return np.nan                                                    # uzatma süresi dolmadı
            if C[n - 1] < Pe:
                w2 = np.where(Hh[n:2 * Hm] >= Pe * 1.0007)[0]
                if len(w2): j = n + w2[0]; cik, fo = Pe * 1.0007, FL
                else: j = 2 * Hm - 1; cik, fo = C[2 * Hm - 1], FP
    nf = (t0m + j + 1) // 480 - (t0m + a) // 480
    return cik / Pe - 1 - fin - fo - FON * nf
def main():
    if not os.path.exists(KAYIT_F): print("karne_gercek: kayıt yok"); return
    K = pd.read_csv(KAYIT_F, dtype=str).fillna(""); K = K[K.k.str.startswith("gönderildi") & (K.s != "panel")]
    rows = []
    for r in K.itertuples():
        tg = pd.Timestamp(r.t, tz=DISPLAY_TZ).tz_convert("UTC"); t0 = tg.floor("h"); su = int(float(r.sure)) if r.sure else None
        sn = "ana" if r.s.startswith("✅") else ("panelden" if "📋" in r.s else "yedek")
        for nm, H, yon, tur, isr in coz(r.e, su):
            if yon < 0 or tur in ("⛓️", "🧑", "📆"): continue
            g = re.search(rf"{nm} \(z ([+-]?[\d.]+)", r.e) or re.search(r"prim \S+ z ([+-]?[\d.]+)", r.e)
            rows.append(dict(tg=tg, t0=t0, sinif=sn, coin=nm, H=int(H), tur=tur, z=float(g.group(1)) if g else np.nan))
    X = pd.DataFrame(rows)
    if X.empty: print("karne_gercek: sinyal yok"); return
    X = X.drop_duplicates(["t0", "coin", "H", "sinif"]).reset_index(drop=True); X["anahtar"] = X.t0.astype(str) + "|" + X.coin + "|" + X.sinif + "|" + X.H.astype(str)
    ESK = pd.read_csv(CSV_F) if os.path.exists(CSV_F) else pd.DataFrame(columns=["anahtar"])
    if len(ESK) and "tpp" not in ESK: ESK = pd.DataFrame(columns=["anahtar"])                    # 24.10: 🎯 mesafesi sütunu eklendi → önbellek bir kez yeniden hesaplanır
    tamam = set(ESK.anahtar[ESK.get("tam", pd.Series(dtype=bool)).astype(str) == "True"]) if len(ESK) else set()
    now = pd.Timestamp.now(tz="UTC")
    FZ = fon_serisi(X.t0.min() - pd.Timedelta(days=60))
    X["fz"] = [float(FZ[FZ.index <= t].iloc[-1]) if (FZ.index <= t).any() else np.nan for t in X.t0]
    X["_so"] = X.sinif.map({"ana": 0, "yedek": 1, "panelden": 2})                                  # A2: saat içi en iyi 5 (z), PROTOKOL_saat70 Ek 2.1 sırası
    sel = X.sort_values(["z", "_so", "H", "coin"], ascending=[False, True, True, True], kind="mergesort").groupby("t0").head(N_A2).index
    X["a2"] = X.index.isin(sel) & (X.fz > FZ_A2)
    yeni = X[~X.anahtar.isin(tamam) & (X.t0 + pd.to_timedelta(X.H, unit="h") <= now)]
    P = {}
    for nm in yeni.coin.unique():
        try: P[nm] = fetch_1h((yeni.t0.min() - pd.Timedelta(days=32)).value // 10**6, now.value // 10**6, sym=nm + "USDT").close
        except Exception as e: print("karne_gercek saatlik yok:", nm, e)
    out = []
    for r in yeni.itertuples():
        c = P.get(r.coin)
        if c is None or r.t0 not in c.index: continue
        G = c[r.t0]; lr = np.log(c[c.index <= r.t0]).diff().dropna().iloc[-720:]
        if len(lr) < 168: continue
        s1 = lr.std(); Hm = r.H * 60; a = int((r.tg - r.t0).total_seconds() // 60); t0m = int(r.t0.timestamp() // 60)
        x = kl1m(r.coin + "USDT", r.t0, min(now, r.t0 + pd.Timedelta(minutes=2 * Hm)))
        if len(x) < Hm or int(x[0][0]) != int(r.t0.timestamp() * 1000): continue
        M = np.array([[float(v) for v in z[1:5]] for z in x]); O, Lo = M[:, 0], M[:, 2]
        d = dict(anahtar=r.anahtar, tg=r.tg, t0=r.t0, sinif=r.sinif, coin=r.coin, H=r.H, tur=r.tur, z=r.z, fz=r.fz, a2=bool(r.a2), G=G, tpp=100 * K0[r.sinif] * s1 * np.sqrt(r.H))   # tpp: 🎯 mesafesi % (24.10 gölge)
        if O[a] <= G: fB, Pb, finb, chkb = True, O[a], FP, a
        else:
            w = np.where(Lo[a + 1:a + 61] <= G)[0]; fB = len(w) > 0
            Pb, finb, chkb = (G, FL, a + 2 + w[0]) if fB else (np.nan, 0, 0)
        tp = G * (1 + K0[r.sinif] * s1 * np.sqrt(r.H)); tpa = G * (1 + KA2[r.sinif] * s1 * np.sqrt(r.H))
        d.update(fB=fB, D_T0=sim(M, a, O[a], FP, a, tp, Hm, t0m))
        if fB:
            ab = dict(M=M, a=a, Pe=Pb, fin=finb, chk=chkb, Hm=Hm, t0m=t0m)
            d.update(B_T0=sim(tp=tp, **ab), B_T1=sim(tp=tp, tau=TAU, s1=s1, **ab), B_T3=sim(tp=tp, uzat=True, **ab), B_A2=sim(tp=tpa, **ab))
        d["tam"] = bool(len(M) >= 2 * Hm)
        out.append(d)
    Y = pd.concat([ESK[~ESK.anahtar.isin([o["anahtar"] for o in out])], pd.DataFrame(out)], ignore_index=True) if len(ESK) else pd.DataFrame(out)
    if Y.empty: print("karne_gercek: kapanan yok"); return
    Y.to_csv(CSV_F, index=False)
    rapor(Y, now)
def rapor(Y, now):
    Y = Y.copy(); Y["t0"] = pd.to_datetime(Y.t0, utc=True)
    for c in ("B_T0", "D_T0", "B_T1", "B_T3", "B_A2"): Y[c] = pd.to_numeric(Y.get(c), errors="coerce")
    def ol(d, c):
        x = d[["t0", c]].dropna()
        if x.empty: return "—"
        sp = x.groupby("t0")[c].mean()
        return f"{len(x)} işlem / {len(sp)} saat · işlem isabeti %{100 * (x[c] > 0).mean():.0f} · **saat isabeti %{100 * (sp > 0).mean():.0f}** · işlem başı {100 * x[c].mean():+.2f}%"
    L = [f"# 📏 Gerçekçi karne — {now.tz_convert(DISPLAY_TZ):%d.%m.%Y %H:%M}",
         "_Giriş: mesajın geldiği dakikadan, kapanış fiyatına limit 60 dk (B; mesajdaki talimat) · vadeli ücret + fonlama · Binance 1 dk mum · 🎯 bugünkü sınıf kuralı. Eski karne (karne.md) saat kapanışından giriş ve %0,04 maliyet sayar → bundan iyimser._\n",
         "## Gönderilen sinyaller (B: limit giriş)"]
    for sn, ad in (("ana", "✅ ana"), ("yedek", "🔸 yedek"), ("panelden", "📋 panelden"), (None, "Tümü")):
        d = Y if sn is None else Y[Y.sinif == sn]
        dol = f" · limit doldu %{100 * d.fB.astype(str).eq('True').mean():.0f}" if len(d) else ""
        L.append(f"- **{ad}:** {ol(d, 'B_T0')}{dol}")
    L.append(f"- Piyasadan giriş (D) karşılaştırma, tümü: {ol(Y, 'D_T0')}")
    L.append("\n## 👻 Gölge izleme (mesaj gitmez; birkaç ay sonra karar için)")
    b = Y.dropna(subset=["B_T0", "B_T1"]); L.append(f"- **T1 takip eden kâr-al (τ 0,25):** {ol(b, 'B_T1')} — aynı işlemler şimdiki kuralla: {ol(b, 'B_T0')}")
    b = Y.dropna(subset=["B_T0", "B_T3"]); L.append(f"- **T3 zarardakini 2 katı süreye uzat:** {ol(b, 'B_T3')} — aynı işlemler şimdiki kuralla: {ol(b, 'B_T0')}")
    Y["tpp"] = pd.to_numeric(Y.get("tpp"), errors="coerce"); ap = Y[Y.sinif.isin(["ana", "panelden"])].dropna(subset=["B_T0", "tpp"])
    L.append(f"- **🎯 ≥ %1,5 filtresi (ana + panelden):** {ol(ap[ap.tpp >= 1.5], 'B_T0')} — filtresiz: {ol(ap, 'B_T0')} · elenenler (🎯 < %1,5): {ol(ap[ap.tpp < 1.5], 'B_T0')}")
    b = Y.dropna(subset=["B_T0", "tpp"]).copy(); b["w"] = np.clip(np.round(4 * 1.5 / b.tpp) / 4, 0.25, 1.0)
    if len(b):
        e = b.groupby("t0").B_T0.mean(); wv = b.assign(wr=b.w * b.B_T0).groupby("t0").agg(wr=("wr", "sum"), w=("w", "sum")); w_ = wv.wr / wv.w
        L.append(f"- **📐 risk payı (pay = 1,5 / 🎯 %, en fazla ×1):** saat sepeti eşit pay → saat isabeti %{100 * (e > 0).mean():.0f} · ort {100 * e.mean():+.2f}% · en kötü saat {100 * e.min():+.2f}% · oynaklık {100 * e.std():.2f} | risk paylı → %{100 * (w_ > 0).mean():.0f} · ort {100 * w_.mean():+.2f}% · en kötü {100 * w_.min():+.2f}% · oynaklık {100 * w_.std():.2f}")
    a2 = Y[Y.a2.astype(str) == "True"]; L.append(f"- **A2 (fonlama yüksek + saatte en iyi 5, PROTOKOL_saat70):** {ol(a2, 'B_A2')} · testte (2025+) saat isabeti %70,5 (sınırda)")
    L.append(f"\n_Kayıt: durum/karne_gercek.csv ({len(Y)} satır) · 22.10 öncesi mesajlarda 🎯 farklıydı/yoktu; burada hepsi bugünkü kuralla ölçülür._")
    open(MD_F, "w", encoding="utf-8").write("\n".join(L) + "\n")
    yerel = now.tz_convert(DISPLAY_TZ)
    try: DUR = json.load(open(DUR_F))
    except Exception: DUR = {}
    if yerel.dayofweek == 6 and yerel.hour >= 20 and DUR.get("hafta") != f"{yerel:%G-%V}":
        tg_send("\n".join(L[:1] + L[2:]).replace("**", ""))
        DUR["hafta"] = f"{yerel:%G-%V}"; json.dump(DUR, open(DUR_F, "w"))
    print("\n".join(L))
if __name__ == "__main__": main()
