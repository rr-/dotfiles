import packages
import util


def run():
    packages.try_install('zsh')
    util.create_symlink('./zshrc', '~/.zshrc')
    util.create_dir('~/.config/zsh')
