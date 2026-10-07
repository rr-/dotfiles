#!/usr/bin/env python3
"""Print a GitHub compare URL that opens a PR prefilled from a draft file."""

import sys
import urllib.parse
from pathlib import Path


def main() -> None:
    text = Path(sys.argv[1]).read_text()
    _, front, body = text.split("---\n", 2)
    meta = dict(line.split(": ", 1) for line in front.strip().splitlines())
    base_repo, base_branch = meta["base"].rsplit(":", 1)
    head = meta["head"]
    query = urllib.parse.urlencode(
        {"expand": 1, "title": meta["title"], "body": body.strip() + "\n"}
    )
    print(
        f"https://github.com/{base_repo}/compare/{base_branch}...{head}?{query}"
    )


if __name__ == "__main__":
    main()
