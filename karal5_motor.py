# karal5_motor.py — PROTOKOL_karal5.md: kâr-al kural listesi + tek bir yol (mumlar) için tüm kuralların neti
# Mumlar: indeks 0 = t (sinyal saatinin kapanışı) mumu · e = giriş mumu · chk = hedef kontrolünün başladığı mum · Hb = süre (mum sayısı) · bm = mum dakikası
import numpy as np
FL, FP, FON, BE_K = 0.0002, 0.0005, 0.0001, 1.0012
def kurallar(kc):
    """kc: sınıfın bugünkü k'sı (ER için). Dönüş: [(ad, fonksiyon tanımı)]"""
    R = []; Sk = [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6, 0.75, 0.9, 1.0, 1.25, 1.5, 2.0, None]
    for k in Sk: R.append((f"S {k}", ("S", k)))
    for q in (1 / 3, 1 / 2, 2 / 3):
        for k1 in (0.25, 0.35, 0.5, 0.6):
            for k2 in (0.75, 1.0, 1.25, 1.5, 2.0, None):
                if k2 is None or k1 < k2: R.append((f"P q{q:.2f} {k1}→{k2}", ("P", q, k1, k2)))
    for k0 in (0.75, 1.0, 1.25, 1.5, 2.0):
        for ke in (0.0, 0.25, 0.5):
            if ke < k0: R.append((f"Z {k0}→{ke}", ("Z", k0, ke)))
    for kb in (0.25, 0.4, 0.5, 0.75):
        for k in (0.75, 1.0, 1.25, 1.5, 2.0, None):
            if k is None or kb < k: R.append((f"BE {kb} hedef {k}", ("BE", kb, k)))
    for ka in (0.25, 0.5, 0.75):
        for ta in (0.1, 0.2, 0.3, 0.5):
            for cap in (None, 1.5): R.append((f"TR {ka} τ{ta} üst {cap}", ("TR", ka, ta, cap)))
    for k in (0.5, 0.75, 1.0):
        for ex in (0.5, 1.0):
            for lv in ("be", "k", "0.25"): R.append((f"UZ {k} +{ex}H {lv}", ("UZ", k, ex, lv)))
    for f in (0.5, 0.75):
        for y in ("0.001", "0.25s", "0.5s"): R.append((f"ER {f}H y{y}", ("ER", kc, f, y)))
        R.append((f"ER- {f}H", ("ERm", kc, f)))
    for k1 in (0.25, 0.35, 0.5, 0.6):
        for k2 in (1.0, 1.5, None): R.append((f"P+BE ½ {k1}→{k2}", ("PBE", 0.5, k1, k2)))
    for q in (1 / 2, 2 / 3):
        for k1 in (0.25, 0.35, 0.5):
            for ta in (0.2, 0.3, 0.5): R.append((f"P+TR q{q:.2f} {k1} τ{ta}", ("PTR", q, k1, ta)))
    return R
