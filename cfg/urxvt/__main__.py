from pathlib import Path

from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, PKG_DIR, create_symlinks

try_install("urxvt-perls")
try_install("rxvt-unicode")

create_symlinks(
    [
        (PKG_DIR / "ext", HOME_DIR / ".urxvt" / "ext"),
        (PKG_DIR / "Xresources", HOME_DIR / ".config" / "Xresources"),
        (
            PKG_DIR / "notify-urxvt",
            HOME_DIR / ".local" / "bin" / "notify-urxvt",
        ),
    ]
)
