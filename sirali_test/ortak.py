# ortak.py — v32 modelinin GitHub Actions sürümü için ortak parçalar (egit.py ve tahmin.py kullanır)
import os, io, json, time, zipfile, warnings, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
warnings.filterwarnings("ignore"); pd.set_option("display.width", 220)
SPOT_FEE, DISPLAY_TZ = 0.001, "Europe/Istanbul"
SYMBOL, TEST_START, HOLD_START, W = "BTCUSDT", "2020-01-01", "2024-01-01", 24 * 30
MICRO_START = "2017-09-01"
CFG = {1: dict(years=[3], don=False, ad="1 saat"), 4: dict(years=[5], don=False, ad="4 saat"), 8: dict(years=[3, 5], don=False, ad="8 saat")}
LEV = ["Zayıf", "Güçlü (en emin %30)", "Çok güçlü (en emin %10)"]
EP = ["https://data-api.binance.vision/api/v3/klines", "https://api.binance.com/api/v3/klines", "https://api.binance.us/api/v3/klines"]
TELEGRAM_TOKEN, TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_TOKEN", "").strip(), os.environ.get("TELEGRAM_CHAT_ID", "").strip()
def baslik(s): print("\n" + "=" * 72 + f"\n{s}\n" + "=" * 72, flush=True)
def fetch_1h(start_ms, end_ms, verbose=False, sym=None):
    for url in EP:
        try:
            rows, cur = [], int(start_ms)
            while cur < end_ms:
                r = requests.get(url, params=dict(symbol=sym or SYMBOL, interval="1h", startTime=cur, endTime=int(end_ms), limit=1000), timeout=20)
                r.raise_for_status(); dt = r.json()
                if not dt: break
                rows += dt; cur = dt[-1][0] + 3_600_000
                if verbose and len(rows) % 20000 < 1000: print(f"  {len(rows):,} mum")
                if len(dt) < 1000: break
            if rows:
                df = pd.DataFrame([x[:6] for x in rows], columns=["t", "open", "high", "low", "close", "volume"]).astype(float)
                df.index = pd.to_datetime(df.t, unit="ms", utc=True) + pd.Timedelta(hours=1)          # indeks = kapanış
                df = df[df.index <= pd.Timestamp.now(tz="UTC")]
                return df[~df.index.duplicated()].sort_index()[["open", "high", "low", "close", "volume"]]
        except Exception as e:
            if verbose: print(f"⚠️ {url.split('/')[2]}: {e}")
    raise RuntimeError("Binance verisi alınamadı")


def rsi(x, n):
    d = x.diff(); up = d.clip(lower=0).ewm(alpha=1/n, adjust=False).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1/n, adjust=False).mean()
    return 100 - 100 / (1 + up / (dn + 1e-12))
def features(o):
    c, h, l, v = o.close, o.high, o.low, o.volume; lr = np.log(c).diff(); F = pd.DataFrame(index=o.index)
    for k in [1, 2, 4, 8, 24, 72, 168, 336, 720]: F[f"r{k}"] = np.log(c / c.shift(k))
    for k in [24, 168, 720]: F[f"vol{k}"] = lr.rolling(k).std()
    F["volr"] = F.vol24 / F.vol720; F["volr2"] = F.vol168 / F.vol720
    for k in [14, 56]: F[f"rsi{k}"] = rsi(c, k)
    for k in [24, 72, 168, 720]: F[f"ema{k}"] = c / c.ewm(span=k, adjust=False).mean() - 1
    for k in [168, 720]: F[f"hh{k}"] = c / h.rolling(k).max() - 1; F[f"ll{k}"] = c / l.rolling(k).min() - 1
    F["pos168"] = (c - l.rolling(168).min()) / (h.rolling(168).max() - l.rolling(168).min() + 1e-9)
    F["v24"] = np.log(v.rolling(24).sum() + 1) - np.log(v.rolling(720).sum() / 30 + 1)
    F["v1"] = np.log(v + 1) - np.log(v.rolling(168).mean() + 1)
    F["rng"] = (h - l) / c; F["body"] = (c - o.open) / (h - l + 1e-9)
    F["r8_vs"] = F.r8 / (F.vol168 * np.sqrt(8) + 1e-9); F["r24_vs"] = F.r24 / (F.vol168 * np.sqrt(24) + 1e-9)
    F["r168_vs"] = F.r168 / (F.vol720 * np.sqrt(168) + 1e-9)
    hr, dw = o.index.hour, o.index.dayofweek
    F["hs"], F["hc"] = np.sin(2 * np.pi * hr / 24), np.cos(2 * np.pi * hr / 24); F["ds"], F["dc"] = np.sin(2 * np.pi * dw / 7), np.cos(2 * np.pi * dw / 7)
    return F.replace([np.inf, -np.inf], np.nan)
