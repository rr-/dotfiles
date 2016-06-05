#!/bin/python
import os
from libinstall import FileInstaller, PackageInstaller, run_verbose
dir = os.path.dirname(__file__)
spell_dir = os.path.expanduser('~/.config/vim/spell/')

choices = ['vim', 'gvim'] #gvim supports for X11 clipboard, but has more dependencies
choice = None
while choice not in choices:
    choice = input('Which package to install? (%s) ' % choices).lower()
PackageInstaller.try_install(choice)
PackageInstaller.try_install('fzf')

for folder in ['undo', 'backup', 'swap', 'spell', 'autoload']:
    FileInstaller.create_dir('~/.config/vim/' + folder)

for path in FileInstaller.glob(os.path.join(dir, '../mod-nvim/*.vim')):
    FileInstaller.create_symlink(path, '~/.config/vim/')
FileInstaller.create_symlink(os.path.join(dir, '../mod-nvim/spell/pl.utf-8.add'), spell_dir)
FileInstaller.create_symlink(os.path.join(dir, '../mod-nvim/spell/en.utf-8.add'), spell_dir)
FileInstaller.download('ftp://ftp.vim.org/pub/vim/runtime/spell/en.utf-8.spl', '~/.config/vim/spell/')
FileInstaller.download('ftp://ftp.vim.org/pub/vim/runtime/spell/pl.utf-8.spl', '~/.config/vim/spell/')
FileInstaller.download('https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim', '~/.config/vim/autoload/plug.vim')
FileInstaller.create_file('~/.config/zsh/editor.sh', 'export EDITOR=vim', overwrite=True)
FileInstaller.create_symlink('~/.config/vim/', '~/.vim')
FileInstaller.create_symlink('~/.config/vim/init.vim', '~/.vimrc')

commands = ['PlugInstall']
for fn in os.listdir(spell_dir):
    if 'add' in fn and not 'spl' in fn:
        commands.append('mkspell! ' + os.path.join(spell_dir, fn))
run_verbose(['vim'] + sum([['-c', cmd] for cmd in commands], []))
