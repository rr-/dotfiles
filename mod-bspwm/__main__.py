#!/bin/python
import os
from libinstall import FileInstaller, PackageInstaller
dir = os.path.dirname(__file__)

PackageInstaller.try_install('dmenu')            # program executor
PackageInstaller.try_install('bspwm-git')        # window manager
PackageInstaller.try_install('sxhkd-git')        # hotkey manager
PackageInstaller.try_install('lemonbar-xft-git') # panel
PackageInstaller.try_install('feh')              # wallpaper renderer

PackageInstaller.try_install('psutil', method='pip')      # CPU usage
PackageInstaller.try_install('pyalsaaudio', method='pip') # system volume
PackageInstaller.try_install('python-mpd2', method='pip') # mpd interaction

FileInstaller.create_symlink(os.path.join(dir, '.sxhkdrc'), '~/.config/sxhkd/sxhkdrc')
FileInstaller.create_symlink(os.path.join(dir, '.bspwmrc'), '~/.config/bspwm/bspwmrc')
FileInstaller.create_symlink(os.path.join(dir, 'panel'), '~/.config/bspwm/panel')
