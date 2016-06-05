import packages
import util

packages.try_install('tmux')
util.create_symlink('./tmux.conf', '~/.tmux.conf')
