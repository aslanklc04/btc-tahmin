# igne_golge.py — 🪡 İĞNE DÖNÜŞÜ · GÖLGE İZLEME (27.10.2026 kullanıcı: "numara 2"). Telegram'a HİÇBİR ŞEY GÖNDERMEZ; yalnız kaydeder ve sonucu ölçer.
# Formül (arastirma3 PROTOKOL_igne4 Ek, en yakın formül (a) — önceden yazılı şartı tam geçmedi; bakılmamış 735 coin'de isabet %70,5, işlem başı ort. +%2,4):
#   saat h kapandı: iğne kr = (açılış − dip) / (açılış · σ1) ≥ 8 (σ1 = önceki 720 saatin 1 s log getiri std'si) · toparlanma (kapanış − dip)/(açılış − dip) ≥ 0,75
#   aynı saatte BTC 1 s getirisi ≥ −%1 · son 7 gün ort. günlük hacim ≥ 2 M$ · aynı coin'de 24 saat bekleme
#   giriş: çalışma anındaki fiyat (piyasa) · 🎯 = dip + 1,25·(açılış − dip) · stop = dip·(1 − 2σ1) · en fazla 48 saat (h + 48 s + 10 dk)
# Not: araştırma Binance VADELİ mumla yapıldı; canlıda erişilebilen Binance SPOT mumu kullanılır (gölgenin ölçtüğü şeylerden biri de bu fark).
import os, json, time, numpy as np, pandas as pd, requests
from concurrent.futures import ThreadPoolExecutor
U = "https://data-api.binance.vision/api/v3/klines"
CSV, DUR, MD = "durum/igne_golge.csv", "durum/igne_golge_durum.json", "durum/igne_golge.md"
FL, FP, FON, KAY = 0.0002, 0.0005, 0.0001, 0.003
K, RR, BTC_MIN, LIQ, F, SK, HMAX = 8.0, 0.75, -0.01, 2e6, 1.25, 2.0, 48
SUTUN = ["sinyal_t", "coin", "acilis", "dip", "kapanis", "sigma", "kr", "rr", "btc_r", "hacim", "giris_t", "giris", "hedef", "stop", "cikis_son", "durum", "cikis_t", "cikis_fiyat", "net"]
S = requests.Session()
def kl(sym, iv, limit=1000, start=None, end=None):
    p = dict(symbol=sym, interval=iv, limit=limit)
    if start is not None: p["startTime"] = int(start)
    if end is not None: p["endTime"] = int(end)
    for k in range(3):
        try:
            r = S.get(U, params=p, timeout=20)
            if r.status_code == 200: return r.json()
            if r.status_code == 400: return None
        except Exception: pass
        time.sleep(1 + k)
    return None
def saatlik(sym, now_ms):
    x = kl(sym, "1h")
    if not x: return None
    d = pd.DataFrame([[float(v) for v in z[:8]] for z in x], columns=["ot", "o", "h", "l", "c", "v", "ct", "qv"])
    return d[d.ct < now_ms].reset_index(drop=True)                                             # yalnız kapanmış saatler
