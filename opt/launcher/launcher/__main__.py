#!/usr/bin/env python3
import argparse
import re
import shlex
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    for line in Path("~/.config/launcher.json").expanduser().open():
        pattern, command = line.split("::")
        pattern = pattern.strip()
        command = command.strip()
        if re.fullmatch(pattern, args.file, flags=re.I):
            parameters = shlex.split(command)
            parameters = [args.file if p == "{}" else p for p in parameters]
            if "{}" not in parameters:
                parameters.append(args.file)
            subprocess.run(parameters)
            sys.exit(0)
    print("No suitable program found")
    sys.exit(1)


if __name__ == "__main__":
    main()
