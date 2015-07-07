#!/bin/python
import os, sys
from libinstall import PackageInstaller, FileInstaller
dir = os.path.dirname(__file__)

PackageInstaller.try_install('mpd')
PackageInstaller.try_install('mpc')

FileInstaller.create_symlink(os.path.join(dir, 'config'), '~/.config/mpd')
FileInstaller.create_dir('~/.config/mpd/playlists')
for file in ['database', 'log', 'pid', 'state', 'sticker.sql']:
    FileInstaller.create_file('~/.config/mpd/' + file)
