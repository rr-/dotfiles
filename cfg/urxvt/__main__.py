from pathlib import Path

from libdotfiles import HOME_DIR, PKG_DIR, packages, util

packages.try_install("urxvt-perls")
packages.try_install("rxvt-unicode")

util.create_symlinks(
    [
        (PKG_DIR / "ext", HOME_DIR / ".urxvt" / "ext"),
        (PKG_DIR / "Xresources", HOME_DIR / ".config" / "Xresources"),
        (
            PKG_DIR / "notify-urxvt",
            HOME_DIR / ".local" / "bin" / "notify-urxvt",
        ),
    ]
)
