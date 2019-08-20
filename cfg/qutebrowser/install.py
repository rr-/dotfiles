import sys

from dotinstall import packages, util


def run():
    packages.try_install("qutebrowser")
    util.create_symlink("./config.py", "~/.config/qutebrowser/")
    util.create_symlink("./greasemonkey", "~/.local/share/qutebrowser/")
