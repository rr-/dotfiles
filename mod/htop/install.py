from dotinstall import packages
from dotinstall import util


def run():
    packages.try_install('htop')
    util.create_symlink('./htoprc', '~/.config/htop/htoprc')
