#!/bin/bash
# usage: clfix.sh <base>   rebuilds base..HEAD so each commit's docs/CHANGELOG.md
# keeps Added, Changed, Fixed order; trees, messages and authors otherwise unchanged.
set -e
D=$(dirname "$(readlink -f "$0")")
base=$1
new=$(git rev-parse "$base")
for c in $(git rev-list --reverse "$base"..HEAD); do
  git read-tree -u --reset "$c"
  python3 "$(dirname "$(readlink -f "$0")")/clorder.py" docs/CHANGELOG.md
  git add docs/CHANGELOG.md
  tree=$(git write-tree)
  if [ "$tree" = "$(git rev-parse "$c^{tree}")" ] && [ "$(git rev-parse "$c^")" = "$new" ]; then
    new=$c
    continue
  fi
  export GIT_AUTHOR_NAME="$(git log -1 --format=%an "$c")" GIT_AUTHOR_EMAIL="$(git log -1 --format=%ae "$c")" GIT_AUTHOR_DATE="$(git log -1 --format=%aD "$c")"
  new=$(git log -1 --format=%B "$c" | git commit-tree -S "$tree" -p "$new")
done
git reset -q --hard "$new"
