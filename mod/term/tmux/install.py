from os.path import expanduser
from dotinstall import packages
from dotinstall import util


def run():
    packages.try_install('tmux')
    util.create_symlink('./tmux.conf', '~/.tmux.conf')
    util.run_verbose([
        'git',
        'clone',
        'https://github.com/tmux-plugins/tpm',
        expanduser('~/.config/tmux/plugins/tpm')])
