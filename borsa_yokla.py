# borsa_yokla.py — BİNANCE DIŞI VADELİ EMİR DEFTERİ: hangi borsa GitHub'dan (ABD sunucusu) açık, defter ±%1'i kapsıyor mu? + Gate.io GEÇMİŞ emir defteri arşivi var mı?
# (kullanıcı isteği 12.10.2026: "Başka borsa dene vadeli için"). Yalnız yoklama, karar yok.
import io, gzip, zlib, json, time, requests, numpy as np, pandas as pd
T0 = time.time(); L = []
def yaz(s=""): print(s, flush=True); L.append(s)
S = requests.Session(); S.headers["User-Agent"] = "btc-tahmin-arastirma"
def get(url, **kw):
    try: r = S.get(url, timeout=25, **kw); return r.status_code, (r.json() if r.status_code == 200 else r.text[:120])
    except Exception as e: return -1, f"{type(e).__name__}: {str(e)[:100]}"
def post(url, js):
    try: r = S.post(url, json=js, timeout=25); return r.status_code, (r.json() if r.status_code == 200 else r.text[:120])
    except Exception as e: return -1, f"{type(e).__name__}: {str(e)[:100]}"
def olc(b, a, carp=1.0, usd=False):
    """b, a: [(fiyat, miktar)] → seviye sayısı, kapsanan aralık %, ±%1 içindeki derinlik ($)"""
    b = [(float(p), float(q)) for p, q in b]; a = [(float(p), float(q)) for p, q in a]
    if not b or not a: return None
    mid = (max(p for p, _ in b) + min(p for p, _ in a)) / 2
    val = (lambda p, q: q * carp) if usd else (lambda p, q: p * q * carp)
    db = sum(val(p, q) for p, q in b if p >= mid * 0.99); da = sum(val(p, q) for p, q in a if p <= mid * 1.01)
    kb = 100 * (mid - min(p for p, _ in b)) / mid; ka = 100 * (max(p for p, _ in a) - mid) / mid
    return len(b), len(a), kb, ka, db, da
SON = []
def kayit(borsa, coin, durum, o, notu=""):
    if o is None: SON.append((borsa, coin, durum, None, None, None, None, None, None, notu)); return
    SON.append((borsa, coin, durum, o[0], o[1], round(o[2], 2), round(o[3], 2), round(o[4] / 1e6, 2), round(o[5] / 1e6, 2), notu))
COINS = ["BTC", "ETH", "DOGE"]
# --- Binance (karşılaştırma) ---
def _b0():
    for c in COINS:
        st, d = get("https://fapi.binance.com/fapi/v1/depth", params={"symbol": c + "USDT", "limit": 1000})
        kayit("Binance vadeli", c, st, olc(d["bids"], d["asks"]) if st == 200 else None, "" if st == 200 else str(d)[:60])
        st, d = get("https://data-api.binance.vision/api/v3/depth", params={"symbol": c + "USDT", "limit": 5000})
        kayit("Binance spot (data-api)", c, st, olc(d["bids"], d["asks"]) if st == 200 else None, "" if st == 200 else str(d)[:60])
try: _b0()
except Exception as e: SON.append(('Binance (karşılaştırma)', '-', 'hata', None, None, None, None, None, None, f'{type(e).__name__}: {str(e)[:80]}'))
# --- Gate.io vadeli ---
def _b1():
    for c in COINS:
        st, ci = get(f"https://api.gateio.ws/api/v4/futures/usdt/contracts/{c}_USDT"); m = float(ci.get("quanto_multiplier", 1)) if st == 200 else 1.0
        for iv in ("0", None):
            p = {"contract": f"{c}_USDT", "limit": 300}
            if iv is None:
                pr = float(ci.get("mark_price", 0)) if st == 200 else 0; p["interval"] = next((x for x in ("100", "10", "1", "0.1", "0.01", "0.001", "0.0001", "0.00001") if pr and float(x) <= pr * 0.0001), "0")
            s2, d = get("https://api.gateio.ws/api/v4/futures/usdt/order_book", params=p)
            kayit("Gate vadeli" + ("" if iv == "0" else f" (aralık {p['interval']})"), c, s2, olc([(x["p"], x["s"]) for x in d["bids"]], [(x["p"], x["s"]) for x in d["asks"]], m) if s2 == 200 else None, "" if s2 == 200 else str(d)[:60])
