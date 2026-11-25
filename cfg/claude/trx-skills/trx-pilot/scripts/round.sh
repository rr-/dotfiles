#!/bin/zsh
D=${0:A:h}
# One pilot round: new activity since the last round, merge candidates, conflicts.
S=/tmp/claude-1000/round.since; since=$(cat $S 2>/dev/null || echo 2026-11-22T07:00:00Z); now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
cd /home/dash/work/priv/TRX
gh pr list --repo LostArtefacts/TRX --author @me --state open --limit 80 --json number,headRefName,headRefOid,mergeable,body > /tmp/claude-1000/round.json 2>/dev/null
echo "round at $(date '+%H:%M'), open: $(jq length /tmp/claude-1000/round.json), activity since $since"
for n in $(jq -r '.[].number' /tmp/claude-1000/round.json | sort); do
  gh api repos/LostArtefacts/TRX/issues/$n/comments --jq ".[]|select(.user.login!=\"rr-\" and .user.login!=\"github-actions[bot]\" and .created_at>\"$since\")|\"#$n \(.user.login) comment: \(.body|gsub(\"\n\";\" \")|.[0:600])\"" 2>/dev/null
  gh api repos/LostArtefacts/TRX/pulls/$n/comments --jq ".[]|select(.user.login!=\"rr-\" and .created_at>\"$since\")|\"#$n \(.user.login) \(.path):\(.line // .original_line): \(.body|gsub(\"\n\";\" \")|.[0:600])\"" 2>/dev/null
  gh api repos/LostArtefacts/TRX/pulls/$n/reviews --jq ".[]|select(.user.login!=\"rr-\" and .submitted_at>\"$since\")|\"#$n \(.user.login) \(.state) \(.body|gsub(\"\n\";\" \")|.[0:300])\"" 2>/dev/null
done
echo "=== double-approved (approver@time, last head commit time):"
for n in $(jq -r '.[].number' /tmp/claude-1000/round.json | sort); do
  r=$(gh api repos/LostArtefacts/TRX/pulls/$n/reviews --jq '[.[]|select(.state=="APPROVED")|"\(.user.login)@\(.submitted_at[5:16])"]|join(" ")' 2>/dev/null)
  u=$(echo $r | tr ' ' '\n' | cut -d@ -f1 | sort -u | grep -c .)
  [[ $u -ge 2 ]] && echo "#$n $r | $(jq -r ".[]|select(.number==$n)|.headRefName+\" stacked-on:\"+((.body|capture(\"(Built|Stacked) on #(?<b>[0-9]+)\")?.b) // \"-\")" /tmp/claude-1000/round.json)"
done
echo "=== not mergeable:"; jq -r '.[]|select(.mergeable!="MERGEABLE")|"\(.number) \(.mergeable)"' /tmp/claude-1000/round.json
echo $now > $S
