from dotinstall import packages
from dotinstall import util


def run():
    packages.try_install('ctags')
    util.create_symlink('./ctags', '~/.ctags')
