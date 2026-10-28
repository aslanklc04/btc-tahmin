# borsa_golge.py — 🏦 BORSADAN GÜÇLÜ ÇIKIŞ (BTC/ETH) · GÖLGE İZLEME (28.10.2026 kullanıcı: "önerilerini uygula"). Telegram'a HİÇBİR ŞEY GÖNDERMEZ.
# Formül (arastirma3 PROTOKOL_kesif7, en yakın aday — önceden yazılı şartı tam geçmedi): CoinMetrics borsa çıkışı − girişi, 7 günlük toplam;
#   önceki 365 günün 7 günlük toplamlarına göre z ≥ 1,5 (D−2 günü verisi) → D günü 01:00 UTC'de al · 🎯 +%3 · en fazla 14 gün · varlık başına 3 gün bekleme.
#   28.10 kullanıcı: stop −%12 (asıl) + karşılaştırma için stopsuz; her sinyal iki satır ("surum" sütunu). −%5 kaldırıldı.
#   Araştırmada: isabet %72 · %85 · %90, işlem başı +%0,4 · +%1,5 · +%2,2 (2022–23 · 2024 · 2025+), ayda ~1–2 sinyal.
# Fiyat: Binance spot 1 s mum (canlıda erişilebilen; araştırma vadeli — fark küçük). Hedef/stop aynı mumda → stop (kötümser).
import os, json, time, numpy as np, pandas as pd, requests
CSV, DUR, MD = "durum/borsa_golge.csv", "durum/borsa_golge_durum.json", "durum/borsa_golge.md"
FL, FP, KAY, SLIP, T, GUN, ESIK = 0.0002, 0.0005, 0.003, 0.001, 0.03, 14, 1.5
SURUM = {"stopsuz": None, "stop −%12": 0.12}                                          # 28.10 kullanıcı: "stopu 12 yap" → −%5 kaldırıldı (geçmişte %59–62 isabet, zarar)
VAR = {"BTC": ("btc", "BTCUSDT"), "ETH": ("eth", "ETHUSDT")}
S = requests.Session()
def get(u, **kw):
    for k in range(3):
        try:
            r = S.get(u, timeout=40, **kw)
            if r.status_code == 200: return r
        except Exception: pass
        time.sleep(2 + 2 * k)
    return None
def akis(a):
    r = get("https://community-api.coinmetrics.io/v4/timeseries/asset-metrics", params=dict(assets=a, metrics="FlowInExNtv,FlowOutExNtv", frequency="1d", start_time=(pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=420)).strftime("%Y-%m-%d"), page_size=1000))
    if r is None: return None
    d = pd.DataFrame(r.json().get("data", []))
    if d.empty: return None
    d["t"] = pd.to_datetime(d.time, utc=True).dt.floor("D")
    for c in ("FlowInExNtv", "FlowOutExNtv"): d[c] = pd.to_numeric(d[c], errors="coerce")
    return d.set_index("t").sort_index()
def mum(sym, start_ms):
    r = get("https://data-api.binance.vision/api/v3/klines", params=dict(symbol=sym, interval="1h", startTime=int(start_ms), limit=1000))
    return [[float(v) for v in z[:5]] + [z[6]] for z in r.json()] if r is not None else None
