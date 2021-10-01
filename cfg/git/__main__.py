from libdotfiles import HOME_DIR, PKG_DIR, packages, util

packages.try_install("git")
packages.try_install("git-extras")
util.create_symlinks(
    [
        (PKG_DIR / "config", HOME_DIR / ".config" / "git"),
        (PKG_DIR / "config" / "ignore", HOME_DIR / ".gitignore"),
    ]
)
