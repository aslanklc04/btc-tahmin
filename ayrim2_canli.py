# ayrim2_canli.py — PROTOKOL_ayrim.md Ek 1 T6 (canlı hesap eşitliği) + T7 (canlı karne, bilgi). Actions: m/ = main kopyası, gonder_aday.py = önerilen gonder.py
import os, sys, shutil, numpy as np, pandas as pd
shutil.copy("gonder_aday.py", "m/gonder.py"); V = pd.read_csv("veri_seti.csv.gz", usecols=["t", "nm", "sinif", "H", "tur", "b_vr"]).drop_duplicates(["t", "nm", "sinif", "H"])
sys.path.insert(0, os.path.abspath("m")); os.chdir("m"); import gonder; from ortak import fetch_1h
V["t"] = pd.to_datetime(V.t, utc=True); S = V[V.sinif.str.startswith("✅") & (V.tur == "🌐🧪") & (V.t >= pd.Timestamp("2026-09-01", tz="UTC"))].drop_duplicates("t")
c = fetch_1h(pd.Timestamp("2026-06-01", tz="UTC").value // 10**6, pd.Timestamp.now(tz="UTC").value // 10**6, sym="BTCUSDT").close
S["canli"] = [gonder.btc_vr_seri(c, t) for t in S.t]; f1, f2 = S.b_vr >= 1.25, S.canli >= 1.25
print(f"T6: {len(S)} sinyal saati (2026-09-01 → 10-21) · işaret aynı %{100 * (f1 == f2).mean():.1f} · ort. mutlak fark {np.abs(S.b_vr - S.canli).mean():.2e} · en büyük {np.abs(S.b_vr - S.canli).max():.2e} · işaretli (araştırma/canlı) {int(f1.sum())}/{int(f2.sum())} → {'✔' if (f1 == f2).mean() >= 0.98 else '✘'}")
t2 = pd.Timestamp.now(tz="UTC").floor("h"); print(f"T6b sarmalayıcı btc_vr({t2:%d.%m %H:%M}) = {gonder.btc_vr(t2):.4f} · seri = {gonder.btc_vr_seri(c, t2):.4f}")
print("T6c ayrıştırma:", [(e, [x[3] for x in gonder._coz(e)]) for e in ("🧪 24 saat: QI (z +7.6)", "🧪 24 saat: BTC (z +1.0)", "🤝 4 saat · BTC ile ortak: METIS (z +3.6)")])
G = pd.read_csv("durum/karne_gercek.csv"); G["t0"] = pd.to_datetime(G.t0, utc=True); G = G[(G.sinif == "ana") & (G.tur == "🌐🧪")].copy()
G["vr"] = [gonder.btc_vr_seri(c, t) for t in G.t0]; fs = lambda y, k_: f"{len(y[k_].dropna())} · %{100 * (y[k_].dropna() > 0).mean():.0f} · {100 * y[k_].dropna().mean():+.2f}" if len(y[k_].dropna()) else "—"
for ad, m in (("BTC oynak (≥ 1,25)", G.vr >= 1.25), ("diğer", G.vr < 1.25)): print(f"T7 canlı ✅ ana 🌐🧪 · {ad}: D {fs(G[m], 'D_T0')} · B {fs(G[m], 'B_T0')}")
