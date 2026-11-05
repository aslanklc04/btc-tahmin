// kilit_disa.ts — emissions-adapters protokollerindeki açılım takvimini düz JSON'a döker (PROTOKOL_kilit.md)
import * as fs from "fs";
import * as path from "path";
const sonuc: any[] = []; const hata: any[] = [];
const ac = (x: any) => x && typeof x === "object" && ["cliff", "linear", "step"].includes(x.type);
async function topla(v: any, derin = 0): Promise<any[]> {
  if (derin > 4 || v == null) return [];
  if (typeof v === "function") { try { v = await Promise.race([v(), new Promise((_, r) => setTimeout(() => r("zaman"), 20000))]); } catch (e) { return [{ _hata: String(e).slice(0, 80) }]; } }
  if (v && typeof v.then === "function") { try { v = await Promise.race([v, new Promise((_, r) => setTimeout(() => r("zaman"), 20000))]); } catch (e) { return [{ _hata: String(e).slice(0, 80) }]; } }
  if (Array.isArray(v)) { const o: any[] = []; for (const y of v) o.push(...(await topla(y, derin + 1))); return o; }
  if (ac(v)) return [v];
  return [];
}
(async () => {
  const dir = path.join(process.cwd(), "protocols");
  for (const f of fs.readdirSync(dir).filter((f) => f.endsWith(".ts"))) {
    try {
      const m = require(path.join(dir, f)); const p = m.default ?? m; const cat = p.categories ?? {};
      const kat: Record<string, string> = {}; for (const [k, arr] of Object.entries(cat)) for (const s of (arr as string[]) ?? []) kat[s] = k;
      for (const [sec, v] of Object.entries(p)) {
        if (["meta", "categories", "documented"].includes(sec)) continue;
        for (const r of await topla(v)) sonuc.push({ p: f.replace(".ts", ""), token: p.meta?.token, sec, kat: kat[sec] ?? null, ...r });
      }
    } catch (e) { hata.push({ f, e: String(e).slice(0, 120) }); }
  }
  fs.writeFileSync("kilit_takvim.json", JSON.stringify(sonuc));
  console.log("kayıt", sonuc.length, "· protokol", new Set(sonuc.map((x) => x.p)).size, "· hata", hata.length); console.log(JSON.stringify(hata.slice(0, 30)));
  process.exit(0);
})();
