#!/usr/bin/env python3
import os
from libinstall import FileInstaller, PackageInstaller
dir = os.path.dirname(__file__)

PackageInstaller.try_install('ibus')
PackageInstaller.try_install('ibus-anthy')

FileInstaller.create_symlink(os.path.join(dir, 'gtk-settings.ini'), '~/.config/ibus/gtk-3.0/settings.ini')
FileInstaller.create_symlink(os.path.join(dir, 'start'), '~/.config/ibus/start')
FileInstaller.create_symlink(os.path.join(dir, 'setup'), '~/.config/ibus/setup')
FileInstaller.create_dir('~/.config/ibus/dconf')
FileInstaller.create_dir('~/.config/ibus/ibus')
FileInstaller.create_dir('~/.config/ibus/ibus-anthy')

# TODO: try to symlink dconf/user to ibus/dconf/user (NOT the other way around)
# if this doesn't work, remember to copy dconf/user to ibus/dconf/user after each change,
# or just commit it.
