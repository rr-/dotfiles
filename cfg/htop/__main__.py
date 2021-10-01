from libdotfiles import HOME_DIR, PKG_DIR, packages, util

packages.try_install("htop")
util.create_symlink(
    PKG_DIR / "htoprc", HOME_DIR / ".config" / "htop" / "htoprc"
)
