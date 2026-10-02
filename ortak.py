# ortak.py — v32 modelinin GitHub Actions sürümü için ortak parçalar (egit.py ve tahmin.py kullanır)
import os, io, time, zipfile, warnings, requests, numpy as np, pandas as pd
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
def fetch_1h(start_ms, end_ms, verbose=False):
    for url in EP:
        try:
            rows, cur = [], int(start_ms)
            while cur < end_ms:
                r = requests.get(url, params=dict(symbol=SYMBOL, interval="1h", startTime=cur, endTime=int(end_ms), limit=1000), timeout=20)
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
def _mzip(ym):
    url = f"https://data.binance.vision/data/spot/monthly/klines/{SYMBOL}/1m/{SYMBOL}-1m-{ym}.zip"
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
def fetch_1m(start_ms, end_ms):
    rows, cur = [], int(start_ms)
    while cur < end_ms:
        dt = None
        for url in EP:
            try:
                r = requests.get(url, params=dict(symbol=SYMBOL, interval="1m", startTime=cur, endTime=int(end_ms), limit=1000), timeout=20)
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
TG_LAST = {"ok": None, "info": ""}
def tg_send(text):
    """Telegram'a gönderir; başarısızsa bir kez daha dener. Sonuç TG_LAST'e yazılır (teşhis için)."""
    global TELEGRAM_CHAT_ID
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
