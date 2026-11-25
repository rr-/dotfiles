#!/bin/zsh
D=${0:A:h}
# usage: train.sh "pr:branch[:base_pr]" ...   merges in order; skips a PR whose base failed
typeset -A failed
for spec in "$@"; do
  n=${spec%%:*}; rest=${spec#*:}; b=${rest%%:*}; base=""; [[ $rest == *:* ]] && base=${rest#*:}
  if [[ -n $base && -n ${failed[$base]:-} ]]; then echo "#$n SKIPPED (base #$base failed)"; failed[$n]=1; continue; fi
  zsh $D/rmerge.sh $n $b 2>&1 | grep -v -e '^hint:' -e '^  - ' -e 'gh event listen'
  st=$(gh pr view $n --repo LostArtefacts/TRX --json state -q .state 2>/dev/null)
  [[ $st == MERGED ]] || failed[$n]=1
done
echo "train done at $(date +%H:%M)"
