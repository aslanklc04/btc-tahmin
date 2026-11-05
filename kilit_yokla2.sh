set +e
GIT_TERMINAL_PROMPT=0 git clone -q --depth 1 https://github.com/Omni-Chain-Protocols/emissions-adapters.git ea && cd ea
echo "== manual.ts"; sed -n 1,140p adapters/manual.ts
npm install --silent --no-audit --no-fund > /dev/null 2>&1; npm install --silent ts-node typescript > /dev/null 2>&1
cp ../kilit_disa.ts . && timeout 1500 npx ts-node --transpile-only kilit_disa.ts 2>&1 | tail -5
ls -la kilit_takvim.json && cp kilit_takvim.json ..
cd .. && python3 - <<'P'
import json, requests, time
T = json.load(open("kilit_takvim.json")); tok = sorted({x["token"] for x in T if x.get("token")}); print("token", len(tok), tok[:20])
r = requests.get("https://api.coingecko.com/api/v3/coins/list?include_platform=true", timeout=120); print("coingecko", r.status_code, len(r.content))
if r.ok: json.dump(r.json(), open("kilit_cg.json", "w"))
P
