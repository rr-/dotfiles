#!/bin/python
import os
from libinstall import FileInstaller, PackageInstaller
dir = os.path.dirname(__file__)

choices = ['vim', 'gvim'] #gvim supports for X11 clipboard, but has more dependencies
choice = None
while choice not in choices:
    choice = input('Which package to install? (%s) ' % choices).lower()
PackageInstaller.try_install(choice)

for folder in ['undo', 'backup', 'swap', 'spell']:
    FileInstaller.create_dir('~/.vim/' + folder)

FileInstaller.create_symlink(os.path.join(dir, 'spell/pl.utf-8.add'), '~/.vim/spell/')
FileInstaller.create_symlink(os.path.join(dir, 'spell/en.utf-8.add'), '~/.vim/spell/')
FileInstaller.create_symlink(os.path.join(dir, 'vundle'), '~/.vim/vundle')
FileInstaller.create_symlink(os.path.join(dir, '.vimrc'), '~/')

if FileInstaller.has_executable('devenv'):
    FileInstaller.copy_file(os.path.join(dir, '.vimrc'), '~/.vsvimrc')
