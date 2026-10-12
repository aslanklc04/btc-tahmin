// Binance USDT-M vadeli emir defteri: fiyatın ±%1'indeki alış / satış derinliği ($). Binance arşivindeki "bookDepth" ±1 ile aynı tanım.
//   /ornek  (yalnız Neon zamanlayıcısı, dakikada bir): 15 coin'i ölçer → nesne deposuna ornek/YYYYMMDDHH/MM.json
//   /saat?h=YYYYMMDDHH : o saatin (UTC) dakikalık ölçümlerinin ortalaması (canlı sistem her saat bunu okur)
//   /dene   : şu anki ölçüm (yazmaz) — kurulum kontrolü
import { S3Client, PutObjectCommand, ListObjectsV2Command, GetObjectCommand } from '@aws-sdk/client-s3';

const s3 = new S3Client({ forcePathStyle: true });
const KOVA = 'derinlik';
const COINS: Record<string, string> = {
  BTC: 'BTCUSDT', ETH: 'ETHUSDT', ADA: 'ADAUSDT', APT: 'APTUSDT', ARB: 'ARBUSDT', BNB: 'BNBUSDT', DOGE: 'DOGEUSDT', DOT: 'DOTUSDT',
  FLOKI: '1000FLOKIUSDT', LINK: 'LINKUSDT', NEAR: 'NEARUSDT', OP: 'OPUSDT', PEPE: '1000PEPEUSDT', SHIB: '1000SHIBUSDT', SUI: 'SUIUSDT',
};
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
async function hepsi() {
  const t = new Date();
  const s = await Promise.all(Object.entries(COINS).map(async ([nm, sym]) => [nm, await olc(sym)] as const));
  return { t: t.toISOString(), coins: Object.fromEntries(s) };
}
const saatAnahtari = (t: Date) => t.toISOString().slice(0, 13).replace(/[-T]/g, '');   // YYYYMMDDHH

export default {
  async fetch(req: Request): Promise<Response> {
    const u = new URL(req.url);
    if (u.pathname === '/ornek') {
      if (!req.headers.get('x-neon-trigger-invocation-id')) return json({ hata: 'yalnız zamanlayıcı' }, 403);
      const o = await hepsi(); const t = new Date(o.t);
      await s3.send(new PutObjectCommand({ Bucket: KOVA, Key: `ornek/${saatAnahtari(t)}/${String(t.getUTCMinutes()).padStart(2, '0')}.json`,
        Body: JSON.stringify(o), ContentType: 'application/json' }));
      return json({ ok: true, t: o.t });
    }
    if (u.pathname === '/dene') return json(await hepsi());
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
    return json({ ok: true, yollar: ['/dene', '/saat?h=YYYYMMDDHH'] });
  },
};
