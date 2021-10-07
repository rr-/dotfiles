from libdotfiles import HOME_DIR, PKG_DIR, packages, util

packages.try_install("sxhkd")
packages.try_install("xdo")
packages.try_install("wmctrl")

util.create_symlinks(
    [
        (PKG_DIR / "config", HOME_DIR / ".config/sxhkd"),
        (
            PKG_DIR / "beep-shot.mp3",
            HOME_DIR / ".local" / "share" / "beep-shot.mp3",
        ),
        (PKG_DIR / "start", HOME_DIR / ".config" / "x" / "start-sxhkd.sh"),
    ]
)
