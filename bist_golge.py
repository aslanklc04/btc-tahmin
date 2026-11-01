# bist_golge.py — 🇹🇷 BIST GÜNLÜK GÖLGE İZLEME (01.11.2026, kullanıcı onayı "olur"). MESAJ GÖNDERMEZ, yalnız kayıt.
# Araştırma: arastirma3/PROTOKOL_bist.md · bist_sonuc.md — günlük "M2 RSI 30'u yukarı · trend yok · V2 OBV 5 g ↑ · 🎯 +0,75σ·√4, en fazla 10 gün" (tek "umut verici" kural):
#   BIST 30: %74 · %74 · %72 (2010–18 · 2019–22 · 2023–26), dolar net +0,67 · +0,52 · +1,30 · diğer 33 hisse: %68 · %75 · %67, +0,37 · +1,45 · +0,22. Aday değil (iki hücre < %70) → gölgede izleniyor.
# Giriş: sinyal gününden sonraki seansın açılışı × 1,0005 · ücret %0,05/taraf · süre sonu çıkış kayması %0,05 · net DOLAR bazında · hisse başına aynı anda tek işlem.
# Veri: Yahoo (yfinance) günlük düzeltilmiş · günde bir (16 UTC, kapanıştan sonra).
# Kullanım: python bist_golge.py → durum/bist_golge.csv · .md · _durum.json   |   python bist_golge.py --dogrula bist_gun.parquet (araştırma verisiyle aynı sonuç mu)
import sys, json, time, numpy as np, pandas as pd
B30 = "AEFES AKBNK ASELS ASTOR BIMAS DSTKF EKGYO ENKAI EREGL FROTO GARAN GUBRF ISCTR KCHOL KRDMD MGROS PETKM PGSUS SAHOL SASA SISE TAVHL TCELL THYAO TOASO TRALT TTKOM TUPRS VAKBN YKBNK".split()
DOG = "AKSA AKSEN ALARK ARCLK BRSAN BTCIM CCOLA CIMSA DOAS DOHOL ECILC EFOR ENJSA GLRMK HALKB HEKTS ISMEN KONTR KTLEV MAVI MPARK ODAS OTKAR OYAKC PASEU SKBNK SOKM TKFEN TSKB TTRAK ULKER VESTL ZOREN".split()
ESKI = {"TRALT": "KOZAL"}
BASLA = pd.Timestamp("2026-11-02"); FP, SLIP, W, MULT = 0.0005, 0.0005, 10, 1.5
def indir():
    import yfinance as yf
    def al(sym):
        for i in range(4):
            try:
                d = yf.Ticker(sym).history(period="10y", interval="1d", auto_adjust=True)
                if len(d): d = d[["Open", "High", "Low", "Close", "Volume"]]; d.columns = ["o", "h", "l", "c", "v"]; d.index = d.index.tz_localize(None).normalize() if d.index.tz is None else d.index.tz_convert("Europe/Istanbul").tz_localize(None).normalize(); return d[~d.index.duplicated()]
            except Exception as e: print("hata", sym, e)
            time.sleep(3 + 3 * i)
        return None
    D = {}
    for nm in B30 + DOG:
        d = al(f"{nm}.IS")
        if nm in ESKI and (d is None or len(d) < 300):
            d0 = al(f"{ESKI[nm]}.IS"); d = d0 if d is None else (pd.concat([d0[d0.index < d.index[0]], d]) if d0 is not None else d)
        if d is not None: D[nm] = d
    U = al("TRY=X"); return D, U.c
