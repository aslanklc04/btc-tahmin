#!/bin/bash
# modeller_yaz.sh <kaynak klasör> <dosya öneki: model_ | model24_> — 🌐 geniş liste modellerini "modeller" dalına yazar (dal tek commit; eski sürümler birikmez).
# Yalnız durum/genis_liste.txt'teki coin'ler; diğer türün dosyaları dalda korunur.
set -e
KAYNAK=$1; ONEK=$2; DAL=${MODELLER_DAL:-modeller}; DEPO="https://x-access-token:${GH_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
rm -rf mdl && (git clone -q --depth 1 -b "$DAL" "$DEPO" mdl 2>/dev/null || (mkdir mdl && cd mdl && git init -q -b "$DAL"))
n=0
for s in $(cat durum/genis_liste.txt); do
  f=$(find "$KAYNAK" -name "${ONEK}${s}.pkl.gz" | head -1)
  if [ -n "$f" ]; then cp "$f" mdl/; n=$((n+1)); fi
done
echo "modeller dalına ${ONEK}: $n dosya"
cd mdl && cp ../durum/genis_liste.txt . && rm -rf .git && git init -q -b "$DAL"
git config user.name "github-actions"; git config user.email "github-actions@users.noreply.github.com"
printf "# modeller dalı — 🌐 geniş liste coin modelleri (genis_aile.py testi: 🤝 ve 🧪). Aylık eğitimde üzerine yazılır.\n" > README.md
git add -A && git commit -qm "Genis liste modelleri $(date -u +%Y-%m-%d) (${ONEK})" && git push -q -f "$DEPO" "$DAL"
