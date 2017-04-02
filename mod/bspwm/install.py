from dotinstall import packages
from dotinstall import util


def run():
    packages.try_install('libxkbcommon-x11')  # fix qt5
    packages.try_install('python-pyqt5')      # for panel
    packages.try_install('dmenu')             # program executor
    if not util.has_executable('bspwm'):
        packages.try_install('bspwm-git')     # window manager
    packages.try_install('sxhkd-git')         # hotkey manager
    packages.try_install('xdo-git')           # like xdotool, but different
    packages.try_install('feh')               # wallpaper renderer

    util.create_symlink('./sxhkdrc', '~/.config/sxhkd/')
    util.create_symlink('./bspwmrc', '~/.config/bspwm/')
    util.create_symlink('./rules', '~/.config/bspwm/')
    util.create_symlink('./start', '~/.config/x/start-bspwm.sh')
    util.create_symlink('./beep-shot.mp3', '~/.local/share/')
