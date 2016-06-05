import packages
import util

packages.try_install('fbterm')
packages.try_install('fbgrab')
packages.try_install('fbv')

if util.has_executable('zsh'):
    util.create_symlink('./zlogin', '~/.zlogin')
