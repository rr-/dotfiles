#!/bin/python
import os
from libinstall import FileInstaller, PackageInstaller
dir = os.path.dirname(__file__)

#TODO: rewrite this to my own screenshot solution
PackageInstaller.try_install('escrotum-git')  # to make screenshots

PackageInstaller.try_install('xorg-xsetroot') # to fix the mouse cursor
PackageInstaller.try_install('xorg-xrandr')   # to query monitor information
PackageInstaller.try_install('xdotool')       # for all sort of things
PackageInstaller.try_install('autocutsel')    # synchronize primary and selection clipboards
PackageInstaller.try_install('clipit')        # keep clipboard content even after application closes
PackageInstaller.try_install('compton')       # for shadows, transparency and vsync

FileInstaller.create_symlink(os.path.join(dir, '.xinitrc'), '~/')
FileInstaller.create_symlink(os.path.join(dir, 'compton.conf'), '~/.config/compton.conf')

if FileInstaller.has_executable('zsh'):
    FileInstaller.create_symlink(os.path.join(dir, '.zlogin'), '~/')
