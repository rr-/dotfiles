from libdotfiles import HOME_DIR, PKG_DIR, packages, util

if util.distro_name() == "arch":
    packages.try_install("mujs")
    packages.try_install("luajit")

packages.try_install("mpv")
util.create_symlink(PKG_DIR / "config", HOME_DIR / ".config" / "mpv")
