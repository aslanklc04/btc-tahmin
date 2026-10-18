# canli_kopya.py — DENETİM (18.10.2026, yalnız bilgi): canlıdaki tahminler testteki yöntemle AYNI mı?
# 1) Sızıntı testi: özellikler / sinyal eşikleri / prim z, veri t anında kesilince değişiyor mu? (değişirse gelecek veri kullanılıyor demektir)
# 2) Canlı kopya: canlının bu hafta kaydettiği tahminler (durum/gecmis*.pkl önbelleği) aynı modelle TAZE veriden yeniden hesaplanır;
#    olasılık farkı ve "Çok güçlü ↑" bayrağı farkı ölçülür. Fark yoksa canlı boru hattı testle aynıdır.
# 3) Gönderilen sinyallerin prim z değeri araştırma yöntemiyle (uzun Coinbase geçmişi) yeniden hesaplanır.
# Main kökünden çalışır (main'in ortak.py'si kullanılır).
import os, glob, gzip, pickle, re, time, traceback, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from ortak import *
L = []
def yaz(s=""): print(s, flush=True); L.append(str(s))
T0 = time.time(); NOW = pd.Timestamp.now(tz="UTC"); now_ms = NOW.timestamp() * 1000
def _merge(old, new_):
    x = pd.concat([old, new_]) if len(new_) else old; return x[~x.index.duplicated(keep="last")].sort_index()
def oku(p):
    with gzip.open(p, "rb") as f: return pickle.load(f)
yaz(f"# 🔍 Canlı = test denetimi — {NOW.tz_convert(DISPLAY_TZ):%d.%m.%Y %H:%M}\n")
# ======================= 1) SIZINTI TESTİ =======================
yaz("## 1) Sızıntı testi (veri t anında kesilince sonuç aynı mı?)")
rg = np.random.default_rng(1)
for sym in ("BTCUSDT", "ETHUSDT", "OPUSDT", "LDOUSDT"):
    try:
        o = fetch_1h(now_ms - 4000 * 3_600_000, now_ms, sym=sym); mn = fetch_1m(now_ms - 400 * 3_600_000, now_ms, sym=sym)
        F = features(o); MIC = micro_features(mn).iloc[1:]; HH = hourly_cv(mn).iloc[1:]; P2 = path2_features(o.close, HH, MIC)
        lr = np.log(o.close); fake = 1 / (1 + np.exp(-(lr.diff(4).fillna(0) * 30)))                      # sahte olasılık serisi (eşik testi için)
        SF = signal_frame(fake, fake.rolling(3).mean().bfill(), F.r4, False); zt = cz(fake)
        en = dict(F=0.0, MIC=0.0, P2=0.0, SF=0.0, cz=0.0)
        for t in o.index[rg.integers(len(o) - 300, len(o) - 5, 12)]:
            ok_ = o.loc[:t]; mk = mn.loc[:t]
            Ft = features(ok_).iloc[-1]; en["F"] = max(en["F"], float(np.nanmax(np.abs((Ft - F.loc[t]).values.astype(float)))))
            Mt = micro_features(mk).iloc[1:]; Ht = hourly_cv(mk).iloc[1:]
            en["MIC"] = max(en["MIC"], float(np.nanmax(np.abs((Mt.iloc[-1] - MIC.loc[t]).values.astype(float)))))
            P2t = path2_features(ok_.close, Ht, Mt).iloc[-1]; en["P2"] = max(en["P2"], float(np.nanmax(np.abs((P2t - P2.loc[t]).values.astype(float)))))
            St = signal_frame(fake.loc[:t], fake.rolling(3).mean().bfill().loc[:t], F.r4.loc[:t], False).iloc[-1]
            en["SF"] = max(en["SF"], float(np.nanmax(np.abs((St - SF.loc[t]).values.astype(float))))); en["cz"] = max(en["cz"], abs(float(cz(fake.loc[:t]).iloc[-1] - zt.loc[t])))
        yaz(f"- {sym[:-4]}: en büyük fark — özellikler {en['F']:.1e} · saat içi {en['MIC']:.1e} · yol {en['P2']:.1e} · sinyal/eşik {en['SF']:.1e} · z {en['cz']:.1e} → "
            + ("✅ sızıntı yok" if max(en.values()) < 1e-5 else "❌ FARK VAR (gelecek veri kullanılıyor olabilir)"))
    except Exception as e: yaz(f"- {sym}: test edilemedi {type(e).__name__} {str(e)[:150]}")
# prim z: canlı (900 saat Coinbase) ile araştırma (uzun geçmiş) yöntemi
UA = {"User-Agent": "btc-tahmin-denetim"}
def cb_seri(nm, a, b):
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
    return pd.Series(d.close.values.astype(float), index=pd.to_datetime(d.t, unit="s", utc=True) + pd.Timedelta(hours=1)).sort_index()
