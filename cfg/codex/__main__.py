import re
import sys

from cfg.theme.render import CODEX_THEME
from libdotfiles.util import HOME_DIR, create_dir, run

CODEX_DIR = HOME_DIR / ".codex"
THEMES_DIR = CODEX_DIR / "themes"
CONFIG_PATH = CODEX_DIR / "config.toml"


def point_at_our_theme() -> None:
    """Name our theme once; theme(1) rewrites what the name refers to.

    codex writes config.toml itself, so edit the one line rather than own the
    file.
    """
    line = f'theme = "{CODEX_THEME}"'
    text = CONFIG_PATH.read_text() if CONFIG_PATH.exists() else ""
    section = re.search(r"^\[tui\][ \t]*\n((?:(?!\[).*\n?)*)", text, re.M)
    if section is None:
        text = (
            text.rstrip("\n") + ("\n\n" if text else "") + f"[tui]\n{line}\n"
        )
    else:
        body = section[1]
        if re.search(r"^theme\s*=", body, re.M):
            body = re.sub(r"^theme\s*=.*$", line, body, count=1, flags=re.M)
        else:
            body = f"{line}\n{body}"
        text = text[: section.start(1)] + body + text[section.end(1) :]
    CONFIG_PATH.write_text(text)


# the directory has to exist before theme(1) runs, or it skips us
create_dir(THEMES_DIR)
point_at_our_theme()
run([sys.executable, "-m", "cfg.theme"], check=True)
