from libdotfiles import packages, util


def run():
    if util.distro_name() == "arch":
        packages.try_install("mujs")
        packages.try_install("luajit")
    packages.try_install("mpv")
    util.create_symlink("./config", "~/.config/mpv")
