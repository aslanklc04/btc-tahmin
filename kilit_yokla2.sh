set +e
git clone -q --depth 1 https://github.com/DefiLlama/emissions-adapters.git ea && cd ea
echo "== dosyalar"; ls; echo "== package.json"; cat package.json | head -60
echo "== README"; head -120 README.md
echo "== protocols sayısı"; ls protocols | wc -l; ls protocols | head -30
echo "== örnek protokol"; f=$(ls protocols | grep -i -E "^arbitrum|^aptos|^optimism" | head -1); echo $f; cat protocols/$f | head -80
echo "== utils/types"; ls adapters 2>/dev/null | head; ls utils 2>/dev/null | head -30; ls types 2>/dev/null
grep -rn "export" types/*.ts 2>/dev/null | head -40