try: _b1()
except Exception as e: SON.append(('Gate.io vadeli', '-', 'hata', None, None, None, None, None, None, f'{type(e).__name__}: {str(e)[:80]}'))
# --- KuCoin vadeli ---
def _b2():
    KS = {"BTC": "XBTUSDTM", "ETH": "ETHUSDTM", "DOGE": "DOGEUSDTM"}
    for c in COINS:
        st, ci = get(f"https://api-futures.kucoin.com/api/v1/contracts/{KS[c]}"); m = float(ci["data"]["multiplier"]) if st == 200 else 1.0
        for yol in ("level2/snapshot", "level2/depth100"):
            s2, d = get(f"https://api-futures.kucoin.com/api/v1/{yol}", params={"symbol": KS[c]})
            ok = s2 == 200 and isinstance(d, dict) and d.get("data")
            kayit(f"KuCoin vadeli ({yol.split('/')[1]})", c, s2 if ok else f"{s2}/{str(d)[:30]}", olc(d["data"]["bids"], d["data"]["asks"], m) if ok else None)
try: _b2()
except Exception as e: SON.append(('KuCoin vadeli', '-', 'hata', None, None, None, None, None, None, f'{type(e).__name__}: {str(e)[:80]}'))
# --- OKX ---
def _b3():
    for c in COINS:
        st, ci = get("https://www.okx.com/api/v5/public/instruments", params={"instType": "SWAP", "instId": f"{c}-USDT-SWAP"})
        m = float(ci["data"][0]["ctVal"]) if st == 200 and ci.get("data") else 1.0
        s2, d = get("https://www.okx.com/api/v5/market/books-full", params={"instId": f"{c}-USDT-SWAP", "sz": 5000})
        ok = s2 == 200 and d.get("data")
        kayit("OKX vadeli", c, s2 if ok else f"{s2}/{str(d)[:40]}", olc([x[:2] for x in d["data"][0]["bids"]], [x[:2] for x in d["data"][0]["asks"]], m) if ok else None)
try: _b3()
except Exception as e: SON.append(('OKX', '-', 'hata', None, None, None, None, None, None, f'{type(e).__name__}: {str(e)[:80]}'))
# --- Bybit ---
def _b4():
    for c in COINS:
        st, d = get("https://api.bybit.com/v5/market/orderbook", params={"category": "linear", "symbol": c + "USDT", "limit": 500})
        ok = st == 200 and isinstance(d, dict) and d.get("result")
        kayit("Bybit vadeli", c, st if ok else f"{st}", olc(d["result"]["b"], d["result"]["a"]) if ok else None, "" if ok else str(d)[:60])
try: _b4()
except Exception as e: SON.append(('Bybit', '-', 'hata', None, None, None, None, None, None, f'{type(e).__name__}: {str(e)[:80]}'))
# --- Bitget ---
def _b5():
    for c in COINS:
        st, d = get("https://api.bitget.com/api/v2/mix/market/merge-depth", params={"symbol": c + "USDT", "productType": "usdt-futures", "limit": "max"})
        ok = st == 200 and d.get("data")
        kayit("Bitget vadeli", c, st if ok else f"{st}", olc(d["data"]["bids"], d["data"]["asks"]) if ok else None, "" if ok else str(d)[:60])
try: _b5()
except Exception as e: SON.append(('Bitget', '-', 'hata', None, None, None, None, None, None, f'{type(e).__name__}: {str(e)[:80]}'))
# --- MEXC ---
def _b6():
    for c in COINS:
        st, ci = get("https://contract.mexc.com/api/v1/contract/detail", params={"symbol": f"{c}_USDT"}); m = float(ci["data"]["contractSize"]) if st == 200 and ci.get("data") else 1.0
        s2, d = get(f"https://contract.mexc.com/api/v1/contract/depth/{c}_USDT", params={"limit": 2000})
        ok = s2 == 200 and d.get("data")
        kayit("MEXC vadeli", c, s2 if ok else f"{s2}", olc([x[:2] for x in d["data"]["bids"]], [x[:2] for x in d["data"]["asks"]], m) if ok else None, "" if ok else str(d)[:60])
