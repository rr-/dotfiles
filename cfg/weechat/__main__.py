from libdotfiles import HOME_DIR, PKG_DIR, packages, util

packages.try_install("weechat")
util.create_symlinks(
    [
        (path, HOME_DIR / ".weechat" / path.name)
        for path in PKG_DIR.glob("*.conf")
    ]
)
util.create_symlinks(
    [
        (path, HOME_DIR / ".weechat" / "python" / path.name)
        for path in (PKG_DIR / "python").glob("*.conf")
    ]
)
