#!/bin/python
import os
from libinstall import FileInstaller, PackageInstaller
dir = os.path.dirname(__file__)

PackageInstaller.try_install('xorg')          # the server itself
PackageInstaller.try_install('xclip')         # for clip to work
PackageInstaller.try_install('xorg-xinit')    # for startx
PackageInstaller.try_install('xorg-xsetroot') # to fix the mouse cursor
PackageInstaller.try_install('xorg-xrandr')   # to query monitor information
PackageInstaller.try_install('xdotool')       # for all sort of things
PackageInstaller.try_install('autocutsel')    # synchronize primary and selection clipboards
PackageInstaller.try_install('clipit')        # keep clipboard content even after application closes
PackageInstaller.try_install('pkg-config')    # for compton
PackageInstaller.try_install('compton')       # for shadows, transparency and vsync

FileInstaller.create_symlink(os.path.join(dir, '.xinitrc'), '~/')
FileInstaller.create_symlink(os.path.join(dir, 'compton.conf'), '~/.config/compton.conf')

if FileInstaller.has_executable('zsh'):
    FileInstaller.create_symlink(os.path.join(dir, '.zlogin'), '~/')
