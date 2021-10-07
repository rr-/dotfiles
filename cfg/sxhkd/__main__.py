from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, PKG_DIR, create_symlinks

try_install("sxhkd")
try_install("xdo")
try_install("wmctrl")

create_symlinks(
    [
        (PKG_DIR / "config", HOME_DIR / ".config/sxhkd"),
        (
            PKG_DIR / "beep-shot.mp3",
            HOME_DIR / ".local" / "share" / "beep-shot.mp3",
        ),
        (PKG_DIR / "start", HOME_DIR / ".config" / "x" / "start-sxhkd.sh"),
    ]
)
