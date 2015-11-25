#!/bin/python
import os, sys
from libinstall import FileInstaller, PackageInstaller
dir = os.path.dirname(__file__)

PackageInstaller.try_install('firefox')
if 'cygwin' in sys.platform:
    FileInstaller.copy_file(os.path.join(dir, 'vimperatorrc'), '~/.vimperatorrc')
else:
    FileInstaller.create_symlink(os.path.join(dir, 'vimperatorrc'), '~/.vimperatorrc')
