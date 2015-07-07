#!/usr/bin/python
import os
from libinstall import FileInstaller, PackageInstaller
dir = os.path.dirname(__file__)

PackageInstaller.try_install('rxvt-unicode')
FileInstaller.create_symlink(os.path.join(dir, 'Xresources'), '~/.config/Xresources')
FileInstaller.create_symlink(os.path.join(dir, 'Xresources-light'), '~/.config/Xresources-light')
FileInstaller.create_symlink(os.path.join(dir, 'Xresources-dark'), '~/.config/Xresources-dark')
