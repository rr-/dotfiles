import packages
import util


def run():
    packages.try_install('fzf')  # super opener
    packages.try_install('silver-searcher-git')  # super grep
    util.create_symlink('./agignore', '~/.agignore')
    util.create_file('~/.config/zsh/lgrep.sh', 'lgrep() { ag "$@" | fzf }')