def nfon(a_ms, b_ms): return int(b_ms // 28_800_000 - a_ms // 28_800_000)
def main():
    now = pd.Timestamp.now(tz="UTC"); now_ms = int(now.timestamp() * 1000)
    syms = ["BTCUSDT"] + [x.strip() for f in ("durum/coin_listesi.txt", "durum/genis_liste.txt") if os.path.exists(f) for x in open(f) if x.strip()]
    syms = list(dict.fromkeys(syms))
    T = pd.read_csv(CSV) if os.path.exists(CSV) else pd.DataFrame(columns=SUTUN)
    for c_ in ("durum", "cikis_t", "giris_t", "sinyal_t", "cikis_son", "coin"): T[c_] = T[c_].astype(object)
    D = json.load(open(DUR)) if os.path.exists(DUR) else {}
    # ---- 1) yeni sinyal
    with ThreadPoolExecutor(8) as ex: H = dict(zip(syms, ex.map(lambda s: saatlik(s, now_ms), syms)))
    bt = H.get("BTCUSDT"); yeni = 0
    if bt is not None and len(bt) > 2:
        h_ot = bt.ot.iloc[-1]; btc_r = bt.c.iloc[-1] / bt.c.iloc[-2] - 1
        for s, d in H.items():
            if d is None or len(d) < 730 or d.ot.iloc[-1] != h_ot: continue
            o, l, c = d.o.iloc[-1], d.l.iloc[-1], d.c.iloc[-1]
            sg = np.log(d.c.iloc[-722:-1]).diff().dropna().std(); hac = d.qv.iloc[-169:-1].sum() / 7
            if not (np.isfinite(sg) and sg > 0 and o > l): continue
            kr = (o - l) / (o * sg); rr = (c - l) / (o - l)
            if kr < K or rr < RR or btc_r < BTC_MIN or hac < LIQ: continue
            if s in D and h_ot - D[s] < 24 * 3_600_000: continue
            px = kl(s, "1m", limit=1); giris = float(px[-1][4]) if px else c
            T.loc[len(T)] = dict(sinyal_t=pd.Timestamp(h_ot + 3_600_000, unit="ms", tz="UTC").isoformat(), coin=s[:-4], acilis=o, dip=l, kapanis=c, sigma=sg, kr=round(kr, 2), rr=round(rr, 2),
                                 btc_r=round(btc_r, 4), hacim=round(hac), giris_t=now.isoformat(), giris=giris, hedef=l + F * (o - l), stop=l * (1 - SK * sg),
                                 cikis_son=pd.Timestamp(h_ot + 3_600_000 + HMAX * 3_600_000 + 600_000, unit="ms", tz="UTC").isoformat(), durum="açık", cikis_t="", cikis_fiyat=np.nan, net=np.nan)
            D[s] = int(h_ot); yeni += 1
    # ---- 2) açık işlemlerin sonucu (spot 5 dk, kötümser: aynı mumda stop önce)
    for i in T.index[T.durum == "açık"]:
        r = T.loc[i]; te = pd.Timestamp(r.giris_t); ts = pd.Timestamp(r.cikis_son); P = float(r.giris)
        x = kl(r.coin + "USDT", "5m", start=te.floor("5min").timestamp() * 1000, end=min(now, ts).timestamp() * 1000)
        if x is None: continue
        bars = [[float(v) for v in z[:5]] for z in x if z[6] < now_ms]
        sonuc = None
        if P <= r.stop: T.loc[i, "durum"] = "alınmadı (fiyat stopun altında)"; continue
        if r.hedef <= P: sonuc = ("hedef≤giriş", te, P, P / P - 1 - 2 * FP)
        for ot, o, h, l, c in bars:
            if sonuc: break
            ilk = ot < te.timestamp() * 1000                                                    # giriş mumu: yalnız stop (kötümser)
            if l <= r.stop:
                p = min(r.stop, o, (r.stop + l) / 2) * (1 - KAY); sonuc = ("stop", pd.Timestamp(ot + 300_000, unit="ms", tz="UTC"), p, p / P - 1 - 2 * FP - FON * nfon(te.timestamp() * 1000, ot + 300_000))
            elif h >= r.hedef and not ilk: sonuc = ("🎯", pd.Timestamp(ot + 300_000, unit="ms", tz="UTC"), r.hedef, r.hedef / P - 1 - FP - FL - FON * nfon(te.timestamp() * 1000, ot + 300_000))
        if not sonuc and now >= ts and bars:
            ot, o, h, l, c = bars[-1]; sonuc = ("süre", pd.Timestamp(ot + 300_000, unit="ms", tz="UTC"), c, c / P - 1 - 2 * FP - FON * nfon(te.timestamp() * 1000, ot + 300_000))
        if sonuc: T.loc[i, ["durum", "cikis_t", "cikis_fiyat", "net"]] = [sonuc[0], sonuc[1].isoformat(), sonuc[2], sonuc[3]]
    T.to_csv(CSV, index=False); json.dump(D, open(DUR, "w"))
    k = T[~T.durum.isin(["açık"]) & T.net.notna()]; n = len(k); ac = int((T.durum == "açık").sum())
    md = ["# 🪡 İğne dönüşü — gölge izleme (mesaj gönderilmez)", f"_güncellendi {now:%Y-%m-%d %H:%M} UTC · başlangıç 27.10.2026 · araştırma beklentisi: isabet ~%70, işlem başı ort. ~+%2,4 (bakılmamış coin'ler, vadeli)_", "",
          f"- toplam sinyal: {len(T)} · kapanan: {n} · açık: {ac}"]
    if n: md.append(f"- kapanan: isabet %{100 * (k.net > 0).mean():.0f} · işlem başı ort. {100 * k.net.mean():+.2f}% · 🎯 {int((k.durum == '🎯').sum())} · stop {int((k.durum == 'stop').sum())} · süre {int((k.durum == 'süre').sum())} · en kötü {100 * k.net.min():+.1f}%")
    md += ["", "| sinyal (UTC) | coin | giriş | 🎯 | stop | durum | net % |", "|---|---|---|---|---|---|---|"]
    for _, r in T.tail(30).iloc[::-1].iterrows():
        md.append(f"| {r.sinyal_t[:16]} | {r.coin} | {r.giris:.6g} | {r.hedef:.6g} | {r.stop:.6g} | {r.durum} | {'' if pd.isna(r.net) else f'{100 * r.net:+.2f}'} |")
    open(MD, "w").write("\n".join(md) + "\n")
    print(f"🪡 gölge: {len(syms)} sembol · bu saat yeni {yeni} · açık {ac} · kapanan {n}")
if __name__ == "__main__":
    main()
