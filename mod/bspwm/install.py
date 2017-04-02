from dotinstall import packages
from dotinstall import util


def run():
    if not util.has_executable('bspwm'):
        packages.try_install('bspwm-git')  # window manager
    packages.try_install('dmenu')          # program executor
    packages.try_install('feh')            # wallpaper renderer

    util.create_symlink('./bspwmrc', '~/.config/bspwm/')
    util.create_symlink('./rules', '~/.config/bspwm/')
    util.create_symlink('./start', '~/.config/x/start-bspwm.sh')
