import packages
import util

if not packages.try_install('rxvt-unicode-24bit'):
    packages.try_install('rxvt-unicode')
util.create_symlink('./ext', '~/.urxvt/ext')
util.create_symlink('./Xresources', '~/.config/Xresources')
util.create_symlink('./Xresources-light', '~/.config/Xresources-light')
util.create_symlink('./Xresources-dark', '~/.config/Xresources-dark')
