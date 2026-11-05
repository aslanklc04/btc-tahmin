set +e
GIT_TERMINAL_PROMPT=0 git clone -q --depth 1 https://github.com/Omni-Chain-Protocols/emissions-adapters.git ea && cd ea
echo "== son commit"; git log -1 --format="%ci %s"
echo "== dosyalar"; ls; echo "== package.json"; cat package.json | head -50
echo "== README"; head -80 README.md
echo "== protocols"; ls protocols | wc -l; ls protocols | head -40 | tr '\n' ' '; echo
for p in arbitrum aptos optimism; do f=$(ls protocols | grep -i "^$p" | head -1); echo "== $f"; cat protocols/$f | head -70; done
echo "== types"; ls types; sed -n 1,120p types/adapters.ts 2>/dev/null
echo "== utils"; ls utils | head -40
