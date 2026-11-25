#!/bin/zsh
D=${0:A:h}
# usage: rbase.sh <pr> <branch> <oldbase-ref> <newbase-ref>
# Moves the commits <oldbase-ref>..fork/<branch> onto <newbase-ref>, verifies, force-pushes with lease.
set -u
n=$1; b=$2; ob=$3; nb=$4; R=/home/dash/work/priv/TRX; W=/tmp/claude-1000/wt-rb-$n
cd $R
old=$(git rev-parse fork/$b); obs=$(git rev-parse $ob); nbs=$(git rev-parse $nb)
if [[ $(git merge-base $nbs $old) == $nbs ]] && ! git log --format=%s $obs..$old | grep -qE '^(fixup|amend|squash)! '; then echo "#$n already on base"; exit 0; fi
want=$(git diff $obs $old -- docs/CHANGELOG.md | grep '^+- ' | sort)
git worktree add -q $W --detach $old || exit 1
cd $W
GIT_SEQUENCE_EDITOR=true git -c core.attributesFile=$D/attr rebase -q -i --autosquash --gpg-sign --onto $nbs $obs >/dev/null 2>&1 || { git rebase --abort 2>/dev/null; echo "#$n REBASE FAILED"; cd $R; git worktree remove --force $W; exit 1; }
got=$(git diff $nbs HEAD -- docs/CHANGELOG.md | grep '^+- ' | sort)
gone=$(git diff $nbs HEAD -- docs/CHANGELOG.md | grep -c '^-- ')
fix=$(git log --format=%s $nbs..HEAD | grep -c '^fixup! ')
sig=$(git log '--format=%G?' $nbs..HEAD | sort -u | tr -d '\n')
cnt=$(git rev-list --count $nbs..HEAD)
if [[ "$got" != "$want" || $gone -ne 0 || $fix -ne 0 || $sig != G ]]; then echo "#$n CHECK FAILED (removed=$gone fixups=$fix sig=$sig)"; cd $R; git worktree remove --force $W; exit 1; fi
git push -q --force-with-lease="${b}:${old}" fork "HEAD:refs/heads/${b}" 2>&1 | grep -v '^remote:'
echo "#$n rebased: $cnt commits -> $(git rev-parse --short=10 HEAD)"
cd $R; git worktree remove --force $W; git fetch -q fork $b
