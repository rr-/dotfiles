import json
import sys

from cfg.theme.render import CLAUDE_THEME
from libdotfiles.util import HOME_DIR, create_dir, run

CLAUDE_DIR = HOME_DIR / ".claude"
THEMES_DIR = CLAUDE_DIR / "themes"
SETTINGS_PATH = CLAUDE_DIR / "settings.json"


def point_at_our_theme() -> None:
    """Name our theme once; theme(1) rewrites what the name refers to."""
    for stale in THEMES_DIR.glob("dash-*.json"):
        stale.unlink()
    if not SETTINGS_PATH.exists():
        return
    settings = json.loads(SETTINGS_PATH.read_text())
    if settings.get("theme") == CLAUDE_THEME:
        return
    settings["theme"] = CLAUDE_THEME
    SETTINGS_PATH.write_text(json.dumps(settings, indent=2) + "\n")


# the directory has to exist before theme(1) runs, or it skips us
create_dir(THEMES_DIR)
point_at_our_theme()
run([sys.executable, "-m", "cfg.theme"], check=True)
