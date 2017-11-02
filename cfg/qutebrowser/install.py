import sys
from dotinstall import packages
from dotinstall import util


def run():
    packages.try_install('qutebrowser')
    util.create_symlink('./config.py', '~/.config/qutebrowser/')
