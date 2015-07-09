#!/bin/python
import os, sys
from libinstall import PackageInstaller, FileInstaller, run_verbose
dir = os.path.dirname(__file__)

PackageInstaller.try_install('wget')
PackageInstaller.try_install('curl')
if 'cygwin' in sys.platform:
    PackageInstaller.try_install('ssh')
else:
    PackageInstaller.try_install('openssh')

FileInstaller.create_symlink(os.path.join(dir, '.ssh'), '~/')

run_verbose(['chmod', '0600', os.path.expanduser('~/.ssh/config')])
