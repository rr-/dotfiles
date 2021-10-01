from libdotfiles import HOME_DIR, PKG_DIR, util

util.create_symlinks(
    [
        (PKG_DIR / "inputrc", HOME_DIR / ".inputrc"),
        (PKG_DIR / "minttyrc", HOME_DIR / ".minttyrc"),
    ]
)
