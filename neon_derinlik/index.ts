// Binance USDT-M vadeli emir defteri: fiyatın ±%1'indeki alış / satış derinliği ($). Binance arşivindeki "bookDepth" ±1 ile aynı tanım.
//   /ornek  (yalnız Neon zamanlayıcısı, dakikada bir): 15 coin'i ölçer → nesne deposuna ornek/YYYYMMDDHH/MM.json
//   /saat?h=YYYYMMDDHH : o saatin (UTC) dakikalık ölçümlerinin ortalaması (canlı sistem her saat bunu okur)
//   /dene   : şu anki ölçüm (yazmaz) — kurulum kontrolü
//   /fonlama?c=BTC,ETH,... : her coin'in son 100 fonlama ödemesi (Binance USDT-M) — 💸 coin fonlaması için
import { S3Client, PutObjectCommand, ListObjectsV2Command, GetObjectCommand, DeleteObjectsCommand } from '@aws-sdk/client-s3';

const s3 = new S3Client({ forcePathStyle: true });
const KOVA = 'derinlik';
const COINS: Record<string, string> = {
  BTC: 'BTCUSDT', ETH: 'ETHUSDT', ADA: 'ADAUSDT', APT: 'APTUSDT', ARB: 'ARBUSDT', BNB: 'BNBUSDT', DOGE: 'DOGEUSDT', DOT: 'DOTUSDT',
  FLOKI: '1000FLOKIUSDT', LINK: 'LINKUSDT', NEAR: 'NEARUSDT', OP: 'OPUSDT', PEPE: '1000PEPEUSDT', SHIB: '1000SHIBUSDT', SUI: 'SUIUSDT',
};
// 💧 geniş liste + 💵 coin'leri (ld_genis.py'de geçti, 118 coin): Binance ağırlık sınırı için dakikada yarısı (tek/çift dakika) ölçülür
const EK: Record<string, string> = {
  '1INCH': '1INCHUSDT',
  ANKR: 'ANKRUSDT',
  AXL: 'AXLUSDT',
  C98: 'C98USDT',
  CVX: 'CVXUSDT',
  FIDA: 'FIDAUSDT',
  HBAR: 'HBARUSDT',
  KNC: 'KNCUSDT',
  METIS: 'METISUSDT',
  PYTH: 'PYTHUSDT',
  RLC: 'RLCUSDT',
  SPELL: 'SPELLUSDT',
  TRB: 'TRBUSDT',
  XLM: 'XLMUSDT',
  AAVE: 'AAVEUSDT',
  APE: 'APEUSDT',
  AXS: 'AXSUSDT',
  CAKE: 'CAKEUSDT',
  DASH: 'DASHUSDT',
  FIL: 'FILUSDT',
  ICP: 'ICPUSDT',
  KSM: 'KSMUSDT',
  MINA: 'MINAUSDT',
  ROSE: 'ROSEUSDT',
  STRK: 'STRKUSDT',
  TURBO: 'TURBOUSDT',
  XRP: 'XRPUSDT',
  ACH: 'ACHUSDT',
  API3: 'API3USDT',
  BAND: 'BANDUSDT',
  CELR: 'CELRUSDT',
  DIA: 'DIAUSDT',
  FLOW: 'FLOWUSDT',
  ILV: 'ILVUSDT',
  LDO: 'LDOUSDT',
  NMR: 'NMRUSDT',
  QNT: 'QNTUSDT',
  RPL: 'RPLUSDT',
  STX: 'STXUSDT',
  UMA: 'UMAUSDT',
  XTZ: 'XTZUSDT',
  AGLD: 'AGLDUSDT',
  ARKM: 'ARKMUSDT',
  BAT: 'BATUSDT',
  CHZ: 'CHZUSDT',
  EGLD: 'EGLDUSDT',
  G: 'GUSDT',
  IMX: 'IMXUSDT',
  LPT: 'LPTUSDT',
  OGN: 'OGNUSDT',
  RSR: 'RSRUSDT',
  SUPER: 'SUPERUSDT',
  UNI: 'UNIUSDT',
  YFI: 'YFIUSDT',
  AI: 'AIUSDT',
  ARPA: 'ARPAUSDT',
  BCH: 'BCHUSDT',
  COMP: 'COMPUSDT',
  ENA: 'ENAUSDT',
  GLM: 'GLMUSDT',
  INJ: 'INJUSDT',
  LQTY: 'LQTYUSDT',
  RARE: 'RAREUSDT',
  SAND: 'SANDUSDT',
  SUSHI: 'SUSHIUSDT',
  VET: 'VETUSDT',
  ZEC: 'ZECUSDT',
  ALGO: 'ALGOUSDT',
  ATOM: 'ATOMUSDT',
  BICO: 'BICOUSDT',
  COTI: 'COTIUSDT',
  ENS: 'ENSUSDT',
  GMT: 'GMTUSDT',
  IO: 'IOUSDT',
  LTC: 'LTCUSDT',
  PENDLE: 'PENDLEUSDT',
  SEI: 'SEIUSDT',
  T: 'TUSDT',
  VTHO: 'VTHOUSDT',
  ZEN: 'ZENUSDT',
  ALICE: 'ALICEUSDT',
  AUCTION: 'AUCTIONUSDT',
  BLUR: 'BLURUSDT',
  CRV: 'CRVUSDT',
  ETC: 'ETCUSDT',
  JASMY: 'JASMYUSDT',
  MAGIC: 'MAGICUSDT',
  POL: 'POLUSDT',
  RENDER: 'RENDERUSDT',
  SKL: 'SKLUSDT',
  TAO: 'TAOUSDT',
  W: 'WUSDT',
  ZK: 'ZKUSDT',
  ALT: 'ALTUSDT',
  BNT: 'BNTUSDT',
  CTSI: 'CTSIUSDT',
  ETHFI: 'ETHFIUSDT',
  GRT: 'GRTUSDT',
  JTO: 'JTOUSDT',
  MANA: 'MANAUSDT',
  POWR: 'POWRUSDT',
  SNX: 'SNXUSDT',
  TIA: 'TIAUSDT',
  WIF: 'WIFUSDT',
  ZRO: 'ZROUSDT',
  AVAX: 'AVAXUSDT',
  BONK: '1000BONKUSDT',
  CVC: 'CVCUSDT',
  FET: 'FETUSDT',
  GTC: 'GTCUSDT',
  KAVA: 'KAVAUSDT',
  MASK: 'MASKUSDT',
  PUNDIX: 'PUNDIXUSDT',
  REZ: 'REZUSDT',
  SOL: 'SOLUSDT',
  TNSR: 'TNSRUSDT',
  WLD: 'WLDUSDT',
  ZRX: 'ZRXUSDT',};
