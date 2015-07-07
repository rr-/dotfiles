#!/bin/python
import os
from libinstall import FileInstaller, PackageInstaller
dir = os.path.dirname(__file__)

PackageInstaller.try_install('fbterm')
PackageInstaller.try_install('fbgrab')
PackageInstaller.try_install('fbv')

if FileInstaller.has_executable('zsh'):
    FileInstaller.create_symlink(os.path.join(dir, '.zlogin'), '~/')
