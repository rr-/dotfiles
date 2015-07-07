#!/bin/python
import os
from libinstall import PackageInstaller, FileInstaller
dir = os.path.dirname(__file__)

PackageInstaller.try_install('htop')
FileInstaller.create_symlink(os.path.join(dir, 'htoprc'), '~/.config/htop/htoprc')