def motor(Hh, Lo, C, e, chk, Pe, fin, G, s, Hb, t0m, bm, R):
    n = min(len(C), Hb); end = n - 1
    rm = np.maximum.accumulate(Hh[chk:n]) if chk < n else np.array([])
    def nf(j): return (t0m + (j + 1) * bm) // 480 - (t0m + e * bm) // 480
    def ret(p, fee, j): return p / Pe - 1 - fin - fee - FON * nf(j)
    def fh(level):
        if not len(rm): return None
        i = int(np.searchsorted(rm, level, side="left")); return chk + i if i < len(rm) else None
    zaman = ret(C[end], FP, end)
    def S(k):
        if k is None: return zaman
        tp = G * (1 + k * s)
        if tp <= Pe: return ret(Pe, FP, e)
        j = fh(tp); return ret(tp, FL, j) if j is not None else zaman
    def stop_sonra(a, stv):                                                               # a'dan sonraki ilk mum: en düşük ≤ stop (stv: sabit ya da dizi)
        if a is None or a + 1 > end: return None
        jj = np.arange(a + 1, end + 1); st = stv if np.isscalar(stv) else stv(jj)
        w = np.where(Lo[jj] <= st)[0]; return (int(jj[w[0]]), (st if np.isscalar(st) else st[w[0]])) if len(w) else None
    def yaris(jt, tp, sx):                                                                 # hedef (jt, tp) ile stop (sx = (j, fiyat)) yarışı · aynı mum → stop
        if sx is not None and (jt is None or sx[0] <= jt): return ret(sx[1], FP, sx[0])
        if jt is not None: return ret(tp, FL, jt)
        return zaman
    def BE(kb, k):
        tp = G * (1 + k * s) if k is not None else None
        if tp is not None and tp <= Pe: return ret(Pe, FP, e)
        a = fh(G * (1 + kb * s)); jt = fh(tp) if tp is not None else None
        if a is None: return S(k)
        return yaris(jt, tp, stop_sonra(a, Pe * BE_K))
    def TR(ka, ta, cap):
        tp = G * (1 + cap * s) if cap is not None else None
        a = fh(G * (1 + ka * s)); jt = fh(tp) if tp is not None else None
        if a is None: return S(cap)
        return yaris(jt, tp, stop_sonra(a, lambda jj: rm[jj - 1 - chk] * (1 - ta * s)))
    def Z(k0, ke):
        if chk > end: return zaman
        ii = np.arange(chk, end + 1); tpv = G * (1 + s * (k0 - (k0 - ke) * ii / Hb)); w = np.where(Hh[chk:end + 1] >= tpv)[0]
        if not len(w): return zaman
        j = chk + int(w[0]); return ret(tpv[w[0]], FL, j)
    def UZ(k, ex, lv):
        tp = G * (1 + k * s)
        if tp <= Pe: return ret(Pe, FP, e)
        j = fh(tp)
        if j is not None: return ret(tp, FL, j)
        if C[end] >= Pe: return zaman
        e2 = min(len(C), Hb + int(ex * Hb)) - 1
        if e2 <= end: return zaman
        L = Pe * BE_K if lv == "be" else (tp if lv == "k" else G * (1 + 0.25 * s))
        w = np.where(Hh[end + 1:e2 + 1] >= L)[0]
        if len(w): jj = end + 1 + int(w[0]); return ret(L, FL, jj)
        return ret(C[e2], FP, e2)
    def ER(kc, f, y, eksi=False):
        tp = G * (1 + kc * s)
        if tp <= Pe: return ret(Pe, FP, e)
        jt = fh(tp); jf = min(int(f * Hb), end)
        if jt is not None and jt <= jf: return ret(tp, FL, jt)
        if jf >= chk:
            if eksi:
                if C[jf] <= Pe * (1 - 0.5 * s): return ret(C[jf], FP, jf)
            else:
                yy = 0.001 if y == "0.001" else (0.25 * s if y == "0.25s" else 0.5 * s)
                if C[jf] >= Pe * (1 + yy): return ret(C[jf], FP, jf)
        return ret(tp, FL, jt) if jt is not None else zaman
    out = np.empty(len(R))
    for i, (_, r) in enumerate(R):
        t = r[0]
        if t == "S": v = S(r[1])
        elif t == "P": v = r[1] * S(r[2]) + (1 - r[1]) * S(r[3])
        elif t == "Z": v = Z(r[1], r[2])
        elif t == "BE": v = BE(r[1], r[2])
        elif t == "TR": v = TR(r[1], r[2], r[3])
        elif t == "UZ": v = UZ(r[1], r[2], r[3])
        elif t == "ER": v = ER(r[1], r[2], r[3])
        elif t == "ERm": v = ER(r[1], r[2], None, True)
        elif t == "PBE": v = r[1] * S(r[2]) + (1 - r[1]) * BE(r[2], r[3])
        elif t == "PTR": v = r[1] * S(r[2]) + (1 - r[1]) * TR(r[2], r[3], None)
        out[i] = v
    return out
