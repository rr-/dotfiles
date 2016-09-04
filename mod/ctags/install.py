import packages
import util


def run():
    packages.try_install('ctags')
    util.create_symlink('./ctags', '~/.ctags')
