from libdotfiles import HOME_DIR, PKG_DIR, packages, util

if not util.has_executable("mpv"):
    packages.try_install("luajit")
    packages.try_install("mpv-git")

util.create_symlinks(
    [
        (PKG_DIR / "config", HOME_DIR / ".config" / "mpi"),
        (PKG_DIR / "mpi", HOME_DIR / ".local" / "bin" / "mpi"),
    ]
)
