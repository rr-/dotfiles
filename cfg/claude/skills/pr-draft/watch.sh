#!/usr/bin/env bash
# Usage: watch.sh PR_DRAFT-<branch>.md
# Prints NOTES when a save leaves >> notes in the draft, GO when one of them
# is ">> go", and GONE (then exits) when the draft is deleted.
set -u
draft=$1
last=$(stat -c %Y.%s "$draft" 2>/dev/null || echo none)
while true; do
    sleep 1
    if [[ ! -e $draft ]]; then
        echo "GONE $draft"
        exit 0
    fi
    cur=$(stat -c %Y.%s "$draft" 2>/dev/null) || continue
    [[ $cur == "$last" ]] && continue
    # editors save in bursts; wait for the file to settle
    sleep 1
    cur=$(stat -c %Y.%s "$draft" 2>/dev/null) || continue
    last=$cur
    if grep -qiE '^\s*>>\s*go\s*$' "$draft"; then
        echo "GO $draft"
    elif n=$(grep -cE '^\s*>>' "$draft") && ((n > 0)); then
        echo "NOTES $n $draft"
    fi
done