def _mzip(ym, sym=None):
    sym = sym or SYMBOL; url = f"https://data.binance.vision/data/spot/monthly/klines/{sym}/1m/{sym}-1m-{ym}.zip"
    for _ in range(3):
        try:
            r = requests.get(url, timeout=60)
            if r.status_code == 404: return None
            r.raise_for_status(); z = zipfile.ZipFile(io.BytesIO(r.content)); return pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=[0, 4, 5])
        except Exception: time.sleep(2)
    return None
def to_min(df):
    ot = pd.to_numeric(df[0], errors="coerce"); ok = ot.notna(); ot = ot[ok].values.astype("float64"); ot = np.where(ot > 1e14, ot / 1000, ot)
    m = pd.DataFrame({"close": pd.to_numeric(df[4][ok]).values, "volume": pd.to_numeric(df[5][ok]).values}, index=pd.to_datetime(ot, unit="ms", utc=True) + pd.Timedelta(minutes=1))
    return m[~m.index.duplicated()].sort_index()
def fetch_1m(start_ms, end_ms, sym=None):
    rows, cur = [], int(start_ms)
    while cur < end_ms:
        dt = None
        for url in EP:
            try:
                r = requests.get(url, params=dict(symbol=sym or SYMBOL, interval="1m", startTime=cur, endTime=int(end_ms), limit=1000), timeout=20)
                if r.status_code == 200: dt = r.json(); break
            except Exception: pass
        if not dt: break
        rows += dt; cur = dt[-1][0] + 60_000
        if len(dt) < 1000: break
    return to_min(pd.DataFrame([x[:6] for x in rows])) if rows else None
def micro_features(m):
    c = m.close.astype("float64"); v = m.volume.astype("float64"); r = np.log(c).diff().fillna(0)
    hour = m.index.ceil("h"); mi = np.asarray(((m.index - (hour - pd.Timedelta(hours=1))) / pd.Timedelta(minutes=1))).astype(int)
    late, l5 = mi > 45, mi > 55
    G = pd.DataFrame({"r": r.values, "rl15": r.values * late, "re45": r.values * ~late, "rl5": r.values * l5, "v": v.values, "vl15": v.values * late,
                      "cv": (c * v).values, "rr": (r * r.shift(1).fillna(0)).values, "r2": (r * r).values, "h": hour, "c": c.values, "mi": mi})
    A = G.groupby("h")[["r", "rl15", "re45", "rl5", "v", "vl15", "cv", "rr", "r2"]].sum(); cl = G.groupby("h").c.last()
    imax, imin = G.groupby("h").c.idxmax(), G.groupby("h").c.idxmin()
    hp = pd.Series(G.loc[imax.values, "mi"].values, index=imax.index); lp = pd.Series(G.loc[imin.values, "mi"].values, index=imin.index)
    sd = np.sqrt(A.r2) + 1e-12; M = pd.DataFrame(index=A.index)
    M["m_last15"] = A.rl15 / sd; M["m_first45"] = A.re45 / sd; M["m_last5"] = A.rl5 / sd; M["m_vwapdev"] = np.log(cl / (A.cv / (A.v + 1e-12))) / sd
    M["m_vol_late"] = A.vl15 / (A.v + 1e-12); M["m_autocorr"] = A.rr / (A.r2 + 1e-18); M["m_hi_pos"] = hp / 60; M["m_lo_pos"] = lp / 60
    M["m_brk_up"] = ((hp >= 55) & (lp <= 30)).astype(float); M["m_brk_dn"] = ((lp >= 55) & (hp <= 30)).astype(float)
    M.index = pd.DatetimeIndex(M.index); return M.replace([np.inf, -np.inf], np.nan).astype("float32")
def hourly_cv(m):
    return pd.DataFrame({"cv": (m.close * m.volume).values, "v": m.volume.values}, index=m.index).resample("1h", label="right", closed="right").sum()
