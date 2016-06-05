#!/bin/python
import os
from libinstall import FileInstaller, PackageInstaller, run_verbose
dir = os.path.dirname(__file__)
spell_dir = os.path.expanduser('~/.config/nvim/spell/')

PackageInstaller.try_install('neovim-git')
PackageInstaller.try_install('vim-fzf')

for folder in ['undo', 'backup', 'swap', 'spell', 'autoload']:
    FileInstaller.create_dir('~/.config/nvim/' + folder)

for path in FileInstaller.glob(os.path.join(dir, '*.vim')):
    FileInstaller.create_symlink(path, '~/.config/nvim/')
FileInstaller.create_symlink(os.path.join(dir, '../mod-vim/spell/pl.utf-8.add'), spell_dir)
FileInstaller.create_symlink(os.path.join(dir, '../mod-vim/spell/en.utf-8.add'), spell_dir)
FileInstaller.create_symlink(os.path.join(dir, 'vim-plug/plug.vim'), '~/.config/nvim/autoload/plug.vim')
FileInstaller.download('ftp://ftp.vim.org/pub/vim/runtime/spell/en.utf-8.spl', '~/.config/nvim/spell/')
FileInstaller.download('ftp://ftp.vim.org/pub/vim/runtime/spell/pl.utf-8.spl', '~/.config/nvim/spell/')
FileInstaller.create_file('~/.config/zsh/editor.sh', 'export EDITOR=vim;alias vim=nvim', overwrite=True)

commands = ['PlugInstall']
for fn in os.listdir(spell_dir):
    if 'add' in fn and not 'spl' in fn:
        commands.append('mkspell! ' + os.path.join(spell_dir, fn))
run_verbose(['nvim'] + sum([['-c', cmd] for cmd in commands], []))

if FileInstaller.has_executable('devenv'):
    FileInstaller.copy_file(os.path.join(dir, 'vimrc'), '~/.vsvimrc')
