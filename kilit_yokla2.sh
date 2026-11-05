set +e
curl -s "https://api.github.com/search/repositories?q=emissions-adapters&per_page=50" | python3 -c "
import json,sys; d=json.load(sys.stdin)
for r in sorted(d['items'], key=lambda r: r['pushed_at'], reverse=True): print(r['full_name'], r['fork'], r['pushed_at'], r['size'], r['stargazers_count'])"
echo "== wayback"; curl -s -m 60 "https://web.archive.org/cdx/search/cdx?url=api.llama.fi/emissions&limit=20" | head -20
