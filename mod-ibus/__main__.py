#!/usr/bin/env python3
import os
from libinstall import FileInstaller, PackageInstaller
dir = os.path.dirname(__file__)

PackageInstaller.try_install('ibus')
PackageInstaller.try_install('ibus-anthy')

FileInstaller.create_symlink(os.path.join(dir, 'gtk.css'), '~/.config/gtk-3.0/gtk.css')
FileInstaller.create_symlink(os.path.join(dir, 'start'), '~/.config/ibus/start')
FileInstaller.create_symlink(os.path.join(dir, 'setup'), '~/.config/ibus/setup')
