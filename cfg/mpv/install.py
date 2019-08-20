from dotinstall import packages, util


def run():
    packages.try_install("mujs")
    packages.try_install("luajit")
    packages.try_install("mpv")
    util.create_symlink("./config", "~/.config/mpv")