def path2_features(close_h, HHm, MIC):
    cl = close_h; lr = np.log(cl).diff(); sd = lr.rolling(720, min_periods=168).std(); HHa = HHm.reindex(cl.index).fillna(0); Mi = MIC.reindex(cl.index)
    P = pd.DataFrame(index=cl.index)
    for k in [4, 8, 24, 72]:
        vw = HHa.cv.rolling(k).sum() / (HHa.v.rolling(k).sum() + 1e-12); P[f"p2_vwap{k}"] = np.log(cl / vw) / (sd * np.sqrt(k) + 1e-12)
    for k in [24, 168]:
        P[f"p2_since_hi{k}"] = (k - 1 - cl.rolling(k).apply(np.argmax, raw=True)) / k; P[f"p2_since_lo{k}"] = (k - 1 - cl.rolling(k).apply(np.argmin, raw=True)) / k
    for k in [4, 8]:
        P[f"p2_last15_sum{k}"] = Mi.m_last15.rolling(k).sum(); P[f"p2_brkdn_cnt{k}"] = Mi.m_brk_dn.rolling(k).sum(); P[f"p2_brkup_cnt{k}"] = Mi.m_brk_up.rolling(k).sum()
        P[f"p2_vwapdev_mean{k}"] = Mi.m_vwapdev.rolling(k).mean()
    return P.replace([np.inf, -np.inf], np.nan).astype("float32")
class ZF:
    """Standartlaştırıcı (Colab'daki zfit ile birebir aynı hesap; dosyaya kaydedilebilir)."""
    def __init__(self, X):
        self.med = X.median(); Z = X.fillna(self.med); self.mu, self.sd = Z.mean(), Z.std() + 1e-9
    def __call__(self, A): return ((A.fillna(self.med) - self.mu) / self.sd).clip(-5, 5).values
class HModel:
    """GBM + lojistik parçalarının ortalaması (Colab'daki lambda ile birebir aynı; dosyaya kaydedilebilir)."""
    def __init__(self, parts, FE): self.parts, self.FE = parts, list(FE)
    def __call__(self, A):
        return (np.mean([g.predict_proba(A[self.FE])[:, 1] for g, _, _ in self.parts], axis=0),
                np.mean([lo.predict_proba(z(A[self.FE]))[:, 1] for _, z, lo in self.parts], axis=0))
def cz(x):  # yalnız GEÇMİŞ 30 güne göre z
    return (x - x.rolling(W, min_periods=24 * 7).mean().shift(1)) / (x.rolling(W, min_periods=24 * 7).std().shift(1) + 1e-9)
lgt = lambda p: np.log(p / (1 - p))
def signal_frame(PG, PL, rh, don):
    S = (cz(lgt(PG)) + cz(lgt(PL)) + (cz(-rh.reindex(PG.index)) if don else 0)) / (3 if don else 2); C = S.abs()
    return pd.DataFrame({"S": S, "C": C, "T30": C.rolling(W, min_periods=24 * 7).quantile(0.70).shift(1), "T10": C.rolling(W, min_periods=24 * 7).quantile(0.90).shift(1)})
def events(mask, H):
    """Canlı ölçüm: sinyal ilk ortaya çıktığı saatte sayılır; aynı sinyal H saat boyunca tekrar sayılmaz."""
    idx = np.where(np.asarray(mask))[0]; out = []; last = -10**9
    for i in idx:
        if i - last >= H: out.append(i); last = i
    return np.array(out, int)
def wboot(v, idx_times, reps=800):
    """Haftalık blok bootstrap ile ortalamanın %90 aralığı."""
    if len(v) < 5: return np.nan, np.nan
    gi = pd.Series(np.arange(len(v))).groupby(pd.DatetimeIndex(idx_times).floor("7D")).indices; gk = list(gi); rg = np.random.default_rng(0)
    bs = [v[np.concatenate([gi[gk[j]] for j in rg.integers(0, len(gk), len(gk))])].mean() for _ in range(reps)]; return np.percentile(bs, 5), np.percentile(bs, 95)
