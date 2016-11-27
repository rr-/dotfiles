from dotinstall import packages
from dotinstall import util


def run():
    packages.try_install('fzf')  # super opener
    packages.try_install('silver-searcher-git')  # super grep
    util.create_symlink('./agignore', '~/.agignore')
