#!/bin/sh
import os
from libinstall import FileInstaller, PackageInstaller
dir = os.path.dirname(__file__)

PackageInstaller.install('git')
FileInstaller.create_symlink(os.path.join(dir, '.gitconfig'), '~/')
FileInstaller.create_symlink(os.path.join(dir, '.gitignore'), '~/')
