# opsiyon_kayit.py — 📈 BTC OPSİYON PİYASASI SAATLİK KAYIT (30.10.2026, 5. tur için veri toplama; MESAJ GÖNDERMEZ, sinyallere dokunmaz)
# Kaynak: Deribit herkese açık API (get_book_summary_by_currency). Satır: put/call açık pozisyon ve 24 s hacim oranı · ATM IV (≈30 g) · çarpıklık (OTM put IV − OTM call IV) · en yakın vadenin "max pain" seviyesi.
import json, time, requests, numpy as np, pandas as pd
S = requests.Session(); DOSYA = "durum/opsiyon.csv"
def get(u, **kw):
    for k in range(4):
        try:
            r = S.get(u, timeout=40, **kw)
            if r.status_code == 200: return r.json().get("result")
        except Exception: pass
        time.sleep(2 + 2 * k)
    return None
def main():
    now = pd.Timestamp.now(tz="UTC"); R = get("https://www.deribit.com/api/v2/public/get_book_summary_by_currency", params=dict(currency="BTC", kind="option"))
    ix = get("https://www.deribit.com/api/v2/public/get_index_price", params=dict(index_name="btc_usd"))
    if not R or not ix: print("deribit yanıt yok"); return
    spot = float(ix["index_price"]); d = pd.DataFrame(R); p = d.instrument_name.str.split("-", expand=True)
    d["vade"] = pd.to_datetime(p[1], format="%d%b%y", utc=True) + pd.Timedelta(hours=8); d["kul"] = pd.to_numeric(p[2], errors="coerce"); d["tur"] = p[3]
    d["gun"] = (d.vade - now).dt.total_seconds() / 86400; d["m"] = d.kul / spot - 1
    for c in ("open_interest", "volume", "mark_iv"): d[c] = pd.to_numeric(d[c], errors="coerce")
    P, C = d[d.tur == "P"], d[d.tur == "C"]
    def iv(x): x = x[x.mark_iv > 0]; return float(x.mark_iv.mean()) if len(x) else np.nan
    v30 = d.loc[(d.gun > 1), "vade"].drop_duplicates(); v30 = v30.iloc[(((v30 - now).dt.total_seconds() / 86400) - 30).abs().argsort()].iloc[0] if len(v30) else None
    orta = (d.gun >= 7) & (d.gun <= 60); kisa = (d.gun > 0.5) & (d.gun <= 7)
    yak = d.loc[d.gun > 1, "vade"].min(); Y = d[d.vade == yak]; ks = np.sort(Y.kul.unique())
    agri = [((np.clip(k - Y[Y.tur == "C"].kul, 0, None) * Y[Y.tur == "C"].open_interest).sum() + (np.clip(Y[Y.tur == "P"].kul - k, 0, None) * Y[Y.tur == "P"].open_interest).sum()) for k in ks]
    mp = float(ks[int(np.argmin(agri))]) if len(ks) else np.nan
    row = dict(t=now.floor("h").isoformat(), endeks=round(spot, 2), pc_oi=round(P.open_interest.sum() / max(C.open_interest.sum(), 1e-9), 4), pc_hacim=round(P.volume.sum() / max(C.volume.sum(), 1e-9), 4),
               oi_btc=round(d.open_interest.sum(), 1), hacim_btc=round(d.volume.sum(), 1),
               atm_iv30=round(iv(d[(d.vade == v30) & (d.m.abs() <= 0.02)]), 2) if v30 is not None else np.nan,
               skew_orta=round(iv(P[orta & (P.m <= -0.05) & (P.m >= -0.15)]) - iv(C[orta & (C.m >= 0.05) & (C.m <= 0.15)]), 2),
               skew_kisa=round(iv(P[kisa & (P.m <= -0.03) & (P.m >= -0.10)]) - iv(C[kisa & (C.m >= 0.03) & (C.m <= 0.10)]), 2),
               maxpain=mp, maxpain_vade=str(yak.date()) if pd.notna(yak) else "", maxpain_uzaklik=round(mp / spot - 1, 4) if np.isfinite(mp) else np.nan, enstruman=len(d))
    try: E = pd.read_csv(DOSYA)
    except Exception: E = pd.DataFrame()
    E = pd.concat([E, pd.DataFrame([row])], ignore_index=True).drop_duplicates("t", keep="last"); E.to_csv(DOSYA, index=False)
    print(json.dumps(row, ensure_ascii=False))
if __name__ == "__main__": main()
