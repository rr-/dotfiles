import argparse
import json
import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

from pw.cmd.base import Command
from pw.db import database


class EditorError(RuntimeError):
    pass


class EditDatabaseCommand(Command):
    name = "edit"

    def decorate_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--editor",
            type=str,
            default=os.environ.get("EDITOR") or "nano",
            help="use this particular editor",
        )

    def run(self, args: argparse.Namespace) -> None:
        with database() as db:
            tmp_file = tempfile.NamedTemporaryFile()
            tmp_path = Path(tmp_file.name)
            tmp_path.write_text(json.dumps(db, indent=4))

            while True:
                retval = subprocess.call(
                    shlex.split(args.editor) + [str(tmp_path)]
                )
                if retval != 0:
                    raise EditorError(
                        f"editor {args.editor} exited nonzero with {retval}"
                    )

                try:
                    new_db = json.loads(tmp_path.read_text())
                except json.JSONDecodeError:
                    print(
                        "Invalid JSON. ^M to edit again, ^C to abort.",
                        file=sys.stderr,
                    )
                    input()
                else:
                    break

            db.clear()
            db.update(new_db)