def z_arastirma(nm, cb, bn):
    ix = bn.index[bn.index >= cb.index[0]]; p = np.log(cb.reindex(ix) / bn.reindex(ix)); return (p - p.rolling(720, min_periods=168).mean()) / (p.rolling(720, min_periods=168).std() + 1e-12)
def z_canli(cb, bn, t):                                                                            # ortak.cb_prim ile aynı: t'den geriye 900 saat, dropna, 720 gözlem
    c = cb[(cb.index > t - pd.Timedelta(hours=900)) & (cb.index <= t)]; b = bn[(bn.index > t - pd.Timedelta(hours=920)) & (bn.index <= t)]
    p = np.log(c / b.reindex(c.index)).dropna(); z = (p - p.rolling(720, min_periods=168).mean()) / (p.rolling(720, min_periods=168).std() + 1e-12); return float(z.iloc[-1]) if len(z) else np.nan
# ======================= 3) gönderilen sinyallerin prim z'si =======================
K = pd.read_csv("durum/karne_kayit.csv"); K = K[K.s != "panel"].copy(); RZ = []
for _, r in K.iterrows():
    t = (pd.Timestamp(r.t, tz=DISPLAY_TZ).floor("h")).tz_convert("UTC")
    for nm, zv in re.findall(r"([A-Z0-9]{2,10}) \(z ([+\-−]?\d+\.\d)", r.e): RZ.append((t, nm, float(zv.replace("−", "-")), r.s, r.e.split(":")[0][:30]))
    m = re.search(r"([A-Z0-9]{2,10}) .*?prim ✅ z ([+-]?\d+\.\d)", r.e)
    if m: RZ.append((t, m.group(1), float(m.group(2)), r.s, r.e[:30]))
RZ = pd.DataFrame(RZ, columns=["t", "nm", "z_mesaj", "s", "tur"])
def prim_kontrol(nm):
    try:
        cb = cb_seri(nm, NOW - pd.Timedelta(days=150), NOW); bn = fetch_1h(now_ms - 150 * 24 * 3_600_000, now_ms, sym=f"{nm}USDT").close
        if cb is None: return nm, None
        za = z_arastirma(nm, cb, bn); return nm, (cb, bn, za)
    except Exception as e: print(nm, e); return nm, None
with ThreadPoolExecutor(4) as ex: PRZ = dict(ex.map(prim_kontrol, sorted(set(RZ.nm))))
za_, zc_ = [], []
for r in RZ.itertuples():
    d = PRZ.get(r.nm)
    if d is None: za_.append(np.nan); zc_.append(np.nan); continue
    cb, bn, za = d; za_.append(float(za.reindex([r.t]).iloc[0]) if r.t in za.index else np.nan); zc_.append(z_canli(cb, bn, r.t))
RZ["z_arastirma"] = np.round(za_, 2); RZ["z_canli_yeniden"] = np.round(zc_, 2); RZ["fark"] = (RZ.z_mesaj - RZ.z_arastirma).round(2)
yaz("\n## 3) Gönderilen sinyallerde coin primi z: mesajdaki ↔ araştırma yöntemi (aynı saat, taze veri)")
yaz(f"- {len(RZ)} coin-sinyal · |fark| ortalama {RZ.fark.abs().mean():.2f} · |fark| > 0,5 olan {int((RZ.fark.abs() > 0.5).sum())} · eşik tarafı değişen (mesaj ≥ 0 ama araştırma < 0 ya da tersi): "
    f"{int(((RZ.z_mesaj >= 0) != (RZ.z_arastirma >= 0)).sum())} · ≥ 2 tarafı değişen: {int(((RZ.z_mesaj >= 2) != (RZ.z_arastirma >= 2)).sum())}")
