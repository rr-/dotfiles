#!/usr/bin/env python3
import os
from libinstall import FileInstaller, PackageInstaller
dir = os.path.dirname(__file__)

PackageInstaller.try_install('libxkbcommon-x11') # fix qt5
PackageInstaller.try_install('python-pyqt5')     # for panel
PackageInstaller.try_install('dmenu')            # program executor
PackageInstaller.try_install('bspwm-git')        # window manager
PackageInstaller.try_install('sxhkd-git')        # hotkey manager
PackageInstaller.try_install('xdo-git')          # like xdotool, but different
PackageInstaller.try_install('feh')              # wallpaper renderer

PackageInstaller.try_install('python-pip')                 # need PIP
PackageInstaller.try_install('psutil', method='pip')       # CPU usage
PackageInstaller.try_install('pyalsaaudio', method='pip')  # system volume
PackageInstaller.try_install('python-mpd2', method='pip')  # mpd interaction
PackageInstaller.try_install('python3-xlib', method='pip') # window titles

FileInstaller.create_symlink(os.path.join(dir, 'sxhkdrc'), '~/.config/sxhkd/sxhkdrc')
FileInstaller.create_symlink(os.path.join(dir, 'bspwmrc'), '~/.config/bspwm/bspwmrc')
FileInstaller.create_symlink(os.path.join(dir, 'toggle-state'), '~/.config/bspwm/toggle-state')
FileInstaller.create_symlink(os.path.join(dir, 'toggle-desktop-padding'), '~/.config/bspwm/toggle-desktop-padding')
FileInstaller.create_symlink(os.path.join(dir, 'rules'), '~/.config/bspwm/rules')
FileInstaller.create_symlink(os.path.join(dir, 'panel'), '~/.config/bspwm/panel')
