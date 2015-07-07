#!/bin/python
import os
from libinstall import PackageInstaller, FileInstaller
dir = os.path.dirname(__file__)

PackageInstaller.try_install('eyecandy', method='pip')
FileInstaller.create_symlink(os.path.join(dir, 'candy.json'), '~/.config/EyeCandy/candy.json')
