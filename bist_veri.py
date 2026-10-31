# bist_veri.py — PROTOKOL_bist.md verisi (Actions; yfinance). Çıktı: bist_saat.parquet · bist_gun.parquet · bist_veri_rapor.txt
import time, pandas as pd, yfinance as yf
B30 = "AEFES AKBNK ASELS ASTOR BIMAS DSTKF EKGYO ENKAI EREGL FROTO GARAN GUBRF ISCTR KCHOL KRDMD MGROS PETKM PGSUS SAHOL SASA SISE TAVHL TCELL THYAO TOASO TRALT TTKOM TUPRS VAKBN YKBNK".split()
DOG = "AKSA AKSEN ALARK ARCLK BRSAN BTCIM CCOLA CIMSA DOAS DOHOL ECILC EFOR ENJSA GLRMK HALKB HEKTS ISMEN KONTR KTLEV MAVI MPARK ODAS OTKAR OYAKC PASEU SKBNK SOKM TKFEN TSKB TTRAK ULKER VESTL ZOREN".split()
ESKI = {"TRALT": "KOZAL"}                                                 # isim değişikliği: eski kodun geçmişi öne eklenir
EK = {"XU030": "XU030.IS", "XU100": "XU100.IS", "USDTRY": "TRY=X"}
def al(sym, **k):
    for i in range(4):
        try:
            d = yf.Ticker(sym).history(auto_adjust=True, **k)
            if len(d): return d[["Open", "High", "Low", "Close", "Volume"]].rename(columns=str.lower)
        except Exception as e: print("hata", sym, e)
        time.sleep(3 + 3 * i)
    return None
G, S, R = [], [], []
for nm in B30 + DOG + list(EK):
    sym = EK.get(nm, f"{nm}.IS")
    g = al(sym, start="2009-01-01", interval="1d"); s = al(sym, period="730d", interval="60m")
    if nm in ESKI:
        g0 = al(f"{ESKI[nm]}.IS", start="2009-01-01", interval="1d")
        if g0 is not None and g is not None: g = pd.concat([g0[g0.index < g.index[0]], g]); 
        elif g is None: g = g0
        s0 = al(f"{ESKI[nm]}.IS", period="730d", interval="60m")
        if s0 is not None and s is not None: s = pd.concat([s0[s0.index < s.index[0]], s])
        elif s is None: s = s0
    for x, L in ((g, G), (s, S)):
        if x is not None:
            x = x.copy(); x.index = x.index.tz_convert("UTC") if x.index.tz else x.index.tz_localize("UTC"); x["kod"] = nm
            x["grup"] = "B30" if nm in B30 else ("DOG" if nm in DOG else "EK"); L.append(x)
    R.append(f"{nm:7s} gün {0 if g is None else len(g):5d} ({'—' if g is None else g.index[0].date()}) · saat {0 if s is None else len(s):5d} ({'—' if s is None else s.index[0]})")
    print(R[-1], flush=True)
pd.concat(G).rename_axis("t").reset_index().to_parquet("bist_gun.parquet"); pd.concat(S).rename_axis("t").reset_index().to_parquet("bist_saat.parquet")
open("bist_veri_rapor.txt", "w").write("\n".join(R) + "\n"); print("bitti")