try: _b6()
except Exception as e: SON.append(('MEXC', '-', 'hata', None, None, None, None, None, None, f'{type(e).__name__}: {str(e)[:80]}'))
# --- HTX ---
def _b7():
    for c in COINS:
        st, ci = get("https://api.hbdm.com/linear-swap-api/v1/swap_contract_info", params={"contract_code": f"{c}-USDT"}); m = float(ci["data"][0]["contract_size"]) if st == 200 and ci.get("data") else 1.0
        s2, d = get("https://api.hbdm.com/linear-swap-ex/market/depth", params={"contract_code": f"{c}-USDT", "type": "step0"})
        ok = s2 == 200 and d.get("tick")
        kayit("HTX vadeli", c, s2 if ok else f"{s2}", olc(d["tick"]["bids"], d["tick"]["asks"], m) if ok else None, "" if ok else str(d)[:60])
try: _b7()
except Exception as e: SON.append(('HTX', '-', 'hata', None, None, None, None, None, None, f'{type(e).__name__}: {str(e)[:80]}'))
# --- BingX ---
def _b8():
    for c in COINS:
        st, d = get("https://open-api.bingx.com/openApi/swap/v2/quote/depth", params={"symbol": f"{c}-USDT", "limit": 1000})
        ok = st == 200 and d.get("data")
        kayit("BingX vadeli", c, st if ok else f"{st}", olc(d["data"]["bids"], d["data"]["asks"]) if ok else None, "" if ok else str(d)[:60])
try: _b8()
except Exception as e: SON.append(('BingX', '-', 'hata', None, None, None, None, None, None, f'{type(e).__name__}: {str(e)[:80]}'))
# --- Hyperliquid ---
def _b9():
    for c in COINS:
        for nsf in (None, 4, 3):
            js = {"type": "l2Book", "coin": c}
            if nsf: js["nSigFigs"] = nsf
            st, d = post("https://api.hyperliquid.xyz/info", js)
            ok = st == 200 and isinstance(d, dict) and d.get("levels")
            kayit(f"Hyperliquid{'' if not nsf else f' ({nsf} hane)'}", c, st, olc([(x["px"], x["sz"]) for x in d["levels"][0]], [(x["px"], x["sz"]) for x in d["levels"][1]]) if ok else None, "" if ok else str(d)[:60])
try: _b9()
except Exception as e: SON.append(('Hyperliquid', '-', 'hata', None, None, None, None, None, None, f'{type(e).__name__}: {str(e)[:80]}'))
# --- Kraken vadeli · dYdX · Deribit ---
def _b10():
    KR = {"BTC": "PF_XBTUSD", "ETH": "PF_ETHUSD", "DOGE": "PF_DOGEUSD"}
    for c in COINS:
        st, d = get("https://futures.kraken.com/derivatives/api/v3/orderbook", params={"symbol": KR[c]})
        ok = st == 200 and d.get("orderBook")
        kayit("Kraken vadeli", c, st, olc(d["orderBook"]["bids"], d["orderBook"]["asks"]) if ok else None, "" if ok else str(d)[:60])
        st, d = get(f"https://indexer.dydx.trade/v4/orderbooks/perpetualMarket/{c}-USD")
        ok = st == 200 and isinstance(d, dict) and d.get("asks")
        kayit("dYdX", c, st, olc([(x["price"], x["size"]) for x in d["bids"]], [(x["price"], x["size"]) for x in d["asks"]]) if ok else None, "" if ok else str(d)[:60])
        if c in ("BTC", "ETH"):
            st, d = get("https://www.deribit.com/api/v2/public/get_order_book", params={"instrument_name": f"{c}-PERPETUAL", "depth": 10000})
            ok = st == 200 and d.get("result")
            kayit("Deribit", c, st, olc(d["result"]["bids"], d["result"]["asks"], usd=True) if ok else None, "" if ok else str(d)[:60])