def islemler(D, U, bas=None):
    R = []
    for nm, d in D.items():
        d = d.astype(float); d = d[(d.c > 0) & (d.o > 0)]
        if len(d) < 500: continue                                                      # araştırmayla aynı (≥ 500 gün geçmiş)
        c = d.c; dl = c.diff(); up = dl.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean(); dn = (-dl.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean(); rsi = 100 - 100 / (1 + up / dn)
        obv = (np.sign(c.diff()).fillna(0) * d.v).cumsum(); sig = np.log(c).diff().rolling(250, min_periods=125).std(); u = U.reindex(d.index, method="ffill")
        r = c.pct_change(); kirli = ((r < -0.25) | (r > 0.30)).astype(float).rolling(61, center=True, min_periods=1).max().fillna(0).values > 0
        trig = ((rsi > 30) & (rsi.shift() <= 30) & (obv - obv.shift(5) > 0)).values & ~kirli
        if bas is not None: trig &= d.index >= bas
        o, h, cl, ix, n = d.o.values, d.h.values, c.values, d.index, len(d); serbest = -1
        for i in np.where(trig)[0]:
            if i + 1 <= serbest or np.isnan(sig.iloc[i]) or np.isnan(u.iloc[i]) or i + 1 >= n: continue
            Pe = o[i + 1] * (1 + SLIP); tp = Pe * (1 + MULT * sig.iloc[i]); son = min(i + W, n - 1)
            hit = np.where(h[i + 1:son + 1] >= tp)[0]
            s = dict(sinyal_gun=ix[i], kod=nm, grup="BIST30" if nm in B30 else "diğer", rsi=round(float(rsi.iloc[i]), 1), giris=round(float(o[i + 1]), 4), hedef=round(float(tp), 4), cikis=np.nan, cikis_gun=pd.NaT, sonuc="açık", net_dolar=np.nan, net_tl=np.nan, supheli=False)
            if len(hit): j = i + 1 + hit[0]; px = tp; s["sonuc"] = "🎯"
            elif i + W <= n - 1: j = i + W; px = cl[j] * (1 - SLIP); s["sonuc"] = "süre"
            else: R.append(s); serbest = n + 10; continue                                     # açık işlem: sonraki sinyaller beklemede
            if np.isnan(u.iloc[j]): continue
            sup = bool((np.abs(r.values[i + 1:j + 1]) > 0.11).any()); g = px / Pe; s.update(supheli=sup, cikis=round(float(px), 4), cikis_gun=ix[j], net_tl=round(100 * (g - 1 - 2 * FP), 3), net_dolar=round(100 * (g * u.iloc[i] / u.iloc[j] - 1 - 2 * FP), 3)); serbest = j; R.append(s)
    return pd.DataFrame(R, columns=["sinyal_gun", "kod", "grup", "rsi", "giris", "hedef", "cikis", "cikis_gun", "sonuc", "net_dolar", "net_tl", "supheli"])
def dogrula(f):
    A = pd.read_parquet(f); A["t"] = pd.to_datetime(A.t, utc=True).dt.tz_convert("Europe/Istanbul").dt.normalize().dt.tz_localize(None)
    ser = lambda k: A[A.kod == k].set_index("t").sort_index().pipe(lambda x: x[~x.index.duplicated()])
    D = {k: ser(k)[["open", "high", "low", "close", "volume"]].set_axis(["o", "h", "l", "c", "v"], axis=1) for k in B30 + DOG if (A.kod == k).any()}
    X = islemler(D, ser("USDTRY").close, pd.Timestamp("2010-01-01")); son = {k: d.index[-12] for k, d in D.items()}; X = X[(X.sonuc != "açık") & (X.sinyal_gun <= X.kod.map(son))]   # araştırma: i ≤ n − W − 2
    for ad, a, b in (("2010–18", "2010", "2019"), ("2019–22", "2019", "2023"), ("2023–26", "2023", "2027")):
        for gr in ("BIST30", "diğer"):
            y = X[(X.grup == gr) & (X.sinyal_gun >= a) & (X.sinyal_gun < b)]; print(f"{gr:6s} {ad}: {len(y)} · %{100 * (y.net_dolar > 0).mean():.0f} · {y.net_dolar.mean():+.2f}")
def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "--dogrula": return dogrula(sys.argv[2])
    D, U = indir(); print("hisse", len(D), "/", len(B30 + DOG), "· son gün", max(d.index[-1] for d in D.values()).date())
    X = islemler(D, U); X = X[X.sinyal_gun >= BASLA].sort_values("sinyal_gun"); X.to_csv("durum/bist_golge.csv", index=False)
    b_ = X[X.sonuc != "açık"]; son = max(d.index[-1] for d in D.values())
    L = [f"# 🇹🇷 BIST gölge izleme — {pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M}", "",
         "_Mesaj göndermez. Kural: günlük RSI 14, 30'un üstüne döner + OBV 5 günde yükselir → ertesi seans açılışında AL, 🎯 +0,75σ·2 (σ = 250 g), en fazla 10 seans. Ücret %0,05/taraf, kayma %0,05, net dolar bazında. Hisse başına aynı anda tek işlem. Stop yok (araştırmadaki gibi). 63 hisse (BIST 30 + 33 büyük hisse). ⚠️ = işlem sırasında bir günde ±%11'den büyük hareket (BIST'te ±%10 sınırı var → büyük ihtimalle bedelli/bölünme düzeltmesi; sonuç şüpheli)._", "",
         f"- Başlangıç {BASLA:%d.%m.%Y} · son veri {son:%d.%m.%Y} · sinyal {len(X)} (biten {len(b_)}, açık {int((X.sonuc == 'açık').sum())})",
         "- **Canlı gölge:** " + (f"isabet %{100 * (b_.net_dolar > 0).mean():.0f} · 🎯 oranı %{100 * (b_.sonuc == '🎯').mean():.0f} · işlem başı dolar net {b_.net_dolar.mean():+.2f}% (TL {b_.net_tl.mean():+.2f}%)" if len(b_) else "henüz biten işlem yok"),
         "- **Araştırma (karşılaştırma):** BIST 30 %74 · %74 · %72 (+0,67 · +0,52 · +1,30) · diğer %68 · %75 · %67 (+0,37 · +1,45 · +0,22) · 63 hissede yılda ≈ 30–40 sinyal"]
    if len(X):
        L += ["", "| sinyal günü | hisse | grup | RSI | giriş | 🎯 | sonuç | çıkış günü | dolar net % |", "|---|---|---|---|---|---|---|---|---|"]
        L += [f"| {r.sinyal_gun:%d.%m.%Y} | {r.kod} | {r.grup} | {r.rsi:.0f} | {r.giris:.4g} | {r.hedef:.4g} | {r.sonuc} | {'—' if pd.isna(r.cikis_gun) else f'{r.cikis_gun:%d.%m}'} | {'—' if pd.isna(r.net_dolar) else f'{r.net_dolar:+.2f}'}{' ⚠️' if r.supheli else ''} |" for r in X.tail(15).itertuples()]
    open("durum/bist_golge.md", "w").write("\n".join(L) + "\n")
    json.dump(dict(guncelleme=pd.Timestamp.now(tz="UTC").isoformat(), hisse=len(D), son_veri=str(son.date()), sinyal=len(X), biten=len(b_), isabet=float((b_.net_dolar > 0).mean()) if len(b_) else None), open("durum/bist_golge_durum.json", "w"), indent=1)
    print("yazıldı", len(X))
if __name__ == "__main__": main()
