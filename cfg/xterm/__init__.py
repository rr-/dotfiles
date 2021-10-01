from os.path import expanduser

from libdotfiles import packages, util


def run() -> None:
    packages.try_install("xterm")

    util.create_symlink("./Xresources", "~/.config/Xresources")
    util.run_verbose(["xrdb", "-override", expanduser("~/.config/Xresources")])