const EK_AD = Object.keys(EK).sort();
const json = (o: unknown, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { 'content-type': 'application/json' } });

async function olc(sym: string) {
  try {
    const r = await fetch(`https://fapi.binance.com/fapi/v1/depth?symbol=${sym}&limit=1000`);
    if (!r.ok) return { hata: r.status, metin: (await r.text()).slice(0, 120) };
    const d: any = await r.json();
    const b: number[][] = d.bids.map((x: string[]) => [+x[0], +x[1]]);
    const a: number[][] = d.asks.map((x: string[]) => [+x[0], +x[1]]);
    if (!b.length || !a.length) return { hata: 'bos' };
    const mid = (b[0][0] + a[0][0]) / 2;
    let bid1 = 0, ask1 = 0;
    for (const [p, q] of b) if (p >= mid * 0.99) bid1 += p * q;
    for (const [p, q] of a) if (p <= mid * 1.01) ask1 += p * q;
    return { bid1, ask1, mid, kb: 1 - b[b.length - 1][0] / mid, ka: a[a.length - 1][0] / mid - 1, n: b.length };
  } catch (e: any) { return { hata: String(e?.message ?? e).slice(0, 120) }; }
}
async function hepsi(ek: string[] = []) {
  const t = new Date();
  const liste: [string, string][] = [...Object.entries(COINS), ...ek.map((nm) => [nm, EK[nm]] as [string, string])];
  const s = await Promise.all(liste.map(async ([nm, sym]) => [nm, await olc(sym)] as const));
  return { t: t.toISOString(), coins: Object.fromEntries(s) };
}
const saatAnahtari = (t: Date) => t.toISOString().slice(0, 13).replace(/[-T]/g, '');   // YYYYMMDDHH

