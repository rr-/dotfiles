#!/bin/python
import os
from libinstall import FileInstaller, PackageInstaller
dir = os.path.dirname(__file__)

FileInstaller.create_symlink(os.path.join(dir, '.inputrc'), '~/')
FileInstaller.create_symlink(os.path.join(dir, '.minttyrc-light'), '~/.minttyrc')
