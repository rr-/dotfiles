from libdotfiles import packages, util


def run() -> None:
    packages.try_install("ibus")
    packages.try_install("ibus-anthy")
    util.create_symlink("./config.ini", "~/.config/ibus/config.ini")
    util.create_symlink("./start", "~/.config/x/start-ibus.sh")
    util.create_symlink("./start", "~/.config/ibus/start")
    util.create_symlink("./setup", "~/.config/ibus/setup")
