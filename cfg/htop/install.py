from dotinstall import packages, util


def run():
    packages.try_install("htop")
    util.create_symlink("./htoprc", "~/.config/htop/htoprc")
