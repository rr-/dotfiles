from os.path import expanduser

from libdotfiles import packages, util


def run():
    packages.try_install("zsh")
    util.create_symlink("./zshrc", "~/.zshrc")
    util.create_symlink("./zprofile", "~/.zprofile")
    util.create_symlink("./zshenv", "~/.zshenv")
    util.create_dir("~/.config/zsh")

    util.run_verbose(
        ["lesskey", "-o", expanduser("~/.less"), "--", "./lesskey"]
    )
