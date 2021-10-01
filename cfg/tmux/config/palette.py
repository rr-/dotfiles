#!/usr/bin/env python3
import argparse
import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ESC = "\033"
BEL = "\007"
DSC = ESC + "P"
OSC = ESC + "]"

THEMES_PATH = Path(__file__).parent


@dataclass
class Theme:
    path: Path

    @property
    def name(self) -> str:
        return self.path.stem


def change_color(name: str, arg: str) -> None:
    result = re.match(r"color(\d+)", name)
    if result:
        send_osc(4, int(result.group(1)), arg)
    elif name == "foreground":
        send_osc(10, arg)
    elif name == "background":
        send_osc(11, arg)
    elif name == "cursor":
        send_osc(12, arg)
    elif name == "mouse_foreground":
        send_osc(13, arg)
    elif name == "mouse_background":
        send_osc(14, arg)
    elif name == "highlight":
        send_osc(17, arg)
    elif name == "border":
        send_osc(708, arg)
    else:
        raise ValueError("Unknown name: " + name)


def send_escape_sequence(escape_sequence: str) -> None:
    escape_sequence = DSC + "tmux;" + ESC + escape_sequence + ESC + "\\"
    sys.stdout.write(escape_sequence)


def send_osc(ps: int, *pt: Any) -> None:
    command = OSC + str(ps) + ";" + ";".join(str(x) for x in pt) + BEL
    send_escape_sequence(command)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command_name")
    subparsers.add_parser("list")
    set_parser = subparsers.add_parser("set")
    set_parser.add_argument("theme")
    return parser.parse_args()


def get_themes() -> Iterable[Theme]:
    return (Theme(path=path) for path in THEMES_PATH.glob("*.txt"))


def apply_theme(theme: Theme) -> None:
    with theme.path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("#"):
                continue
            match = re.match(r"\s*(.+?)\s*[=:]\s*(.+?)\s*$", line)
            if not match:
                continue
            key, value = match.groups()
            change_color(key, value)


def main() -> None:
    args = parse_args()

    themes = sorted(get_themes(), key=lambda theme: theme.name)
    if not themes:
        print("No themes", file=sys.stderr)
        sys.exit(1)

    elif args.command_name == "list":
        print("\n".join([theme.name for theme in themes]))
    elif args.command_name == "set":
        for theme in themes:
            if theme.name == args.theme:
                apply_theme(theme)
                break
        else:
            print("No such theme", file=sys.stderr)
            sys.exit(1)
    else:
        print("No command chosen", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
