#!/bin/python
import os
from libinstall import FileInstaller, PackageInstaller, run_verbose
dir = os.path.dirname(__file__)
spell_dir = os.path.expanduser('~/.vims/spell/')

choices = ['vim', 'gvim'] #gvim supports for X11 clipboard, but has more dependencies
choice = None
while choice not in choices:
    choice = input('Which package to install? (%s) ' % choices).lower()
PackageInstaller.try_install(choice)
PackageInstaller.try_install('vim-command-t')

for folder in ['undo', 'backup', 'swap', 'spell']:
    FileInstaller.create_dir('~/.vim/' + folder)

FileInstaller.create_symlink(os.path.join(dir, 'spell/pl.utf-8.add'), spell_dir)
FileInstaller.create_symlink(os.path.join(dir, 'spell/en.utf-8.add'), spell_dir)
FileInstaller.create_symlink(os.path.join(dir, 'vundle'), '~/.vim/vundle')
FileInstaller.create_symlink(os.path.join(dir, 'vimrc'), '~/.vimrc')

for fn in os.listdir(spell_dir):
    if 'add' in fn and not 'spl' in fn:
        run_verbose(['vim', '-c', 'mkspell! ' + os.path.join(spell_dir, fn) + '|quit'])

if FileInstaller.has_executable('devenv'):
    FileInstaller.copy_file(os.path.join(dir, 'vimrc'), '~/.vsvimrc')
