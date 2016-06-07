import packages
import util

packages.try_install('ctags')
util.create_symlink('./ctags', '~/.ctags')
