#!/bin/zsh
D=${0:A:h}
# usage: rmerge.sh <pr> <branch>   (rebases onto origin/develop, verifies, waits for CI, merges)
set -u
n=$1; b=$2; R=/home/dash/work/priv/TRX; W=/tmp/claude-1000/wt-merge-$n
cd $R; git fetch -q origin develop; git fetch -q fork $b
old=$(git rev-parse fork/$b)
want=$(git diff $(git merge-base origin/develop $old) $old -- docs/CHANGELOG.md | grep '^+- ' | sort)
git worktree add -q $W --detach $old || exit 1
cd $W
if ! git merge-base --is-ancestor origin/develop HEAD || git log --format=%s origin/develop..HEAD | grep -qE '^(fixup|amend|squash)! '; then
  GIT_SEQUENCE_EDITOR=true git -c core.attributesFile=$D/attr rebase -q -i --autosquash --gpg-sign origin/develop >/dev/null 2>&1 || { git rebase --abort; echo "#$n REBASE FAILED"; cd $R; git worktree remove --force $W; exit 1; }
fi
got=$(git diff origin/develop HEAD -- docs/CHANGELOG.md | grep '^+- ' | sort)
gone=$(git diff origin/develop HEAD -- docs/CHANGELOG.md | grep -c '^-- ')
if [[ "$got" != "$want" || $gone -ne 0 ]]; then echo "#$n CHANGELOG MISMATCH (removed=$gone)"; cd $R; git worktree remove --force $W; exit 1; fi
git log --format=%s origin/develop..HEAD | grep -qE "^(fixup|amend|squash)! " && { echo "#$n FIXUPS LEFT"; cd $R; git worktree remove --force $W; exit 1; }
signed=$(git log '--format=%G?' origin/develop..HEAD | sort -u | tr -d '\n')
[[ $signed == G ]] || { echo "#$n UNSIGNED ($signed)"; cd $R; git worktree remove --force $W; exit 1; }
new=$(git rev-parse HEAD)
[[ $new != $old ]] && git push -q --force-with-lease="${b}:${old}" fork "HEAD:refs/heads/${b}" 2>&1 | grep -v '^remote:'
cd $R; git worktree remove --force $W
echo "#$n head ${new:0:10}, waiting for CI"
for i in $(seq 1 30); do st=$(gh pr view $n --repo LostArtefacts/TRX --json headRefOid -q .headRefOid 2>/dev/null); [[ $st == $new ]] && break; sleep 5; done
for i in $(seq 1 60); do c=$(gh pr checks $n --repo LostArtefacts/TRX --json name -q length 2>/dev/null); [[ ${c:-0} -gt 0 ]] && break; sleep 5; done
sleep 10
for i in $(seq 1 240); do s=$(gh pr checks $n --repo LostArtefacts/TRX --json bucket -q '[.[].bucket]|unique|join(",")' 2>/dev/null); [[ $s == *pending* || -z $s ]] || break; sleep 15; done
[[ $s == pass || $s == pass,skipping || $s == skipping,pass ]] && rc=0 || { rc=1; echo "#$n checks: $s"; }
[[ $rc -eq 0 ]] || { echo "#$n CI FAILED"; exit 1; }
for i in $(seq 1 100); do st=$(gh pr view $n --repo LostArtefacts/TRX --json mergeable,mergeStateStatus -q '.mergeable+" "+.mergeStateStatus' 2>/dev/null); [[ $st == UNKNOWN* ]] || break; sleep 3; done
[[ $st == "MERGEABLE CLEAN" ]] || { echo "#$n NOT CLEAN: $st"; exit 1; }
gh pr merge $n --repo LostArtefacts/TRX --rebase >/dev/null 2>&1
echo "#$n -> $(gh pr view $n --repo LostArtefacts/TRX --json state -q .state 2>/dev/null)"
