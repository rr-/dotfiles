import logs
import packages
import util

packages.try_install('git')
util.create_symlink('#/gitconfig', '~/.gitconfig')
util.create_symlink('#/gitignore', '~/.gitignore')
