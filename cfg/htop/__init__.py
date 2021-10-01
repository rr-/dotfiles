from libdotfiles import packages, util


def run() -> None:
    packages.try_install("htop")
    util.create_symlink("./htoprc", "~/.config/htop/htoprc")