def main():
    now = pd.Timestamp.now(tz="UTC"); now_ms = now.timestamp() * 1000; bugun = now.floor("D")
    T_ = pd.read_csv(CSV) if os.path.exists(CSV) else pd.DataFrame(columns=["gun", "varlik", "surum", "z", "giris_t", "giris", "hedef", "stop", "cikis_son", "durum", "cikis_t", "net"])
    if "surum" not in T_.columns: T_.insert(2, "surum", "stop −%12")
    for c in ("gun", "varlik", "surum", "giris_t", "cikis_son", "durum", "cikis_t"): T_[c] = T_[c].astype(object)
    D = json.load(open(DUR)) if os.path.exists(DUR) else {}
    yeni = 0
    if now.hour >= 1:                                                                         # günde bir kez, 01:00 UTC sonrası ilk çalışma
        for v, (a, sym) in VAR.items():
            if D.get(v + "_kontrol") == str(bugun.date()): continue
            A = akis(a)
            if A is None: continue                                                             # veri gelmezse sonraki saat yeniden dener
            net7 = (A.FlowOutExNtv - A.FlowInExNtv).rolling(7).sum()
            z = ((net7 - net7.rolling(365, min_periods=200).mean().shift(1)) / net7.rolling(365, min_periods=200).std().shift(1)).get(bugun - pd.Timedelta(days=2), np.nan)
            if not np.isfinite(z) and now.hour < 4: continue                                    # D−2 verisi henüz yayınlanmadıysa 04:00 UTC'ye kadar yeniden dene
            D[v + "_kontrol"] = str(bugun.date()); D[v + "_z"] = None if not np.isfinite(z) else round(float(z), 2)
            son = D.get(v + "_son")
            if np.isfinite(z) and z >= ESIK and (son is None or (bugun - pd.Timestamp(son, tz="UTC")).days >= 3):
                m = mum(sym, now_ms - 3_600_000)
                if not m: continue
                P = m[-1][4] * (1 + SLIP)
                for sn, sp in SURUM.items():
                    T_.loc[len(T_)] = dict(gun=str(bugun.date()), varlik=v, surum=sn, z=round(float(z), 2), giris_t=now.isoformat(), giris=P, hedef=P * (1 + T), stop=(P * (1 - sp) if sp else np.nan),
                                           cikis_son=(bugun + pd.Timedelta(hours=1) + pd.Timedelta(days=GUN)).isoformat(), durum="açık", cikis_t="", net=np.nan)
                D[v + "_son"] = str(bugun.date()); yeni += 1
    for i in T_.index[T_.durum == "açık"]:
        r = T_.loc[i]; te = pd.Timestamp(r.giris_t); ts = pd.Timestamp(r.cikis_son); P = float(r.giris)
        m = mum(VAR[r.varlik][1], te.floor("h").timestamp() * 1000)
        if not m: continue
        son = None; last = None
        for ot, o, h, l, c, ct in m:
            if ct >= now_ms or ot >= ts.timestamp() * 1000: break
            ilk = ot < te.timestamp() * 1000                                                    # giriş mumu: yalnız stop
            if pd.notna(r.stop) and l <= r.stop: p = min(r.stop, o) * (1 - KAY); son = ("stop", ot, p / P - 1 - 2 * FP - 0.0001 * (ot - te.timestamp() * 1000) / 28_800_000); break
            if h >= r.hedef and not ilk: son = ("🎯", ot, T - FP - FL - 0.0001 * (ot - te.timestamp() * 1000) / 28_800_000); break
            last = (ot, c)
        if son is None and now >= ts and last:
            ot, c = last; son = ("süre", ot, c / P - 1 - 2 * FP - 0.0001 * GUN * 3)
        if son: T_.loc[i, ["durum", "cikis_t", "net"]] = [son[0], pd.Timestamp(son[1], unit="ms", tz="UTC").isoformat(), son[2]]
    T_.to_csv(CSV, index=False); json.dump(D, open(DUR, "w"))
    k = T_[T_.net.notna()]; n = len(k)
    md = ["# 🏦 Borsadan güçlü çıkış (BTC/ETH) — gölge izleme (mesaj gönderilmez)",
          f"_güncellendi {now:%Y-%m-%d %H:%M} UTC · başlangıç 28.10.2026 · araştırma: isabet %72 · %85 · %90, işlem başı +%0,4 · +%1,5 · +%2,2 · son z: BTC {D.get('BTC_z')} · ETH {D.get('ETH_z')} (eşik 1,5)_", "",
          f"- toplam sinyal: {T_.drop_duplicates(["gun", "varlik"]).shape[0]} (her biri {len(SURUM)} sürüm) · kapanan satır: {n} · açık: {int((T_.durum == 'açık').sum())}"]
    for sn in SURUM:
        kk = k[k.surum == sn]
        if len(kk): md.append(f"- {sn}: {len(kk)} kapanan · isabet %{100 * (kk.net > 0).mean():.0f} · işlem başı ort. {100 * kk.net.mean():+.2f}% · en kötü {100 * kk.net.min():+.1f}%")
    md += ["", "| gün | varlık | sürüm | z | giriş | 🎯 | stop | durum | net % |", "|---|---|---|---|---|---|---|---|---|"]
    for _, r in T_.iloc[::-1].head(30).iterrows():
        md.append(f"| {r.gun} | {r.varlik} | {r.surum} | {r.z} | {r.giris:.6g} | {r.hedef:.6g} | {'—' if pd.isna(r.stop) else f'{r.stop:.6g}'} | {r.durum} | {'' if pd.isna(r.net) else f'{100 * r.net:+.2f}'} |")
    open(MD, "w").write("\n".join(md) + "\n")
    print(f"🏦 borsa gölge: z BTC {D.get('BTC_z')} · ETH {D.get('ETH_z')} · yeni {yeni} · kapanan {n}")
if __name__ == "__main__":
    main()
