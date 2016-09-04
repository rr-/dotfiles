import packages
import util


def run():
    packages.try_install('htop')
    util.create_symlink('./htoprc', '~/.config/htop/htoprc')
