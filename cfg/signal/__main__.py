from libdotfiles import HOME_DIR, PKG_DIR, packages, util

packages.try_install("signal-desktop")

util.create_symlink(
    PKG_DIR / "start", HOME_DIR / ".config" / "x" / "start-signal.sh"
)
