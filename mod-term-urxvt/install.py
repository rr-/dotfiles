import packages
import util

packages.try_install('urxvt-perls')
if not packages.try_install('rxvt-unicode-24bit'):
    packages.try_install('rxvt-unicode')

if util.exists('/usr/lib/urxvt/perl/keyboard-select') \
        and not util.exists('/usr/local/lib/urxvt/perl/keyboard-select'):
    util.create_symlink(
        '/usr/lib/urxvt/perl/keyboard-select',
        '/usr/local/lib/urxvt/perl/keyboard-select')

util.create_symlink('./ext', '~/.urxvt/ext')
util.create_symlink('./Xresources', '~/.config/Xresources')
util.create_symlink('./Xresources-light', '~/.config/Xresources-light')
util.create_symlink('./Xresources-dark', '~/.config/Xresources-dark')