def rpct(S): return S.rolling(W, min_periods=24 * 7).rank(pct=True)                   # son 30 güne göre yüzdelik (yalnız geçmiş + şimdi)
def auc_se(a, n):   # Hanley–McNeil standart hatası (n bağımsız blok, sınıflar ~eşit)
    n1 = n2 = n / 2; q1, q2 = a / (2 - a), 2 * a * a / (1 + a)
    return np.sqrt((a * (1 - a) + (n1 - 1) * (q1 - a * a) + (n2 - 1) * (q2 - a * a)) / (n1 * n2))

def frame_from_S(S):
    C = S.abs(); return pd.DataFrame({"S": S, "C": C, "T30": C.rolling(W, min_periods=24 * 7).quantile(0.70).shift(1), "T10": C.rolling(W, min_periods=24 * 7).quantile(0.90).shift(1)})
def action(H, sg, li, st):
    if li == 0: return "⚪ Zayıf sinyal — belirgin avantaj yok", "nt"
    if sg == 1 and li == 2 and st["lo"] > 0 and st["net"] > 0: return f"✅ ALIM SİNYALİ — {H} saat tut (testte komisyon sonrası ort. %{st['net']:+.2f}, marj ince)", "up"
    if sg == 1 and st["lo"] > 0: return "🟢 Planlı alım için iyi an (işlem olarak komisyonu karşılamıyor)", "up"
    if sg == -1 and st["lo"] > 0: return "🔴 Alımı ertele / elde varsa satışı düşün", "dn"
    return f"{'🟡 Yukarı' if sg == 1 else '🟠 Aşağı'} eğilim — bu seviyenin geçmişi anlamlı değil (bilgi amaçlı)", "up" if sg == 1 else "dn"
