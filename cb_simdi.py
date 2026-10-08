# cb_simdi.py — her coin için ŞU ANKİ Coinbase primi (ortak.cb_prim ile, canlı sistemle aynı hesap): z (son 30 güne göre) ve baz puan
import os, numpy as np, pandas as pd
from ortak_canli import *
os.makedirs("tmp_cb", exist_ok=True); L = []
CL = ["BTC"] + [l.strip().replace("USDT", "") for l in open("durum/coin_listesi.txt") if l.strip()]
L.append(f"# 💵 Coinbase primi — {pd.Timestamp.now(tz=DISPLAY_TZ):%d.%m.%Y %H:%M}\n| Coin | Prim (baz puan) | z (son 30 güne göre) | Durum |\n|---|---|---|---|")
for nm in CL:
    d = cb_prim(nm, path=f"tmp_cb/{nm}.json")
    if not d: L.append(f"| {nm} | — | — | Coinbase'de yok ya da alınamadı |"); continue
    z = d["z"]; st = "✅ ABD alıyor" if z > 0 else ("⚠️ ABD almıyor" if z > -1 else ("⛔ ABD satıyor" if z > -2 else "⛔⛔ ABD güçlü satıyor"))
    if z >= 1: st = "✅✅ ABD güçlü alıyor" if z >= 2 else "✅ ABD alıyor (normalin üstü)"
    L.append(f"| {nm} | {d['bp']:+.1f} | {z:+.2f} | {st}{' (bu coin’de filtre yalnız bilgi)' if nm in CB_BILGI else ''} |")
open("cb_simdi_sonuc.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