yaz("```"); yaz(RZ.assign(t=RZ.t.dt.tz_convert(DISPLAY_TZ).dt.strftime("%d.%m %H")).to_string(index=False)); yaz("```")
# ======================= 2) CANLI KOPYA =======================
yaz("\n## 2) Canlı kopya: canlının kaydettiği tahmin ↔ aynı modelle taze veriden yeniden hesap (son 7 gün)")
GB = pickle.load(open("durum/gecmis.pkl", "rb")); GC = pickle.load(open("durum/gecmis_coin.pkl", "rb"))
BAS7 = NOW - pd.Timedelta(days=7)
def yeniden(sym, M, Gpg, Gpl, nfull, btc=False):
    full = fetch_1h(now_ms - nfull * 3_600_000, now_ms, sym=sym); mins = fetch_1m(now_ms - 220 * 3_600_000, now_ms, sym=sym)
    MIC = micro_features(mins).iloc[1:]; HHM = hourly_cv(mins).iloc[1:]; MIC, HHM = MIC[MIC.index <= full.index[-1]], HHM[HHM.index <= full.index[-1]]
    MICX = _merge(M.get("MIC_TAIL", MIC.iloc[:0]), MIC); HHMX = _merge(M.get("HHM_TAIL", HHM.iloc[:0]), HHM)
    Fl = features(full).iloc[-2000:]; FR = {1: Fl.join(MICX.reindex(Fl.index)), 4: Fl.join(path2_features(full.close, HHMX, MICX).reindex(Fl.index)), 8: Fl}
    out = {}
    for H in CFG:
        idx = Gpg[H].index[(Gpg[H].index > M["R"][H]["PG"].index[-1]) & (Gpg[H].index >= BAS7)]; idx = idx[idx.isin(Fl.index) & (idx >= MICX.index[0] + pd.Timedelta(hours=10))]
        if not len(idx): continue
        pg, pl = M["R"][H]["model"](FR[H].loc[idx]); dpg = np.abs(pg - Gpg[H].loc[idx].values); dpl = np.abs(pl - Gpl[H].loc[idx].values)
        PGr = Gpg[H].copy(); PGr.loc[idx] = pg; PLr = Gpl[H].copy(); PLr.loc[idx] = pl
        a = signal_frame(Gpg[H], Gpl[H], Fl[f"r{H}"], False).reindex(idx); b = signal_frame(PGr, PLr, Fl[f"r{H}"], False).reindex(idx)
        ua = ((a.S > 0) & (a.C >= a.T10)).values; ub = ((b.S > 0) & (b.C >= b.T10)).values
        out[H] = dict(n=len(idx), dmax=float(max(dpg.max(), dpl.max())), dort=float((dpg.mean() + dpl.mean()) / 2), u_canli=int(ua.sum()), u_yeni=int(ub.sum()), u_fark=int((ua != ub).sum()),
                      saatler=[f"{t:%d.%m %H}" for t in idx[ua != ub]][:6])
    return out
SATIR = []
try:
    M = oku("durum/model.pkl.gz"); yaz(f"- BTC modeli {M['created']:%d.%m %H:%M} · canlı geçmişi aynı modelden mi: {'✅' if GB.get('created') == M['created'] else '❌ HAYIR'}")
    o_ = yeniden("BTCUSDT", M, GB["PG"], GB["PL"], 4000, True)
    for H, v in o_.items(): SATIR.append(("BTC", H, v))
except Exception as e: yaz(f"- BTC: {type(e).__name__} {str(e)[:200]}"); traceback.print_exc()
MF = {os.path.basename(p)[6:-7]: p for p in glob.glob("modeller/model_*.pkl.gz")}; MF.update({os.path.basename(p)[6:-7]: p for p in glob.glob("durum/model_*.pkl.gz")})
def is_(sym):
    try:
        G = GC.get(sym); p = MF.get(sym)
        if not isinstance(G, dict) or "PG" not in G or p is None: return sym, None, "kayıt/model yok"
        M = oku(p)
        if G.get("created") != M["created"]: return sym, None, "canlı geçmişi başka modelden"
        return sym, yeniden(sym, M, G["PG"], G["PL"], 3200), ""
    except Exception as e: return sym, None, f"{type(e).__name__} {str(e)[:80]}"
syms = sorted(k for k in GC if isinstance(GC[k], dict) and "PG" in GC[k]); yaz(f"- canlı önbellekte {len(syms)} coin")
with ThreadPoolExecutor(6) as ex: RES = list(ex.map(is_, syms))
atl = [(s, m) for s, o, m in RES if o is None]
for s, o, m in RES:
    if o: SATIR += [(s[:-4], H, v) for H, v in o.items()]
T = pd.DataFrame([dict(coin=c, H=H, **{k: v for k, v in d.items() if k != "saatler"}, saatler=" ".join(d["saatler"])) for c, H, d in SATIR])
yaz(f"- yeniden hesaplanan: {T.coin.nunique() if len(T) else 0} coin · atlanan {len(atl)}: " + ", ".join(f"{s[:-4]} ({m})" for s, m in atl[:15]))
if len(T):
    for H in CFG:
        x = T[T.H == H]
        if len(x): yaz(f"- {H} saat: {x.n.sum()} tahmin · olasılık farkı ort {x.dort.mean():.1e} · en büyük {x.dmax.max():.1e} · 'Çok güçlü ↑' saat: canlı {x.u_canli.sum()} / yeniden {x.u_yeni.sum()} · farklı {x.u_fark.sum()}")
    yaz("```"); yaz(T.sort_values(["u_fark", "dmax"], ascending=False).head(40).to_string(index=False)); yaz("```")
yaz(f"\n_süre {(time.time() - T0) / 60:.0f} dk_")
open("canli_kopya_sonuc.md", "w").write("\n".join(L) + "\n")