try: _b10()
except Exception as e: SON.append(('Kraken vadeli · dYdX · Deribit', '-', 'hata', None, None, None, None, None, None, f'{type(e).__name__}: {str(e)[:80]}'))
T = pd.DataFrame(SON, columns=["borsa", "coin", "durum", "alış_sev", "satış_sev", "alış_kapsam%", "satış_kapsam%", "±1% alış M$", "±1% satış M$", "not"])
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200); pd.set_option("display.max_colwidth", 60)
yaz(f"# 🏦 Vadeli emir defteri yoklaması (GitHub ABD sunucusundan) — {pd.Timestamp.now(tz='Europe/Istanbul'):%d.%m.%Y %H:%M}\n_kapsam: defterin fiyattan ne kadar uzağa gittiği (%1'i geçmeli) · ±1% derinlik milyon $_\n```")
yaz(T.to_string(index=False)); yaz("```")
# --- Gate.io GEÇMİŞ emir defteri arşivi ---
yaz("\n## Gate.io geçmiş emir defteri arşivi (download.gatedata.org)\n```")
KAL = []
for biz in ("futures_usdt",):
    for ay, gun, saat in (("202301", "20230115", "00"), ("202401", "20240115", "12"), ("202509", "20250915", "08"), ("202609", "20260915", "16")):
        for url in (f"https://download.gatedata.org/{biz}/orderbooks/{ay}/BTC_USDT-{gun}{saat}.csv.gz", f"https://download.gatedata.org/{biz}/orderbooks/{ay}/BTC_USDT-{gun}.csv.gz",
                    f"https://download.gatedata.org/{biz}/orderbooks/{ay}/BTC_USDT-{ay}.csv.gz"):
            try:
                r = S.get(url, headers={"Range": "bytes=0-1048575"}, timeout=40, stream=True); raw = r.raw.read(1048576, decode_content=False) if r.status_code in (200, 206) else b""
                yaz(f"{r.status_code} {r.headers.get('Content-Range', r.headers.get('Content-Length', '')):>28} {url}")
                if raw and not KAL: KAL.append((url, raw, r.status_code))
            except Exception as e: yaz(f"hata {type(e).__name__} {url}")
yaz("```")
if KAL:
    url, raw, st = KAL[0]; txt = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(raw).decode("utf-8", "replace"); sat = txt.splitlines()
    yaz(f"İlk çalışan: {url} (durum {st}, Range {'destekleniyor' if st == 206 else 'YOK'}) · 1 MB'ta {len(sat):,} satır\nİlk 8 satır:\n```\n" + "\n".join(sat[:8]) + "\n```")
    try:
        df = pd.read_csv(io.StringIO("\n".join(sat[:-1])), header=None); yaz(f"Sütunlar: {df.shape[1]} · eylem değerleri: {df[1].value_counts().head(5).to_dict()}")
        snap = df[df[1] == "set"] if (df[1] == "set").any() else df.iloc[:0]
        if len(snap):
            p, s = snap[2].astype(float), snap[3].astype(float); mid = (p[s > 0].max() + p[s < 0].min()) / 2 if (s > 0).any() and (s < 0).any() else np.nan
            yaz(f"Anlık görüntü satırı: {len(snap):,} · alış (s>0) {int((s > 0).sum())} · satış (s<0) {int((s < 0).sum())} · orta fiyat {mid:,.1f} · "
                f"±%1 alış {float((p * s.abs())[(s > 0) & (p >= mid * 0.99)].sum()):,.0f} · satış {float((p * s.abs())[(s < 0) & (p <= mid * 1.01)].sum()):,.0f} (sözleşme × fiyat)")
    except Exception as e: yaz(f"çözümlenemedi: {type(e).__name__} {str(e)[:150]}")
yaz(f"\n_Süre: {time.time()-T0:.0f} sn_")
open("borsa_yokla_sonuc.md", "w").write("\n".join(L) + "\n")
