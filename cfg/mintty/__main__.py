from libdotfiles.util import HOME_DIR, PKG_DIR, create_symlinks

create_symlinks(
    [
        (PKG_DIR / "inputrc", HOME_DIR / ".inputrc"),
        (PKG_DIR / "minttyrc", HOME_DIR / ".minttyrc"),
    ]
)
