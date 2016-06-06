import packages
import util

packages.try_install('git')
packages.try_install('git-extras-git')
util.create_symlink('./gitconfig', '~/.gitconfig')
util.create_symlink('./gitignore', '~/.gitignore')
