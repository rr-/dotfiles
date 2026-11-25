#!/usr/bin/env python3
"""PreToolUse guard: the plans repository changes only through `track`.

Denies Edit/Write/MultiEdit/NotebookEdit on files under the plans folder, and
Bash commands that name the folder (or run in it) and look like a write. Reads
(cat, grep, git log, git config --get ...) and `track` itself pass.

Also denies setting TRACK_UNATTENDED, in a command or in a file outside
track's own source: an unattended run lets track_replan apply without the
user's approval, so only the user turns it on.
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import NoReturn

PLANS = Path(
    os.environ.get("TRACK_HOME", Path.home() / "work/priv/plans")
).resolve()
TRACK_SOURCE = Path.home() / "work/priv/track"
REASON = (
    f"{PLANS} changes only through the track MCP tools (they commit every change): "
    "track_set, track_note (kind handoff|decision|open), track_add, track_update, "
    "track_move, track_drop, track_delete, track_bulk, track_replan. Reading with "
    "track_list/track_show, cat, grep or git log is fine. Prose in plan.md is the "
    "user's to edit in the live view; say what to change."
)
UNATTENDED = "TRACK_UNATTENDED"
UNATTENDED_REASON = (
    f"{UNATTENDED} lets track_replan change the plans without the user's approval; "
    "only the user sets it, when they start an unattended run. Ask them instead."
)
# Setting it: NAME=1, "NAME": "1", environ["NAME"] = "1", -e/--env NAME.
SETS_UNATTENDED = re.compile(
    UNATTENDED + r"""["'\\\]]*\s*[:=]|(?:-e|--env)[\s=]+["']?""" + UNATTENDED
)
# git's options before its subcommand: -C dir, -c key=value, --flag[=value].
GIT = r"\bgit\b(?:\s+(?:-[Cc]\s+\S+|--?[\w-]+(?:=\S+)?))*\s+"
WRITES = re.compile(
    r"(\bsed\b[^|;&]*\s-i|>>?|\btee\b|\bmv\b|\bcp\b|\brm\b|\btouch\b|\bln\b|\btruncate\b|"
    r"\bperl\b[^|;&]*\s-i|\bpython3?\b|"
    + GIT
    + r"(?:commit|reset|checkout|switch|restore|rebase|revert|stash|rm|mv|apply|am|"
    r"clean|push|pull|merge|cherry-pick|tag|branch|remote\s+(?:add|remove|rm|set-url)|"
    r"config(?!\s+(?:--get|--get-all|--get-regexp|--list|-l)\b))\b)"
)
# Redirects that write nothing: to /dev/null, or one stream into another.
HARMLESS = re.compile(r"\d?>>?\s*/dev/null|\d?>&\d")


def is_under(path: str, root: Path) -> bool:
    try:
        return Path(os.path.expanduser(path)).resolve().is_relative_to(root)
    except (OSError, ValueError):
        return False


def under_plans(path: str) -> bool:
    return is_under(path, PLANS)


def deny(reason: str = REASON) -> NoReturn:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    sys.exit(0)


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    tool = event.get("tool_name", "")
    data = event.get("tool_input", {})
    path = data.get("file_path") or data.get("notebook_path") or ""
    in_source = bool(path) and is_under(path, TRACK_SOURCE)
    if not in_source and SETS_UNATTENDED.search(json.dumps(data)):
        deny(UNATTENDED_REASON)
    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        if path and under_plans(path):
            deny()
        return
    if tool != "Bash":
        return
    command = data.get("command", "")
    if re.match(r"\s*track(\s|$)", command) and not re.search(
        r"[;&|]", command
    ):
        return
    home = str(Path.home())
    names = {
        str(PLANS),
        str(PLANS).replace(home, "~", 1),
        str(PLANS).replace(home, "$HOME", 1),
    }
    # A leading cd sets where the rest runs, so it, not the session's cwd, counts.
    lead = re.match(r"\s*cd\s+([^\s;&|]+)\s*&&", command)
    cwd = lead.group(1) if lead else event.get("cwd", "")
    mentions = any(n in command for n in names) or under_plans(cwd)
    if mentions and WRITES.search(HARMLESS.sub(" ", command)):
        deny()


if __name__ == "__main__":
    main()