# ---- v35: 💥 teslimiyet onayı (derin kural araması: ~4 milyon kural, 3 dönem + şans kontrolü ile seçilen 20 kural) ----
TES_RULES = [[["ret240_d1", "≤", "20"], ["dnw1_z", "≤", "20"], ["rn_xdn_4", "≥", "80"]], [["volr_336_720_d4", "≥", "80"], ["rng24", "≥", "60"], ["hh24_d1", "≤", "20"], ["m_last5", "≤", "40"]], [["volr_336_720_d4", "≥", "80"], ["rng24", "≥", "60"], ["rng72_d4", "≥", "60"], ["hh24_d1", "≤", "20"], ["m_last5", "≤", "40"]], [["volr_336_720_d4", "≥", "80"], ["rng6", "≥", "80"], ["hh24_d1", "≤", "20"], ["m_last5", "≤", "40"]], [["volr_48_720", "≥", "60"], ["volr_336_720_d4", "≥", "80"], ["rng72_d4", "≥", "60"], ["hh24_d1", "≤", "20"], ["m_last5", "≤", "40"]], [["ret240_d1", "≤", "20"], ["dnw1", "≤", "20"], ["rn_xdn_4", "≥", "80"]], [["volr_24_720_d4", "≥", "60"], ["volr_336_720_d4", "≥", "80"], ["rng24", "≥", "60"], ["hh24_d1", "≤", "20"], ["m_last5", "≤", "40"]], [["ret72_d1", "≤", "40"], ["ret240_d1", "≤", "20"], ["dnw1_z", "≤", "20"], ["rn_xdn_4", "≥", "80"]], [["ret16_d1", "≤", "20"], ["p2_vwapdev_mean4", "≤", "20"], ["rn_xdn_4_z", "≥", "80"]], [["ret16_d1", "≤", "20"], ["hh48", "≤", "20"], ["p2_vwapdev_mean4_z", "≤", "20"]], [["volr_48_720", "≥", "60"], ["volr_336_720_d4", "≥", "80"], ["emax_6_24_d1", "≤", "20"], ["p2_vwapdev_mean4_z", "≤", "20"]], [["volr_168_720_d4", "≥", "80"], ["rng6", "≥", "60"], ["hh24_d1", "≤", "20"], ["m_last5", "≤", "40"]], [["volr_24_720", "≥", "60"], ["volr_336_720_d4", "≥", "80"], ["emax_6_24_d1", "≤", "20"], ["p2_vwapdev_mean4_z", "≤", "20"], ["rn_xdn_4", "≥", "80"]], [["m_lo_pos", "≥", "80"], ["rn_xdn_4", "≥", "80"]], [["volr_168_720_d4", "≥", "80"], ["hh24_d1", "≤", "20"], ["m_last5_z", "≤", "40"]], [["volr_336_720_d4", "≥", "80"], ["hh24_d1", "≤", "20"], ["m_last5", "≤", "40"]], [["volr_168_720_d4", "≥", "80"], ["hh24_d1", "≤", "20"], ["m_last5", "≤", "40"]], [["ret16_d1", "≤", "20"], ["emax_336_720_d4", "≤", "20"], ["ll720_d4", "≤", "20"], ["p2_vwapdev_mean4_z", "≤", "20"]], [["ret2", "≤", "20"], ["dnw1", "≤", "20"]], [["volr_336_720_d4", "≥", "80"], ["rng24_d4", "≥", "80"], ["hh24_d1", "≤", "20"], ["m_last5", "≤", "40"]]]
def tes_features(o, MIC, P2):
    """20 kuralın kullandığı 27 özellik (laboratuvar tanımlarıyla birebir)."""
    c, h, l, op = o.close, o.high, o.low, o.open; lr = np.log(c).diff(); v720 = lr.rolling(720, min_periods=168).std(); Bs = {}
    for k in [2, 16, 72, 240]: Bs[f"ret{k}"] = np.log(c / c.shift(k)) / (v720 * np.sqrt(k))
    V = {k: lr.rolling(k).std() for k in [24, 48, 168, 336, 720]}
    for a in [24, 48, 168, 336]: Bs[f"volr_{a}_720"] = V[a] / (V[720] + 1e-12)
    rng = (h - l) / c; rm = rng.rolling(720, min_periods=168).mean() + 1e-12
    for k in [6, 24, 72]: Bs[f"rng{k}"] = rng.rolling(k).mean() / rm
    Bs["dnw1"] = (np.minimum(c, op) - l) / (h - l + 1e-12)
    E = {k: c.ewm(span=k, adjust=False).mean() for k in [6, 24, 336, 720]}
    Bs["emax_336_720"] = np.log(E[336] / E[720]) / v720; Bs["emax_6_24"] = np.log(E[6] / E[24]) / v720
    Bs["hh24"] = np.log(c / h.rolling(24).max()) / v720; Bs["hh48"] = np.log(c / h.rolling(48).max()) / v720; Bs["ll720"] = np.log(c / l.rolling(720).min()) / v720
    Mi = MIC.reindex(o.index); Bs["m_last5"] = Mi.m_last5.astype(float); Bs["m_lo_pos"] = Mi.m_lo_pos.astype(float)
    Bs["p2_vwapdev_mean4"] = P2.reindex(o.index).p2_vwapdev_mean4.astype(float)
    unit = 10 ** (np.floor(np.log10(c)) - 1); Bs["rn_xdn_4"] = (np.floor(c / unit) < np.floor(c.shift(1) / unit)).astype(float).rolling(4).sum()
    X = pd.DataFrame(Bs, index=o.index); out = {}
    for f in X.columns:
        s = X[f]; out[f] = s; out[f + "_d1"] = s - s.shift(1); out[f + "_d4"] = s - s.shift(4)
        out[f + "_z"] = (s - s.rolling(720, min_periods=168).mean()) / (s.rolling(720, min_periods=168).std() + 1e-12)
    return pd.DataFrame(out, index=o.index).replace([np.inf, -np.inf], np.nan)
def tes_eval(TF, THR):
    """THR: [[(özellik, '≤'/'≥', eşik), ...], ...] → her saat için 'en az bir kural tetiklendi mi'."""
    U = pd.Series(False, index=TF.index)
    for rule in THR:
        m = pd.Series(True, index=TF.index)
        for f, op, thr in rule: m &= (TF[f] <= thr) if op == "≤" else (TF[f] >= thr)
        U |= m.fillna(False)
    return U
