from libdotfiles import HOME_DIR, PKG_DIR, packages, util

if not util.has_executable("vifm"):
    packages.try_install("vifm")

util.create_dir(HOME_DIR / ".config" / "vifm")
util.create_symlinks(
    [
        (PKG_DIR / "vifmrc", HOME_DIR / ".config" / "vifm" / "vifmrc"),
        (PKG_DIR / "colors", HOME_DIR / ".config" / "vifm" / "colors"),
    ]
)
