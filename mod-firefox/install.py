import sys
import packages
import util

packages.try_install('firefox')
if 'cygwin' in sys.platform:
    util.copy_file('./vimperatorrc', '~/.vimperatorrc')
else:
    util.create_symlink('./vimperatorrc', '~/.vimperatorrc')
