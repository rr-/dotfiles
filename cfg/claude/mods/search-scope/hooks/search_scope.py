"""Deny Bash commands that would walk the whole disk.

A search rooted at / is always denied. A search rooted at a broad
directory (a top-level directory, /home or the home directory) is denied
unless it passes the tool's flag for staying on one filesystem, so it
does not wander into other mounts.
"""

import json
import os
import shlex
import sys

HOME = os.path.expanduser("~")

# tool -> flags that keep it on one filesystem, the one to suggest first
# (empty: it has none)
ONE_FS_FLAGS: dict[str, tuple[str, ...]] = {
    "find": ("-xdev", "-mount"),
    "fd": ("--one-file-system", "--mount", "--xdev"),
    "fdfind": ("--one-file-system", "--mount", "--xdev"),
    "rg": ("--one-file-system",),
    "du": ("-x", "--one-file-system"),
    "tree": ("-x",),
    "grep": (),
    "egrep": (),
    "fgrep": (),
    "ugrep": (),
}
# tools whose first positional argument is a pattern, not a path
PATTERN_FIRST = {"fd", "fdfind", "rg", "grep", "egrep", "fgrep", "ugrep"}
# tools that only recurse when asked to
NEEDS_RECURSE = {"grep", "egrep", "fgrep"}
RECURSE_FLAGS = ("-r", "-R", "--recursive", "--dereference-recursive")
# prefixes that run the next word as the command
WRAPPERS = {"sudo", "env", "nice", "ionice", "timeout", "command", "exec"}
SEPARATORS = {"|", "||", "&", "&&", ";", ";;", "(", ")", "\n"}


def split_commands(command: str) -> list[list[str]]:
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()")
    lexer.whitespace_split = True
    commands: list[list[str]] = [[]]
    try:
        for token in lexer:
            if token in SEPARATORS:
                commands.append([])
            else:
                commands[-1].append(token)
    except ValueError:
        pass  # unbalanced quotes; judge what was read so far
    return [words for words in commands if words]


def strip_wrappers(words: list[str]) -> list[str]:
    while words:
        name = os.path.basename(words[0])
        if name in WRAPPERS:
            words = words[1:]
            # drop the wrapper's own options and arguments, e.g. timeout 60
            while words and (
                words[0].startswith("-")
                or "=" in words[0]
                or words[0].replace(".", "").isdigit()
                or words[0][-1:] in "smhd"
                and words[0][:-1].isdigit()
            ):
                words = words[1:]
        elif "=" in name and not name.startswith("-"):
            words = words[1:]  # VAR=value prefix
        else:
            break
    return words


def expand(path: str, cwd: str) -> str:
    for home in ("$HOME", "${HOME}"):
        if path == home or path.startswith(home + "/"):
            path = HOME + path[len(home) :]
    return os.path.normpath(os.path.join(cwd, os.path.expanduser(path)))


def has_flag(args: list[str], flags: tuple[str, ...]) -> bool:
    """Whether args pass one of flags, also inside a cluster like -xsh."""
    short = {flag[1] for flag in flags if len(flag) == 2}
    return any(
        arg in flags
        or (
            arg.startswith("-")
            and not arg.startswith("--")
            and bool(short & set(arg[1:]))
        )
        for arg in args
    )


def is_broad(path: str) -> bool:
    parent = os.path.dirname(path)
    return parent == "/" or path in (HOME, os.path.dirname(HOME))


def search_roots(tool: str, args: list[str]) -> list[str]:
    if tool == "find":
        roots = []
        for arg in args:
            if arg.startswith(("-", "(", "!")):
                break
            roots.append(arg)
        return roots
    positional = [arg for arg in args if not arg.startswith("-")]
    has_explicit_pattern = any(
        arg in ("-e", "-f", "--regexp", "--file")
        or arg.startswith(("--regexp=", "--file="))
        for arg in args
    )
    if tool in PATTERN_FIRST and not has_explicit_pattern:
        positional = positional[1:]
    return positional


def check(words: list[str], cwd: str) -> str | None:
    words = strip_wrappers(words)
    if not words:
        return None
    tool = os.path.basename(words[0])
    if tool not in ONE_FS_FLAGS:
        return None
    args = words[1:]
    if tool in NEEDS_RECURSE and not has_flag(args, RECURSE_FLAGS):
        return None
    # with no path, they all search the working directory
    roots = [expand(root, cwd) for root in search_roots(tool, args)] or [cwd]
    if "/" in roots:
        return (
            f"{tool} rooted at / walks every mounted disk. Search the "
            "directories that can actually hold the answer instead."
        )
    broad = [root for root in roots if is_broad(root)]
    if not broad:
        return None
    flags = ONE_FS_FLAGS[tool]
    if has_flag(args, flags):
        return None
    if not flags:
        return (
            f"recursive {tool} over {', '.join(broad)} can cross into "
            "other filesystems. Narrow the path, or use "
            "rg --one-file-system."
        )
    return (
        f"{tool} over {', '.join(broad)} can cross into other "
        f"filesystems. Add {flags[0]} to stay on one, or narrow "
        "the path."
    )


def main() -> None:
    payload = json.load(sys.stdin)
    command = payload.get("tool_input", {}).get("command", "")
    cwd = payload.get("cwd") or os.getcwd()
    for words in split_commands(command):
        if words[0] == "cd":
            cwd = expand(words[1] if len(words) > 1 else "~", cwd)
            continue
        reason = check(words, cwd)
        if reason:
            json.dump(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"search-scope: {reason}",
                    }
                },
                sys.stdout,
            )
            return


if __name__ == "__main__":
    main()
