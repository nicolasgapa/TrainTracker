#!/bin/sh
# Collect new arrivals on this Mac and push them to GitHub.
# The GitHub Actions job also writes data/arrivals.csv, so always start from
# the latest GitHub version; collect.py merges new rows into it.
set -e
cd "$(dirname "$0")"
export PATH="$HOME/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

for attempt in 1 2 3; do
  git pull -q --ff-only origin main
  python3 collect.py
  git add data/arrivals.csv
  if git diff --cached --quiet; then echo "No new arrivals."; exit 0; fi
  git commit -q -m "Collect arrivals (local) $(date -u +%Y-%m-%dT%H:%MZ)" -- data/arrivals.csv
  if git push -q origin main; then echo "Pushed."; exit 0; fi
  # GitHub's job pushed first: drop our commit and data change, then redo on top of theirs.
  echo "Push raced with GitHub's job, retrying ($attempt)..."
  git reset -q HEAD~1
  git checkout -- data/arrivals.csv
done
exit 1
