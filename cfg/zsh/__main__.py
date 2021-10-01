from libdotfiles import HOME_DIR, PKG_DIR, packages, util

packages.try_install("zsh")

util.create_symlinks(
    [
        (PKG_DIR / "zshrc", HOME_DIR / ".zshrc"),
        (PKG_DIR / "zprofile", HOME_DIR / ".zprofile"),
        (PKG_DIR / "zshenv", HOME_DIR / ".zshenv"),
    ]
)

util.create_dir(HOME_DIR / ".config" / "zsh")
util.run_verbose(
    ["lesskey", "-o", HOME_DIR / ".less", "--", PKG_DIR / "lesskey"]
)
