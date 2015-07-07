#!/bin/python
import os
from libinstall import FileInstaller, PackageInstaller
dir = os.path.dirname(__file__)

PackageInstaller.try_install('vim')

for folder in ['undo', 'backup', 'swap', 'spell']:
    FileInstaller.create_dir('~/.vim/' + folder)

FileInstaller.create_symlink(os.path.join(dir, 'spell/pl.utf-8.add'), '~/.vim/spell/')
FileInstaller.create_symlink(os.path.join(dir, 'spell/en.utf-8.add'), '~/.vim/spell/')
FileInstaller.create_symlink(os.path.join(dir, 'vundle'), '~/.vim/vundle')
FileInstaller.create_symlink(os.path.join(dir, '.vimrc'), '~/')

if FileInstaller.has_executable('devenv'):
    FileInstaller.copy(os.path.join(dir, '.vimrc'), '~/.vsvimrc')
