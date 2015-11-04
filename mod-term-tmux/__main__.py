#!/usr/bin/python
import os
from libinstall import FileInstaller, PackageInstaller
dir = os.path.dirname(__file__)

PackageInstaller.try_install('tmux')
FileInstaller.create_symlink(os.path.join(dir, 'tmux.conf'), '~/.tmux.conf')
