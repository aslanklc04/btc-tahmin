# canli_dok.py — altcoin canlı iç ölçüm günlüğünü (durum/gecmis_coin.pkl) CSV'ye döker (analiz için, 17.10.2026)
import pandas as pd, numpy as np
o = pd.read_pickle("durum/gecmis_coin.pkl"); rows = []
for sym, st in (o.items() if isinstance(o, dict) else []):
    if not isinstance(st, dict): continue
    for e in st.get("log", []):
        if isinstance(e, dict): rows.append({"sym": sym, **{k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in e.items() if not isinstance(v, (dict, list))}})
D = pd.DataFrame(rows); D.to_csv("canli_coin_log.csv", index=False); print(D.shape); print(D.columns.tolist()); print(D.tail(5).to_string())
o2 = pd.read_pickle("durum/gecmis.pkl"); B = pd.DataFrame([{k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in e.items() if not isinstance(v, (dict, list))} for e in o2.get("log", []) if isinstance(e, dict)])
B.to_csv("canli_btc_log.csv", index=False); print(B.shape, B.columns.tolist())