TG_LAST = {"ok": None, "info": ""}
KUYRUK_F = "durum/tg_kuyruk.json"
def tg_send(text, oncelik=None, etiket=None):
    """Telegram'a gönderir; başarısızsa bir kez daha dener. Sonuç TG_LAST'e yazılır (teşhis için).
    TG_SIRALI=1 ise (saatlik iş) mesaj hemen gitmez: kuyruğa yazılır, işin sonunda gonder.py öncelik sırasıyla (en iyisi üstte) gönderir.
    oncelik: sira_puani() (küçük = önce) · yoksa rapor/bilgi sayılır, sinyallerden sonra gider. etiket: sıralama listesindeki kısa ad."""
    global TELEGRAM_CHAT_ID
    if os.environ.get("TG_SIRALI") == "1":
        try:
            q = json.load(open(KUYRUK_F, encoding="utf-8")) if os.path.exists(KUYRUK_F) else []
            q.append(dict(o=float(oncelik) if oncelik is not None else 9999.0, e=etiket or text.split("\n")[0][:70], m=text, t=time.time(), s=len(q)))
            os.makedirs(os.path.dirname(KUYRUK_F), exist_ok=True); json.dump(q, open(KUYRUK_F, "w", encoding="utf-8"), ensure_ascii=False)
            TG_LAST.update(ok=True, info="sıraya alındı (gonder.py gönderir)"); return True
        except Exception as e: print(f"⚠️ kuyruk yazılamadı, doğrudan gönderiliyor: {e}")
    if not TELEGRAM_TOKEN: TG_LAST.update(ok=False, info="TELEGRAM_TOKEN boş (gizli ayar gelmedi)"); print("(Telegram token yok — mesaj gönderilmedi)"); return False
    for deneme in range(2):
        try:
            if not TELEGRAM_CHAT_ID:
                up = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates", timeout=15).json().get("result", [])
                if up: TELEGRAM_CHAT_ID = str(up[-1].get("message", up[-1].get("channel_post", {})).get("chat", {}).get("id", ""))
            r = requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data=dict(chat_id=TELEGRAM_CHAT_ID, text=text[:4000]), timeout=20)
            if r.status_code == 200: TG_LAST.update(ok=True, info="gönderildi"); return True
            TG_LAST.update(ok=False, info=f"HTTP {r.status_code}: {r.text[:200]}"); print("⚠️ Telegram hatası:", r.text[:300])
        except Exception as e:
            TG_LAST.update(ok=False, info=f"istisna: {type(e).__name__}: {str(e)[:160]}"); print(f"⚠️ Telegram hatası: {str(e)[:200]}")
        time.sleep(3)
    return False
# ---- 💵 Coinbase primi (ABD alıcıları) — araştırma: bosluklar2.py, cb_kontrol.py, birlesim.py ----
# Prim = log(Coinbase BTC-USD / Binance BTCUSDT), son 30 güne göre z. Model ↑ sinyali z > 0 iken (ABD normalden fazla ödüyor) geçmişte belirgin daha isabetli/kârlı,
# z ≤ −1 iken (ABD satıyor) sinyaller kaybettirdi. Aynı saatlik çalışmada tek kez hesaplanır (durum/cb_prim.json), diğer betikler dosyadan okur.
def cb_prim(nm="BTC", path=None):
    import json
    path = path or ("durum/cb_prim.json" if nm == "BTC" else f"durum/cb_prim_{nm}.json")
    try:
        d = json.load(open(path))
        if time.time() - d["hesap"] < 1800: return d
    except Exception: pass
    try:
        now = pd.Timestamp.now(tz="UTC").floor("h"); out = []; s = requests.Session(); s.headers.update({"User-Agent": "btc-tahmin"})
        for k in (3, 2, 1):
            a, b = now - pd.Timedelta(hours=300 * k), now - pd.Timedelta(hours=300 * (k - 1))
            for _ in range(3):
                r = s.get(f"https://api.exchange.coinbase.com/products/{nm}-USD/candles", params=dict(granularity=3600, start=a.isoformat(), end=b.isoformat()), timeout=20)
                if r.status_code == 404: return None                                         # bu coin Coinbase'de yok
                if r.status_code == 200: out += r.json(); break
                time.sleep(1.5)
        cb = pd.DataFrame(out, columns=["t", "low", "high", "open", "close", "volume"]).drop_duplicates("t")
        cb = pd.Series(cb.close.values.astype(float), index=pd.to_datetime(cb.t, unit="s", utc=True) + pd.Timedelta(hours=1)).sort_index()
        if len(out) < 200: return None
        bn = fetch_1h((now - pd.Timedelta(hours=920)).timestamp() * 1000, time.time() * 1000, sym=f"{nm}USDT").close
        p = np.log(cb / bn.reindex(cb.index)).dropna(); p = p[p.index <= bn.index[-1]]
        z = (p - p.rolling(720, min_periods=168).mean()) / (p.rolling(720, min_periods=168).std() + 1e-12)
        if len(z) == 0 or pd.Timestamp.now(tz="UTC") - z.index[-1] > pd.Timedelta(hours=3) or not np.isfinite(z.iloc[-1]):   # eksik/eski veri: prim yok say (eski z ile sinyal verme)
            print(f"⚠️ {nm} Coinbase primi eski ya da eksik (son {z.index[-1] if len(z) else '—'}) — kullanılmadı"); return None
        d = dict(z=float(z.iloc[-1]), bp=float(p.iloc[-1] * 1e4), t=str(z.index[-1]), hesap=time.time())
        os.makedirs(os.path.dirname(path), exist_ok=True); json.dump(d, open(path, "w")); return d
    except Exception as e:
        print(f"⚠️ {nm} Coinbase primi alınamadı:", str(e)[:200]); return None
