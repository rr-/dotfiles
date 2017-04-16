from dotinstall import packages
from dotinstall import util


def run():
    if not util.has_executable('vifm'):
        packages.try_install('vifm')
    util.create_dir('~/.config/vifm')
    util.create_symlink('./vifmrc', '~/.config/vifm/vifmrc')
    util.create_symlink('./colors', '~/.config/vifm/colors')