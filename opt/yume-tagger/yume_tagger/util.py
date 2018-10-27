import os
import re
import tempfile
import subprocess
from pathlib import Path
from typing import Any, Callable


DB_DIR = Path("~/.local/share/yume-tagger/").expanduser()


def confirm(text: str) -> bool:
    while True:
        result = input("{} ".format(text.strip())).lower()
        if result in ["yes", "yep", "yeah", "y", "true"]:
            return True
        if result in ["no", "nah", "nay", "n", "false"]:
            return False


def sanitize_tag(name: str) -> str:
    return re.sub(r"\s+", "_", name)


def capitalize(name: str) -> str:
    return re.sub(r"(^|[_()])([a-z])", lambda m: m.group(0).upper(), name)


def run_editor(
    file_name: str,
    source: Any,
    serializer: Callable[[Any], str],
    deserializer: Callable[[str], Any],
) -> Any:
    text = serializer(source)
    with tempfile.TemporaryDirectory() as tmp_dir:
        path: Path = Path(tmp_dir).joinpath(file_name)
        path.write_text(text)
        while True:
            subprocess.run([os.getenv("EDITOR") or "vim", str(path)])
            text = path.read_text()
            try:
                return deserializer(text)
            except ValueError as ex:
                input(
                    "Error: {}. Press return to edit again, ^C to abort. ".format(
                        ex
                    )
                )
