set +e
echo "== arama"; curl -s "https://api.github.com/search/repositories?q=org:DefiLlama+emission" | python3 -c "import json,sys; d=json.load(sys.stdin); [print(r['full_name'], r['private'], r['pushed_at'], r['description']) for r in d.get('items',[])]; print(d.get('message',''))"
curl -s "https://api.github.com/search/repositories?q=org:DefiLlama+unlock" | python3 -c "import json,sys; d=json.load(sys.stdin); [print(r['full_name'], r['pushed_at'], r['description']) for r in d.get('items',[])]"
for r in DefiLlama/emissions-adapters DefiLlama/emissions DefiLlama/unlocks DefiLlama/emission-adapters; do echo "== $r"; GIT_TERMINAL_PROMPT=0 git ls-remote https://github.com/$r HEAD 2>&1 | head -2; done
