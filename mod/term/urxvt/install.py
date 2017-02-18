from dotinstall import packages
from dotinstall import util


def run():
    packages.try_install('urxvt-perls')
    packages.try_install('rxvt-unicode')

    if util.exists('/usr/lib/urxvt/perl/keyboard-select') \
            and not util.exists('/usr/local/lib/urxvt/perl/keyboard-select'):
        util.create_symlink(
            '/usr/lib/urxvt/perl/keyboard-select',
            '/usr/local/lib/urxvt/perl/keyboard-select')

    util.create_symlink('./ext', '~/.urxvt/ext')
    util.create_symlink('./Xresources', '~/.config/Xresources')
