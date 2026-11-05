set +e
echo "== github arama (ham)"; curl -s "https://api.github.com/search/repositories?q=emissions-adapters" | head -c 1500; echo
echo "== wayback cdx emissions"; curl -s "https://web.archive.org/cdx/search/cdx?url=api.llama.fi/emissions&output=json&limit=50" | head -c 3000; echo
echo "== wayback cdx emission/*"; curl -s "https://web.archive.org/cdx/search/cdx?url=api.llama.fi/emission/*&output=json&limit=30&collapse=urlkey" | head -c 3000; echo
