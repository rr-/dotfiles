#!/bin/bash
# usage: regen-each.sh <base> <tip>   in the current worktree: rebuilds base..tip so
# every commit carries its own regenerated catalog files and passes prek.
set -e
base=$1; tip=$2
new=$(git rev-parse "$base")
for c in $(git rev-list --reverse "$base".."$tip"); do
  git read-tree -u --reset "$c"
  ln -sfn /home/dash/work/ext/tomb4 src/tomb4
  tools/tr4/generate_object_catalog >/dev/null 2>&1 || true
  rm -f src/tomb4
  python3 "$(dirname "$(readlink -f "$0")")/clorder.py" docs/CHANGELOG.md
  TRX_DATA_DIR=/home/dash/work/priv/TRX-data prek -a >/dev/null 2>&1 || TRX_DATA_DIR=/home/dash/work/priv/TRX-data prek -a >/dev/null 2>&1 || { echo "prek fails at $(git log -1 --format=%s $c)"; exit 1; }
  git add -A
  tree=$(git write-tree)
  export GIT_AUTHOR_NAME="$(git log -1 --format=%an "$c")" GIT_AUTHOR_EMAIL="$(git log -1 --format=%ae "$c")" GIT_AUTHOR_DATE="$(git log -1 --format=%aD "$c")"
  new=$(git log -1 --format=%B "$c" | git commit-tree -S "$tree" -p "$new")
  echo "  $(git log -1 --format='%h %s' $new)"
done
git reset -q --hard "$new"
