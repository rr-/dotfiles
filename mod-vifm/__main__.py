#!/bin/python
import os
from libinstall import FileInstaller, PackageInstaller
dir = os.path.dirname(__file__)

if not FileInstaller.has_executable('vifm'):
    PackageInstaller.try_install('vifm')
FileInstaller.create_dir('~/.config/vifm')
FileInstaller.create_symlink(os.path.join(dir, 'vifmrc'), '~/.config/vifm/vifmrc')
FileInstaller.create_symlink(os.path.join(dir, 'colors'), '~/.config/vifm/colors')
