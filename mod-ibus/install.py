import packages
import util

packages.try_install('ibus')
packages.try_install('ibus-anthy')
util.create_symlink('./start', '~/.config/ibus/start')
util.create_symlink('./setup', '~/.config/ibus/setup')