def cb_z(d): return float(d["z"]) if d and np.isfinite(d.get("z", np.nan)) else float("nan")
def cb_satir(d):
    z = cb_z(d)
    if not np.isfinite(z): return "💵 ABD (Coinbase primi): bu saat alınamadı"
    if z >= 1: return f"💵 ABD güçlü alıyor (Coinbase primi z {z:+.1f}) ✅ onaylı — geçmişte bu durumda isabet ve kâr en yüksek"
    if z > 0: return f"💵 ABD alıyor (Coinbase primi z {z:+.1f}) ✅ onaylı"
    if z > -1: return f"💵 ABD almıyor (Coinbase primi z {z:+.1f}) ⚠️ onaysız — geçmişte isabet ve kâr daha düşük"
    return f"💵 ABD satıyor (Coinbase primi z {z:+.1f}) ⛔ ALMA — geçmişte bu durumda BTC ⭐ %52, 4/8 saat ↑ sinyalleri %51–56 tuttu (ABD alırken %58–69)"   # prim_hepsi.py, 2024+
def cb_ozet(x):                                                                              # haftalık rapor: onaylı / onaysız ayrımı
    a = [e for e in x if np.isfinite(e.get("cb", np.nan)) and e["cb"] > 0]; b = [e for e in x if np.isfinite(e.get("cb", np.nan)) and e["cb"] <= 0]
    f = lambda v: f"{sum(e['ok'] for e in v)}/{len(v)} tuttu (%{100*sum(e['ok'] for e in v)/len(v):.0f})" if v else "yok"
    return f"💵 ABD onaylı (prim z > 0): {f(a)} · onaysız: {f(b)}" if (a or b) else ""
# Coin sinyallerinde coin'in KENDİ Coinbase primi (BTC primi coin'lerde işe yaramadı). prim_hepsi.py (08.10.2026, tüm sinyal türleri, 15 coin): 2026'da coin sinyalleri
# ⛔ (z ≤ −1) %48, ✅ (z > 0) %64; 2024+'da 15 coin'in 14'ünde ✅ > ⛔ — DOGE, NEAR, PEPE dahil (önceki dar testteki 'yalnız bilgi' istisnası kaldırıldı).
CB_BILGI = set()
def cb_kisa(d):
    z = cb_z(d)
    if not np.isfinite(z): return "?"
    return f"{'✅' if z > 0 else ('⚠️' if z > -1 else '⛔')} z {z:+.1f}"
def cb_satir_coin(nm, d_own, d_btc):
    z = cb_z(d_own); btc = f" · BTC geneli: {cb_kisa(d_btc)}"
    if not np.isfinite(z): return f"💵 {nm} için Coinbase primi yok · BTC geneli: {cb_kisa(d_btc)} (coin'lerde BTC primi işe yaramadı — yalnız bilgi)"
    if nm in CB_BILGI: return f"💵 {nm} Coinbase primi z {z:+.1f} (bu coin'de prim filtresi geçmişte işe yaramadı — yalnız bilgi){btc}"
    if z >= 1: return f"💵 {nm}: ABD güçlü alıyor (kendi Coinbase primi z {z:+.1f}) ✅ onaylı{btc}"
    if z > 0: return f"💵 {nm}: ABD alıyor (kendi Coinbase primi z {z:+.1f}) ✅ onaylı{btc}"
    if z > -1: return f"💵 {nm}: ABD almıyor (kendi Coinbase primi z {z:+.1f}) ⚠️ onaysız — geçmişte isabet daha düşük{btc}"
    return f"💵 {nm}: ABD SATIYOR (kendi Coinbase primi z {z:+.1f}) ⛔ ALMA — geçmişte bu durumda coin sinyalleri 2026'da %48 tuttu (ABD alırken %64){btc}"
