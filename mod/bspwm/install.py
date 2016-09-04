import packages
import util


def run():
    packages.try_install('libxkbcommon-x11')  # fix qt5
    packages.try_install('python-pyqt5')      # for panel
    packages.try_install('dmenu')             # program executor
    if not util.has_executable('bspwm'):
        packages.try_install('bspwm-git')     # window manager
    packages.try_install('sxhkd-git')         # hotkey manager
    packages.try_install('xdo-git')           # like xdotool, but different
    packages.try_install('feh')               # wallpaper renderer

    packages.try_install('python-pip')                  # need PIP
    packages.try_install('psutil', method='pip')        # CPU usage
    packages.try_install('pyalsaaudio', method='pip')   # system volume
    packages.try_install('python-mpd2', method='pip')   # mpd interaction
    packages.try_install('python3-xlib', method='pip')  # window titles

    util.create_symlink('./sxhkdrc', '~/.config/sxhkd/')
    util.create_symlink('./bspwmrc', '~/.config/bspwm/')
    util.create_symlink('./toggle-state', '~/.config/bspwm/')
    util.create_symlink('./toggle-desktop-padding', '~/.config/bspwm/')
    util.create_symlink('./rules', '~/.config/bspwm/')
    util.create_symlink('./panel', '~/.config/bspwm/')
    util.create_symlink('./start', '~/.config/x/start-bspwm.sh')