export default {
  async fetch(req: Request): Promise<Response> {
    const u = new URL(req.url);
    if (u.pathname === '/ornek') {
      if (!req.headers.get('x-neon-trigger-invocation-id')) return json({ hata: 'yalnız zamanlayıcı' }, 403);
      const dk = new Date().getUTCMinutes();
      const o = await hepsi(EK_AD.filter((_, i) => i % 2 === dk % 2)); const t = new Date(o.t);
      if (dk === 30) {                                                                       // 3 günden eski örnekleri sil (depo sınırı)
        const eski = saatAnahtari(new Date(Date.now() - 72 * 3600_000));
        try {
          const ls = await s3.send(new ListObjectsV2Command({ Bucket: KOVA, Prefix: `ornek/${eski}/` }));
          const ks = (ls.Contents ?? []).map((x) => ({ Key: x.Key! }));
          if (ks.length) await s3.send(new DeleteObjectsCommand({ Bucket: KOVA, Delete: { Objects: ks } }));
        } catch { /* sonraki saat tekrar */ }
      }
      await s3.send(new PutObjectCommand({ Bucket: KOVA, Key: `ornek/${saatAnahtari(t)}/${String(t.getUTCMinutes()).padStart(2, '0')}.json`,
        Body: JSON.stringify(o), ContentType: 'application/json' }));
      return json({ ok: true, t: o.t });
    }
    if (u.pathname === '/dene') return json(await hepsi((u.searchParams.get('ek') ?? '').split(',').filter((x) => x in EK).slice(0, 40)));
    if (u.pathname === '/fonlama') {
      const cs = (u.searchParams.get('c') ?? Object.keys(COINS).join(',')).split(',').map((x) => x.trim().toUpperCase()).filter(Boolean).slice(0, 60);
      const r = await Promise.all(cs.map(async (nm) => {
        for (const sym of [COINS[nm] ?? `${nm}USDT`, `1000${nm}USDT`]) {
          try {
            const q = await fetch(`https://fapi.binance.com/fapi/v1/fundingRate?symbol=${sym}&limit=100`);
            if (!q.ok) continue;
            const d: any[] = await q.json();
            if (Array.isArray(d) && d.length) return [nm, d.map((x) => [x.fundingTime, +x.fundingRate])] as const;
          } catch { /* sonraki sembol */ }
        }
        return [nm, null] as const;
      }));
      return json({ t: new Date().toISOString(), coins: Object.fromEntries(r) });
    }
    if (u.pathname === '/saat') {
      const h = u.searchParams.get('h') ?? saatAnahtari(new Date(Date.now() - 3600_000));
      const ls = await s3.send(new ListObjectsV2Command({ Bucket: KOVA, Prefix: `ornek/${h}/` }));
      const anah = (ls.Contents ?? []).map((x) => x.Key!).filter(Boolean);
      const top: Record<string, { bid1: number; ask1: number; n: number; kb: number; ka: number }> = {};
      for (const k of anah) {
        const g = await s3.send(new GetObjectCommand({ Bucket: KOVA, Key: k }));
        const o: any = JSON.parse((await g.Body?.transformToString('utf-8')) ?? '{}');
        for (const [nm, v] of Object.entries<any>(o.coins ?? {})) {
          if (v?.hata !== undefined || !Number.isFinite(v?.bid1)) continue;
          const z = (top[nm] ??= { bid1: 0, ask1: 0, n: 0, kb: 1, ka: 1 });
          z.bid1 += v.bid1; z.ask1 += v.ask1; z.n += 1; z.kb = Math.min(z.kb, v.kb); z.ka = Math.min(z.ka, v.ka);
        }
      }
      for (const z of Object.values(top)) { z.bid1 /= z.n; z.ask1 /= z.n; }
      return json({ saat: h, ornek_dosya: anah.length, coins: top });
    }
    return json({ ok: true, yollar: ['/dene', '/saat?h=YYYYMMDDHH', '/fonlama?c=BTC,ETH'] });
  },
};
