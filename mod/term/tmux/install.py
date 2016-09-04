import packages
import util


def run():
    packages.try_install('tmux')
    util.create_symlink('./tmux.conf', '~/.tmux.conf')