def cb_coin_z(nm, d_own, d_btc):                                                             # kayıt için: coin'in kendi primi (yoksa BTC'ninki)
    z = cb_z(d_own); return z if np.isfinite(z) else cb_z(d_btc)
# ---- 📋 MESAJ ÖNCELİK SIRASI: aynı saatte gelen sinyaller en iyisi üstte (gonder.py) ----
# Tür sırası araştırmadaki 2024+ isabet · işlem başı net'e göre (merdiven.py, satis.py, zincir3.py, tipler3.py; ⛔ olanlar hariç):
#   ⛓️ ETH arz/talep AL %61 · +%2,5 (7 g) ve 🧑 küçük yatırımcı %66 · +%2,9 (7 g) → 🤝 BTC ile ortak %62 · +%0,23 (2026 %67) → 🔇 BTC sessizken %62 · +%0,29 →
#   🪙 coin tek başına %59 · +%0,13 → 🧪 24 saat %56 · +%0,69 → 💵 ABD alıyor (tek başına) %54 · +%0,72 → ₿ BTC saatlik/⭐/A %58 · +%0,05 → 🔻 kısa %51 · +%0,36 → ℹ️ bilgi.
# Aynı türde coin'in kendi Coinbase primi yüksek olan önce (merdiven: prim yükseldikçe isabet ve kâr artıyor). ⛔ (ABD satıyor) olanlar en sona.
SIRA_TUR = {"⛓️": 1, "🧑": 1, "🤝": 2, "🔇": 3, "🪙": 4, "🧪": 5, "💵": 6, "₿": 7, "🔻": 8, "ℹ️": 9}
def sira_puani(tur, z=float("nan"), alma=False):
    g = SIRA_TUR.get(tur, 9) + (20 if alma else 0); zz = float(z) if z is not None and np.isfinite(z) else -1.0
    return g * 100 - max(-5.0, min(5.0, zz)) * 10
def fiyat_yaz(p):
    if p is None or not np.isfinite(p) or p <= 0: return "$?"
    if p >= 1000: return f"${p:,.0f}"
    if p >= 1: return f"${p:,.3f}"
    return f"${p:.{min(12, 3 - int(np.floor(np.log10(p))))}f}"
CIKIS_NOT = "kâr-al / stop koyma"                                                             # cikis.py: 9 sinyal türünde 19 çıkış stratejisi — kâr-al, zarar-kes, iz süren stop hiçbirinde süre dolunca satmayı geçmedi
def hiz_notu(z):                                                                              # prim_pencere.py (30 gün z, 49 coin, 2024+) + cikis.py: z ≥ 3'te 4 saatte çıkmak kârı ~%60 düşürdü
    if z is None or not np.isfinite(z) or z < 1: return ""
    if z >= 3: return "⚡ Prim çok yüksek (z ≥ 3): yükseliş hızlı başlıyor (ilk 4 saatte belirgin) ve günlerce sürebiliyor — hemen gir, ERKEN ÇIKMA (testte 4 saatte çıkmak kârı ~%60 düşürdü)"
    if z >= 2: return "⏩ Prim yüksek (z 2–3): yükseliş kademeli, 1–3 güne yayılıyor — hemen gir, erken çıkma"
    return "🐢 Prim normalin üstünde (z 1–2): yükseliş yavaş, günlere yayılıyor — erken çıkma"
def giris_cikis(p, cikis_t, ort, yon=1, giris="Giriş (limit)"):
    """p: giriş fiyatı · cikis_t: çıkış zamanı (UTC) · ort: geçmişte bu sinyalin ortalama BRÜT getirisi % (yön dahil, komisyon öncesi)."""
    c = f"{giris} {fiyat_yaz(p)} → çıkış {pd.Timestamp(cikis_t).tz_convert(DISPLAY_TZ):%d.%m %H:%M}'de {'sat' if yon > 0 else 'kapat'} ({CIKIS_NOT})"
    if ort is not None and np.isfinite(ort): c += f" · geçmiş ort. sonuç {'+' if ort >= 0 else '−'}%{abs(ort):.2f}"
    return c
