#!/bin/bash
D=$(dirname "$(readlink -f "$0")")
# usage: rbcat.sh <pr> <branch> : rebase onto origin/develop resolving catalog conflicts, test, push
set -u
n=$1; b=$2; R=/home/dash/work/priv/TRX; W=/tmp/claude-1000/wt-rb-$n
cd $R; git fetch -q origin develop; git fetch -q fork $b
old=$(git rev-parse fork/$b); base=${3:-$(git merge-base $old origin/develop)}
want=$(git diff $base $old -- docs/CHANGELOG.md | grep '^+- ' | sort)
objc=$(git log --format=%H --reverse $base..$old -- src/trx/game/catalog/objects.def | head -1)
git worktree add -q $W --detach $old || exit 1
cd $W
GIT_SEQUENCE_EDITOR=true git -c core.attributesFile=$D/attr rebase -q -i --autosquash --gpg-sign --onto origin/develop $base >/dev/null 2>&1
while [ -d "$(git rev-parse --git-path rebase-merge)" ]; do
  for f in $(git diff --name-only --diff-filter=U); do
    case $f in
      src/trx/game/catalog/objects.def|tools/tr4/generate_object_catalog|src/trx/game/objects/names.def|src/trx/game/catalog/samples.def|data/trx/ship/games/tr4/catalog_samples.csv) python3 $D/keepboth.py $f >/dev/null ;;
      data/trx/ship/games/tr4/catalog_objects.csv|docs/trx/lua/reference/CATALOG.md) git checkout --theirs $f ;;
      src/meson.build) python3 $D/sortboth.py $f >/dev/null ;;
      *) echo "#$n UNHANDLED CONFLICT $f"; git rebase --abort; cd $R; git worktree remove --force $W; exit 1 ;;
    esac
    git add $f
  done
  if git diff --cached --name-only | grep -q catalog_objects.csv || [ -f data/trx/ship/games/tr4/catalog_objects.csv ]; then
    ln -sfn /home/dash/work/ext/tomb4 src/tomb4; tools/tr4/generate_object_catalog >/dev/null 2>&1; rm -f src/tomb4; git add data/trx/ship/games/tr4/catalog_objects.csv
  fi
  GIT_EDITOR=true git -c core.attributesFile=$D/attr rebase --continue >/dev/null 2>&1
done
TRX_DATA_DIR=/home/dash/work/priv/TRX-data prek -a >/dev/null 2>&1
if [ -n "$(git status --short | grep -v '^??')" ]; then
  tgt=$(git log --format=%H --reverse origin/develop..HEAD -- src/trx/game/catalog/objects.def | head -1)
  [ -z "$tgt" ] && tgt=$(git log --format=%H --reverse origin/develop..HEAD | head -1)
  git commit -q -S -a --fixup=$tgt >/dev/null 2>&1
  GIT_SEQUENCE_EDITOR=true git -c core.attributesFile=$D/attr rebase -q -i --autosquash --gpg-sign origin/develop >/dev/null 2>&1 || { echo "#$n autosquash failed"; exit 1; }
  TRX_DATA_DIR=/home/dash/work/priv/TRX-data prek -a >/dev/null 2>&1 || { echo "#$n prek still dirty"; exit 1; }
fi
got=$(git diff origin/develop HEAD -- docs/CHANGELOG.md | grep '^+- ' | sort)
mk=$(git grep -l '^<<<<<<< ' HEAD -- src docs data 2>/dev/null | wc -l)
sig=$(git log '--format=%G?' origin/develop..HEAD | sort -u | tr -d '\n')
fx=$(git log --format=%s origin/develop..HEAD | grep -c '^fixup! ')
[ "$got" = "$want" ] && [ $mk -eq 0 ] && [ "$sig" = G ] && [ $fx -eq 0 ] || { echo "#$n CHECK FAILED changelog=$([ "$got" = "$want" ] && echo ok || echo bad) markers=$mk sig=$sig fixups=$fx"; exit 1; }
myjust trx-build-linux >/dev/null 2>&1 || { echo "#$n BUILD FAILED"; exit 1; }
myjust test >/dev/null 2>&1; grep -q '^Fail: *0' build/tests/meson-logs/testlog.txt || { echo "#$n TESTS FAILED"; exit 1; }
git push -q --force-with-lease=$b:$old fork HEAD:refs/heads/$b 2>&1 | grep -v '^remote:'
echo "#$n rebased: $(git rev-list --count origin/develop..HEAD) commits -> $(git rev-parse --short=10 HEAD)"
cd $R; git worktree remove --force $W; git fetch -q fork $b
